"""RELIEF axis: move mass between basin / piedmont / range-front classes.

The axis is a controlled single-variable edit of a parent dot raster:
  * the dot COUNT is held exactly fixed,
  * dots are removed only from one relief class and added only to another,
  * every added dot obeys the parent's own placement rules (footprint,
    >= 3 px from the catalogue, >= 2.8 px from any other dot -- the parent's
    documented suppression radius),
  * nothing else about the parent changes.

Source class = the class with the lowest known-fault density that still holds
at least MIN_SOURCE_SHARE of the parent's dots (a class holding a handful of
dots cannot supply a 10-15 % transfer).  Target class = the highest-density
class.  Both are measured from the pinned catalogue, never from test truth.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

NODATA_F32 = np.float32(-3.4028234663852886e38)
MIN_SOURCE_SHARE = 0.10        # a source class must hold >=10 % of the parent's dots
MIN_SEP_PX = 2.8               # parent's own dot-suppression radius
CATALOGUE_CLEARANCE_PX = 3.0   # hard constraint 4
BLOCK_PX = 10                  # 1 km block, for the density-CV report


# --------------------------------------------------------------------------- #
# input streaming
# --------------------------------------------------------------------------- #
def stream_bands(path, bands_1based):
    """Read selected bands of a multi-band float32 GeoTIFF row by row.

    The competition feature stack is 3730x3292x19 float32; materialising all
    19 bands costs ~0.9 GB, so bands are accumulated one row at a time.
    Returns dict {band_number: 2-D float32 array with nodata -> NaN}.
    """
    import tifffile

    with tifffile.TiffFile(path) as t:
        page = t.pages[0]
        height, width = page.imagelength, page.imagewidth
        nbands = int(np.prod(page.shape)) // (height * width)
        for b in bands_1based:
            if not 1 <= b <= nbands:
                raise ValueError(f"band {b} outside 1..{nbands}")
        out = {b: np.empty((height, width), dtype=np.float32) for b in bands_1based}
        r = 0
        for arr, _idx, _shp in page.segments():
            for b in bands_1based:
                out[b][r] = arr[0, 0, :, b - 1]
            r += 1
            if r >= height:
                break
        if r != height:
            raise IOError(f"read {r} of {height} rows from {path}")
    for b in bands_1based:
        out[b][out[b] == NODATA_F32] = np.nan
    return out


# --------------------------------------------------------------------------- #
# classes
# --------------------------------------------------------------------------- #
def define_classes(field, domain):
    """Equal-AREA terciles of `field` over `domain` (bool mask).

    Returns (class raster int8 with -1 outside the domain, cut points).
    """
    vals = field[domain]
    cuts = np.percentile(vals[np.isfinite(vals)], [100 / 3, 200 / 3])
    cls = np.full(field.shape, -1, dtype=np.int8)
    finite = domain & np.isfinite(field)
    cls[finite & (field <= cuts[0])] = 0            # basin / low
    cls[finite & (field > cuts[0]) & (field <= cuts[1])] = 1   # piedmont / mid
    cls[finite & (field > cuts[1])] = 2             # range front / high
    return cls, cuts


def class_stats(cls, catalogue_mask, dots):
    """Area, catalogue density and parent dot density for each class."""
    rows = []
    for c in (0, 1, 2):
        m = cls == c
        area = int(m.sum())
        cat = int((m & catalogue_mask).sum())
        d = int((m & dots).sum())
        rows.append(
            {
                "class": c,
                "area_px": area,
                "area_share": area / max(1, (cls >= 0).sum()),
                "catalogue_px": cat,
                "catalogue_density_per_1000px": 1000.0 * cat / max(1, area),
                "parent_dots": d,
                "parent_density_per_1000px": 1000.0 * d / max(1, area),
            }
        )
    total = sum(r["catalogue_px"] for r in rows) or 1
    for r in rows:
        r["catalogue_share"] = r["catalogue_px"] / total
    for r in rows:
        r["parent_share"] = r["parent_dots"] / max(1, sum(x["parent_dots"] for x in rows))
        r["lift_parent_over_catalogue"] = (
            r["parent_share"] / r["catalogue_share"] if r["catalogue_share"] > 0 else None
        )
    return rows


def choose_source_target(stats):
    """Lowest-density class holding enough mass -> highest-density class."""
    total_dots = sum(r["parent_dots"] for r in stats)
    eligible = [r for r in stats if r["parent_dots"] >= MIN_SOURCE_SHARE * total_dots]
    if not eligible:
        raise ValueError("no class holds enough mass to be a source")
    source = min(eligible, key=lambda r: r["catalogue_density_per_1000px"])
    target = max(stats, key=lambda r: r["catalogue_density_per_1000px"])
    if source["class"] == target["class"]:
        raise ValueError("source and target class coincide: no relief move available")
    return source, target


# --------------------------------------------------------------------------- #
# relocation
# --------------------------------------------------------------------------- #
def nearest_neighbour_distance(dots):
    """Distance from each dot to its nearest OTHER dot (0 for a lone dot)."""
    pts = np.argwhere(dots)
    if len(pts) < 2:
        return np.zeros(len(pts)), pts
    tree = cKDTree(pts)
    d, _ = tree.query(pts, k=2)
    return d[:, 1], pts


def select_source_dots(dots, cls, source_class, n_move, rng):
    """The n_move most redundant dots inside the source class.

    Redundancy = small nearest-neighbour distance.  Under the max-operator
    kernel a dot whose kernel is already covered by a neighbour adds almost
    nothing to T but all of its mass to S and M, so it is the cheapest mass
    to move.
    """
    nn, pts = nearest_neighbour_distance(dots)
    in_cls = cls[pts[:, 0], pts[:, 1]] == source_class
    idx = np.flatnonzero(in_cls)
    if len(idx) < n_move:
        raise ValueError(
            f"source class holds {len(idx)} dots, need {n_move}"
        )
    order = np.lexsort((rng.random(len(idx)), nn[idx]))  # by nn asc, seeded tie-break
    chosen = idx[order[:n_move]]
    return pts[chosen], nn[chosen]


def select_destinations(capacity_mask, remaining_dots, n, rng, gradient=None,
                        min_structure_px=None, min_sep=MIN_SEP_PX, pool_factor=60):
    """Greedy farthest-point placement inside `capacity_mask`.

    Candidates are ranked by distance to the nearest surviving dot, so the new
    mass lands in the largest existing gaps of the target class (the max
    operator makes a dot that merely repeats its neighbour's kernel worthless).
    A minimum separation keeps the new dots at the parent's own suppression
    radius instead of stacking them.
    """
    dist_to_dots = ndi.distance_transform_edt(~remaining_dots)
    usable = capacity_mask
    if gradient is not None and min_structure_px is not None:
        # keep the new dots on ground at least as structured as a typical
        # parent dot; otherwise the rule fills smooth, featureless ground and
        # the variant tests placement quality rather than relief.
        structured = capacity_mask & (gradient >= min_structure_px)
        if structured.sum() >= n:
            usable = structured
        else:
            usable = capacity_mask
    d = np.where(usable, dist_to_dots, -1.0)
    flat = d.ravel()
    pool = min(flat.size, max(pool_factor * n, 20000))
    cand = np.argpartition(-flat, min(pool, flat.size - 1))[:pool]
    cand = cand[flat[cand] > 0]
    if len(cand) < n:
        raise ValueError(f"only {len(cand)} usable destination pixels for {n} dots")
    order = np.lexsort((rng.random(len(cand)), -flat[cand]))
    cand = cand[order]
    ys, xs = np.unravel_index(cand, d.shape)
    pts = np.column_stack([ys, xs]).astype(np.int32)
    accepted = []
    tree = cKDTree(pts)
    taken = np.zeros(len(pts), dtype=bool)
    # iterate in distance order, accept if far enough from everything accepted
    acc_list = []
    acc_tree = None
    for i in range(len(pts)):
        if taken[i]:
            continue
        if acc_tree is not None:
            dd, _ = acc_tree.query(pts[i])
            if dd < min_sep:
                continue
        acc_list.append(pts[i])
        acc_tree = cKDTree(np.array(acc_list))
        if len(acc_list) >= n:
            break
        # suppress near neighbours to keep the loop cheap
        taken[tree.query_ball_point(pts[i], min_sep)] = True
    if len(acc_list) < n:
        raise ValueError(f"greedy placement produced {len(acc_list)} of {n} dots")
    return np.array(acc_list[:n], dtype=np.int32)


def block_density_cv(dots, footprint, block=BLOCK_PX):
    """Coefficient of variation of dot density over fixed blocks (report only)."""
    h, w = dots.shape
    bh, bw = h // block, w // block
    dm = dots[: bh * block, : bw * block].reshape(bh, block, bw, block).sum((1, 3)).ravel()
    fm = footprint[: bh * block, : bw * block].reshape(bh, block, bw, block).sum((1, 3)).ravel()
    keep = fm > 0.5 * block * block
    dens = dm[keep] / fm[keep]
    return float(np.std(dens) / np.mean(dens)) if keep.any() and np.mean(dens) > 0 else float("nan")


def build(field, domain, catalogue_mask, footprint, parent_dots, fraction,
          rng, source_class=None, target_class=None, gradient=None,
          structure_percentile=50.0):
    """Return (variant dot mask, stats dict). Count is preserved exactly."""
    cls, cuts = define_classes(field, domain)
    stats = class_stats(cls, catalogue_mask, parent_dots)
    src, tgt = choose_source_target(stats)
    if source_class is not None:
        src = next(r for r in stats if r["class"] == source_class)
    if target_class is not None:
        tgt = next(r for r in stats if r["class"] == target_class)

    n_dots = int(parent_dots.sum())
    n_move = int(round(fraction * n_dots))
    removed_pts, removed_nn = select_source_dots(
        parent_dots, cls, src["class"], n_move, rng
    )
    remaining = parent_dots.copy()
    remaining[removed_pts[:, 0], removed_pts[:, 1]] = False

    clearance = ndi.distance_transform_edt(~catalogue_mask)
    capacity = (
        (cls == tgt["class"])
        & footprint
        & (clearance >= CATALOGUE_CLEARANCE_PX)
        & ~remaining
    )
    min_structure = None
    if gradient is not None:
        min_structure = float(np.percentile(gradient[parent_dots], structure_percentile))
    added_pts = select_destinations(capacity, remaining, n_move, rng,
                                    gradient=gradient, min_structure_px=min_structure)

    variant = remaining.copy()
    variant[added_pts[:, 0], added_pts[:, 1]] = True
    assert int(variant.sum()) == n_dots, "count not preserved"

    # how far the mass actually moved: removed dot -> nearest added dot
    if len(added_pts):
        dd, _ = cKDTree(added_pts).query(removed_pts)
        disp = dd
    else:
        disp = np.zeros(0)

    nn_after, _ = nearest_neighbour_distance(variant)
    stats_out = {
        "classes": stats,
        "cuts": [float(c) for c in cuts],
        "source_class": int(src["class"]),
        "target_class": int(tgt["class"]),
        "fraction_requested": float(fraction),
        "n_dots": n_dots,
        "n_moved": int(n_move),
        "pct_changed": 100.0 * n_move / n_dots,  # moved dots; each moved dot counts once
        "removed_nn_median_px": float(np.median(removed_nn)) if len(removed_nn) else None,
        "mean_displacement_px": float(disp.mean()) if len(disp) else None,
        "median_displacement_px": float(np.median(disp)) if len(disp) else None,
        "nn_median_before_px": float(np.median(nearest_neighbour_distance(parent_dots)[0])),
        "nn_median_after_px": float(np.median(nn_after)),
        "block_cv_before": block_density_cv(parent_dots, footprint),
        "block_cv_after": block_density_cv(variant, footprint),
        "source_class_dots_before": int(src["parent_dots"]),
        "source_class_dots_after": int((variant & (cls == src["class"])).sum()),
        "target_class_dots_before": int(tgt["parent_dots"]),
        "target_class_dots_after": int((variant & (cls == tgt["class"])).sum()),
        "min_structure_px": min_structure,
        "structure_percentile": structure_percentile if gradient is not None else None,
        "added_mean_gradient": float(gradient[variant & ~parent_dots].mean())
        if gradient is not None and (variant & ~parent_dots).any() else None,
        "parent_mean_gradient": float(gradient[parent_dots].mean()) if gradient is not None else None,
    }
    return variant, stats_out
