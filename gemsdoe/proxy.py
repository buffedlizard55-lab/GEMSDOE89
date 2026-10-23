"""REPORT-ONLY instruments. Nothing here can pass or fail a release.

1. Catalogue hide-and-recover proxy: withhold a seeded 30 % of the known
   catalogue pixels, then measure the fraction of withheld positives that have
   a dot within the kernel radius.  History (brief sec.3): this proxy correlated
   -0.87..+0.54 with live scores over n=12-14 files, so it is reported, never
   gated, and never called a score.

2. Leakage canary: single-feature AUC against catalogue membership.  A feature
   with AUC > 0.90 means stop and investigate.

3. Surrogate DTI: DTI computed with the catalogue as the "truth" raster.  The
   catalogue is *masked* in live scoring, so this is a counterfactual measure
   of structural coverage, not an estimate of the live score.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

from .metric import KERNEL_RADIUS_PX, dti


def wilson_interval(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (float(max(0.0, centre - half)), float(min(1.0, centre + half)))


def _recall(points, withheld_pts, radius=KERNEL_RADIUS_PX):
    if len(withheld_pts) == 0:
        return 0.0, 0.0, 0
    tree = cKDTree(points)
    d, _ = tree.query(withheld_pts, distance_upper_bound=radius)
    hit = int(np.isfinite(d).sum())
    lo, hi = wilson_interval(hit, len(withheld_pts))
    return hit / len(withheld_pts), hi - lo, len(withheld_pts)


def hide_and_recover(dots, catalogue_mask, seed=20261023, holdout=0.30):
    """Recall of a seeded catalogue holdout. Returns dict."""
    cat_pts = np.argwhere(catalogue_mask)
    rng = np.random.default_rng(seed)
    n_hold = int(round(holdout * len(cat_pts)))
    sel = rng.choice(len(cat_pts), size=n_hold, replace=False)
    withheld = cat_pts[sel]
    dots_pts = np.argwhere(dots)
    rec, half, n = _recall(dots_pts, withheld)
    return {
        "n_withheld": int(n),
        "seed": seed,
        "holdout_fraction": holdout,
        "recall": rec,
        "ci95_halfwidth": half,
        "ci95": [max(0.0, rec - half), min(1.0, rec + half)],
    }


def random_null(dots, footprint, catalogue_mask, clearance_px=3.0, seed=7):
    """Same dot count, placed uniformly in the footprint outside the collar."""
    rng = np.random.default_rng(seed)
    clearance = ndi.distance_transform_edt(~catalogue_mask)
    free = footprint & (clearance >= clearance_px)
    pts = np.argwhere(free)
    n = int(dots.sum())
    sel = rng.choice(len(pts), size=n, replace=False)
    null = np.zeros_like(dots, dtype=bool)
    null[pts[sel, 0], pts[sel, 1]] = True
    return null


def auc(feature, labels, sample=400_000, seed=11):
    """Rank AUC via the Mann-Whitney statistic on a seeded subsample."""
    f = feature.ravel().astype(np.float64)
    y = labels.ravel().astype(bool)
    ok = np.isfinite(f)
    idx = np.flatnonzero(ok)
    if len(idx) > sample:
        idx = np.random.default_rng(seed).choice(idx, size=sample, replace=False)
    f, y = f[idx], y[idx]
    n1, n0 = int(y.sum()), int((~y).sum())
    if n1 == 0 or n0 == 0:
        return None
    order = np.argsort(f, kind="mergesort")
    ranks = np.empty(len(f), dtype=np.float64)
    ranks[order] = np.arange(1, len(f) + 1)
    # average ranks for ties
    fs = f[order]
    start = 0
    for i in range(1, len(fs) + 1):
        if i == len(fs) or fs[i] != fs[start]:
            if i - start > 1:
                ranks[order[start:i]] = ranks[order[start:i]].mean()
            start = i
    return float((ranks[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def canary(features: dict, catalogue_mask, threshold=0.90):
    out = {}
    for name, arr in features.items():
        a = auc(arr, catalogue_mask)
        out[name] = {"auc": a, "flag": bool(a is not None and max(a, 1 - a) > threshold)}
    return out


def surrogate_dti(dots, catalogue_mask, radius=KERNEL_RADIUS_PX):
    """DTI with the pinned catalogue as the truth raster (counterfactual)."""
    return dti(catalogue_mask, dots.astype(np.float64), radius)
