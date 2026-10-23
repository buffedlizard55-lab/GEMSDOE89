"""SPACING axis: a hard-disk relaxation of the parent dot field at fixed count.

Why this is a single-variable edit
----------------------------------
The parent R0 is not a random field.  Measured from the pinned raster:

  * 37,654 unit dots, minimum nearest-neighbour distance 2.828 px (= sqrt(8),
    the (2,2) diagonal), 30.3 % of the dots sit at exactly that distance and
    the median nearest-neighbour distance is 3.0 px;
  * the footprint holds 5,167,373 px, so the mean density is 0.73 %.  A Poisson
    field at that density has a median nearest-neighbour distance of ~5.5 px.

So the parent is a *saturated hard disk of radius ~2.83 px laid on ribbons*:
inside a ribbon the dots are packed at the suppression radius, and between
ribbons the map is empty.  That is a spacing statement, not a mass statement,
and it is the thing this axis changes.

Metric reason the axis can pay
------------------------------
DTI = T / (0.2T + 0.2(S-M) + 0.8|G|) with T = sum_truth max_i p_i k(i,g).
The max operator means T depends on the *union* of the kernel disks: two dots
2.83 px apart both cost 1.0 of mass S but their disks overlap by a wide lens,
so part of that mass buys no new coverage.  Relocating the redundant member of
such a pair into a nearby gap keeps S, keeps or raises the union area (hence
T), and cannot raise the cost term -- the sign of the geometric effect is
non-negative.  Whether it pays in the live score depends on whether truth is
where the ribbons are; that is the question the arms test.

Constructions (all at exactly the parent's dot count)
-----------------------------------------------------
  1. hard-disk MIS at radius r, redundant dots relocated by Poisson
     relaxation to the locally best admissible free pixel ("poisson").
  2. the same, one radius step coarser ("dose arm").
  3. the same selection, destinations restricted to the local strike corridor
     ("along"), the strike estimated from the parent's own dot density via a
     structure tensor.  Cross-strike gaps between two dots 2.83 px apart are
     already inside both kernels; along strike the kernel runs out sooner, so
     trend-following is the geometric hypothesis most likely to convert a
     relocation into new coverage.

Everything is deterministic: the greedy independent set is ordered by nearest-
neighbour distance (ascending) with a seeded random tie-break, and every
placement tie is broken by the same seeded stream.
"""

from __future__ import annotations

import math

import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

from .metric import KERNEL_RADIUS_PX

CATALOGUE_CLEARANCE_PX = 3.0   # hard constraint 4 (applies to every NEW position)
MIN_SEP_PARENT_PX = math.sqrt(8.0)   # measured: parent's own suppression radius (2.828 px)


# --------------------------------------------------------------------------- #
# geometry helpers
# --------------------------------------------------------------------------- #
def dot_points(dots):
    return np.argwhere(np.asarray(dots, dtype=bool))


def nn_distance(pts):
    """Distance from every dot to its nearest other dot."""
    if len(pts) < 2:
        return np.zeros(len(pts), dtype=np.float64)
    d, _ = cKDTree(pts).query(pts, k=2)
    return d[:, 1]


def hard_disk_independent_set(pts, target, rng, priority=None):
    """Greedy maximal set of dots that are all >= target apart.

    Dots are visited in ascending `priority` order (default: nearest-neighbour
    distance, so the least crowded dots are kept first) with a seeded random
    tie-break.  Returns a boolean keep-mask.  Deterministic for a given seed.
    """
    n = len(pts)
    if priority is None:
        priority = nn_distance(pts)
    order = np.lexsort((rng.random(n), priority))
    reach = int(math.ceil(target))
    t2 = target * target
    kept = np.zeros(n, dtype=bool)
    buckets = {}
    for i in order:
        y, x = int(pts[i, 0]), int(pts[i, 1])
        ok = True
        for dy in range(-reach, reach + 1):
            for dx in range(-reach, reach + 1):
                if dy * dy + dx * dx > t2:
                    continue
                for j in buckets.get((y + dy, x + dx), ()):
                    py, px = pts[j]
                    if (py - y) ** 2 + (px - x) ** 2 < t2:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                break
        if ok:
            kept[i] = True
            buckets.setdefault((y, x), []).append(i)
    return kept


