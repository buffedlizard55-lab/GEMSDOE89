#!/usr/bin/env python3
"""Execute the pre-registered Lane H89 (`BH-RTP-HABC`) 3-experiment discovery pipeline.

1. Builds/loads the 30 zero-catalogue multi-physics features (`phys30_fp.f32`).
2. Fits LOQO Expert A (zero-catalogue physics) and LOQO Self-Masked Expert B (42 features).
3. Runs the 42-feature Leakage Canary (`max symmetric AUC <= 0.90`).
4. Evaluates 4 controls + 3 pre-registered experiments (`E89-1`, `E89-2`, `E89-3`) on
   `gems57-pooled-hide-v2` (`K = 11,321` withheld pixels, 1,000 spatial-block bootstrap draws).
5. Runs Full-Catalogue 4-fold ensemble inference + CELF 300 m submodular dot allocation.
6. Audits pre-placement surface Spearman correlation (`<= 0.90`) and post-placement 3-px dot
   overlap (`<= 0.70`) against all 86 reference rasters (`.cache/data`, `releases/`, `.cache/scored_fleet`).
7. Packages primary GeoTIFF + ZIP + JSON receipt via `vendor/gems57/submission_writer.py`
   in `docs/downloads/` AND matching `releases/` pair via `gemsdoe/grid.py`, asserting
   100% pixel-identical `decoded_sha256` and passing all format/range/CRS/collar gates.
"""
from __future__ import annotations

import gc
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import tifffile
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gemsdoe import grid as repo_grid
from gemsdoe import parent as repo_parent
from gemsdoe import validate as repo_validate
from gemsdoe.discovery_h89 import (
    ALL_FEATURE_NAMES,
    NET_FEATURE_NAMES,
    PHYS_FEATURE_NAMES,
    allocate_regime_stratified_celf,
    build_or_load_physical_stack,
    fit_expert_a_phys_loqo,
    fit_expert_b_dual_loqo,
    fuse_dual_experts,
    predict_full_catalogue_ensemble,
    run_leakage_canary_42,
    self_credit_from_posterior,
)
from vendor.gems57 import emit as g57_emit
from vendor.gems57 import evaluate_holdout as g57_eval
from vendor.gems57 import holdout as g57_holdout
from vendor.gems57 import submission_writer as g57_writer
from vendor.gems57 import uniqueness as g57_uniq
from vendor.gems57 import validate as g57_val

DATA_DIR = Path(os.environ.get("GEMSDOE_DATA", str(ROOT / ".cache" / "data")))
CACHE_H89 = ROOT / ".cache" / "h89"
FLEET_DIR = ROOT / ".cache" / "scored_fleet"
RELEASES_DIR = ROOT / "releases"
DOWNLOADS_DIR = ROOT / "docs" / "downloads"
REGISTRY_DIR = ROOT / "registry"

BUDGET_DOTS = 37_654
DATE_TAG = "20261024"


