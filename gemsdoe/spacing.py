"""SPACING axis: matched local lattice / Poisson-disk / along-strike edits.

All three arms share one control built from the verified parent:

* remove the same 10% of dots (smallest nearest-neighbour distance, seeded ties);
* keep every replacement inside its source dot's 5 km x 5 km block, so the
  block-scale concentration of every arm is exactly the parent's;
* require new pixels to be in the footprint, off all parent pixels, >=3 px
  from the catalogue, and >=2.8 px from every surviving/placed dot;
* use one matched Poisson gap anchor per removed dot in every arm.

The Poisson arm uses best-candidate Poisson-disk placement (16 seeded draws).
The lattice arm chooses the nearest legal point on a fixed 3 px lattice to the
same anchor. The strike arm minimises an anisotropic distance to that anchor,
with along-strike displacement four times cheaper than perpendicular movement.
Local strike is PCA of surviving R0 dots, not an independently mapped fault.
"""

from __future__ import annotations

from collections import Counter
import hashlib

import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

MIN_SEP_PX = 2.8
CATALOGUE_CLEARANCE_PX = 3.0
CONTROL_BLOCK_PX = 50  # 5 km at 100 m; matches the CONCENTRATION control scale
SEARCH_RADII_PX = (6, 8, 10, 12, 16, 20, 28)
BEST_CANDIDATE_DRAWS = 16
LATTICE_STEP_PX = 3
STRIKE_FIT_RADIUS_PX = 20
STRIKE_MAX_NEIGHBOURS = 24
STRIKE_ALONG_SCALE = 0.25
PATTERNS = ("lattice", "poisson", "strike")


def _points_sha256(points) -> str:
    a = np.ascontiguousarray(np.asarray(points, dtype=np.int32))
    return hashlib.sha256(a.tobytes()).hexdigest()


def _candidate_points(origin, radius, valid, block_px=CONTROL_BLOCK_PX):
    """Legal pixels in a circular window, clipped to the source control block."""
    y, x = (int(v) for v in origin)
    by, bx = y // block_px, x // block_px
    y0 = max(0, y - radius, by * block_px)
    y1 = min(valid.shape[0], y + radius + 1, (by + 1) * block_px)
    x0 = max(0, x - radius, bx * block_px)
    x1 = min(valid.shape[1], x + radius + 1, (bx + 1) * block_px)
    if y0 >= y1 or x0 >= x1:
        return np.empty((0, 2), dtype=np.int32)
    pts = np.argwhere(valid[y0:y1, x0:x1]).astype(np.int32) + (y0, x0)
    if not len(pts):
        return pts
    d2 = np.sum((pts - np.asarray(origin)) ** 2, axis=1)
    return pts[d2 <= radius * radius]


def _far_from_placed(candidates, placed, min_sep=MIN_SEP_PX):
    if not len(placed) or not len(candidates):
        return candidates
    d = cKDTree(np.asarray(placed, dtype=np.int32)).query(candidates)[0]
    return candidates[d >= min_sep]


def _select_crowded(parent_dots, n_move, rng):
    pts = np.argwhere(parent_dots).astype(np.int32)
    if len(pts) < 2:
        raise ValueError("SPACING needs at least two parent dots")
    nn = cKDTree(pts).query(pts, k=2)[0][:, 1]
    if not 0 < n_move <= len(pts):
        raise ValueError(f"invalid move count {n_move} for {len(pts)} dots")
    # Random numbers are used only to break the many exact NN-distance ties.
    order = np.lexsort((rng.random(len(pts)), nn))
    chosen = order[:n_move]
    return pts[chosen], nn, nn[chosen]


