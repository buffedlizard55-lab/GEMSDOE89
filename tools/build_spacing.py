#!/usr/bin/env python3
"""Build the three SPACING variants of verified parent R0 (h33-h33-2-b2).

Usage:
    python tools/build_spacing.py --all
    python tools/build_spacing.py --value strike

Each run:
  1. Verifies every pinned input against registry/data_manifest.json (sha256 + bytes).
  2. Verifies parent R0 against its pinned sha256 (c55bafc4... / baeae321...).
  3. Runs the single-feature leakage canary (stops if any feature has AUC > 0.90).
  4. Prepares the shared 610-corridor ridge manifold from scored_h19_5 (d_cat >= 3 px).
  5. Builds each requested SPACING variant ('strike', 'poisson', 'lattice') at exact
     per-corridor and global dot count (37,654).
  6. Writes releases/<id>.tif (NaN outside) and releases/<id>-zeros.tif (0 outside),
     re-reads both from disk, and runs all MUST gates.
  7. Computes all REPORT-ONLY instruments (catalogue hide-and-recover, leakage canary,
     off-catalogue SGMC control, surrogate DTI) and writes registry JSON receipts.
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
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe import grid, metric, proxy, relief, spacing, validate  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
PARENT_SHA256 = "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
PARENT_NAN_SHA256 = "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd"
DATE = "20261023"
SEED = 20261023

VARIANTS = {
    "strike": {
        "mode": "strike",
        "note": (
            "anisotropic along-strike crest-first spacing (r_along=2.0 px, r_across=4.2 px) "
            "inside R0's 610 widest multi-dot fault corridors, exact per-corridor count preserved"
        ),
        "predicted_change": "+0.006 (MODEL; band -0.004..+0.011). Crest-localized 1-D fault truth favors strike.",
        "form_note": (
            "h33-h33-2-b2; SPACING strike (5444/37654=14.46% along-strike on H19 crest, "
            "dcat>=3px); pred +0.006 (-0.004..+0.011)"
        ),
        "recommend": "SLOT 1 (primary). Highest crest kernel gain (+1119 units); tests 1-D fault-trace crest mechanism.",
    },
    "poisson": {
        "mode": "poisson",
        "note": (
            "isotropic farthest-point (Poisson-disk) + discrete Voronoi/Lloyd relaxation "
            "inside R0's 610 widest multi-dot fault corridors, exact per-corridor count preserved"
        ),
        "predicted_change": "+0.001 (MODEL; band -0.002..+0.004). Isotropic 2-D corridor covering benchmark.",
        "form_note": (
            "h33-h33-2-b2; SPACING poisson (4800/37654=12.75% Voronoi/Poisson on H19, "
            "dcat>=3px); pred +0.001 (-0.002..+0.004)"
        ),
        "recommend": "SLOT 2 (control if strike moves >=0.010 or to separate 2-D corridor scatter vs 1-D crest).",
    },
    "lattice": {
        "mode": "lattice",
        "note": (
            "hexagonal covering-lattice snapping (pitch a=3.20 px) "
            "inside R0's 610 widest multi-dot fault corridors, exact per-corridor count preserved"
        ),
        "predicted_change": "0.000 (MODEL; band -0.003..+0.003). Periodic hex-lattice control on H19 manifold.",
        "form_note": (
            "h33-h33-2-b2; SPACING lattice (5195/37654=13.80% hex-lattice a=3.2px on H19, "
            "dcat>=3px); pred 0.000 (-0.003..+0.003)"
        ),
        "recommend": "HOLD / crystallographic covering control (do not spend a weekly slot unless both strike and poisson move).",
    },
}


def _git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def verify_inputs(manifest: dict, data_root: Path) -> dict:
    report = {}
    for f in manifest["files"]:
        path = data_root / f["local"]
        if not path.exists():
            report[f["id"]] = {"present": False, "ok": False}
            continue
        sha = grid.sha256_file(path)
        size = path.stat().st_size
        report[f["id"]] = {
            "present": True,
            "ok": sha == f["sha256"] and size == f["bytes"],
            "sha256": sha,
            "expected": f["sha256"],
            "bytes": size,
        }
    return report


def prior_ledger_hashes(path: Path, exclude_axis: str = "SPACING") -> set[str]:
    if not path.exists():
        return set()
    out: set[str] = set()
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("source") == "GEMSDOE89" and (row.get("axis") or "").upper() == exclude_axis:
                continue
            for k in ("sha256", "sha256_zeros"):
                v = (row.get(k) or "").strip()
                if v:
                    out.add(v)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--value", choices=sorted(VARIANTS), default=None)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if not args.all and args.value is None:
        ap.error("give --value or --all")

    manifest = json.loads((ROOT / "registry" / "data_manifest.json").read_text())
    data_root = Path(
        os.environ.get(
            manifest.get("data_root_env", "GEMSDOE_DATA"),
            ROOT / manifest.get("data_root_default", "data"),
        )
    )
    ver = verify_inputs(manifest, data_root)
    bad = {k: v for k, v in ver.items() if not v.get("ok")}
    if bad:
        print(json.dumps({"ERROR": "pinned inputs failed verification", "detail": bad}, indent=1))
        return 2
    print(f"[ok] verified all {len(ver)} manifest hashes")

    paths = {f["id"]: data_root / f["local"] for f in manifest["files"]}
    assert grid.sha256_file(paths["parent_r0_zeros"]) == PARENT_SHA256
    assert grid.sha256_file(paths["parent_r0_nan"]) == PARENT_NAN_SHA256

    parent = grid.read_back(paths["parent_r0_zeros"])[0]
    parent_dots = parent > 0
    sample, contract = grid.read_template(paths["sample_submission"])
    footprint = np.isfinite(sample)
    del sample
    catalogue = grid.read_back(paths["existing_faults"])[0]
    cat_mask = (catalogue > 0) & footprint
    h19_arr = grid.read_back(paths["scored_h19_5"])[0]
    ridge_mask = (np.nan_to_num(h19_arr, nan=0.0) > 0) & footprint
    sgmc_arr = grid.read_back(paths["ext_derived_sgmc_faults_100m_u8"])[0]
    sgmc_mask = (sgmc_arr > 0) & footprint

    assert int(parent_dots.sum()) == 37_654
    assert int((parent_dots & ridge_mask).sum()) == 37_654, "parent dots must lie on scored_h19_5"
    print(f"[ok] parent R0 verified: 37,654 dots (100% on scored_h19_5)")

    # Prepare shared corridor manifold & orientation
    ctx = spacing.prepare_manifold(ridge_mask, parent_dots, cat_mask, footprint)
    print(
        f"[ok] prepared {len(ctx.chosen_corridors)} corridors "
        f"({int((parent_dots & ctx.in_repack).sum())} R0 dots in {int(ctx.in_repack.sum())} manifold px)"
    )

    # Leakage canary across both RELIEF bands and SPACING ridge fields
    raw_bands = relief.stream_bands(paths["training_features"], [12, 19])
    det_elev = raw_bands[12]
    det_slope = raw_bands[19]
    del raw_bands
    domain = footprint & np.isfinite(det_elev) & np.isfinite(det_slope)
    elev_cls, _ = relief.define_classes(det_elev, domain)
    f_det = np.nan_to_num(det_elev.astype(np.float32), nan=0.0)
    gy, gx = np.gradient(f_det)
    abs_grad = np.where(footprint, np.hypot(gy, gx), np.nan)
    del f_det, gy, gx

    canary_inputs = {
        "det_elev": det_elev,
        "det_elev_slope": det_slope,
        "elev_class": np.where(domain, elev_cls.astype(np.float32), np.nan),
        "abs_elev_gradient": abs_grad,
        "scored_h19_5": np.where(footprint, ridge_mask.astype(np.float32), np.nan),
        "h19_centrality_s1p5": np.where(footprint, ctx.centrality, np.nan),
        "h19_strike_coherence": np.where(footprint, ctx.coherence, np.nan),
    }
    canary_res = proxy.canary(canary_inputs, cat_mask, threshold=0.90)
    del det_elev, det_slope, elev_cls, abs_grad, canary_inputs
    flagged = [k for k, v in canary_res.items() if v["flag"]]
    canary_doc = {
        "instrument": "leakage canary (single-feature AUC vs catalogue membership)",
        "threshold": 0.9,
        "sample_px": 400000,
        "seed": 11,
        "features": canary_res,
        "verdict": (
            "PASS: no single feature exceeds the canary threshold"
            if not flagged else f"STOP: flagged {flagged}"
        ),
        "note": (
            "REPORT ONLY. AUC close to 0.5 means the feature carries little catalogue "
            "information alone; AUC > 0.90 triggers an immediate stop."
        ),
    }
    (ROOT / "registry" / "leakage_canary.json").write_text(json.dumps(canary_doc, indent=1) + "\n")
    if flagged:
        print(f"[STOP] leakage canary flagged {flagged}")
        return 2
    max_auc = max(max(v["auc"], 1.0 - v["auc"]) for v in canary_res.values())
    print(f"[ok] leakage canary PASS (max |AUC| = {max_auc:.3f} <= 0.90)")

    # Report-only baselines on R0 and random null
    d_cat = ndi.distance_transform_edt(~cat_mask)
    parent_proxy = proxy.hide_and_recover(parent_dots, cat_mask)
    parent_surrogate = proxy.surrogate_dti(parent_dots, cat_mask)
    parent_sgmc = proxy.sgmc_off_catalogue(parent_dots, sgmc_mask, cat_mask, footprint)
    null_dots = proxy.random_null(parent_dots, footprint, cat_mask)
    null_proxy = proxy.hide_and_recover(null_dots, cat_mask)
    null_surrogate = proxy.surrogate_dti(null_dots, cat_mask)
    null_sgmc = proxy.sgmc_off_catalogue(null_dots, sgmc_mask, cat_mask, footprint)

    known_hashes = prior_ledger_hashes(ROOT / "ledger" / "submissions.csv", exclude_axis="SPACING")

    # Remove old SPACING release files if rebuilding
    for old_f in (ROOT / "releases").glob(f"{PARENT_ID}-spacing-*.tif"):
        old_f.unlink()

    values = ["strike", "poisson", "lattice"] if args.all else [args.value]
    reports = []
    git_sha = _git_sha()

    for value in values:
        spec = VARIANTS[value]
        assert len(spec["form_note"]) <= 140, f"{value} form_note > 140 chars"
        t0 = time.time()
        rng = np.random.default_rng(SEED)
        variant_dots, stats = spacing.build(
            mode=spec["mode"],
            ctx=ctx,
            parent_dots=parent_dots,
            footprint=footprint,
            rng=rng,
        )

        # Write both twins deterministically, hash, and rename
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

        # Re-read from disk and run MUST gates
        nan_arr, _ = grid.read_back(final_nan)
        zeros_arr, _ = grid.read_back(final_zeros)
        dots_read_nan = np.nan_to_num(nan_arr) > 0
        dots_read_zeros = zeros_arr > 0

        ok_nan, res_nan = validate.gate_release(
            final_nan, contract, footprint=footprint, dots_mask=dots_read_nan,
            require_nan_outside=True, ledger_hashes=known_hashes,
            min_clearance_px=0.0, clearance_raster=catalogue,
        )
        ok_zeros, res_zeros = validate.gate_release(
            final_zeros, contract, footprint=footprint, dots_mask=dots_read_zeros,
            require_nan_outside=False, ledger_hashes=known_hashes,
            min_clearance_px=0.0, clearance_raster=catalogue,
        )
        known_hashes.add(sha_nan)
        known_hashes.add(sha_zeros)

        added = variant_dots & ~parent_dots
        removed = parent_dots & ~variant_dots
        added_min_clear = float(d_cat[added].min()) if added.any() else None
        added_clear_ok = added_min_clear is not None and added_min_clear >= 3.0 - 1e-6
        support_ok = bool(not (variant_dots & ~ridge_mask).any())
        pct_ok = 1.0 <= stats["pct_changed"] <= 50.0 and 1.0 <= stats["pct_symmetric_diff"] <= 50.0
        twins_equal = (
            bool(np.array_equal(dots_read_nan, dots_read_zeros))
            and bool(np.array_equal(variant_dots, dots_read_nan))
        )

        all_gates_ok = ok_nan and ok_zeros and added_clear_ok and support_ok and pct_ok and twins_equal
        if not all_gates_ok:
            raise RuntimeError(
                f"Gate failure on {rid}: nan={ok_nan}, zeros={ok_zeros}, "
                f"added_clear={added_min_clear}, support={support_ok}, pct={pct_ok}, twins={twins_equal}"
            )

        # Report-only instruments
        v_proxy = proxy.hide_and_recover(variant_dots, cat_mask)
        v_surrogate = proxy.surrogate_dti(variant_dots, cat_mask)
        v_sgmc = proxy.sgmc_off_catalogue(variant_dots, sgmc_mask, cat_mask, footprint)
        k_add = metric.kernel_weight(d_cat[added])

        model = {
            "added_dots": int(added.sum()),
            "removed_dots": int(removed.sum()),
            "added_min_clearance_px": added_min_clear,
            "all_dots_on_scored_h19_5": support_ok,
            "added_frac_within_kernel_of_catalogue": float((k_add > 0).mean()) if added.any() else None,
            "t_crest_delta_units": stats["t_crest_delta"],
            "t_manifold_delta_units": stats["t_manifold_delta"],
            "crest_dots_delta": stats["crest_dots_after"] - stats["crest_dots_before"],
            "across_strike_twins_delta": stats["across_strike_twins_after"] - stats["across_strike_twins_before"],
            "pays_threshold_at_parent_dti": metric.pays_threshold(0.2778),
            "inherited_dots_below_3px_of_catalogue": int((d_cat[variant_dots] < 3.0).sum()),
            "parent_min_clearance_px": float(d_cat[parent_dots].min()),
        }

        rep = {
            "id": rid,
            "axis": "SPACING",
            "value": value,
            "spec": spec,
            "parent": PARENT_ID,
            "parent_sha256": PARENT_SHA256,
            "git_sha": git_sha,
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
                "added_clearance_ge_3px": added_clear_ok,
                "all_dots_on_h19_5_support": support_ok,
                "pct_changed_in_1_50": pct_ok,
                "twins_identical_mask": twins_equal,
            },
            "report_only": {
                "proxy_variant": v_proxy,
                "proxy_parent": parent_proxy,
                "proxy_random_null": null_proxy,
                "sgmc_off_catalogue_variant": v_sgmc,
                "sgmc_off_catalogue_parent": parent_sgmc,
                "sgmc_off_catalogue_random_null": null_sgmc,
                "surrogate_dti_variant": v_surrogate,
                "surrogate_dti_parent": parent_surrogate,
                "surrogate_dti_random_null": null_surrogate,
                "model_inputs": model,
            },
            "seconds": round(time.time() - t0, 2),
        }
        (ROOT / "registry" / f"build_report_spacing_{value}.json").write_text(
            json.dumps(rep, indent=1) + "\n"
        )
        reports.append(rep)
        print(
            f"[{value:7s}] {rid}  gates=PASS  moved={stats['n_moved']} ({stats['pct_changed']:.2f}% / "
            f"sym {stats['pct_symmetric_diff']:.2f}%)  dT_crest={stats['t_crest_delta']:+.1f}  "
            f"dT_manif={stats['t_manifold_delta']:+.1f}  sgmc_rec={v_sgmc['recall_within_3px']:.4f}  "
            f"({rep['seconds']}s)"
        )

    if args.all:
        (ROOT / "registry" / "build_reports_spacing.json").write_text(
            json.dumps(reports, indent=1) + "\n"
        )
        # Also compute SGMC on the existing RELIEF variants so report_only_status.json is complete
        relief_sgmc = {}
        relief_reports = json.loads((ROOT / "registry" / "build_reports.json").read_text())
        for rr in relief_reports:
            r_arr = grid.read_back(ROOT / rr["files"]["zeros"])[0]
            relief_sgmc[rr["value"]] = proxy.sgmc_off_catalogue(
                r_arr > 0, sgmc_mask, cat_mask, footprint
            )

        status_doc = {
            "note": "REPORT ONLY. None of these instruments can pass or fail a release, and none is a live score.",
            "catalogue_hide_and_recover": {
                "seed": SEED,
                "holdout_fraction": 0.30,
                "n_withheld": parent_proxy["n_withheld"],
                "parent_recall": round(parent_proxy["recall"], 4),
                "spacing_strike": round(reports[0]["report_only"]["proxy_variant"]["recall"], 4),
                "spacing_poisson": round(reports[1]["report_only"]["proxy_variant"]["recall"], 4),
                "spacing_lattice": round(reports[2]["report_only"]["proxy_variant"]["recall"], 4),
                "relief_r10": 0.0356,
                "relief_r15": 0.0348,
                "relief_r15s": 0.0341,
                "random_null": round(null_proxy["recall"], 4),
                "ci": "Wilson 95% computed per file in registry/build_report_*.json",
                "caveat": (
                    "Every newly placed dot has d_cat >= 3.0 px by construction, so hide-and-recover "
                    "cannot credit newly placed dots and only registers the untouched near-collar dots "
                    "(constant 0.0384 across all SPACING variants because SPACING locks d_cat < 3.0 dots "
                    "and only respaces d_cat >= 3.0 corridors)."
                ),
            },
            "sgmc_control": {
                "status": "RUN (REPORT ONLY)",
                "source": "USGS State Geologic Map Compilation (Horton et al., 2017, https://doi.org/10.3133/ds1052, public domain)",
                "n_sgmc_offcat_px": parent_sgmc["n_sgmc_offcat_px"],
                "clearance_from_catalogue_px": 3.0,
                "recall_within_3px": {
                    "parent_r0": round(parent_sgmc["recall_within_3px"], 4),
                    "spacing_strike": round(reports[0]["report_only"]["sgmc_off_catalogue_variant"]["recall_within_3px"], 4),
                    "spacing_poisson": round(reports[1]["report_only"]["sgmc_off_catalogue_variant"]["recall_within_3px"], 4),
                    "spacing_lattice": round(reports[2]["report_only"]["sgmc_off_catalogue_variant"]["recall_within_3px"], 4),
                    "relief_r10": round(relief_sgmc["r10"]["recall_within_3px"], 4),
                    "relief_r15": round(relief_sgmc["r15"]["recall_within_3px"], 4),
                    "relief_r15s": round(relief_sgmc["r15s"]["recall_within_3px"], 4),
                    "random_null": round(null_sgmc["recall_within_3px"], 4),
                },
                "surrogate_dti_sgmc_offcat": {
                    "parent_r0": round(parent_sgmc["surrogate_dti_sgmc_offcat"], 5),
                    "spacing_strike": round(reports[0]["report_only"]["sgmc_off_catalogue_variant"]["surrogate_dti_sgmc_offcat"], 5),
                    "spacing_poisson": round(reports[1]["report_only"]["sgmc_off_catalogue_variant"]["surrogate_dti_sgmc_offcat"], 5),
                    "spacing_lattice": round(reports[2]["report_only"]["sgmc_off_catalogue_variant"]["surrogate_dti_sgmc_offcat"], 5),
                    "relief_r10": round(relief_sgmc["r10"]["surrogate_dti_sgmc_offcat"], 5),
                    "relief_r15": round(relief_sgmc["r15"]["surrogate_dti_sgmc_offcat"], 5),
                    "relief_r15s": round(relief_sgmc["r15s"]["surrogate_dti_sgmc_offcat"], 5),
                    "random_null": round(null_sgmc["surrogate_dti_sgmc_offcat"], 5),
                },
                "caveat": (
                    "1:500k bedrock SGMC faults are mostly pre-Quaternary structures; upstream SGMC-only "
                    "submissions scored 0.0492-0.0512 live. Reported strictly as a structural sanity control "
                    "(all H19-supported variants sit ~1.29x above random null on surrogate DTI); never used as a gate or target."
                ),
            },
            "leakage_canary": (
                f"see registry/leakage_canary.json - PASS, max |AUC| {max_auc:.3f} (threshold 0.90)"
            ),
            "block_density_cv": {
                "definition_1km": "1 km x 1 km blocks (10 x 10 px), density = dots / footprint px, blocks with >=50% footprint",
                "definition_5km": "5 km x 5 km blocks (50 x 50 px), density = dots / footprint px, blocks with >=50% footprint",
                "parent_1km": round(reports[0]["stats"]["block_cv_before"], 4),
                "spacing_strike_1km": round(reports[0]["stats"]["block_cv_after"], 4),
                "spacing_poisson_1km": round(reports[1]["stats"]["block_cv_after"], 4),
                "spacing_lattice_1km": round(reports[2]["stats"]["block_cv_after"], 4),
                "parent_5km": round(reports[0]["stats"]["block_cv_5km_before"], 4),
                "spacing_strike_5km": round(reports[0]["stats"]["block_cv_5km_after"], 4),
                "spacing_poisson_5km": round(reports[1]["stats"]["block_cv_5km_after"], 4),
                "spacing_lattice_5km": round(reports[2]["stats"]["block_cv_5km_after"], 4),
            },
        }
        (ROOT / "registry" / "report_only_status.json").write_text(
            json.dumps(status_doc, indent=1) + "\n"
        )

    print("[done] SPACING build complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
