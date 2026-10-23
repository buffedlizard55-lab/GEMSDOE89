"""SPACING axis: lattice vs Poisson-disk vs along-strike at matched count.

The axis is a controlled single-variable edit of a parent dot raster:
  * the dot COUNT is held exactly fixed,
  * only the geometry of the point set changes -- no mass, ranking, relief
    class, or catalogue-collar change,
  * every moved dot hops to a free pixel inside a bounded local window, so the
    variant tests spacing rather than geography,
  * every NEW pixel obeys the hard constraints: inside the footprint and
    >= 3 px from the catalogue. Inherited dots (including the parent's 2.236 px
    collar, IRREGULARITIES item 2) keep their exact pixel unless they move.

R0 measures min nearest-neighbour (NN) distance 2.828 px with 30.3 % of dots at
exactly that diagonal separation, so the natural intervention strength is a
3.0 px minimum separation (the kernel radius is also 3.0 px).
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

from .relief import block_density_cv, nearest_neighbour_distance

CATALOGUE_CLEARANCE_PX = 3.0   # hard constraint 4, applied to NEW pixels only
BLOCK_PX = 10                 # 1 km blocks for the report-only density CV


# --------------------------------------------------------------------------- #
# shared machinery
# --------------------------------------------------------------------------- #
def _offsets(radius):
    """Integer (dy, dx) offsets with 0 < Euclidean distance <= radius, sorted."""
    r = int(np.ceil(radius))
    offs = [
        (dy, dx)
        for dy in range(-r, r + 1)
        for dx in range(-r, r + 1)
        if 0 < dy * dy + dx * dx <= radius * radius + 1e-12
    ]
    return sorted(offs, key=lambda t: (t[0] * t[0] + t[1] * t[1], t[0], t[1]))


def capacity_mask(footprint, catalogue_mask, clearance=CATALOGUE_CLEARANCE_PX):
    """Pixels a MOVED dot is allowed to occupy."""
    d = ndi.distance_transform_edt(~(catalogue_mask > 0))
    return footprint & (d >= clearance)


def greedy_violators(pts, shape, r_min, rng):
    """Seeded greedy split into r_min-separated anchors and mover violators.

    Dots are visited in a seeded random order. A dot becomes an anchor iff no
    accepted anchor lies within r_min; otherwise it is a mover and the nearest
    accepted anchor is recorded (the along-strike arm re-spaces relative to it).
    Occupancy is tracked on a raster with sorted window offsets, which is exact
    for integer pixel coordinates and avoids rebuilding a tree per dot.
    """
    h, w = shape
    occ = np.zeros(shape, dtype=bool)
    owner = np.full(shape, -1, dtype=np.int64)
    is_anchor = np.zeros(len(pts), dtype=bool)
    violated_anchor = np.full(len(pts), -1, dtype=np.int64)
    offs = _offsets(r_min)
    for k in rng.permutation(len(pts)):
        y, x = int(pts[k, 0]), int(pts[k, 1])
        nearest = -1
        for dy, dx in offs:
            yy, xx = y + dy, x + dx
            if 0 <= yy < h and 0 <= xx < w and occ[yy, xx]:
                nearest = owner[yy, xx]
                break  # offsets are distance-sorted -> first hit is nearest
        if nearest < 0:
            is_anchor[k] = True
            occ[y, x] = True
            owner[y, x] = k
        else:
            violated_anchor[k] = nearest
    movers = np.flatnonzero(~is_anchor)
    return is_anchor, movers, violated_anchor


def _window_patch(y, x, w, shape, margin=0):
    h, wd = shape
    y0, y1 = max(0, int(y - w - margin)), min(h, int(y + w + margin + 1))
    x0, x1 = max(0, int(x - w - margin)), min(wd, int(x + w + margin + 1))
    return y0, y1, x0, x1


# Occupied neighbours beyond this distance are irrelevant: every acceptance
# rule below only needs to confirm the parent's 2.828 px floor or to rank
# candidates whose own origin NN is below 3 px.
EDT_MARGIN = 4
PARENT_MIN_SEP = float(np.sqrt(8))  # 2.828 px: R0's own suppression radius


def _extended_edt(y, x, w, occ, margin=EDT_MARGIN):
    """EDT to the nearest occupied pixel on an margin-extended window.

    The extension matters: a candidate at the edge of the displacement window
    can have an occupied neighbour just outside that window, and a tight patch
    would not see it. The padded border stays conservative (treated occupied).
    """
    y0, y1, x0, x1 = _window_patch(y, x, w, occ.shape, margin)
    patch_occ = occ[y0:y1, x0:x1]
    # EDT returns the distance to the nearest ZERO pixel: put False at occupied
    # cells and False on the padded border so the border stays conservative
    # (an occupied neighbour just outside the window is never missed).
    padded = np.zeros((y1 - y0 + 2, x1 - x0 + 2), dtype=bool)
    padded[1:-1, 1:-1] = ~patch_occ
    d_patch = ndi.distance_transform_edt(padded)[1:-1, 1:-1]
    return y0, x0, d_patch


def _free_candidates(y, x, w, capacity, occ):
    """Free, valid candidate pixels within Euclidean w of (y, x).

    Returns arrays (gy, gx, dist_to_origin, nn_if_placed) or None. NN-if-placed
    is the distance to the nearest currently occupied pixel, measured on an
    extended patch so neighbours just outside the window are visible.
    """
    y0, x0, d_patch = _extended_edt(y, x, w, occ)
    y1, x1 = y0 + d_patch.shape[0], x0 + d_patch.shape[1]
    patch_cap = capacity[y0:y1, x0:x1]
    patch_occ = occ[y0:y1, x0:x1]
    free = patch_cap & ~patch_occ
    if not free.any():
        return None
    ly, lx = np.nonzero(free)
    gy, gx = ly + y0, lx + x0
    d_origin = np.hypot(gy - y, gx - x)
    keep = d_origin <= w + 1e-9
    if not keep.any():
        return None
    gy, gx, d_origin = gy[keep], gx[keep], d_origin[keep]
    nn_placed = d_patch[ly[keep], lx[keep]]
    return gy, gx, d_origin, nn_placed


def _seeded_pick(n, score_desc, rng):
    """Argmax with a seeded random tie-break."""
    order = np.lexsort((rng.random(n), -score_desc))
    return order[0]


# --------------------------------------------------------------------------- #
# arm 1: Poisson-disk (isotropic minimum-separation enforcement)
# --------------------------------------------------------------------------- #
def place_poisson_disk(pts, movers, origin_nn, capacity, window, rng):
    occ = np.zeros(capacity.shape, dtype=bool)
    occ[pts[:, 0], pts[:, 1]] = True
    out = pts.copy()
    moved = np.zeros(len(pts), dtype=bool)
    for k in movers:
        y, x = int(out[k, 0]), int(out[k, 1])
        cand = _free_candidates(y, x, window, capacity, occ)
        if cand is None:
            continue
        gy, gx, _d_origin, nn_placed = cand
        if nn_placed.max() <= origin_nn[k] + 1e-12:
            continue  # no free pixel improves this dot's separation: keep it
        j = _seeded_pick(len(gy), nn_placed, rng)
        ny, nx = int(gy[j]), int(gx[j])
        occ[y, x] = False
        occ[ny, nx] = True
        out[k] = (ny, nx)
        moved[k] = True
    return out, moved


# --------------------------------------------------------------------------- #
# arm 2: along-strike re-spacing of the same violators
# --------------------------------------------------------------------------- #
def strike_field(det_elev, sigma=1.0):
    """Unit strike orientation (uy, ux) from the smoothed det_elev gradient.

    Strike is perpendicular to the topographic gradient; orientation is modulo
    pi so the sign is arbitrary. Flat pixels (zero gradient) return zeros.
    """
    f = np.where(np.isfinite(det_elev), det_elev, 0.0).astype(np.float32)
    f = ndi.gaussian_filter(f, sigma=sigma)
    gy, gx = np.gradient(f)
    norm = np.hypot(gy, gx)
    uy = np.divide(-gx, norm, out=np.zeros_like(norm), where=norm > 0)
    ux = np.divide(gy, norm, out=np.zeros_like(norm), where=norm > 0)
    return uy, ux


def place_along_strike(pts, movers, violated_anchor, uy, ux, capacity,
                       window, cos_gate, rng):
    occ = np.zeros(capacity.shape, dtype=bool)
    occ[pts[:, 0], pts[:, 1]] = True
    out = pts.copy()
    moved = np.zeros(len(pts), dtype=bool)
    no_strike = 0
    for k in movers:
        y, x = int(out[k, 0]), int(out[k, 1])
        a = int(violated_anchor[k])
        ay, ax = int(pts[a, 0]), int(pts[a, 1])
        uay, uax = uy[ay, ax], ux[ay, ax]
        if uay == 0.0 and uax == 0.0:
            uay, uax = uy[y, x], ux[y, x]
        if uay == 0.0 and uax == 0.0:
            no_strike += 1
            continue
        cand = _free_candidates(y, x, window, capacity, occ)
        if cand is None:
            continue
        gy, gx, d_origin, nn_placed = cand
        vy, vx = gy - ay, gx - ax
        vnorm = np.hypot(vy, vx)
        cos = np.divide(np.abs(vy * uay + vx * uax), vnorm,
                        out=np.zeros_like(vnorm), where=vnorm > 0)
        # never create a pair closer than the parent's own 2.828 px floor,
        # and keep only strike-aligned destinations
        ok = (cos >= cos_gate) & (nn_placed >= PARENT_MIN_SEP - 1e-9)
        if not ok.any():
            continue  # nothing strike-aligned in reach: keep the parent pixel
        sep_ok = (nn_placed[ok] >= 3.0).astype(np.float64)
        # lexical: separation first, then strike alignment, then shortest hop
        score_y = sep_ok
        score_cos = cos[ok]
        score_d = -d_origin[ok]
        gy, gx, nn_placed = gy[ok], gx[ok], nn_placed[ok]
        order = np.lexsort((rng.random(len(gy)), score_d, score_cos, score_y))
        j = order[-1]
        ny, nx = int(gy[j]), int(gx[j])
        occ[y, x] = False
        occ[ny, nx] = True
        out[k] = (ny, nx)
        moved[k] = True
    return out, moved, no_strike


# --------------------------------------------------------------------------- #
# arm 3: partial square-lattice regularization
# --------------------------------------------------------------------------- #
def best_lattice_phase(pts, spacing):
    """Lattice phase (oy, ox) in [0, s)^2 minimizing total snap distance."""
    best = None
    s = spacing
    for oy in range(s):
        for ox in range(s):
            ny = np.rint((pts[:, 0] - oy) / s) * s + oy
            nx = np.rint((pts[:, 1] - ox) / s) * s + ox
            tot = float(np.hypot(ny - pts[:, 0], nx - pts[:, 1]).sum())
            if best is None or tot < best[0]:
                best = (tot, oy, ox)
    return best[1], best[2]


def place_lattice(pts, capacity, spacing, tol, window, rng):
    h, w = capacity.shape
    s = spacing
    oy, ox = best_lattice_phase(pts, s)
    occ = np.zeros(capacity.shape, dtype=bool)
    occ[pts[:, 0], pts[:, 1]] = True
    out = pts.copy()
    moved = np.zeros(len(pts), dtype=bool)
    n_anchored = 0
    for k in rng.permutation(len(pts)):
        y, x = int(out[k, 0]), int(out[k, 1])
        nny = int(round((y - oy) / s) * s + oy)
        nnx = int(round((x - ox) / s) * s + ox)
        snap = np.hypot(nny - y, nnx - x)
        if snap <= tol + 1e-12 and 0 <= nny < h and 0 <= nnx < w \
                and capacity[nny, nnx] and not occ[nny, nnx]:
            n_anchored += 1
            continue  # already on the lattice to tolerance: keep exact pixel
        # nearest FREE valid lattice node inside the displacement window;
        # an extended EDT enforces the parent's 2.828 px separation floor
        ey0, ex0, d_patch = _extended_edt(y, x, window, occ)
        ky0 = int(np.ceil((y - window - oy) / s))
        ky1 = int(np.floor((y + window - oy) / s))
        kx0 = int(np.ceil((x - window - ox) / s))
        kx1 = int(np.floor((x + window - ox) / s))
        keys = []
        for iy in range(ky0, ky1 + 1):
            for ix in range(kx0, kx1 + 1):
                qy, qx = oy + iy * s, ox + ix * s
                if not (0 <= qy < h and 0 <= qx < w):
                    continue
                if not capacity[qy, qx] or occ[qy, qx]:
                    continue
                if d_patch[qy - ey0, qx - ex0] < PARENT_MIN_SEP - 1e-9:
                    continue
                d = np.hypot(qy - y, qx - x)
                if d <= window + 1e-9 and d > 1e-12:
                    keys.append((d, qy, qx))
        if not keys:
            continue
        r = rng.random(len(keys))
        order = sorted(range(len(keys)), key=lambda i: (keys[i][0], r[i]))
        _d, ny, nx = keys[order[0]]
        occ[y, x] = False
        occ[ny, nx] = True
        out[k] = (ny, nx)
        moved[k] = True
    return out, moved, (oy, ox), n_anchored


# --------------------------------------------------------------------------- #
# stats and the unified build entry
# --------------------------------------------------------------------------- #
def strike_alignment(dots, uy, ux, nn_cut=3.5):
    """Mean |cos(angle)| between each close-pair vector and local strike."""
    pts = np.argwhere(dots)
    if len(pts) < 2:
        return float("nan")
    tree = cKDTree(pts)
    d, idx = tree.query(pts, k=2)
    nn = d[:, 1]
    close = nn < nn_cut
    if not close.any():
        return float("nan")
    p = pts[close]
    q = pts[idx[close, 1]]
    vy, vx = (q - p).T
    vn = np.hypot(vy, vx)
    cos = np.abs(vy * uy[p[:, 0], p[:, 1]] + vx * ux[p[:, 0], p[:, 1]]) / vn
    return float(np.nanmean(cos))


def spacing_stats(parent_dots, variant_dots, footprint, moved, pts0, pts1,
                  uy=None, ux=None, extra=None):
    """pts0/pts1 are the same dots in the same row order (out = pts.copy())."""
    n = int(parent_dots.sum())
    assert int(variant_dots.sum()) == n
    nn0, _ = nearest_neighbour_distance(parent_dots)
    nn1, _ = nearest_neighbour_distance(variant_dots)
    if moved.any():
        disp = np.hypot(pts1[:, 0] - pts0[:, 0], pts1[:, 1] - pts0[:, 1])[moved]
    else:
        disp = np.zeros(0)
    out = {
        "n_dots": n,
        "n_changed": int(moved.sum()),
        "pct_changed": 100.0 * moved.sum() / n,
        "mean_displacement_px": float(disp.mean()) if len(disp) else 0.0,
        "median_displacement_px": float(np.median(disp)) if len(disp) else 0.0,
        "max_displacement_px": float(disp.max()) if len(disp) else 0.0,
        "nn_min_before": float(nn0.min()),
        "nn_min_after": float(nn1.min()),
        "nn_median_before": float(np.median(nn0)),
        "nn_median_after": float(np.median(nn1)),
        "nn_mean_before": float(nn0.mean()),
        "nn_mean_after": float(nn1.mean()),
        "frac_nn_below3_before": float((nn0 < 3.0).mean()),
        "frac_nn_below3_after": float((nn1 < 3.0).mean()),
        "frac_nn_eq_2p828_before": float((np.isclose(nn0, np.sqrt(8))).mean()),
        "frac_nn_eq_2p828_after": float((np.isclose(nn1, np.sqrt(8))).mean()),
        "block_cv_before": block_density_cv(parent_dots, footprint),
        "block_cv_after": block_density_cv(variant_dots, footprint),
    }
    if uy is not None and ux is not None:
        out["strike_alignment_before"] = strike_alignment(parent_dots, uy, ux)
        out["strike_alignment_after"] = strike_alignment(variant_dots, uy, ux)
    if extra:
        out.update(extra)
    return out


def mask_from_pts(pts, shape):
    m = np.zeros(shape, dtype=bool)
    m[pts[:, 0], pts[:, 1]] = True
    return m