def _place_poisson(control, rng):
    """Create the shared gap anchors by best-candidate Poisson-disk sampling."""
    placed = []
    radius_usage = Counter()
    for index, source in enumerate(control["removed_pts"]):
        found = None
        for radius in SEARCH_RADII_PX:
            cand = _candidate_points(source, radius, control["valid"])
            cand = _far_from_placed(cand, placed)
            if len(cand):
                k = min(BEST_CANDIDATE_DRAWS, len(cand))
                draw = cand[rng.choice(len(cand), size=k, replace=False)]
                clearance = control["distance_to_remaining"][draw[:, 0], draw[:, 1]]
                found = draw[int(np.argmax(clearance))]
                radius_usage[radius] += 1
                break
        if found is None:
            raise RuntimeError(f"no legal Poisson destination for source {index}: {source}")
        placed.append(found)
    return np.asarray(placed, dtype=np.int32), radius_usage


def prepare_control(parent_dots, footprint, catalogue_mask, fraction=0.10, seed=20261023):
    """Build the shared removal set and Poisson anchors for all three arms."""
    parent_dots = np.asarray(parent_dots, dtype=bool)
    footprint = np.asarray(footprint, dtype=bool)
    catalogue_mask = np.asarray(catalogue_mask, dtype=bool)
    if parent_dots.shape != footprint.shape or parent_dots.shape != catalogue_mask.shape:
        raise ValueError("parent, footprint and catalogue shapes differ")
    if (parent_dots & ~footprint).any():
        raise ValueError("parent dots outside footprint")
    if (parent_dots & catalogue_mask).any():
        raise ValueError("parent has catalogue mass")
    n_dots = int(parent_dots.sum())
    n_move = int(round(fraction * n_dots))
    if not 1.0 <= 100.0 * n_move / n_dots <= 50.0:
        raise ValueError("SPACING edit must change 1-50% of parent dots")

    rng = np.random.default_rng(seed)
    removed_pts, parent_nn, removed_nn = _select_crowded(parent_dots, n_move, rng)
    remaining = parent_dots.copy()
    remaining[removed_pts[:, 0], removed_pts[:, 1]] = False
    distance_to_remaining = ndi.distance_transform_edt(~remaining)
    distance_to_catalogue = ndi.distance_transform_edt(~catalogue_mask)
    valid = (
        footprint
        & ~parent_dots  # every arm must move every selected dot; no source reuse
        & (distance_to_catalogue >= CATALOGUE_CLEARANCE_PX)
        & (distance_to_remaining >= MIN_SEP_PX)
    )
    control = {
        "parent_dots": parent_dots,
        "footprint": footprint,
        "catalogue_mask": catalogue_mask,
        "remaining": remaining,
        "removed_pts": removed_pts,
        "removed_nn": removed_nn,
        "parent_nn": parent_nn,
        "distance_to_remaining": distance_to_remaining,
        "distance_to_catalogue": distance_to_catalogue,
        "valid": valid,
        "fraction": float(fraction),
        "seed": int(seed),
    }
    anchors, radius_usage = _place_poisson(control, rng)
    control["anchors"] = anchors
    control["poisson_radius_usage"] = radius_usage
    control["removed_sha256"] = _points_sha256(removed_pts)
    control["anchors_sha256"] = _points_sha256(anchors)
    return control


def _strike_vectors(control):
    """PCA strike at each source, fitted to surviving parent dots only."""
    remaining_pts = np.argwhere(control["remaining"]).astype(np.int32)
    tree = cKDTree(remaining_pts)
    vectors = []
    anisotropy = []
    fallbacks = 0
    for source in control["removed_pts"]:
        idx = tree.query_ball_point(source, STRIKE_FIT_RADIUS_PX)
        neighbours = remaining_pts[idx]
        if len(neighbours) > STRIKE_MAX_NEIGHBOURS:
            d2 = np.sum((neighbours - source) ** 2, axis=1)
            neighbours = neighbours[np.argsort(d2)[:STRIKE_MAX_NEIGHBOURS]]
        if len(neighbours) >= 2:
            cov = np.cov((neighbours - neighbours.mean(axis=0)).T)
            eigenvalues, eigenvectors = np.linalg.eigh(cov)
            vector = eigenvectors[:, int(np.argmax(eigenvalues))]
            vectors.append(vector / np.linalg.norm(vector))
            anisotropy.append(float(eigenvalues.max() / max(eigenvalues.min(), 1e-12)))
        else:
            vectors.append(np.array([1.0, 0.0]))
            anisotropy.append(1.0)
            fallbacks += 1
    return np.asarray(vectors), np.asarray(anisotropy), fallbacks


