"""SPACING axis: lattice vs Poisson-disk vs along-strike at matched count.

Single-variable controlled edit of Parent R0 (h33-h33-2-b2, 37,654 unit dots):
  * Global dot count is held strictly fixed at 37,654 (zero MASS confound).
  * Every re-spaced fault corridor keeps its exact integer R0 dot budget k_c
    (zero CONCENTRATION and zero RELIEF confound).
  * No geophysical gradient snapping is applied (zero SNAP confound).
  * R0's 1,611 inherited 2 < d_cat < 3 px collar dots and short (< MIN_COMPONENT_DOTS)
    fragments are frozen unchanged; 100 % of re-spaced dots obey d_cat >= 3.0 px
    and sit strictly inside the footprint (zero PRUNE confound, Hard Constraint 4).

The three spacing operators act on the 834 major H19-5 fault corridors
(8-connected ridge strands at d_cat >= 3.0 px carrying >= 6 R0 dots, i.e.,
>= ~1.8 km trace length, holding 8,241 R0 dots = 21.89 % of R0):

  1. alongstrike : 1-D graph-geodesic arc-length equipartition + exact DTI
                   triangular-kernel (R = 3.0 px) 1-swap refinement on the 1-px
                   H19-5 ridge skeleton, preferring inter-dot separation >= 3.0 px
                   (fallback 2.8 px) so northern-root BFS crowding and southern/
                   eastern tip overhangs are eliminated.
  2. poisson     : Seeded 2-D Bridson / dart-throwing Poisson-disk blue-noise
                   packing (r_disk = 3.4 -> 3.2 -> 3.0 -> 2.8 px) across each
                   strand's d <= 1.5 px (+-150 m) GeoDAWN positional-uncertainty
                   corridor (400 m flight-line spacing -> ~kernel-radius lateral
                   uncertainty).
  3. lattice     : Isometric hexagonal lattice sampling (pitch a = 3.5 px, row
                   step a*sqrt(3)/2 = 3.031 px, half-pitch row stagger, Kershner-
                   optimal 2-D disk covering) inside each strand's d <= 2.0 px
                   corridor, enforcing inter-dot clearance >= 3.0 -> 2.8 px.
"""

from __future__ import annotations

import heapq

import numpy as np
from scipy import ndimage as ndi
from scipy.ndimage import distance_transform_edt, label as ndi_label
from scipy.spatial import cKDTree

from .relief import BLOCK_PX, block_density_cv, define_classes, nearest_neighbour_distance

CATALOGUE_CLEARANCE_PX = 3.0
MIN_EXT_SEP_PX = 2.8
MIN_COMPONENT_DOTS = 6
HEX_LATTICE_PITCH_PX = 3.5
POISSON_CORRIDOR_PX = 1.5
LATTICE_CORRIDOR_PX = 2.0


def hex_lattice_distance_field(shape: tuple[int, int], pitch: float = HEX_LATTICE_PITCH_PX) -> np.ndarray:
    """Euclidean distance (px) from every grid cell to the nearest isometric hex lattice node."""
    h, w = shape
    yy, xx = np.indices((h, w), dtype=np.float32)
    dy = float(pitch * (np.sqrt(3.0) / 2.0))
    row0 = np.rint(yy / dy)
    d2 = np.full((h, w), np.inf, dtype=np.float32)
    for dr in (-1.0, 0.0, 1.0):
        ri = row0 + dr
        yn = ri * dy
        x_shift = (np.abs(ri.astype(np.int32)) % 2) * (0.5 * pitch)
        xn = np.rint((xx - x_shift) / pitch) * pitch + x_shift
        d2 = np.minimum(d2, (yy - yn) ** 2 + (xx - xn) ** 2)
    return np.sqrt(d2)


def geodesic_arc_coordinate(pts: np.ndarray) -> np.ndarray:
    """Graph-geodesic distance along an 8-connected ridge component from a diameter endpoint."""
    n = len(pts)
    if n <= 1:
        return np.zeros(n, dtype=np.float64)
    tree = cKDTree(pts)
    pairs = tree.query_pairs(1.5)
    adj: list[list[tuple[int, float]]] = [[] for _ in range(n)]
    for i, j in pairs:
        w = float(np.hypot(pts[i, 0] - pts[j, 0], pts[i, 1] - pts[j, 1]))
        adj[i].append((j, w))
        adj[j].append((i, w))

    def dijkstra(src: int) -> np.ndarray:
        dist = np.full(n, np.inf, dtype=np.float64)
        dist[src] = 0.0
        pq = [(0.0, src)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, w in adj[u]:
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))
        return dist

    d0 = dijkstra(0)
    finite_d0 = np.where(np.isfinite(d0), d0, -1.0)
    u = int(np.argmax(finite_d0))
    du = dijkstra(u)
    if not np.isfinite(du).all():
        # Fallback if a component was split: replace inf with Euclidean distance from u
        fallback = np.hypot(pts[:, 0] - pts[u, 0], pts[:, 1] - pts[u, 1])
        du = np.where(np.isfinite(du), du, fallback)
    return du


