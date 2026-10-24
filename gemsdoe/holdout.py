"""Protocol segment holdout: hide-and-recover with whole fault segments.

Parallel-run protocol (session prompt, item 2): withhold whole fault
segments with a buffer, derive every catalogue-based feature only from the
visible faults, mask visible faults pixel-exactly, score pooled DTI
(alpha 0.2, beta 0.8, 300 m triangular kernel = `gemsdoe.metric`).

This is a DIFFERENT instrument from `proxy.hide_and_recover` (pixel-random
30% recall), whose known degeneracies are documented in IRREGULARITIES
item 4.  Here a "segment" is an 8-connected component of the catalogue
mask with >= `min_segment_px` pixels; each segment is withheld wholly in
exactly one of K folds (seeded assignment stratified by segment size).
Pixels within `buffer_px` of a withheld segment are excluded from the
visible catalogue for that fold, so no catalogue-derived quantity
(d_cat collars, parent prune) can see the withheld fault or its collar.

The caller supplies `build_fn(visible_catalogue_mask) -> dots_mask`, which
must rebuild BOTH the parent and the candidate from the visible catalogue
alone (plus catalogue-free inputs).  Scoring per fold: predictions on
visible-catalogue pixels are zeroed (pixel-exact masking, as in live
scoring), truth is the withheld segments, and DTI sufficient statistics
(T, S, M, |G|) are pooled across folds before forming the ratio.

The 95% CI is a segment cluster bootstrap of the pooled DTI difference:
withheld segments are resampled with replacement; T and |G| are recomputed
from per-segment kernel credits against each fold's fixed predictions,
while S and M are held at their realised values (stated conditional CI).

Every number produced here is HOLDOUT-DTI, never a live score.  Catalogue
segments are surface-mapped faults; recovering them is a proxy for, not a
measurement of, blind-fault discovery.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi

from .metric import KERNEL_RADIUS_PX, kernel_weight

EVALUATOR_VERSION = "segment-holdout-v1 (gemsdoe/holdout.py; metric DTI a=0.2 b=0.8 R=3px)"


def segment_labels(catalogue: np.ndarray, foot: np.ndarray,
                   min_segment_px: int = 20):
    """(label image, list of segment ids kept) using 8-connectivity."""
    cat = np.asarray(catalogue, dtype=bool) & np.asarray(foot, dtype=bool)
    lab, _ = ndi.label(cat, structure=np.ones((3, 3), dtype=np.int8))
    sizes = np.bincount(lab.ravel())
    keep = [i for i in range(1, len(sizes)) if sizes[i] >= min_segment_px]
    return lab, keep


def assign_folds(lab: np.ndarray, keep: list[int], k_folds: int = 5,
                 seed: int = 20261024) -> dict[int, int]:
    """Seeded size-stratified whole-segment fold assignment."""
    sizes = {i: int((lab == i).sum()) for i in keep}
    rng = np.random.default_rng(seed)
    ids = list(keep)
    rng.shuffle(ids)
    ids.sort(key=lambda i: -sizes[i])  # largest first, shuffle breaks ties
    fold_of, fold_px = {}, np.zeros(k_folds, dtype=int)
    for i in ids:  # greedy balance by withheld pixel count
        f = int(np.argmin(fold_px))
        fold_of[i] = f
        fold_px[f] += sizes[i]
    return fold_of


def _fold_stats(truth: np.ndarray, pred_masked: np.ndarray):
    """DTI sufficient statistics (T, S, M, |G|) for one fold."""
    g = float(truth.sum())
    s = float(pred_masked.sum())
    if g == 0 or s == 0:
        return 0.0, s, 0.0, g
    d_to_pred = ndi.distance_transform_edt(~pred_masked)
    t = float(kernel_weight(d_to_pred[truth]).sum())
    d_to_truth = ndi.distance_transform_edt(~truth)
    m = float(kernel_weight(d_to_truth[pred_masked]).sum())
    return t, s, m, g


def _dti_from_stats(t, s, m, g):
    denom = 0.2 * t + 0.2 * (s - m) + 0.8 * g
    return float(t / denom) if denom > 0 else 0.0


def run_segment_holdout(build_parent, build_candidate, catalogue, foot,
                        k_folds: int = 5, buffer_px: float = 10.0,
                        min_segment_px: int = 20, seed: int = 20261024,
                        n_bootstrap: int = 2000, boot_seed: int = 7):
    """Pooled HOLDOUT-DTI for candidate vs parent.  See module docstring."""
    cat = np.asarray(catalogue, dtype=bool) & foot
    lab, keep = segment_labels(cat, foot, min_segment_px)
    fold_of = assign_folds(lab, keep, k_folds, seed)

    stats = {"parent": [0.0, 0.0, 0.0, 0.0], "candidate": [0.0, 0.0, 0.0, 0.0]}
    per_segment = []  # (g_s, t_parent_s, t_candidate_s) for the bootstrap
    folds = []
    for f in range(k_folds):
        withheld_ids = [i for i in keep if fold_of[i] == f]
        truth = np.isin(lab, withheld_ids)
        near_withheld = ndi.distance_transform_edt(~truth) <= buffer_px
        visible = cat & ~near_withheld

        entry = {"fold": f, "n_segments": len(withheld_ids),
                 "n_withheld_px": int(truth.sum())}
        d_to = {}
        for name, build in (("parent", build_parent),
                            ("candidate", build_candidate)):
            dots = np.asarray(build(visible), dtype=bool) & foot
            dots[visible] = False  # mask visible faults pixel-exactly
            t, s, m, g = _fold_stats(truth, dots)
            for j, v in enumerate((t, s, m, g)):
                stats[name][j] += v
            entry[name] = {"dti_fold": _dti_from_stats(t, s, m, g),
                           "n_dots_masked": int(dots.sum()), "T": t, "S": s,
                           "M": m, "G": g}
            d_to[name] = ndi.distance_transform_edt(~dots)
        for i in withheld_ids:
            seg = lab == i
            per_segment.append((
                float(seg.sum()),
                float(kernel_weight(d_to["parent"][seg]).sum()),
                float(kernel_weight(d_to["candidate"][seg]).sum()),
            ))
        folds.append(entry)

    pooled = {k: _dti_from_stats(*v) for k, v in stats.items()}
    diff = pooled["candidate"] - pooled["parent"]

    seg = np.asarray(per_segment)
    rng = np.random.default_rng(boot_seed)
    n = len(seg)
    boot = np.empty(n_bootstrap)
    for b in range(n_bootstrap):
        idx = rng.integers(0, n, n)
        g_b = seg[idx, 0].sum()
        scale = {}  # hold S, M fixed; rescale T,G by bootstrap totals
        d = {}
        for name, col in (("parent", 1), ("candidate", 2)):
            t_b = seg[idx, col].sum()
            _, s_fix, m_fix, _ = stats[name]
            d[name] = _dti_from_stats(t_b, s_fix, m_fix, g_b)
        boot[b] = d["candidate"] - d["parent"]
    lo, hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))

    return {
        "evaluator": EVALUATOR_VERSION,
        "k_folds": k_folds, "buffer_px": buffer_px,
        "min_segment_px": min_segment_px, "seed": seed,
        "n_segments_total": len(keep),
        "n_withheld_positives_px": int(sum(f_["n_withheld_px"] for f_ in folds)),
        "pooled_holdout_dti_parent": pooled["parent"],
        "pooled_holdout_dti_candidate": pooled["candidate"],
        "diff_candidate_minus_parent": diff,
        "diff_ci95_bootstrap_segments": [lo, hi],
        "n_bootstrap": n_bootstrap,
        "ci_note": "segment cluster bootstrap of (T,|G|) at fixed realised (S,M)",
        "folds": folds,
    }
