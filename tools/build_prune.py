#!/usr/bin/env python3
"""Build PRUNE variants of the verified Parent R0 (h33-h33-2-b2).

Usage:
    python tools/build_prune.py --value c1p0
    python tools/build_prune.py --all

Implements the PRUNE axis:
  - c1p0: 1.0 px collar (swaps in 2,545 dots at 1.0 < d_cat <= 2.0 px from d28,
          drops 2,545 lowest unique-credit dots in R0; count fixed at 37,654)
  - c3p0: 3.0 px collar (prunes 2,171 dots at 2.0 < d_cat <= 3.0 px from R0,
          refills 2,171 dots on h19_5 at d_cat > 3.0 px, sep >= 2.0 px; count 37,654)
  - c4p0: 4.0 px collar (prunes 3,825 dots at 2.0 < d_cat <= 4.0 px from R0,
          refills 3,825 dots on h19_5 at d_cat > 4.0 px, sep >= 2.0 px; count 37,654)

Each run:
  1. verifies all pinned inputs against registry/data_manifest.json,
  2. verifies the parent R0 against ledger-recorded sha256 (c55bafc4...),
  3. builds the variant (deterministic, count strictly preserved, zero catalogue mass),
  4. writes <id>.tif (NaN outside) and <id>-zeros.tif (zeros outside) with exact profile,
  5. re-reads both files from disk and runs MUST gates,
  6. computes report-only instruments (proxy, canary),
  7. records build reports in registry/build_report_prune_<value>.json and
     registry/build_reports_prune.json.
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
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe import grid, parent, proxy, prune, validate  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
PARENT_ZEROS_SHA256 = parent.R0_ZEROS_SHA256
PARENT_NAN_SHA256 = parent.R0_NAN_SHA256
DATE = "20261024"
SEED = 20261024

VARIANTS = {
    "c1p0": {
        "collar_px": 1.0,
        "role": "PROXIMAL_SPLAY_PROBE",
        "predicted_central": -0.004,
        "band": [-0.015, -0.004, 0.008],
        "form_note": "h33-h33-2-b2; PRUNE c1p0: collar >1px, swap in 2545 ring dots, drop 2545 low-gain, n37654; pred -0.004 (-0.015..+0.008)",
        "predicted_text": "-0.004 (MODEL; band -0.015..+0.008). Tests near-fault step-overs / splays vs false-positive mask penalty.",
        "note": "Swap in 2545 dots from d28 with 1.0 < d_cat <= 2.0 px, drop 2545 lowest unique credit dots in R0; tests whether near-fault step-overs and splays carry new-fault truth.",
    },
    "c3p0": {
        "collar_px": 3.0,
        "role": "FULL_KERNEL_CLEARANCE",
        "predicted_central": 0.003,
        "band": [-0.005, 0.003, 0.012],
        "form_note": "h33-h33-2-b2; PRUNE c3p0: collar >3px, prune 2171 ring dots, refill on H19-5, n37654; pred +0.003 (-0.005..+0.012)",
        "predicted_text": "+0.003 (MODEL; band -0.005..+0.012). Full 300 m kernel clearance eliminates boundary truncation.",
        "note": "Remove 2171 dots in R0 with 2.0 < d_cat <= 3.0 px, refill 2171 dots onto h19_5 outside 300 m collar; tests whether full kernel clearance eliminates boundary truncation loss.",
    },
    "c4p0": {
        "collar_px": 4.0,
        "role": "SMEAR_ENVELOPE_PURGE",
        "predicted_central": -0.001,
        "band": [-0.018, -0.001, 0.015],
        "form_note": "h33-h33-2-b2; PRUNE c4p0: collar >4px, prune 3825 ring dots, refill on H19-5, n37654; pred -0.001 (-0.018..+0.015)",
        "predicted_text": "-0.001 (MODEL; band -0.018..+0.015). Wide 400 m collar purges GeoDAWN flight-line interpolation smear.",
        "note": "Remove 3825 dots in R0 with 2.0 < d_cat <= 4.0 px, refill 3825 dots onto h19_5 outside 400 m collar; tests whether wide clearance purges 400 m flight-line interpolation smear.",
    },
}


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"


def load_manifest() -> dict:
    return json.loads((ROOT / "registry" / "data_manifest.json").read_text())


def verify_inputs(manifest: dict, data_root: Path) -> dict:
    report = {}
    for f in manifest["files"]:
        if f.get("unverified"):
            report[f["id"]] = {"present": False, "ok": True, "skipped": True}
            continue
        p = data_root / f["local"]
        if not p.exists():
            report[f["id"]] = {"present": False, "ok": False}
            continue
        sha = grid.sha256_file(p)
        report[f["id"]] = {
            "present": True,
            "ok": sha == f["sha256"],
            "sha256": sha,
            "expected": f["sha256"],
        }
    return report


def ledger_hashes(path: Path) -> set[str]:
    if not path.exists():
        return set()
    out = set()
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            for k in ("sha256", "sha256_zeros"):
                v = (row.get(k) or "").strip()
                if v:
                    out.add(v)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--value", choices=sorted(VARIANTS), default=None)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if not args.all and args.value is None:
        ap.error("Must specify --value or --all")

    manifest = load_manifest()
    data_root = Path(
        os.environ.get(
            manifest.get("data_root_env", "GEMSDOE_DATA"),
            ROOT / manifest.get("data_root_default", "data"),
        )
    )

    ver = verify_inputs(manifest, data_root)
    bad = {k: v for k, v in ver.items() if not v.get("ok")}
    if bad:
        print(f"ERROR: pinned inputs failed verification: {bad}")
        return 2
    print("[ok] all pinned inputs verified")

    paths = {f["id"]: data_root / f["local"] for f in manifest["files"]}

    # Load and verify Parent R0
    r0_arr = grid.read_back(paths["parent_r0_zeros"])[0]
    r0_dots = r0_arr > 0
    r0_sha = grid.sha256_file(paths["parent_r0_zeros"])
    if r0_sha != PARENT_ZEROS_SHA256:
        print(f"STOP: parent R0 sha256 mismatch: {r0_sha} != {PARENT_ZEROS_SHA256}")
        return 2
    print(f"[ok] parent R0 verified ({int(r0_dots.sum())} dots, sha256 {r0_sha[:12]}...)")

    sample, contract = grid.read_template(paths["sample_submission"])
    footprint = np.isfinite(sample)
    del sample

    cat_arr = grid.read_back(paths["existing_faults"])[0]
    catalogue = (np.isfinite(cat_arr) & (cat_arr > 0)) & footprint
    del cat_arr

    h19_arr = grid.read_back(paths["scored_h19_5"])[0]
    h19 = (np.isfinite(h19_arr) & (h19_arr > 0)) & footprint
    del h19_arr

    d28_local = next(f["local"] for f in manifest["files"] if f["id"] == "parent_ancestor_d28")
    d28_arr = grid.read_back(data_root / d28_local)[0]
    d28 = (np.isfinite(d28_arr) & (d28_arr > 0)) & footprint
    del d28_arr

    # Base report-only measurements on parent
    parent_proxy = proxy.hide_and_recover(r0_dots, catalogue)
    parent_surrogate = proxy.surrogate_dti(r0_dots, catalogue)
    print(f"[ok] parent hide-and-recover proxy: {parent_proxy['recall']:.4f} (95% CI +- {parent_proxy['ci95_halfwidth']:.4f})")

    known_ledger_hashes = ledger_hashes(ROOT / "ledger" / "submissions.csv")

    with rasterio.open(paths["sample_submission"]) as src:
        prof = src.profile.copy()
    prof.update(
        driver="GTiff",
        dtype="float32",
        count=1,
        compress="deflate",
        predictor=3,
        zlevel=9,
        tiled=True,
        blockxsize=256,
        blockysize=256,
        nodata=None,
    )
    prof_nan = prof.copy()
    prof_nan["nodata"] = float("nan")

    values = sorted(VARIANTS) if args.all else [args.value]
    reports = []

    for value in values:
        t0 = time.time()
        spec = VARIANTS[value]
        print(f"\n--- Building PRUNE variant: {value} ({spec['role']}) ---")

        variant_dots, stats = prune.build_prune(
            mode=value,
            parent_dots=r0_dots,
            d28_dots=d28,
            h19_5_mask=h19,
            catalogue_mask=catalogue,
            footprint=footprint,
            seed=SEED,
        )

        tmp_nan = ROOT / "releases" / f"_tmp_prune_{value}_nan.tif"
        tmp_zeros = ROOT / "releases" / f"_tmp_prune_{value}_zeros.tif"
        tmp_nan.parent.mkdir(parents=True, exist_ok=True)

        with rasterio.open(tmp_zeros, "w", **prof) as dst:
            dst.write(np.where(footprint, variant_dots.astype(np.float32), 0.0).astype(np.float32), 1)
        with rasterio.open(tmp_nan, "w", **prof_nan) as dst:
            dst.write(np.where(footprint, variant_dots.astype(np.float32), np.nan).astype(np.float32), 1)

        sha_nan = grid.sha256_file(tmp_nan)
        sha_zeros = grid.sha256_file(tmp_zeros)
        sha8 = sha_nan[:8]

        rid = f"{PARENT_ID}-prune-{value}-{DATE}-{sha8}"
        final_nan = ROOT / "releases" / f"{rid}.tif"
        final_zeros = ROOT / "releases" / f"{rid}-zeros.tif"
        tmp_nan.replace(final_nan)
        tmp_zeros.replace(final_zeros)

        # Re-read from disk and validate MUST gates
        nan_arr, _ = grid.read_back(final_nan)
        zeros_arr, _ = grid.read_back(final_zeros)
        read_dots_nan = np.nan_to_num(nan_arr) > 0
        read_dots_zeros = zeros_arr > 0

        ok_nan, res_nan = validate.gate_release(
            final_nan,
            contract,
            footprint=footprint,
            dots_mask=read_dots_nan,
            require_nan_outside=True,
            ledger_hashes=known_ledger_hashes,
            min_clearance_px=0.0,
            clearance_raster=catalogue,
        )
        ok_zeros, res_zeros = validate.gate_release(
            final_zeros,
            contract,
            footprint=footprint,
            dots_mask=read_dots_zeros,
            require_nan_outside=False,
            ledger_hashes=known_ledger_hashes,
            min_clearance_px=0.0,
            clearance_raster=catalogue,
        )

        if not ok_nan:
            print(f"FAILED gates for {final_nan.name}: {res_nan}")
            return 2
        if not ok_zeros:
            print(f"FAILED gates for {final_zeros.name}: {res_zeros}")
            return 2

        print(f"[pass] MUST gates passed for {final_nan.name} and {final_zeros.name}")

        # Report-only instruments
        var_proxy = proxy.hide_and_recover(variant_dots, catalogue)
        var_surrogate = proxy.surrogate_dti(variant_dots, catalogue)

        elapsed = time.time() - t0

        report = {
            "id": rid,
            "parent": PARENT_ID,
            "axis": "PRUNE",
            "value": value,
            "role": spec["role"],
            "date": DATE,
            "git_sha": git_sha(),
            "elapsed_seconds": round(elapsed, 2),
            "spec": spec,
            "form_note": spec["form_note"],
            "files": {
                "sha8": sha8,
                "nan": {
                    "path": f"releases/{final_nan.name}",
                    "sha256": sha_nan,
                    "bytes": final_nan.stat().st_size,
                },
                "zeros": {
                    "path": f"releases/{final_zeros.name}",
                    "sha256": sha_zeros,
                    "bytes": final_zeros.stat().st_size,
                },
            },
            "stats": stats,
            "model_prediction": {
                "central": spec["predicted_central"],
                "band": spec["band"],
                "predicted_change_text": spec["predicted_text"],
                "evidence_class": "MODEL",
            },
            "report_only": {
                "parent_hide_and_recover_recall": parent_proxy["recall"],
                "parent_hide_and_recover_ci95": parent_proxy["ci95"],
                "variant_hide_and_recover_recall": var_proxy["recall"],
                "variant_hide_and_recover_ci95": var_proxy["ci95"],
                "parent_surrogate_dti": parent_surrogate,
                "variant_surrogate_dti": var_surrogate,
                "note": "REPORT-ONLY; local proxy holdout correlates -0.87..+0.54 with live scores and never gates a file",
            },
            "gates": {
                "nan_all_ok": ok_nan,
                "zeros_all_ok": ok_zeros,
                "sha256_in_ledger_before_build": False,
            },
        }

        # Write single report
        single_rep_path = ROOT / "registry" / f"build_report_prune_{value}.json"
        single_rep_path.write_text(json.dumps(report, indent=1) + "\n")
        reports.append(report)
        print(f"[ok] saved {single_rep_path.name}")

    # Write aggregate report if --all
    if args.all or len(reports) == 3:
        all_rep_path = ROOT / "registry" / "build_reports_prune.json"
        all_rep_path.write_text(json.dumps(reports, indent=1) + "\n")
        print(f"[ok] saved aggregate report {all_rep_path.name}")

    print("\nPRUNE build completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