def strike_orientation(dots, sigma_structure=2.0, sigma_tensor=4.0):
    """Local strike angle and coherence from the parent's own dot density.

    Structure tensor on a Gaussian-smoothed dot-density image.  The dominant
    eigenvector is the direction of maximum gradient (across the ribbon); the
    strike is that direction plus 90 degrees.  Coherence = normalised
    eigenvalue contrast, in [0, 1].

    This uses no external dataset: the field is the parent raster itself, so
    the arm stays a function of pinned inputs only.
    """
    dens = ndi.gaussian_filter(np.asarray(dots, dtype=np.float32), sigma_structure)
    gy, gx = np.gradient(dens)
    jxx = ndi.gaussian_filter(gx * gx, sigma_tensor)
    jyy = ndi.gaussian_filter(gy * gy, sigma_tensor)
    jxy = ndi.gaussian_filter(gx * gy, sigma_tensor)
    theta_grad = 0.5 * np.arctan2(2.0 * jxy, jxx - jyy)
    coherence = np.hypot(jxx - jyy, 2.0 * jxy) / (jxx + jyy + 1e-12)
    return (theta_grad + np.pi / 2.0).astype(np.float32), coherence.astype(np.float32)


def poisson_offsets(window):
    return [(dy, dx)
            for dy in range(-window, window + 1)
            for dx in range(-window, window + 1)
            if (dy, dx) != (0, 0)]


def along_strike_offsets(angle, reach=3, corridor=2):
    """Integer offsets along +/- the strike, with a small perpendicular jog."""
    ca, sa = math.cos(angle), math.sin(angle)
    out = []
    for t in (1, 2, 3):
        if t > reach:
            break
        for s in (1, -1):
            ay, ax = s * t * sa, s * t * ca
            for p in range(-corridor, corridor + 1):
                dy = int(round(ay + p * ca))
                dx = int(round(ax - p * sa))
                if (dy, dx) != (0, 0) and (dy, dx) not in out:
                    out.append((dy, dx))
    return out


def _placed_grid():
    """Spatial hash of accepted positions (cell size 4 px, > any target)."""
    return {}


def _min_dist_to_placed(placed, y, x, target, cell=4):
    best = math.inf
    cy, cx = y // cell, x // cell
    for gy in (cy - 1, cy, cy + 1):
        for gx in (cx - 1, cx, cx + 1):
            for (py, px) in placed.get((gy, gx), ()):
                d = math.hypot(py - y, px - x)
                if d < best:
                    best = d
    return best


