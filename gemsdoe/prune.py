"""PRUNE axis: evaluate distance-to-catalogue exclusion collars on Parent R0.

Structural and Metric Context
-----------------------------
1. Parent R0 (h33-h33-2-b2) was created by pruning the unpruned d28 dot field
   (44,090 dots) at Euclidean catalogue distance d_cat > 2.0 px (200 m),
   yielding 37,654 dots. This raised the claimed score from 0.2600 to 0.2778.
2. The DrivenData / DOE competition rules state that known USGS/INGENIOUS faults
   are masked pixel-exactly, but 'new-fault truth can lie within 300 m of known
   traces' (extensional step-overs, tip splays, breaching faults).
3. The evaluation metric uses a triangular kernel of radius R = 300 m (3 px).
   A dot at d_cat <= 3.0 px has part of its kernel overlapping the masked
   catalogue boundary, potentially suffering false-positive mass penalty S with
   reduced T credit if near-catalogue new faults are scarce.
4. GeoDAWN aeromagnetic and gravity survey flight lines are spaced at 400 m,
   meaning gradient enhancement features within 400 m of large-displacement
   known faults may contain flight-line interpolation smear.

Variants Defined in This Module
-------------------------------
- c1p0 (1.0 px collar / 100 m):
  Swaps in the 2,545 dots from d28 with 1.0 < d_cat <= 2.0 px that R0 pruned,
  while dropping the 2,545 lowest-marginal-gain dots in R0 (under flat-truth
  DTI unique credit) to hold count fixed at 37,654 dots (6.76% changed).
  Tests whether near-fault step-overs and splays carry new-fault truth.

- c3p0 (3.0 px collar / 300 m):
  Removes the 2,171 dots in R0 with 2.0 < d_cat <= 3.0 px that sit within the
  300 m triangular kernel radius of known faults. Refills 2,171 dots onto
  corroborated h19_5 fault ridges outside the 300 m collar (d_cat > 3.0 px,
  spacing >= 2.0 px) via greedy farthest-point placement (5.77% changed).
  Tests whether full kernel clearance eliminates boundary truncation loss.

- c4p0 (4.0 px collar / 400 m):
  Removes the 3,825 dots in R0 with 2.0 < d_cat <= 4.0 px (the 400 m flight-line
  smear corridor). Refills 3,825 dots onto corroborated h19_5 fault ridges
  outside the 400 m collar (d_cat > 4.0 px, spacing >= 2.0 px) (10.16% changed).
  Tests whether wide clearance purges 400 m flight-line interpolation smear.

Everything here is deterministic: fixed inputs + fixed seed -> identical bytes.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi

from . import mass

MIN_REFILL_SEP_PX = 2.0
BLOCK_PX_1KM = 10
BLOCK_PX_5KM = 50
BLOCK_PX_12P8KM = 128


def compute_catalogue_distance(catalogue_mask: np.ndarray) -> np.ndarray:
    """Euclidean distance in pixels from each cell to nearest catalogue pixel."""
    cat = np.asarray(catalogue_mask, dtype=bool)
    return ndi.distance_transform_edt(~cat)


def select_swapin_dots(
    d28_dots: np.ndarray,
    d_cat: np.ndarray,
    min_dist: float = 1.0,
    max_dist: float = 2.0,
) -> np.ndarray:
    """Dots in d28 that lie strictly within min_dist < d_cat <= max_dist."""
    d28 = np.asarray(d28_dots, dtype=bool)
    return d28 & (d_cat > min_dist) & (d_cat <= max_dist)


def refill_greedy_farthest(
    candidate_mask: np.ndarray,
    existing_dots: np.ndarray,
    n_needed: int,
    min_sep_px: float = MIN_REFILL_SEP_PX,
) -> np.ndarray:
    """Greedy farthest-point placement on candidate_mask.

    Iteratively picks the candidate site farthest from all existing and newly
    placed dots, enforcing minimum internal separation of min_sep_px.
    Deterministic: ties broken by row-major order (lexsort).
    """
    cand = np.asarray(candidate_mask, dtype=bool)
    exist = np.asarray(existing_dots, dtype=bool)
    if n_needed <= 0:
        return np.zeros((0, 2), dtype=np.int32)

    d_exist = ndi.distance_transform_edt(~exist)
    legal = cand & (d_exist >= min_sep_px - 1e-6)
    ys, xs = np.nonzero(legal)
    if len(ys) < n_needed:
        raise ValueError(
            f"Insufficient candidate capacity: {len(ys)} legal pixels for {n_needed} refill dots"
        )

    # Order candidates descending by distance to existing dots; break ties by (y, x)
    order = np.lexsort((xs, ys, -d_exist[ys, xs]))

    h, w = cand.shape
    r_win = int(np.ceil(min_sep_px))
    min_sep_sq = (min_sep_px - 1e-6) ** 2
    blocked = np.zeros((h, w), dtype=bool)

    placed: list[tuple[int, int]] = []
    for idx in order:
        y, x = int(ys[idx]), int(xs[idx])
        if blocked[y, x]:
            continue
        placed.append((y, x))
        if len(placed) >= n_needed:
            break
        y0, y1 = max(0, y - r_win), min(h, y + r_win + 1)
        x0, x1 = max(0, x - r_win), min(w, x + r_win + 1)
        dys, dxs = np.mgrid[y0 - y : y1 - y, x0 - x : x1 - x]
        mask = (dys * dys + dxs * dxs) < min_sep_sq
        blocked[y0:y1, x0:x1] |= mask

    if len(placed) < n_needed:
        raise ValueError(
            f"Greedy farthest-point placement produced {len(placed)} of {n_needed} dots"
        )
    return np.array(placed, dtype=np.int32)


def block_density_cv(dots: np.ndarray, footprint: np.ndarray, block_px: int = BLOCK_PX_5KM) -> float:
    """CV of dot density over blocks with >= 50% footprint coverage (report-only)."""
    h, w = dots.shape
    bh, bw = h // block_px, w // block_px
    d_m = dots[: bh * block_px, : bw * block_px].reshape(bh, block_px, bw, block_px).sum((1, 3)).ravel()
    f_m = footprint[: bh * block_px, : bw * block_px].reshape(bh, block_px, bw, block_px).sum((1, 3)).ravel()
    keep = f_m >= 0.5 * block_px * block_px
    if not keep.any():
        return float("nan")
    dens = d_m[keep] / f_m[keep]
    m = float(dens.mean())
    if m == 0.0:
        return 0.0
    return float(dens.std() / m)


def build_prune(
    mode: str,
    parent_dots: np.ndarray,
    d28_dots: np.ndarray,
    h19_5_mask: np.ndarray,
    catalogue_mask: np.ndarray,
    footprint: np.ndarray,
    seed: int = 20261024,
) -> tuple[np.ndarray, dict]:
    """Build one PRUNE variant ('c1p0', 'c3p0', or 'c4p0').

    Returns:
        (variant_dots_mask, stats_dict)
    """
    if mode not in ("c1p0", "c3p0", "c4p0"):
        raise ValueError(f"Unknown PRUNE mode: {mode!r} (expected 'c1p0', 'c3p0', or 'c4p0')")

    foot = np.asarray(footprint, dtype=bool)
    cat = np.asarray(catalogue_mask, dtype=bool) & foot
    r0 = np.asarray(parent_dots, dtype=bool) & foot
    d28 = np.asarray(d28_dots, dtype=bool) & foot
    h19 = np.asarray(h19_5_mask, dtype=bool) & foot

    n_r0 = int(r0.sum())
    d_cat = compute_catalogue_distance(cat)

    rng = np.random.default_rng(seed)
    cv5_before = block_density_cv(r0, foot, BLOCK_PX_5KM)
    cv12_before = block_density_cv(r0, foot, BLOCK_PX_12P8KM)

    if mode == "c1p0":
        # 1.0 px collar: restore the 2,545 dots in d28 with 1.0 < d_cat <= 2.0 px
        swapin_mask = select_swapin_dots(d28, d_cat, min_dist=1.0, max_dist=2.0)
        n_swap = int(swapin_mask.sum())
        if n_swap == 0:
            raise RuntimeError("No swap-in dots found for c1p0 collar")

        # Drop n_swap lowest-marginal-gain dots in R0 under flat-truth unique credit
        u_r0, pts_r0 = mass.unique_credit(r0)
        drop_idx = mass.choose_drop(r0, u_r0, n_swap, rng, mode="unique")
        drop_mask = np.zeros_like(r0)
        drop_mask[pts_r0[drop_idx, 0], pts_r0[drop_idx, 1]] = True

        variant = (r0 & (~drop_mask)) | swapin_mask
        n_moved = n_swap
        n_removed = n_swap
        n_added = n_swap
        collar_spec_px = 1.0
        details = f"swap in {n_swap} dots (1.0 < d_cat <= 2.0 px); drop {n_swap} lowest-gain R0 dots"

    elif mode == "c3p0":
        # 3.0 px collar: remove dots in R0 with d_cat <= 3.0 px (2,171 dots)
        rem_mask = r0 & (d_cat <= 3.0)
        n_rem = int(rem_mask.sum())
        kept = r0 & (~rem_mask)

        # Refill n_rem dots onto h19 outside the 300 m collar
        cand_mask = h19 & foot & (~cat) & (d_cat > 3.0)
        added_pts = refill_greedy_farthest(cand_mask, kept, n_rem, min_sep_px=MIN_REFILL_SEP_PX)

        variant = kept.copy()
        variant[added_pts[:, 0], added_pts[:, 1]] = True
        n_moved = n_rem
        n_removed = n_rem
        n_added = n_rem
        collar_spec_px = 3.0
        details = f"prune {n_rem} dots (d_cat <= 3.0 px); refill {n_rem} dots on h19 (d_cat > 3.0 px)"

    elif mode == "c4p0":
        # 4.0 px collar: remove dots in R0 with d_cat <= 4.0 px (3,825 dots)
        rem_mask = r0 & (d_cat <= 4.0)
        n_rem = int(rem_mask.sum())
        kept = r0 & (~rem_mask)

        # Refill n_rem dots onto h19 outside the 400 m collar
        cand_mask = h19 & foot & (~cat) & (d_cat > 4.0)
        added_pts = refill_greedy_farthest(cand_mask, kept, n_rem, min_sep_px=MIN_REFILL_SEP_PX)

        variant = kept.copy()
        variant[added_pts[:, 0], added_pts[:, 1]] = True
        n_moved = n_rem
        n_removed = n_rem
        n_added = n_rem
        collar_spec_px = 4.0
        details = f"prune {n_rem} dots (d_cat <= 4.0 px); refill {n_rem} dots on h19 (d_cat > 4.0 px)"

    n_variant = int(variant.sum())
    if n_variant != n_r0:
        raise AssertionError(f"Count mismatch: variant has {n_variant} dots, expected {n_r0}")

    cat_mass = int((variant & cat).sum())
    if cat_mass != 0:
        raise AssertionError(f"Catalogue violation: {cat_mass} dots land on catalogue pixels")

    # Symmetric difference and displacement stats
    diff_mask = variant ^ r0
    sym_diff = int(diff_mask.sum())
    pct_changed = 100.0 * (sym_diff / 2) / n_r0
    pct_symdiff = 100.0 * sym_diff / n_r0

    # Nearest catalogue distance of variant dots
    d_variant_cat = d_cat[variant]
    min_dcat_variant = float(d_variant_cat.min())

    cv5_after = block_density_cv(variant, foot, BLOCK_PX_5KM)
    cv12_after = block_density_cv(variant, foot, BLOCK_PX_12P8KM)

    stats = {
        "mode": mode,
        "collar_spec_px": collar_spec_px,
        "n_dots": n_variant,
        "n_moved": n_moved,
        "n_removed": n_removed,
        "n_added": n_added,
        "pct_changed": pct_changed,
        "pct_symmetric_diff": pct_symdiff,
        "min_catalogue_distance_px": min_dcat_variant,
        "catalogue_mass": cat_mass,
        "block_cv_5km_before": cv5_before,
        "block_cv_5km_after": cv5_after,
        "block_cv_12p8km_before": cv12_before,
        "block_cv_12p8km_after": cv12_after,
        "details": details,
    }
    return variant, stats
