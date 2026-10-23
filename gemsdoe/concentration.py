"""CONCENTRATION axis: fixed-count transfers between km-scale prior blocks.

The prior is known-catalogue areal density, never test truth.  Source blocks are
at/below the median prior among blocks containing parent dots; target blocks are
at/above the upper-quartile prior among blocks with unused H19-5 candidates.
All additions remain on the same binary H19-5 lineament field as R0, so this
axis does not substitute a new physical signal.

Dots are ranked by *exact* marginal DTI changes under the explicitly labelled
H19-5 surrogate truth.  The implementation includes the max-operator credit,
explained mass M, and denominator changes; it is not the isolated-pixel
shortcut.  Live predictions remain scenario MODELs because H19-5 is not test
truth.
"""

from __future__ import annotations

import heapq

import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

from . import mass, metric

KERNEL_RADIUS_PX = 3.0
CATALOGUE_CLEARANCE_PX = 3.0
ANCHOR_D = 18734.44  # recorded upstream live-anchor MODEL scale; not a receipt


def _kernel(distance):
    return metric.kernel_weight(distance, KERNEL_RADIUS_PX)


def _offsets(radius=KERNEL_RADIUS_PX):
    """All integer offsets inside the kernel, including (0, 0)."""
    r = int(np.floor(radius))
    return [
        (dy, dx, float(np.hypot(dy, dx)), 1.0 - float(np.hypot(dy, dx)) / radius)
        for dy in range(-r, r + 1)
        for dx in range(-r, r + 1)
        if np.hypot(dy, dx) < radius
    ]


def make_block_prior(
    catalogue_mask,
    footprint,
    parent_dots,
    candidate_mask,
    block_px=20,
    source_quantile=0.50,
    target_quantile=0.75,
):
    """Return source/target rasters and an audit of the catalogue block prior.

    Blocks with <=50% footprint coverage and the incomplete right/bottom grid
    fringe are frozen, matching ``mass.block_density_cv``.  Prior units are
    catalogue pixels per 1,000 footprint pixels.  Quantile ties are retained,
    so a zero-heavy bottom half can contain more than half of eligible blocks.
    """
    if not 0 <= source_quantile < target_quantile <= 1:
        raise ValueError("require 0 <= source_quantile < target_quantile <= 1")
    parent_dots = np.asarray(parent_dots, dtype=bool)
    footprint = np.asarray(footprint, dtype=bool)
    catalogue_mask = np.asarray(catalogue_mask, dtype=bool) & footprint
    candidate_mask = np.asarray(candidate_mask, dtype=bool) & footprint
    h, w = parent_dots.shape
    bh, bw = h // block_px, w // block_px
    if bh == 0 or bw == 0:
        raise ValueError("block is larger than the raster")
    sl = np.s_[: bh * block_px, : bw * block_px]

    def sums(a):
        return a[sl].reshape(bh, block_px, bw, block_px).sum(axis=(1, 3))

    area = sums(footprint)
    n_cat = sums(catalogue_mask)
    n_parent = sums(parent_dots)
    n_candidate = sums(candidate_mask)
    active = area > 0.5 * block_px * block_px
    prior = np.full(area.shape, np.nan, dtype=np.float64)
    np.divide(1000.0 * n_cat, area, out=prior, where=active & (area > 0))

    source_eligible = active & (n_parent > 0)
    target_eligible = active & (n_candidate > 0)
    if not source_eligible.any() or not target_eligible.any():
        raise ValueError("empty source- or target-eligible block population")
    source_cut = float(np.quantile(prior[source_eligible], source_quantile))
    target_cut = float(np.quantile(prior[target_eligible], target_quantile))
    source_blocks = source_eligible & (prior <= source_cut)
    target_blocks = target_eligible & (prior >= target_cut)
    if (source_blocks & target_blocks).any():
        raise ValueError("source and target blocks overlap; no concentration contrast")
    if not source_blocks.any() or not target_blocks.any():
        raise ValueError("empty source or target block selection")

    def expand(blocks, fill=False, dtype=None):
        out = np.full(parent_dots.shape, fill, dtype=dtype or blocks.dtype)
        out[sl] = np.repeat(np.repeat(blocks, block_px, axis=0), block_px, axis=1)
        return out

    source_mask = expand(source_blocks) & footprint
    target_mask = expand(target_blocks) & footprint
    prior_raster = expand(prior, fill=np.nan, dtype=np.float64)
    prior_raster[~footprint] = np.nan

    stats = {
        "block_px": int(block_px),
        "block_km": block_px / 10.0,
        "prior": "1000 * catalogue_pixels / footprint_pixels; known-fault prior, not test truth",
        "source_quantile": source_quantile,
        "target_quantile": target_quantile,
        "source_cut_per_1000px": source_cut,
        "target_cut_per_1000px": target_cut,
        "active_blocks": int(active.sum()),
        "source_eligible_blocks": int(source_eligible.sum()),
        "target_eligible_blocks": int(target_eligible.sum()),
        "source_blocks": int(source_blocks.sum()),
        "target_blocks": int(target_blocks.sum()),
        "source_parent_dots": int((parent_dots & source_mask).sum()),
        "target_parent_dots": int((parent_dots & target_mask).sum()),
        "target_candidate_pixels": int((candidate_mask & target_mask).sum()),
        "source_block_prior_mean": float(np.mean(prior[source_blocks])),
        "target_block_prior_mean": float(np.mean(prior[target_blocks])),
        "active_block_prior_mean": float(np.mean(prior[active])),
        "source_parent_prior_mean": float(np.mean(prior_raster[parent_dots & source_mask])),
        "target_parent_prior_mean": float(np.mean(prior_raster[parent_dots & target_mask])),
        "quantile_ties_retained": True,
        "frozen_edge_rule": "incomplete right/bottom fringe and blocks with <=50% footprint are unchanged",
    }
    return source_mask, target_mask, prior_raster, stats


