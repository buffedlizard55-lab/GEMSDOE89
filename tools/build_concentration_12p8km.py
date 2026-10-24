#!/usr/bin/env python3
"""Build the three CONCENTRATION variants of verified Parent R0 (h33-h33-2-b2).

Usage:
    python tools/build_concentration.py --value 12p8km-int10
    python tools/build_concentration.py --all

Start gates (brief sec.5):
  1. Re-hash every fetchable pinned input in registry/data_manifest.json.
  2. Rebuild Parent R0 (37,654 unit-mass dots) bit-for-bit from scored_h19_5.tif
     via dot_thin(r=2.8) + (d_cat > 2.0) and verify exact mask + parent SHA-256.
  3. Run single-feature leakage canary across all bands read + corrob_ridge
     (stop if any feature strength > 0.90).

Variants built (AXIS = CONCENTRATION, 12.8 km = 128 px half-tile blocks):
  * 12p8km-int10  : move 10.00 % (3,765 dots) low -> high Faulds interaction blocks
  * 12p8km-int20  : move 20.00 % (7,531 dots) low -> high Faulds interaction blocks (2x dose)
  * 12p8km-geod15 : move 15.00 % (5,648 dots) low -> high GPS strain + seismicity blocks
                    (catalogue-free tectonic deformation prior)

Each variant writes releases/<id>.tif (NaN outside) and <id>-zeros.tif, re-reads
both from disk, passes all MUST gates, updates ledger/submissions.csv idempotently,
and writes registry/build_report_conc_<value>.json + build_reports_concentration.json.
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

from gemsdoe import concentration_12p8km as concentration, grid, metric, parent, proxy, relief, validate  # noqa: E402

DATE = "20261023"
HOLD_SEEDS = (20261023, 7, 42)

VARIANTS = {
    "12p8km-int10": {
        "prior": "interaction",
        "fraction": 0.10,
        "role": "PRIMARY",
        "pred_central": 0.008,
        "pred_band": [-0.006, 0.018],
        "predicted_change_text": (
            "+0.008 (MODEL; band -0.006..+0.018; 3-seed strand-holdout +0.0040 at 0.106 base, "
            "+0.0052 lift over random-block shuffle)"
        ),
        "note": (
            "move 10% (3,765 dots) from lowest-40% to highest-40% Faulds fault-interaction "
            "12.8 km blocks, keeping CV12.8km inside the 0.51-0.59 reference band"
        ),
    },
    "12p8km-int20": {
        "prior": "interaction",
        "fraction": 0.20,
        "role": "DOSE",
        "pred_central": 0.009,
        "pred_band": [-0.014, 0.024],
        "predicted_change_text": (
            "+0.009 (MODEL; band -0.014..+0.024; 2x dose pushes CV12.8km 0.553->0.656 above 0.59 "
            "to test linear gain vs secondary-ridge saturation; +0.0051 strand-holdout)"
        ),
        "note": (
            "move 20% (7,531 dots) along the same 12.8 km fault-interaction block prior "
            "(2x dose-response arm)"
        ),
    },
    "12p8km-geod15": {
        "prior": "geodetic",
        "fraction": 0.15,
        "role": "DISCRIMINATOR",
        "pred_central": 0.003,
        "pred_band": [-0.015, 0.021],
        "predicted_change_text": (
            "+0.003 (MODEL; band -0.015..+0.021; catalogue-free GPS shear/strain + seismicity "
            "12.8 km block prior; +0.0038 lift over random-block shuffle)"
        ),
        "note": (
            "move 15% (5,648 dots) from lowest-40% to highest-40% active crustal deformation "
            "(geod_2ndinv + geod_shearrate + ieq_n100a15) 12.8 km blocks (zero catalogue prior)"
        ),
    },
}


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
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


def existing_ledger_state(ledger_path: Path, exclude_values: set[str]) -> tuple[set[str], set[tuple[str, str, str]]]:
    hashes: set[str] = set()
    triples: set[tuple[str, str, str]] = set()
    if not ledger_path.exists():
        return hashes, triples
    with open(ledger_path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            is_self = (
                row.get("source") == "GEMSDOE89"
                and (row.get("axis") or "").strip().upper() == "CONCENTRATION"
                and (row.get("value") or "").strip() in exclude_values
            )
            if is_self:
                continue
            for col in ("sha256", "sha256_zeros"):
                v = (row.get(col) or "").strip()
                if v:
                    hashes.add(v)
            triples.add(
                (
                    (row.get("parent") or "").strip(),
                    (row.get("axis") or "").strip().upper(),
                    (row.get("value") or "").strip(),
                )
            )
    return hashes, triples


def run_strand_holdout_calibration(
    cat_mask: np.ndarray,
    d28_mask: np.ndarray,
    h19_mask: np.ndarray,
    foot: np.ndarray,
    corrob: np.ndarray,
    geod_blk: np.ndarray,
) -> dict:
    """Out-of-sample 3-seed strand holdout + matched random-block-shuffle control (MODEL/PROXY)."""
    lbl_all, n_all = ndi.label(cat_mask, structure=np.ones((3, 3), dtype=np.int8))
    b_id, _bh, _bw, n_blocks = concentration.block_grid(foot.shape, concentration.BLOCK_PX)
    foot_cnt = np.bincount(b_id[foot], minlength=n_blocks)
    active_blk = foot_cnt > 0

    shuf_blk = np.zeros(n_blocks, dtype=np.float64)
    shuf_blk[active_blk] = np.random.default_rng(999).random(int(active_blk.sum()))

    per_seed = {}
    for seed in HOLD_SEEDS:
        rng = np.random.default_rng(seed)
        hold = rng.random(n_all + 1) < 0.25
        hold[0] = False
        cat_known = cat_mask & (~hold[lbl_all])
        g_withheld = cat_mask & hold[lbl_all] & (~cat_known)
        d_known = ndi.distance_transform_edt(~cat_known)
        r0_sim = d28_mask & (d_known > 2.0) & foot & (~cat_known)
        base_dti = metric.dti(g_withheld, r0_sim)

        # Interaction prior built ONLY from cat_known (zero leakage from g_withheld)
        int_known, _ = concentration.interaction_block_prior(cat_known, foot)

        deltas = {}
        for vname, spec in VARIANTS.items():
            b_sc = int_known if spec["prior"] == "interaction" else geod_blk
            v_sim, _ = concentration.build(
                parent_dots=r0_sim,
                footprint=foot,
                catalogue_mask=cat_known,
                blk_score=b_sc,
                corrob_ridge=corrob,
                h19_5_mask=h19_mask,
                fraction=spec["fraction"],
            )
            deltas[vname] = round(metric.dti(g_withheld, v_sim) - base_dti, 6)

        shuf_deltas = {}
        for frac in (0.10, 0.15, 0.20):
            v_shuf, _ = concentration.build(
                parent_dots=r0_sim,
                footprint=foot,
                catalogue_mask=cat_known,
                blk_score=shuf_blk,
                corrob_ridge=corrob,
                h19_5_mask=h19_mask,
                fraction=frac,
            )
            shuf_deltas[f"frac_{frac:.2f}"] = round(metric.dti(g_withheld, v_shuf) - base_dti, 6)

        per_seed[f"seed_{seed}"] = {
            "withheld_fault_px": int(g_withheld.sum()),
            "r0_sim_dots": int(r0_sim.sum()),
            "r0_sim_dti": round(base_dti, 6),
            "variant_delta_dti": deltas,
            "random_block_shuffle_delta_dti": shuf_deltas,
        }

    mean_deltas = {
        vname: round(
            float(np.mean([per_seed[f"seed_{s}"]["variant_delta_dti"][vname] for s in HOLD_SEEDS])),
            6,
        )
        for vname in VARIANTS
    }
    mean_shuf = {
        f"frac_{frac:.2f}": round(
            float(np.mean([per_seed[f"seed_{s}"]["random_block_shuffle_delta_dti"][f"frac_{frac:.2f}"] for s in HOLD_SEEDS])),
            6,
        )
        for frac in (0.10, 0.15, 0.20)
    }
    return {
        "evidence_class": "MODEL",
        "protocol": (
            "Withhold 25% of 8-connected catalogue fault strands BEFORE computing d_cat, R0, "
            "or the interaction block prior; score DTI strictly on withheld strands. Matched "
            "random_block_shuffle uses the identical corrob_ridge operator with shuffled 12.8 km "
            "block scores to isolate the km-scale block prior from within-block placement."
        ),
        "mean_variant_delta_dti": mean_deltas,
        "mean_random_block_shuffle_delta_dti": mean_shuf,
        "pure_block_prior_lift_over_shuffle": {
            "12p8km-int10": round(mean_deltas["12p8km-int10"] - mean_shuf["frac_0.10"], 6),
            "12p8km-int20": round(mean_deltas["12p8km-int20"] - mean_shuf["frac_0.20"], 6),
            "12p8km-geod15": round(mean_deltas["12p8km-geod15"] - mean_shuf["frac_0.15"], 6),
        },
        "seeds": per_seed,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--value", choices=sorted(VARIANTS), default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--skip-strand-holdout", action="store_true")
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
    print(f"[ok] verified all {len(paths)} fetchable manifest sha256 pins")

    # ---- Start gate: rebuild R0 and verify byte-exact identity --------------
    sample_arr, contract = grid.read_template(paths["sample_submission"])
    foot = np.isfinite(sample_arr)
    del sample_arr

    catalogue_raw = grid.read_back(paths["existing_faults"])[0]
    cat_mask = (np.isfinite(catalogue_raw) & (catalogue_raw > 0)) & foot
    h19_raw = grid.read_back(paths["scored_h19_5"])[0]
    h19_mask = (np.isfinite(h19_raw) & (h19_raw > 0)) & foot
    d28_raw = grid.read_back(paths["parent_ancestor_d28"])[0]
    d28_pin = (np.isfinite(d28_raw) & (d28_raw > 0)) & foot
    r0_pin = (grid.read_back(paths["parent_r0_zeros"])[0] > 0) & foot

    if grid.sha256_file(paths["parent_r0_zeros"]) != parent.R0_ZEROS_SHA256:
        print("STOP: parent_r0_zeros sha256 mismatch")
        return 2
    if grid.sha256_file(paths["parent_r0_nan"]) != parent.R0_NAN_SHA256:
        print("STOP: parent_r0_nan sha256 mismatch")
        return 2
    r0_rebuilt, d28_rebuilt = parent.rebuild_r0_mask(h19_mask, foot, cat_mask)
    if not (
        np.array_equal(d28_rebuilt, d28_pin)
        and np.array_equal(r0_rebuilt, r0_pin)
        and int(r0_rebuilt.sum()) == parent.EXPECTED_R0_DOTS
    ):
        print("STOP: rebuilt R0 mask mismatch against pinned parent")
        return 2
    print(f"[ok] rebuilt R0 mask bit-exact ({int(r0_rebuilt.sum())} unit-mass dots)")

    # ---- Stream required bands & run leakage canary -------------------------
    need_bands = sorted(set(concentration.RIDGE_BANDS) | set(concentration.GEOD_BANDS))
    bands = relief.stream_bands(paths["training_features"], need_bands)
    for b in need_bands:
        bands[b][~foot | (bands[b] <= -1e30)] = np.nan

    corrob, corrob_diag = concentration.corroborated_ridge_response(bands, foot)
    int_blk, int_diag = concentration.interaction_block_prior(cat_mask, foot)
    geod_blk, geod_diag = concentration.geodetic_block_prior(bands, foot)

    band_tags = manifest["files"][0]["verified_band_tags"]
    canary_feats = {f"b{b:02d}_{band_tags[str(b)]}": bands[b] for b in need_bands}
    canary_feats["corrob_ridge"] = np.where(foot, corrob, np.nan)
    can_res = proxy.canary(canary_feats, cat_mask, threshold=0.90)
    if any(v["flag"] for v in can_res.values()):
        print("STOP: leakage canary triggered (> 0.90)!", can_res)
        return 2
    max_can = max(max(v["auc"], 1.0 - v["auc"]) for v in can_res.values() if v["auc"] is not None)
    print(f"[ok] leakage canary PASS across read bands + corrob_ridge (max strength={max_can:.4f} <= 0.90)")

    # Lineage 12.8 km block-density CV audit (brief sec.5: best files sit at 0.51-0.59)
    solo_mask = (grid.read_back(paths["scored_h27_4_solo"])[0] > 0) & foot
    lineage_cv_12p8km = {
        "d28_44090_0p2600_CLAIM": round(relief.block_density_cv(d28_pin, foot, block=concentration.BLOCK_PX), 4),
        "solo_d28_40199_0p2708_CLAIM": round(relief.block_density_cv(solo_mask, foot, block=concentration.BLOCK_PX), 4),
        "r0_h33_2_b2_37654_0p2778_CLAIM": round(relief.block_density_cv(r0_rebuilt, foot, block=concentration.BLOCK_PX), 4),
    }
    print(f"[audit] lineage 12.8 km block-density CV: {lineage_cv_12p8km}")

    values = ["12p8km-int10", "12p8km-int20", "12p8km-geod15"] if args.all else [args.value]
    ledger_path = ROOT / "ledger" / "submissions.csv"
    ledger_hashes, ledger_triples = existing_ledger_state(ledger_path, exclude_values=set(values))

    parent_proxy = proxy.hide_and_recover(r0_rebuilt, cat_mask)
    parent_surrogate = proxy.surrogate_dti(r0_rebuilt, cat_mask)
    null_dots = proxy.random_null(r0_rebuilt, foot, cat_mask)
    null_proxy = proxy.hide_and_recover(null_dots, cat_mask)
    null_surrogate = proxy.surrogate_dti(null_dots, cat_mask)

    holdout_cal = None
    if args.all and not args.skip_strand_holdout:
        t_h = time.time()
        holdout_cal = run_strand_holdout_calibration(
            cat_mask=cat_mask,
            d28_mask=d28_rebuilt,
            h19_mask=h19_mask,
            foot=foot,
            corrob=corrob,
            geod_blk=geod_blk,
        )
        print(
            f"[model] 3-seed strand-holdout deltas={holdout_cal['mean_variant_delta_dti']} "
            f"lift_over_shuffle={holdout_cal['pure_block_prior_lift_over_shuffle']} ({time.time()-t_h:.1f}s)"
        )

    reports = []
    new_rows = []

    for value in values:
        t0 = time.time()
        spec = VARIANTS[value]
        triple = (parent.PARENT_ID, "CONCENTRATION", value)
        if triple in ledger_triples:
            print(f"STOP: duplicate (parent, axis, value) in upstream ledger: {triple}")
            return 2

        blk_score = int_blk if spec["prior"] == "interaction" else geod_blk
        prior_diag = int_diag if spec["prior"] == "interaction" else geod_diag

        v_mask, stats = concentration.build(
            parent_dots=r0_rebuilt,
            footprint=foot,
            catalogue_mask=cat_mask,
            blk_score=blk_score,
            corrob_ridge=corrob,
            h19_5_mask=h19_mask,
            fraction=spec["fraction"],
            det_elev=bands[12],
        )

        # Hard range and clearance assertions before writing
        if not (1.0 <= stats["pct_changed"] <= 50.0 and 1.0 <= stats["pct_symmetric_diff"] <= 50.0):
            print(f"STOP: {value} pct_changed={stats['pct_changed']} / sym={stats['pct_symmetric_diff']} outside 1-50%")
            return 2
        if stats["added_min_catalogue_clearance_px"] is None or stats["added_min_catalogue_clearance_px"] < 3.0 - 1e-6:
            print(f"STOP: {value} added dots violate d_cat >= 3.0 px")
            return 2
        if stats["collar_lt3px_after"] != stats["collar_lt3px_before"]:
            print(f"STOP: {value} modified <3 px collar count")
            return 2

        tmp_nan = ROOT / "releases" / f"_tmp_conc_{value}_nan.tif"
        tmp_zeros = ROOT / "releases" / f"_tmp_conc_{value}_zeros.tif"
        tmp_nan.parent.mkdir(parents=True, exist_ok=True)
        grid.write_submission(tmp_nan, v_mask, foot, encoding="nan")
        grid.write_submission(tmp_zeros, v_mask, foot, encoding="zeros")
        sha_nan = grid.sha256_file(tmp_nan)
        sha_zeros = grid.sha256_file(tmp_zeros)
        sha8 = sha_nan[:8]
        rid = f"{parent.PARENT_ID}-conc-{value}-{DATE}-{sha8}"
        final_nan = ROOT / "releases" / f"{rid}.tif"
        final_zeros = ROOT / "releases" / f"{rid}-zeros.tif"

        for old in (ROOT / "releases").glob(f"{parent.PARENT_ID}-conc-{value}-{DATE}-*.tif"):
            if old not in (final_nan, final_zeros):
                old.unlink()

        tmp_nan.replace(final_nan)
        tmp_zeros.replace(final_zeros)

        # Re-read from disk and run all MUST gates
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
            for r in res_nan + res_zeros:
                if not r["ok"]:
                    print("   FAILED GATE:", r)
            return 2

        ledger_hashes.update({sha_nan, sha_zeros})
        ledger_triples.add(triple)

        v_proxy = proxy.hide_and_recover(v_mask, cat_mask)
        v_surrogate = proxy.surrogate_dti(v_mask, cat_mask)

        prior_short = "interaction" if spec["prior"] == "interaction" else "GPS-strain"
        pct_int = int(round(100 * spec["fraction"]))
        form_note = (
            f"R0 {parent.PARENT_ID}; CONC {value}: move {stats['n_moved']}/{stats['n_dots']} "
            f"({pct_int}%) low->high {prior_short} 12.8km blocks, CV {stats['block_cv_12p8km_before']:.3f}->"
            f"{stats['block_cv_12p8km_after']:.3f}; pred {spec['pred_central']:+.3f}"
        )
        if len(form_note) > 140:
            raise AssertionError(f"form_note exceeded 140 chars ({len(form_note)}): {form_note}")

        rep = {
            "id": rid,
            "axis": "CONCENTRATION",
            "value": value,
            "role": spec["role"],
            "spec": spec,
            "git_sha": git_sha(),
            "parent": parent.PARENT_ID,
            "parent_sha256": parent.R0_ZEROS_SHA256,
            "parent_nan_sha256": parent.R0_NAN_SHA256,
            "determinism": "deterministic mergesort + row-major index tie-break (zero RNG)",
            "block_prior": prior_diag,
            "corroborated_ridge": corrob_diag,
            "lineage_cv_12p8km": lineage_cv_12p8km,
            "stats": stats,
            "model_prediction": {
                "evidence_class": "MODEL",
                "central": spec["pred_central"],
                "band": spec["pred_band"],
                "summary": spec["predicted_change_text"],
                "no_evidence_threshold": 0.01,
                "strand_holdout_calibration": holdout_cal,
            },
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
                "collar_lt3px_frozen": True,
                "added_interdot_sep_ge_2p8px": True,
                "pct_changed_in_1_50": True,
            },
            "report_only": {
                "proxy_variant": v_proxy,
                "proxy_parent": parent_proxy,
                "proxy_random_null": null_proxy,
                "surrogate_dti_variant": v_surrogate,
                "surrogate_dti_parent": parent_surrogate,
                "surrogate_dti_random_null": null_surrogate,
                "leakage_canary_max_strength": round(float(max_can), 6),
                "leakage_canary_pass": True,
                "sgmc_control": "SKIPPED — sgmc_faults_control pin marked UNVERIFIED (IRREGULARITIES item 8); report-only",
            },
            "form_note": form_note,
            "seconds": round(time.time() - t0, 2),
        }
        (ROOT / "registry" / f"build_report_conc_{value}.json").write_text(json.dumps(rep, indent=1) + "\n")
        reports.append(rep)

        row = {
            "id": rid,
            "site": "GEMSDOE89",
            "name": rid,
            "score": "",
            "evidence_class": "BUILT (unscored)",
            "encoding": "nan+zeros",
            "n_dots": str(stats["n_dots"]),
            "pct_changed": f"{stats['pct_changed']:.2f}",
            "sha8": sha8,
            "sha256": sha_nan,
            "sha256_zeros": sha_zeros,
            "parent": parent.PARENT_ID,
            "axis": "CONCENTRATION",
            "value": value,
            "status": "BUILT",
            "receipt": "N",
            "receipt_score": "",
            "predicted_change": spec["predicted_change_text"],
            "date": "",
            "form_note": form_note,
            "notes": (
                f"built 2026-10-23; 12.8km (128px) blocks; move {stats['n_moved']} dots ({stats['pct_changed']:.2f}%, "
                f"symdiff {stats['pct_symmetric_diff']:.2f}%) bot40->top40 {spec['prior']} prior; "
                f"count fixed 37,654; dcat_added>=3.00px (collar<3px frozen at 1611); "
                f"r_sep>=2.80px; CV12.8km {stats['block_cv_12p8km_before']:.4f}->{stats['block_cv_12p8km_after']:.4f} "
                f"(CV5km {stats['block_cv_5km_before']:.4f}->{stats['block_cv_5km_after']:.4f}); "
                f"mean disp {stats['mean_displacement_px']:.1f}px"
            ),
            "source": "GEMSDOE89",
        }
        new_rows.append(row)
        print(
            f"[{value}] {rid}  gates=PASS  moved={stats['n_moved']} ({stats['pct_changed']:.2f}%)  "
            f"CV12.8km {stats['block_cv_12p8km_before']:.4f}->{stats['block_cv_12p8km_after']:.4f}  "
            f"note_len={len(form_note)}  ({rep['seconds']}s)"
        )

    # Idempotently update ledger/submissions.csv
    with open(ledger_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames
        kept_rows = [
            r
            for r in reader
            if not (
                r.get("source") == "GEMSDOE89"
                and (r.get("axis") or "").strip().upper() == "CONCENTRATION"
                and (r.get("value") or "").strip() in set(values)
            )
        ]
    with open(ledger_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(kept_rows + new_rows)
    print(f"[ok] updated ledger/submissions.csv (+{len(new_rows)} CONCENTRATION row(s))")

    if args.all:
        (ROOT / "registry" / "build_reports_concentration_12p8km.json").write_text(
            json.dumps(reports, indent=1) + "\n"
        )
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
