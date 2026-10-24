"""Spatially blocked holdout and registry-drift tools for GEMSDOE89.

The evaluator is deliberately distinct from the older pixel-random catalogue
proxy in ``gemsdoe.proxy``. It holds out whole 8-connected fault components by
large spatial tiles, removes a 300 m buffer around held-out components from the
visible catalogue, and scores only held-out fault pixels inside tile interiors.
Prediction/truth interactions cannot cross tile boundaries because each tile
is inset by the DTI kernel radius. The pooled metric is assembled from exact
per-tile DTI sufficient statistics; its confidence interval is a spatial-tile
cluster bootstrap.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi
from scipy.stats import rankdata, spearmanr

from .metric import kernel_weight

KERNEL_RADIUS_PX = 3.0
EVALUATOR_VERSION = "GEMSDOE89-spatial-segment-holdout-v1"


def conductivity_edge(cond: np.ndarray, valid: np.ndarray, scales=(2.0, 4.0)) -> np.ndarray:
    """Max multi-scale Gaussian gradient magnitude of the conductivity layer.

    Invalid/nodata cells are median-filled only for convolution and are not
    eligible output pixels. A 2*max(scale)+1 support erosion prevents nodata
    boundaries from being interpreted as conductivity edges.
    """
    field = np.asarray(cond, dtype=np.float32)
    valid = np.asarray(valid, dtype=bool) & np.isfinite(field) & (field > -1.0e30)
    if not valid.any():
        raise ValueError("conductivity layer has no valid cells")
    med = np.float32(np.median(field[valid]))
    filled = np.where(valid, field, med).astype(np.float32, copy=False)
    out = np.zeros(field.shape, dtype=np.float32)
    for sigma in scales:
        grad = ndi.gaussian_gradient_magnitude(filled, sigma=float(sigma), mode="nearest")
        np.maximum(out, grad, out=out)
        del grad
    support = ndi.minimum_filter(valid.astype(np.uint8), size=2 * int(np.ceil(max(scales))) + 1,
                                 mode="constant", cval=0) > 0
    out[~support] = np.nan
    return out


def potential_field_edge(fields: dict[str, np.ndarray], valid: np.ndarray,
                         scales=(2.0, 4.0)) -> np.ndarray:
    """Max multi-scale Gaussian gradient magnitude across potential-field layers.

    For each named layer, invalid cells are median-filled for convolution only;
    per-layer, per-scale gradients are combined by elementwise maximum so a
    ridge scores where either the magnetic or the gravity field has an edge at
    either smoothing scale. Nodata boundaries are eroded out of the output.
    """
    out = None
    for name in sorted(fields):
        field = np.asarray(fields[name], dtype=np.float32)
        v = np.asarray(valid, dtype=bool) & np.isfinite(field) & (field > -1.0e30)
        if not v.any():
            continue
        med = np.float32(np.median(field[v]))
        filled = np.where(v, field, med).astype(np.float32, copy=False)
        for sigma in scales:
            grad = ndi.gaussian_gradient_magnitude(filled, sigma=float(sigma), mode="nearest")
            grad = np.where(v, grad, 0.0).astype(np.float32, copy=False)
            out = grad if out is None else np.maximum(out, grad)
            del grad
    if out is None:
        raise ValueError("no valid potential-field layers")
    support = ndi.minimum_filter(valid.astype(np.uint8), size=2 * int(np.ceil(max(scales))) + 1,
                                 mode="constant", cval=0) > 0
    out[~support] = np.nan
    return out


def select_spaced_peaks(score: np.ndarray, eligible: np.ndarray, n: int,
                        min_sep_px: float = 2.8) -> np.ndarray:
    """Deterministically take the highest-scoring local peaks with disk NMS."""
    score = np.asarray(score, dtype=np.float32)
    eligible = np.asarray(eligible, dtype=bool) & np.isfinite(score)
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return np.zeros(score.shape, dtype=bool)
    # Local maxima shrink the search pool; deterministic row/column ordering
    # resolves exact ties after descending score order.
    safe = np.where(eligible, score, -np.inf)
    local = ndi.maximum_filter(safe, size=7, mode="constant", cval=-np.inf)
    peak = eligible & (safe == local)
    ys, xs = np.nonzero(peak)
    if len(ys) < n:
        ys, xs = np.nonzero(eligible)
    vals = score[ys, xs]
    order = np.lexsort((xs, ys, -vals))
    ys, xs = ys[order], xs[order]

    radius = float(min_sep_px)
    r = int(np.ceil(radius))
    dy, dx = np.mgrid[-r:r + 1, -r:r + 1]
    keep_disk = dy * dy + dx * dx <= radius * radius + 1e-9
    off_y, off_x = dy[keep_disk], dx[keep_disk]
    blocked = np.zeros(score.shape, dtype=bool)
    out = np.zeros(score.shape, dtype=bool)
    count = 0
    h, w = score.shape
    for y0, x0 in zip(ys, xs):
        y, x = int(y0), int(x0)
        if blocked[y, x]:
            continue
        out[y, x] = True
        count += 1
        ry, rx = y + off_y, x + off_x
        inside = (ry >= 0) & (ry < h) & (rx >= 0) & (rx < w)
        blocked[ry[inside], rx[inside]] = True
        if count == n:
            break
    if count != n:
        raise ValueError(f"only placed {count} spaced peaks; requested {n}")
    return out


def tile_fold_map(shape: tuple[int, int], tile_px: int = 512, n_folds: int = 5):
    """Assign each map tile to a deterministic fold; return fold-id raster/tiles."""
    h, w = shape
    fold_map = np.full(shape, -1, dtype=np.int8)
    tiles = []
    for y0 in range(0, h, tile_px):
        y1 = min(h, y0 + tile_px)
        by = y0 // tile_px
        for x0 in range(0, w, tile_px):
            x1 = min(w, x0 + tile_px)
            bx = x0 // tile_px
            fold = (3 * bx + 2 * by) % n_folds
            fold_map[y0:y1, x0:x1] = fold
            tiles.append({"y0": y0, "y1": y1, "x0": x0, "x1": x1,
                          "bx": bx, "by": by, "fold": fold})
    return fold_map, tiles


def component_holdouts(catalogue: np.ndarray, fold_map: np.ndarray,
                       tiles: list[dict], n_folds: int = 5, buffer_px: float = 3.0):
    """Withhold whole connected segments touching each fold's test tiles.

    The visible catalogue for a fold is further masked within ``buffer_px`` of
    held-out segments. Returns component labels and per-fold masks.
    """
    cat = np.asarray(catalogue, dtype=bool)
    labels, n_labels = ndi.label(cat, structure=np.ones((3, 3), dtype=np.uint8))
    by_fold = []
    for fold in range(n_folds):
        test_tile = np.zeros(cat.shape, dtype=bool)
        for t in tiles:
            if t["fold"] == fold:
                test_tile[t["y0"]:t["y1"], t["x0"]:t["x1"]] = True
        ids = np.unique(labels[test_tile & cat])
        ids = ids[ids > 0]
        hid = np.zeros(n_labels + 1, dtype=bool)
        hid[ids] = True
        hidden = cat & hid[labels]
        visible = cat & ~hidden
        if hidden.any() and buffer_px > 0:
            d_to_hidden = ndi.distance_transform_edt(~hidden)
            visible &= d_to_hidden > float(buffer_px)
        by_fold.append({"fold": fold, "hidden": hidden, "visible": visible,
                        "hidden_component_ids": ids, "test_tile": test_tile})
    return labels, n_labels, by_fold


def metric_components(truth: np.ndarray, pred: np.ndarray,
                      radius_px: float = KERNEL_RADIUS_PX) -> dict:
    """Exact DTI sufficient statistics T, S, M, G for a disjoint tile."""
    truth = np.asarray(truth, dtype=bool)
    pred = np.asarray(pred, dtype=bool)
    if truth.shape != pred.shape:
        raise ValueError("truth and prediction shapes differ")
    g = int(truth.sum())
    s = int(pred.sum())
    if g and s:
        d_pred = ndi.distance_transform_edt(~pred)
        t = float(np.clip(1.0 - d_pred[truth] / radius_px, 0.0, 1.0).sum())
    else:
        # EDT on an all-ones array measures distance to its implicit outside
        # background; an empty prediction must not get phantom TP credit.
        t = 0.0
    if s and g:
        d_truth = ndi.distance_transform_edt(~truth)
        m = float(np.clip(1.0 - d_truth[pred] / radius_px, 0.0, 1.0).sum())
    else:
        m = 0.0
    return {"T": t, "S": float(s), "M": m, "G": float(g)}


def dti_from_components(rows: list[dict]) -> float:
    """Pooled official-form DTI from non-overlapping spatial tile statistics."""
    t = sum(float(x["T"]) for x in rows)
    s = sum(float(x["S"]) for x in rows)
    m = sum(float(x["M"]) for x in rows)
    g = sum(float(x["G"]) for x in rows)
    den = 0.2 * t + 0.2 * (s - m) + 0.8 * g
    return float(t / den) if den else 0.0


def bootstrap_dti(rows: list[dict], seed: int = 20261024,
                  n_boot: int = 2000) -> tuple[list[float], dict]:
    """Spatial-tile cluster bootstrap CI for pooled DTI."""
    if len(rows) < 2:
        raise ValueError("at least two spatial tiles are required for bootstrap CI")
    rng = np.random.default_rng(seed)
    t = np.asarray([r["T"] for r in rows], dtype=np.float64)
    s = np.asarray([r["S"] for r in rows], dtype=np.float64)
    m = np.asarray([r["M"] for r in rows], dtype=np.float64)
    g = np.asarray([r["G"] for r in rows], dtype=np.float64)
    draws = np.empty(n_boot, dtype=np.float64)
    for i in range(n_boot):
        ix = rng.integers(0, len(rows), len(rows))
        tt, ss, mm, gg = t[ix].sum(), s[ix].sum(), m[ix].sum(), g[ix].sum()
        den = 0.2 * tt + 0.2 * (ss - mm) + 0.8 * gg
        draws[i] = tt / den if den else 0.0
    ci = {"lower_95": float(np.quantile(draws, 0.025)),
          "upper_95": float(np.quantile(draws, 0.975)),
          "method": "percentile bootstrap over non-overlapping 512 px spatial tiles",
          "n_bootstrap": int(n_boot), "n_spatial_tiles": int(len(rows)),
          "seed": int(seed)}
    return draws, ci


def paired_delta_bootstrap(candidate_rows: list[dict], baseline_rows: list[dict],
                           seed: int = 20261024, n_boot: int = 2000):
    """Paired tile bootstrap of candidate-minus-baseline pooled DTI."""
    if len(candidate_rows) != len(baseline_rows) or len(candidate_rows) < 2:
        raise ValueError("paired bootstrap requires equal, multiple tile rows")
    rng = np.random.default_rng(seed + 1)
    ndx = len(candidate_rows)
    draws = np.empty(n_boot, dtype=np.float64)
    for i in range(n_boot):
        ix = rng.integers(0, ndx, ndx)
        draws[i] = (dti_from_components([candidate_rows[j] for j in ix]) -
                    dti_from_components([baseline_rows[j] for j in ix]))
    return {"lower_95": float(np.quantile(draws, 0.025)),
            "upper_95": float(np.quantile(draws, 0.975)),
            "method": "paired percentile bootstrap over non-overlapping spatial tiles",
            "n_bootstrap": int(n_boot), "n_spatial_tiles": int(ndx),
            "seed": int(seed + 1)}


def auc_strength(feature: np.ndarray, labels: np.ndarray, domain: np.ndarray,
                 seed: int = 11, n_pos: int = 25000, n_neg: int = 100000):
    """Stratified rank AUC on holdout pixels; strength is max(AUC, 1-AUC)."""
    f = np.asarray(feature).ravel()
    y = np.asarray(labels, dtype=bool).ravel()
    d = np.asarray(domain, dtype=bool).ravel() & np.isfinite(f)
    pos = np.flatnonzero(d & y)
    neg = np.flatnonzero(d & ~y)
    if not len(pos) or not len(neg):
        return {"auc": None, "strength": None, "n_positive": int(len(pos)),
                "n_negative": int(len(neg)), "flag_leakage": False}
    rng = np.random.default_rng(seed)
    if len(pos) > n_pos:
        pos = rng.choice(pos, n_pos, replace=False)
    if len(neg) > n_neg:
        neg = rng.choice(neg, n_neg, replace=False)
    vals = np.concatenate((f[pos].astype(np.float64), f[neg].astype(np.float64)))
    labels_sample = np.r_[np.ones(len(pos), dtype=bool), np.zeros(len(neg), dtype=bool)]
    ranks = rankdata(vals, method="average")
    n1, n0 = int(labels_sample.sum()), int((~labels_sample).sum())
    auc = float((ranks[labels_sample].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))
    strength = max(auc, 1.0 - auc)
    return {"auc": auc, "strength": strength, "n_positive": int(n1),
            "n_negative": int(n0), "flag_leakage": bool(strength > 0.90)}


def surface_registry_audit(surface: np.ndarray, footprint: np.ndarray,
                           dot_mask: np.ndarray, registry_paths: list[Path],
                           seed: int = 20261024, sample_n: int = 150000,
                           overlap_radius_px: float = 3.0,
                           surface_label: str = "candidate score surface") -> dict:
    """Audit surface rank-correlation and dot proximity vs local registry rasters.

    The audit deduplicates reference rasters by their positive-pixel mask hash.
    ``registry_paths`` must include all locally available release TIFFs and
    pinned ancestor rasters; it cannot infer remote rasters absent from disk.
    """
    import rasterio

    surface = np.asarray(surface, dtype=np.float32)
    foot = np.asarray(footprint, dtype=bool) & np.isfinite(surface)
    dots = np.asarray(dot_mask, dtype=bool)
    flat_valid = np.flatnonzero(foot.ravel())
    if len(flat_valid) > sample_n:
        sample = np.random.default_rng(seed).choice(flat_valid, sample_n, replace=False)
    else:
        sample = flat_valid
    surf_values = surface.ravel()[sample]
    unique = {}
    for path in sorted(set(Path(p) for p in registry_paths)):
        if not path.exists():
            continue
        with rasterio.open(path) as ds:
            a = ds.read(1)
        ref = np.isfinite(a) & (a > 0)
        if ref.shape != dots.shape:
            continue
        digest = hashlib.sha256(np.packbits(ref.ravel()).tobytes()).hexdigest()
        unique.setdefault(digest, {"path": path, "mask": ref})

    def display_path(path: Path) -> str:
        root = Path(__file__).resolve().parents[1]
        try:
            return path.resolve().relative_to(root).as_posix()
        except ValueError:
            return path.as_posix()

    correlations = []
    overlaps = []
    for item in unique.values():
        ref = item["mask"]
        ref_flat = ref.ravel()
        # Spearman is estimated on one deterministic common footprint sample.
        with np.errstate(invalid="ignore"):
            corr = float(spearmanr(surf_values, ref_flat[sample]).statistic)
        if np.isfinite(corr):
            correlations.append({"r_spearman": corr, "registry_raster": display_path(item["path"])})
        if dots.any() and ref.any():
            dist = ndi.distance_transform_edt(~ref)
            pct = float(np.mean(dist[dots] <= overlap_radius_px))
        else:
            pct = 0.0
        overlaps.append({"fraction_dots_within_3px": pct,
                         "registry_raster": display_path(item["path"]),
                         "registry_positive_pixels": int(ref.sum())})
    correlations.sort(key=lambda x: abs(x["r_spearman"]), reverse=True)
    overlaps.sort(key=lambda x: x["fraction_dots_within_3px"], reverse=True)
    max_r = abs(correlations[0]["r_spearman"]) if correlations else 0.0
    max_overlap = overlaps[0]["fraction_dots_within_3px"] if overlaps else 0.0
    return {"surface_tested": surface_label,
            "n_reference_geometries": len(unique), "n_reference_paths": len(registry_paths),
            "sample_pixels": int(len(sample)), "max_abs_surface_spearman": max_r,
            "max_dot_overlap_3px": max_overlap,
            "duplicate_stop": bool(max_r > 0.90 or max_overlap > 0.70),
            "top_correlations": correlations[:5], "top_overlaps": overlaps[:5],
            "audit_scope": "all existing releases/*.tif plus pinned parent/ancestor rasters; remote site rasters absent from this checkout are not inferred"}


# Shared segment-fold API retained for the BSTP builders merged from main.
# The COND-EDGE run card uses the stricter disjoint-tile evaluator above.
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
                        k_folds: int = 5, buffer_px: float = 3.0,
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