def marginal_rankings(truth, dots, candidate_points, radius=KERNEL_RADIUS_PX):
    """Exact one-dot removal/addition DTI deltas for a binary prediction.

    Returns parent points and removal deltas, candidate addition deltas, and
    the base T/S/M/G/D components.  Addition candidates must not already be
    dots.  Equal-distance prediction ties cause zero T loss when one tied dot
    is removed, exactly matching the max operator.
    """
    truth = np.asarray(truth, dtype=bool)
    dots = np.asarray(dots, dtype=bool)
    if truth.shape != dots.shape:
        raise ValueError("truth and dots must have the same shape")
    pts = np.argwhere(dots).astype(np.int32)
    truth_pts = np.argwhere(truth).astype(np.int32)
    candidates = np.asarray(candidate_points, dtype=np.int32).reshape(-1, 2)
    if len(candidates) and bool(dots[candidates[:, 0], candidates[:, 1]].any()):
        raise ValueError("addition candidates must be absent from the parent")
    n, g = len(pts), len(truth_pts)
    s = float(n)
    truth_tree = cKDTree(truth_pts) if g else None

    if g:
        if n:
            pred_tree = cKDTree(pts)
            distances, indices = pred_tree.query(truth_pts, k=2 if n > 1 else 1)
            if n == 1:
                d1 = distances
                i1 = indices
                d2 = np.full(g, np.inf)
            else:
                d1, d2 = distances[:, 0], distances[:, 1]
                i1 = indices[:, 0]
            current_credit = _kernel(d1)
            t = float(current_credit.sum())
            unique = d2 > d1 + 1e-9
            unique_credit = np.bincount(
                i1[unique], weights=current_credit[unique], minlength=n
            ).astype(np.float64)
            d_truth_at_pred = truth_tree.query(pts, k=1)[0]
            m_each = _kernel(d_truth_at_pred)
        else:
            current_credit = np.zeros(g, dtype=np.float64)
            t = 0.0
            unique_credit = np.zeros(0, dtype=np.float64)
            m_each = np.zeros(0, dtype=np.float64)
        m = float(m_each.sum())
    else:
        current_credit = np.zeros(0, dtype=np.float64)
        t = m = 0.0
        unique_credit = np.zeros(n, dtype=np.float64)
        m_each = np.zeros(n, dtype=np.float64)

    d = 0.2 * t + 0.2 * (s - m) + 0.8 * g
    if d <= 0:
        raise ValueError("undefined DTI scene: no truth and no prediction mass")
    base = t / d
    d_removed = d - 0.2 * unique_credit - 0.2 * (1.0 - m_each)
    remove_delta = (t - unique_credit) / d_removed - base

    add_truth_credit = np.zeros(len(candidates), dtype=np.float64)
    if len(candidates) and g:
        truth_index = np.full(truth.shape, -1, dtype=np.int32)
        truth_index[truth_pts[:, 0], truth_pts[:, 1]] = np.arange(g, dtype=np.int32)
        h, w = truth.shape
        for dy, dx, _distance, k in _offsets(radius):
            q = candidates + np.array([dy, dx], dtype=np.int32)
            inside = (q[:, 0] >= 0) & (q[:, 0] < h) & (q[:, 1] >= 0) & (q[:, 1] < w)
            ci = np.flatnonzero(inside)
            if not len(ci):
                continue
            ti = truth_index[q[ci, 0], q[ci, 1]]
            valid = ti >= 0
            if valid.any():
                ci_valid = ci[valid]
                gain = np.maximum(0.0, k - current_credit[ti[valid]])
                add_truth_credit[ci_valid] += gain
        m_add = _kernel(truth_tree.query(candidates, k=1)[0])
    else:
        m_add = np.zeros(len(candidates), dtype=np.float64)
    d_added = d + 0.2 * add_truth_credit + 0.2 * (1.0 - m_add)
    add_delta = (t + add_truth_credit) / d_added - base

    return {
        "points": pts,
        "remove_delta": remove_delta,
        "remove_unique_truth_credit": unique_credit,
        "remove_m": m_each,
        "candidate_points": candidates,
        "current_truth_credit": current_credit,
        "add_delta": add_delta,
        "add_truth_credit": add_truth_credit,
        "add_m": m_add,
        "base": {"T": t, "S": s, "M": m, "G": float(g), "D": d, "DTI": base},
    }


