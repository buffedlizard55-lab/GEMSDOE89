#!/usr/bin/env python3
"""Build the SPACING variants of the verified R0 parent.

    python tools/build_spacing.py --all
    python tools/build_spacing.py --value hd3p0

Each run
  1. verifies every pinned input it needs against registry/data_manifest.json
     (sha256), and the parent against the ledger-recorded sha256 (c55bafc4...),
  2. builds the variant at exactly the parent's dot count, seeded,
  3. writes <id>.tif (NaN outside) and <id>-zeros.tif,
  4. re-reads both from disk and runs the MUST gates,
  5. records the parent-diff statistics, the coverage model and the REPORT-ONLY
     instruments in registry/build_report_spacing_<value>.json,
  6. appends one row per variant to ledger/submissions.csv.

The SHA8 in the file name is the first 8 hex of the NaN-twin sha256, so the
name can be checked against the file without an external table.

Inputs actually needed by this axis: parent, template, catalogue.  The 419 MB
feature stack is NOT touched (no elevation band is used), which is stated in
the build report so nobody assumes it was verified silently.
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
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe import grid, proxy, spacing, validate  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
PARENT_SHA256 = "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
PARENT_DTI_CLAIM = 0.2778            # ledger CLAIM, not a receipt
DATE = "20261023"
SEED = 20261023

# value -> construction.  One selection rule (hard-disk MIS ordered by nearest
# neighbour distance); the arms differ in the hard-disk radius (dose) or in the
# destination geometry (trend-following).
VARIANTS = {
    "hd3p0": dict(mode="poisson", target_sep=3.0, window=3, corridor=2, dose="mild"),
    "hd4p0": dict(mode="poisson", target_sep=4.0, window=4, corridor=2, dose="strong"),
    "hd3p0-along": dict(mode="along", target_sep=3.0, window=3, corridor=2, dose="mild"),
}

REQUIRED_INPUTS = ("parent_r0_zeros", "sample_submission", "existing_faults")


def data_root():
    return Path(os.environ.get("GEMSDOE_DATA", ROOT / "data"))


def load_manifest():
    return json.loads((ROOT / "registry" / "data_manifest.json").read_text())


def verify_inputs(manifest, required=REQUIRED_INPUTS):
    report = {}
    for f in manifest["files"]:
        path = data_root() / f["local"]
        ok = path.exists() and grid.sha256_file(path) == f["sha256"]
        report[f["id"]] = {
            "required_by_this_axis": f["id"] in required,
            "present": path.exists(),
            "sha256_ok": bool(ok),
            "sha256": grid.sha256_file(path) if path.exists() else None,
            "expected": f["sha256"],
        }
    missing = [k for k in required if not report.get(k, {}).get("sha256_ok")]
    return report, missing


def ledger_hashes(path):
    out = set()
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            for k in ("sha256", "sha256_zeros"):
                v = (row.get(k) or "").strip()
                if v:
                    out.add(v)
    return out


def append_ledger_row(row):
    path = ROOT / "ledger" / "submissions.csv"
    with open(path, newline="") as fh:
        fields = next(csv.reader(fh))
    with open(path, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\r\n")
        w.writerow({k: row.get(k, "") for k in fields})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--value", choices=sorted(VARIANTS), default=None)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if not args.all and args.value is None:
        ap.error("give --value or --all")

    manifest = load_manifest()
    report, missing = verify_inputs(manifest)
    if missing:
        print(json.dumps({"ERROR": "pinned inputs failed verification", "missing": missing}, indent=1))
        return 2
    print("[ok] pinned inputs verified:", ", ".join(REQUIRED_INPUTS))

    paths = {f["id"]: data_root() / f["local"] for f in manifest["files"]}
    parent = grid.read_back(paths["parent_r0_zeros"])[0]
    parent_dots = parent > 0
    assert grid.sha256_file(paths["parent_r0_zeros"]) == PARENT_SHA256, "parent sha mismatch"
    print(f"[ok] parent R0 sha256 {PARENT_SHA256[:12]} with {int(parent_dots.sum())} dots")

    sample, contract = grid.read_template(paths["sample_submission"])
    footprint = np.isfinite(sample)
    del sample
    catalogue = grid.read_back(paths["existing_faults"])[0]
    cat_mask = catalogue > 0
    clearance = ndi.distance_transform_edt(~cat_mask).astype(np.float32)
    print(f"[ok] footprint {int(footprint.sum())} px, catalogue {int(cat_mask.sum())} px")

    strike, coherence = spacing.strike_orientation(parent_dots)
    pts_parent = spacing.dot_points(parent_dots)
    in_fp = strike[parent_dots]
    print(f"[ok] parent local strike coherence: median {np.median(coherence[parent_dots]):.3f}")

    hashes = ledger_hashes(ROOT / "ledger" / "submissions.csv")
    cov_parent = spacing.coverage_area(parent_dots)
    nn_parent = spacing.nn_distance(pts_parent)
    proxy_parent = proxy.hide_and_recover(parent_dots, cat_mask)
    surrogate_parent = proxy.surrogate_dti(parent_dots, cat_mask)

    # REPORT-ONLY leakage canary on the only two features this axis looks at
    canary = proxy.canary(
        {"parent_dot_indicator": parent_dots.astype(np.float32),
         "distance_to_nearest_dot": ndi.distance_transform_edt(~parent_dots).astype(np.float32)},
        cat_mask,
    )

    values = sorted(VARIANTS) if args.all else [args.value]
    mis_cache = {}
    out = []
    for value in values:
        spec = VARIANTS[value]
        t0 = time.time()
        rng = np.random.default_rng(SEED)
        variant_dots, stats = spacing.relocate(
            parent_dots=parent_dots, footprint=footprint, clearance_px=clearance,
            target_sep=spec["target_sep"], mode=spec["mode"], rng=rng,
            window=spec["window"], corridor=spec["corridor"], strike=strike,
        )

        cov_variant = spacing.coverage_area(variant_dots)
        pred = spacing.predict_dti_change(PARENT_DTI_CLAIM, cov_parent, cov_variant)

        removed = parent_dots & ~variant_dots
        added = variant_dots & ~parent_dots
        moved_clearance = clearance[added]
        removed_pts = np.argwhere(removed)
        if len(removed_pts):
            # nearest other dot for each dot that was taken out of the parent
            nn_at_removed = cKDTree(pts_parent).query(removed_pts, k=2)[0][:, 1]
        else:
            nn_at_removed = np.zeros(0)
        stats.update({
            "n_removed": int(removed.sum()),
            "n_added": int(added.sum()),
            "added_min_clearance_px": float(moved_clearance.min()) if added.any() else None,
            "added_median_clearance_px": float(np.median(moved_clearance)) if added.any() else None,
            "removed_mean_nn_px": float(nn_at_removed.mean()) if len(nn_at_removed) else None,
            "removed_frac_at_parent_hard_disk": float(
                np.isclose(nn_at_removed, spacing.MIN_SEP_PARENT_PX, atol=1e-6).mean()
            ) if len(nn_at_removed) else None,
            "coverage_before": cov_parent,
            "coverage_after": cov_variant,
            "median_coherence_at_moved_dots": float(np.median(coherence[removed]))
            if removed.any() else None,
        })

        tmp_nan = ROOT / "releases" / "_tmp_spacing_nan.tif"
        tmp_zeros = ROOT / "releases" / "_tmp_spacing_zeros.tif"
        tmp_nan.parent.mkdir(parents=True, exist_ok=True)
        grid.write_submission(tmp_nan, variant_dots, footprint, encoding="nan")
        grid.write_submission(tmp_zeros, variant_dots, footprint, encoding="zeros")
        sha_nan = grid.sha256_file(tmp_nan)
        sha_zeros = grid.sha256_file(tmp_zeros)
        sha8 = sha_nan[:8]
        rid = f"{PARENT_ID}-spacing-{value}-{DATE}-{sha8}"
        final_nan = ROOT / "releases" / f"{rid}.tif"
        final_zeros = ROOT / "releases" / f"{rid}-zeros.tif"
        tmp_nan.replace(final_nan)
        tmp_zeros.replace(final_zeros)

        nan_arr, _ = grid.read_back(final_nan)
        zeros_arr, _ = grid.read_back(final_zeros)
        dots_nan = np.nan_to_num(nan_arr) > 0
        dots_zeros = zeros_arr > 0
        ok_nan, res_nan = validate.gate_release(
            final_nan, contract, footprint=footprint, dots_mask=dots_nan,
            require_nan_outside=True, ledger_hashes=hashes,
            min_clearance_px=0.0, clearance_raster=catalogue)
        ok_zeros, res_zeros = validate.gate_release(
            final_zeros, contract, footprint=footprint, dots_mask=dots_zeros,
            require_nan_outside=False, ledger_hashes=hashes,
            min_clearance_px=0.0, clearance_raster=catalogue)
        twins_equal = bool(np.array_equal(dots_nan, dots_zeros)) and \
            bool(np.array_equal(variant_dots, dots_nan))

        # extra MUST gate specific to this axis: every NEW position clears the
        # catalogue by the hard-constraint radius (inherited dots are the
        # parent's own ring, see IRREGULARITIES item 2).
        new_clearance_ok = bool(added.sum() == 0 or moved_clearance.min() >= spacing.CATALOGUE_CLEARANCE_PX)
        # invariant: the relaxation may never create a pair tighter than the
        # parent's own hard disk (2.828 px), which is what makes this a single
        # "spacing" edit rather than a re-clustering.
        disk_ok = bool(stats["nn_min_after_px"] >= spacing.MIN_SEP_PARENT_PX - 1e-9)
        # brief sec.5: every non-SNAP arm must change 1-50 % of the parent's dots
        frac_ok = bool(1.0 <= stats["pct_changed"] <= 50.0)

        proxy_variant = proxy.hide_and_recover(variant_dots, cat_mask)
        surrogate_variant = proxy.surrogate_dti(variant_dots, cat_mask)

        rep = {
            "id": rid,
            "value": value,
            "axis": "SPACING",
            "spec": spec,
            "parent": PARENT_ID,
            "parent_sha256": PARENT_SHA256,
            "seed": SEED,
            "inputs": report,
            "feature_stack_used": False,
            "stats": stats,
            "model": pred,
            "files": {"nan": str(final_nan.relative_to(ROOT)),
                      "zeros": str(final_zeros.relative_to(ROOT)),
                      "sha256": sha_nan, "sha256_zeros": sha_zeros, "sha8": sha8},
            "gates": {
                "nan": {"ok": ok_nan, "results": res_nan},
                "zeros": {"ok": ok_zeros, "results": res_zeros},
                "twins_identical_mask": twins_equal,
                "new_positions_catalogue_clearance": {
                    "ok": new_clearance_ok,
                    "detail": f"min clearance of new dots = {stats['added_min_clearance_px']} px "
                              f"(required >= {spacing.CATALOGUE_CLEARANCE_PX})"},
                "pct_changed_within_1_50": {
                    "ok": frac_ok,
                    "detail": f"{stats['pct_changed']:.2f} % of the parent's dots changed"},
                "no_pair_tighter_than_parent_disk": {
                    "ok": disk_ok,
                    "detail": f"min nearest-neighbour distance after = {stats['nn_min_after_px']:.3f} px "
                              f"(required >= {spacing.MIN_SEP_PARENT_PX:.3f})"},
            },
            "report_only": {
                "proxy_variant": proxy_variant,
                "proxy_parent": proxy_parent,
                "surrogate_dti_variant": surrogate_variant,
                "surrogate_dti_parent": surrogate_parent,
                "leakage_canary": canary,
                "sgmc_control": "not available: no SGMC layer is pinned in registry/data_manifest.json",
            },
            "seconds": round(time.time() - t0, 1),
        }
        gates_ok = ok_nan and ok_zeros and twins_equal and new_clearance_ok and disk_ok and frac_ok

        note = (f"{PARENT_ID}; SPACING {value}: {stats['n_moved']} dots relocated "
                f"({stats['pct_changed']:.1f}%), sep {spec['target_sep']} px, "
                f"mean {stats['mean_displacement_px']:.1f} px; pred {pred['point']:+.3f}")
        assert len(note) <= 140, f"form note too long: {len(note)}"

        row = {
            "id": rid,
            "site": "GEMSDOE89",
            "name": rid,
            "score": "",
            "evidence_class": "BUILT (unscored)",
            "encoding": "nan+zeros",
            "n_dots": stats["n_dots"],
            "pct_changed": f"{stats['pct_changed']:.2f}",
            "sha8": sha8,
            "sha256": sha_nan,
            "sha256_zeros": sha_zeros,
            "parent": PARENT_ID,
            "axis": "SPACING",
            "value": value,
            "status": "BUILT" if gates_ok else "GATE-FAIL",
            "receipt": "N",
            "receipt_score": "",
            "predicted_change": (f"{pred['point']:+.4f} DTI (MODEL; band {pred['band'][0]:+.4f}"
                                 f"..{pred['band'][1]:+.4f}; coverage {pred['coverage_rel_change']*100:+.2f}%"
                                 f" at fixed mass)"),
            "date": DATE,
            "form_note": note,
            "notes": (f"{spec['mode']} hard-disk relaxation at {spec['target_sep']} px; "
                      f"{stats['n_moved']} dots moved, {stats['n_placement_failures']} left in place, "
                      f"mean displacement {stats['mean_displacement_px']:.2f} px; "
                      f"W={spec['window']}, corridor={spec['corridor'] if spec['mode']=='along' else '-'}"),
            "source": "GEMSDOE89",
        }
        rep["ledger_row"] = row
        (ROOT / "registry" / f"build_report_spacing_{value}.json").write_text(json.dumps(rep, indent=1) + "\n")
        append_ledger_row(row)
        out.append(rep)

        print(f"[{value}] {rid}  gates={gates_ok} twins={twins_equal} moved={stats['n_moved']} "
              f"({stats['pct_changed']:.1f}%) disp={stats['mean_displacement_px']:.2f} "
              f"cov {pred['coverage_rel_change']*100:+.2f}% pred {pred['point']:+.4f} "
              f"[{rep['seconds']}s]")
        if not gates_ok:
            for r in res_nan + res_zeros:
                if not r["ok"]:
                    print("   FAILED GATE:", r)
            print("   new-position clearance:", rep["gates"]["new_positions_catalogue_clearance"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
