#!/usr/bin/env python3
"""Build one RELIEF variant of the verified R0 parent.

Usage:
    python tools/build_relief.py --value r10 --fraction 0.10 --field det_elev
    python tools/build_relief.py --all

Each run
  1. verifies every pinned input against registry/data_manifest.json,
  2. verifies the parent against the ledger-recorded sha256 (c55bafc4...),
  3. builds the variant (count preserved, collar enforced, seeded),
  4. writes <id>.tif (NaN outside) and <id>-zeros.tif,
  5. re-reads both from disk, runs the MUST gates,
  6. appends the ledger row and writes registry/build_report_<value>.json.

The sha8 in the file name is the first 8 hex of the NaN-twin sha256, so the
name is checkable against the file without any external table.
"""

from __future__ import annotations

import argparse
import os
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe import grid, proxy, relief, validate  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
PARENT_SHA256 = "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
DATE = "20261023"
SEED = 20261023

# variant spec: value -> (fraction, field key, human description)
VARIANTS = {
    "r10": dict(fraction=0.10, field="det_elev",
                note="move 10% of dots from the lowest known-fault-density relief class to the highest"),
    "r15": dict(fraction=0.15, field="det_elev",
                note="move 15% of dots from the lowest known-fault-density relief class to the highest"),
    "r15s": dict(fraction=0.15, field="det_elev_slope",
                 note="same 15% move, but classes defined by detrended-elevation slope"),
}

BAND_1BASED = {"det_elev": 12, "det_elev_slope": 19}  # verified against feature_receipt


def load_manifest():
    p = ROOT / "registry" / "data_manifest.json"
    return json.loads(p.read_text())


def verify_inputs(manifest):
    report = {}
    for f in manifest["files"]:
        if f.get("unverified"):
            report[f["id"]] = {"present": False, "ok": True,
                               "skipped": "unverified report-only pin (IRREGULARITIES item 8)"}
            continue
        data_root = Path(os.environ.get(manifest.get("data_root_env", "GEMSDOE_DATA"), ROOT / manifest.get("data_root_default", "data")))
        path = data_root / f["local"]
        if not path.exists():
            report[f["id"]] = {"present": False, "ok": False}
            continue
        sha = grid.sha256_file(path)
        report[f["id"]] = {
            "present": True,
            "ok": sha == f["sha256"],
            "sha256": sha,
            "expected": f["sha256"],
            "path": str(path.relative_to(ROOT)) if str(path).startswith(str(ROOT)) else str(path),
        }
    return report