def _greedy_on_truth_from_ranking(truth, candidates, ranking, n_select, seed):
    """Lazy exact greedy additions for candidates that lie on surrogate truth.

    Coverage gains only decrease as accepted dots raise current kernel credit.
    A max-heap of stale gains therefore supplies upper bounds: a popped candidate
    is re-scored until its current gain equals its bound, at which point it is
    the exact greedy maximizer.  Since every candidate has m=1, exact DTI gain
    is monotone in this coverage gain at each step.
    """
    candidates = np.asarray(candidates, dtype=np.int32).reshape(-1, 2)
    if len(candidates) and not truth[candidates[:, 0], candidates[:, 1]].all():
        raise ValueError("greedy_on_truth requires every candidate to be on truth")
    if not 0 <= n_select <= len(candidates):
        raise ValueError("invalid greedy selection count")
    current_credit = ranking["current_truth_credit"].copy()
    truth_index = np.full(truth.shape, -1, dtype=np.int32)
    truth_points = np.argwhere(truth).astype(np.int32)
    truth_index[truth_points[:, 0], truth_points[:, 1]] = np.arange(len(truth_points))
    neighbor_ids = [[] for _ in range(len(candidates))]
    neighbor_weights = [[] for _ in range(len(candidates))]
    h, w = truth.shape
    for dy, dx, _distance, k in _offsets():
        q = candidates + np.array([dy, dx], dtype=np.int32)
        inside = (q[:, 0] >= 0) & (q[:, 0] < h) & (q[:, 1] >= 0) & (q[:, 1] < w)
        ci = np.flatnonzero(inside)
        if not len(ci):
            continue
        ti = truth_index[q[ci, 0], q[ci, 1]]
        valid = ti >= 0
        for c, t in zip(ci[valid], ti[valid]):
            neighbor_ids[int(c)].append(int(t))
            neighbor_weights[int(c)].append(k)
    neighbor_ids = [np.asarray(v, dtype=np.int32) for v in neighbor_ids]
    neighbor_weights = [np.asarray(v, dtype=np.float64) for v in neighbor_weights]

    def gain(i):
        ids = neighbor_ids[i]
        if not len(ids):
            return 0.0
        return float(np.maximum(0.0, neighbor_weights[i] - current_credit[ids]).sum())

    rng = np.random.default_rng(seed)
    tie = rng.random(len(candidates))
    heap = [(-float(g), float(tie[i]), i) for i, g in enumerate(ranking["add_truth_credit"])]
    heapq.heapify(heap)
    selected, gains, deltas = [], [], []
    t, d = ranking["base"]["T"], ranking["base"]["D"]
    while len(selected) < n_select:
        if not heap:
            raise RuntimeError("greedy heap exhausted before requested selection")
        negative_bound, _tie, i = heapq.heappop(heap)
        bound = -negative_bound
        current = gain(i)
        if current < bound - 1e-12:
            heapq.heappush(heap, (-current, float(tie[i]), i))
            continue
        # current <= bound always; equality means every other stale heap key is
        # an upper bound no greater than this candidate's current exact gain.
        selected.append(i)
        gains.append(current)
        deltas.append((t + current) / (d + 0.2 * current) - t / d)
        ids = neighbor_ids[i]
        if len(ids):
            current_credit[ids] = np.maximum(current_credit[ids], neighbor_weights[i])
        t += current
        d += 0.2 * current  # S and M both increase by one (m=1)
    return {
        "indices": np.asarray(selected, dtype=np.int32),
        "truth_credit": np.asarray(gains, dtype=np.float64),
        "exact_marginal_dti": np.asarray(deltas, dtype=np.float64),
    }


