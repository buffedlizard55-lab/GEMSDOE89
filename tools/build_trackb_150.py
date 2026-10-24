#!/usr/bin/env python3
"""Build the three Phase 2 TRACKB variants of verified Parent R0 (h33-h33-2-b2).

Usage:
    python tools/build_trackb.py --value t150add
    python tools/build_trackb.py --all

Start gates (brief sec.5):
  1. Re-hash every fetchable pinned input in registry/data_manifest.json.
  2. Rebuild Parent R0 (37,654 unit-mass dots) bit-for-bit from scored_h19_5.tif
     via dot_thin(r=2.8) + (d_cat > 2.0) and verify exact mask + parent SHA-256.
  3. Run single-feature leakage canary across all read bands + composite score_px
     (stop if any feature strength > 0.90).

Variants built (AXIS = TRACKB, Phase 2 strike-consistent traces >= 1.0 km):
  * t150add  : top 150 unbroken h19_5 strike-consistent >=1.0 km fault traces
               consolidated to continuous 8-connected 1-px polylines, retaining
               100 % of R0 dots (S = 37,654 + n_infill; primary Phase 1+2 arm).
  * t150swap : identical 150 unbroken >=1.0 km continuous fault traces, funded
               1-for-1 by retiring n_infill lowest-ranked isolated 1-dot R0
               speckles (S = 37,654 strictly conserved; mass-neutral control).
  * t150link : top 150 strike-consistent >=1.0 km fault traces assembled by
               linking R0's top-ranked dots across <=620 m Holocene wash /
               step-over gaps corroborated by subsurface potential-field/scarp
               support, funded 1-for-1 by retiring lowest-ranked 1-dot speckles
               (S = 37,654 strictly conserved; wash/relay bridge probe).

Each variant writes:
  * releases/<id>.tif        (NaN outside footprint, primary submission raster)
  * releases/<id>-zeros.tif  (zeros outside footprint, fallback submission raster)
  * releases/<id>.geojson    (RFC 7946 LineString FeatureCollection with one
                              quantitative geological evidence paragraph per trace)
Re-reads all written files from disk, runs every MUST gate + GeoJSON trace gate,
updates registry/build_report_trackb_<value>.json + registry/build_reports_trackb.json,
writes docs/TRACKB_EVIDENCE.md, and refreshes ledger/submissions.csv via build_ledger.
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

from gemsdoe import grid, metric, parent, proxy, relief, trackb_150 as trackb, validate  # noqa: E402

DATE = "20261024"
HOLD_SEEDS = (20261023, 7, 42)

VARIANTS = {
    "t150add": {
        "n_traces": 150,
        "trace_mode": "skeleton",
        "mass_mode": "add",
        "role": "PRIMARY PHASE-2 (zero R0 drop)",
        "p1_central": 0.000,
        "p1_band": [-0.004, 0.004],
        "p2_central": 0.012,
        "p2_band": [0.004, 0.024],
        "predicted_change_text": (
            "P1 +0.000 (-0.004..+0.004) / P2 +0.012 (+0.004..+0.024) MODEL "
            "(150 continuous >=1km traces added to R0; zero Phase-1 dot loss, full k=1.0 Phase-2 trace credit)"
        ),
        "short_pred": "P1 +0.000 / P2 +0.012 MODEL",
        "description": (
            "Consolidates top 150 unbroken strike-consistent >=1.0 km h19_5 fault traces to "
            "continuous 1-px polylines while retaining 100% of Parent R0 dots."
        ),
    },
    "t150swap": {
        "n_traces": 150,
        "trace_mode": "skeleton",
        "mass_mode": "swap",
        "role": "MASS-NEUTRAL CONTROL (S=37,654)",
        "p1_central": -0.002,
        "p1_band": [-0.008, 0.004],
        "p2_central": 0.011,
        "p2_band": [0.002, 0.022],
        "predicted_change_text": (
            "P1 -0.002 (-0.008..+0.004) / P2 +0.011 (+0.002..+0.022) MODEL "
            "(same 150 continuous >=1km traces funded by retiring lowest-ranked 1-dot R0 speckles; S=37,654)"
        ),
        "short_pred": "P1 -0.002 / P2 +0.011 MODEL",
        "description": (
            "Identical 150 continuous >=1.0 km h19_5 fault traces as t150add, funded 1-for-1 "
            "by retiring lowest-ranked isolated 1-dot R0 speckles at fixed S=37,654."
        ),
    },
    "t150link": {
        "n_traces": 150,
        "trace_mode": "dotlink",
        "mass_mode": "swap",
        "role": "WASH/RELAY BRIDGE PROBE (S=37,654)",
        "p1_central": -0.003,
        "p1_band": [-0.010, 0.005],
        "p2_central": 0.009,
        "p2_band": [0.001, 0.021],
        "predicted_change_text": (
            "P1 -0.003 (-0.010..+0.005) / P2 +0.009 (+0.001..+0.021) MODEL "
            "(150 dot-linked >=1km traces bridging <=620m wash/step-over gaps, speckle-funded; S=37,654)"
        ),
        "short_pred": "P1 -0.003 / P2 +0.009 MODEL",
        "description": (
            "Links top-ranked R0 dots across <=620 m Holocene wash and step-over gaps where "
            "potential-field/scarp support >=P65, funded 1-for-1 by retiring 1-dot speckles."
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
                and (row.get("axis") or "").strip().upper() == "TRACKB"
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


def gate_geojson(geojson_path: Path, expected_traces: int) -> tuple[bool, list[dict]]:
    """Re-read GeoJSON from disk and verify trace count, >=1.0 km chord,CRS84 range, and evidence."""
    doc = json.loads(geojson_path.read_text(encoding="utf-8"))
    results = []

    def add(name: str, ok: bool, detail: str = ""):
        results.append({"gate": name, "ok": bool(ok), "detail": detail})

    add("feature_collection", doc.get("type") == "FeatureCollection", str(doc.get("type")))
    feats = doc.get("features") or []
    add("trace_count", len(feats) == expected_traces, f"{len(feats)} vs {expected_traces}")

    min_len = min((f["properties"]["length_chord_km"] for f in feats), default=0.0)
    add("all_traces_ge_1km", min_len >= 1.0 - 1e-6, f"min_chord_km={min_len}")

    max_rms = max((f["properties"]["cross_strike_rms_m"] for f in feats), default=999.0)
    add("strike_consistent_rms", max_rms <= 250.0 + 1e-6, f"max_rms_m={max_rms}")

    lon_ok = True
    lat_ok = True
    ev_ok = True
    for f in feats:
        geom = f.get("geometry") or {}
        coords = geom.get("coordinates") or []
        if geom.get("type") != "LineString" or len(coords) < 8:
            lon_ok = False
        for lo, la in coords:
            if not (-122.0 <= lo <= -113.0):
                lon_ok = False
            if not (36.0 <= la <= 43.0):
                lat_ok = False
        ev = (f.get("properties") or {}).get("evidence") or ""
        if len(ev) < 200 or "Primary non-fault mimic:" not in ev:
            ev_ok = False

    add("valid_wgs84_linestrings", lon_ok and lat_ok, f"lon_ok={lon_ok} lat_ok={lat_ok}")
    add("geologist_evidence_per_trace", ev_ok, f"all {len(feats)} traces have >=200-char paragraph + mimic")
    return all(r["ok"] for r in results), results


def run_strand_holdout_calibration(
    cat_mask: np.ndarray,
    d28_mask: np.ndarray,
    h19_mask: np.ndarray,
    foot: np.ndarray,
    score_px: np.ndarray,
) -> dict:
    """Out-of-sample 3-seed strand holdout for Phase-1 (unexpanded) and Phase-2 (expert-expanded) DTI."""
    lbl_all, n_all = ndi.label(cat_mask, structure=np.ones((3, 3), dtype=np.int8))
    per_seed = {}

    for seed in HOLD_SEEDS:
        rng = np.random.default_rng(seed)
        hold = rng.random(n_all + 1) < 0.25
        hold[0] = False
        cat_known = cat_mask & (~hold[lbl_all])
        g_withheld = cat_mask & hold[lbl_all] & (~cat_known)
        d_known = ndi.distance_transform_edt(~cat_known)
        r0_sim = d28_mask & (d_known > 2.0) & foot & (~cat_known)
        base_p1 = metric.dti(g_withheld, r0_sim)
        d_gw = ndi.distance_transform_edt(~g_withheld)

        p1_deltas = {}
        p2_deltas = {}
        validated_counts = {}

        for vname, spec in VARIANTS.items():
            v_sim, sel_tr, _ = trackb.build_variant(
                parent_dots=r0_sim,
                h19_mask=h19_mask,
                footprint=foot,
                catalogue_mask=cat_known,
                score_px=score_px,
                n_traces=spec["n_traces"],
                trace_mode=spec["trace_mode"],
                mass_mode=spec["mass_mode"],
            )
            p1_deltas[vname] = round(metric.dti(g_withheld, v_sim) - base_p1, 6)

            # Phase-2 simulation: traces where >=20% of pixels lie within <=3.0 px of withheld
            # unmapped truth represent real fault continuations expanded by expert review.
            g_p2 = g_withheld.copy()
            n_val = 0
            for tr in sel_tr:
                ry = np.array([p[0] for p in tr["pixels"]], dtype=np.int32)
                rx = np.array([p[1] for p in tr["pixels"]], dtype=np.int32)
                if float(np.mean(d_gw[ry, rx] <= 3.0)) >= 0.20:
                    g_p2[ry, rx] = True
                    n_val += 1
            base_p2 = metric.dti(g_p2, r0_sim)
            p2_deltas[vname] = round(metric.dti(g_p2, v_sim) - base_p2, 6)
            validated_counts[vname] = n_val

        per_seed[f"seed_{seed}"] = {
            "withheld_fault_px": int(g_withheld.sum()),
            "r0_sim_dots": int(r0_sim.sum()),
            "r0_sim_phase1_dti": round(base_p1, 6),
            "phase1_unexpanded_delta_dti": p1_deltas,
            "phase2_expanded_delta_dti": p2_deltas,
            "phase2_validated_traces_of_150": validated_counts,
        }

    mean_p1 = {
        v: round(float(np.mean([per_seed[f"seed_{s}"]["phase1_unexpanded_delta_dti"][v] for s in HOLD_SEEDS])), 6)
        for v in VARIANTS
    }
    mean_p2 = {
        v: round(float(np.mean([per_seed[f"seed_{s}"]["phase2_expanded_delta_dti"][v] for s in HOLD_SEEDS])), 6)
        for v in VARIANTS
    }
    scale_to_live = round(0.2778 / float(np.mean([per_seed[f"seed_{s}"]["r0_sim_phase1_dti"] for s in HOLD_SEEDS])), 3)

    return {
        "evidence_class": "MODEL",
        "protocol": (
            "Withhold 25% of 8-connected catalogue fault strands BEFORE computing d_cat or R0. "
            "Phase-1 delta scores unexpanded withheld truth; Phase-2 delta simulates expert label "
            "expansion along submitted >=1.0 km traces that intersect/follow withheld truth (>=20% "
            "of trace within 300 m of withheld strand)."
        ),
        "mean_phase1_unexpanded_delta_dti_at_holdout_base": mean_p1,
        "mean_phase2_expanded_delta_dti_at_holdout_base": mean_p2,
        "live_dti_scale_factor_approx": scale_to_live,
        "mean_phase1_scaled_to_0p278": {k: round(v * scale_to_live, 5) for k, v in mean_p1.items()},
        "mean_phase2_scaled_to_0p278": {k: round(v * scale_to_live, 5) for k, v in mean_p2.items()},
        "seeds": per_seed,
    }


def write_evidence_summary_md(reports: list[dict], geojsons_by_val: dict[str, dict]) -> None:
    """Write concise structural-geologist summary + top-trace showcase in docs/TRACKB_EVIDENCE.md."""
    lines = [
        "# TRACKB Phase 2 Structural Fault-Trace Dossier (`GEMSDOE89`)",
        "",
        "Generated reproducibly by `tools/build_trackb.py` from SHA-256-verified Parent R0",
        "(`h33-h33-2-b2`, `37,654` unit dots) and the pinned 19-band GeoDAWN feature stack.",
        "Every trace in each companion GeoJSON (`releases/<id>.geojson`) is `>= 1.00 km`",
        "end-to-end chord length, strictly strike-consistent (`cross_strike_max <= 250 m`),",
        "`d_cat >= 3.00 px` (`>= 300 m` off known USGS/INGENIOUS faults), and carries its",
        "own quantitative structural-geologist evidence paragraph (`properties.evidence`).",
        "",
        "## Variant Summary",
        "",
        "| Value | Release ID | GeoJSON | Traces (`>=1 km`) | Bridged Traces | Total Chord (`km`) | Raster Dots (`n`) | Added / Removed (`% R0`) | Predicted (`MODEL`) |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for rep in reports:
        s = rep["stats"]
        val = rep["value"]
        lines.append(
            f"| `{val}` | `{rep['id']}` | `{rep['files']['geojson']}` | "
            f"{s['n_traces_emitted']} | {s['n_bridged_traces']} | {s['total_trace_chord_km']:.1f} | "
            f"{s['n_dots']:,} | +{s['n_added']}/-{s['n_removed']} ({s['pct_changed']:.2f}%) | "
            f"{rep['spec']['short_pred']} |"
        )

    lines.extend(
        [
            "",
            "## Representative Top-Ranked Geological Evidence Paragraphs",
            "",
            "*(Full 150-trace per-trace paragraphs are stored in `releases/<id>.geojson` under `features[*].properties.evidence`.)*",
            "",
        ]
    )
    for val in ("t150add", "t150link"):
        if val not in geojsons_by_val:
            continue
        doc = geojsons_by_val[val]
        lines.append(f"### `{val}` (`{doc['name']}` — top 5 of {len(doc['features'])} traces)")
        lines.append("")
        for feat in doc["features"][:5]:
            lines.append(f"- {feat['properties']['evidence']}")
        lines.append("")

    (ROOT / "docs" / "TRACKB_EVIDENCE.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--value", choices=sorted(VARIANTS), default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--skip-strand-holdout", action="store_true")
    args = ap.parse_args()
    if not args.all and args.value is None:
        ap.error("specify --value or --all")

    manifest = json.loads((ROOT / "registry" / "data_manifest.json").read_text(encoding="utf-8"))
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

    # ---- Stream required physical bands & run leakage canary ----------------
    bands = relief.stream_bands(paths["training_features"], list(trackb.TRACKB_BANDS))
    phys = trackb.compute_physical_stack(bands, foot)
    cat_kin = trackb.catalogue_kinematic_field(cat_mask, foot)

    band_tags = manifest["files"][0]["verified_band_tags"]
    canary_feats = {f"b{b:02d}_{band_tags[str(b)]}": phys["clean_bands"][b] for b in trackb.TRACKB_BANDS}
    canary_feats["trackb_score_px"] = np.where(foot, phys["score_px"], np.nan)
    can_res = proxy.canary(canary_feats, cat_mask, threshold=0.90)
    if any(v["flag"] for v in can_res.values()):
        print("STOP: leakage canary triggered (> 0.90)!", can_res)
        return 2
    max_can = max(max(v["auc"], 1.0 - v["auc"]) for v in can_res.values() if v["auc"] is not None)
    print(f"[ok] leakage canary PASS across 11 bands + trackb_score_px (max strength={max_can:.4f} <= 0.90)")

    values = ["t150add", "t150swap", "t150link"] if args.all else [args.value]
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
            score_px=phys["score_px"],
        )
        print(
            f"[model] 3-seed strand-holdout P1={holdout_cal['mean_phase1_unexpanded_delta_dti_at_holdout_base']} "
            f"P2={holdout_cal['mean_phase2_expanded_delta_dti_at_holdout_base']} ({time.time() - t_h:.1f}s)"
        )

    reports = []
    geojsons_by_val = {}

    for value in values:
        t0 = time.time()
        spec = VARIANTS[value]
        triple = (parent.PARENT_ID, "TRACKB", value)
        if triple in ledger_triples:
            print(f"STOP: duplicate (parent, axis, value) in ledger: {triple}")
            return 2

        v_mask, sel_traces, stats = trackb.build_variant(
            parent_dots=r0_rebuilt,
            h19_mask=h19_mask,
            footprint=foot,
            catalogue_mask=cat_mask,
            score_px=phys["score_px"],
            n_traces=spec["n_traces"],
            trace_mode=spec["trace_mode"],
            mass_mode=spec["mass_mode"],
            det_elev=phys["clean_bands"][12],
        )

        # Hard range and clearance assertions before writing
        if not (1.0 <= stats["pct_changed"] <= 50.0 and 1.0 <= stats["pct_symmetric_diff"] <= 50.0):
            print(f"STOP: {value} pct_changed={stats['pct_changed']} / sym={stats['pct_symmetric_diff']} outside 1-50%")
            return 2
        if stats["added_min_catalogue_clearance_px"] is None or stats["added_min_catalogue_clearance_px"] < 3.0 - 1e-6:
            print(f"STOP: {value} added trace pixels violate d_cat >= 3.0 px")
            return 2
        if stats["trace_min_catalogue_clearance_px"] < 3.0 - 1e-6:
            print(f"STOP: {value} trace pixels violate d_cat >= 3.0 px")
            return 2
        if stats["collar_lt3px_after"] != stats["collar_lt3px_before"]:
            print(f"STOP: {value} modified <3 px collar count")
            return 2

        tmp_nan = ROOT / "releases" / f"_tmp_trackb_{value}_nan.tif"
        tmp_zeros = ROOT / "releases" / f"_tmp_trackb_{value}_zeros.tif"
        tmp_nan.parent.mkdir(parents=True, exist_ok=True)
        grid.write_submission(tmp_nan, v_mask, foot, encoding="nan")
        grid.write_submission(tmp_zeros, v_mask, foot, encoding="zeros")
        sha_nan = grid.sha256_file(tmp_nan)
        sha_zeros = grid.sha256_file(tmp_zeros)
        sha8 = sha_nan[:8]
        rid = f"{parent.PARENT_ID}-TRACKB{value}-{DATE}-{sha8}"
        final_nan = ROOT / "releases" / f"{rid}.tif"
        final_zeros = ROOT / "releases" / f"{rid}-zeros.tif"
        final_geojson = ROOT / "releases" / f"{rid}.geojson"

        for old in (ROOT / "releases").glob(f"{parent.PARENT_ID}-TRACKB{value}-{DATE}-*"):
            if old not in (final_nan, final_zeros, final_geojson):
                old.unlink()

        tmp_nan.replace(final_nan)
        tmp_zeros.replace(final_zeros)

        geojson_doc = trackb.build_trace_geojson(
            variant_id=rid,
            value=value,
            traces=sel_traces,
            r0_mask=r0_rebuilt,
            phys=phys,
            cat_kin=cat_kin,
            raster_sha256=sha_nan,
        )
        final_geojson.write_text(json.dumps(geojson_doc, indent=1) + "\n", encoding="utf-8")
        sha_geojson = grid.sha256_file(final_geojson)
        geojsons_by_val[value] = geojson_doc

        # Re-read GeoTIFFs and GeoJSON from disk and run all MUST gates
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
        ok_gj, res_gj = gate_geojson(final_geojson, expected_traces=spec["n_traces"])
        twins_equal = bool(np.array_equal(dots_nan, dots_zeros) and np.array_equal(v_mask, dots_nan))
        if not (ok_nan and ok_zeros and ok_gj and twins_equal):
            print(f"STOP: MUST gate failure on {rid}: nan={ok_nan} zeros={ok_zeros} geojson={ok_gj} twins={twins_equal}")
            for r in res_nan + res_zeros + res_gj:
                if not r["ok"]:
                    print("   FAILED GATE:", r)
            return 2

        ledger_hashes.update({sha_nan, sha_zeros})
        ledger_triples.add(triple)

        v_proxy = proxy.hide_and_recover(v_mask, cat_mask)
        v_surrogate = proxy.surrogate_dti(v_mask, cat_mask)

        if spec["mass_mode"] == "add":
            chg_str = f"+{stats['n_added']}px ({stats['pct_changed']:.1f}%) {stats['n_traces_emitted']} >=1km traces, n={stats['n_dots']}"
        elif spec["trace_mode"] == "dotlink":
            chg_str = f"{stats['n_added']}px ({stats['pct_changed']:.1f}%) wash-bridged >=1km traces swap speckles, n={stats['n_dots']}"
        else:
            chg_str = f"{stats['n_added']}px ({stats['pct_changed']:.1f}%) >=1km traces swap speckles, n={stats['n_dots']}"

        form_note = f"R0 {parent.PARENT_ID}; TRACKB {value}: {chg_str}; {spec['short_pred']}"
        if len(form_note) > 140:
            raise AssertionError(f"form_note exceeded 140 chars ({len(form_note)}): {form_note}")

        rep = {
            "id": rid,
            "date": "2026-10-24",
            "axis": "TRACKB",
            "value": value,
            "role": spec["role"],
            "spec": spec,
            "git_sha": git_sha(),
            "parent": parent.PARENT_ID,
            "parent_sha256": parent.R0_ZEROS_SHA256,
            "parent_nan_sha256": parent.R0_NAN_SHA256,
            "determinism": "deterministic mergesort/lexsort + canonical NW endpoint orientation (zero RNG)",
            "physical_scoring": phys["diagnostics"],
            "stats": stats,
            "model_prediction": {
                "evidence_class": "MODEL",
                "phase1_central": spec["p1_central"],
                "phase1_band": spec["p1_band"],
                "phase2_central": spec["p2_central"],
                "phase2_band": spec["p2_band"],
                "summary": spec["predicted_change_text"],
                "no_evidence_threshold": 0.01,
                "strand_holdout_calibration": holdout_cal,
            },
            "files": {
                "nan": str(final_nan.relative_to(ROOT)),
                "zeros": str(final_zeros.relative_to(ROOT)),
                "geojson": str(final_geojson.relative_to(ROOT)),
                "sha256": sha_nan,
                "sha256_zeros": sha_zeros,
                "sha256_geojson": sha_geojson,
                "sha8": sha8,
            },
            "gates": {
                "nan": {"ok": ok_nan, "results": res_nan},
                "zeros": {"ok": ok_zeros, "results": res_zeros},
                "geojson": {"ok": ok_gj, "results": res_gj},
                "twins_identical_mask": twins_equal,
                "all_trace_pixels_dcat_ge_3px": True,
                "collar_lt3px_frozen": True,
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
        (ROOT / "registry" / f"build_report_trackb_{value}.json").write_text(
            json.dumps(rep, indent=1) + "\n", encoding="utf-8"
        )
        reports.append(rep)
        print(
            f"[{value}] {rid}  gates=PASS  traces={stats['n_traces_emitted']} ({stats['total_trace_chord_km']:.1f} km)  "
            f"added={stats['n_added']} removed={stats['n_removed']} ({stats['pct_changed']:.2f}%)  "
            f"note_len={len(form_note)}  ({rep['seconds']}s)"
        )

    if args.all:
        (ROOT / "registry" / "build_reports_trackb_150.json").write_text(
            json.dumps(reports, indent=1) + "\n", encoding="utf-8"
        )
        write_evidence_summary_md(reports, geojsons_by_val)

    # Rebuild integrated ledger via tools/build_ledger.py
    import build_ledger  # type: ignore

    build_ledger.main()
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "tools"))
    sys.exit(main())
