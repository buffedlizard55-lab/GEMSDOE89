"""CONCENTRATION axis: reallocate dots from lowest-prior to highest-prior km-scale blocks.

Single-variable controlled edit of Parent R0 (h33-h33-2-b2, 37,654 unit-mass dots):
  * Global dot count is held strictly fixed at 37,654 (zero MASS confound).
  * Inherited 2.0 < d_cat < 3.0 px diagonal collar dots (1,611 in R0) are frozen
    unchanged and 100 % of newly added dots obey d_cat >= 3.0 px inside the
    footprint (zero PRUNE confound; Hard Constraint 4).
  * Every newly added dot obeys R0's exact Euclidean suppression radius
    r_min = 2.8 px against all kept and newly placed dots (zero SPACING confound).
  * No existing surviving dot is shifted in place (zero SNAP confound).
  * Only km-scale block allocation changes: 10-20 % of R0's dots are removed from
    the lowest-prior 12.8 km x 12.8 km (128 x 128 px, half-tile) structural blocks
    and placed onto anisotropic strike-coherent geophysical/topographic ridges in
    the highest-prior 12.8 km blocks.

Why 12.8 km (128 px) blocks:
  1. Physical scale: Great Basin fault-interaction districts (relay ramps, step-overs,
     horse-tail terminations; Faulds & Hinz 2015) and GPS strain inversions operate at
     10-15 km wavelength, not 100 m pixel scale.
  2. Lineage CV signature (brief sec.5): across >=50 %-footprint 12.8 km blocks, R0's
     climb sits squarely inside the brief's 0.51-0.59 reference band
     (d28 = 0.518, solo-d2.8 = 0.537, R0 = 0.553).

Two orthogonal 12.8 km block priors (same grid, quotas, removal & placement rules):
  * 'interaction' : Faulds structural-interaction prior from existing_faults.tif ONLY
                    (rank-mean of fault-tip density, fault-junction density, and <=1 km
                    multi-strand step-over zone fraction; zero heat/vent inputs).
  * 'geodetic'    : Catalogue-free active crustal deformation prior from pinned
                    training_features.tif bands 4 (geod_2ndinv), 7 (geod_shearrate),
                    and 16 (ieq_n100a15); zero existing_faults.tif input to the prior.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from scipy.stats import rankdata

from . import mass, relief, snap

BLOCK_PX = 128                 # 12.8 km x 12.8 km structural-district block (half of 256-px tile)
MIN_SEP_PX = 2.8               # parent R0's exact dot_thin suppression radius
CATALOGUE_CLEARANCE_PX = 3.0   # Hard Constraint 4 on all newly placed dots
QUANTILE_SPLIT = (40.0, 60.0)  # bottom 40 % -> top 40 % of interior blocks (20 % buffer)
STEPOVER_RADIUS_PX = 10        # 1.0 km inter-strand step-over interaction radius

RIDGE_BANDS = (3, 5, 12, 19)   # tmi_hg, iso_grav_anom_slope, det_elev, det_elev_slope
GEOD_BANDS = (4, 7, 16)        # geod_2ndinv, geod_shearrate, ieq_n100a15


def _clean_band(raw: np.ndarray, foot: np.ndarray) -> np.ndarray:
    """Replace non-finite and <= -1e30 float32 sentinels with the footprint median."""
    v = foot & np.isfinite(raw) & (raw > -1e30)
    med = float(np.median(raw[v])) if v.any() else 0.0
    return np.where(v, raw, med).astype(np.float32)


def block_grid(shape: tuple[int, int], block_px: int = BLOCK_PX) -> tuple[np.ndarray, int, int, int]:
    """Return (pixel_block_id, bh, bw, n_blocks) tiling `shape` by `block_px`."""
    h, w = shape
    bh = (h + block_px - 1) // block_px
    bw = (w + block_px - 1) // block_px
    yy, xx = np.indices((h, w), dtype=np.int32)
    b_id = (yy // block_px) * bw + (xx // block_px)
    return b_id, bh, bw, bh * bw


def linear_concavity(
    field: np.ndarray,
    foot: np.ndarray,
    sigmas: tuple[float, ...] = (1.0, 2.0, 3.5),
) -> np.ndarray:
    """Multi-scale anisotropic concave-up break-in-slope / ridge curvature in [0, 1].

    Subtracts 0.5 * |lambda_along| from lambda_across so circular volcanic cones,
    craters, and isotropic DEM pits are suppressed relative to elongated fault scarps.
    """
    best = np.zeros(field.shape, dtype=np.float32)
    if not foot.any():
        return best
    for s in sigmas:
        sm = ndi.gaussian_filter(field.astype(np.float32), s, mode="nearest")
        gyy = ndi.sobel(ndi.sobel(sm, axis=0), axis=0)
        gxx = ndi.sobel(ndi.sobel(sm, axis=1), axis=1)
        gxy = ndi.sobel(ndi.sobel(sm, axis=0), axis=1)
        tr = gxx + gyy
        det_h = np.hypot(gxx - gyy, 2.0 * gxy)
        l_across = 0.5 * (tr + det_h)
        l_along = 0.5 * (tr - det_h)
        lin = np.maximum(0.0, l_across - 0.5 * np.abs(l_along))
        p99 = float(np.percentile(lin[foot], 99.0)) + 1e-9
        best = np.maximum(best, np.clip(lin / p99, 0.0, 3.0) / 3.0)
    best[~foot] = 0.0
    return best


def strike_coherence(field: np.ndarray, foot: np.ndarray, sigma_grad: float = 1.2, sigma_tensor: float = 6.0) -> np.ndarray:
    """Structure-tensor orientation coherence in [0, 1] at ~600 m (6 px) scale."""
    sm = ndi.gaussian_filter(field.astype(np.float32), sigma_grad, mode="nearest")
    gy = ndi.sobel(sm, axis=0)
    gx = ndi.sobel(sm, axis=1)
    jyy = ndi.gaussian_filter(gy * gy, sigma_tensor, mode="nearest")
    jxx = ndi.gaussian_filter(gx * gx, sigma_tensor, mode="nearest")
    jyx = ndi.gaussian_filter(gy * gx, sigma_tensor, mode="nearest")
    coh = np.hypot(jxx - jyy, 2.0 * jyx) / (jxx + jyy + 1e-6)
    coh = np.clip(coh, 0.0, 1.0).astype(np.float32)
    coh[~foot] = 0.0
    return coh


def corroborated_ridge_response(bands: dict[int, np.ndarray], footprint: np.ndarray) -> tuple[np.ndarray, dict]:
    """Unsupervised multi-layer strike-coherent fault-scarp/potential-field ridge response.

    Uses ONLY local physical bands (b3 tmi_hg, b5 iso_grav_anom_slope, b12 det_elev,
    b19 det_elev_slope); zero labels and zero geodetic/catalogue block-prior bands enter.
    """
    foot = np.asarray(footprint, dtype=bool)
    b3 = _clean_band(bands[3], foot)
    b5 = _clean_band(bands[5], foot)
    b12 = _clean_band(bands[12], foot)
    b19 = _clean_band(bands[19], foot)

    c_toe = linear_concavity(b12, foot, sigmas=(1.0, 2.0, 3.5))
    c_crest = linear_concavity(-b19, foot, sigmas=(1.0, 2.0))
    u_grav = snap.robust_unit(b5, foot)
    u_tmi = snap.robust_unit(np.log1p(np.maximum(b3, 0.0)), foot)
    coh = strike_coherence(b12, foot, sigma_grad=1.2, sigma_tensor=6.0)

    corrob = ((0.50 * c_toe + 0.25 * c_crest + 0.15 * u_grav + 0.10 * u_tmi) * (0.5 + 0.5 * coh)).astype(np.float32)
    corrob[~foot] = 0.0
    diag = {
        "bands_used": {"3": "tmi_hg", "5": "iso_grav_anom_slope", "12": "det_elev", "19": "det_elev_slope"},
        "formula": "(0.50*linear_concavity(det_elev) + 0.25*linear_concavity(-det_elev_slope) + 0.15*robust_unit(iso_grav_anom_slope) + 0.10*robust_unit(log1p(tmi_hg))) * (0.5 + 0.5*strike_coherence_600m(det_elev))",
        "mean_in_footprint": float(corrob[foot].mean()) if foot.any() else 0.0,
        "p99_in_footprint": float(np.percentile(corrob[foot], 99.0)) if foot.any() else 0.0,
    }
    return corrob, diag


def interaction_block_prior(
    catalogue_mask: np.ndarray,
    footprint: np.ndarray,
    block_px: int = BLOCK_PX,
    stepover_radius_px: int = STEPOVER_RADIUS_PX,
) -> tuple[np.ndarray, dict]:
    """Faulds-type structural-interaction block prior from known fault geometry ONLY.

    Equal-weight average of empirical block percentile ranks of:
      1. fault termination density (1 neighbour on 8-connected catalogue),
      2. fault branch/intersection density (>=3 neighbours on 8-connected catalogue),
      3. <=1 km (10 px) multi-strand step-over zone fraction (>=2 distinct catalogue components).
    """
    foot = np.asarray(footprint, dtype=bool)
    cat = np.asarray(catalogue_mask, dtype=bool) & foot
    b_id, bh, bw, n_blocks = block_grid(foot.shape, block_px)
    foot_cnt = np.bincount(b_id[foot], minlength=n_blocks)
    active = foot_cnt > 0
    area = np.maximum(foot_cnt, 1).astype(np.float64)

    lbl, n_comp = ndi.label(cat, structure=np.ones((3, 3), dtype=np.int8))
    ker = np.ones((3, 3), dtype=np.int16)
    ker[1, 1] = 0
    nbr = ndi.convolve(cat.astype(np.int16), ker, mode="constant", cval=0)
    tips = cat & (nbr == 1)
    juncs = cat & (nbr >= 3)

    r = int(stepover_radius_px)
    yy_k, xx_k = np.mgrid[-r : r + 1, -r : r + 1]
    disc = (yy_k * yy_k + xx_k * xx_k) <= r * r
    max_lbl = ndi.maximum_filter(lbl, footprint=disc, mode="constant", cval=0)
    inf_lbl = n_comp + 999
    min_lbl = ndi.minimum_filter(np.where(lbl > 0, lbl, inf_lbl), footprint=disc, mode="constant", cval=inf_lbl)
    stepover = foot & (max_lbl > 0) & (min_lbl < inf_lbl) & (max_lbl != min_lbl)

    tip_d = np.bincount(b_id[tips], minlength=n_blocks) / area
    junc_d = np.bincount(b_id[juncs], minlength=n_blocks) / area
    step_d = np.bincount(b_id[stepover], minlength=n_blocks) / area

    score = np.zeros(n_blocks, dtype=np.float64)
    n_act = max(int(active.sum()), 1)
    for comp in (tip_d, junc_d, step_d):
        rk = np.zeros(n_blocks, dtype=np.float64)
        if active.any():
            rk[active] = rankdata(comp[active], method="average") / n_act
        score += rk / 3.0

    diag = {
        "prior_mode": "interaction",
        "block_px": int(block_px),
        "block_km": round(0.1 * block_px, 2),
        "grid_blocks": [bh, bw],
        "active_blocks": int(active.sum()),
        "catalogue_components": int(n_comp),
        "catalogue_tips_px": int(tips.sum()),
        "catalogue_junctions_px": int(juncs.sum()),
        "stepover_zone_px": int(stepover.sum()),
        "stepover_radius_px": int(stepover_radius_px),
    }
    return score, diag


def geodetic_block_prior(
    bands: dict[int, np.ndarray],
    footprint: np.ndarray,
    block_px: int = BLOCK_PX,
) -> tuple[np.ndarray, dict]:
    """Catalogue-free active crustal deformation block prior (GPS strain + seismicity)."""
    foot = np.asarray(footprint, dtype=bool)
    b4 = _clean_band(bands[4], foot)
    b7 = _clean_band(bands[7], foot)
    b16 = _clean_band(bands[16], foot)

    u_g2 = snap.robust_unit(b4, foot)
    u_gs = snap.robust_unit(b7, foot)
    u_eq = snap.robust_unit(np.log1p(np.maximum(b16, 0.0)), foot)
    px_score = (u_g2 + u_gs + u_eq) / 3.0

    b_id, bh, bw, n_blocks = block_grid(foot.shape, block_px)
    foot_cnt = np.bincount(b_id[foot], minlength=n_blocks)
    active = foot_cnt > 0
    area = np.maximum(foot_cnt, 1).astype(np.float64)

    score = np.zeros(n_blocks, dtype=np.float64)
    if active.any():
        w_sum = np.bincount(b_id[foot], weights=px_score[foot], minlength=n_blocks)
        score[active] = w_sum[active] / area[active]

    diag = {
        "prior_mode": "geodetic",
        "block_px": int(block_px),
        "block_km": round(0.1 * block_px, 2),
        "grid_blocks": [bh, bw],
        "active_blocks": int(active.sum()),
        "bands_used": {"4": "geod_2ndinv", "7": "geod_shearrate", "16": "ieq_n100a15"},
        "uses_catalogue": False,
    }
    return score, diag


def _integer_quotas(weights: np.ndarray, total: int, caps: np.ndarray | None = None) -> np.ndarray:
    """Deterministic largest-remainder integer allocation summing to `total`."""
    if total <= 0:
        return np.zeros(len(weights), dtype=np.int32)
    w = np.maximum(np.asarray(weights, dtype=np.float64), 0.0)
    if w.sum() <= 0:
        w = np.ones_like(w)
    raw = total * w / w.sum()
    q = np.floor(raw).astype(np.int32)
    if caps is not None:
        caps_i = np.asarray(caps, dtype=np.int32)
        if int(caps_i.sum()) < total:
            raise ValueError(f"total capacity {int(caps_i.sum())} < requested {total}")
        q = np.minimum(q, caps_i)
    short = total - int(q.sum())
    if short > 0:
        rem = raw - np.floor(raw)
        # Deterministic tie-break by index
        order = np.argsort(-rem, kind="mergesort")
        while short > 0:
            progressed = False
            for idx in order:
                if short == 0:
                    break
                if caps is None or q[idx] < caps[idx]:
                    q[idx] += 1
                    short -= 1
                    progressed = True
            if not progressed:
                raise RuntimeError("unable to allocate integer quotas within block capacities")
    return q


def build(
    parent_dots: np.ndarray,
    footprint: np.ndarray,
    catalogue_mask: np.ndarray,
    blk_score: np.ndarray,
    corrob_ridge: np.ndarray,
    h19_5_mask: np.ndarray | None = None,
    fraction: float = 0.10,
    block_px: int = BLOCK_PX,
    q_split: tuple[float, float] = QUANTILE_SPLIT,
    min_sep_px: float = MIN_SEP_PX,
    clearance_px: float = CATALOGUE_CLEARANCE_PX,
    det_elev: np.ndarray | None = None,
) -> tuple[np.ndarray, dict]:
    """Reallocate `fraction` of `parent_dots` from lowest-prior to highest-prior blocks.

    Deterministic (mergesort + row-major index tie-breaking; no RNG required).
    Preserves exact dot count, freezes inherited <3 px collar dots, enforces
    d_cat >= 3.0 px and inter-dot separation >= 2.8 px on every added dot.
    """
    foot = np.asarray(footprint, dtype=bool)
    cat = np.asarray(catalogue_mask, dtype=bool) & foot
    r0 = np.asarray(parent_dots, dtype=bool) & foot
    h19 = (np.asarray(h19_5_mask, dtype=bool) & foot) if h19_5_mask is not None else np.zeros_like(foot)
    corrob = np.asarray(corrob_ridge, dtype=np.float32)

    h, w = foot.shape
    n_dots = int(r0.sum())
    if not (0.0 < fraction <= 0.50):
        raise ValueError(f"fraction {fraction} must lie in (0, 0.50]")
    n_move = int(round(fraction * n_dots))
    if n_move <= 0:
        raise ValueError("n_move resolved to 0 dots")

    b_id, bh, bw, n_blocks = block_grid((h, w), block_px)
    if len(blk_score) != n_blocks:
        raise ValueError(f"blk_score length {len(blk_score)} != {n_blocks}")

    foot_cnt = np.bincount(b_id[foot], minlength=n_blocks)
    active_blk = foot_cnt > 0
    valid_blk = foot_cnt >= 0.50 * block_px * block_px
    ref_blk = valid_blk if int(valid_blk.sum()) >= 3 else active_blk

    q_lo, q_hi = np.percentile(blk_score[ref_blk], list(q_split))
    src_blks = np.flatnonzero(active_blk & (blk_score <= q_lo))
    tgt_blks = np.flatnonzero(active_blk & (blk_score >= q_hi))
    # Ensure disjoint source and target sets even on degenerate constant/tied synthetic inputs
    overlap = np.intersect1d(src_blks, tgt_blks)
    if len(overlap) > 0:
        ordered = np.flatnonzero(active_blk)[np.argsort(blk_score[active_blk], kind="mergesort")]
        half = max(1, len(ordered) // 2)
        src_blks = ordered[:half]
        tgt_blks = ordered[-half:]

    d_cat = ndi.distance_transform_edt(~cat)
    elig_src = r0 & (d_cat >= clearance_px)
    src_elig_cnt = np.bincount(b_id[elig_src], minlength=n_blocks)
    if int(src_elig_cnt[src_blks].sum()) < n_move:
        raise ValueError(
            f"source blocks hold {int(src_elig_cnt[src_blks].sum())} removable dots, need {n_move}"
        )

    # ---- 1. Source removal inside lowest-prior blocks -----------------------
    u_cred, pts_r0 = mass.unique_credit(r0)
    u_map = np.zeros((h, w), dtype=np.float32)
    if len(pts_r0):
        u_map[pts_r0[:, 0], pts_r0[:, 1]] = u_cred.astype(np.float32)

    s_max = float(blk_score[src_blks].max()) + 1e-9
    w_src = src_elig_cnt[src_blks].astype(np.float64) * (1.05 - 0.50 * (blk_score[src_blks] / s_max))
    q_rem = _integer_quotas(w_src, n_move, caps=src_elig_cnt[src_blks])

    rem_mask = np.zeros((h, w), dtype=bool)
    for bi, k_rem in zip(src_blks.tolist(), q_rem.tolist()):
        if k_rem <= 0:
            continue
        by, bx = divmod(bi, bw)
        y0, y1 = by * block_px, min(h, (by + 1) * block_px)
        x0, x1 = bx * block_px, min(w, (bx + 1) * block_px)
        sy, sx = np.nonzero(elig_src[y0:y1, x0:x1])
        sc = 0.5 * rankdata(u_map[y0 + sy, x0 + sx], method="ordinal") + 0.5 * rankdata(
            corrob[y0 + sy, x0 + sx], method="ordinal"
        )
        pick = np.argsort(sc, kind="mergesort")[:k_rem]
        rem_mask[y0 + sy[pick], x0 + sx[pick]] = True

    kept = r0 & (~rem_mask)

    # ---- 2. Target placement inside highest-prior blocks --------------------
    tgt_order = np.argsort(-blk_score[tgt_blks], kind="mergesort")
    tgt_blks = tgt_blks[tgt_order]
    span_hi = max(float(blk_score[ref_blk].max()) - float(q_hi), 1e-6)
    excess = np.clip((blk_score[tgt_blks] - float(q_hi)) / span_hi, 0.0, 2.0)
    w_tgt = foot_cnt[tgt_blks].astype(np.float64) * (0.50 + excess)
    q_add = _integer_quotas(w_tgt, n_move, caps=None)

    variant = kept.copy()
    r_pad = int(np.ceil(min_sep_px)) + 2
    r_win = int(np.floor(min_sep_px))
    min_sep_sq = (min_sep_px - 1e-6) ** 2

    def _fill_block(bi: int, need: int) -> int:
        if need <= 0:
            return 0
        by, bx = divmod(bi, bw)
        y0, y1 = by * block_px, min(h, (by + 1) * block_px)
        x0, x1 = bx * block_px, min(w, (bx + 1) * block_px)
        py0, py1 = max(0, y0 - r_pad), min(h, y1 + r_pad)
        px0, px1 = max(0, x0 - r_pad), min(w, x1 + r_pad)
        sub_var = variant[py0:py1, px0:px1]
        if sub_var.any():
            d_loc = ndi.distance_transform_edt(~sub_var)[y0 - py0 : y1 - py0, x0 - px0 : x1 - px0]
        else:
            d_loc = np.full((y1 - y0, x1 - x0), 999.0, dtype=np.float64)
        cand = foot[y0:y1, x0:x1] & (d_cat[y0:y1, x0:x1] >= clearance_px) & (d_loc >= min_sep_px - 1e-6)
        cy, cx = np.nonzero(cand)
        if len(cy) == 0:
            return 0
        sc = corrob[y0 + cy, x0 + cx] + 0.50 * h19[y0 + cy, x0 + cx].astype(np.float32)
        order = np.argsort(-sc, kind="mergesort")
        placed = 0
        for idx in order:
            gy_i = y0 + int(cy[idx])
            gx_i = x0 + int(cx[idx])
            wy0, wy1 = max(0, gy_i - r_win), min(h, gy_i + r_win + 1)
            wx0, wx1 = max(0, gx_i - r_win), min(w, gx_i + r_win + 1)
            oy, ox = np.nonzero(variant[wy0:wy1, wx0:wx1])
            if len(oy) and np.any((wy0 + oy - gy_i) ** 2 + (wx0 + ox - gx_i) ** 2 < min_sep_sq):
                continue
            variant[gy_i, gx_i] = True
            placed += 1
            if placed >= need:
                break
        return placed

    leftover = 0
    for bi, k_add in zip(tgt_blks.tolist(), q_add.tolist()):
        need = k_add + leftover
        placed = _fill_block(bi, need)
        leftover = need - placed

    if leftover > 0:
        for bi in tgt_blks.tolist():
            if leftover == 0:
                break
            leftover -= _fill_block(bi, leftover)

    if leftover > 0 or int(variant.sum()) != n_dots:
        raise RuntimeError(f"target capacity shortfall: leftover={leftover}, dots={int(variant.sum())}/{n_dots}")

    added = variant & (~r0)
    removed = r0 & (~variant)
    n_added = int(added.sum())
    n_removed = int(removed.sum())
    sym_diff = int((r0 ^ variant).sum())

    if n_added > 0 and n_removed > 0:
        disp, _ = cKDTree(np.argwhere(added)).query(np.argwhere(removed))
    else:
        disp = np.zeros(0, dtype=np.float64)

    nn_before, _ = relief.nearest_neighbour_distance(r0)
    nn_after, var_pts = relief.nearest_neighbour_distance(variant)
    is_added_pt = added[var_pts[:, 0], var_pts[:, 1]] if len(var_pts) else np.zeros(0, dtype=bool)
    added_min_nn = float(nn_after[is_added_pt].min()) if is_added_pt.any() else None

    src_px_mask = np.isin(b_id, src_blks) & foot
    tgt_px_mask = np.isin(b_id, tgt_blks) & foot

    relief_terciles = None
    if det_elev is not None:
        dom = foot & np.isfinite(det_elev) & (det_elev > -1e30)
        if dom.any():
            cls, _ = relief.define_classes(det_elev, dom)
            relief_terciles = {
                "before": [int((r0 & (cls == c)).sum()) for c in (0, 1, 2)],
                "after": [int((variant & (cls == c)).sum()) for c in (0, 1, 2)],
            }

    stats = {
        "block_px": int(block_px),
        "block_km": round(0.1 * block_px, 2),
        "quantile_split": [float(q_split[0]), float(q_split[1])],
        "q_lo_cut": float(q_lo),
        "q_hi_cut": float(q_hi),
        "source_blocks": int(len(src_blks)),
        "target_blocks": int(len(tgt_blks)),
        "interior_blocks_ge50pct_footprint": int(valid_blk.sum()),
        "fraction_requested": float(fraction),
        "n_dots": n_dots,
        "n_moved": n_added,
        "n_added": n_added,
        "n_removed": n_removed,
        "pct_changed": round(100.0 * n_added / max(1, n_dots), 4),
        "symmetric_diff_dots": sym_diff,
        "pct_symmetric_diff": round(100.0 * sym_diff / max(1, n_dots), 4),
        "source_dots_before": int((r0 & src_px_mask).sum()),
        "source_dots_after": int((variant & src_px_mask).sum()),
        "target_dots_before": int((r0 & tgt_px_mask).sum()),
        "target_dots_after": int((variant & tgt_px_mask).sum()),
        "added_min_catalogue_clearance_px": float(d_cat[added].min()) if added.any() else None,
        "collar_lt3px_before": int((d_cat[r0] < clearance_px).sum()),
        "collar_lt3px_after": int((d_cat[variant] < clearance_px).sum()),
        "added_min_interdot_sep_px": added_min_nn,
        "nn_median_before_px": float(np.median(nn_before)) if len(nn_before) else 0.0,
        "nn_median_after_px": float(np.median(nn_after)) if len(nn_after) else 0.0,
        "mean_displacement_px": float(disp.mean()) if len(disp) else 0.0,
        "median_displacement_px": float(np.median(disp)) if len(disp) else 0.0,
        "removed_mean_corrob_ridge": float(corrob[removed].mean()) if removed.any() else 0.0,
        "added_mean_corrob_ridge": float(corrob[added].mean()) if added.any() else 0.0,
        "parent_mean_corrob_ridge": float(corrob[r0].mean()) if r0.any() else 0.0,
        "block_cv_12p8km_before": round(relief.block_density_cv(r0, foot, block=block_px), 4),
        "block_cv_12p8km_after": round(relief.block_density_cv(variant, foot, block=block_px), 4),
        "block_cv_10km_before": round(relief.block_density_cv(r0, foot, block=100), 4),
        "block_cv_10km_after": round(relief.block_density_cv(variant, foot, block=100), 4),
        "block_cv_15km_before": round(relief.block_density_cv(r0, foot, block=150), 4),
        "block_cv_15km_after": round(relief.block_density_cv(variant, foot, block=150), 4),
        "block_cv_5km_before": round(relief.block_density_cv(r0, foot, block=50), 4),
        "block_cv_5km_after": round(relief.block_density_cv(variant, foot, block=50), 4),
        "block_cv_1km_before": round(relief.block_density_cv(r0, foot, block=10), 4),
        "block_cv_1km_after": round(relief.block_density_cv(variant, foot, block=10), 4),
        "relief_tercile_dots": relief_terciles,
    }
    return variant, stats
