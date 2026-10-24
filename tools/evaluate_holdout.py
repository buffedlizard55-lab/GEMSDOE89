#!/usr/bin/env python3
"""Evaluate the single COND-EDGE hypothesis on a spatially blocked holdout.

Run from repository root after ``python tools/fetch_pinned_data.py``:
    .venv/bin/python tools/evaluate_holdout.py

This runs exactly one candidate experiment. It does not access DrivenData,
select a weekly slot, upload a file, or treat MODEL/PROXY output as a score.
The evaluator withholds whole connected fault components touching test tiles,
excludes a 3-pixel buffer around those components from the fold's visible
catalogue, masks visible fault pixels exactly, and computes one pooled DTI from
non-overlapping tile interiors. No catalogue-derived input to the selected
COND-EDGE surface is used; the R0 comparator's distance transform is rebuilt
from visible faults only.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe import grid  # noqa: E402
from gemsdoe.holdout import (  # noqa: E402
    EVALUATOR_VERSION, auc_strength, bootstrap_dti, component_holdouts,
    conductivity_edge, dti_from_components, metric_components,
    paired_delta_bootstrap, select_spaced_peaks, surface_registry_audit,
    tile_fold_map,
)
from submission_writer import write_candidate, note_length  # noqa: E402

SEED = 20261024
TILE_PX = 512
N_FOLDS = 5
BUFFER_PX = 3.0
CORE_GUARD_PX = 3
MIN_SEP_PX = 2.8
NODATA_F32 = -1.0e30


def read_mask(path: Path, positive=True) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = ds.read(1)
    return np.isfinite(a) & (a > 0 if positive else a >= 0)


def core_slice(tile: dict, guard: int = CORE_GUARD_PX):
    y0, y1, x0, x1 = tile["y0"], tile["y1"], tile["x0"], tile["x1"]
    # The 3-pixel interior guard makes radius-3 interactions local to one tile.
    return (slice(y0 + guard, max(y0 + guard, y1 - guard)),
            slice(x0 + guard, max(x0 + guard, x1 - guard)))


def registry_paths(data_root: Path) -> list[Path]:
    # Re-running this deterministic experiment must not compare its earlier
    # output with itself and falsely trip the duplicate guard.
    paths = [p for p in (ROOT / "releases").glob("*.tif")
             if not (p.name.startswith("h89-condedge-s2-4-20261024-") and
                     p.name.endswith("-candidate.tif"))]
    for name in ("parent_r0_zeros.tif", "parent_r0_nan.tif", "scored_h19_5.tif",
                 "scored_h27_4_solo.tif", "d28.tif"):
        p = data_root / name
        if p.exists():
            paths.append(p)
    return paths


def ledger_hashes() -> set[str]:
    out = set()
    own_prefix = "h89-condedge-s2-4-20261024-"
    with (ROOT / "ledger" / "submissions.csv").open(newline="") as fh:
        for row in csv.DictReader(fh):
            # A deterministic rerun may recreate this experiment's own ledger row.
            # Exclude only that row; all other GEMSDOE89/upstream hashes remain gated.
            if (row.get("id") or "").startswith(own_prefix):
                continue
            for field in ("sha256", "sha256_zeros", "sha8"):
                value = (row.get(field) or "").strip()
                if value:
                    out.add(value)
    return out


def load_manifest_paths(data_root: Path) -> dict[str, Path]:
    manifest = json.loads((ROOT / "registry" / "data_manifest.json").read_text())
    return {x["id"]: data_root / x["local"] for x in manifest["files"]}


def main() -> int:
    data_root = Path(os.environ.get("GEMSDOE_DATA", ROOT / "data"))
    paths = load_manifest_paths(data_root)
    required = ("training_features", "sample_submission", "existing_faults",
                "parent_ancestor_d28")
    missing = [name for name in required if not paths[name].exists()]
    if missing:
        print(f"STOP: pinned data missing: {missing}; run tools/fetch_pinned_data.py")
        return 2

    for entry in json.loads((ROOT / "registry" / "data_manifest.json").read_text())["files"]:
        if entry.get("unverified"):
            continue
        p = data_root / entry["local"]
        if not p.exists():
            print(f"STOP: missing pinned input: {entry['id']}")
            return 2
        got = grid.sha256_file(p)
        if got != entry["sha256"]:
            print(f"STOP: manifest checksum mismatch for {entry['id']}: {got}")
            return 2
    print("[PASS] all fetchable pinned inputs SHA-256 verified")

    with rasterio.open(paths["sample_submission"]) as ds:
        template = ds.read(1)

    footprint = np.isfinite(template)
    with rasterio.open(paths["existing_faults"]) as ds:
        catalogue = (ds.read(1) > 0) & footprint
    d28 = read_mask(paths["parent_ancestor_d28"])
    with rasterio.open(paths["training_features"]) as ds:
        if ds.count != 19 or ds.shape != footprint.shape:
            print(f"STOP: feature stack contract mismatch: bands={ds.count}, shape={ds.shape}")
            return 2
        cond = ds.read(17).astype(np.float32, copy=False)
    cond_valid = footprint & np.isfinite(cond) & (cond > NODATA_F32)
    edge_score = conductivity_edge(cond, cond_valid)
    del cond
    candidate_valid = footprint & np.isfinite(edge_score)

    fold_map, tiles = tile_fold_map(footprint.shape, tile_px=TILE_PX, n_folds=N_FOLDS)
    comp_labels, n_components, holdouts = component_holdouts(
        catalogue, fold_map, tiles, n_folds=N_FOLDS, buffer_px=BUFFER_PX)
    eval_domain = np.zeros(footprint.shape, dtype=bool)
    for tile in tiles:
        sy, sx = core_slice(tile)
        eval_domain[sy, sx] = True
    truth_domain = catalogue & eval_domain
    n_withheld = int(truth_domain.sum())
    scored_component_ids = np.unique(comp_labels[truth_domain])
    n_scored_components = int(np.count_nonzero(scored_component_ids))
    if n_withheld == 0:
        print("STOP: spatial holdout contains no withheld positives")
        return 3

    # Per-fold, recipe-faithful R0 comparator: reuse the pinned geophysical d28
    # field and derive distance-to-catalogue only from the fold's visible faults.
    baseline_by_fold = {}
    base_counts = []
    hidden_component_count = 0
    for item in holdouts:
        hidden = item["hidden"]
        visible = item["visible"]
        hidden_component_count += len(item["hidden_component_ids"])
        dist_vis = ndi.distance_transform_edt(~visible)
        base = d28 & footprint & (dist_vis > 2.0) & ~visible
        baseline_by_fold[item["fold"]] = base
        base_counts.append(int(base.sum()))
        del dist_vis
    n_points = int(np.median(np.asarray(base_counts, dtype=np.int64)))
    if n_points <= 0:
        print("STOP: visible-fault R0 comparator is empty")
        return 3
    print(f"[HOLDOUT] {len(tiles)} spatial tiles; {N_FOLDS} folds; "
          f"{n_withheld} withheld positive pixels; candidate mass={n_points}")

    # Audit the actual surface BEFORE any candidate placement, including folds.
    refs = registry_paths(data_root)
    surface_audit = surface_registry_audit(
        edge_score, footprint, np.zeros_like(footprint), refs,
        seed=SEED, sample_n=150000, surface_label="before any dot placement")
    if surface_audit["duplicate_stop"] or not surface_audit["n_reference_geometries"]:
        stop_card = {"experiment": "COND-EDGE", "verdict": "negative",
                     "reason": "duplicate surface or empty registry; placement stopped",
                     "registry_audit": surface_audit, "raster": None}
        (ROOT / "registry/run_card_condedge_duplicate.json").write_text(
            json.dumps(stop_card, indent=2) + "\n")
        print("STOP: pre-placement surface gate; no candidate dots generated")
        return 4

    candidate_by_fold = {}
    for item in holdouts:
        visible = item["visible"]
        eligible = candidate_valid & ~visible
        candidate_by_fold[item["fold"]] = select_spaced_peaks(
            edge_score, eligible, n_points, min_sep_px=MIN_SEP_PX)

    # Build per-tile score components for exact pooled DTI and spatial bootstrap.
    candidate_rows, baseline_rows = [], []
    candidate_oof = np.zeros(footprint.shape, dtype=bool)
    baseline_oof = np.zeros(footprint.shape, dtype=bool)
    tile_truth_counts = []
    for tile in tiles:
        sy, sx = core_slice(tile)
        item = holdouts[tile["fold"]]
        truth = catalogue[sy, sx]
        pred_c = candidate_by_fold[tile["fold"]][sy, sx]
        pred_b = baseline_by_fold[tile["fold"]][sy, sx]
        candidate_oof[sy, sx] = pred_c
        baseline_oof[sy, sx] = pred_b
        candidate_rows.append(metric_components(truth, pred_c))
        baseline_rows.append(metric_components(truth, pred_b))
        tile_truth_counts.append(int(truth.sum()))

    candidate_dti = dti_from_components(candidate_rows)
    baseline_dti = dti_from_components(baseline_rows)
    _, candidate_ci = bootstrap_dti(candidate_rows, seed=SEED, n_boot=2000)
    _, baseline_ci = bootstrap_dti(baseline_rows, seed=SEED, n_boot=2000)
    delta_ci = paired_delta_bootstrap(candidate_rows, baseline_rows, seed=SEED, n_boot=2000)
    print(f"HOLDOUT-DTI ({EVALUATOR_VERSION}; {n_withheld} withheld positives; "
          f"95% tile-bootstrap CI): candidate={candidate_dti:.6f} "
          f"[{candidate_ci['lower_95']:.6f}, {candidate_ci['upper_95']:.6f}], "
          f"R0-visible={baseline_dti:.6f} "
          f"[{baseline_ci['lower_95']:.6f}, {baseline_ci['upper_95']:.6f}], "
          f"paired delta={candidate_dti-baseline_dti:+.6f} "
          f"[{delta_ci['lower_95']:+.6f}, {delta_ci['upper_95']:+.6f}]")

    # Leakage canary: each raw feature tested alone, plus the selected
    # conductivity-edge transform, against the spatially held-out positives.
    canary = {}
    with rasterio.open(paths["training_features"]) as ds:
        for band in range(1, ds.count + 1):
            feat = ds.read(band).astype(np.float32, copy=False)
            feat[~np.isfinite(feat) | (feat <= NODATA_F32)] = np.nan
            result = auc_strength(feat, truth_domain, eval_domain, seed=SEED + band)
            canary[f"band_{band:02d}_{ds.descriptions[band-1] or 'unnamed'}"] = result
            del feat
    canary["cond_surf_multiscale_edge"] = auc_strength(
        edge_score, truth_domain, eval_domain, seed=SEED + 100)
    canary_flags = [k for k, v in canary.items() if v["flag_leakage"]]
    print(f"[CANARY] {len(canary)} single-feature holdout tests; "
          f"max strength={max((v['strength'] or 0) for v in canary.values()):.4f}; "
          f"flags={canary_flags}")

    # The existing catalogue-derived comparator was constructed only from the
    # fold's visible pixels. Candidate positions at submission time exclude
    # only known pixels (pixel-exact scoring mask), never an invented buffer.
    final_eligible = candidate_valid & ~catalogue
    proposed = select_spaced_peaks(edge_score, final_eligible, n_points,
                                   min_sep_px=MIN_SEP_PX)
    refs = registry_paths(data_root)
    audit_pre = surface_registry_audit(edge_score, footprint, proposed, refs,
                                       seed=SEED, sample_n=150000,
                                       surface_label="pre-placement conductivity-edge surface")
    known_hashes = ledger_hashes()
    print(f"[UNIQUENESS pre-write] max |surface rho|="
          f"{audit_pre['max_abs_surface_spearman']:.4f}; max dots within 3px="
          f"{audit_pre['max_dot_overlap_3px']:.3%}; refs="
          f"{audit_pre['n_reference_geometries']} geometries")

    verdict = "promote" if (
        candidate_dti > baseline_dti and delta_ci["lower_95"] > 0.0 and
        not canary_flags and not audit_pre["duplicate_stop"]
    ) else "negative"

    # The unique candidate is kept even for a negative result, as a research
    # artifact. Documentation explicitly says whether it is appropriate to
    # spend a competition slot; no slot selector or upload is performed here.
    temp_path = ROOT / "releases" / "_tmp_condedge_candidate.tif"
    note = "COND-EDGE: band-17 multiscale conductivity edges; exact known-fault mask; spatial holdout candidate"
    note_length(note)
    validator = None
    raster_sha = None
    final_path = None
    audit_post = None
    if audit_pre["duplicate_stop"]:
        verdict = "negative"
        print("STOP: duplicate threshold crossed before writing; no TIF emitted")
    else:
        written_dots, validator = write_candidate(
            temp_path, proposed, footprint, catalogue, ledger_hashes=known_hashes, encoding="nan")
        raster_sha = validator["sha256"]
        with rasterio.open(temp_path) as ds:
            readback = ds.read(1)
        reread_dots = np.isfinite(readback) & (readback > 0)
        if not np.array_equal(reread_dots, written_dots):
            temp_path.unlink(missing_ok=True)
            raise RuntimeError("disk reread dot mask differs from the proposed mask")
        audit_post = surface_registry_audit(readback, footprint, reread_dots, refs,
                                            seed=SEED, sample_n=150000,
                                            surface_label="disk-reread final prediction raster")
        if audit_post["duplicate_stop"]:
            temp_path.unlink(missing_ok=True)
            verdict = "negative"
            final_path = None
            print("STOP: post-write registry drift threshold crossed; duplicate artifact removed")
        else:
            sha8 = raster_sha[:8]
            final_path = ROOT / "releases" / f"h89-condedge-s2-4-20261024-{sha8}-candidate.tif"
            temp_path.replace(final_path)
            print(f"[PASS] unique candidate TIF written: {final_path.relative_to(ROOT)}")

    # Validate output grid transform/CRS directly from the GeoTIFF, not only
    # from copied tags; compare to the pinned sample template.
    grid_match = None
    if final_path is not None:
        with rasterio.open(paths["sample_submission"]) as src, rasterio.open(final_path) as out:
            grid_match = bool(out.crs == src.crs and out.shape == src.shape and
                              out.transform == src.transform and out.count == 1 and
                              out.dtypes[0] == "float32")
        validator["crs_shape_transform_dtype_match_template"] = grid_match
        if not grid_match:
            verdict = "negative"

    n_tiles = len(tiles)
    card = {
        "schema_version": 1,
        "experiment": "COND-EDGE",
        "hypothesis": "Multi-scale conductivity-surface edges may indicate fluid-altered or lithologic boundaries associated with unmapped fault geometry.",
        "mechanism": "Band 17 cond_surf; max Gaussian gradient magnitude at sigma 2 and 4 pixels; local-maximum selection with 2.8-pixel minimum spacing; fixed candidate mass set by median visible-only R0 fold count.",
        "non_fault_mimic": "Lithologic contacts, basin-fill/saline groundwater boundaries, interpolation seams, and survey or nodata edges can produce conductivity gradients without a fault.",
        "holdout_protocol": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": EVALUATOR_VERSION,
            "spatial_tiles": n_tiles,
            "tile_size_px": TILE_PX,
            "folds": N_FOLDS,
            "withheld_positive_pixels": n_withheld,
            "unique_withheld_components_in_scored_cores": n_scored_components,
            "hidden_component_fold_memberships": int(hidden_component_count),
            "buffer_px": BUFFER_PX,
            "tile_interior_guard_px": CORE_GUARD_PX,
            "kernel_radius_px": 3.0,
            "alpha": 0.2,
            "beta": 0.8,
            "pooled_dti_definition": "exact DTI sufficient statistics summed over disjoint, boundary-guarded spatial tile interiors; spatial-tile percentile bootstrap CI",
            "candidate": {"evidence_class": "HOLDOUT-DTI", "value": candidate_dti,
                          "n_withheld_positive_pixels": n_withheld, "ci95": candidate_ci},
            "visible_only_R0_baseline": {"evidence_class": "HOLDOUT-DTI", "value": baseline_dti,
                                          "n_withheld_positive_pixels": n_withheld, "ci95": baseline_ci},
            "paired_delta_candidate_minus_R0": {"evidence_class": "HOLDOUT-DTI",
                                                  "value": candidate_dti - baseline_dti,
                                                  "ci95": delta_ci},
            "historical_12p8km_holdout_note": "registry/report_only_status.json uses a different 25% connected-strand MODEL protocol and is not directly comparable to this evaluator.",
        },
        "leakage_canary": {"threshold_strength": 0.90, "features_tested": canary,
                            "flagged_features": canary_flags,
                            "verdict": "FAIL" if canary_flags else "PASS"},
        "registry_uniqueness": {"before_placement": surface_audit,
                                "complete_registry_coverage": False,
                                "prewrite": audit_pre, "postwrite": audit_post,
                                "exact_sha256_against_ledger": {
                                    "checked_ledger_hash_values": len(known_hashes),
                                    "candidate_sha256": raster_sha,
                                    "unique": bool(raster_sha is not None and raster_sha not in known_hashes)},
                                "duplicate_thresholds": {"abs_spearman_gt": 0.90,
                                                          "dot_overlap_within_3px_gt": 0.70}},
        "raster": {"path": str(final_path.relative_to(ROOT)) if final_path else None,
                   "sha256": raster_sha, "validator": validator},
        "submission": {"name": final_path.stem if final_path else None,
                       "note": note, "note_chars": len(note),
                       "slot_status": "not selected; selector step is separate",
                       "download_submit_status": ("ELIGIBLE_FOR_SELECTOR" if verdict == "promote" else "DO_NOT_SUBMIT")},
        "verdict": verdict,
        "experiment_budget": {"experiments_run": 1, "maximum": 3},
        "official_sources": [
            "https://www.usgs.gov/publications/discovering-blind-geothermal-systems-great-basin-region-integrated-geologic-and",
            "https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and",
            "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/",
            "https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516",
        ],
    }
    out_json = ROOT / "registry" / "run_card_condedge_20261024.json"
    out_json.write_text(json.dumps(card, indent=2, sort_keys=True) + "\n")
    print(f"[RUN CARD] {out_json.relative_to(ROOT)} verdict={verdict}")
    return 0 if final_path is not None and validator and validator["passed"] and grid_match else 4


if __name__ == "__main__":
    raise SystemExit(main())
