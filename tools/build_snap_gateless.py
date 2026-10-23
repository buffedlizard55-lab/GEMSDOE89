#!/usr/bin/env python3
"""Build the gateless SNAP variants of the verified R0 parent.

Usage:
    python tools/build_snap_gateless.py --value 2p0px-g0p00
    python tools/build_snap_gateless.py --all

Start gates first (brief sec.5):
  1. every pinned input in registry/data_manifest.json re-hashed,
  2. parent R0 rebuilt from its mask with the parent writer profile and the
     emitted bytes matched against c55bafc470054e8271dcb89347a17e07fefe50de6
     af6e6ba6c4b169ef7ab6fa9 (tools/rebuild_r0.py, run in-process),
then, per variant (one controlled edit each):
  3. deterministic snap (gate 0.00 = any strictly stronger allowed pixel in
     the window; targets >= 3 px off the catalogue; count fixed at 37,654),
  4. write <id>.tif (NaN outside) + <id>-zeros.tif, re-read both from disk,
     run the MUST gates,
  5. append the ledger row and write registry/build_report_snap_<value>.json.

The response recipe is replicated exactly from the upstream recorded SNAP
recipe (bands 3 tmi_hg + 18 iso_grav_anom_hg, median-fill, gaussian sigma 1,
robust_unit at p99.5, pixel-wise max), so a cross-session comparison against
the upstream gated arms isolates the gate and nothing else.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe import grid, proxy, relief, snap, validate  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
PARENT_SHA256 = "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
DATE = "20261023"
EXPECTED_DOTS = 37654

# Recorded live-anchor MODEL inversion (upstream evidence/h33_validation.json,
# from the live pair D2.8 0.2600 -> H27-4-R1-SOLO 0.2708 at 40,199->36,308
# dots): a pure position change gives dDTI ~= dT / D.
ANCHOR_D = 18734.44
ANCHOR_T = 5073.29
# Scenario fractions of moved dots that NET-close one full pixel (kernel gain
# 1/3 each); negative side prices the mimic (snapping onto non-fault crests).
SCEN_FRAC = {"lo": -0.05, "central": 0.05, "hi": 0.15}

VARIANTS = {
    "1p0px-g0p00": dict(window_px=1.0, margin=0.0,
                        note="edge-neighbour window: minimum decisive snap"),
    "1p4px-g0p00": dict(window_px=1.42, margin=0.0,
                        note="8-neighbour window; gate ablation of upstream 1p4px-g0p02"),
    "2p0px-g0p00": dict(window_px=2.0, margin=0.0,
                        note="full 2 px disc; gate ablation of upstream 2p0px-g0p01/g0p02"),
}


def load_manifest():
    return json.loads((ROOT / "registry" / "data_manifest.json").read_text())


def data_paths(manifest):
    import os

    root = Path(os.environ.get(manifest.get("data_root_env", "GEMSDOE_DATA"),
                                ROOT / manifest.get("data_root_default", "data")))
    return root, {f["id"]: root / f["local"] for f in manifest["files"]}


def verify_inputs(manifest):
    root, paths = data_paths(manifest)
    report = {}
    for f in manifest["files"]:
        if f.get("unverified"):
            report[f["id"]] = {"present": False, "ok": True,
                               "skipped": "unverified report-only pin (IRREGULARITIES item 8)"}
            continue
        p = paths[f["id"]]
        if not p.exists():
            report[f["id"]] = {"present": False, "ok": False}
            continue
        sha = grid.sha256_file(p)
        report[f["id"]] = {"present": True, "ok": sha == f["sha256"], "sha256": sha,
                           "expected": f["sha256"]}
    return report


def parent_rebuild_check(paths):
    """Rebuild R0 from its mask with the parent profile; require byte match."""
    import rasterio
    import tifffile

    parent = tifffile.imread(paths["parent_r0_zeros"])
    dots = parent > 0
    with rasterio.open(paths["sample_submission"]) as tpl:
        profile = tpl.profile.copy()
        foot = np.isfinite(tpl.read(1))
    profile.update(driver="GTiff", dtype="float32", count=1, compress="deflate",
                   predictor=3, zlevel=9, tiled=True, blockxsize=256,
                   blockysize=256, nodata=None)
    tmp = ROOT / "data" / "_rebuild_r0_check.tif"
    out = np.where(foot, dots.astype(np.float32), 0.0).astype(np.float32)
    with rasterio.open(tmp, "w", **profile) as dst:
        dst.write(out, 1)
    sha = grid.sha256_file(tmp)
    ok = sha == PARENT_SHA256 == grid.sha256_file(paths["parent_r0_zeros"])
    return ok, sha, int(dots.sum())


def ledger_hashes(path):
    out = set()
    if not path.exists():
        return out
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            for k in ("sha256", "sha256_zeros", "sha8"):
                v = (row.get(k) or "").strip()
                if v:
                    out.add(v)
    return out


def ledger_triples(path):
    out = set()
    if not path.exists():
        return out
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            out.add(((row.get("parent") or "").strip(),
                     (row.get("axis") or "").strip().upper(),
                     (row.get("value") or "").strip()))
    return out


def git_sha():
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def predict(moved):
    """MODEL projection from the recorded live anchor; not a score."""
    lo = SCEN_FRAC["lo"] * moved / 3.0 / ANCHOR_D
    mid = SCEN_FRAC["central"] * moved / 3.0 / ANCHOR_D
    hi = SCEN_FRAC["hi"] * moved / 3.0 / ANCHOR_D
    return lo, mid, hi


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

    _, paths = data_paths(manifest)

    # ---- start gate: rebuild R0, match its sha256 --------------------------
    ok_rebuild, sha_rebuild, n_parent = parent_rebuild_check(paths)
    if not ok_rebuild or n_parent != EXPECTED_DOTS:
        print(f"[FAIL] R0 rebuild sha {sha_rebuild} != {PARENT_SHA256} (dots {n_parent})")
        sys.exit(3)
    print(f"[ok] R0 rebuilt byte-exactly ({sha_rebuild[:12]}…, {n_parent} dots)")

    parent = grid.read_back(paths["parent_r0_zeros"])[0]
    parent_dots = parent > 0
    assert int(parent_dots.sum()) == EXPECTED_DOTS

    sample, contract = grid.read_template(paths["sample_submission"])
    footprint = np.isfinite(sample)
    del sample
    catalogue = grid.read_back(paths["existing_faults"])[0]
    cat_mask = catalogue > 0

    from scipy import ndimage as ndi

    d_cat = ndi.distance_transform_edt(~cat_mask)
    allowed = footprint & (d_cat >= 3.0)
    print(f"[ok] footprint {int(footprint.sum())} px; catalogue {int(cat_mask.sum())} px; "
          f"parent min d_cat {float(d_cat[parent_dots].min()):.3f} px; "
          f"parent dots <3 px: {int((d_cat[parent_dots] < 3).sum())}")

    # ---- response surface ---------------------------------------------------
    bands = relief.stream_bands(paths["training_features"],
                                [i for i, _n in snap.EDGE_BANDS])
    resp, resp_diag = snap.edge_response(bands, footprint)
    del bands
    print("[ok] response: " + ", ".join(f"{b['name']}(b{b['index']})"
                                        for b in resp_diag["response"]["bands"]))

    hashes = ledger_hashes(ROOT / "ledger" / "submissions.csv")
    triples = ledger_triples(ROOT / "ledger" / "submissions.csv")

    # ---- report-only instruments on the parent ------------------------------
    parent_proxy = proxy.hide_and_recover(parent_dots, cat_mask)
    parent_surrogate = proxy.surrogate_dti(parent_dots, cat_mask)
    canary = proxy.canary({"tmi_hg": resp_diag["per_band"]["tmi_hg"],
                           "iso_grav_anom_hg": resp_diag["per_band"]["iso_grav_anom_hg"]},
                          cat_mask)
    canary_pass = all(not v["flag"] for v in canary.values())
    print(f"[report-only] parent hide&recover recall {parent_proxy['recall']:.4f}; "
          f"canary {'PASS' if canary_pass else 'FLAG'} "
          f"({ {k: round(v['auc'], 3) for k, v in canary.items()} })")

    values = sorted(VARIANTS) if args.all else [args.value]
    ledger_path = ROOT / "ledger" / "submissions.csv"
    new_rows = []
    reports = []

    for value in values:
        spec = VARIANTS[value]
        triple = (PARENT_ID, "SNAP", value)
        if triple in triples:
            print(f"[skip] (parent, axis, value) already built: {triple}")
            continue

        t0 = time.time()
        res = snap.snap_dots(parent_dots, resp, allowed,
                             max_shift=spec["window_px"], margin=spec["margin"])
        mask = res.mask
        stats = res.stats
        assert stats["count_preserved"] and int(mask.sum()) == EXPECTED_DOTS

        moved_targets = np.zeros_like(mask)
        for (y0, x0, y1, x1, *_r) in res.moves:
            moved_targets[y1, x1] = True
        targets_min_dcat = float(d_cat[moved_targets].min()) if res.moves else None

        # ---- mask gates (before writing) ------------------------------------
        collar_before = int((d_cat[parent_dots] < 3.0).sum())
        collar_after = int((d_cat[mask] < 3.0).sum())
        mask_gates = {
            "count_preserved": int(mask.sum()) == EXPECTED_DOTS,
            "zero_catalogue_mass": int((mask & cat_mask).sum()) == 0,
            "inside_footprint": int((mask & ~footprint).sum()) == 0,
            "moved_targets_ge_3px": (targets_min_dcat is None
                                     or targets_min_dcat >= 3.0),
            "collar_not_increased": collar_after <= collar_before,
            "differs_from_parent": not np.array_equal(mask, parent_dots),
        }
        if not all(mask_gates.values()):
            print(json.dumps({"ERROR": "mask gate failed", "value": value,
                              "gates": mask_gates,
                              "targets_min_dcat": targets_min_dcat}, indent=1))
            sys.exit(4)

        # ---- write both twins, content-addressed ---------------------------
        tmp_nan = ROOT / "releases" / "_tmp_nan.tif"
        tmp_zeros = ROOT / "releases" / "_tmp_zeros.tif"
        grid.write_submission(tmp_nan, mask, footprint, encoding="nan")
        grid.write_submission(tmp_zeros, mask, footprint, encoding="zeros")
        sha_nan = grid.sha256_file(tmp_nan)
        sha_zeros = grid.sha256_file(tmp_zeros)
        sha8 = sha_nan[:8]
        rid = f"{PARENT_ID}-snap{value}-{DATE}-{sha8}"
        final_nan = ROOT / "releases" / f"{rid}.tif"
        final_zeros = ROOT / "releases" / f"{rid}-zeros.tif"
        tmp_nan.replace(final_nan)
        tmp_zeros.replace(final_zeros)

        # ---- re-read from disk, run the MUST gates --------------------------
        nan_arr, nan_contract = grid.read_back(final_nan)
        zeros_arr, _ = grid.read_back(final_zeros)
        dots_read_nan = np.nan_to_num(nan_arr) > 0
        dots_read_zeros = zeros_arr > 0
        ok_nan, res_nan = validate.gate_release(
            final_nan, contract, footprint=footprint, dots_mask=dots_read_nan,
            require_nan_outside=True, ledger_hashes=hashes,
            min_clearance_px=0.0, clearance_raster=catalogue)
        ok_zeros, res_zeros = validate.gate_release(
            final_zeros, contract, footprint=footprint, dots_mask=dots_read_zeros,
            require_nan_outside=False, ledger_hashes=hashes,
            clearance_raster=catalogue)
        twins_equal = bool(np.array_equal(dots_read_nan, dots_read_zeros)) and \
            bool(np.array_equal(mask, dots_read_nan))

        # ---- report-only instruments on the variant -------------------------
        v_proxy = proxy.hide_and_recover(mask, cat_mask)
        v_surrogate = proxy.surrogate_dti(mask, cat_mask)

        # ---- parent-diff statistics + MODEL prediction ----------------------
        moved = stats["dots_moved"]
        pred_lo, pred_mid, pred_hi = predict(moved)
        d_cat_parent = d_cat[parent_dots]
        d_cat_var = d_cat[mask]
        added = mask & ~parent_dots
        removed = parent_dots & ~mask
        nn_parent = relief.nearest_neighbour_distance(parent_dots)[0]
        nn_var = relief.nearest_neighbour_distance(mask)[0]
        diff_stats = {
            **stats,
            "pct_of_parent_dots_moved": round(100.0 * moved / EXPECTED_DOTS, 3),
            "moved_targets_min_dcat_px": targets_min_dcat,
            "collar_lt3px_before": collar_before,
            "collar_lt3px_after": collar_after,
            "pixels_added_vs_parent": int(added.sum()),
            "pixels_removed_vs_parent": int(removed.sum()),
            "min_dcat_parent_px": float(d_cat_parent.min()),
            "min_dcat_variant_px": float(d_cat_var.min()),
            "median_dcat_parent_px": float(np.median(d_cat_parent)),
            "median_dcat_variant_px": float(np.median(d_cat_var)),
            "nn_median_before_px": float(np.median(nn_parent)),
            "nn_median_after_px": float(np.median(nn_var)),
            "block_cv_1km_before": snap.block_density_cv(parent_dots, footprint),
            "block_cv_1km_after": snap.block_density_cv(mask, footprint),
            "block_cv_5km_before": relief.block_density_cv(parent_dots, footprint, block=50),
            "block_cv_5km_after": relief.block_density_cv(mask, footprint, block=50),
            "mean_response_gain": stats["mean_response_gain"],
        }

        note = (f"R0 h33-h33-2-b2 + SNAP {value}: {moved:,}/{EXPECTED_DOTS} dots "
                f"moved, mean {stats['mean_displacement_px']:.2f} px, targets dcat>=3px; "
                f"pred {pred_mid:+.3f}")
        if len(note) > 140:
            note = note[:137] + "..."

        rep = {
            "id": rid,
            "value": value,
            "spec": spec,
            "parent": PARENT_ID,
            "parent_sha256": PARENT_SHA256,
            "parent_rebuild_sha256": sha_rebuild,
            "seed": None,
            "determinism": "no RNG; row-major dots; offsets by (dist, dy, dx)",
            "git_sha": git_sha(),
            "recipe": {
                "inputs": [f"parent_r0_zeros.tif (sha256 {PARENT_SHA256[:12]}…)",
                           "training_features.tif bands 3 tmi_hg + 18 iso_grav_anom_hg "
                           "(identities via registry/data_manifest.json band_identity_source)"],
                "response": "per-band: footprint-median fill -> gaussian sigma=1.0 px -> "
                            "robust_unit (median/IQR z, 1.0 = 99.5th pct, clip 6) -> max fusion",
                "window_px": spec["window_px"],
                "margin": spec["margin"],
                "allowed_targets": "footprint & d_cat >= 3.0 px",
            },
            "stats": diff_stats,
            "model_prediction": {
                "band": [pred_lo, pred_mid, pred_hi],
                "central": pred_mid,
                "basis": (f"pure position change dDTI ~= dT/D; D={ANCHOR_D}, "
                          f"T={ANCHOR_T} from the recorded live-anchor inversion "
                          "(upstream evidence/h33_validation.json, live pair 0.2600->0.2708); "
                          f"scenario: {SCEN_FRAC['lo']:+.2f}..{SCEN_FRAC['hi']:+.2f} net "
                          f"fraction of moved dots close (or open) one full pixel, "
                          f"kernel gain 1/3; central {SCEN_FRAC['central']:+.2f}. "
                          "Evidence class MODEL, not a score."),
                "no_evidence_threshold": 0.01,
            },
            "files": {
                "nan": {"path": str(final_nan.relative_to(ROOT)), "sha256": sha_nan,
                        "bytes": final_nan.stat().st_size},
                "zeros": {"path": str(final_zeros.relative_to(ROOT)), "sha256": sha_zeros,
                          "bytes": final_zeros.stat().st_size},
                "sha8": sha8,
            },
            "gates": {"mask": mask_gates, "nan": {"ok": ok_nan, "results": res_nan},
                      "zeros": {"ok": ok_zeros, "results": res_zeros},
                      "twins_identical_mask": twins_equal,
                      "all_passed": all(mask_gates.values()) and ok_nan and ok_zeros
                      and twins_equal},
            "report_only": {
                "proxy_variant": v_proxy, "proxy_parent": parent_proxy,
                "surrogate_variant": v_surrogate, "surrogate_parent": parent_surrogate,
                "leakage_canary": canary, "leakage_canary_pass": canary_pass,
                "sgmc_control": "NOT RUN - control raster not in manifest (deferred, "
                                "report-only, cannot gate)",
            },
            "response_surface": resp_diag["response"],
            "form_note": note,
            "seconds": round(time.time() - t0, 1),
        }
        (ROOT / "registry" / f"build_report_snap_{value}.json").write_text(
            json.dumps(rep, indent=1) + "\n")
        reports.append(rep)

        row = {
            "id": rid, "site": "GEMSDOE89", "name": rid, "score": "",
            "evidence_class": "BUILT (unscored)", "encoding": "nan+zeros",
            "n_dots": str(EXPECTED_DOTS),
            "pct_changed": f"{diff_stats['pct_of_parent_dots_moved']:.2f}",
            "sha8": sha8, "sha256": sha_nan, "sha256_zeros": sha_zeros,
            "parent": PARENT_ID, "axis": "SNAP", "value": value,
            "status": "BUILT" if rep["gates"]["all_passed"] else "GATE-FAIL",
            "receipt": "N", "receipt_score": "",
            "predicted_change": (f"{pred_lo:+.4f}..{pred_hi:+.4f} "
                                 f"(MODEL central {pred_mid:+.4f}; band prices the mimic)"),
            "date": DATE, "form_note": note,
            "notes": (f"window {spec['window_px']} px, gate 0.00, {moved:,} dots moved, "
                      f"mean displacement {stats['mean_displacement_px']:.3f} px, "
                      f"moved-target min dcat {targets_min_dcat:.2f} px, "
                      f"cv1km {diff_stats['block_cv_1km_before']:.3f}->"
                      f"{diff_stats['block_cv_1km_after']:.3f}"),
            "source": "GEMSDOE89",
        }
        new_rows.append(row)
        print(f"[{value}] {rid}  gates={rep['gates']['all_passed']}  moved={moved} "
              f"({diff_stats['pct_of_parent_dots_moved']}%)  mean disp "
              f"{stats['mean_displacement_px']:.3f} px  pred {pred_lo:+.4f}..{pred_hi:+.4f} "
              f"({rep['seconds']}s)")
        if not rep["gates"]["all_passed"]:
            for r in res_nan + res_zeros:
                if not r["ok"]:
                    print("   FAILED GATE:", r)
            sys.exit(5)

    # ---- append ledger rows --------------------------------------------------
    if new_rows:
        with open(ledger_path, newline="", encoding="utf-8") as fh:
            fieldnames = csv.DictReader(fh).fieldnames
        with open(ledger_path, "a", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
            for row in new_rows:
                w.writerow(row)
        print(f"[ok] appended {len(new_rows)} ledger row(s)")

    (ROOT / "registry" / "build_reports_snap.json").write_text(
        json.dumps(reports, indent=1) + "\n")
    print("[done]")


if __name__ == "__main__":
    main()
