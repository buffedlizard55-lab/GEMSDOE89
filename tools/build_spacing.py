#!/usr/bin/env python3
"""Build the three SPACING variants of verified Parent R0 (h33-h33-2-b2).

Usage:
    python tools/build_spacing.py --value alongstrike
    python tools/build_spacing.py --all

Each run:
  1. Verifies all pinned inputs in registry/data_manifest.json by SHA-256.
  2. Rebuilds Parent R0 (37,654 unit dots) from scored_h19_5.tif via
     BFS dot_thin(2.8) + B=2 catalogue prune and asserts exact mask + sha256 match.
  3. Runs the 19-band + h19_5 single-feature leakage canary (stops if AUC > 0.90).
  4. Builds the requested SPACING variant(s): alongstrike, poisson, lattice
     (count fixed at 37,654, per-corridor count fixed, d_cat >= 3.0 px on all
     relocated dots, % changed strictly inside 1-50 %).
  5. Writes releases/<id>.tif (NaN outside) and <id>-zeros.tif, re-reads both
     from disk, and runs every MUST gate.
  6. Records REPORT-ONLY diagnostics (catalogue hide-and-recover proxy with n
     withheld positives & 95 % CI, SGMC off-catalogue control, surrogate DTI,
     cross-strike jitter MODEL sensitivity) to registry/.
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
from scipy.ndimage import distance_transform_edt, label as ndi_label

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe import grid, metric, parent, proxy, relief, spacing, validate  # noqa: E402

DATE = "20261023"
SEED = 20261023

VARIANTS = {
    "alongstrike": {
        "mode": "alongstrike",
        "note": "1-D geodesic arc-length equipartition + exact DTI kernel 1-swap along >=6-dot H19-5 strands",
    },
    "poisson": {
        "mode": "poisson",
        "note": "2-D Bridson/dart-throwing Poisson-disk blue-noise packing across +-150 m (d<=1.5 px) corridor",
    },
    "lattice": {
        "mode": "lattice",
        "note": "isometric hexagonal lattice sampling (pitch 3.5 px) across +-200 m (d<=2.0 px) corridor",
    },
}


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"


def verify_manifest(manifest: dict, data_root: Path) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    bad = {}
    for entry in manifest["files"]:
        if entry.get("unverified"):
            print(f"[skip] unverified report-only pin {entry['id']} (IRREGULARITIES item 8)")
            continue
        p = data_root / entry["local"]
        if not p.exists():
            bad[entry["id"]] = {"present": False, "path": str(p)}
            continue
        got = grid.sha256_file(p)
        if got != entry["sha256"]:
            bad[entry["id"]] = {"got": got, "expected": entry["sha256"]}
            continue
        paths[entry["id"]] = p
    if bad:
        print(json.dumps({"ERROR": "manifest verification failed", "detail": bad}, indent=1))
        sys.exit(2)
    return paths


def existing_ledger_hashes(ledger_path: Path, exclude_axis: str = "SPACING") -> set[str]:
    if not ledger_path.exists():
        return set()
    out: set[str] = set()
    with open(ledger_path, newline="") as fh:
        for row in csv.DictReader(fh):
            if (row.get("source") == "GEMSDOE89") and ((row.get("axis") or "").upper() == exclude_axis):
                continue
            for col in ("sha256", "sha256_zeros"):
                v = (row.get(col) or "").strip()
                if v:
                    out.add(v)
    return out


def compute_jitter_model_deltas(
    r0: np.ndarray,
    variants: dict[str, np.ndarray],
    elig_h19: np.ndarray,
    foot: np.ndarray,
    cat: np.ndarray,
) -> dict:
    """Measure MODEL delta-DTI across lateral truth-offset std sigma_perp in {0, 0.8, 1.5, 2.2} px."""
    lbl, ncomp = ndi_label(elig_h19, structure=np.ones((3, 3), dtype=np.int8))
    rng = np.random.default_rng(42)
    keep = rng.random(ncomp + 1) < 0.165
    keep[0] = False
    truth0 = keep[lbl]
    ys, xs = np.nonzero(truth0)
    cids = lbl[ys, xs]

    out = {}
    for sigma in (0.0, 0.8, 1.5, 2.2):
        if sigma == 0.0:
            ts = truth0
        else:
            r = np.random.default_rng(99)
            dy_c = np.rint(r.normal(0.0, sigma, size=ncomp + 1)).astype(int)
            dx_c = np.rint(r.normal(0.0, sigma, size=ncomp + 1)).astype(int)
            ny = np.clip(ys + dy_c[cids], 0, foot.shape[0] - 1)
            nx = np.clip(xs + dx_c[cids], 0, foot.shape[1] - 1)
            ok = foot[ny, nx] & (~cat[ny, nx])
            ts = np.zeros_like(truth0)
            ts[ny[ok], nx[ok]] = True
        base_dti = metric.dti(ts, r0)
        row = {"truth_px": int(ts.sum()), "r0_dti": round(base_dti, 5), "delta_vs_r0": {}}
        for k, v in variants.items():
            row["delta_vs_r0"][k] = round(metric.dti(ts, v) - base_dti, 5)
        out[f"sigma_{sigma:.1f}px"] = row
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--value", choices=sorted(VARIANTS), default=None)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if not args.all and args.value is None:
        ap.error("specify --value or --all")

    manifest = json.loads((ROOT / "registry" / "data_manifest.json").read_text())
    data_root = Path(
        os.environ.get(
            manifest.get("data_root_env", "GEMSDOE_DATA"),
            ROOT / manifest.get("data_root_default", "data"),
        )
    )
    paths = verify_manifest(manifest, data_root)
    print(f"[ok] verified all {len(paths)} pinned manifest inputs")

    sample_arr, contract = grid.read_template(paths["sample_submission"])
    foot = np.isfinite(sample_arr)
    del sample_arr

    catalogue_raw = grid.read_back(paths["existing_faults"])[0]
    cat_mask = (np.isfinite(catalogue_raw) & (catalogue_raw > 0)) & foot
    h19_raw = grid.read_back(paths["scored_h19_5"])[0]
    h19_mask = (np.isfinite(h19_raw) & (h19_raw > 0)) & foot
    d28_pin = (np.isfinite(grid.read_back(paths["parent_ancestor_d28"])[0]) & (grid.read_back(paths["parent_ancestor_d28"])[0] > 0)) & foot
    r0_pin = (grid.read_back(paths["parent_r0_zeros"])[0] > 0) & foot
    sgmc_mask = (grid.read_back(paths["sgmc_faults"])[0] > 0) & foot

    assert grid.sha256_file(paths["parent_r0_zeros"]) == parent.R0_ZEROS_SHA256
    assert grid.sha256_file(paths["parent_r0_nan"]) == parent.R0_NAN_SHA256
    r0_rebuilt, d28_rebuilt = parent.rebuild_r0_mask(h19_mask, foot, cat_mask)
    if not np.array_equal(d28_rebuilt, d28_pin) or not np.array_equal(r0_rebuilt, r0_pin):
        print("STOP: rebuilt R0 mask does not match pinned parent_r0_zeros.tif")
        return 2
    print(f"[ok] rebuilt R0 mask bit-exact ({int(r0_rebuilt.sum())} dots)")

    # Stream all 19 bands once for the full leakage canary + det_elev relief-invariance check
    t_can = time.time()
    band_tags = manifest["files"][0]["verified_band_tags"]
    all_bands = relief.stream_bands(paths["training_features"], list(range(1, 20)))
    det_elev = all_bands[12].copy()
    feat_for_canary = {f"b{b:02d}_{band_tags[str(b)]}": all_bands[b] for b in range(1, 20)}
    feat_for_canary["scored_h19_5"] = np.where(foot, h19_mask.astype(np.float32), np.nan)
    can_res = proxy.canary(feat_for_canary, cat_mask, threshold=0.90)
    del all_bands, feat_for_canary
    any_flag = any(v["flag"] for v in can_res.values())
    max_strength = max(max(v["auc"], 1.0 - v["auc"]) for v in can_res.values() if v["auc"] is not None)
    canary_doc = {
        "instrument": "leakage canary (single-feature AUC vs catalogue membership across all 19 bands + scored_h19_5)",
        "threshold": 0.90,
        "sample_px": 400000,
        "seed": 11,
        "max_single_feature_strength": round(float(max_strength), 6),
        "features": can_res,
        "verdict": "FAIL: STOP AND INVESTIGATE" if any_flag else "PASS: no single feature exceeds 0.90",
        "note": "REPORT ONLY unless > 0.90. Checked all 19 competition bands plus scored_h19_5.",
    }
    (ROOT / "registry" / "leakage_canary.json").write_text(json.dumps(canary_doc, indent=1) + "\n")
    if any_flag:
        print("STOP: leakage canary triggered!", canary_doc["verdict"])
        return 2
    print(f"[ok] 20-feature leakage canary PASS (max strength={max_strength:.4f}, {time.time()-t_can:.1f}s)")

    ledger_hashes = existing_ledger_hashes(ROOT / "ledger" / "submissions.csv", exclude_axis="SPACING")

    parent_proxy = proxy.hide_and_recover(r0_rebuilt, cat_mask)
    parent_surrogate = proxy.surrogate_dti(r0_rebuilt, cat_mask)
    parent_sgmc = proxy.sgmc_off_catalogue_control(r0_rebuilt, foot, cat_mask, sgmc_mask)
    null_dots = proxy.random_null(r0_rebuilt, foot, cat_mask)
    null_proxy = proxy.hide_and_recover(null_dots, cat_mask)
    null_surrogate = proxy.surrogate_dti(null_dots, cat_mask)
    null_sgmc = proxy.sgmc_off_catalogue_control(null_dots, foot, cat_mask, sgmc_mask)

    values = ["alongstrike", "poisson", "lattice"] if args.all else [args.value]
    built_masks: dict[str, np.ndarray] = {}
    reports = []

    for value in values:
        t0 = time.time()
        spec = VARIANTS[value]
        v_mask, stats = spacing.build(
            mode=spec["mode"],
            parent_dots=r0_rebuilt,
            h19_5_mask=h19_mask,
            footprint=foot,
            catalogue_mask=cat_mask,
            seed=SEED,
            det_elev=det_elev,
        )
        built_masks[value] = v_mask

        # Enforce 1-50 % change under both relocation and symmetric-difference conventions
        if not (1.0 <= stats["pct_changed"] <= 50.0 and 1.0 <= stats["pct_symmetric_diff"] <= 50.0):
            print(f"STOP: {value} pct_changed={stats['pct_changed']:.2f}% / sym={stats['pct_symmetric_diff']:.2f}% outside 1-50%")
            return 2
        if stats["added_min_catalogue_clearance_px"] is None or stats["added_min_catalogue_clearance_px"] < 3.0 - 1e-6:
            print(f"STOP: {value} added dots violate d_cat >= 3.0 px: {stats['added_min_catalogue_clearance_px']}")
            return 2

        tmp_nan = ROOT / "releases" / f"_tmp_spacing_{value}_nan.tif"
        tmp_zeros = ROOT / "releases" / f"_tmp_spacing_{value}_zeros.tif"
        tmp_nan.parent.mkdir(parents=True, exist_ok=True)
        grid.write_submission(tmp_nan, v_mask, foot, encoding="nan")
        grid.write_submission(tmp_zeros, v_mask, foot, encoding="zeros")
        sha_nan = grid.sha256_file(tmp_nan)
        sha_zeros = grid.sha256_file(tmp_zeros)
        sha8 = sha_nan[:8]
        rid = f"{parent.PARENT_ID}-spacing-{value}-{DATE}-{sha8}"
        final_nan = ROOT / "releases" / f"{rid}.tif"
        final_zeros = ROOT / "releases" / f"{rid}-zeros.tif"

        # Clean up any stale spacing file for the same value if re-running deterministically
        for old in (ROOT / "releases").glob(f"{parent.PARENT_ID}-spacing-{value}-{DATE}-*.tif"):
            if old not in (final_nan, final_zeros):
                old.unlink()

        tmp_nan.replace(final_nan)
        tmp_zeros.replace(final_zeros)

        nan_arr, _ = grid.read_back(final_nan)
        zeros_arr, _ = grid.read_back(final_zeros)
        dots_nan = np.nan_to_num(nan_arr) > 0
        dots_zeros = zeros_arr > 0

        ok_nan, res_nan = validate.gate_release(
            final_nan,
            contract,
            footprint=foot,
            dots_mask=dots_nan,
            require_nan_outside=True,
            ledger_hashes=ledger_hashes,
            min_clearance_px=0.0,
            clearance_raster=catalogue_raw,
        )
        ok_zeros, res_zeros = validate.gate_release(
            final_zeros,
            contract,
            footprint=foot,
            dots_mask=dots_zeros,
            require_nan_outside=False,
            ledger_hashes=ledger_hashes,
            min_clearance_px=0.0,
            clearance_raster=catalogue_raw,
        )
        twins_equal = bool(np.array_equal(dots_nan, dots_zeros) and np.array_equal(v_mask, dots_nan))
        if not (ok_nan and ok_zeros and twins_equal):
            print(f"STOP: MUST gate failure on {rid}: nan={ok_nan} zeros={ok_zeros} twins={twins_equal}")
            return 2

        ledger_hashes.update({sha_nan, sha_zeros})

        v_proxy = proxy.hide_and_recover(v_mask, cat_mask)
        v_surrogate = proxy.surrogate_dti(v_mask, cat_mask)
        v_sgmc = proxy.sgmc_off_catalogue_control(v_mask, foot, cat_mask, sgmc_mask)

        rep = {
            "id": rid,
            "axis": "SPACING",
            "value": value,
            "spec": spec,
            "git_sha": git_sha(),
            "parent": parent.PARENT_ID,
            "parent_sha256": parent.R0_ZEROS_SHA256,
            "seed": SEED,
            "stats": stats,
            "files": {
                "nan": str(final_nan.relative_to(ROOT)),
                "zeros": str(final_zeros.relative_to(ROOT)),
                "sha256": sha_nan,
                "sha256_zeros": sha_zeros,
                "sha8": sha8,
            },
            "gates": {
                "nan": {"ok": ok_nan, "results": res_nan},
                "zeros": {"ok": ok_zeros, "results": res_zeros},
                "twins_identical_mask": twins_equal,
                "added_dots_dcat_ge_3px": True,
                "pct_changed_in_1_50": True,
            },
            "report_only": {
                "proxy_variant": v_proxy,
                "proxy_parent": parent_proxy,
                "proxy_random_null": null_proxy,
                "sgmc_variant": v_sgmc,
                "sgmc_parent": parent_sgmc,
                "sgmc_random_null": null_sgmc,
                "surrogate_dti_variant": v_surrogate,
                "surrogate_dti_parent": parent_surrogate,
                "surrogate_dti_random_null": null_surrogate,
            },
            "seconds": round(time.time() - t0, 2),
        }
        reports.append(rep)
        print(
            f"[{value}] {rid}  gates=PASS  moved={stats['n_moved']} ({stats['pct_changed']:.2f}% / "
            f"sym {stats['pct_symmetric_diff']:.2f}%)  sgmc_cov={v_sgmc['sgmc_coverage']:.5f}  {rep['seconds']}s"
        )

    if args.all:
        d_cat = distance_transform_edt(~cat_mask)
        elig_h19 = h19_mask & (d_cat >= 3.0) & foot
        jitter = compute_jitter_model_deltas(r0_rebuilt, built_masks, elig_h19, foot, cat_mask)
        for rep in reports:
            vname = rep["value"]
            rep["report_only"]["jitter_model_sensitivity"] = {
                k: {"r0_dti": d["r0_dti"], "delta": d["delta_vs_r0"][vname]}
                for k, d in jitter.items()
            }
            (ROOT / "registry" / f"build_report_spacing_{vname}.json").write_text(
                json.dumps(rep, indent=1) + "\n"
            )
        (ROOT / "registry" / "build_reports_spacing.json").write_text(
            json.dumps(reports, indent=1) + "\n"
        )

        # Also evaluate SGMC on existing RELIEF releases so report_only_status.json is complete
        relief_sgmc = {}
        for rval in ("r10", "r15", "r15s"):
            matches = sorted((ROOT / "releases").glob(f"{parent.PARENT_ID}-relief-{rval}-*-zeros.tif"))
            if matches:
                rm = (grid.read_back(matches[0])[0] > 0) & foot
                relief_sgmc[rval] = proxy.sgmc_off_catalogue_control(rm, foot, cat_mask, sgmc_mask)

        status_doc = {
            "note": "REPORT ONLY. None of these instruments can pass or fail a release; none is a live score.",
            "catalogue_hide_and_recover": {
                "evidence_class": "PROXY",
                "seed": SEED,
                "holdout_fraction": 0.30,
                "n_withheld": parent_proxy["n_withheld"],
                "parent": {
                    "recall": round(parent_proxy["recall"], 6),
                    "ci95": [round(x, 6) for x in parent_proxy["ci95"]],
                },
                "spacing": {
                    r["value"]: {
                        "recall": round(r["report_only"]["proxy_variant"]["recall"], 6),
                        "ci95": [round(x, 6) for x in r["report_only"]["proxy_variant"]["ci95"]],
                    }
                    for r in reports
                },
                "relief": {"r10": 0.0356, "r15": 0.0348, "r15s": 0.0341},
                "random_null": round(null_proxy["recall"], 6),
                "caveat": (
                    "Every relocated dot obeys d_cat >= 3.0 px, and SPACING freezes dots with "
                    "d_cat < 3.0 px plus short (<6-dot) strands; catalogue recall therefore "
                    "measures only near-collar spillover at d_cat == 3.0 px."
                ),
            },
            "sgmc_off_catalogue_control": {
                "evidence_class": "PROXY",
                "source_url": "https://doi.org/10.3133/ds1052",
                "parent": parent_sgmc,
                "spacing": {r["value"]: r["report_only"]["sgmc_variant"] for r in reports},
                "relief": relief_sgmc,
                "random_null": null_sgmc,
            },
            "leakage_canary": (
                f"see registry/leakage_canary.json - PASS, max single-feature strength "
                f"{max_strength:.4f} across 19 bands + scored_h19_5 (threshold 0.90)"
            ),
            "jitter_model_sensitivity": jitter,
        }
        (ROOT / "registry" / "report_only_status.json").write_text(
            json.dumps(status_doc, indent=1) + "\n"
        )
    else:
        for rep in reports:
            (ROOT / "registry" / f"build_report_spacing_{rep['value']}.json").write_text(
                json.dumps(rep, indent=1) + "\n"
            )

    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