def _place_matched(control, pattern):
    """Place lattice/strike dots around the exact same Poisson gap anchors."""
    placed = []
    radius_usage = Counter()
    vectors = anisotropy = None
    fallbacks = 0
    if pattern == "strike":
        vectors, anisotropy, fallbacks = _strike_vectors(control)

    for index, (source, anchor) in enumerate(zip(control["removed_pts"], control["anchors"])):
        found = None
        for radius in SEARCH_RADII_PX:
            cand = _candidate_points(source, radius, control["valid"])
            cand = _far_from_placed(cand, placed)
            if pattern == "lattice":
                cand = cand[
                    (cand[:, 0] % LATTICE_STEP_PX == 0)
                    & (cand[:, 1] % LATTICE_STEP_PX == 0)
                ]
                distance = np.sum((cand - anchor) ** 2, axis=1) if len(cand) else np.empty(0)
            elif pattern == "strike":
                delta = cand - anchor
                vector = vectors[index]
                along = delta @ vector
                perpendicular = delta @ np.array([-vector[1], vector[0]])
                keep = np.any(delta != 0, axis=1)  # do not simply copy the Poisson arm
                cand = cand[keep]
                along = along[keep]
                perpendicular = perpendicular[keep]
                distance = perpendicular ** 2 + (STRIKE_ALONG_SCALE * along) ** 2
            else:
                raise ValueError(f"unknown matched pattern {pattern!r}")
            if len(cand):
                clearance = control["distance_to_remaining"][cand[:, 0], cand[:, 1]]
                # Primary: matched-anchor geometry. Secondary: largest gap.
                chosen = int(np.lexsort((cand[:, 1], cand[:, 0], -clearance, distance))[0])
                found = cand[chosen]
                radius_usage[radius] += 1
                break
        if found is None:
            raise RuntimeError(f"no legal {pattern} destination for source {index}: {source}")
        placed.append(found)
    extra = {
        "radius_usage": radius_usage,
        "strike_anisotropy": anisotropy,
        "strike_orientation_fallbacks": fallbacks,
        "strike_vectors": vectors,
    }
    return np.asarray(placed, dtype=np.int32), extra


def _block_density_cv(dots, footprint, block=10):
    h, w = dots.shape
    bh, bw = h // block, w // block
    dm = dots[:bh * block, :bw * block].reshape(bh, block, bw, block).sum((1, 3)).ravel()
    fm = footprint[:bh * block, :bw * block].reshape(bh, block, bw, block).sum((1, 3)).ravel()
    keep = fm > 0.5 * block * block
    density = dm[keep] / fm[keep]
    return float(np.std(density) / np.mean(density)) if len(density) and density.mean() else float("nan")


