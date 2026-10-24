#!/usr/bin/env python3
"""Build TRACKB: Phase-2 strike-consistent trace inventory + 3 count-preserving
structural-concentration variants of verified Parent R0 (h33-h33-2-b2).

Usage:
    python tools/build_trackb.py --all
    python tools/build_trackb.py --value tr10

Start gate (Brief sec.5): verify every fetchable manifest pin by SHA-256 and
rebuild R0 bit-exactly before doing any work.  Then:
  1. Link R0 dots into >=1 km, sinuosity<=1.6 strike-consistent chains across
     <=4 px step-overs (one GeoDAWN line spacing). Rank by metric unique credit.
  2. Emit the Phase-2 inventory: releases/<...>-traces.geojson (WGS84 + evidence
     paragraph per trace) and evidence/TRACKB_trace_atlas.md (top traces).
  3. Build 3 nested, count-preserving (n=37,654) variants relocating 10/20/30 %
     of off-trace dots into the +-300 m trace corridor (r_sep>=2.8px, d_cat>=3).
  4. Write NaN/zeros twins, re-read from disk, run every MUST gate, record
     REPORT-ONLY proxy + a cross-strike jitter MODEL to registry/.
Never logs in, scrapes, or submits. SGMC control is UNVERIFIED and skipped.
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

from gemsdoe import grid, metric, parent, proxy, relief, trackb, validate  # noqa: E402

DATE = "20261024"
SEED = trackb.SEED

VARIANTS = {
    "tr10": {"frac": 0.10, "dose": "10%"},
    "tr20": {"frac": 0.20, "dose": "20%"},
    "tr30": {"frac": 0.30, "dose": "30%"},
}


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def verify_manifest(manifest: dict, data_root: Path) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    bad: dict = {}
    for entry in manifest["files"]:
        if entry.get("unverified"):
            print(f"[skip] unverified report-only pin {entry['id']} (IRREGULARITIES item 8)")
            continue
        p = data_root / entry["local"]
        if not p.exists():
            bad[entry["id"]] = {"present": False, "path": str(p)}
            continue
        if grid.sha256_file(p) != entry["sha256"]:
            bad[entry["id"]] = {"got": grid.sha256_file(p), "expected": entry["sha256"]}
            continue
        paths[entry["id"]] = p
    if bad:
        print(json.dumps({"ERROR": "manifest verification failed", "detail": bad}, indent=1))
        sys.exit(2)
    return paths


def existing_ledger_hashes(ledger_path: Path) -> set[str]:
    out: set[str] = set()
    if ledger_path.exists():
        with open(ledger_path, newline="") as fh:
            for row in csv.DictReader(fh):
                for col in ("sha256", "sha256_zeros"):
                    v = (row.get(col) or "").strip()
                    if v:
                        out.add(v)
    return out


def jitter_model(r0, variants: dict[str, np.ndarray], elig_h19, foot, cat):
    """Cross-strike positional-uncertainty MODEL (GeoDAWN ~kernel-radius jitter).

    Hold out a seeded 16.5% of eligible H19 strands as surrogate truth, jitter
    each strand laterally by sigma px, and report DTI(variant)-DTI(R0). At
    sigma=0 the corridor dots can lose (off-ridge); at sigma~1-2 px they should
    gain (they hedge lineament mislocation). MODEL, never a live score.
    """
    lbl, ncomp = ndi.label(elig_h19, structure=np.ones((3, 3), dtype=np.int8))
    rng = np.random.default_rng(42)
    keep = rng.random(ncomp + 1) < 0.165
    keep[0] = False
    truth0 = keep[lbl]
    ys, xs = np.nonzero(truth0)
    cids = lbl[ys, xs]
    out = {}
    # sigma=3.0 px is the brief's stated GeoDAWN lineament uncertainty
    # ("about the kernel radius"). sigma=0 is the ridge-locked worst case.
    for sigma in (0.0, 1.0, 1.8, 2.5, 3.0):
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
        base = metric.dti(ts, r0.astype(np.float64))
        row = {"truth_px": int(ts.sum()), "r0_dti": round(base, 5), "delta_vs_r0": {}}
        for k, v in variants.items():
            row["delta_vs_r0"][k] = round(metric.dti(ts, v.astype(np.float64)) - base, 5)
        out[f"sigma_{sigma:.1f}px"] = row
    return out


def evidence_paragraph(tr, r0, pts, d_cat, comp_strengths, pct_credit):
    """One structural-geologist evidence paragraph for a single trace."""
    strike = trackb.strike_azimuth(tr, r0, pts)
    length_km = tr.arc_px * 0.1
    dmin = float(d_cat[pts[tr.dot_idx][:, 0], pts[tr.dot_idx][:, 1]].min()) * trackb.PIXEL_M
    near = dmin <= 300.0
    dom = max(comp_strengths, key=comp_strengths.get)
    dom_label = {
        "tmi_hg": "TMI horizontal-gradient crest",
        "grav_slope": "isostatic-gravity slope break",
        "elev_slope": "detrended-elevation scarp",
    }[dom]
    loc = (f"{dmin:.0f} m from the nearest mapped fault (inside the 300 m scoring "
           f"kernel): consistent with newly mapped geometry of an existing system"
           if near else
           f"{dmin/1000:.1f} km from the nearest mapped fault: a frontier lineament, "
           f"the kind of structure expert review could add to the label set")
    article = "an" if dom_label[0].lower() in "aeiou" else "a"
    review = ("Priority for Phase-2 review: verify along-strike scarp continuity in lidar "
              "if supplied; the en-echelon step-overs linked at <=400 m are candidate "
              "relay ramps / breaching segments.")
    return (f"Trace T-{tr.rank:04d} — {length_km:.2f} km, sinuosity {tr.sinuosity:.2f}, "
            f"strike {strike:03.0f} deg, {tr.n_dots} R0 dots (peak metric unique-credit "
            f"{tr.max_credit:.1f}; long traces are densely dotted, so the mean dot sits "
            f"at the {pct_credit:.0f}th fleet credit percentile). Geophysics: coincides "
            f"with {article} {dom_label} (relative strengths TMI-HG "
            f"{comp_strengths['tmi_hg']:.2f}, gravity-slope "
            f"{comp_strengths['grav_slope']:.2f}, DEM-scarp "
            f"{comp_strengths['elev_slope']:.2f}). Setting: {loc}. {review}")


def build_geojson(traces, r0, d_cat, bands_comp, footprint, out_path: Path, atlas_path: Path,
                  top_atlas: int = 48):
    """Write the WGS84 trace inventory (with per-trace evidence) + a Markdown atlas."""
    pts = np.argwhere(r0)
    # global credit percentile lookup
    from gemsdoe.mass import unique_credit
    u, _ = unique_credit(r0)
    order = np.argsort(u)
    pct = np.empty(len(u), dtype=float)
    pct[order] = np.linspace(0, 100, len(u))

    features = []
    atlas_rows = []
    for tr in traces:
        p = pts[tr.dot_idx]
        rows = p[:, 0]
        cols = p[:, 1]
        # spine -> lon/lat (spine holds GLOBAL node indices into pts)
        spts = pts[tr.spine] if len(tr.spine) >= 2 else p
        lons, lats = trackb.utm_to_lonlat(spts[:, 0].astype(float), spts[:, 1].astype(float))
        coords = [[float(round(lo, 6)), float(round(la, 6))] for lo, la in zip(lons, lats)]
        comp_strengths = {
            "tmi_hg": float(np.nanmean(bands_comp["b03_tmi_hg"][rows, cols])),
            "grav_slope": float(np.nanmean(bands_comp["b05_iso_grav_anom_slope"][rows, cols])),
            "elev_slope": float(np.nanmean(bands_comp["b19_det_elev_slope"][rows, cols])),
        }
        comp_means = comp_strengths
        pct_credit = float(np.mean(pct[tr.dot_idx]))
        ev = evidence_paragraph(tr, r0, pts, d_cat, comp_strengths, pct_credit)
        dmin = float(d_cat[rows, cols].min()) * trackb.PIXEL_M
        props = {
            "trace_id": f"T-{tr.rank:04d}",
            "rank": tr.rank,
            "length_km": round(tr.arc_px * 0.1, 3),
            "sinuosity": round(tr.sinuosity, 3),
            "strike_azimuth_deg": round(trackb.strike_azimuth(tr, r0, pts), 1),
            "n_r0_dots": tr.n_dots,
            "mean_unique_credit": round(tr.mean_credit, 3),
            "max_unique_credit": round(tr.max_credit, 3),
            "structural_confidence": round(tr.confidence, 2),
            "nearest_catalogue_fault_m": round(dmin, 1),
            "within_300m_of_catalogue": bool(dmin <= 300.0),
            "band_strength": {k: round(v, 3) for k, v in comp_strengths.items()},
            "evidence": ev,
        }
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": props,
        })
        if tr.rank <= top_atlas:
            atlas_rows.append(f"### T-{tr.rank:04d} — {props['length_km']:.2f} km, "
                              f"strike {props['strike_azimuth_deg']:03.0f}°, "
                              f"sinu {props['sinuosity']:.2f}, "
                              f"{dmin:.0f} m to catalogue\n\n{ev}\n")

    fc = {
        "type": "FeatureCollection",
        "name": f"{parent.PARENT_ID}-TRACKB-traces-{DATE}",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "metadata": {
            "parent": parent.PARENT_ID,
            "axis": "TRACKB",
            "phase": "Phase-2 evidence inventory (not a weekly-slot candidate unless the human decides)",
            "crs_note": "geometry in WGS84 lon/lat (CRS84); source grid EPSG:32611, 100 m",
            "trace_rule": f"R0 dots linked across <= {trackb.GAP_PX:.0f} px (400 m) step-overs; "
                          f"kept if geodesic arc >= {trackb.MIN_LEN_PX:.0f} px (1 km) and "
                          f"sinuosity <= {trackb.MAX_SINUOSITY}; ranked by mean metric unique credit",
            "n_traces": len(features),
            "evidence_class": "derived from pinned rasters; all band values are relative robust-unit strengths",
            "data_sources": {
                "geodawn_line_spacing": "https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7",
                "scoring_metric": "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/",
                "new_fault_definition": "https://community.drivendata.org/t/where-do-you-draw-the-line/11536",
            },
            "disclaimer": "Hypotheses for a structural geologist, NOT confirmed faults. "
                          "Band strengths are relative (0-1) robust-unit means along the trace.",
        },
        "features": features,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(fc, indent=1) + "\n")

    atlas_path.parent.mkdir(parents=True, exist_ok=True)
    hdr = (f"# TRACKB trace atlas — {parent.PARENT_ID} ({DATE})\n\n"
           f"Top {min(top_atlas, len(features))} of {len(features)} strike-consistent "
           f"traces by metric unique credit; the complete inventory with one evidence "
           f"paragraph per trace is `{out_path.relative_to(ROOT)}`. Phase-2 evidence "
           f"only — these are hypotheses for a structural geologist, not confirmed "
           f"faults, and not a weekly-slot candidate unless the human decides.\n\n"
           f"Rule: R0 dots linked across <= {trackb.GAP_PX:.0f} px (400 m, one GeoDAWN "
           f"line spacing) step-overs; kept if geodesic arc >= 1 km and sinuosity "
           f"<= {trackb.MAX_SINUOSITY}. Every paragraph is generated from pinned rasters; "
           f"band strengths are relative (0-1) robust-unit means.\n\n---\n\n")
    atlas_path.write_text(hdr + "\n".join(atlas_rows))
    return len(features)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--value", choices=sorted(VARIANTS), default=None)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if not args.all and args.value is None:
        ap.error("specify --value or --all")

    manifest = json.loads((ROOT / "registry" / "data_manifest.json").read_text())
    data_root = Path(os.environ.get(manifest.get("data_root_env", "GEMSDOE_DATA"),
                                    ROOT / manifest.get("data_root_default", "data")))
    paths = verify_manifest(manifest, data_root)
    print(f"[ok] verified all {len(paths)} fetchable manifest pins")

    sample_arr, contract = grid.read_template(paths["sample_submission"])
    foot = np.isfinite(sample_arr)
    del sample_arr
    catalogue_raw = grid.read_back(paths["existing_faults"])[0]
    cat_mask = (np.isfinite(catalogue_raw) & (catalogue_raw > 0)) & foot
    h19_raw = grid.read_back(paths["scored_h19_5"])[0]
    h19_mask = (np.isfinite(h19_raw) & (h19_raw > 0)) & foot
    r0_pin = (grid.read_back(paths["parent_r0_zeros"])[0] > 0) & foot
    d28_pin = (grid.read_back(paths["parent_ancestor_d28"])[0] > 0) & foot

    assert grid.sha256_file(paths["parent_r0_zeros"]) == parent.R0_ZEROS_SHA256
    assert grid.sha256_file(paths["parent_r0_nan"]) == parent.R0_NAN_SHA256
    r0, d28 = parent.rebuild_r0_mask(h19_mask, foot, cat_mask)
    if not np.array_equal(d28, d28_pin) or not np.array_equal(r0, r0_pin) or int(r0.sum()) != parent.EXPECTED_R0_DOTS:
        print("STOP: rebuilt R0 mask does not match pinned parent")
        return 2
    print(f"[ok] rebuilt R0 bit-exact ({int(r0.sum())} dots)")

    d_cat = ndi.distance_transform_edt(~cat_mask)

    # stream bands for corroboration + full 19-band leakage canary
    t_can = time.time()
    band_tags = manifest["files"][0]["verified_band_tags"]
    all_bands = relief.stream_bands(paths["training_features"], list(range(1, 20)))
    feat_for_canary = {f"b{b:02d}_{band_tags[str(b)]}": all_bands[b] for b in range(1, 20)}
    feat_for_canary["scored_h19_5"] = np.where(foot, h19_mask.astype(np.float32), np.nan)
    can_res = proxy.canary(feat_for_canary, cat_mask, threshold=0.90)
    corrob = trackb.corroboration({
        "b03_tmi_hg": all_bands[3],
        "b05_iso_grav_anom_slope": all_bands[5],
        "b19_det_elev_slope": all_bands[19],
    })
    # AUC must be footprint-masked: robust_unit maps nodata/sentinels to 0, and
    # catalogue lies inside the finite footprint, so an unmasked composite AUC
    # is inflated by a pure data-availability artifact (measured 0.8125 raw,
    # 0.5431 inside the footprint). Evaluate on the region that can be scored.
    corrob_in = np.where(foot, corrob, np.nan)
    can_res["TRACKB_corroboration_composite"] = {
        "auc": proxy.auc(corrob_in, cat_mask), "flag": None,
        "auc_unmasked_artifact": round(float(proxy.auc(corrob, cat_mask)), 4),
    }
    cc = can_res["TRACKB_corroboration_composite"]["auc"]
    can_res["TRACKB_corroboration_composite"]["flag"] = bool(cc is not None and max(cc, 1 - cc) > 0.90)
    comp_bands = {
        "b03_tmi_hg": trackb.robust_unit(np.abs(all_bands[3])),
        "b05_iso_grav_anom_slope": trackb.robust_unit(np.abs(all_bands[5])),
        "b19_det_elev_slope": trackb.robust_unit(np.abs(all_bands[19])),
    }
    del all_bands, feat_for_canary
    any_flag = any(v["flag"] for v in can_res.values() if v.get("flag") is not None)
    max_strength = max(max(v["auc"], 1.0 - v["auc"]) for v in can_res.values() if v.get("auc") is not None)
    canary_doc = {
        "instrument": "leakage canary (single-feature AUC vs catalogue membership; 19 bands + h19_5 + TRACKB corroboration composite)",
        "threshold": 0.90,
        "sample_px": 400000, "seed": 11,
        "max_single_feature_strength": round(float(max_strength), 6),
        "features": can_res,
        "verdict": "FAIL: STOP" if any_flag else "PASS: no single feature exceeds 0.90",
        "note": ("REPORT ONLY. Composite AUC is footprint-masked; the raw 0.8125 is a pure "
                 "data-availability artifact (the finite-band flag alone scores 0.789). Inside "
                 "the footprint the composite is 0.543, matching the 19-band canary. Known "
                 "faults are masked in scoring and the composite only re-ranks LEGAL corridor "
                 "pixels at d_cat>=3, never selecting regions or overriding gates "
                 "(IRREGULARITIES item 14)."),
    }
    (ROOT / "registry" / "leakage_canary.json").write_text(json.dumps(canary_doc, indent=1) + "\n")
    if any_flag:
        print("STOP: leakage canary triggered (a single feature AUC > 0.90)")
        return 2
    print(f"[ok] leakage canary PASS (max {max_strength:.4f} incl. corroboration composite, {time.time()-t_can:.1f}s)")

    # ---- Phase-2 trace inventory ------------------------------------------
    t_tr = time.time()
    traces, on_trace = trackb.build_traces(r0)
    corridor = trackb.corridor_mask(traces, r0)
    placements = trackb.placement_list(r0, traces, corridor, corrob, foot, d_cat)
    collar = r0 & (d_cat < 3.0)              # inherited 2-3 px collar, frozen (no PRUNE edit)
    off_order = trackb.off_trace_order(r0, on_trace, seed=SEED, protect=collar)
    n_on = int(on_trace.sum())
    print(f"[ok] {len(traces)} traces; on-trace dots {n_on}; off-trace pool {len(off_order)}; "
          f"legal corridor placements {len(placements)}  ({time.time()-t_tr:.1f}s)")

    geojson_path = ROOT / "releases" / f"{parent.PARENT_ID}-TRACKB-traces-{DATE}.geojson"
    atlas_path = ROOT / "evidence" / f"TRACKB_trace_atlas_{DATE}.md"
    n_feat = build_geojson(traces, r0, d_cat, comp_bands, foot, geojson_path, atlas_path)
    print(f"[ok] wrote {geojson_path.name} ({n_feat} traces) + {atlas_path.relative_to(ROOT)}")

    # ---- report-only parent instruments -----------------------------------
    parent_proxy = proxy.hide_and_recover(r0, cat_mask)
    parent_surrogate = proxy.surrogate_dti(r0, cat_mask)
    null_dots = proxy.random_null(r0, foot, cat_mask)
    null_proxy = proxy.hide_and_recover(null_dots, cat_mask)

    ledger_hashes = existing_ledger_hashes(ROOT / "ledger" / "submissions.csv")
    # exclude any pre-existing TRACKB files (idempotent re-runs)
    for old in (ROOT / "releases").glob(f"{parent.PARENT_ID}-TRACKB-*.tif"):
        ledger_hashes.discard(grid.sha256_file(old))

    elig_h19 = h19_mask & (d_cat >= 3.0) & foot
    values = ["tr10", "tr20", "tr30"] if args.all else [args.value]
    built_masks: dict[str, np.ndarray] = {}
    reports = []

    N = int(r0.sum())
    for value in values:
        t0 = time.time()
        spec = VARIANTS[value]
        n_move = int(round(spec["frac"] * N))
        if n_move > len(placements):
            print(f"STOP: {value} needs {n_move} placements but only {len(placements)} legal slots")
            return 2
        if n_move > len(off_order):
            print(f"STOP: {value} needs {n_move} sources but off-trace pool is {len(off_order)}")
            return 2
        sources = off_order[:n_move]
        dests = placements[:n_move]
        v_mask, stats = trackb.build_variant(r0, foot, sources, dests)

        # hard invariants
        if not stats["count_preserved"]:
            print(f"STOP: {value} count not preserved"); return 2
        added = v_mask & ~r0
        removed = r0 & ~v_mask
        pct_changed = 100.0 * n_move / N
        min_add_dcat = float(d_cat[added].min()) if added.any() else None
        if min_add_dcat is None or min_add_dcat < 3.0 - 1e-6:
            print(f"STOP: {value} added dots violate d_cat>=3: {min_add_dcat}"); return 2
        if not (1.0 <= pct_changed <= 50.0):
            print(f"STOP: {value} pct_changed={pct_changed} outside 1-50%"); return 2
        # zero catalogue mass
        if int((v_mask & cat_mask).sum()) != 0:
            print(f"STOP: {value} has catalogue mass"); return 2
        # the inherited 2-3 px collar must be untouched (no PRUNE confound)
        n_collar_removed = int((removed & collar).sum())
        if n_collar_removed != 0:
            print(f"STOP: {value} moved {n_collar_removed} protected collar dots"); return 2
        # min separation: distance from each added dot to its nearest other dot
        from scipy.spatial import cKDTree
        all_pts = np.argwhere(v_mask)
        added_pts = np.argwhere(added)
        tree_all = cKDTree(all_pts)
        d2, _ = tree_all.query(added_pts, k=2)
        min_sep = float(d2[:, 1].min()) if added_pts.size else None
        if min_sep is not None and min_sep < trackb.MIN_SEP_PX - 1e-6:
            print(f"STOP: {value} added-dot separation {min_sep:.3f} < {trackb.MIN_SEP_PX}")
            return 2

        # parent-diff statistics: mean displacement of removed dots to their replacements
        disp = None
        if added.any():
            tree_add = cKDTree(np.argwhere(added))
            dd, _ = tree_add.query(np.argwhere(removed))
            disp = float(dd.mean())

        tmp_nan = ROOT / "releases" / f"_tmp_trackb_{value}_nan.tif"
        tmp_zeros = ROOT / "releases" / f"_tmp_trackb_{value}_zeros.tif"
        grid.write_submission(tmp_nan, v_mask, foot, encoding="nan")
        grid.write_submission(tmp_zeros, v_mask, foot, encoding="zeros")
        sha_nan = grid.sha256_file(tmp_nan)
        sha_zeros = grid.sha256_file(tmp_zeros)
        sha8 = sha_nan[:8]
        rid = f"{parent.PARENT_ID}-TRACKB-{value.upper()}-{DATE}-{sha8}"
        final_nan = ROOT / "releases" / f"{rid}.tif"
        final_zeros = ROOT / "releases" / f"{rid}-zeros.tif"
        for old in (ROOT / "releases").glob(f"{parent.PARENT_ID}-TRACKB-{value.upper()}-{DATE}-*.tif"):
            if old not in (final_nan, final_zeros):
                old.unlink()
        tmp_nan.replace(final_nan)
        tmp_zeros.replace(final_zeros)

        # re-read from disk, gate
        nan_arr, _ = grid.read_back(final_nan)
        zeros_arr, _ = grid.read_back(final_zeros)
        dots_nan = np.nan_to_num(nan_arr) > 0
        dots_zeros = zeros_arr > 0
        # min_clearance_px=0.0 -> hard gate is zero catalogue mass (R0 inherits a
        # frozen 2-3 px collar). Added dots are separately required at d_cat>=3.
        ok_nan, res_nan = validate.gate_release(
            final_nan, contract, footprint=foot, dots_mask=dots_nan,
            require_nan_outside=True, ledger_hashes=ledger_hashes,
            min_clearance_px=0.0, clearance_raster=catalogue_raw)
        ok_zeros, res_zeros = validate.gate_release(
            final_zeros, contract, footprint=foot, dots_mask=dots_zeros,
            require_nan_outside=False, ledger_hashes=ledger_hashes,
            min_clearance_px=0.0, clearance_raster=catalogue_raw)
        twins_equal = bool(np.array_equal(dots_nan, dots_zeros) and np.array_equal(v_mask, dots_nan))
        if not (ok_nan and ok_zeros and twins_equal):
            print(f"STOP: MUST gate failure on {rid}: nan={ok_nan} zeros={ok_zeros} twins={twins_equal}")
            for r in res_nan + res_zeros:
                if not r["ok"]:
                    print("   ", r["gate"], r["detail"])
            return 2
        ledger_hashes.update({sha_nan, sha_zeros})

        # report-only
        v_proxy = proxy.hide_and_recover(v_mask, cat_mask)
        v_surrogate = proxy.surrogate_dti(v_mask, cat_mask)
        # H19 ridge coverage (MODEL directional) within kernel
        d_r0 = ndi.distance_transform_edt(~r0)
        d_var = ndi.distance_transform_edt(~v_mask)
        cov_before = float(np.clip(1 - d_r0[elig_h19] / 3.0, 0, 1).mean())
        cov_after = float(np.clip(1 - d_var[elig_h19] / 3.0, 0, 1).mean())

        built_masks[value] = v_mask
        stats.update({
            "pct_changed": pct_changed,
            "n_sources": len(sources),
            "added_min_catalogue_clearance_px": min_add_dcat,
            "added_min_separation_px": min_sep,
            "inherited_collar_dots_frozen": int(collar.sum()),
            "collar_dots_moved": 0,
            "mean_displacement_px": disp,
            "h19_coverage_before": round(cov_before, 5),
            "h19_coverage_after": round(cov_after, 5),
        })
        reports.append({
            "id": rid,
            "axis": "TRACKB",
            "value": value.upper(),
            "spec": dict(spec),  # predicted_change_text filled from the jitter MODEL below
            "git_sha": git_sha(),
            "parent": parent.PARENT_ID,
            "parent_sha256": parent.R0_ZEROS_SHA256,
            "seed": SEED,
            "stats": stats,
            "files": {"nan": str(final_nan.relative_to(ROOT)),
                      "zeros": str(final_zeros.relative_to(ROOT)),
                      "sha256": sha_nan, "sha256_zeros": sha_zeros, "sha8": sha8},
            "gates": {"nan": {"ok": ok_nan, "results": res_nan},
                      "zeros": {"ok": ok_zeros, "results": res_zeros},
                      "twins_identical_mask": twins_equal,
                      "count_preserved": stats["count_preserved"],
                      "added_dots_dcat_ge_3px": True,
                      "pct_changed_in_1_50": True},
            "phase2_inventory": {"geojson": str(geojson_path.relative_to(ROOT)),
                                 "atlas": str(atlas_path.relative_to(ROOT)),
                                 "n_traces": n_feat},
            "report_only": {
                "proxy_variant": v_proxy, "proxy_parent": parent_proxy,
                "proxy_random_null": null_proxy,
                "surrogate_dti_variant": v_surrogate, "surrogate_dti_parent": parent_surrogate,
            },
            "form_note": "",  # filled below with the MODEL central (<=140 chars)
            "seconds": round(time.time() - t0, 2),
        })
        print(f"[{value}] {rid}  gates=PASS  moved={n_move} ({pct_changed:.1f}%)  "
              f"minsep={min_sep:.2f}px  disp={disp:.1f}px  h19cov {cov_before:.4f}->{cov_after:.4f}  {reports[-1]['seconds']}s")

    # Mechanism-matched cross-strike jitter MODEL. The brief states GeoDAWN
    # lineaments are uncertain by ~the kernel radius (3 px), so the central
    # prediction is taken at sigma=2.5px (conservative near that uncertainty);
    # the band spans sigma=0 (ridge-locked worst case) to sigma=3.0 (kernel
    # radius, where the corridor hedge pays). H19 is R0's own source, so this
    # surrogate can price the on-ridge coverage COST but cannot value the
    # Phase-2 expert-expansion BENEFIT — it is a floor, not a point forecast.
    jitter = jitter_model(r0, built_masks, elig_h19, foot, cat_mask)
    central_key = "sigma_2.5px" if "sigma_2.5px" in jitter else list(jitter)[-1]
    for rep in reports:
        v = rep["value"].lower()
        deltas = {k: d["delta_vs_r0"][v] for k, d in jitter.items()}
        rep["report_only"]["jitter_model_sensitivity"] = {
            k: {"r0_dti": d["r0_dti"], "delta": d["delta_vs_r0"][v]}
            for k, d in jitter.items()
        }
        central = deltas[central_key]
        lo, hi = min(deltas.values()), max(deltas.values())
        d0 = deltas.get("sigma_0.0px", lo)
        dkr = deltas.get("sigma_3.0px", hi)
        rep["spec"]["predicted_change_text"] = (
            f"{central:+.3f} (MODEL central at 2.5px cross-strike jitter; band "
            f"{lo:+.3f}..{hi:+.3f}; ridge-locked sigma=0 {d0:+.3f}, kernel-radius "
            f"sigma=3 {dkr:+.3f}). Count-preserving structural concentration; H19-"
            f"surrogate prices only the on-ridge coverage cost, not the Phase-2 "
            f"expert-expansion benefit — a floor. Phase-2 evidence play, NOT a "
            f"weekly-slot candidate unless the human decides. |Δ|<0.01 = no evidence."
        )
        rep["form_note"] = (
            f"{parent.PARENT_ID}; TRACKB {v}: {rep['stats']['n_sources']} "
            f"({rep['spec']['dose']}) off-trace -> +-300m of >=1km traces; "
            f"n=37654; dcat>=3; Phase-2 GeoJSON; pred {central:+.3f}"
        )
        assert len(rep["form_note"]) <= 140, (v, len(rep["form_note"]), rep["form_note"])
        (ROOT / "registry" / f"build_report_trackb_{v}.json").write_text(json.dumps(rep, indent=1) + "\n")
    (ROOT / "registry" / "build_reports_trackb.json").write_text(json.dumps(reports, indent=1) + "\n")

    if args.all:
        # extend report_only_status.json (report-only, never a gate)
        status_path = ROOT / "registry" / "report_only_status.json"
        status = json.loads(status_path.read_text()) if status_path.exists() else {}
        status["trackb_phase2_inventory"] = {
            "evidence_class": "MODEL/PROXY — never a live score",
            "n_traces": n_feat,
            "on_trace_r0_dots": n_on,
            "off_trace_pool": int(len(off_order)),
            "legal_corridor_placements": int(len(placements)),
            "geojson": str(geojson_path.relative_to(ROOT)),
        }
        status["trackb_jitter_model"] = {
            "evidence_class": "MODEL (cross-strike positional-uncertainty sensitivity)",
            "note": "at sigma=0 corridor dots can lose (off-ridge); sigma~1-2px hedges "
                    "GeoDAWN lineament mislocation. Directional only, not a live score.",
            "deltas": jitter,
        }
        status_path.write_text(json.dumps(status, indent=1) + "\n")
        print(f"[done] TRACKB: {len(reports)} variants, {n_feat} traces; "
              f"jitter central@2.5px " + ", ".join(
                  f"{rep['value']}={jitter[central_key]['delta_vs_r0'][rep['value'].lower()]:+.4f}"
                  for rep in reports))
    return 0


if __name__ == "__main__":
    sys.exit(main())
