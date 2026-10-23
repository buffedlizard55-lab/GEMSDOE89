"""SPACING axis: lattice vs Poisson-disk vs along-strike at matched count.

Single-variable design on R0 (h33-h33-2-b2, 37,654 unit-mass dots):
  * 100% of R0 sits on the binary corroborated fault-ridge network scored_h19_5
    (37,654 / 37,654 dots).
  * To vary ONLY dot spacing without confounding with MASS, RELIEF,
    CONCENTRATION, PRUNE, or off-ridge false positives, we identify R0's broad
    multi-dot ridge corridors at catalogue clearance >= 3.0 px and re-pack EACH
    corridor to its OWN exact R0 dot count n_c under one of three spacing laws:
      - 'strike'  : strike-anisotropic crest-first submodular kernel coverage
                    (tighter along local fault strike r_along=2.0 px, wider
                    across strike r_across=4.2 px to suppress flank doublets).
      - 'poisson' : isotropic farthest-point (maximal Poisson-disk) seeding
                    followed by discrete Voronoi/Lloyd medoid relaxation across
                    the 2-D corridor.
      - 'lattice' : hexagonal covering-lattice snapping (pitch a=3.20 px, row
                    spacing a*sqrt(3)/2 = 2.771 px) on the corridor pixels,
                    ranked by marginal R=3.0 px kernel coverage.
  * Every untouched dot outside those corridors (including all 1,611 inherited
    2 < d_cat < 3 diagonal-collar dots) stays fixed, and 100% of newly placed
    dots satisfy d_cat >= 3.0 px and sit on scored_h19_5 > 0.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

from .metric import KERNEL_RADIUS_PX, kernel_weight
from .relief import block_density_cv, nearest_neighbour_distance

CATALOGUE_CLEARANCE_PX = 3.0
ACTIVE_CORRIDOR_RADIUS_PX = 4.5
DEFAULT_CLEAR_BUDGET = 8500
HEX_PITCH_PX = 3.20
STRIKE_ALONG_PX = 2.00
STRIKE_ACROSS_PX = 4.20


@dataclass
class ManifoldContext:
    """Precomputed ridge manifold, orientation field, 1-px crest, and corridors."""

    manifold: np.ndarray
    crest: np.ndarray
    centrality: np.ndarray
    coherence: np.ndarray
    tx: np.ndarray
    ty: np.ndarray
    nx: np.ndarray
    ny: np.ndarray
    in_repack: np.ndarray
    fixed_dots: np.ndarray
    corr_id: np.ndarray
    chosen_corridors: np.ndarray
    dots_per_corr: np.ndarray


def compute_ridge_orientation(ridge_mask: np.ndarray):
    """Return (centrality, coherence, tx, ty, nx, ny) from binary ridge_mask.

    Uses the 2-D gradient structure tensor of the smoothed ridge indicator:
    gradients point across the ridge (normal n), so the major eigenvector gives
    across-strike normal (nx, ny) and its 90-degree rotation gives local fault
    strike tangent (tx, ty) = (-ny, nx).
    """
    r_f32 = np.asarray(ridge_mask, dtype=np.float32)
    centrality = ndi.gaussian_filter(r_f32, sigma=1.5)
    sm2 = ndi.gaussian_filter(r_f32, sigma=2.0)
    gy, gx = np.gradient(sm2)
    jyy = ndi.gaussian_filter(gy * gy, sigma=3.0)
    jxx = ndi.gaussian_filter(gx * gx, sigma=3.0)
    jyx = ndi.gaussian_filter(gy * gx, sigma=3.0)
    trace = jyy + jxx + 1e-12
    det_part = np.hypot(jyy - jxx, 2.0 * jyx)
    coherence = (det_part / trace).astype(np.float32)
    theta_n = 0.5 * np.arctan2(2.0 * jyx, jxx - jyy)
    nx = np.cos(theta_n).astype(np.float32)
    ny = np.sin(theta_n).astype(np.float32)
    tx = (-ny).astype(np.float32)
    ty = nx.astype(np.float32)
    return centrality, coherence, tx, ty, nx, ny


def extract_crest(manifold: np.ndarray, centrality: np.ndarray,
                  nx: np.ndarray, ny: np.ndarray) -> np.ndarray:
    """1-px-wide across-strike non-maximum-suppression crest of `manifold`."""
    ys, xs = np.nonzero(manifold)
    if len(ys) == 0:
        return np.zeros_like(manifold, dtype=bool)
    s0 = centrality[ys, xs]
    sp = ndi.map_coordinates(centrality, [ys + ny[ys, xs], xs + nx[ys, xs]],
                             order=1, mode="nearest")
    sn = ndi.map_coordinates(centrality, [ys - ny[ys, xs], xs - nx[ys, xs]],
                             order=1, mode="nearest")
    keep = (s0 >= sp) & (s0 >= sn)
    crest = np.zeros_like(manifold, dtype=bool)
    crest[ys[keep], xs[keep]] = True
    return crest


def prepare_manifold(ridge_mask: np.ndarray, parent_dots: np.ndarray,
                     catalogue_mask: np.ndarray, footprint: np.ndarray,
                     clearance_px: float = CATALOGUE_CLEARANCE_PX,
                     active_radius_px: float = ACTIVE_CORRIDOR_RADIUS_PX,
                     target_clear_dots: int = DEFAULT_CLEAR_BUDGET,
                     min_corridor_dots: int = 4) -> ManifoldContext:
    """Build the shared corridor domain used identically by all SPACING arms."""
    ridge_mask = np.asarray(ridge_mask, dtype=bool) & footprint
    parent_dots = np.asarray(parent_dots, dtype=bool)
    catalogue_mask = np.asarray(catalogue_mask, dtype=bool)
    footprint = np.asarray(footprint, dtype=bool)

    d_r0 = ndi.distance_transform_edt(~parent_dots)
    d_cat = ndi.distance_transform_edt(~catalogue_mask)
    manifold = ridge_mask & (d_r0 <= active_radius_px) & footprint

    centrality, coherence, tx, ty, nx, ny = compute_ridge_orientation(ridge_mask)
    crest = extract_crest(manifold, centrality, nx, ny)

    elig_m = manifold & (d_cat >= clearance_px)
    bridged = ndi.binary_dilation(elig_m, structure=np.ones((3, 3), dtype=bool), iterations=1)
    lbl_b, n_corr = ndi.label(bridged, structure=np.ones((3, 3), dtype=bool))
    corr_id = np.where(elig_m, lbl_b, 0)

    r0_dge = parent_dots & elig_m
    dots_per_corr = np.bincount(corr_id[r0_dge], minlength=n_corr + 1)
    offcrest_per_corr = np.bincount(corr_id[r0_dge & ~crest], minlength=n_corr + 1)
    px_per_corr = np.bincount(corr_id[elig_m], minlength=n_corr + 1)
    crest_per_corr = np.bincount(corr_id[elig_m & crest], minlength=n_corr + 1)

    valid_c = np.flatnonzero(
        (dots_per_corr >= min_corridor_dots) & (np.arange(len(dots_per_corr)) > 0)
    )
    if len(valid_c) == 0:
        raise ValueError("no eligible multi-dot corridors found for SPACING")

    width_ratio = px_per_corr[valid_c] / np.maximum(1, crest_per_corr[valid_c])
    off_frac = offcrest_per_corr[valid_c] / dots_per_corr[valid_c]
    score_c = off_frac + 0.5 * (width_ratio - 1.0)
    # Deterministic sort: score desc, then corridor id asc
    order = np.lexsort((valid_c, -score_c))
    ordered_c = valid_c[order]

    cum_dots = np.cumsum(dots_per_corr[ordered_c])
    k_sel = min(len(ordered_c), int(np.searchsorted(cum_dots, target_clear_dots)) + 1)
    chosen_corrs = ordered_c[:k_sel]
    in_repack = np.isin(corr_id, chosen_corrs)
    fixed_dots = parent_dots & ~in_repack

    return ManifoldContext(
        manifold=manifold,
        crest=crest,
        centrality=centrality,
        coherence=coherence,
        tx=tx,
        ty=ty,
        nx=nx,
        ny=ny,
        in_repack=in_repack,
        fixed_dots=fixed_dots,
        corr_id=corr_id,
        chosen_corridors=chosen_corrs,
        dots_per_corr=dots_per_corr,
    )


def _boundary_guards(fixed_dots: np.ndarray, cpts: np.ndarray, pad: int = 5) -> np.ndarray:
    h, w = fixed_dots.shape
    y0 = max(0, int(cpts[:, 0].min()) - pad)
    x0 = max(0, int(cpts[:, 1].min()) - pad)
    y1 = min(h, int(cpts[:, 0].max()) + pad + 1)
    x1 = min(w, int(cpts[:, 1].max()) + pad + 1)
    sub = np.argwhere(fixed_dots[y0:y1, x0:x1])
    if len(sub) == 0:
        return np.empty((0, 2), dtype=np.int32)
    return (sub + np.array([y0, x0], dtype=np.int32)).astype(np.int32)


def _repack_corridor_strike(cpts: np.ndarray, nc: int, guards: np.ndarray,
                            ctx: ManifoldContext, rng: np.random.Generator,
                            r_along: float = STRIKE_ALONG_PX,
                            r_across: float = STRIKE_ACROSS_PX) -> np.ndarray:
    is_cr = ctx.crest[cpts[:, 0], cpts[:, 1]]
    tpts = cpts[is_cr] if is_cr.any() else cpts
    cur_k = np.zeros(len(tpts), dtype=np.float64)
    if len(guards):
        df = np.hypot(
            tpts[:, None, 0] - guards[None, :, 0],
            tpts[:, None, 1] - guards[None, :, 1],
        ).min(axis=1)
        cur_k = kernel_weight(df, KERNEL_RADIUS_PX)

    dist_mt = np.hypot(
        cpts[:, None, 0] - tpts[None, :, 0],
        cpts[:, None, 1] - tpts[None, :, 1],
    )
    k_mt = kernel_weight(dist_mt, KERNEL_RADIUS_PX)
    sm_c = ctx.centrality[cpts[:, 0], cpts[:, 1]].astype(np.float64)
    coh_c = ctx.coherence[cpts[:, 0], cpts[:, 1]].astype(np.float64)
    tx_c = ctx.tx[cpts[:, 0], cpts[:, 1]].astype(np.float64)
    ty_c = ctx.ty[cpts[:, 0], cpts[:, 1]].astype(np.float64)
    jit = rng.random(len(cpts)) * 1e-6

    chosen: list[int] = []
    tiers = [(r_along, r_across), (1.8, 3.2), (1.5, 2.0), (0.9, 0.9)]
    for r_al, r_ac in tiers:
        if len(chosen) >= nc:
            break
        while len(chosen) < nc:
            valid = np.ones(len(cpts), dtype=bool)
            if chosen:
                valid[chosen] = False
            g_list = []
            if len(guards):
                g_list.append(guards)
            if chosen:
                g_list.append(cpts[chosen])
            if g_list:
                gp = np.vstack(g_list)
                dy = gp[None, :, 0] - cpts[:, None, 0]
                dx = gp[None, :, 1] - cpts[:, None, 1]
                euc2 = dx * dx + dy * dy
                da = np.abs(dx * tx_c[:, None] + dy * ty_c[:, None])
                dc = np.abs(-dx * ty_c[:, None] + dy * tx_c[:, None])
                bad = (euc2 < r_al * r_al) | ((da / r_al) ** 2 + (dc / r_ac) ** 2 < 1.0)
                valid &= ~bad.any(axis=1)
            if not valid.any():
                break
            gains = np.maximum(0.0, k_mt - cur_k[None, :]).sum(axis=1)
            score = gains * (1.0 + 0.25 * coh_c) + 0.05 * sm_c + jit
            score[~valid] = -1e9
            best = int(np.argmax(score))
            chosen.append(best)
            cur_k = np.maximum(cur_k, k_mt[best])
    return cpts[chosen[:nc]]


def _repack_corridor_poisson(cpts: np.ndarray, nc: int, guards: np.ndarray,
                             rng: np.random.Generator, lloyd_iters: int = 6) -> np.ndarray:
    dmat = np.hypot(
        cpts[:, None, 0] - cpts[None, :, 0],
        cpts[:, None, 1] - cpts[None, :, 1],
    )
    if len(guards):
        d_guard = np.hypot(
            cpts[:, None, 0] - guards[None, :, 0],
            cpts[:, None, 1] - guards[None, :, 1],
        ).min(axis=1)
        min_d = d_guard.copy()
    else:
        d_guard = None
        min_d = np.full(len(cpts), 1e6, dtype=np.float64)

    jit = rng.random(len(cpts)) * 1e-4
    chosen: list[int] = []
    if d_guard is None:
        first = int(rng.integers(len(cpts)))
        chosen.append(first)
        min_d = np.minimum(min_d, dmat[first])
    while len(chosen) < nc:
        sc = min_d + jit
        if chosen:
            sc[chosen] = -1.0
        nxt = int(np.argmax(sc))
        chosen.append(nxt)
        min_d = np.minimum(min_d, dmat[nxt])

    chosen_arr = np.array(chosen, dtype=int)
    for _ in range(lloyd_iters):
        d_ch = dmat[:, chosen_arr]
        if d_guard is not None:
            owner = np.argmin(np.hstack([d_ch, d_guard[:, None]]), axis=1)
        else:
            owner = np.argmin(d_ch, axis=1)
        new_chosen = chosen_arr.copy()
        used: set[int] = set()
        for k in range(nc):
            cell = np.flatnonzero(owner == k)
            if len(cell) == 0:
                cand_idx = int(chosen_arr[k])
                if cand_idx not in used:
                    used.add(cand_idx)
                continue
            sub_d2 = dmat[np.ix_(cell, cell)] ** 2
            order_med = cell[np.argsort(sub_d2.sum(axis=1))]
            placed = False
            for med in order_med:
                if int(med) not in used:
                    new_chosen[k] = int(med)
                    used.add(int(med))
                    placed = True
                    break
            if not placed and int(chosen_arr[k]) not in used:
                used.add(int(chosen_arr[k]))
        if len(set(new_chosen.tolist())) == nc:
            if np.array_equal(new_chosen, chosen_arr):
                break
            chosen_arr = new_chosen
        else:
            break
    return cpts[chosen_arr]


def _repack_corridor_lattice(cpts: np.ndarray, nc: int, guards: np.ndarray,
                             rng: np.random.Generator,
                             pitch_px: float = HEX_PITCH_PX) -> np.ndarray:
    dy_hex = pitch_px * np.sqrt(3.0) / 2.0
    ymin, xmin = cpts.min(axis=0) - 2
    ymax, xmax = cpts.max(axis=0) + 3
    k0 = int(np.floor(ymin / dy_hex))
    k1 = int(np.ceil(ymax / dy_hex)) + 1
    hnodes = []
    for k in range(k0, k1):
        ry = k * dy_hex
        x_off = 0.5 * pitch_px if (k % 2 == 1) else 0.0
        j0 = int(np.floor((xmin - x_off) / pitch_px))
        j1 = int(np.ceil((xmax - x_off) / pitch_px)) + 1
        xs = x_off + np.arange(j0, j1) * pitch_px
        hnodes.append(np.column_stack([np.full_like(xs, ry), xs]))
    hnodes = np.vstack(hnodes)

    dh = np.hypot(
        cpts[:, None, 0] - hnodes[None, :, 0],
        cpts[:, None, 1] - hnodes[None, :, 1],
    )
    nearest_node = np.argmin(dh, axis=1)
    dist_to_hex = dh[np.arange(len(cpts)), nearest_node]
    best_for_node: dict[int, int] = {}
    for idx_p in np.argsort(dist_to_hex, kind="mergesort"):
        if dist_to_hex[idx_p] > 1.60:
            break
        nd = int(nearest_node[idx_p])
        if nd not in best_for_node:
            best_for_node[nd] = int(idx_p)
    hex_cands = sorted(best_for_node.values())

    dmat = np.hypot(
        cpts[:, None, 0] - cpts[None, :, 0],
        cpts[:, None, 1] - cpts[None, :, 1],
    )
    k_mm = kernel_weight(dmat, KERNEL_RADIUS_PX)
    cur_k = np.zeros(len(cpts), dtype=np.float64)
    if len(guards):
        df = np.hypot(
            cpts[:, None, 0] - guards[None, :, 0],
            cpts[:, None, 1] - guards[None, :, 1],
        ).min(axis=1)
        cur_k = kernel_weight(df, KERNEL_RADIUS_PX)
    jit = rng.random(len(cpts)) * 1e-6

    all_idx = list(range(len(cpts)))
    chosen: list[int] = []
    for pool, rsep in [(hex_cands, 2.5), (hex_cands, 1.8), (all_idx, 2.2), (all_idx, 0.9)]:
        if len(chosen) >= nc or not pool:
            continue
        pool_arr = np.array(pool, dtype=int)
        while len(chosen) < nc:
            valid = np.ones(len(pool_arr), dtype=bool)
            for c_idx in chosen:
                valid &= dmat[pool_arr, c_idx] >= rsep
            if len(guards):
                df_p = np.hypot(
                    cpts[pool_arr, None, 0] - guards[None, :, 0],
                    cpts[pool_arr, None, 1] - guards[None, :, 1],
                ).min(axis=1)
                valid &= df_p >= rsep
            if not valid.any():
                break
            gains = (
                np.maximum(0.0, k_mm[pool_arr] - cur_k[None, :]).sum(axis=1)
                - 0.1 * dist_to_hex[pool_arr]
                + jit[pool_arr]
            )
            gains[~valid] = -1e9
            best = int(pool_arr[int(np.argmax(gains))])
            chosen.append(best)
            cur_k = np.maximum(cur_k, k_mm[best])
    return cpts[chosen[:nc]]


def count_across_strike_twins(dots: np.ndarray, tx: np.ndarray, ty: np.ndarray,
                              r_along: float = 2.2, r_across: float = 4.2) -> int:
    pts = np.argwhere(dots)
    if len(pts) < 2:
        return 0
    pairs = cKDTree(pts).query_pairs(r=max(r_along, r_across), output_type="ndarray")
    if len(pairs) == 0:
        return 0
    p0, p1 = pairs[:, 0], pairs[:, 1]
    dy = pts[p1, 0] - pts[p0, 0]
    dx = pts[p1, 1] - pts[p0, 1]
    t0x, t0y = tx[pts[p0, 0], pts[p0, 1]], ty[pts[p0, 0], pts[p0, 1]]
    t1x, t1y = tx[pts[p1, 0], pts[p1, 1]], ty[pts[p1, 1], pts[p1, 1]]
    t1y = ty[pts[p1, 0], pts[p1, 1]]
    sgn = np.where(t0x * t1x + t0y * t1y >= 0, 1.0, -1.0)
    mx = t0x + sgn * t1x
    my = t0y + sgn * t1y
    mn = np.hypot(mx, my) + 1e-12
    mx /= mn
    my /= mn
    da = np.abs(dx * mx + dy * my)
    dc = np.abs(-dx * my + dy * mx)
    inside = ((da / r_along) ** 2 + (dc / r_across) ** 2 < 1.0) & (dc > da)
    return int(inside.sum())


def build(mode: str, ctx: ManifoldContext, parent_dots: np.ndarray,
          footprint: np.ndarray, rng: np.random.Generator):
    """Build one SPACING variant ('strike', 'poisson', or 'lattice').

    Preserves exact dot count per corridor and globally.
    Returns (variant_dots_mask, stats_dict).
    """
    if mode not in ("strike", "poisson", "lattice"):
        raise ValueError(f"unknown SPACING mode {mode!r}")

    n_dots = int(parent_dots.sum())
    variant = ctx.fixed_dots.copy()

    repack_ys, repack_xs = np.nonzero(ctx.in_repack)
    repack_cids = ctx.corr_id[repack_ys, repack_xs]
    sort_idx = np.argsort(repack_cids, kind="mergesort")
    repack_ys = repack_ys[sort_idx]
    repack_xs = repack_xs[sort_idx]
    repack_cids = repack_cids[sort_idx]
    uniq_c, starts, counts = np.unique(repack_cids, return_index=True, return_counts=True)

    for cid, st, cnt in zip(uniq_c, starts, counts):
        nc = int(ctx.dots_per_corr[cid])
        cpts = np.column_stack([repack_ys[st:st + cnt], repack_xs[st:st + cnt]])
        guards = _boundary_guards(ctx.fixed_dots, cpts, pad=5)
        if mode == "strike":
            sel = _repack_corridor_strike(cpts, nc, guards, ctx, rng)
        elif mode == "poisson":
            sel = _repack_corridor_poisson(cpts, nc, guards, rng)
        else:
            sel = _repack_corridor_lattice(cpts, nc, guards, rng)
        if len(sel) != nc:
            raise RuntimeError(f"corridor {cid}: placed {len(sel)} != {nc} dots")
        variant[sel[:, 0], sel[:, 1]] = True

    if int(variant.sum()) != n_dots:
        raise RuntimeError(f"dot count {int(variant.sum())} != parent {n_dots}")

    added_mask = variant & ~parent_dots
    removed_mask = parent_dots & ~variant
    n_moved = int(added_mask.sum())
    assert n_moved == int(removed_mask.sum()), "added and removed counts differ"

    if n_moved > 0:
        added_pts = np.argwhere(added_mask)
        removed_pts = np.argwhere(removed_mask)
        disp, _ = cKDTree(added_pts).query(removed_pts)
    else:
        disp = np.zeros(0, dtype=np.float64)

    nn_before, _ = nearest_neighbour_distance(parent_dots)
    nn_after, _ = nearest_neighbour_distance(variant)

    d_before = ndi.distance_transform_edt(~parent_dots)
    d_after = ndi.distance_transform_edt(~variant)
    t_crest_before = float(kernel_weight(d_before[ctx.crest], KERNEL_RADIUS_PX).sum())
    t_crest_after = float(kernel_weight(d_after[ctx.crest], KERNEL_RADIUS_PX).sum())
    t_manif_before = float(kernel_weight(d_before[ctx.manifold], KERNEL_RADIUS_PX).sum())
    t_manif_after = float(kernel_weight(d_after[ctx.manifold], KERNEL_RADIUS_PX).sum())

    stats = {
        "mode": mode,
        "n_dots": n_dots,
        "n_corridors_repacked": int(len(uniq_c)),
        "n_cleared_in_corridors": int((parent_dots & ctx.in_repack).sum()),
        "n_moved": n_moved,
        "pct_changed": 100.0 * n_moved / n_dots,
        "pct_symmetric_diff": 100.0 * (2 * n_moved) / n_dots,
        "mean_displacement_px": float(disp.mean()) if len(disp) else 0.0,
        "median_displacement_px": float(np.median(disp)) if len(disp) else 0.0,
        "nn_p10_before_px": float(np.percentile(nn_before, 10)),
        "nn_p10_after_px": float(np.percentile(nn_after, 10)),
        "nn_median_before_px": float(np.median(nn_before)),
        "nn_median_after_px": float(np.median(nn_after)),
        "crest_dots_before": int((parent_dots & ctx.crest).sum()),
        "crest_dots_after": int((variant & ctx.crest).sum()),
        "t_crest_before": t_crest_before,
        "t_crest_after": t_crest_after,
        "t_crest_delta": t_crest_after - t_crest_before,
        "t_manifold_before": t_manif_before,
        "t_manifold_after": t_manif_after,
        "t_manifold_delta": t_manif_after - t_manif_before,
        "across_strike_twins_before": count_across_strike_twins(parent_dots, ctx.tx, ctx.ty),
        "across_strike_twins_after": count_across_strike_twins(variant, ctx.tx, ctx.ty),
        "block_cv_before": block_density_cv(parent_dots, footprint, block=10),
        "block_cv_after": block_density_cv(variant, footprint, block=10),
        "block_cv_5km_before": block_density_cv(parent_dots, footprint, block=50),
        "block_cv_5km_after": block_density_cv(variant, footprint, block=50),
    }
    return variant, stats