def build_from_control(control, pattern):
    """Return (variant dot mask, parent-diff statistics) for one SPACING arm."""
    if pattern not in PATTERNS:
        raise ValueError(f"pattern must be one of {PATTERNS}")
    if pattern == "poisson":
        added_pts = control["anchors"].copy()
        extra = {
            "radius_usage": control["poisson_radius_usage"],
            "strike_anisotropy": None,
            "strike_orientation_fallbacks": 0,
            "strike_vectors": None,
        }
    else:
        added_pts, extra = _place_matched(control, pattern)

    removed_pts = control["removed_pts"]
    anchors = control["anchors"]
    variant = control["remaining"].copy()
    variant[added_pts[:, 0], added_pts[:, 1]] = True
    parent = control["parent_dots"]
    n_dots = int(parent.sum())
    n_move = len(removed_pts)
    if int(variant.sum()) != n_dots:
        raise AssertionError("dot count not preserved")
    if int((parent & ~variant).sum()) != n_move or int((variant & ~parent).sum()) != n_move:
        raise AssertionError("parent diff is not the requested one-for-one move")
    if not np.array_equal(removed_pts // CONTROL_BLOCK_PX, added_pts // CONTROL_BLOCK_PX):
        raise AssertionError("5 km control-block counts changed")
    if (variant & control["catalogue_mask"]).any():
        raise AssertionError("variant has catalogue mass")

    all_pts = np.argwhere(variant).astype(np.int32)
    all_nn = cKDTree(all_pts).query(all_pts, k=2)[0][:, 1]
    added_nn = cKDTree(all_pts).query(added_pts, k=2)[0][:, 1]
    displacement = np.linalg.norm(added_pts - removed_pts, axis=1)
    anchor_shift = np.linalg.norm(added_pts - anchors, axis=1)
    d_cat_added = control["distance_to_catalogue"][added_pts[:, 0], added_pts[:, 1]]
    radius_usage = {str(int(k)): int(v) for k, v in sorted(extra["radius_usage"].items())}
    stats = {
        "pattern": pattern,
        "n_dots": n_dots,
        "n_moved": int(n_move),
        "pct_changed": 100.0 * n_move / n_dots,
        "seed": control["seed"],
        "removed_sha256": control["removed_sha256"],
        "anchors_sha256": control["anchors_sha256"],
        "control_block_px": CONTROL_BLOCK_PX,
        "control_block_km": CONTROL_BLOCK_PX / 10.0,
        "control_block_counts_preserved": True,
        "catalogue_clearance_px": CATALOGUE_CLEARANCE_PX,
        "min_separation_px": MIN_SEP_PX,
        "added_min_catalogue_clearance_px": float(d_cat_added.min()),
        "added_min_nearest_dot_px": float(added_nn.min()),
        "catalogue_mass": int((variant & control["catalogue_mask"]).sum()),
        "mean_displacement_px": float(displacement.mean()),
        "median_displacement_px": float(np.median(displacement)),
        "p95_displacement_px": float(np.percentile(displacement, 95)),
        "max_displacement_px": float(displacement.max()),
        "mean_anchor_shift_px": float(anchor_shift.mean()),
        "anchor_exact_matches": int((anchor_shift == 0).sum()),
        "source_nn_median_px": float(np.median(control["removed_nn"])),
        "nn_median_before_px": float(np.median(control["parent_nn"])),
        "nn_median_after_px": float(np.median(all_nn)),
        "nn_below_3px_before": int((control["parent_nn"] < 3.0).sum()),
        "nn_below_3px_after": int((all_nn < 3.0).sum()),
        "block_cv_1km_before": _block_density_cv(parent, control["footprint"], 10),
        "block_cv_1km_after": _block_density_cv(variant, control["footprint"], 10),
        "search_radius_usage": radius_usage,
        "expanded_beyond_6px": int(sum(v for k, v in extra["radius_usage"].items() if k > 6)),
        "best_candidate_draws": BEST_CANDIDATE_DRAWS,
        "lattice_step_px": LATTICE_STEP_PX,
        "added_on_3px_lattice_fraction": float(np.mean(
            (added_pts[:, 0] % LATTICE_STEP_PX == 0)
            & (added_pts[:, 1] % LATTICE_STEP_PX == 0)
        )),
        "strike_fit_radius_px": STRIKE_FIT_RADIUS_PX,
        "strike_along_scale": STRIKE_ALONG_SCALE,
        "strike_orientation_fallbacks": int(extra["strike_orientation_fallbacks"]),
    }
    if pattern == "strike":
        vectors = extra["strike_vectors"]
        delta = added_pts - anchors
        along = np.sum(delta * vectors, axis=1)
        perpendicular = np.sum(delta * np.column_stack([-vectors[:, 1], vectors[:, 0]]), axis=1)
        anisotropy = extra["strike_anisotropy"]
        stats.update({
            "strike_median_abs_perpendicular_px": float(np.median(np.abs(perpendicular))),
            "strike_p90_abs_perpendicular_px": float(np.percentile(np.abs(perpendicular), 90)),
            "strike_mean_abs_along_px": float(np.mean(np.abs(along))),
            "strike_anisotropy_median": float(np.median(anisotropy)),
            "strike_anisotropy_p90": float(np.percentile(anisotropy, 90)),
        })
    return variant, stats
