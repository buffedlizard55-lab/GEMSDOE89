#!/usr/bin/env python3
"""Build the nested 2 km CONCENTRATION arms from byte-verified Parent R0.

Usage: ``python tools/build_concentration.py --all``.  The start gate runs
``tools/rebuild_r0.py`` (all fetchable manifest hashes plus exact zeros/NaN
parent SHA-256).  Every addition is an unused H19-5 pixel at d_cat >= 3 px;
source/target blocks use only known-catalogue density.  Exact sequential DTI
marginals rank destinations under H19 surrogate truth.  Live projections are
uncalibrated MODEL sensitivities, never scores.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe import concentration, grid, parent, proxy, relief, validate  # noqa: E402

DATE = "20261023"
SEED = 20261023
BLOCK_PX = 20
SOURCE_QUANTILE = 0.50
TARGET_QUANTILE = 2.0 / 3.0  # top one-third, printed as t33
EXPECTED_DOTS = 37_654
VARIANTS = {
    "2km-b50-t33-m3765": {"n_move": 3765, "role": "PRIMARY"},
    "2km-b50-t33-m5648": {"n_move": 5648, "role": "CONDITIONAL DOSE"},
    "2km-b50-t33-m7531": {"n_move": 7531, "role": "HOLD / HIGH DOSE"},
}


def git_sha():
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def ledger_state(path):
    hashes, triples = set(), set()
    if path.exists():
        with open(path, newline="") as fh:
            for row in csv.DictReader(fh):
                for key in ("sha256", "sha256_zeros"):
                    value = (row.get(key) or "").strip()
                    if value:
                        hashes.add(value)
                triples.add((
                    (row.get("parent") or "").strip(),
                    (row.get("axis") or "").strip().upper(),
                    (row.get("value") or "").strip(),
                ))
    return hashes, triples


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--all", action="store_true", required=True)
    args = ap.parse_args()
    del args

    ledger_path = ROOT / "ledger" / "submissions.csv"
    hashes, triples = ledger_state(ledger_path)
    requested = [v for v in VARIANTS if (parent.PARENT_ID, "CONCENTRATION", v) not in triples]
    if not requested:
        print("[done] all three (parent, axis, value) experiments already exist")
        return 0
    if len(requested) != len(VARIANTS):
        raise RuntimeError(f"partial concentration family already in ledger: {requested}")

    # Fail closed before candidate construction if any pin or parent byte differs.
    subprocess.run([sys.executable, str(ROOT / "tools" / "rebuild_r0.py")], cwd=ROOT, check=True)
    manifest = json.loads((ROOT / "registry" / "data_manifest.json").read_text())
    data_root = Path(os.environ.get(
        manifest.get("data_root_env", "GEMSDOE_DATA"),
        ROOT / manifest.get("data_root_default", "data"),
    ))
    paths = {f["id"]: data_root / f["local"] for f in manifest["files"]}

    sample, contract = grid.read_template(paths["sample_submission"])
    footprint = np.isfinite(sample)
    del sample
    catalogue_raw = grid.read_back(paths["existing_faults"])[0]
    cat = (np.isfinite(catalogue_raw) & (catalogue_raw > 0)) & footprint
    r0 = (grid.read_back(paths["parent_r0_zeros"])[0] > 0) & footprint
    h19 = (grid.read_back(paths["scored_h19_5"])[0] > 0) & footprint
    if int(r0.sum()) != EXPECTED_DOTS:
        raise RuntimeError("parent dot count mismatch after exact rebuild")
    print(f"[ok] loaded exact R0 ({EXPECTED_DOTS} dots) and pinned H19-5/catalogue")

    # REPORT-ONLY canary.  A >0.90 single feature is the brief's explicit stop.
    feature_entry = next(f for f in manifest["files"] if f["id"] == "training_features")
    band_tags = feature_entry["verified_band_tags"]
    all_bands = relief.stream_bands(paths["training_features"], list(range(1, 20)))
    canary_features = {
        f"b{b:02d}_{band_tags[str(b)]}": all_bands[b] for b in range(1, 20)
    }
    canary_features["scored_h19_5"] = np.where(footprint, h19, np.nan).astype(np.float32)
    canary = proxy.canary(canary_features, cat, threshold=0.90)
    del all_bands, canary_features
    strengths = [max(v["auc"], 1.0 - v["auc"]) for v in canary.values() if v["auc"] is not None]
    canary_doc = {
        "instrument": "single-feature AUC vs known catalogue; 19 pinned bands + H19-5",
        "evidence_class": "PROXY / leakage diagnostic",
        "threshold": 0.90,
        "sample_px": 400000,
        "seed": 11,
        "max_single_feature_strength": max(strengths),
        "features": canary,
        "verdict": "STOP AND INVESTIGATE" if any(v["flag"] for v in canary.values()) else "PASS",
        "note": "Block prior is target-derived from the catalogue and is not an independent leakage feature.",
    }
    (ROOT / "registry" / "build_concentration_canary.json").write_text(
        json.dumps(canary_doc, indent=1) + "\n"
    )
    if any(v["flag"] for v in canary.values()):
        print("STOP: leakage canary exceeded 0.90")
        return 2
    print(f"[report-only] leakage canary PASS; max strength={max(strengths):.6f}")

    t0 = time.time()
    variants, audit = concentration.build_family(
        r0, h19, footprint, cat,
        n_moves=[spec["n_move"] for spec in VARIANTS.values()],
        block_px=BLOCK_PX, seed=SEED,
        source_quantile=SOURCE_QUANTILE, target_quantile=TARGET_QUANTILE,
    )
    print(f"[ok] built nested masks in {time.time() - t0:.1f}s; "
          f"source dots={audit['block_stats']['source_parent_dots']}, "
          f"target candidates={audit['block_stats']['target_candidate_pixels']}")

    parent_proxy = proxy.hide_and_recover(r0, cat)
    parent_catalogue_dti = proxy.surrogate_dti(r0, cat)
    build_git = git_sha()
    code_pins = {
        "build_script_sha256": grid.sha256_file(Path(__file__)),
        "concentration_module_sha256": grid.sha256_file(ROOT / "gemsdoe" / "concentration.py"),
    }
    new_rows, reports = [], []
    for value, spec in VARIANTS.items():
        t_variant = time.time()
        mask, stats = variants[spec["n_move"]]
        prediction = concentration.predicted_delta(
            spec["n_move"], stats["h19_surrogate_delta"]
        )
        tmp_nan = ROOT / "releases" / f"_tmp_concentration_{value}_nan.tif"
        tmp_zeros = ROOT / "releases" / f"_tmp_concentration_{value}_zeros.tif"
        grid.write_submission(tmp_nan, mask, footprint, encoding="nan")
        grid.write_submission(tmp_zeros, mask, footprint, encoding="zeros")
        sha_nan = grid.sha256_file(tmp_nan)
        sha_zeros = grid.sha256_file(tmp_zeros)
        rid = f"{parent.PARENT_ID}-conc{value}-{DATE}-{sha_nan[:8]}"
        final_nan = ROOT / "releases" / f"{rid}.tif"
        final_zeros = ROOT / "releases" / f"{rid}-zeros.tif"
        tmp_nan.replace(final_nan)
        tmp_zeros.replace(final_zeros)

        nan_arr, _ = grid.read_back(final_nan)
        zeros_arr, _ = grid.read_back(final_zeros)
        dots_nan = np.nan_to_num(nan_arr) > 0
        dots_zeros = zeros_arr > 0
        ok_nan, gates_nan = validate.gate_release(
            final_nan, contract, footprint=footprint, dots_mask=dots_nan,
            require_nan_outside=True, ledger_hashes=hashes,
            clearance_raster=catalogue_raw,
        )
        ok_zeros, gates_zeros = validate.gate_release(
            final_zeros, contract, footprint=footprint, dots_mask=dots_zeros,
            require_nan_outside=False, ledger_hashes=hashes,
            clearance_raster=catalogue_raw,
        )
        twins = bool(np.array_equal(dots_nan, dots_zeros) and np.array_equal(mask, dots_nan))
        all_passed = bool(ok_nan and ok_zeros and twins and all(stats["mask_gates"].values()))
        if not all_passed:
            print(json.dumps({
                "ERROR": "release gate failure", "id": rid,
                "nan": gates_nan, "zeros": gates_zeros, "twins": twins,
                "mask": stats["mask_gates"],
            }, indent=1))
            return 3
        hashes.update((sha_nan, sha_zeros))

        variant_proxy = proxy.hide_and_recover(mask, cat)
        variant_catalogue_dti = proxy.surrogate_dti(mask, cat)
        note = (
            f"R0 {parent.PARENT_ID}; CONC 2km b50->t33 move {spec['n_move']} "
            f"({stats['pct_changed']:.1f}%), H19 greedy, n={EXPECTED_DOTS}; "
            f"MODEL {prediction['central']:+.3f}"
        )
        if len(note) > 140:
            raise AssertionError("form note exceeds 140 characters")
        report = {
            "id": rid,
            "axis": "CONCENTRATION",
            "value": value,
            "role": spec["role"],
            "parent": parent.PARENT_ID,
            "parent_sha256": parent.R0_ZEROS_SHA256,
            "parent_rebuild": "tools/rebuild_r0.py exited 0; both parent GeoTIFF SHA-256 pins matched",
            "git_sha": build_git,
            "code_pins": code_pins,
            "seed": SEED,
            "spec": {
                "block_km": 2.0,
                "source": "bottom-half catalogue-prior blocks, ties retained (cut 0)",
                "target": "top-one-third catalogue-prior blocks with unused H19 candidates (cut >=5/1000 px)",
                "n_move": spec["n_move"],
                "destination_rule": "lazy exact sequential greedy DTI marginal on off-catalogue H19-5; no spacing gate",
                "catalogue_clearance_added_px": 3.0,
            },
            "block_prior": audit["block_stats"],
            "stats": stats,
            "model_prediction": {
                **prediction,
                "basis": "H19 surrogate counterindicator + block-prior effective-credit sensitivity (-0.050/+0.025/+0.100 per moved dot) / upstream anchor D=18734.44; uncalibrated, not a confidence interval",
                "no_evidence_threshold_live": 0.01,
            },
            "files": {
                "nan": {"path": str(final_nan.relative_to(ROOT)), "sha256": sha_nan, "bytes": final_nan.stat().st_size},
                "zeros": {"path": str(final_zeros.relative_to(ROOT)), "sha256": sha_zeros, "bytes": final_zeros.stat().st_size},
                "sha8": sha_nan[:8],
            },
            "gates": {
                "all_passed": True,
                "mask": stats["mask_gates"],
                "nan": {"ok": ok_nan, "results": gates_nan},
                "zeros": {"ok": ok_zeros, "results": gates_zeros},
                "twins_identical_mask": twins,
                "re_read_from_disk": True,
            },
            "report_only": {
                "catalogue_hide_and_recover_parent": parent_proxy,
                "catalogue_hide_and_recover_variant": variant_proxy,
                "catalogue_surrogate_dti_parent": parent_catalogue_dti,
                "catalogue_surrogate_dti_variant": variant_catalogue_dti,
                "leakage_canary": "registry/build_concentration_canary.json; PASS",
                "sgmc_control": "NOT RUN: manifest pin UNVERIFIED (IRREGULARITIES item 8); report-only and never a gate",
            },
            "form_note": note,
            "seconds": round(time.time() - t_variant, 2),
        }
        reports.append(report)
        new_rows.append({
            "id": rid, "site": "GEMSDOE89", "name": rid, "score": "",
            "evidence_class": "BUILT (unscored)", "encoding": "nan+zeros",
            "n_dots": str(EXPECTED_DOTS), "pct_changed": f"{stats['pct_changed']:.2f}",
            "sha8": sha_nan[:8], "sha256": sha_nan, "sha256_zeros": sha_zeros,
            "parent": parent.PARENT_ID, "axis": "CONCENTRATION", "value": value,
            "status": "BUILT", "receipt": "N", "receipt_score": "",
            "predicted_change": (
                f"MODEL central {prediction['central']:+.4f}; sensitivity "
                f"{prediction['lo']:+.4f}..{prediction['hi']:+.4f} (not a CI)"
            ),
            "date": DATE, "form_note": note,
            "notes": (
                f"{spec['role']}; 2km CV {stats['cv_2km_before']:.4f}->{stats['cv_2km_after']:.4f}; "
                f"5km CV {stats['cv_5km_before']:.4f}->{stats['cv_5km_after']:.4f}; "
                f"H19 counterindicator {stats['h19_surrogate_delta']:+.6f}; "
                f"added min dcat {stats['added_min_catalogue_clearance_px']:.2f}px"
            ),
            "source": "GEMSDOE89",
        })
        print(
            f"[{value}] {rid} gates=PASS moved={spec['n_move']} "
            f"CV2={stats['cv_2km_before']:.4f}->{stats['cv_2km_after']:.4f} "
            f"H19={stats['h19_surrogate_delta']:+.6f} "
            f"MODEL={prediction['lo']:+.4f}/{prediction['central']:+.4f}/{prediction['hi']:+.4f}"
        )

    with open(ledger_path, newline="") as fh:
        fieldnames = csv.DictReader(fh).fieldnames
    with open(ledger_path, "a", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writerows(new_rows)
    for report in reports:
        (ROOT / "registry" / f"build_report_concentration_{report['value']}.json").write_text(
            json.dumps(report, indent=1) + "\n"
        )
    (ROOT / "registry" / "build_reports_concentration.json").write_text(
        json.dumps(reports, indent=1) + "\n"
    )
    print(f"[done] wrote {len(reports)} variants ({2 * len(reports)} rasters) and appended ledger rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