def _place_alongstrike(
    pts_ridge: np.ndarray,
    d_exist_ridge: np.ndarray,
    k: int,
) -> np.ndarray:
    """Place k dots on pts_ridge via geodesic equipartition + exact kernel-credit 1-swap."""
    s_full = geodesic_arc_coordinate(pts_ridge)
    base_cov = np.clip(1.0 - d_exist_ridge / 3.0, 0.0, 1.0)

    ok = d_exist_ridge >= MIN_EXT_SEP_PX - 1e-6
    if int(ok.sum()) < k:
        ok = d_exist_ridge > 0.0
    cand_idx = np.flatnonzero(ok)
    cpts = pts_ridge[cand_idx]
    s = s_full[cand_idx]

    diff_all = pts_ridge[:, None, :] - cpts[None, :, :]
    k_mat = np.clip(1.0 - np.hypot(diff_all[..., 0], diff_all[..., 1]) / 3.0, 0.0, 1.0)
    diff_cc = cpts[:, None, :] - cpts[None, :, :]
    dist_cc = np.hypot(diff_cc[..., 0], diff_cc[..., 1])

    s_min = float(s.min())
    s_span = max(float(s.max()) - s_min, 1e-6)
    targets = s_min + (np.arange(k, dtype=np.float64) + 0.5) * s_span / k

    chosen: list[int] | None = None
    used_sep = 0.0
    for r_sep in (3.0, 2.8, 2.0, 1.0, 0.0):
        ch: list[int] = []
        for t_val in targets:
            order = np.argsort(np.abs(s - t_val), kind="mergesort")
            for idx in order:
                i_int = int(idx)
                if i_int in ch:
                    continue
                if all(dist_cc[i_int, c] >= r_sep - 1e-6 for c in ch):
                    ch.append(i_int)
                    break
        if len(ch) == k:
            chosen = ch
            used_sep = r_sep
            break
    if chosen is None:
        chosen = list(range(k))
        used_sep = 0.0

    for _ in range(4):
        improved = False
        for pos in range(k):
            others = [chosen[j] for j in range(k) if j != pos]
            cov_others = np.maximum(base_cov, k_mat[:, others].max(axis=1)) if others else base_cov
            cur = chosen[pos]
            best_score = float(np.maximum(cov_others, k_mat[:, cur]).sum())
            valid_c = np.ones(len(cpts), dtype=bool)
            for o in others:
                valid_c &= dist_cc[:, o] >= used_sep - 1e-6
            valid_c[others] = False
            v_idxs = np.flatnonzero(valid_c)
            if len(v_idxs) == 0:
                continue
            scores = np.maximum(cov_others[:, None], k_mat[:, v_idxs]).sum(axis=0)
            bi = int(np.argmax(scores))
            if float(scores[bi]) > best_score + 1e-5:
                chosen[pos] = int(v_idxs[bi])
                improved = True
        if not improved:
            break

    return cpts[chosen]


def _place_greedy_ranked(
    cpts: np.ndarray,
    d_exist: np.ndarray,
    k: int,
    radii: tuple[float, ...],
) -> np.ndarray:
    """Accept k points in priority order, relaxing internal separation only if required."""
    chosen: list[int] = []
    chosen_set: set[int] = set()
    for r_sep in radii:
        ext_req = min(r_sep, MIN_EXT_SEP_PX) - 1e-6
        r2_req = (r_sep - 1e-6) ** 2
        for i in range(len(cpts)):
            if len(chosen) >= k:
                break
            if i in chosen_set:
                continue
            if d_exist[i] < ext_req:
                continue
            py, px = int(cpts[i, 0]), int(cpts[i, 1])
            if all((py - int(cpts[c, 0])) ** 2 + (px - int(cpts[c, 1])) ** 2 >= r2_req for c in chosen):
                chosen.append(i)
                chosen_set.add(i)
        if len(chosen) >= k:
            break
    if len(chosen) < k:
        raise RuntimeError(f"Corridor capacity shortfall: placed {len(chosen)} of {k} dots")
    return cpts[chosen[:k]]


