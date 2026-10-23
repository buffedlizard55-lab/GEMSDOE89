"""MASS axis: remove mass, ranked by the credit a dot can claim on its own.

Why this ranking, and why it is not a repeat
--------------------------------------------
The brief's MASS definition is "drop the lowest-ranked 10 % ... by the parent's
own ranking (rebuild the ranking from the recorded recipe if it is not stored)".
The recipe was never stored: `h33-h33-2-b2` has no build script, and its
ancestor field `h19-5` is a **binary** dot mask (121,131 cells, values {0, 1}),
so it carries no ordering at all.  Every MASS row already in the fleet ledger
was therefore ranked on something invented at build time -- `GEMSDOE88` records
its own ranking as ``0.6*clip(d_catalogue_px/50,0,1) + 0.4*uniform`` and notes
that 89.4 % of its dropped dots lay within 10 px of the catalogue, i.e. that arm
is a collar/prune move wearing a MASS label.

This module supplies the missing ranking from the metric itself, with no truth
and no labels:

    u_i = credit dot i would claim if truth were uniformly distributed over
          the footprint, counting only pixels where i is the strictly nearest
          dot (the max operator means a neighbour's kernel already claims
          everything else, and a dot that repeats a neighbour is pure mass).

`u_i` is exactly the expected value of the per-dot term that the DTI algebra
differentiates, under a flat truth prior.  Dropping the dots with the smallest
`u_i` is therefore "drop the lowest-ranked 10 %" with the ranking derived from
the metric definition rather than from a stored artefact that does not exist.

The break-even that decides the experiment
------------------------------------------
Removing one unit dot whose kernel credit is ``k`` changes DTI by

    dDTI = -(k - 0.2*DTI) / D          (D = 0.2T + 0.2(S-M) + 0.8|G|)

so at the parent's claimed 0.2778 every removed dot with ``k < 0.0556`` is a
gain and every dot with ``k > 0.0556`` is a loss.  ``u_i`` is a *proxy* for
whether k is on the low side of that line; it is not an estimate of k.  The
mechanism card states the consequence plainly: this arm wins only if the
dropped decile sits below break-even.

Everything here is deterministic: same parent + same seed -> same file bytes.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

KERNEL_RADIUS_PX = 3.0
BLOCK_PX_1KM = 10
BLOCK_PX_2P5KM = 25
BLOCK_PX_5KM = 50


def _disc_offsets(radius=KERNEL_RADIUS_PX):
    """Integer offsets inside the triangular kernel, excluding the dot itself."""
    r = int(np.floor(radius))
    out = []
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = float(np.hypot(dy, dx))
            if 0.0 < d < radius:
                out.append((dy, dx, d, 1.0 - d / radius))
    return out


def unique_credit(dots, radius=KERNEL_RADIUS_PX):
    """Per-dot expected unique kernel credit under a flat truth prior.

    Returns (u, pts) with u[i] the credit of dot i.  The dot's own pixel
    contributes 1.0 always (it is the only dot there).  A pixel is attributed
    to a dot only when that dot is the *strict* nearest; exact ties (another
    dot at the same distance) contribute nothing, which is the conservative
    convention and affects <0.1 % of pixels at the parent's >=2.24 px
    suppression radius.
    """
    dots = np.asarray(dots, dtype=bool)
    pts = np.argwhere(dots).astype(np.int32)
    n = len(pts)
    if n == 0:
        return np.zeros(0), pts
    tree = cKDTree(pts)
    h, w = dots.shape
    u = np.ones(n, dtype=np.float64)  # the dot's own pixel
    for dy, dx, d, k in _disc_offsets(radius):
        p = pts + np.array([dy, dx], dtype=np.int32)
        inside = (p[:, 0] >= 0) & (p[:, 0] < h) & (p[:, 1] >= 0) & (p[:, 1] < w)
        if not inside.any():
            continue
        q = p[inside]
        dist, _ = tree.query(q, k=2)          # [own dot, next nearest]
        nearest_is_self = np.isclose(dist[:, 0], d, atol=1e-9)
        strict = nearest_is_self & (dist[:, 1] > dist[:, 0] + 1e-9)
        u[np.flatnonzero(inside)[strict]] += k
    return u, pts


def total_credit(u):
    """Expected T under a flat truth prior (E[T] over truth placements)."""
    return float(np.sum(u))


def choose_drop(dots, u, n_drop, rng, mode="unique"):
    """Indices of the dots to remove.

    mode='unique' : the n_drop smallest u (ties broken by the seeded rng)
    mode='random' : n_drop drawn uniformly from all dots (matched null)
    """
    n = int(dots.sum())
    if not 1 <= n_drop < n:
        raise ValueError(f"n_drop={n_drop} outside 1..{n-1}")
    if mode == "unique":
        order = np.lexsort((rng.random(n), u))
        return order[:n_drop]
    if mode == "random":
        return rng.choice(n, size=n_drop, replace=False)
    raise ValueError(f"unknown mode {mode!r}")


def block_density_cv(dots, footprint, block=BLOCK_PX_1KM):
    """CV of dot density over fixed blocks (report only, never a gate)."""
    h, w = dots.shape
    bh, bw = h // block, w // block
    dm = dots[: bh * block, : bw * block].reshape(bh, block, bw, block).sum((1, 3)).ravel()
    fm = footprint[: bh * block, : bw * block].reshape(bh, block, bw, block).sum((1, 3)).ravel()
    keep = fm > 0.5 * block * block
    dens = dm[keep] / fm[keep]
    if not keep.any() or dens.mean() == 0:
        return float("nan"), int(keep.sum())
    return float(dens.std() / dens.mean()), int(keep.sum())


def nn_distances(dots):
    pts = np.argwhere(dots)
    if len(pts) < 2:
        return np.zeros(len(pts))
    d, _ = cKDTree(pts).query(pts, k=2)
    return d[:, 1]


def build(dots, footprint, catalogue_mask, n_drop, rng, mode="unique",
          clearance_ring_px=3.0):
    """Return (variant dot mask, stats dict).  A drop-only edit: no new dots."""
    dots = np.asarray(dots, dtype=bool)
    n_before = int(dots.sum())
    u, pts = unique_credit(dots)
    drop_idx = choose_drop(dots, u, n_drop, rng, mode=mode)
    kept = np.ones(n_before, dtype=bool)
    kept[drop_idx] = False
    variant = np.zeros_like(dots)
    variant[pts[kept, 0], pts[kept, 1]] = True
    n_after = int(variant.sum())
    assert n_after == n_before - n_drop, "drop count mismatch"

    d_cat = ndi.distance_transform_edt(~np.asarray(catalogue_mask, dtype=bool))
    nn = nn_distances(dots)
    u_drop = u[drop_idx]
    u_keep = u[kept]
    dropped_pts = pts[drop_idx]

    stats = {
        "mode": mode,
        "n_before": n_before,
        "n_after": n_after,
        "n_dropped": int(n_drop),
        "pct_changed": 100.0 * n_drop / n_before,
        # the ranking's own quantity: expected credit lost under a flat prior
        "unique_credit_total_before": total_credit(u),
        "unique_credit_total_after": total_credit(u_keep),
        "unique_credit_lost": total_credit(u_drop),
        "unique_credit_lost_frac": float(u_drop.sum() / u.sum()),
        "u_mean_all": float(u.mean()),
        "u_mean_dropped": float(u_drop.mean()),
        "u_mean_kept": float(u_keep.mean()),
        "u_min_kept": float(u_keep.min()),
        # what the dropped set looks like, so the confound is measured
        "dropped_frac_within_3px_catalogue": float((d_cat[dropped_pts[:, 0], dropped_pts[:, 1]] < clearance_ring_px).mean()),
        "dropped_frac_within_10px_catalogue": float((d_cat[dropped_pts[:, 0], dropped_pts[:, 1]] < 10.0).mean()),
        "dropped_mean_dcat_px": float(d_cat[dropped_pts[:, 0], dropped_pts[:, 1]].mean()),
        "parent_frac_within_3px_catalogue": float((d_cat[dots] < clearance_ring_px).mean()),
        "parent_mean_dcat_px": float(d_cat[dots].mean()),
        "dropped_mean_nn_px": float(nn[drop_idx].mean()),
        "dropped_median_nn_px": float(np.median(nn[drop_idx])),
        "parent_mean_nn_px": float(nn.mean()),
        "parent_median_nn_px": float(np.median(nn)),
        # report-only geometry
        "cv_1km_before": block_density_cv(dots, footprint, BLOCK_PX_1KM)[0],
        "cv_1km_after": block_density_cv(variant, footprint, BLOCK_PX_1KM)[0],
        "cv_2p5km_before": block_density_cv(dots, footprint, BLOCK_PX_2P5KM)[0],
        "cv_2p5km_after": block_density_cv(variant, footprint, BLOCK_PX_2P5KM)[0],
        "cv_5km_before": block_density_cv(dots, footprint, BLOCK_PX_5KM)[0],
        "cv_5km_after": block_density_cv(variant, footprint, BLOCK_PX_5KM)[0],
        "mass_before": float(n_before),
        "mass_after": float(n_after),
        "catalogue_clearance_min_px_after": float(d_cat[variant].min()) if variant.any() else None,
        "catalogue_clearance_violations_after": int((d_cat[variant] < clearance_ring_px).sum()),
    }
    return variant, stats


def predicted_delta(stats, dti_parent=0.2778, D_lo=1.0e4, D_hi=2.0e4, k_lo=0.0, k_hi=0.12):
    """MODEL band for a drop-only edit, from dDTI = -n*(k - 0.2*DTI)/D.

    k is the *actual* kernel credit of the dropped dots, which is not
    observable locally; the band spans k from 0 (pure wasted mass: maximum
    gain) to 0.12 (the dropped set is on truth: a loss).  D is the DTI
    denominator, bracketed from the one measured collar step in the lineage
    (2,545 dots removed for +0.007 => D ~ 1.0e4..2.0e4).
    """
    n = stats["n_dropped"]
    thr = 0.2 * dti_parent
    out = {}
    for tag, D in (("D_lo", D_lo), ("D_hi", D_hi)):
        out[tag] = {
            "k_0": -n * (k_lo - thr) / D,
            "k_thr": -n * (thr - thr) / D,
            "k_hi": -n * (k_hi - thr) / D,
        }
    # central: k = 0.055 (just at break-even, i.e. the ranking is uninformative)
    out["central"] = -n * (0.055 - thr) / 1.5e4
    return out
