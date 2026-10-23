#!/usr/bin/env python3
"""Build SPACING-axis variants of the verified R0 parent.

Three constructions at matched count (brief sec.5, SPACING):
  pd3       Poisson-disk: greedy <3 px violators hop to the best local gap
  strike3   the SAME violators re-spaced along the local det_elev strike
  lat3-t1p5 partial square-lattice regularization (s=3 px, tolerance 1.5 px)

Every run
  1. verifies every pinned input against registry/data_manifest.json,
  2. verifies the parent against the ledger sha256 (c55bafc4...),
  3. builds the variant (count preserved, bounded local hops, seeded),
  4. writes <id>.tif (NaN outside) and <id>-zeros.tif, re-reads both,
  5. runs the MUST gates and the REPORT-ONLY instruments,
  6. writes registry/build_report_spacing_<value>.json and merges into
     registry/build_reports.json.

Only spacing geometry changes: no mass, ranking, relief or collar edit.
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

from gemsdoe import grid, proxy, spacing, validate  # noqa: E402
from gemsdoe.metric import kernel_weight  # noqa: E402
from gemsdoe.relief import stream_bands  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
PARENT_SHA256 = "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
DATE = "20261023"
SEED = 20261023
BAND_DET_ELEV = 12

VARIANTS = {
    "pd3": dict(kind="poisson_disk", r_min=3.0, window=6.0,
                note="Poisson-disk: greedy <3px violators move to the farthest free pixel within 6px"),
    "strike3": dict(kind="along_strike", r_min=3.0, window=5.0, cos_gate=0.5,
                    sigma=1.0,
                    note="same violators re-spaced along local det_elev strike, |cos|>=0.5, window 5px"),
    "lat3-t1p5": dict(kind="lattice", spacing=3, tol=1.5, window=4.0,
                      note="square lattice s=3px; dots >1.5px from a node move to the nearest free node within 4px"),
}

# MODEL predictions from the marginal-gain algebra. Scale: with the catalogue
# as a counterfactual truth, D=56341 -> c = 1/(D+0.2) = 1.78e-5 DTI per kernel
# unit per dot (a MODEL assumption: the live denominator uses the undisclosed
# new-fault count G, so the true scale can differ). Per moved dot the scenarios
# span -0.10 (pessimistic: hop off a covered line) to +0.15 (optimistic:
# redundant credit converted to distinct-truth coverage), central +0.02.
PREDICTIONS = {
    "pd3": "+0.003 (MODEL; band -0.016..+0.025). 9215 dots de-clustered; per-dot swing -0.10..+0.15 kernel units at c=1.78e-5. No-evidence outcome expected.",
    "strike3": "+0.004 (MODEL; band -0.013..+0.024). Same scale as pd3; mover-anchor strike alignment 0.76->0.94 trims the line-truth downside.",
    "lat3-t1p5": "-0.001 (MODEL; band -0.008..+0.012). Structure-agnostic control; 4642 shorter hops, no placement signal of its own.",
}
FORM_NOTES = {
    "pd3": "R0 h33-h33-2-b2 + SPACING pd3: 9215/37654 dots (24.5%) de-clustered to NN>=3px, hops<=6px, count fixed, dcat>=3px; pred +0.003",
    "strike3": "R0 h33-h33-2-b2 + SPACING strike3: 9092/37654 dots (24.1%) re-spaced along det_elev strike, hops<=5px, count fixed; pred +0.004",
    "lat3-t1p5": "R0 h33-h33-2-b2 + SPACING lat3-t1p5: 4642/37654 dots (12.3%) onto 3px lattice nodes, hops<=4px, count fixed; pred -0.001",
}


def load_manifest():
    return json.loads((ROOT / "registry" / "data_manifest.json").read_text())


def data_root(manifest):
    return Path(os.environ.get(manifest.get("data_root_env", "GEMSDOE_DATA"),
                               ROOT / manifest.get("data_root_default", "data")))


def verify_inputs(manifest):
    report = {}
    root = data_root(manifest)
    for f in manifest["files"]:
        path = root / f["local"]
        if not path.exists():
            report[f["id"]] = {"present": False, "ok": False}
            continue
        sha = grid.sha256_file(path)
        report[f["id"]] = {"present": True, "ok": sha == f["sha256"],
                           "sha256": sha, "expected": f["sha256"]}
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


def build_one(value, spec, pts, parent_dots, capacity, footprint, catalogue,
              cat_mask, uy, ux, rng_split):
    t0 = time.time()
    r_min = spec.get("r_min", 3.0)
    if spec["kind"] in ("poisson_disk", "along_strike"):
        is_anchor, movers, violated_anchor = spacing.greedy_violators(
            pts, parent_dots.shape, r_min, rng_split)
        extra = {"n_greedy_violators": int(len(movers)),
                 "n_anchors": int(is_anchor.sum()), "r_min_px": r_min}
        if spec["kind"] == "poisson_disk":
            nn0, _ = spacing.nearest_neighbour_distance(parent_dots)
            out, moved = spacing.place_poisson_disk(
                pts, movers, nn0, capacity, spec["window"],
                np.random.default_rng(SEED + 1))
        else:
            out, moved, no_strike = spacing.place_along_strike(
                pts, movers, violated_anchor, uy, ux, capacity,
                spec["window"], spec["cos_gate"], np.random.default_rng(SEED + 2))
            extra["no_strike_kept"] = int(no_strike)
    else:
        out, moved, phase, n_anchored = spacing.place_lattice(
            pts, capacity, spec["spacing"], spec["tol"], spec["window"],
            np.random.default_rng(SEED + 3))
        violated_anchor = None
        extra = {"lattice_phase": [int(phase[0]), int(phase[1])],
                 "lattice_spacing_px": spec["spacing"],
                 "lattice_tol_px": spec["tol"],
                 "n_within_tolerance_kept": int(n_anchored)}

    variant = spacing.mask_from_pts(out, parent_dots.shape)
    stats = spacing.spacing_stats(
        parent_dots, variant, footprint, moved, pts, out,
        uy=uy, ux=ux, extra=extra)

    # catalogue clearance of the NEW pixels (hard constraint 4 on moved dots)
    d_cat = ndi.distance_transform_edt(~cat_mask)
    old_pos = pts[moved]
    new_pos = out[moved]
    stats["moved_min_clearance_after_px"] = float(d_cat[new_pos[:, 0], new_pos[:, 1]].min()) \
        if moved.any() else None
    stats["moved_min_clearance_before_px"] = float(d_cat[old_pos[:, 0], old_pos[:, 1]].min()) \
        if moved.any() else None
    stats["inherited_dots_below_3px"] = int((d_cat[pts[:, 0], pts[:, 1]] < 3.0).sum())
    stats["seconds"] = round(time.time() - t0, 1)

    # direct mover->anchor strike alignment: the controlled local quantity
    if violated_anchor is not None and moved.any():
        ks = np.flatnonzero(moved)
        anc = violated_anchor[ks]
        ks, anc = ks[anc >= 0], anc[anc >= 0]
        uay = uy[pts[anc, 0], pts[anc, 1]]
        uax = ux[pts[anc, 0], pts[anc, 1]]

        def _cos(frm):
            vy = frm[ks, 0] - pts[anc, 0]
            vx = frm[ks, 1] - pts[anc, 1]
            vn = np.hypot(vy, vx)
            return np.abs(vy * uay + vx * uax) / vn

        stats["mover_anchor_alignment_before"] = float(_cos(pts).mean())
        stats["mover_anchor_alignment_after"] = float(_cos(out).mean())

    # MODEL inputs: catalogue kernel credit of old vs new moved-dot pixels
    k_old = kernel_weight(d_cat[old_pos[:, 0], old_pos[:, 1]]) if moved.any() else np.zeros(0)
    k_new = kernel_weight(d_cat[new_pos[:, 0], new_pos[:, 1]]) if moved.any() else np.zeros(0)
    model = {
        "moved_dots": int(moved.sum()),
        "moved_mean_catalogue_kernel_before": float(k_old.mean()) if moved.any() else None,
        "moved_mean_catalogue_kernel_after": float(k_new.mean()) if moved.any() else None,
        "moved_frac_within_kernel_of_catalogue_before": float((k_old > 0).mean()) if moved.any() else None,
        "moved_frac_within_kernel_of_catalogue_after": float((k_new > 0).mean()) if moved.any() else None,
        "pays_threshold_at_parent_dti": 0.2 * 0.2778,
        "parent_min_clearance_px": float(d_cat[pts[:, 0], pts[:, 1]].min()),
    }
    return variant, out, moved, stats, model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--value", choices=sorted(VARIANTS), default=None)
    ap.add_argument("--all", action="store_true")
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
    root = data_root(manifest)
    paths = {f["id"]: root / f["local"] for f in manifest["files"]}

    parent = grid.read_back(paths["parent_r0_zeros"])[0]
    parent_dots = parent > 0
    assert grid.sha256_file(paths["parent_r0_zeros"]) == PARENT_SHA256
    pts = np.argwhere(parent_dots)
    print(f"[ok] parent R0 verified {PARENT_SHA256[:12]} with {len(pts)} dots")

    sample, contract = grid.read_template(paths["sample_submission"])
    footprint = np.isfinite(sample)
    del sample
    catalogue = grid.read_back(paths["existing_faults"])[0]
    cat_mask = catalogue > 0
    capacity = spacing.capacity_mask(footprint, cat_mask)
    print(f"[ok] footprint {int(footprint.sum())} px, catalogue {int(cat_mask.sum())} px, "
          f"capacity {int(capacity.sum())} px")

    det = stream_bands(paths["training_features"], [BAND_DET_ELEV])[BAND_DET_ELEV]
    uy, ux = spacing.strike_field(det, sigma=1.0)
    del det
    print("[ok] strike field built from det_elev band 12 (sigma=1px)")

    hashes = ledger_hashes(ROOT / "ledger" / "submissions.csv")
    parent_proxy = proxy.hide_and_recover(parent_dots, cat_mask)
    parent_surrogate = proxy.surrogate_dti(parent_dots, cat_mask)
    null_dots = proxy.random_null(parent_dots, footprint, cat_mask)
    null_proxy = proxy.hide_and_recover(null_dots, cat_mask)
    null_surrogate = proxy.surrogate_dti(null_dots, cat_mask)

    values = sorted(VARIANTS) if args.all else [args.value]
    reports = []
    rng_split = np.random.default_rng(SEED)
    for value in values:
        spec = VARIANTS[value]
        variant, out, moved, stats, model = build_one(
            value, spec, pts, parent_dots, capacity, footprint, catalogue,
            cat_mask, uy, ux, rng_split)

        tmp_nan = ROOT / "releases" / "_tmp_nan.tif"
        tmp_zeros = ROOT / "releases" / "_tmp_zeros.tif"
        grid.write_submission(tmp_nan, variant, footprint, encoding="nan")
        grid.write_submission(tmp_zeros, variant, footprint, encoding="zeros")
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
            clearance_raster=catalogue)
        twins_equal = bool(np.array_equal(dots_nan, dots_zeros)) and \
            bool(np.array_equal(variant, dots_nan))

        v_proxy = proxy.hide_and_recover(variant, cat_mask)
        v_surrogate = proxy.surrogate_dti(variant, cat_mask)
        model["surrogate_dti_delta"] = v_surrogate - parent_surrogate

        rep = {
            "id": rid, "value": value, "axis": "SPACING", "spec": spec,
            "parent": PARENT_ID, "parent_sha256": PARENT_SHA256, "seed": SEED,
            "stats": stats,
            "files": {"nan": str(final_nan.relative_to(ROOT)),
                      "zeros": str(final_zeros.relative_to(ROOT)),
                      "sha256": sha_nan, "sha256_zeros": sha_zeros, "sha8": sha8},
            "gates": {"nan": {"ok": ok_nan, "results": res_nan},
                      "zeros": {"ok": ok_zeros, "results": res_zeros},
                      "twins_identical_mask": twins_equal},
            "report_only": {
                "proxy_variant": v_proxy, "proxy_parent": parent_proxy,
                "proxy_random_null": null_proxy,
                "surrogate_dti_variant": v_surrogate,
                "surrogate_dti_parent": parent_surrogate,
                "surrogate_dti_random_null": null_surrogate,
                "model_inputs": model,
            },
            "predicted_change": PREDICTIONS[value],
            "form_note": FORM_NOTES[value],
        }
        (ROOT / "registry" / f"build_report_spacing_{value}.json").write_text(
            json.dumps(rep, indent=1) + "\n")
        reports.append(rep)
        print(f"[{value}] {rid}  gates nan={ok_nan} zeros={ok_zeros} twins={twins_equal}  "
              f"changed={stats['pct_changed']:.2f}%  {stats['seconds']}s")
        if not ok_nan or not ok_zeros:
            for r in res_nan + res_zeros:
                if not r["ok"]:
                    print("   FAILED GATE:", r)

    # merge with prior (RELIEF) reports without reordering them
    merged_path = ROOT / "registry" / "build_reports.json"
    prior = json.loads(merged_path.read_text()) if merged_path.exists() else []
    ids_new = {r["id"] for r in reports}
    prior = [r for r in prior if r["id"] not in ids_new]
    merged_path.write_text(json.dumps(prior + reports, indent=1) + "\n")
    print("[done]")


if __name__ == "__main__":
    main()