def build(
    mode: str,
    parent_dots: np.ndarray,
    h19_5_mask: np.ndarray,
    footprint: np.ndarray,
    catalogue_mask: np.ndarray,
    seed: int = 20261023,
    min_component_dots: int = MIN_COMPONENT_DOTS,
    det_elev: np.ndarray | None = None,
) -> tuple[np.ndarray, dict]:
    """Build one SPACING variant ('alongstrike', 'poisson', or 'lattice').

    Returns (variant_mask, stats_dict). Global and per-corridor dot counts are
    preserved exactly.
    """
    if mode not in ("alongstrike", "poisson", "lattice"):
        raise ValueError(f"Unknown SPACING mode: {mode!r}")

    foot = np.asarray(footprint, dtype=bool)
    cat = np.asarray(catalogue_mask, dtype=bool) & foot
    r0 = np.asarray(parent_dots, dtype=bool) & foot
    h19 = np.asarray(h19_5_mask, dtype=bool) & foot
    n_dots = int(r0.sum())

    d_cat = distance_transform_edt(~cat)
    elig_h19 = h19 & (d_cat >= CATALOGUE_CLEARANCE_PX) & foot
    lbl, ncomp = ndi_label(elig_h19, structure=np.ones((3, 3), dtype=np.int8))
    elig_r0 = r0 & (lbl > 0)
    dots_c = np.bincount(lbl[elig_r0], minlength=ncomp + 1)
    dots_c[0] = 0

    active_cids = np.flatnonzero(dots_c >= min_component_dots)
    m_active = len(active_cids)
    remap = np.zeros(ncomp + 1, dtype=np.int32)
    remap[active_cids] = np.arange(1, m_active + 1)

    active_lbl = remap[lbl]
    is_active = active_lbl > 0
    active_r0 = elig_r0 & is_active
    frozen = r0 & (~active_r0)
    active_h19 = elig_h19 & is_active

    d_act, idx_act = distance_transform_edt(~active_h19, return_indices=True)
    nearest_m = active_lbl[idx_act[0], idx_act[1]]
    valid_free = foot & (d_cat >= CATALOGUE_CLEARANCE_PX) & (~frozen)
    corr_lbl = np.where((d_act <= LATTICE_CORRIDOR_PX + 1e-6) & valid_free, nearest_m, 0)
    slices = ndi.find_objects(corr_lbl)

    d_lat = hex_lattice_distance_field(foot.shape) if mode == "lattice" else None
    rng = np.random.default_rng(seed)

    h, w = foot.shape
    variant = frozen.copy()

    for m_id in range(1, m_active + 1):
        cid = int(active_cids[m_id - 1])
        k = int(dots_c[cid])
        sl = slices[m_id - 1]
        if sl is None:
            raise RuntimeError(f"Missing bounding box for active corridor {m_id}")
        y0 = max(0, sl[0].start - 4)
        y1 = min(h, sl[0].stop + 4)
        x0 = max(0, sl[1].start - 4)
        x1 = min(w, sl[1].stop + 4)

        sub_var = variant[y0:y1, x0:x1]
        sub_d_exist = (
            distance_transform_edt(~sub_var)
            if sub_var.any()
            else np.full((y1 - y0, x1 - x0), 99.0, dtype=np.float64)
        )

        if mode == "alongstrike":
            sub_ridge = active_lbl[y0:y1, x0:x1] == m_id
            ry, rx = np.nonzero(sub_ridge)
            pts_r = np.column_stack([ry, rx])
            sel = _place_alongstrike(pts_r, sub_d_exist[ry, rx], k)
        elif mode == "poisson":
            sub_corr = (corr_lbl[y0:y1, x0:x1] == m_id) & (
                d_act[y0:y1, x0:x1] <= POISSON_CORRIDOR_PX + 1e-6
            )
            cy, cx = np.nonzero(sub_corr)
            if len(cy) < k:
                sub_corr = corr_lbl[y0:y1, x0:x1] == m_id
                cy, cx = np.nonzero(sub_corr)
            cpts = np.column_stack([cy, cx])
            d_ex = sub_d_exist[cy, cx]
            perm = rng.permutation(len(cpts))
            sel = _place_greedy_ranked(
                cpts[perm], d_ex[perm], k, radii=(3.4, 3.2, 3.0, 2.8, 2.0, 0.1)
            )
        else:  # lattice
            assert d_lat is not None
            sub_corr = corr_lbl[y0:y1, x0:x1] == m_id
            cy, cx = np.nonzero(sub_corr)
            cpts = np.column_stack([cy, cx])
            score = d_lat[y0 + cy, x0 + cx] + 0.15 * d_act[y0 + cy, x0 + cx]
            order = np.argsort(score, kind="mergesort")
            sel = _place_greedy_ranked(
                cpts[order], sub_d_exist[cy, cx][order], k, radii=(3.0, 2.8, 2.0, 0.1)
            )

        variant[y0 + sel[:, 0], x0 + sel[:, 1]] = True

    if int(variant.sum()) != n_dots:
        raise RuntimeError(f"Dot count changed: got {int(variant.sum())}, want {n_dots}")

    added = variant & (~r0)
    removed = r0 & (~variant)
    n_moved = int(removed.sum())
    sym_diff = int((r0 ^ variant).sum())

    if n_moved > 0:
        disp, _ = cKDTree(np.argwhere(added)).query(np.argwhere(removed))
    else:
        disp = np.zeros(0, dtype=np.float64)

    nn_before, _ = nearest_neighbour_distance(r0)
    nn_after, _ = nearest_neighbour_distance(variant)

    d_r0 = distance_transform_edt(~r0)
    d_var = distance_transform_edt(~variant)
    cov_act_before = float(np.clip(1.0 - d_r0[active_h19] / 3.0, 0.0, 1.0).mean()) if active_h19.any() else 0.0
    cov_act_after = float(np.clip(1.0 - d_var[active_h19] / 3.0, 0.0, 1.0).mean()) if active_h19.any() else 0.0
    cov_h19_before = float(np.clip(1.0 - d_r0[elig_h19] / 3.0, 0.0, 1.0).mean()) if elig_h19.any() else 0.0
    cov_h19_after = float(np.clip(1.0 - d_var[elig_h19] / 3.0, 0.0, 1.0).mean()) if elig_h19.any() else 0.0

    relief_drift = None
    if det_elev is not None:
        domain = foot & np.isfinite(det_elev)
        cls, _ = define_classes(det_elev, domain)
        relief_drift = {
            "before": [int((r0 & (cls == c)).sum()) for c in (0, 1, 2)],
            "after": [int((variant & (cls == c)).sum()) for c in (0, 1, 2)],
        }

    stats = {
        "mode": mode,
        "seed": int(seed),
        "min_component_dots": int(min_component_dots),
        "active_components": int(m_active),
        "active_r0_dots": int(active_r0.sum()),
        "frozen_r0_dots": int(frozen.sum()),
        "n_dots": n_dots,
        "n_moved": n_moved,
        "pct_changed": 100.0 * n_moved / max(1, n_dots),
        "symmetric_diff_dots": sym_diff,
        "pct_symmetric_diff": 100.0 * sym_diff / max(1, n_dots),
        "mean_displacement_px": float(disp.mean()) if len(disp) else 0.0,
        "median_displacement_px": float(np.median(disp)) if len(disp) else 0.0,
        "p95_displacement_px": float(np.percentile(disp, 95)) if len(disp) else 0.0,
        "nn_median_before_px": float(np.median(nn_before)) if len(nn_before) else 0.0,
        "nn_median_after_px": float(np.median(nn_after)) if len(nn_after) else 0.0,
        "nn_lt_3px_before": int((nn_before < 3.0).sum()),
        "nn_lt_3px_after": int((nn_after < 3.0).sum()),
        "active_ridge_kernel_cov_before": round(cov_act_before, 5),
        "active_ridge_kernel_cov_after": round(cov_act_after, 5),
        "all_elig_ridge_kernel_cov_before": round(cov_h19_before, 5),
        "all_elig_ridge_kernel_cov_after": round(cov_h19_after, 5),
        "added_min_catalogue_clearance_px": float(d_cat[added].min()) if added.any() else None,
        "block_cv_1km_before": round(block_density_cv(r0, foot, block=BLOCK_PX), 4),
        "block_cv_1km_after": round(block_density_cv(variant, foot, block=BLOCK_PX), 4),
        "block_cv_5km_before": round(block_density_cv(r0, foot, block=50), 4),
        "block_cv_5km_after": round(block_density_cv(variant, foot, block=50), 4),
        "relief_tercile_dots": relief_drift,
    }
    return variant, stats
