#!/usr/bin/env python3
"""Build and validate the three matched SPACING variants of verified R0.

Examples:
    python tools/build_spacing.py --all
    python tools/build_spacing.py --value poisson10

Every run verifies all manifest inputs before construction. The code refuses to
build from a modified copy of the tracked source/manifest; the clean git SHA is
recorded in every report. Existing identical rows are reproducibly replaceable,
but a changed raster for an existing (parent, axis, value) triple is rejected.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe import grid, proxy, spacing, validate  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
PARENT_SHA256 = "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
DATE = "20261023"
SEED = 20261023
VARIANTS = {
    "lattice10": {
        "pattern": "lattice",
        "prediction": "+0.001 (MODEL; plausible -0.008..+0.010, not a calibrated interval)",
        "short_prediction": "+0.001",
        "description": "matched 3px lattice around shared gap anchors",
    },
    "poisson10": {
        "pattern": "poisson",
        "prediction": "+0.002 (MODEL; plausible -0.008..+0.012, not a calibrated interval)",
        "short_prediction": "+0.002",
        "description": "best-candidate Poisson-disk gap filling",
    },
    "strike10": {
        "pattern": "strike",
        "prediction": "+0.003 (MODEL; plausible -0.010..+0.016, not a calibrated interval)",
        "short_prediction": "+0.003",
        "description": "matched local-PCA along-strike gap filling",
    },
}


def _git_sha():
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def _source_is_clean():
    tracked = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no", "--",
         "gemsdoe", "tools", "tests", "requirements.txt", "registry/data_manifest.json"],
        cwd=ROOT, text=True,
    )
    return not tracked.strip()


def _verify_inputs(manifest):
    data_root = Path(os.environ.get(manifest.get("data_root_env", "GEMSDOE_DATA"),
                                    ROOT / manifest.get("data_root_default", "data")))
    report = {}
    for item in manifest["files"]:
        path = data_root / item["local"]
        row = {"path": str(path), "expected_sha256": item["sha256"],
               "expected_bytes": item["bytes"], "present": path.exists()}
        if path.exists():
            row["sha256"] = grid.sha256_file(path)
            row["bytes"] = path.stat().st_size
            row["ok"] = row["sha256"] == item["sha256"] and row["bytes"] == item["bytes"]
        else:
            row["ok"] = False
        report[item["id"]] = row
    return data_root, report


def _read_ledger(path):
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader), list(reader.fieldnames or ())


def _write_ledger(path, rows, fieldnames):
    tmp = path.with_suffix(".csv.tmp")
    with open(tmp, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def _hashes(rows):
    out = set()
    for row in rows:
        for key in ("sha256", "sha256_zeros"):
            value = (row.get(key) or "").strip()
            if value:
                out.add(value)
    return out


def _row_for(value, rid, stats, sha_nan, sha_zeros):
    spec = VARIANTS[value]
    note = (
        f"R0 {PARENT_ID} + SPACING {value}: {stats['n_moved']} dots "
        f"({stats['pct_changed']:.1f}%), same 5km blocks, dcat>=3px; "
        f"pred {spec['short_prediction']}"
    )
    if len(note) > 140:
        raise AssertionError(f"form note is {len(note)} characters")
    return {
        "id": rid,
        "site": "GEMSDOE89",
        "name": rid,
        "score": "",
        "evidence_class": "BUILT (unscored)",
        "encoding": "nan+zeros",
        "n_dots": str(stats["n_dots"]),
        "pct_changed": f"{stats['pct_changed']:.2f}",
        "sha8": sha_nan[:8],
        "sha256": sha_nan,
        "sha256_zeros": sha_zeros,
        "parent": PARENT_ID,
        "axis": "SPACING",
        "value": value,
        "status": "BUILT",
        "receipt": "N",
        "receipt_score": "",
        "predicted_change": spec["prediction"],
        "date": "2026-10-23",
        "form_note": note,
        "notes": (
            f"{spec['description']}; shared removal {stats['removed_sha256'][:12]} and "
            f"anchors {stats['anchors_sha256'][:12]}; mean displacement "
            f"{stats['mean_displacement_px']:.2f}px; 5km-block counts fixed; "
            "receipt fields left blank for the human."
        ),
        "source": "GEMSDOE89-SPACING",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--value", choices=sorted(VARIANTS))
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    if not args.all and not args.value:
        parser.error("give --value or --all")
    values = sorted(VARIANTS) if args.all else [args.value]

    git_sha = _git_sha()
    if not _source_is_clean():
        raise SystemExit("Tracked builder/source/manifest changes are uncommitted; commit them so git_sha is exact")
    manifest = json.loads((ROOT / "registry" / "data_manifest.json").read_text())
    data_root, input_report = _verify_inputs(manifest)
    bad = {key: row for key, row in input_report.items() if not row["ok"]}
    if bad:
        print(json.dumps({"ERROR": "pinned inputs failed verification", "detail": bad}, indent=1))
        return 2
    print("[ok] all four pinned inputs match sha256 and byte count")

    paths = {item["id"]: data_root / item["local"] for item in manifest["files"]}
    if grid.sha256_file(paths["parent_r0_zeros"]) != PARENT_SHA256:
        raise SystemExit("R0 hash mismatch: STOP; never approximate the parent")
    parent = grid.read_back(paths["parent_r0_zeros"])[0]
    parent_dots = parent > 0
    if int(parent_dots.sum()) != 37654 or not set(np.unique(parent)).issubset({0.0, 1.0}):
        raise SystemExit("R0 content mismatch: STOP; expected 37,654 unit-mass dots")
    sample, contract = grid.read_template(paths["sample_submission"])
    footprint = np.isfinite(sample)
    del sample
    catalogue = grid.read_back(paths["existing_faults"])[0]
    cat_mask = catalogue > 0
    if (parent_dots & cat_mask).any() or (parent_dots & ~footprint).any():
        raise SystemExit("R0 footprint/catalogue mismatch: STOP")
    print("[ok] exact R0 restored and re-read: c55bafc4..., 37,654 unit dots")

    verification = {
        "date": "2026-10-23",
        "git_sha": git_sha,
        "all_ok": True,
        "files": input_report,
        "parent": {
            "id": PARENT_ID,
            "sha256": PARENT_SHA256,
            "sha256_match": True,
            "n_dots": int(parent_dots.sum()),
            "unit_mass": True,
            "note": "Byte-exact artifact restored from the pinned mirror; no approximate parent or recipe substitution.",
        },
    }
    (ROOT / "registry" / "input_verification_spacing.json").write_text(
        json.dumps(verification, indent=1, sort_keys=True) + "\n"
    )

    import scipy
    import tifffile
    environment = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "tifffile": tifffile.__version__,
    }

    t0 = time.time()
    control = spacing.prepare_control(parent_dots, footprint, cat_mask, fraction=0.10, seed=SEED)
    print(f"[ok] shared control: {len(control['removed_pts'])} removals and matched anchors ({time.time()-t0:.1f}s)")

    # REPORT ONLY: none of these measurements participates in placement or gates.
    parent_proxy = proxy.hide_and_recover(parent_dots, cat_mask)
    parent_surrogate = proxy.surrogate_dti(parent_dots, cat_mask)
    null_dots = proxy.random_null(parent_dots, footprint, cat_mask)
    null_proxy = proxy.hide_and_recover(null_dots, cat_mask)
    null_surrogate = proxy.surrogate_dti(null_dots, cat_mask)
    from scipy import ndimage as ndi
    d_parent = ndi.distance_transform_edt(~parent_dots).astype(np.float32)
    d_remaining = control["distance_to_remaining"].astype(np.float32)
    d_parent[~footprint] = np.nan
    d_remaining[~footprint] = np.nan
    canary = proxy.canary({
        "distance_to_parent_dot": d_parent,
        "distance_to_surviving_dot": d_remaining,
    }, cat_mask)
    del d_parent, d_remaining
    canary_report = {
        "instrument": "REPORT-ONLY single-geometry-feature AUC against catalogue membership",
        "threshold": 0.90,
        "sample_px": 400000,
        "seed": 11,
        "features": canary,
        "verdict": "PASS" if not any(row["flag"] for row in canary.values()) else "INVESTIGATE",
        "note": "No external feature is used by SPACING. The mandated catalogue-distance exclusion is not tested as a predictor because it is label-defined by construction.",
    }
    (ROOT / "registry" / "leakage_canary_spacing.json").write_text(
        json.dumps(canary_report, indent=1) + "\n"
    )
    if canary_report["verdict"] != "PASS":
        print("[warning] leakage canary requires investigation; it remains REPORT ONLY")

    ledger_path = ROOT / "ledger" / "submissions.csv"
    original_rows, fieldnames = _read_ledger(ledger_path)
    working_rows = list(original_rows)
    known_hashes = _hashes(original_rows)
    new_rows = []
    reports = []

    for value in values:
        start = time.time()
        spec = VARIANTS[value]
        variant_dots, stats = spacing.build_from_control(control, spec["pattern"])
        tmp_nan = ROOT / "releases" / "_tmp_spacing_nan.tif"
        tmp_zeros = ROOT / "releases" / "_tmp_spacing_zeros.tif"
        grid.write_submission(tmp_nan, variant_dots, footprint, encoding="nan")
        grid.write_submission(tmp_zeros, variant_dots, footprint, encoding="zeros")
        sha_nan = grid.sha256_file(tmp_nan)
        sha_zeros = grid.sha256_file(tmp_zeros)
        rid = f"{PARENT_ID}-spacing-{value}-{DATE}-{sha_nan[:8]}"
        final_nan = ROOT / "releases" / f"{rid}.tif"
        final_zeros = ROOT / "releases" / f"{rid}-zeros.tif"

        prior = next((row for row in original_rows
                      if row.get("parent") == PARENT_ID
                      and (row.get("axis") or "").upper() == "SPACING"
                      and row.get("value") == value), None)
        if prior and (prior.get("sha256") != sha_nan or prior.get("sha256_zeros") != sha_zeros):
            raise SystemExit(f"{value}: rebuilt hash differs from the ledger; refusing duplicate (parent, axis, value)")
        gate_hashes = set(known_hashes)
        if prior:
            gate_hashes.discard(prior.get("sha256"))
            gate_hashes.discard(prior.get("sha256_zeros"))

        tmp_nan.replace(final_nan)
        tmp_zeros.replace(final_zeros)
        nan_arr = grid.read_back(final_nan)[0]
        zeros_arr = grid.read_back(final_zeros)[0]
        dots_nan = np.nan_to_num(nan_arr) > 0
        dots_zeros = zeros_arr > 0
        ok_nan, gates_nan = validate.gate_release(
            final_nan, contract, footprint=footprint, dots_mask=dots_nan,
            require_nan_outside=True, ledger_hashes=gate_hashes,
            min_clearance_px=0.0, clearance_raster=catalogue,
        )
        ok_zeros, gates_zeros = validate.gate_release(
            final_zeros, contract, footprint=footprint, dots_mask=dots_zeros,
            require_nan_outside=False, ledger_hashes=gate_hashes,
            min_clearance_px=0.0, clearance_raster=catalogue,
        )
        twins_equal = bool(np.array_equal(dots_nan, dots_zeros) and np.array_equal(dots_nan, variant_dots))
        parent_diff_gates = {
            "count_fixed": stats["n_dots"] == 37654,
            "changed_1_to_50_percent": 1.0 <= stats["pct_changed"] <= 50.0,
            "exact_ten_percent_parent_diff": stats["n_moved"] == 3765,
            "added_catalogue_clearance_at_least_3px": stats["added_min_catalogue_clearance_px"] >= 3.0,
            "zero_catalogue_mass": stats["catalogue_mass"] == 0,
            "minimum_dot_separation_at_least_2p8px": stats["added_min_nearest_dot_px"] >= 2.8 - 1e-6,
            "same_5km_block_counts": stats["control_block_counts_preserved"],
            "twins_identical_mask": twins_equal,
        }
        parent_diff_ok = all(parent_diff_gates.values())

        variant_proxy = proxy.hide_and_recover(variant_dots, cat_mask)
        variant_surrogate = proxy.surrogate_dti(variant_dots, cat_mask)
        report = {
            "id": rid,
            "parent": PARENT_ID,
            "parent_sha256": PARENT_SHA256,
            "axis": "SPACING",
            "value": value,
            "pattern": spec["pattern"],
            "git_sha": git_sha,
            "source_clean_at_build": True,
            "seed": SEED,
            "environment": environment,
            "stats": stats,
            "files": {
                "nan": str(final_nan.relative_to(ROOT)),
                "zeros": str(final_zeros.relative_to(ROOT)),
                "sha256": sha_nan,
                "sha256_zeros": sha_zeros,
            },
            "gates": {
                "nan": {"ok": ok_nan, "results": gates_nan},
                "zeros": {"ok": ok_zeros, "results": gates_zeros},
                "parent_diff": {"ok": parent_diff_ok, "results": parent_diff_gates},
            },
            "report_only": {
                "proxy_variant": variant_proxy,
                "proxy_parent": parent_proxy,
                "proxy_random_null": null_proxy,
                "surrogate_dti_variant": variant_surrogate,
                "surrogate_dti_parent": parent_surrogate,
                "surrogate_dti_random_null": null_surrogate,
                "surrogate_dti_delta": variant_surrogate - parent_surrogate,
                "leakage_canary": "registry/leakage_canary_spacing.json",
                "sgmc_control": "NOT RUN: no SGMC raster is pinned in registry/data_manifest.json; report-only and not used in any decision",
                "caveat": "Added dots are >=3 px from catalogue pixels, so catalogue recovery cannot see their credit; the proxy is blind to the placement half of this edit.",
            },
            "predicted_change": spec["prediction"],
            "mechanism_card": "ledger/MECHANISM_CARDS_SPACING.md",
            "seconds": round(time.time() - start, 1),
        }
        (ROOT / "registry" / f"build_report_spacing_{value}.json").write_text(
            json.dumps(report, indent=1) + "\n"
        )
        reports.append(report)

        row = _row_for(value, rid, stats, sha_nan, sha_zeros)
        if not (ok_nan and ok_zeros and parent_diff_ok):
            row["status"] = "GATE-FAIL"
        if prior:
            # Exact reproducibility rebuilds must not erase human receipt fields.
            for key in ("score", "evidence_class", "status", "receipt", "receipt_score", "date"):
                if prior.get(key):
                    row[key] = prior[key]
        row["notes"] += f" code git {git_sha[:12]}."
        new_rows.append(row)
        known_hashes.update((sha_nan, sha_zeros))
        print(f"[{value}] {rid}; gates={ok_nan and ok_zeros and parent_diff_ok}; "
              f"moved={stats['n_moved']}; mean displacement={stats['mean_displacement_px']:.2f}px")

    new_ids = {row["id"] for row in new_rows}
    combined = new_rows + [row for row in working_rows if row.get("id") not in new_ids]
    _write_ledger(ledger_path, combined, fieldnames)
    aggregate = []
    for value in sorted(VARIANTS):
        path = ROOT / "registry" / f"build_report_spacing_{value}.json"
        if path.exists():
            aggregate.append(json.loads(path.read_text()))
    (ROOT / "registry" / "build_reports_spacing.json").write_text(
        json.dumps(aggregate, indent=1) + "\n"
    )
    print(f"[done] wrote {len(new_rows)} SPACING row(s); ledger has {len(combined)} rows")
    return 0 if all(
        rep["gates"]["nan"]["ok"] and rep["gates"]["zeros"]["ok"] and rep["gates"]["parent_diff"]["ok"]
        for rep in reports
    ) else 2


if __name__ == "__main__":
    sys.exit(main())