def ledger_hashes(path):
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
    ap.add_argument("--fraction", type=float, default=None)
    ap.add_argument("--field", choices=["det_elev", "det_elev_slope"], default=None)
    args = ap.parse_args()
    if not args.all and args.value is None:
        ap.error("give --value or --all")

    manifest = load_manifest()
    ver = verify_inputs(manifest)
    bad = {k: v for k, v in ver.items() if not v.get("ok")}
    if bad:
        print(json.dumps({"ERROR": "pinned inputs failed verification", "detail": bad}, indent=1))
        sys.exit(2)
    print("[ok] all pinned inputs verified")

    import os
    data_root = Path(os.environ.get(manifest.get("data_root_env", "GEMSDOE_DATA"), ROOT / manifest.get("data_root_default", "data")))
    paths = {f["id"]: data_root / f["local"] for f in manifest["files"]}

    parent = grid.read_back(paths["parent_r0_zeros"])[0]
    parent_dots = parent > 0
    assert grid.sha256_file(paths["parent_r0_zeros"]) == PARENT_SHA256, "parent sha mismatch"
    print(f"[ok] parent R0 verified sha256 {PARENT_SHA256[:12]} with {int(parent_dots.sum())} dots")

    sample, contract = grid.read_template(paths["sample_submission"])
    footprint = np.isfinite(sample)
    del sample
    catalogue = grid.read_back(paths["existing_faults"])[0]
    cat_mask = catalogue > 0
    print(f"[ok] footprint {int(footprint.sum())} px, catalogue {int(cat_mask.sum())} px")

    raw = relief.stream_bands(paths["training_features"], [BAND_1BASED["det_elev"],
                                                           BAND_1BASED["det_elev_slope"]])
    fields = {name: raw[b] for name, b in BAND_1BASED.items()}
    del raw
    domain = footprint & np.isfinite(fields["det_elev"]) & np.isfinite(fields["det_elev_slope"])
    print(f"[ok] relief domain {int(domain.sum())} px")

    hashes = ledger_hashes(ROOT / "ledger" / "submissions.csv")

    # report-only instruments on the parent (computed once)
    parent_proxy = proxy.hide_and_recover(parent_dots, cat_mask)
    parent_surrogate = proxy.surrogate_dti(parent_dots, cat_mask)
    null_dots = proxy.random_null(parent_dots, footprint, cat_mask)
    null_proxy = proxy.hide_and_recover(null_dots, cat_mask)
    null_surrogate = proxy.surrogate_dti(null_dots, cat_mask)

    values = sorted(VARIANTS) if args.all else [args.value]
    reports = []
    for value in values:
        spec = dict(VARIANTS[value])
        if args.fraction is not None:
            spec["fraction"] = args.fraction
        if args.field is not None:
            spec["field"] = args.field
        t0 = time.time()
        rng = np.random.default_rng(SEED)
        field = fields[spec["field"]]
        f_det = np.nan_to_num(fields["det_elev"].astype(np.float32), nan=0.0)
        gy, gx = np.gradient(f_det)
        grad_all = np.hypot(gy, gx)
        del f_det
        variant_dots, stats = relief.build(
            field=field, domain=domain, catalogue_mask=cat_mask, footprint=footprint,
            parent_dots=parent_dots, fraction=spec["fraction"], rng=rng,
            gradient=grad_all,
        )
        cls, _ = relief.define_classes(field, domain)
        del field

        # write both twins, hash, rename to the content-addressed id
        tmp_nan = ROOT / "releases" / "_tmp_nan.tif"
        tmp_zeros = ROOT / "releases" / "_tmp_zeros.tif"
        tmp_nan.parent.mkdir(parents=True, exist_ok=True)
        grid.write_submission(tmp_nan, variant_dots, footprint, encoding="nan")
        grid.write_submission(tmp_zeros, variant_dots, footprint, encoding="zeros")
        sha_nan = grid.sha256_file(tmp_nan)
        sha_zeros = grid.sha256_file(tmp_zeros)
        sha8 = sha_nan[:8]
        rid = f"{PARENT_ID}-relief-{value}-{DATE}-{sha8}"
        final_nan = ROOT / "releases" / f"{rid}.tif"
        final_zeros = ROOT / "releases" / f"{rid}-zeros.tif"
        tmp_nan.replace(final_nan)
        tmp_zeros.replace(final_zeros)

        # gates on the re-read files
        nan_arr, nan_contract = grid.read_back(final_nan)
        zeros_arr, _ = grid.read_back(final_zeros)
        dots_read_nan = np.nan_to_num(nan_arr) > 0
        dots_read_zeros = zeros_arr > 0
        ok_nan, res_nan = validate.gate_release(
            final_nan, contract, footprint=footprint, dots_mask=dots_read_nan,
            require_nan_outside=True, ledger_hashes=hashes,
            min_clearance_px=0.0, clearance_raster=catalogue,
        )
        ok_zeros, res_zeros = validate.gate_release(
            final_zeros, contract, footprint=footprint, dots_mask=dots_read_zeros,
            require_nan_outside=False, ledger_hashes=hashes,
            clearance_raster=catalogue,
        )
        # exact equivalence of the twins
        twins_equal = bool(np.array_equal(dots_read_nan, dots_read_zeros)) and \
            bool(np.array_equal(variant_dots, dots_read_nan))

        # report-only instruments
        v_proxy = proxy.hide_and_recover(variant_dots, cat_mask)
        v_surrogate = proxy.surrogate_dti(variant_dots, cat_mask)
        # credit of the placed dots against the catalogue (MODEL input)
        from scipy import ndimage as ndi
        d_cat = ndi.distance_transform_edt(~cat_mask)
        added = variant_dots & ~parent_dots
        removed = parent_dots & ~variant_dots
        from gemsdoe.metric import kernel_weight
        k_add = kernel_weight(d_cat[added])
        k_rem = kernel_weight(np.minimum(d_cat[removed], 3.0))
        f_det = np.nan_to_num(fields["det_elev"].astype(np.float32), nan=0.0)
        gy, gx = np.gradient(f_det)
        grad = np.hypot(gy, gx)
        del f_det
        added_clear = d_cat[added]
        model = {
            "added_min_clearance_px": float(added_clear.min()) if added.any() else None,
            "added_dots": int(added.sum()),
            "removed_dots": int(removed.sum()),
            "added_mean_kernel_to_catalogue": float(k_add.mean()) if added.any() else None,
            "added_frac_within_kernel_of_catalogue": float((k_add > 0).mean()) if added.any() else None,
            "parent_frac_within_kernel_of_catalogue": float((kernel_weight(d_cat[parent_dots]) > 0).mean()),
            "removed_median_nn_px": stats["removed_nn_median_px"],
            "surrogate_dti_delta": v_surrogate - parent_surrogate,
            "added_mean_elev_gradient": float(grad[added].mean()) if added.any() else None,
            "removed_mean_elev_gradient": float(grad[removed].mean()) if removed.any() else None,
            "parent_mean_elev_gradient": float(grad[parent_dots].mean()),
            "pays_threshold_at_parent_dti": 0.2 * 0.2778,
            "inherited_dots_below_3px_of_catalogue": int((d_cat[parent_dots] < 3.0).sum()),
            "parent_min_clearance_px": float(d_cat[parent_dots].min()),
        }

        rep = {
            "id": rid,
            "value": value,
            "spec": spec,
            "parent": PARENT_ID,
            "parent_sha256": PARENT_SHA256,
            "seed": SEED,
            "stats": stats,
            "files": {
                "nan": str(final_nan.relative_to(ROOT)),
                "zeros": str(final_zeros.relative_to(ROOT)),
                "sha256": sha_nan,
                "sha256_zeros": sha_zeros,
                "sha8": sha8,
            },
            "gates": {"nan": {"ok": ok_nan, "results": res_nan},
                      "zeros": {"ok": ok_zeros, "results": res_zeros},
                      "twins_identical_mask": twins_equal},
            "report_only": {
                "proxy_variant": v_proxy,
                "proxy_parent": parent_proxy,
                "proxy_random_null": null_proxy,
                "surrogate_dti_variant": v_surrogate,
                "surrogate_dti_parent": parent_surrogate,
                "surrogate_dti_random_null": null_surrogate,
                "model_inputs": model,
            },
            "seconds": round(time.time() - t0, 1),
        }
        (ROOT / "registry" / f"build_report_{value}.json").write_text(
            json.dumps(rep, indent=1) + "\n")
        reports.append(rep)
        print(f"[{value}] {rid}  gates nan={ok_nan} zeros={ok_zeros} twins={twins_equal}  "
              f"moved={stats['n_moved']}  {rep['seconds']}s")
        if not ok_nan or not ok_zeros:
            for r in res_nan + res_zeros:
                if not r["ok"]:
                    print("   FAILED GATE:", r)

        # ledger row (receipt fields left for the human)
        row = {
            "id": rid,
            "site": "GEMSDOE89",
            "parent": PARENT_ID,
            "axis": "RELIEF",
            "value": value,
            "n_dots": stats["n_dots"],
            "pct_changed": f"{stats['pct_changed']:.2f}",
            "sha256": sha_nan,
            "sha256_zeros": sha_zeros,
            "status": "BUILT" if (ok_nan and ok_zeros and twins_equal) else "GATE-FAIL",
            "predicted_change": rep.get("predicted_change", ""),
            "receipt_score": "",
            "receipt_date": "",
            "form_note": "",
        }
        reports[-1]["ledger_row"] = row

    (ROOT / "registry" / "build_reports.json").write_text(json.dumps(reports, indent=1) + "\n")
    print("[done]")


if __name__ == "__main__":
    main()