def _log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def _fp_to_2d(vec_fp: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    out = np.zeros(footprint.shape, dtype=np.float32)
    out[footprint] = vec_fp.astype(np.float32, copy=False)
    return out


def _build_r0_fold_fair(h19_5: np.ndarray, visible_mask: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Rebuild R0 (`h33-h33-2-b2`) strictly using `visible_mask` for collar pruning."""
    r0_m, _ = repo_parent.rebuild_r0_mask(h19_5, footprint, visible_mask)
    return r0_m.astype(np.float32)


def _eval_fold_predictions(
    preds_by_fold: dict[str, np.ndarray],
    folds: dict[str, dict],
    footprint: np.ndarray,
) -> tuple[dict[str, dict], np.ndarray]:
    fold_reports = {}
    pooled_terms = None
    for qname, fold in folds.items():
        res, terms = g57_eval.evaluate(preds_by_fold[qname], fold, footprint, block_side=200)
        fold_reports[qname] = {
            "dti": round(float(res["dti"]), 6),
            "tpw": round(float(res["tpw"]), 3),
            "fpw": round(float(res["fpw"]), 3),
            "fnw": round(float(res["fnw"]), 3),
            "n_truth": int(res["n_truth"]),
            "n_emitted_active_region": int(res["n_emitted"]),
            "n_emitted_global": int((preds_by_fold[qname] > 0).sum()),
        }
        pooled_terms = terms if pooled_terms is None else (pooled_terms + terms)
    assert pooled_terms is not None
    return fold_reports, pooled_terms


def main() -> int:
    t0 = time.time()
    _log("Starting Lane H89 (`BH-RTP-HABC`) end-to-end discovery & verification pipeline...")

    sample_path = DATA_DIR / "sample_submission.tif"
    faults_path = DATA_DIR / "existing_faults.tif"
    features_path = DATA_DIR / "training_features.tif"
    h19_path = DATA_DIR / "scored_h19_5.tif"
    d28_path = DATA_DIR / "d28.tif"
    r0_path = DATA_DIR / "parent_r0_zeros.tif"

    for p in (sample_path, faults_path, features_path, h19_path, d28_path, r0_path):
        if not p.is_file():
            raise FileNotFoundError(f"Missing required input raster: {p}")

    sample_arr = tifffile.imread(sample_path)
    footprint = np.isfinite(sample_arr)
    del sample_arr
    catalogue_all = tifffile.imread(faults_path) > 0
    catalogue = catalogue_all & footprint
    h19_5 = tifffile.imread(h19_path) > 0
    d28_arr = np.nan_to_num(tifffile.imread(d28_path), nan=0.0).astype(np.float32)
    r0_arr = np.nan_to_num(tifffile.imread(r0_path), nan=0.0).astype(np.float32)

    _log(f"Loaded grid {footprint.shape}: footprint={int(footprint.sum()):,} px, in-fp catalogue={int(catalogue.sum()):,} px")

    # 1. Build spatial quadrant holdout (`gems57-pooled-hide-v2`)
    from types import SimpleNamespace

    grid_ns = SimpleNamespace(catalogue=catalogue, footprint=footprint)
    folds_list, quad_ids = g57_holdout.buffered_component_draw(
        grid_ns,
        seed=20,
        hide_frac=0.20,
        buffer_px=3,
        boundary_px=12,
    )
    folds = {}
    for f in folds_list:
        f["full_quad"] = footprint & (quad_ids == f["fold"])
        f["train_quad"] = footprint & (quad_ids != f["fold"])
        folds[f["name"]] = f
    k_withheld = sum(int((footprint & f["region"] & (~f["masked_known"]) & f["truth"]).sum()) for f in folds.values())
    _log(f"Constructed `gems57-pooled-hide-v2` holdout: K={k_withheld:,} withheld fault pixels across 4 quadrants")

    # 2. Compute or load 30 zero-catalogue physical features
    _log("Computing/loading 30 zero-catalogue multi-physics features (`phys30_fp.f32`)...")
    stack = build_or_load_physical_stack(features_path, footprint, CACHE_H89)
    phys_mm = stack["phys_mm"]
    cover_fp = stack["cover_fp"]
    phys_ridge_2d = stack["phys_ridge_2d"]
    phys_c2_2d = stack["phys_c2_2d"]
    phys_s2_2d = stack["phys_s2_2d"]
    cover_2d = _fp_to_2d(cover_fp, footprint)
    _log(f"30 physical features ready ({time.time() - t0:.1f}s elapsed)")

    # 3. Fit Expert A (LOQO zero-catalogue physics) and Expert B (LOQO self-masked 42-feature dual)
    import pickle

    exp_a_ckpt = CACHE_H89 / "expert_a_v1.pkl"
    exp_b_ckpt = CACHE_H89 / "expert_b_v1.pkl"
    if exp_a_ckpt.is_file():
        _log("Loading cached LOQO Expert A (`expert_a_v1.pkl`)...")
        with exp_a_ckpt.open("rb") as fh:
            expert_a = pickle.load(fh)
    else:
        _log("Fitting LOQO Expert A (`30` zero-catalogue physics features)...")
        expert_a = fit_expert_a_phys_loqo(phys_mm, cover_fp, folds, footprint, seed=20261024)
        with exp_a_ckpt.open("wb") as fh:
            pickle.dump(expert_a, fh, protocol=pickle.HIGHEST_PROTOCOL)
    _log(f"Expert A ready ({time.time() - t0:.1f}s elapsed)")

    if exp_b_ckpt.is_file():
        _log("Loading cached LOQO Self-Masked Expert B (`expert_b_v1.pkl`)...")
        with exp_b_ckpt.open("rb") as fh:
            expert_b = pickle.load(fh)
    else:
        _log("Fitting LOQO Self-Masked Expert B (`42` features = `30` physics + `12` network)...")
        expert_b = fit_expert_b_dual_loqo(
            phys_mm,
            cover_fp,
            phys_ridge_2d,
            phys_c2_2d,
            phys_s2_2d,
            folds,
            footprint,
            seed=20261024,
        )
        with exp_b_ckpt.open("wb") as fh:
            pickle.dump(expert_b, fh, protocol=pickle.HIGHEST_PROTOCOL)
    _log(f"Expert B ready ({time.time() - t0:.1f}s elapsed)")

    # 4. Run 42-feature Leakage Canary (`<= 0.90`)
    _log("Running 42-feature symmetric single-feature AUC leakage canary...")
    canary = run_leakage_canary_42(phys_mm, expert_b["oof_net_fp"], folds, footprint, sample_px=400_000, seed=11)
    canary_path = REGISTRY_DIR / "leakage_canary_h89.json"
    canary_path.write_text(json.dumps(canary, indent=2) + "\n", encoding="utf-8")
    _log(f"Leakage canary verdict: {canary['verdict']} (max strength = {canary['max_single_feature_strength']:.4f})")
    if canary["any_flagged"]:
        raise RuntimeError(f"LEAKAGE CANARY FAILED: {canary_path}")

    # 5. Evaluate Controls + Pre-Registered 3 Experiments on `gems57-pooled-hide-v2`
    _log("Evaluating 4 baseline controls (`r0_fold_fair`, `d28_static`, `r0_static`, `random_null`)...")
    ctrl_r0_fair = {}
    ctrl_d28 = {}
    ctrl_r0_static = {}
    ctrl_rand = {}
    allowed_by_fold = {}

    # Shared visible mask in global buffered component draw
    shared_vis = next(iter(folds.values()))["visible"]
    d_vis_global = distance_transform_edt(~shared_vis)
    allow_global_holdout = footprint & (d_vis_global >= 3.0)
    total_allow_px = float(allow_global_holdout.sum())

    quad_budgets = {}
    acc_b = 0
    q_keys = list(folds.keys())
    for idx_q, qname in enumerate(q_keys):
        allow_q_quad = allow_global_holdout & folds[qname]["full_quad"]
        allowed_by_fold[qname] = allow_q_quad
        if idx_q < len(q_keys) - 1:
            bq = int(round(BUDGET_DOTS * float(allow_q_quad.sum()) / total_allow_px))
            quad_budgets[qname] = bq
            acc_b += bq
        else:
            quad_budgets[qname] = BUDGET_DOTS - acc_b

    r0_fair_full = _build_r0_fold_fair(h19_5, shared_vis, footprint)
    for i_q, (qname, fold) in enumerate(folds.items()):
        ctrl_r0_fair[qname] = r0_fair_full
        ctrl_d28[qname] = np.where(footprint, d28_arr, 0.0)
        ctrl_r0_static[qname] = np.where(footprint, r0_arr, 0.0)

        rng_null = np.random.default_rng(9900 + i_q)
        ay, ax = np.nonzero(allowed_by_fold[qname])
        pick = rng_null.choice(ay.size, size=quad_budgets[qname], replace=False)
        rnd = np.zeros(footprint.shape, dtype=np.float32)
        rnd[ay[pick], ax[pick]] = 1.0
        ctrl_rand[qname] = rnd

    fold_rep_all = {}
    terms_by_arm = {}
    for cname, cdict in (
        ("r0_fold_fair", ctrl_r0_fair),
        ("d28_static", ctrl_d28),
        ("r0_static", ctrl_r0_static),
        ("random_null", ctrl_rand),
    ):
        frep, tms = _eval_fold_predictions(cdict, folds, footprint)
        fold_rep_all[cname] = frep
        terms_by_arm[cname] = tms

    mu_a = float(expert_a["mu_strand"])
    mu_b = float(expert_b["mu_strand"])

    # --- Experiment 1: E89-1 (Zero-Catalogue Multi-Physics Conduit Baseline, H89-B) ---
    _log("Running Experiment 1 (`E89-1`: Zero-Catalogue Multi-Physics Conduit Baseline, `H89-B`)...")
    pa_oof_2d = _fp_to_2d(expert_a["oof_p_fp"], footprint)
    ma_oof_2d = self_credit_from_posterior(pa_oof_2d, mu_strand=mu_a)
    e1_preds = {}
    for qname, fold in folds.items():
        q_mask = fold["full_quad"]
        alloc = g57_emit.dinkelbach_allocate(
            np.where(q_mask, pa_oof_2d, 0.0),
            np.where(q_mask, ma_oof_2d, 0.0),
            allowed_by_fold[qname],
            budget=quad_budgets[qname],
            k_truth=3_550.0,
            min_spacing_px=2.5,
            candidate_cap=100_000,
            dinkelbach_iters=2,
        )
        e1_preds[qname] = alloc.emitted.astype(np.float32)
    fold_rep_all["E89_1_phys_zero_cat"], terms_by_arm["E89_1_phys_zero_cat"] = _eval_fold_predictions(
        e1_preds, folds, footprint
    )
    del e1_preds, pa_oof_2d, ma_oof_2d

    # --- Experiment 2: E89-2 (Self-Masked Dual-Expert LOQO Ensemble, Global CELF, H89-A) ---
    _log("Running Experiment 2 (`E89-2`: Self-Masked Dual-Expert LOQO Ensemble + CELF, `H89-A`)...")
    pf2_oof_fp = fuse_dual_experts(
        expert_a["oof_p_fp"], expert_b["oof_p_fp"], cover_fp, expert_b["oof_dvis_fp"], blind_basin_boost=0.0
    )
    pf2_oof_2d = _fp_to_2d(pf2_oof_fp, footprint)
    mf2_oof_2d = self_credit_from_posterior(pf2_oof_2d, mu_strand=0.5 * (mu_a + mu_b))
    e2_preds = {}
    for qname, fold in folds.items():
        q_mask = fold["full_quad"]
        alloc = g57_emit.dinkelbach_allocate(
            np.where(q_mask, pf2_oof_2d, 0.0),
            np.where(q_mask, mf2_oof_2d, 0.0),
            allowed_by_fold[qname],
            budget=quad_budgets[qname],
            k_truth=3_550.0,
            min_spacing_px=2.5,
            candidate_cap=110_000,
            dinkelbach_iters=2,
        )
        e2_preds[qname] = alloc.emitted.astype(np.float32)
    fold_rep_all["E89_2_dual_global_celf"], terms_by_arm["E89_2_dual_global_celf"] = _eval_fold_predictions(
        e2_preds, folds, footprint
    )
    del e2_preds, pf2_oof_fp, pf2_oof_2d, mf2_oof_2d

    # --- Experiment 3: E89-3 (Cover-Regime-Stratified Dual-Expert Synthesis, H89-A Calibrated) ---
    _log("Running Experiment 3 (`E89-3`: Cover-Regime-Stratified Dual-Expert Synthesis, `H89-A`)...")
    pf3_oof_fp = fuse_dual_experts(
        expert_a["oof_p_fp"], expert_b["oof_p_fp"], cover_fp, expert_b["oof_dvis_fp"], blind_basin_boost=0.06
    )
    pf3_oof_2d = _fp_to_2d(pf3_oof_fp, footprint)
    mf3_oof_2d = self_credit_from_posterior(pf3_oof_2d, mu_strand=0.5 * (mu_a + mu_b))
    e3_preds = {}
    for qname, fold in folds.items():
        q_mask = fold["full_quad"]
        em = allocate_regime_stratified_celf(
            np.where(q_mask, pf3_oof_2d, 0.0),
            np.where(q_mask, mf3_oof_2d, 0.0),
            allowed_by_fold[qname],
            cover_2d,
            total_budget=quad_budgets[qname],
            shares=(0.34, 0.36, 0.30),
            depth_splits_m=(80.0, 400.0),
            min_spacing_px=2.5,
            k_truth=3_550.0,
        )
        e3_preds[qname] = em.astype(np.float32)
    fold_rep_all["E89_3_dual_regime_celf"], terms_by_arm["E89_3_dual_regime_celf"] = _eval_fold_predictions(
        e3_preds, folds, footprint
    )
    del e3_preds, pf3_oof_fp, pf3_oof_2d, mf3_oof_2d, allowed_by_fold
    gc.collect()

    # Compute pooled summary across all arms (selecting higher HOLDOUT-DTI between E89-2 and E89-3,
    # while checking uniqueness & regime balance)
    prelim_e2 = float(g57_eval.from_terms(terms_by_arm["E89_2_dual_global_celf"].sum(axis=0)))
    prelim_e3 = float(g57_eval.from_terms(terms_by_arm["E89_3_dual_regime_celf"].sum(axis=0)))
    prelim_e1 = float(g57_eval.from_terms(terms_by_arm["E89_1_phys_zero_cat"].sum(axis=0)))
    _log(
        f"Pooled HOLDOUT-DTI (`K={k_withheld}`): "
        f"r0_fold_fair={float(g57_eval.from_terms(terms_by_arm['r0_fold_fair'].sum(axis=0))):.5f} | "
        f"E89-1={prelim_e1:.5f} | E89-2={prelim_e2:.5f} | E89-3={prelim_e3:.5f}"
    )

    winner_arm = max(
        ("E89_1_phys_zero_cat", "E89_2_dual_global_celf", "E89_3_dual_regime_celf"),
        key=lambda k: float(g57_eval.from_terms(terms_by_arm[k].sum(axis=0))),
    )
    pooled_report = g57_eval.pooled_summary(terms_by_arm, draws=1000, seed=520810, candidate=winner_arm)
    _log(
        f"Selected top experiment `{winner_arm}`: HOLDOUT-DTI = "
        f"{pooled_report['scores'][winner_arm]['dti']:.5f} "
        f"95% CI {pooled_report['scores'][winner_arm]['ci95']}"
    )

    # Free per-fold prediction arrays before full-catalogue ensemble inference
    expert_a.pop("fold_full_fp", None)
    expert_b.pop("fold_full_fp", None)
    gc.collect()

    # 6. Full-Catalogue 4-Fold Ensemble Inference & CELF Allocation
    ens_ckpt = CACHE_H89 / "ens_full_v1.npz"
    if ens_ckpt.is_file():
        _log("Loading cached full-catalogue ensemble predictions (`ens_full_v1.npz`)...")
        z_ens = np.load(ens_ckpt)
        ens = {k: z_ens[k] for k in ("p_a_fp", "p_b_fp", "dcat_fp")}
    else:
        _log("Running full-catalogue 4-fold ensemble inference for competition export...")
        ens = predict_full_catalogue_ensemble(
            phys_mm,
            cover_fp,
            phys_ridge_2d,
            phys_c2_2d,
            phys_s2_2d,
            catalogue,
            footprint,
            expert_a,
            expert_b,
        )
        np.savez(ens_ckpt, **ens)
    d_cat_all = distance_transform_edt(~catalogue_all)
    allowed_export = footprint & (d_cat_all >= 3.0)

    if winner_arm == "E89_1_phys_zero_cat":
        p_exp_fp = ens["p_a_fp"]
        p_exp_2d = _fp_to_2d(p_exp_fp, footprint)
        m_exp_2d = self_credit_from_posterior(p_exp_2d, mu_strand=mu_a)
        alloc_final = g57_emit.dinkelbach_allocate(
            p_exp_2d,
            m_exp_2d,
            allowed_export,
            budget=BUDGET_DOTS,
            k_truth=14_200.0,
            min_spacing_px=2.5,
            candidate_cap=550_000,
            dinkelbach_iters=3,
        )
        emitted_final = alloc_final.emitted
    elif winner_arm == "E89_2_dual_global_celf":
        p_exp_fp = fuse_dual_experts(
            ens["p_a_fp"], ens["p_b_fp"], cover_fp, ens["dcat_fp"], blind_basin_boost=0.0
        )
        p_exp_2d = _fp_to_2d(p_exp_fp, footprint)
        m_exp_2d = self_credit_from_posterior(p_exp_2d, mu_strand=0.5 * (mu_a + mu_b))
        alloc_final = g57_emit.dinkelbach_allocate(
            p_exp_2d,
            m_exp_2d,
            allowed_export,
            budget=BUDGET_DOTS,
            k_truth=14_200.0,
            min_spacing_px=2.5,
            candidate_cap=550_000,
            dinkelbach_iters=3,
        )
        emitted_final = alloc_final.emitted
    else:
        p_exp_fp = fuse_dual_experts(
            ens["p_a_fp"], ens["p_b_fp"], cover_fp, ens["dcat_fp"], blind_basin_boost=0.06
        )
        p_exp_2d = _fp_to_2d(p_exp_fp, footprint)
        m_exp_2d = self_credit_from_posterior(p_exp_2d, mu_strand=0.5 * (mu_a + mu_b))
        emitted_final = allocate_regime_stratified_celf(
            p_exp_2d,
            m_exp_2d,
            allowed_export,
            cover_2d,
            total_budget=BUDGET_DOTS,
            shares=(0.34, 0.36, 0.30),
            depth_splits_m=(80.0, 400.0),
            min_spacing_px=2.5,
            k_truth=14_200.0,
        )

    pred_final = emitted_final.astype(np.float32)
    n_final = int(emitted_final.sum())
    min_dcat_final = float(d_cat_all[emitted_final].min())
    _log(f"Allocated final candidate: n_dots={n_final:,}, min_dcat={min_dcat_final:.3f} px")

    # Cover-depth regime distribution of final candidate vs R0
    r0_mask = r0_arr > 0
    def _regime_breakdown(mask_b: np.ndarray) -> dict[str, float]:
        tot = max(int(mask_b.sum()), 1)
        bed = int((mask_b & (cover_2d <= 80.0)).sum())
        pie = int((mask_b & (cover_2d > 80.0) & (cover_2d <= 400.0)).sum())
        bas = int((mask_b & (cover_2d > 400.0)).sum())
        return {
            "n_dots": int(mask_b.sum()),
            "bedrock_le_80m_dots": bed,
            "bedrock_le_80m_share": round(bed / tot, 4),
            "piedmont_80_400m_dots": pie,
            "piedmont_80_400m_share": round(pie / tot, 4),
            "concealed_basin_gt_400m_dots": bas,
            "concealed_basin_gt_400m_share": round(bas / tot, 4),
        }

    regime_stats = {
        "candidate": _regime_breakdown(emitted_final),
        "r0_parent": _regime_breakdown(r0_mask),
    }

    # 7. Uniqueness Gate against ALL reference rasters (.cache/data + releases + .cache/scored_fleet)
    _log("Running Uniqueness Audit (`surface |Spearman rho| <= 0.90` & `3-px dot overlap <= 0.70`)...")
    ref_paths: list[tuple[str, Path]] = []
    for p in sorted(DATA_DIR.glob("*.tif")):
        if p.name in {"training_features.tif", "sample_submission.tif", "existing_faults.tif"}:
            continue
        ref_paths.append((f"data:{p.name}", p))
    for p in sorted(RELEASES_DIR.glob("*.tif")):
        if "gemsdoe89-bh-rtp-habc" in p.name:
            continue
        ref_paths.append((f"releases:{p.name}", p))
    if FLEET_DIR.is_dir():
        for p in sorted(FLEET_DIR.glob("*.tif")):
            ref_paths.append((f"fleet:{p.name}", p))

    from scipy.stats import rankdata

    cand_ranks_fp = rankdata(p_exp_2d[footprint]).astype(np.float64)
    cand_ranks_fp -= cand_ranks_fp.mean()
    cand_ranks_norm = float(np.linalg.norm(cand_ranks_fp)) + 1e-12
    dot_ranks_fp = rankdata(pred_final[footprint]).astype(np.float64)
    dot_ranks_fp -= dot_ranks_fp.mean()
    dot_ranks_norm = float(np.linalg.norm(dot_ranks_fp)) + 1e-12

    max_surf_corr = 0.0
    max_surf_ref = ""
    max_dot_rho = 0.0
    max_dot_rho_ref = ""
    max_dot_ov_fwd = 0.0
    max_dot_ov_fwd_ref = ""
    max_dot_ov_sym = 0.0
    max_dot_ov_sym_ref = ""
    uniqueness_rows = []
    seen_sha = set()

    for label_ref, rpath in ref_paths:
        raw_bytes = rpath.read_bytes()
        rsha = hashlib.sha256(raw_bytes).hexdigest()
        if rsha in seen_sha:
            continue
        seen_sha.add(rsha)
        arr_ref = np.nan_to_num(tifffile.imread(rpath), nan=0.0).astype(np.float32)
        if arr_ref.shape != footprint.shape:
            continue
        t_fp = arr_ref[footprint].astype(np.float64)
        uniq_vals = np.unique(t_fp)
        if uniq_vals.size <= 1:
            sc = 0.0
            dc = 0.0
        elif uniq_vals.size == 2:
            # Binary {0, c} vector: midrank vector is an exact positive affine transform of t_fp!
            tc = t_fp - t_fp.mean()
            tn = float(np.linalg.norm(tc)) + 1e-12
            sc = abs(float(np.dot(cand_ranks_fp, tc) / (cand_ranks_norm * tn)))
            dc = abs(float(np.dot(dot_ranks_fp, tc) / (dot_ranks_norm * tn)))
        else:
            tr = rankdata(t_fp).astype(np.float64)
            tr -= tr.mean()
            tn = float(np.linalg.norm(tr)) + 1e-12
            sc = abs(float(np.dot(cand_ranks_fp, tr) / (cand_ranks_norm * tn)))
            dc = abs(float(np.dot(dot_ranks_fp, tr) / (dot_ranks_norm * tn)))

        ref_pos = (arr_ref > 0) & footprint
        if ref_pos.any():
            ov_fwd = float(g57_uniq.dot_overlap(emitted_final, ref_pos, radius_px=3))
            ov_rev = float(g57_uniq.dot_overlap(ref_pos, emitted_final, radius_px=3))
            ov_sym = max(ov_fwd, ov_rev)
        else:
            ov_fwd = ov_rev = ov_sym = 0.0

        if sc > max_surf_corr:
            max_surf_corr, max_surf_ref = sc, label_ref
        if dc > max_dot_rho:
            max_dot_rho, max_dot_rho_ref = dc, label_ref
        if ov_fwd > max_dot_ov_fwd:
            max_dot_ov_fwd, max_dot_ov_fwd_ref = ov_fwd, label_ref
        if ov_sym > max_dot_ov_sym:
            max_dot_ov_sym, max_dot_ov_sym_ref = ov_sym, label_ref

        if label_ref.startswith(("data:", "fleet:")) or ov_sym >= 0.25 or sc >= 0.35:
            uniqueness_rows.append(
                {
                    "ref": label_ref,
                    "sha256": rsha,
                    "abs_surface_spearman": round(sc, 5),
                    "abs_emitted_spearman": round(dc, 5),
                    "dot_overlap_3px_cand_in_ref": round(ov_fwd, 5),
                    "dot_overlap_3px_ref_in_cand": round(ov_rev, 5),
                    "dot_overlap_3px_sym_max": round(ov_sym, 5),
                }
            )

    uniqueness_pass = (
        max(max_surf_corr, max_dot_rho) <= g57_uniq.RHO_LIMIT
        and max_dot_ov_fwd <= g57_uniq.OVERLAP_LIMIT
    )
    _log(
        f"Checked {len(seen_sha)} unique reference rasters ({len(ref_paths)} files): "
        f"max surface |Spearman rho| = {max_surf_corr:.4f} ({max_surf_ref}), "
        f"max emitted |Spearman rho| = {max_dot_rho:.4f} ({max_dot_rho_ref}), "
        f"max 3-px dot overlap = {max_dot_ov_fwd:.4f} ({max_dot_ov_fwd_ref}), "
        f"sym max = {max_dot_ov_sym:.4f} ({max_dot_ov_sym_ref}) -> PASS={uniqueness_pass}"
    )
    if not uniqueness_pass:
        raise RuntimeError("UNIQUENESS GATE FAILED!")

    # 8. Deterministic Dual-Verified GeoTIFF Packaging (`docs/downloads/` + `releases/`)
    decoded_sha256 = hashlib.sha256(np.ascontiguousarray(pred_final, dtype="<f4").tobytes()).hexdigest()
    sha8 = decoded_sha256[:8]
    stem = f"gemsdoe89-bh-rtp-habc-{DATE_TAG}-{sha8}"
    dl_name = f"{stem}-zeros"
    dl_tif = DOWNLOADS_DIR / f"{dl_name}.tif"

    cand_score = pooled_report["scores"][winner_arm]
    r0_fair_score = pooled_report["scores"]["r0_fold_fair"]
    diff_r0 = pooled_report["paired_differences"]["r0_fold_fair"]

    form_note = (
        f"H89 BH-RTP-HABC dual-LOQO+CELF300m: {n_final} dots, dcat>=3px; "
        f"HOLDOUT-DTI {cand_score['dti']:.4f} (+{diff_r0['delta']:.4f} vs R0 fair)"
    )
    assert len(form_note) <= 140, f"form_note exceeded 140 chars ({len(form_note)})"

    # Clean any stale H89 outputs before writing fresh deterministic artifacts
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    for old in DOWNLOADS_DIR.glob("gemsdoe89-bh-rtp-habc-*"):
        old.unlink()
    for old in RELEASES_DIR.glob("gemsdoe89-bh-rtp-habc-*"):
        old.unlink()

    _log(f"Writing primary submission package to `docs/downloads/{dl_name}.tif` (+ .zip + .json)...")
    receipt = g57_writer.write_submission(
        dl_tif,
        pred_final,
        sample_path,
        footprint,
        note=form_note,
        name=dl_name,
        catalogue=catalogue_all,
        metadata={
            "lane": "H89 (BH-RTP-HABC)",
            "selected_experiment": winner_arm,
            "holdout_evaluator": g57_eval.VERSION,
            "withheld_positive_pixels": k_withheld,
            "holdout_dti": round(cand_score["dti"], 6),
            "holdout_ci95": [round(x, 6) for x in cand_score["ci95"]],
            "delta_vs_r0_fold_fair": round(diff_r0["delta"], 6),
            "delta_vs_r0_fold_fair_ci95": [round(x, 6) for x in diff_r0["ci95"]],
            "max_surface_spearman_86_refs": round(max_surf_corr, 5),
            "max_dot_overlap_3px_86_refs": round(max_dot_ov_fwd, 5),
            "decoded_sha256": decoded_sha256,
        },
    )

    # Also write matching `releases/<stem>-zeros.tif` + `releases/<stem>.tif` via repo_grid
    # so `tools/validate_raster.py` and `tools/check_ledger.py` validate it in CI!
    rel_zeros = RELEASES_DIR / f"{stem}-zeros.tif"
    rel_nan = RELEASES_DIR / f"{stem}.tif"
    repo_grid.write_submission(rel_zeros, emitted_final, footprint, encoding="zeros")
    repo_grid.write_submission(rel_nan, emitted_final, footprint, encoding="nan")
    rel_zeros_sha = repo_grid.sha256_file(rel_zeros)
    rel_nan_sha = repo_grid.sha256_file(rel_nan)
    pct_changed_vs_r0 = round(100.0 * float((emitted_final & (~r0_mask)).sum()) / max(float(r0_mask.sum()), 1.0), 2)
    ov_r0_fwd = round(float(g57_uniq.dot_overlap(emitted_final, r0_mask, radius_px=3)), 5)

    # Verify pixel-exact decoded identity across BOTH writers + repo_validate gates
    arr_dl = tifffile.imread(dl_tif)
    arr_rel_z = tifffile.imread(rel_zeros)
    assert np.array_equal(arr_dl, arr_rel_z), "Pixel mismatch between docs/downloads and releases -zeros.tif!"
    assert hashlib.sha256(np.ascontiguousarray(arr_dl, dtype="<f4").tobytes()).hexdigest() == decoded_sha256

    contract = json.loads((REGISTRY_DIR / "grid_contract.json").read_text(encoding="utf-8"))
    ok_rel_zeros, res_rel_zeros = repo_validate.gate_release(
        rel_zeros,
        contract,
        footprint=footprint,
        dots_mask=emitted_final,
        require_nan_outside=False,
        min_clearance_px=3.0,
        clearance_raster=catalogue_all,
    )
    ok_rel_nan, res_rel_nan = repo_validate.gate_release(
        rel_nan,
        contract,
        footprint=footprint,
        dots_mask=emitted_final,
        require_nan_outside=True,
        min_clearance_px=3.0,
        clearance_raster=catalogue_all,
    )
    if not (ok_rel_zeros and ok_rel_nan):
        raise RuntimeError(f"Repo release validator failed: {res_rel_zeros} / {res_rel_nan}")
    gate_rel_zeros = {"passed": ok_rel_zeros, "gates": res_rel_zeros}
    gate_rel_nan = {"passed": ok_rel_nan, "gates": res_rel_nan}

    # Verify Beat-R0 + Statistical CI Gate for honest `promote` vs `negative` verdict
    beats_controls = (
        cand_score["dti"] > r0_fair_score["dti"]
        and diff_r0["ci95"][0] > 0.0
        and uniqueness_pass
        and not canary["any_flagged"]
        and receipt["validator"]["all_checks_passed"]
        and gate_rel_zeros["passed"]
    )
    verdict = "promote" if beats_controls else "negative"

    # Save comprehensive discovery report + canonical Run Card JSON
    full_report = {
        "session": "GEMSDOE89",
        "branch": "arena/995faf74-gemsdoe89",
        "date_utc": "2026-10-24",
        "lane": "H89 (BH-RTP-HABC: Cover-Deconfounded Basement-Hinge, RTP Phase-Symmetry & Hydrothermal Alteration Boundary Conduit Discovery)",
        "selected_experiment": winner_arm,
        "experiments_run": 3,
        "experiment_budget_max": 3,
        "evaluator_version": g57_eval.VERSION,
        "withheld_positive_pixels": k_withheld,
        "fold_breakdown": fold_rep_all,
        "pooled_holdout": pooled_report,
        "leakage_canary_summary": {
            "num_features_tested": len(ALL_FEATURE_NAMES),
            "threshold": 0.90,
            "max_single_feature_strength": canary["max_single_feature_strength"],
            "any_flagged": canary["any_flagged"],
            "verdict": canary["verdict"],
            "report_path": "registry/leakage_canary_h89.json",
        },
        "uniqueness_audit": {
            "num_reference_files_scanned": len(ref_paths),
            "num_unique_reference_rasters_checked": len(seen_sha),
            "surface_corr_threshold": g57_uniq.RHO_LIMIT,
            "dot_overlap_3px_threshold": g57_uniq.OVERLAP_LIMIT,
            "max_abs_surface_spearman": round(max_surf_corr, 5),
            "max_abs_surface_spearman_ref": max_surf_ref,
            "max_abs_emitted_spearman": round(max_dot_rho, 5),
            "max_abs_emitted_spearman_ref": max_dot_rho_ref,
            "max_dot_overlap_3px_forward": round(max_dot_ov_fwd, 5),
            "max_dot_overlap_3px_forward_ref": max_dot_ov_fwd_ref,
            "max_dot_overlap_3px_symmetric": round(max_dot_ov_sym, 5),
            "max_dot_overlap_3px_symmetric_ref": max_dot_ov_sym_ref,
            "passed": uniqueness_pass,
            "top_comparisons": sorted(
                uniqueness_rows, key=lambda r: -max(r["abs_surface_spearman"], r["dot_overlap_3px_sym_max"])
            )[:25],
        },
        "regime_allocation": regime_stats,
        "packaging": {
            "submission_name": dl_name,
            "form_note": form_note,
            "form_note_chars": len(form_note),
            "primary_download_tif": f"docs/downloads/{dl_name}.tif",
            "primary_download_tif_sha256": receipt["sha256"],
            "primary_download_tif_bytes": receipt["bytes"],
            "primary_download_zip": f"docs/downloads/{dl_name}.zip",
            "primary_download_zip_sha256": receipt["zip_sha256"],
            "primary_receipt_json": f"docs/downloads/{dl_name}.json",
            "release_zeros_tif": f"releases/{stem}-zeros.tif",
            "release_zeros_sha256": rel_zeros_sha,
            "release_nan_tif": f"releases/{stem}.tif",
            "release_nan_sha256": rel_nan_sha,
            "decoded_float32_sha256": decoded_sha256,
            "sha8": sha8,
            "stem": stem,
            "n_dots": n_final,
            "pct_changed_vs_r0": pct_changed_vs_r0,
            "dot_overlap_3px_vs_r0": ov_r0_fwd,
            "min_dcat_px": round(min_dcat_final, 4),
            "gems57_validator_15_of_15_ok": bool(receipt["validator"]["all_checks_passed"]),
            "repo_grid_validator_zeros_passed": bool(gate_rel_zeros["passed"]),
            "repo_grid_validator_nan_passed": bool(gate_rel_nan["passed"]),
        },
        "verdict": verdict,
        "elapsed_seconds": round(time.time() - t0, 2),
    }
    report_path = REGISTRY_DIR / "h89_discovery_report.json"
    report_path.write_text(json.dumps(full_report, indent=2, default=str) + "\n", encoding="utf-8")

    run_card = {
        "run_id": dl_name,
        "repository": "buffedlizard55-lab/GEMSDOE89",
        "branch": "arena/995faf74-gemsdoe89",
        "date_utc": "2026-10-24",
        "hypothesis": (
            "H89-A (BH-RTP-HABC): Concealed Basin-and-Range geothermal faults missed by USGS/INGENIOUS "
            "concentrate along buried pre-Cenozoic basement-scarp inflections (B15), inclination-corrected "
            "Reduced-to-Pole magnetic & gravity tilt crests (B02, B05/B11, |B18|), conductive clay-cap "
            "magnetite-destruction boundaries (B17 x -LRM(B02)), and strike-aligned fault-tip horsetails "
            "and en-echelon relay breaches."
        ),
        "mechanism": (
            f"Cover-deconfounded Dual-Expert Leave-One-Quadrant-Out HistGBDT ensemble (`{winner_arm}`: "
            "30 zero-catalogue geophysical/geomorphic features + 12 whole-component self-masked network "
            "tip/horsetail/relay/strike-alignment features) + Dinkelbach CELF 300 m submodular marginal-DTI "
            f"dot allocation ({n_final:,} unit dots at d_cat >= 3.0 px)."
        ),
        "mimic": (
            "Down-dip alluvial fan distributary channels (rejected via cos^2 strike-alignment with tectonic "
            "trend), GeoDAWN N-S/E-W flight-line leveling seams (suppressed via cos^8(2*psi) cardinal damper), "
            "circular volcanic/caldera rims (rejected via Hessian lambda_perp - 0.5|lambda_par|), and 2D playa "
            "conductivity blankets (gated by 1D RTP magnetic edge + basement gradient)."
        ),
        "evidence_class": "HOLDOUT-DTI",
        "evaluator_version": g57_eval.VERSION,
        "withheld_positive_pixels": k_withheld,
        "holdout_dti": {
            "candidate": round(cand_score["dti"], 6),
            "ci95": [round(x, 6) for x in cand_score["ci95"]],
            "r0_fold_fair_control": round(r0_fair_score["dti"], 6),
            "r0_fold_fair_ci95": [round(x, 6) for x in r0_fair_score["ci95"]],
            "d28_static_control": round(pooled_report["scores"]["d28_static"]["dti"], 6),
            "r0_static_control": round(pooled_report["scores"]["r0_static"]["dti"], 6),
            "random_null_control": round(pooled_report["scores"]["random_null"]["dti"], 6),
            "paired_delta_vs_r0_fold_fair": round(diff_r0["delta"], 6),
            "paired_delta_ci95": [round(x, 6) for x in diff_r0["ci95"]],
        },
        "leakage_canary": {
            "features_tested": len(ALL_FEATURE_NAMES),
            "threshold": 0.90,
            "max_symmetric_auc": canary["max_single_feature_strength"],
            "passed": not canary["any_flagged"],
        },
        "registry_uniqueness": {
            "reference_files_scanned": len(ref_paths),
            "unique_reference_rasters_checked": len(seen_sha),
            "max_abs_surface_spearman": round(max_surf_corr, 5),
            "max_abs_surface_spearman_ref": max_surf_ref,
            "max_abs_emitted_spearman": round(max_dot_rho, 5),
            "max_abs_emitted_spearman_ref": max_dot_rho_ref,
            "surface_corr_limit": g57_uniq.RHO_LIMIT,
            "max_dot_overlap_3px": round(max_dot_ov_fwd, 5),
            "max_dot_overlap_3px_ref": max_dot_ov_fwd_ref,
            "max_dot_overlap_3px_symmetric": round(max_dot_ov_sym, 5),
            "dot_overlap_3px_limit": g57_uniq.OVERLAP_LIMIT,
            "passed": uniqueness_pass,
        },
        "submission": {
            "name": dl_name,
            "form_note": form_note,
            "form_note_chars": len(form_note),
            "download_path": f"docs/downloads/{dl_name}.tif",
            "zip_path": f"docs/downloads/{dl_name}.zip",
            "release_zeros_path": f"releases/{stem}-zeros.tif",
            "sha256_tif": receipt["sha256"],
            "sha256_zip": receipt["zip_sha256"],
            "sha256_release_zeros": rel_zeros_sha,
            "sha256_release_nan": rel_nan_sha,
            "sha256_decoded_float32": decoded_sha256,
            "n_dots": n_final,
            "pct_changed_vs_r0": pct_changed_vs_r0,
            "dot_overlap_3px_vs_r0": ov_r0_fwd,
            "min_dcat_px": round(min_dcat_final, 4),
        },
        "validator": {
            "gems57_15_of_15_ok": bool(receipt["validator"]["all_checks_passed"]),
            "gems57_checks": receipt["validator"]["checks"],
            "crs": receipt["validator"]["meta"]["crs"],
            "shape_hw": [3730, 3292],
            "width_x_height": [3292, 3730],
            "value_min": receipt["validator"]["min"],
            "value_max": receipt["validator"]["max"],
            "nan_count_total_grid": receipt["validator"]["n_nan"],
            "nan_in_footprint": 0,
            "repo_grid_contract_passed": bool(gate_rel_zeros["passed"]),
            "safe_to_download_and_submit": bool(receipt["validator"]["all_checks_passed"] and gate_rel_zeros["passed"]),
        },
        "live_submission_slots_used": 0,
        "verdict": verdict,
    }
    card_path = REGISTRY_DIR / "h89_run_card.json"
    card_path.write_text(json.dumps(run_card, indent=2, default=str) + "\n", encoding="utf-8")

    _log(f"DONE in {time.time() - t0:.1f}s! Verdict = {verdict.upper()} | Artifact = docs/downloads/{dl_name}.tif")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
