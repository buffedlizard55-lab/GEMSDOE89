#!/usr/bin/env python3
"""Evaluate the ANNULUS hypothesis on the spatially blocked holdout.

Lane (single method, parallel-run protocol item 1): splay / stepover /
parallel-strand targeting. Place dots on potential-field ridge peaks (max over
bands 3 `tmi_hg` and 18 `iso_grav_anom_hg` of multi-scale Gaussian gradient
magnitude at sigma 2 and 4 px) restricted to the annulus 2..8 px from the
fold's VISIBLE catalogue faults. Fixed mass = median fold R0 count.

Why this lane: held-out fault segments cluster near visible faults
(-dist-to-visible AUC 0.76-0.88 across folds, below the 0.90 leakage
threshold, so this is signal, not leakage). R0's uniform ridge thinning spreads
mass evenly along the skeleton; conditioning on the visible-fault annulus
concentrates dots where unmapped splays and stepovers of the same fault
systems are geologically expected, staying inside R0's potential-field habitat
(baseline-habitat placement, not off-habitat blind lineaments).

Holdout = hide whole fault segments with a 3 px buffer; catalogue features
derived from visible faults only; visible faults masked pixel-exactly; pooled
DTI (alpha 0.2, beta 0.8, 300 m triangular kernel). Does not access
DrivenData, does not select a slot, does not upload.

Run:
    GEMSDOE_DATA=/path/to/verified/inputs python3 tools/evaluate_annulus.py
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
    dti_from_components, metric_components, paired_delta_bootstrap,
    potential_field_edge, select_spaced_peaks, surface_registry_audit,
    tile_fold_map,
)
from submission_writer import write_candidate, note_length  # noqa: E402

SEED = 20261024
TILE_PX = 512
N_FOLDS = 5
BUFFER_PX = 3.0
CORE_GUARD_PX = 3
MIN_SEP_PX = 2.8
ANNULUS_INNER_PX = 2.0
ANNULUS_OUTER_PX = 8.0
NODATA_F32 = -1.0e30


def read_mask(path: Path, positive=True) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = ds.read(1)
    return np.isfinite(a) & (a > 0 if positive else a >= 0)


def core_slice(tile: dict, guard: int = CORE_GUARD_PX):
    y0, y1, x0, x1 = tile["y0"], tile["y1"], tile["x0"], tile["x1"]
    return (slice(y0 + guard, max(y0 + guard, y1 - guard)),
            slice(x0 + guard, max(x0 + guard, x1 - guard)))


def registry_paths(data_root: Path) -> list[Path]:
    paths = [p for p in (ROOT / "releases").glob("*.tif")]
    for name in ("parent_r0_zeros.tif", "parent_r0_nan.tif", "scored_h19_5.tif",
                 "scored_h27_4_solo.tif", "d28.tif"):
        p = data_root / name
        if p.exists():
            paths.append(p)
    return paths


def ledger_hashes(own_prefix: str) -> set[str]:
    out = set()
    with (ROOT / "ledger" / "submissions.csv").open(newline="") as fh:
        for row in csv.DictReader(fh):
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
        desc = [d or f"band_{i+1}" for i, d in enumerate(ds.descriptions)]
        tmi_hg = ds.read(3).astype(np.float32, copy=False)
        grav_hg = ds.read(18).astype(np.float32, copy=False)
    fields = {"tmi_hg": tmi_hg, "iso_grav_anom_hg": grav_hg}
    valid_all = footprint & np.isfinite(tmi_hg) & np.isfinite(grav_hg) \
        & (tmi_hg > NODATA_F32) & (grav_hg > NODATA_F32)
    edge_score = potential_field_edge(fields, valid_all, scales=(2.0, 4.0))
    del tmi_hg, grav_hg
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

    # Per-fold R0 comparator: d28 thinned skeleton pruned >2.0 px from visible faults.
    baseline_by_fold = {}
    base_counts = []
    for item in holdouts:
        visible = item["visible"]
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
          f"{n_withheld} withheld positive pixels; fixed candidate mass={n_points}")

    candidate_by_fold = {}
    for item in holdouts:
        visible = item["visible"]
        dist_vis = ndi.distance_transform_edt(~visible)
        annulus = (dist_vis >= ANNULUS_INNER_PX) & (dist_vis <= ANNULUS_OUTER_PX)
        eligible = candidate_valid & ~visible & annulus
        candidate_by_fold[item["fold"]] = select_spaced_peaks(
            edge_score, eligible, n_points, min_sep_px=MIN_SEP_PX)
        del dist_vis, annulus

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
          f"95% tile-bootstrap CI): ANNULUS={candidate_dti:.6f} "
          f"[{candidate_ci['lower_95']:.6f}, {candidate_ci['upper_95']:.6f}], "
          f"R0-visible={baseline_dti:.6f} "
          f"[{baseline_ci['lower_95']:.6f}, {baseline_ci['upper_95']:.6f}], "
          f"paired delta={candidate_dti - baseline_dti:+.6f} "
          f"[{delta_ci['lower_95']:+.6f}, {delta_ci['upper_95']:+.6f}]")

    # Leakage canary: raw feature gradients and the composite edge surface alone.
    canary = {}
    with rasterio.open(paths["training_features"]) as ds:
        for band in (3, 18):
            feat = ds.read(band).astype(np.float32, copy=False)
            v = footprint & np.isfinite(feat) & (feat > NODATA_F32)
            med = np.float32(np.median(feat[v]))
            filled = np.where(v, feat, med)
            for sigma in (2.0, 4.0):
                g = ndi.gaussian_gradient_magnitude(filled, sigma=sigma, mode="nearest")
                key = f"band_{band:02d}_{desc[band-1]}_g{int(sigma)}"
                canary[key] = auc_strength(
                    np.where(v, g, np.nan), truth_domain, eval_domain, seed=SEED + band + int(sigma))
                del g
    canary["pf_edge_tmi3_grav18_max_s2s4"] = auc_strength(
        edge_score, truth_domain, eval_domain, seed=SEED + 100)
    canary_flags = [k for k, v in canary.items() if v["flag_leakage"]]
    print(f"[CANARY] {len(canary)} single-feature holdout tests; "
          f"max strength={max((v['strength'] or 0) for v in canary.values()):.4f}; "
          f"flags={canary_flags}")

    # Final (submission-time) raster: annulus from the FULL catalogue, catalogue
    # pixels masked pixel-exactly (no invented proximity collar).
    dist_cat = ndi.distance_transform_edt(~catalogue)
    annulus_cat = (dist_cat >= ANNULUS_INNER_PX) & (dist_cat <= ANNULUS_OUTER_PX)
    final_eligible = candidate_valid & ~catalogue & annulus_cat
    proposed = select_spaced_peaks(edge_score, final_eligible, n_points,
                                   min_sep_px=MIN_SEP_PX)

    refs = registry_paths(data_root)
    audit_pre = surface_registry_audit(edge_score, footprint, proposed, refs,
                                       seed=SEED, sample_n=150000,
                                       surface_label="pre-placement potential-field annulus surface")
    known_hashes = ledger_hashes("h89-annulus-splay-20261024-")
    print(f"[UNIQUENESS pre-write] max |surface rho|="
          f"{audit_pre['max_abs_surface_spearman']:.4f}; max dots within 3px="
          f"{audit_pre['max_dot_overlap_3px']:.3%}; refs="
          f"{audit_pre['n_reference_geometries']} geometries")

    verdict = "promote" if (
        candidate_dti > baseline_dti and delta_ci["lower_95"] > 0.0 and
        not canary_flags and not audit_pre["duplicate_stop"]
    ) else "negative"

    temp_path = ROOT / "releases" / "_tmp_annulus_candidate.tif"
    note = ("ANNULUS: PF ridge peaks 200-800m from visible faults; splay/stepover targeting; "
            "exact known-fault mask; spatial holdout candidate")
    note_length(note)
    validator = None
    raster_sha = None
    final_path = None
    audit_post = None
    grid_match = None
    if audit_pre["duplicate_stop"]:
        verdict = "negative"
        print("STOP: duplicate threshold crossed before writing; no TIF emitted")
    else:
        written_dots, validator = write_candidate(
            temp_path, proposed, footprint, catalogue, ledger_hashes=known_hashes)
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
            final_path = ROOT / "releases" / f"h89-annulus-splay-20261024-{sha8}-candidate.tif"
            temp_path.replace(final_path)
            print(f"[PASS] unique candidate TIF written: {final_path.relative_to(ROOT)}")

    if final_path is not None:
        with rasterio.open(paths["sample_submission"]) as src, rasterio.open(final_path) as out:
            grid_match = bool(out.crs == src.crs and out.shape == src.shape and
                              out.transform == src.transform and out.count == 1 and
                              out.dtypes[0] == "float32")
        validator["crs_shape_transform_dtype_match_template"] = grid_match
        if not grid_match:
            verdict = "negative"

    canary_simple = {k: {"auc": v["auc"], "strength": v["strength"],
                         "flag_leakage": v["flag_leakage"]} for k, v in canary.items()}
    card = {
        "schema_version": 1,
        "experiment": "ANNULUS",
        "hypothesis": ("Unmapped geothermal-relevant fault strands (splays, stepovers, parallel "
                       "strands) cluster within 200-800 m of mapped catalogue faults and carry the "
                       "same potential-field ridge signature; conditioning ridge-peak placement on "
                       "the visible-fault annulus recovers more held-out fault length than R0's "
                       "uniform ridge thinning."),
        "mechanism": ("Band 3 tmi_hg + band 18 iso_grav_anom_hg; max multi-scale Gaussian gradient "
                      "magnitude (sigma 2, 4 px); select fixed-mass spaced peaks in the 2-8 px "
                      "annulus around visible catalogue faults per fold; final dots 2-8 px from the "
                      "full catalogue, catalogue pixels masked pixel-exactly; mass = median fold R0 "
                      "count (37,654-dot class); 2.8 px disk NMS."),
        "non_fault_mimic": ("Lithologic contacts, intrusive contacts, dike swarms, basin-fill edges "
                            "and cultural magnetic noise can produce potential-field gradients near "
                            "mapped faults without a fault; the annulus gate alone cannot distinguish "
                            "them, which is why the holdout (held-out segments) is the gate."),
        "holdout_protocol": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": EVALUATOR_VERSION,
            "spatial_tiles": len(tiles),
            "tile_size_px": TILE_PX,
            "folds": N_FOLDS,
            "withheld_positive_pixels": n_withheld,
            "unique_withheld_components_in_scored_cores": n_scored_components,
            "buffer_px": BUFFER_PX,
            "tile_interior_guard_px": CORE_GUARD_PX,
            "kernel_radius_px": 3.0,
            "alpha": 0.2,
            "beta": 0.8,
            "pooled_dti_definition": ("exact DTI sufficient statistics summed over disjoint, "
                                      "boundary-guarded spatial tile interiors; spatial-tile "
                                      "percentile bootstrap CI"),
            "candidate": {"evidence_class": "HOLDOUT-DTI", "value": candidate_dti,
                          "n_withheld_positive_pixels": n_withheld, "ci95": candidate_ci},
            "visible_only_R0_baseline": {"evidence_class": "HOLDOUT-DTI", "value": baseline_dti,
                                         "n_withheld_positive_pixels": n_withheld, "ci95": baseline_ci},
            "paired_delta_candidate_minus_R0": {"evidence_class": "HOLDOUT-DTI",
                                                  "value": candidate_dti - baseline_dti,
                                                  "ci95": delta_ci},
        },
        "leakage_canary": {"threshold_strength": 0.90, "features_tested": canary_simple,
                           "flagged_features": canary_flags,
                           "verdict": "FAIL" if canary_flags else "PASS"},
        "registry_uniqueness": {"prewrite": audit_pre, "postwrite": audit_post,
                                "exact_sha256_against_ledger": {
                                    "checked_ledger_hash_values": len(known_hashes),
                                    "candidate_sha256": raster_sha,
                                    "unique": bool(raster_sha is None or raster_sha not in known_hashes)},
                                "duplicate_thresholds": {"abs_spearman_gt": 0.90,
                                                         "dot_overlap_within_3px_gt": 0.70}},
        "raster": {"path": str(final_path.relative_to(ROOT)) if final_path else None,
                   "sha256": raster_sha, "validator": validator},
        "submission": {"name": final_path.stem if final_path else None,
                       "note": note, "note_chars": len(note),
                       "slot_status": "not selected; selector step is separate",
                       "download_submit_status": ("OK_TO_SUBMIT" if verdict == "promote" else "DO_NOT_SUBMIT")},
        "verdict": verdict,
        "experiment_budget": {"experiments_run": 1, "maximum": 3},
        "official_sources": [
            "https://www.usgs.gov/publications/discovering-blind-geothermal-systems-great-basin-region-integrated-geologic-and",
            "https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and",
            "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/",
            "https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516",
        ],
    }
    out_json = ROOT / "registry" / "run_card_annulus_20261024.json"
    out_json.write_text(json.dumps(card, indent=2, sort_keys=True) + "\n")
    print(f"[RUN CARD] {out_json.relative_to(ROOT)} verdict={verdict}")
    return 0 if (final_path is not None and validator and validator["passed"] and grid_match) else 4


if __name__ == "__main__":
    raise SystemExit(main())