def greedy_on_truth_additions(truth, dots, candidate_points, n_select, seed=20261023):
    """Public tested wrapper for exact sequential on-truth greedy additions."""
    ranking = marginal_rankings(truth, dots, candidate_points)
    return _greedy_on_truth_from_ranking(
        np.asarray(truth, dtype=bool), candidate_points, ranking, n_select, seed
    )


def _dti_from_distances(truth, dots, distance_to_truth):
    distance_to_pred = ndi.distance_transform_edt(~dots)
    t = float(_kernel(distance_to_pred[truth]).sum())
    s = float(dots.sum())
    m = float(_kernel(distance_to_truth[dots]).sum())
    g = float(truth.sum())
    d = 0.2 * t + 0.2 * (s - m) + 0.8 * g
    return {"T": t, "S": s, "M": m, "G": g, "D": d, "DTI": t / d if d else 0.0}


def build_family(
    parent_dots,
    h19_mask,
    footprint,
    catalogue_mask,
    n_moves,
    block_px=20,
    seed=20261023,
    source_quantile=0.50,
    target_quantile=0.75,
):
    """Build nested fixed-count transfers; return ``(variants, audit)``.

    ``variants`` maps each requested move count to ``(mask, stats)``.  Source
    ranks are computed once on R0 and destinations are exact sequential greedy
    additions, so every lower-dose edit is an exact subset of the higher-dose
    edit.  No minimum-separation rule is imposed: local crowding is
    a measured consequence of concentration, while exact marginal ranking
    penalizes redundant destinations under the H19 surrogate.
    """
    parent_dots = np.asarray(parent_dots, dtype=bool)
    h19_mask = np.asarray(h19_mask, dtype=bool)
    footprint = np.asarray(footprint, dtype=bool)
    catalogue_mask = np.asarray(catalogue_mask, dtype=bool) & footprint
    if (parent_dots & ~h19_mask).any():
        raise ValueError("parent contains dots outside the H19 physical field")
    moves = sorted(set(int(n) for n in n_moves))
    n_dots = int(parent_dots.sum())
    if not moves or moves[0] < 1 or moves[-1] >= n_dots:
        raise ValueError("invalid move counts")

    d_cat = ndi.distance_transform_edt(~catalogue_mask)
    candidate_mask = (
        h19_mask & footprint & ~catalogue_mask & ~parent_dots
        & (d_cat >= CATALOGUE_CLEARANCE_PX)
    )
    source_mask, target_mask, prior_raster, block_stats = make_block_prior(
        catalogue_mask, footprint, parent_dots, candidate_mask,
        block_px=block_px, source_quantile=source_quantile,
        target_quantile=target_quantile,
    )
    source_pool = parent_dots & source_mask
    target_candidates = candidate_mask & target_mask
    if int(source_pool.sum()) < moves[-1] or int(target_candidates.sum()) < moves[-1]:
        raise ValueError("source or target pool is too small for the largest dose")

    # Off-catalogue H19 is a MODEL surrogate for line-like fault truth.
    truth = h19_mask & footprint & ~catalogue_mask
    parent_flat = np.flatnonzero(parent_dots.ravel())
    source_flat = np.flatnonzero(source_pool.ravel())
    source_indices = np.searchsorted(parent_flat, source_flat)
    candidate_points = np.argwhere(target_candidates).astype(np.int32)
    ranking = marginal_rankings(truth, parent_dots, candidate_points)
    rng = np.random.default_rng(seed)
    source_order = np.lexsort((
        rng.random(len(source_indices)),
        -ranking["remove_delta"][source_indices],
    ))
    target_sequence = _greedy_on_truth_from_ranking(
        truth, candidate_points, ranking, moves[-1], seed + 1
    )
    ranked_source_indices = source_indices[source_order]
    ranked_source_points = ranking["points"][ranked_source_indices]
    ranked_target_points = candidate_points[target_sequence["indices"]]
    distance_to_truth = ndi.distance_transform_edt(~truth)

    audit = {
        "source_mask": source_mask,
        "target_mask": target_mask,
        "candidate_mask": candidate_mask,
        "prior_raster": prior_raster,
        "truth": truth,
        "block_stats": block_stats,
        "base_h19_surrogate": ranking["base"],
        "seed": int(seed),
    }
    variants = {}
    previous_removed = previous_added = None
    for n_move in moves:
        chosen_source = ranked_source_indices[:n_move]
        removed_points = ranked_source_points[:n_move]
        added_points = ranked_target_points[:n_move]
        variant = parent_dots.copy()
        variant[removed_points[:, 0], removed_points[:, 1]] = False
        variant[added_points[:, 0], added_points[:, 1]] = True
        added = variant & ~parent_dots
        removed = parent_dots & ~variant
        if previous_removed is not None:
            if not (previous_removed <= removed).all() or not (previous_added <= added).all():
                raise AssertionError("dose series is not nested")
        previous_removed, previous_added = removed, added

        pct = 100.0 * n_move / n_dots
        pct_sym = 100.0 * int((variant ^ parent_dots).sum()) / n_dots
        added_min_dcat = float(d_cat[added].min())
        mask_gates = {
            "count_preserved": int(variant.sum()) == n_dots,
            "exact_removed_and_added": int(removed.sum()) == n_move and int(added.sum()) == n_move,
            "inside_footprint": not (variant & ~footprint).any(),
            "zero_catalogue_mass": not (variant & catalogue_mask).any(),
            "added_dcat_ge_3px": added_min_dcat >= CATALOGUE_CLEARANCE_PX,
            "all_mass_on_h19": not (variant & ~h19_mask).any(),
            "removed_from_low_prior": not (removed & ~source_mask).any(),
            "added_to_high_prior": not (added & ~target_mask).any(),
            "pct_changed_in_1_50": 1.0 <= pct <= 50.0 and 1.0 <= pct_sym <= 50.0,
            "differs_from_parent": not np.array_equal(variant, parent_dots),
        }
        if not all(mask_gates.values()):
            raise ValueError(f"concentration mask gate failed: {mask_gates}")

        surrogate = _dti_from_distances(truth, variant, distance_to_truth)
        nn_before = mass.nn_distances(parent_dots)
        nn_after = mass.nn_distances(variant)
        displacement = cKDTree(added_points).query(removed_points, k=1)[0]
        stats = {
            "n_dots": n_dots,
            "n_moved": n_move,
            "pct_changed": pct,
            "symmetric_difference": int((variant ^ parent_dots).sum()),
            "pct_symmetric_diff": pct_sym,
            "block_px": block_px,
            "block_km": block_px / 10.0,
            "source_prior_per_1000px": block_stats["source_cut_per_1000px"],
            "target_prior_per_1000px": block_stats["target_cut_per_1000px"],
            "removed_mean_block_prior": float(prior_raster[removed].mean()),
            "added_mean_block_prior": float(prior_raster[added].mean()),
            "removed_mean_exact_marginal_dti": float(ranking["remove_delta"][chosen_source].mean()),
            "removed_min_exact_marginal_dti": float(ranking["remove_delta"][chosen_source].min()),
            "added_mean_exact_marginal_dti": float(target_sequence["exact_marginal_dti"][:n_move].mean()),
            "added_min_exact_marginal_dti": float(target_sequence["exact_marginal_dti"][:n_move].min()),
            "removed_mean_unique_h19_credit": float(ranking["remove_unique_truth_credit"][chosen_source].mean()),
            "added_mean_new_h19_credit": float(target_sequence["truth_credit"][:n_move].mean()),
            "h19_surrogate_parent": ranking["base"],
            "h19_surrogate_variant": surrogate,
            "h19_surrogate_delta": surrogate["DTI"] - ranking["base"]["DTI"],
            "mean_displacement_px": float(displacement.mean()),
            "median_displacement_px": float(np.median(displacement)),
            "nn_median_before_px": float(np.median(nn_before)),
            "nn_median_after_px": float(np.median(nn_after)),
            "nn_lt_3px_before": int((nn_before < 3.0).sum()),
            "nn_lt_3px_after": int((nn_after < 3.0).sum()),
            "collar_lt3px_before": int((d_cat[parent_dots] < 3.0).sum()),
            "collar_lt3px_after": int((d_cat[variant] < 3.0).sum()),
            "added_min_catalogue_clearance_px": added_min_dcat,
            "mask_gates": mask_gates,
        }
        for km, bp in ((1, 10), (2, 20), (5, 50)):
            cv_before, nb = mass.block_density_cv(parent_dots, footprint, bp)
            cv_after, _ = mass.block_density_cv(variant, footprint, bp)
            stats[f"cv_{km}km_before"] = cv_before
            stats[f"cv_{km}km_after"] = cv_after
            stats[f"cv_{km}km_blocks"] = nb
        variants[n_move] = (variant, stats)
    return variants, audit


def predicted_delta(n_move, h19_surrogate_delta, anchor_d=ANCHOR_D):
    """Additive MODEL sensitivity, charging the measured H19 counter-indicator.

    Block-prior scenarios are effective live credit per moved dot: -0.050,
    +0.025, +0.100, scaled by the recorded upstream anchor D.  The measured
    H19 surrogate delta is added unchanged as a structural coverage cost.  The
    two components have different truth sets, so this is deliberately an
    uncalibrated sensitivity band, not a confidence interval or live score.
    """
    credits = {"lo": -0.050, "central": 0.025, "hi": 0.100}
    out = {
        key: h19_surrogate_delta + n_move * value / anchor_d
        for key, value in credits.items()
    }
    out["effective_credit_per_moved_dot"] = credits
    out["h19_surrogate_counterindicator"] = h19_surrogate_delta
    out["anchor_d"] = anchor_d
    out["evidence_class"] = "MODEL"
    return out
