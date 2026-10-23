#!/usr/bin/env python3
"""Build the CONCENTRATION arms of session GEMSDOE89 from the verified R0 parent.

Axis value, stated once: **5 km blocks, prior = catalogued-fault density,
10 % / 20 % moved toward the prior, plus a 10 % sign-control arm moved away
from it.**  GEMSDOE84 already spent `5km-t25-move2400`, `5km-t50-move3765` and
`spread5km-move2400` on this axis with a *self-referential* prior (the parent's
own gain surface).  All three arms here use an independent prior (known-fault
density) and are therefore new (parent, axis, value) triples.

Each run
  1. verifies every pinned input this axis reads against
     registry/data_manifest.json (sha256 recomputed from disk),
  2. re-derives R0's dot set from the pinned ancestors and requires it to be
     cell-identical to the parent raster (never approximate the parent),
  3. builds each arm (count fixed at 37,654; new dots >= 3 px from the
     catalogue, >= 2.8 px from every surviving dot, inside recipient blocks),
  4. writes <id>.tif (NaN outside footprint) and <id>-zeros.tif,
  5. re-reads both from disk and runs every MUST gate,
  6. writes registry/build_concentration_<value>.json and the combined report.

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

from gemsdoe import concentration, grid, mass, proxy, relief, validate  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
PARENT_SHA256 = "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
DATE = "20261023"
SEED = 20261023

# Inputs this axis reads.  Kept local on purpose: the manifest's `session_gate`
# block that the MASS builder reads was removed from registry/data_manifest.json
# (see IRREGULARITIES), so builders must name their own requirements.
REQUIRED = (
    "sample_submission", "existing_faults", "parent_r0_zeros", "parent_r0_nan",
    "parent_field_h19_5", "parent_ancestor_solo_d28", "parent_ancestor_d28",
    "training_features",
)
EDGE_BANDS = {2: "rtp", 13: "iso_grav_anom"}   # potential-field gradients only

VARIANTS = {
    "cat10": dict(fraction=0.10, direction="toward", role="PRIMARY",
                  predicted_note="10 % of dots moved from zero-catalogue blocks into the top-prior quartile"),
    "cat20": dict(fraction=0.20, direction="toward", role="DOSE",
                  predicted_note="20 % dose of cat10 (2x the moved count)"),
    "cat10away": dict(fraction=0.10, direction="away", role="SIGN CONTROL",
                      predicted_note="10 % moved the other way: out of the top-prior quartile into zero-catalogue blocks"),
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
    ver, bad = verify_inputs(manifest, set(REQUIRED))
    if bad:
        print(json.dumps({"ERROR": "pinned inputs failed verification", "detail": bad}, indent=1))
        sys.exit(2)
    print(f"[ok] pinned inputs verified: "
          f"{len([v for v in ver.values() if v['present'] and v['ok']])} of {len(ver)} "
          f"present and hash-clean (required: {sorted(REQUIRED)})")

    root = data_root(manifest)
    paths = {f["id"]: root / f["local"] for f in manifest["files"]}

    sample, contract = grid.read_template(paths["sample_submission"])
    footprint = np.isfinite(sample)
    del sample
    catalogue = grid.read_back(paths["existing_faults"])[0]
    cat_mask = (catalogue > 0) & footprint
    parent = grid.read_back(paths["parent_r0_zeros"])[0]
    parent_dots = (parent > 0) & footprint
    if grid.sha256_file(paths["parent_r0_zeros"]) != PARENT_SHA256:
        print("STOP: parent raster sha256 does not match the pinned R0 zeros twin")
        sys.exit(2)
    print(f"[ok] parent R0 sha256 {PARENT_SHA256[:12]}  dots={int(parent_dots.sum())}")

    # ---- parent identity: re-derive the dot set from pinned ancestors ----
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
    h19 = grid.read_back(paths["parent_field_h19_5"])[0] > 0
    from gemsdoe import parent as parent_mod  # noqa: E402  (recipe rebuild)
    r0_mask, _d28 = parent_mod.rebuild_r0_mask(h19, footprint, cat_mask, r_min=2.8, collar_px=2.0)
    rebuild["recipe_dot_thin_2p8"] = {
        "h19_5_pixels": int(h19.sum()),
        "derived_dots": int(r0_mask.sum()),
        "differing_cells_vs_parent": int((r0_mask ^ parent_dots).sum()),
        "identical": bool(np.array_equal(r0_mask, parent_dots)),
    }
    if not all(v["identical"] for v in rebuild.values()):
        print(json.dumps({"ERROR": "R0 not reproduced from pinned inputs", "detail": rebuild}, indent=1))
        sys.exit(3)
    print(f"[ok] R0 reproduced exactly from both ancestors and from the recipe")

    # ---- inputs to the axis ----
    bands = relief.stream_bands(paths["training_features"], sorted(EDGE_BANDS))
    edge = concentration.structural_edge_score(bands, footprint)
    del bands
    u_vec, u_pts = mass.unique_credit(parent_dots)
    u = np.zeros(parent_dots.shape, dtype=np.float32)
    u[u_pts[:, 0], u_pts[:, 1]] = u_vec.astype(np.float32)
    print(f"[ok] structural edge score built from bands {sorted(EDGE_BANDS)}; "
          f"per-dot rank (unique kernel credit) mean {u_vec.mean():.4f}")

    prior, eligible, n_foot, n_cat = concentration.block_prior(cat_mask, footprint)
    st0 = concentration.strata(prior, eligible)
    bid = concentration.block_id(parent_dots.shape)
    dots_per_block = np.bincount(bid[parent_dots], minlength=prior.size)
    block_table = {
        "block_px": concentration.BLOCK_PX,
        "block_km": concentration.BLOCK_PX / 10.0,
        "eligible_blocks": int(st0["eligible_blocks"]),
        "zero_prior_blocks": int(st0["zero_blocks"]),
        "high_prior_blocks": int(st0["high_blocks"]),
        "high_prior_cut": st0["high_cut"],
        "prior_median": st0["prior_median"],
        "prior_p90": st0["prior_p90"],
        "r0_dots_in_zero_blocks": int(dots_per_block[st0["zero"]].sum()),
        "r0_dots_in_high_blocks": int(dots_per_block[st0["high"]].sum()),
        "r0_dots_in_zero_blocks_share": float(dots_per_block[st0["zero"]].sum() / parent_dots.sum()),
        "corr_r0_block_density_vs_prior": concentration._corr(
            (dots_per_block / np.maximum(n_foot, 1.0))[eligible], prior[eligible]),
        "brief_reported_best_cv": "0.51-0.59 (block size unstated; MEASURED: R0 sits at 0.516 at 15 km "
                                  "and 0.899 at 5 km, so the band cannot be used as a 5 km target)",
    }
    print(f"[ok] block table: {json.dumps(block_table)}")

    hashes = ledger_hashes()
    parent_proxy = proxy.hide_and_recover(parent_dots, cat_mask)
    parent_surrogate = proxy.surrogate_dti(parent_dots, cat_mask)
    null_proxy = proxy.hide_and_recover(
        proxy.random_null(parent_dots, footprint, cat_mask), cat_mask)
    print(f"[report-only] parent catalogue recall {parent_proxy['recall']:.4f} "
          f"(CI +-{parent_proxy['ci95_halfwidth']:.4f}, n={parent_proxy['n_withheld']}); "
          f"random null {null_proxy['recall']:.4f} -- blind to every d_cat >= 3 px edit "
          f"(IRREGULARITIES item 4)")

    values = sorted(VARIANTS) if args.all else [args.value]
    reports = []
    for value in values:
        spec = VARIANTS[value]
        t0 = time.time()
        rng = np.random.default_rng(SEED)
        variant, stats = concentration.build(
            dots=parent_dots, footprint=footprint, catalogue_mask=cat_mask,
            edge_score=edge, dot_rank=u, fraction=spec["fraction"],
            direction=spec["direction"], rng=rng,
        )
        pred = concentration.predicted_delta(stats["n_moved"], spec["direction"])

        tmp_nan = ROOT / "releases" / "_tmp_nan.tif"
        tmp_zeros = ROOT / "releases" / "_tmp_zeros.tif"
        tmp_nan.parent.mkdir(parents=True, exist_ok=True)
        grid.write_submission(tmp_nan, variant, footprint, encoding="nan")
        grid.write_submission(tmp_zeros, variant, footprint, encoding="zeros")
        sha_nan = grid.sha256_file(tmp_nan)
        sha_zeros = grid.sha256_file(tmp_zeros)
        sha8 = sha_nan[:8]
        rid = f"{PARENT_ID}-CONC5km{value}-{DATE}-{sha8}"
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
        # the >= 3 px rule binds the new dots; report the new-dot minimum too
        added = dots_nan & ~parent_dots
        added_clearance = float(d_cat[added].min()) if added.any() else None
        twins = bool(np.array_equal(dots_nan, dots_zeros)) and bool(np.array_equal(variant, dots_nan))
        parent_diff = {
            "added_vs_parent": int(added.sum()),
            "removed_vs_parent": int((parent_dots & ~dots_nan).sum()),
            "symmetric_difference": int((dots_nan ^ parent_dots).sum()),
            "pct_changed_moved": float(100.0 * added.sum() / parent_dots.sum()),
            "pct_changed_symdiff": float(200.0 * added.sum() / parent_dots.sum()),
            "jaccard": float((dots_nan & parent_dots).sum() / max(1, (dots_nan | parent_dots).sum())),
            "identical": bool(np.array_equal(dots_nan, parent_dots)),
        }
        v_proxy = proxy.hide_and_recover(dots_nan, cat_mask)
        v_surrogate = proxy.surrogate_dti(dots_nan, cat_mask)

        rep = {
            "id": rid,
            "value": value,
            "axis": "CONCENTRATION",
            "role": spec["role"],
            "spec": spec,
            "parent": PARENT_ID,
            "parent_sha256": PARENT_SHA256,
            "seed": SEED,
            "block_table": block_table,
            "parent_rebuild": rebuild,
            "edge_bands": EDGE_BANDS,
            "stats": stats,
            "predicted_delta_model": pred,
            "files": {"nan": str(final_nan.relative_to(ROOT)),
                      "zeros": str(final_zeros.relative_to(ROOT)),
                      "sha256": sha_nan, "sha256_zeros": sha_zeros, "sha8": sha8},
            "gates": {"nan": {"ok": ok_nan, "results": res_nan},
                      "zeros": {"ok": ok_zeros, "results": res_zeros},
                      "twins_identical": twins,
                      "new_dot_min_clearance_px": added_clearance},
            "parent_diff": parent_diff,
            "report_only": {
                "proxy_variant": v_proxy, "proxy_parent": parent_proxy,
                "proxy_random_null": null_proxy,
                "surrogate_dti_variant": v_surrogate,
                "surrogate_dti_parent": parent_surrogate,
            },
            "seconds": round(time.time() - t0, 1),
        }
        (ROOT / "registry" / f"build_concentration_{value}.json").write_text(
            json.dumps(rep, indent=1) + "\n")
        reports.append(rep)
        ok = ok_nan and ok_zeros and twins
        print(f"[{value}] {rid} gates nan={ok_nan} zeros={ok_zeros} twins={twins} "
              f"moved={stats['n_moved']} dcat_added_min={added_clearance} "
              f"pred={pred['central']:+.4f} ({rep['seconds']}s)")
        if not ok:
            for r in res_nan + res_zeros:
                if not r["ok"]:
                    print("   FAILED GATE:", r)

    (ROOT / "registry" / "build_concentration_reports.json").write_text(
        json.dumps(reports, indent=1) + "\n")
    print("[done]")


if __name__ == "__main__":
    main()