def _add_placed(placed, y, x, cell=4):
    placed.setdefault((y // cell, x // cell), []).append((y, x))


# --------------------------------------------------------------------------- #
# coverage statistics (label-free; MODEL input only)
# --------------------------------------------------------------------------- #
def coverage_area(dots, radius=KERNEL_RADIUS_PX):
    """Area integral of the triangular kernel over the union of dot disks.

    = sum over pixels of max(0, 1 - d/radius) where d is the distance to the
    nearest dot.  This is exactly T when truth is uniformly distributed over
    the covered region, so its relative change is the assumption-light proxy
    for Delta(T)/T at fixed mass.  It is a geometric statistic, not a score.
    """
    d = ndi.distance_transform_edt(~dots)
    k = np.clip(1.0 - d / radius, 0.0, 1.0)
    return float(k.sum())


def block_density_cv(dots, footprint, block=10):
    """CV of dot density over 1 km blocks (report only; see IRREGULARITIES 6)."""
    h, w = dots.shape
    bh, bw = h // block, w // block
    dm = dots[: bh * block, : bw * block].reshape(bh, block, bw, block).sum((1, 3)).ravel()
    fm = footprint[: bh * block, : bw * block].reshape(bh, block, bw, block).sum((1, 3)).ravel()
    keep = fm > 0.5 * block * block
    dens = dm[keep] / fm[keep]
    return float(np.std(dens) / np.mean(dens)) if keep.any() and np.mean(dens) > 0 else float("nan")


# --------------------------------------------------------------------------- #
# the build
# --------------------------------------------------------------------------- #
def relocate(parent_dots, footprint, clearance_px, target_sep, mode, rng,
             window=3, offsets_reach=3, corridor=2, strike=None):
    """Relocate the redundant member of every close pair.  Count is preserved.

    Parameters
    ----------
    parent_dots : bool raster
    footprint   : bool raster (scored domain)
    clearance_px: float raster, Euclidean distance to the catalogue
    target_sep  : hard-disk radius to enforce among *kept and placed* dots
    mode        : 'poisson' (free choice inside the window) or 'along'
    strike      : angle raster, required for mode='along'

    Returns (variant mask, stats dict).  A dot whose relocation finds no
    admissible destination stays exactly where it was, so the count is always
    the parent's count.
    """
    if mode not in ("poisson", "along"):
        raise ValueError(f"unknown mode {mode!r}")
    pts = dot_points(parent_dots)
    n = len(pts)
    kept = hard_disk_independent_set(pts, target_sep, rng)
    kept_pts = pts[kept]
    ktree = cKDTree(kept_pts)
    to_move = pts[~kept]

    shape = parent_dots.shape
    # Every parent position is blocked as a destination.  A dot whose
    # relocation fails stays exactly where it was, so allowing a later dot to
    # land on a parent pixel could stack two dots on one pixel (or create a
    # pair tighter than the parent's own 2.83 px disk).  Blocking all origin
    # pixels makes the outcome independent of processing order.
    free_static = footprint & (clearance_px >= CATALOGUE_CLEARANCE_PX) & ~parent_dots
    placed = _placed_grid()
    moved_from, moved_to, disp = [], [], []
    n_fail = 0

    poisson_off = poisson_offsets(window)
    for (y, x) in to_move:
        offs = poisson_off if mode == "poisson" else along_strike_offsets(
            float(strike[y, x]), reach=offsets_reach, corridor=corridor)
        cand = np.empty((len(offs), 2), dtype=np.int64)
        for k, (dy, dx) in enumerate(offs):
            cand[k, 0] = y + dy
            cand[k, 1] = x + dx
        yy, xx = cand[:, 0], cand[:, 1]
        inside = (yy >= 0) & (yy < shape[0]) & (xx >= 0) & (xx < shape[1])
        valid = inside.copy()
        valid[inside] &= free_static[yy[inside], xx[inside]]
        if not valid.any():
            n_fail += 1
            continue
        idx = np.flatnonzero(valid)
        dkept = ktree.query(cand[idx])[0]
        idx = idx[dkept >= target_sep]
        if len(idx) == 0:
            n_fail += 1
            continue
        best = None
        for j in idx:
            sep = _min_dist_to_placed(placed, int(yy[j]), int(xx[j]), target_sep)
            if sep < target_sep:
                continue
            if mode == "poisson":
                tie = -(abs(int(yy[j]) - y) + abs(int(xx[j]) - x))
            else:  # prefer the far end of the corridor: extend the trace
                tie = math.hypot(yy[j] - y, xx[j] - x)
            key = (min(sep, 2.0 * target_sep), tie, rng.random())
            if best is None or key > best[0]:
                best = (key, int(yy[j]), int(xx[j]))
        if best is None:
            n_fail += 1
            continue
        _, py, px = best
        _add_placed(placed, py, px)
        moved_from.append((y, x))
        moved_to.append((py, px))
        disp.append(math.hypot(py - y, px - x))

    variant = parent_dots.copy()
    if moved_from:
        mf = np.array(moved_from)
        variant[mf[:, 0], mf[:, 1]] = False
        mt = np.array(moved_to)
        variant[mt[:, 0], mt[:, 1]] = True

    # A dot whose relocation found no destination stays where it was, and the
    # loop above only checks kept + already-placed dots, so a later placement
    # can land right next to such a stayer.  Repair: revert any new position
    # that ends up closer than target_sep to a dot that did not move, and
    # repeat until no pair is tighter than the parent's own hard disk.
    # key = destination (row, col), value = the origin it came from
    origin_of = {(int(py), int(px)): (int(y), int(x))
                 for (y, x), (py, px) in zip(moved_from, moved_to)}
    n_reverted = 0
    for _ in range(8):
        pos = dot_points(variant)
        d, j = cKDTree(pos).query(pos, k=2)
        tight = np.flatnonzero(d[:, 1] < target_sep - 1e-9)
        reverted_now = 0
        for i in tight:
            a = (int(pos[i, 0]), int(pos[i, 1]))
            if a not in origin_of:
                continue
            variant[a[0], a[1]] = False
            oy, ox = origin_of.pop(a)
            variant[oy, ox] = True
            reverted_now += 1
        n_reverted += reverted_now
        if reverted_now == 0:
            break
    staying = {(int(y), int(x)) for y, x in dot_points(variant)}
    pairs = [(a, b) for a, b in zip(moved_from, moved_to)
             if (int(b[0]), int(b[1])) in staying and (int(a[0]), int(a[1])) not in staying]
    moved_from = [a for a, _ in pairs]
    moved_to = [b for _, b in pairs]
    disp = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in pairs]

    if int(variant.sum()) != n:  # cannot happen by construction; refuse silently? no
        raise AssertionError(f"count changed: {int(variant.sum())} != {n}")

    nn_after = nn_distance(dot_points(variant))
    stats = {
        "mode": mode,
        "target_sep_px": float(target_sep),
        "window_px": int(window),
        "corridor_px": int(corridor) if mode == "along" else None,
        "n_dots": n,
        "n_kept": int(kept.sum()),
        "n_selected_for_move": int(len(to_move)),
        "n_moved": int(len(moved_from)),
        "n_placement_failures": int(n_fail),
        "n_reverted_by_repair": int(n_reverted),
        "pct_changed": 100.0 * len(moved_to) / n,
        "mean_displacement_px": float(np.mean(disp)) if disp else 0.0,
        "median_displacement_px": float(np.median(disp)) if disp else 0.0,
        "p95_displacement_px": float(np.percentile(disp, 95)) if disp else 0.0,
        "max_displacement_px": float(np.max(disp)) if disp else 0.0,
        "nn_min_before_px": float(nn_distance(pts).min()),
        "nn_min_after_px": float(nn_after.min()),
        "nn_median_before_px": float(np.median(nn_distance(pts))),
        "nn_median_after_px": float(np.median(nn_after)),
        "block_cv_before": block_density_cv(parent_dots, footprint),
        "block_cv_after": block_density_cv(variant, footprint),
    }
    return variant, stats


# --------------------------------------------------------------------------- #
# prediction model (MODEL, never a score)
# --------------------------------------------------------------------------- #
def predict_dti_change(parent_dti, coverage_before, coverage_after):
    """Delta-DTI implied by a relative coverage change at fixed mass.

    DTI = T/D with D = 0.2T + 0.2(S-M) + 0.8|G|, so
        dDTI/dT = (1/D)(1 - 0.2*DTI)  =>  Delta DTI = (1 - 0.2*DTI)*DTI*(dT/T)
    with S, M and |G| held fixed.  The band below is the modelling assumption:
    truth uniformly spread over the covered region (point estimate) versus
    truth concentrated inside the parent's own saturated ribbons, where the
    gain collapses to zero and placement error can cost up to half of it.
    """
    d = coverage_after / coverage_before - 1.0
    point = (1.0 - 0.2 * parent_dti) * parent_dti * d
    return {
        "coverage_rel_change": d,
        "point": float(point),
        "band": [float(min(0.0, point) - 0.5 * abs(point)),
                 float(max(0.0, point) + 1.5 * abs(point))],
    }
