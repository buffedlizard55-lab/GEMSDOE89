#!/usr/bin/env python3
"""Build the MASS arms of session GEMSDOE89 from the verified R0 parent.

Usage:
    python tools/build_mass.py --all
    python tools/build_mass.py --value m10uniq

Each run
  1. verifies every pinned input that this axis reads against
     registry/data_manifest.json (sha256 recomputed from disk),
  2. re-derives R0's dot set from two pinned ancestors (solo-d2.8 and d2.8,
     each minus every dot within 2.0 px of the catalogue) and requires it to be
     cell-identical to the parent raster,
  3. builds each arm (drop-only; no new dot is created anywhere),
  4. writes <id>.tif (NaN outside footprint) and <id>-zeros.tif,
  5. re-reads both from disk and runs every MUST gate,
  6. appends one ledger row per arm and writes registry/build_mass_<value>.json.

The sha8 in a file name is the first 8 hex of the NaN twin's sha256, so the
name is checkable against the file with no external table.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe import grid, mass, proxy, validate  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
PARENT_SHA256 = "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
DATE = "20261023"
SEED = 20261023

# value -> (fraction dropped, selection mode, description, slot role)
VARIANTS = {
    "m10uniq": dict(fraction=0.10, mode="unique",
                    note="drop the 10% of dots with the smallest unique kernel credit",
                    role="PRIMARY"),
    "m10rand": dict(fraction=0.10, mode="random",
                    note="drop 10% of dots uniformly at random (count-matched null for m10uniq)",
                    role="CONTROL"),
    "m20uniq": dict(fraction=0.20, mode="unique",
                    note="drop the 20% of dots with the smallest unique kernel credit",
                    role="DOSE"),
}


def load_manifest():
    return json.loads((ROOT / "registry" / "data_manifest.json").read_text())


def data_root(manifest):
    return Path(os.environ.get(manifest.get("data_root_env", "GEMSDOE_DATA"),
                               ROOT / manifest.get("data_root_default", "data")))


def verify_inputs(manifest, required):
    root = data_root(manifest)
    report, bad = {}, []
    for f in manifest["files"]:
        path = root / f["local"]
        entry = {"required": f["id"] in required, "path": str(path)}
        if not path.exists():
            entry.update(present=False, ok=False)
            if f["id"] in required:
                bad.append(f["id"])
        else:
            sha = grid.sha256_file(path)
            entry.update(present=True, ok=(sha == f["sha256"]), sha256=sha,
                         expected=f["sha256"])
            if entry["ok"] is False and f["id"] in required:
                bad.append(f["id"])
        report[f["id"]] = entry
    return report, bad


def ledger_hashes():
    path = ROOT / "ledger" / "submissions.csv"
    out = set()
    if not path.exists():
        return out
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
        ap.error("give --value or --all")

    manifest = load_manifest()
    required = set(manifest["session_gate"]["required_ids"])
    ver, bad = verify_inputs(manifest, required)
    if bad:
        print(json.dumps({"ERROR": "pinned inputs failed verification", "detail": bad}, indent=1))
        sys.exit(2)
    print(f"[ok] pinned inputs verified: {len([v for v in ver.values() if v['present'] and v['ok']])} "
          f"of {len(ver)} present and hash-clean (required: {sorted(required)})")

    root = data_root(manifest)
    paths = {f["id"]: root / f["local"] for f in manifest["files"]}

    sample, contract = grid.read_template(paths["sample_submission"])
    footprint = np.isfinite(sample)
    del sample
    catalogue = grid.read_back(paths["existing_faults"])[0]
    cat_mask = catalogue > 0
    parent = grid.read_back(paths["parent_r0_zeros"])[0]
    parent_dots = parent > 0
    assert grid.sha256_file(paths["parent_r0_zeros"]) == PARENT_SHA256, "parent sha mismatch"
    print(f"[ok] parent R0 sha256 {PARENT_SHA256[:12]}  dots={int(parent_dots.sum())}")

    # ---- parent identity: re-derive the dot set from two pinned ancestors ----
    d_cat = ndi.distance_transform_edt(~cat_mask)
    rebuild = {}
    for anc, path in (("solo_d28", paths["parent_ancestor_solo_d28"]),
                      ("d28", paths["parent_ancestor_d28"])):
        m = grid.read_back(path)[0] > 0
        derived = m & (d_cat > 2.0)
        rebuild[anc] = {
            "ancestor_dots": int(m.sum()),
            "derived_dots": int(derived.sum()),
            "differing_cells_vs_parent": int((derived ^ parent_dots).sum()),
            "identical": bool(np.array_equal(derived, parent_dots)),
        }
    if not all(v["identical"] for v in rebuild.values()):
        print(json.dumps({"ERROR": "R0 not reproduced from pinned ancestors", "detail": rebuild}, indent=1))
        sys.exit(3)
    h195 = grid.read_back(paths["parent_field_h19_5"])[0]
    ranking_audit = {
        "h19_5_unique_values": [float(v) for v in np.unique(h195)],
        "h19_5_set_cells": int((h195 > 0).sum()),
        "conclusion": "the ancestor field is binary, so no stored ranking exists for this lineage",
    }
    del h195
    print(f"[ok] R0 reproduced exactly from both ancestors: {rebuild}")

    hashes = ledger_hashes()
    parent_proxy = proxy.hide_and_recover(parent_dots, cat_mask)
    parent_surrogate = proxy.surrogate_dti(parent_dots, cat_mask)
    null_dots = proxy.random_null(parent_dots, footprint, cat_mask)
    null_proxy = proxy.hide_and_recover(null_dots, cat_mask)
    null_surrogate = proxy.surrogate_dti(null_dots, cat_mask)
    print(f"[report-only] parent proxy recall {parent_proxy['recall']:.4f}, "
          f"random null {null_proxy['recall']:.4f}")

    values = sorted(VARIANTS) if args.all else [args.value]
    reports = []
    for value in values:
        spec = VARIANTS[value]
        t0 = time.time()
        rng = np.random.default_rng(SEED)
        n_drop = int(round(spec["fraction"] * int(parent_dots.sum())))
        variant, stats = mass.build(
            dots=parent_dots, footprint=footprint, catalogue_mask=cat_mask,
            n_drop=n_drop, rng=rng, mode=spec["mode"],
        )
        pred = mass.predicted_delta(stats)

        tmp_nan = ROOT / "releases" / "_tmp_nan.tif"
        tmp_zeros = ROOT / "releases" / "_tmp_zeros.tif"
        tmp_nan.parent.mkdir(parents=True, exist_ok=True)
        grid.write_submission(tmp_nan, variant, footprint, encoding="nan")
        grid.write_submission(tmp_zeros, variant, footprint, encoding="zeros")
        sha_nan = grid.sha256_file(tmp_nan)
        sha_zeros = grid.sha256_file(tmp_zeros)
        sha8 = sha_nan[:8]
        rid = f"{PARENT_ID}-MASS{value}-{DATE}-{sha8}"
        final_nan = ROOT / "releases" / f"{rid}.tif"
        final_zeros = ROOT / "releases" / f"{rid}-zeros.tif"
        tmp_nan.replace(final_nan)
        tmp_zeros.replace(final_zeros)

        # ---- gates on the files as re-read from disk ----
        nan_arr = grid.read_back(final_nan)[0]
        zeros_arr = grid.read_back(final_zeros)[0]
        dots_nan = np.nan_to_num(nan_arr) > 0
        dots_zeros = zeros_arr > 0
        ok_nan, res_nan = validate.gate_release(
            final_nan, contract, footprint=footprint, dots_mask=dots_nan,
            require_nan_outside=True, ledger_hashes=hashes,
            min_clearance_px=0.0, clearance_raster=catalogue)
        ok_zeros, res_zeros = validate.gate_release(
            final_zeros, contract, footprint=footprint, dots_mask=dots_zeros,
            require_nan_outside=False, ledger_hashes=hashes,
            clearance_raster=catalogue)
        twins = bool(np.array_equal(dots_nan, dots_zeros)) and bool(np.array_equal(variant, dots_nan))
        parent_diff = {
            "added_vs_parent": int((variant & ~parent_dots).sum()),
            "removed_vs_parent": int((parent_dots & ~variant).sum()),
            "symmetric_difference": int((variant ^ parent_dots).sum()),
            "identical": bool(np.array_equal(variant, parent_dots)),
        }
        v_proxy = proxy.hide_and_recover(variant, cat_mask)
        v_surrogate = proxy.surrogate_dti(variant, cat_mask)

        central = pred["central"]
        rep = {
            "id": rid,
            "value": value,
            "axis": "MASS",
            "role": spec["role"],
            "spec": spec,
            "parent": PARENT_ID,
            "parent_sha256": PARENT_SHA256,
            "seed": SEED,
            "parent_rebuild": rebuild,
            "ranking_audit": ranking_audit,
            "stats": stats,
            "predicted_delta_model": pred,
            "files": {"nan": str(final_nan.relative_to(ROOT)),
                      "zeros": str(final_zeros.relative_to(ROOT)),
                      "sha256": sha_nan, "sha256_zeros": sha_zeros, "sha8": sha8},
            "gates": {"nan": {"ok": ok_nan, "results": res_nan},
                      "zeros": {"ok": ok_zeros, "results": res_zeros},
                      "twins_identical": twins},
            "parent_diff": parent_diff,
            "report_only": {
                "proxy_variant": v_proxy, "proxy_parent": parent_proxy,
                "proxy_random_null": null_proxy,
                "surrogate_dti_variant": v_surrogate,
                "surrogate_dti_parent": parent_surrogate,
                "surrogate_dti_random_null": null_surrogate,
            },
            "seconds": round(time.time() - t0, 1),
        }
        (ROOT / "registry" / f"build_mass_{value}.json").write_text(json.dumps(rep, indent=1) + "\n")
        reports.append(rep)
        ok = ok_nan and ok_zeros and twins
        print(f"[{value}] {rid} gates nan={ok_nan} zeros={ok_zeros} twins={twins} "
              f"dropped={stats['n_dropped']} u_lost_frac={stats['unique_credit_lost_frac']:.4f} "
              f"pred={central:+.4f} ({rep['seconds']}s)")
        if not ok:
            for r in res_nan + res_zeros:
                if not r["ok"]:
                    print("   FAILED GATE:", r)

    (ROOT / "registry" / "build_mass_reports.json").write_text(json.dumps(reports, indent=1) + "\n")
    print("[done]")


if __name__ == "__main__":
    main()
