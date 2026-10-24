#!/usr/bin/env python3
"""Build the TRACKB (Phase 2) trace deliverable from the verified R0 parent.

Usage:  python tools/build_trackb.py

TRACKB is the only brief axis with no (parent, axis, value) row anywhere
in the ledger (all weekly axes, incl. PRUNE at 1/1.5/2.5/3/4 px, were
already built in GEMSDOE84/GEMSDOE89 sessions -- see IRREGULARITIES item
14).  It is a Phase-2 expert-review product, NOT a weekly-slot candidate.

Outputs:
  releases/<id>.tif + <id>-zeros.tif   member dots of the delivered traces
  releases/<id>.geojson                trace polylines (EPSG:32611 metres)
  ledger/TRACKB_TRACES.md              one evidence paragraph per trace
  registry/build_trackb_top12.json + registry/build_reports_trackb.json
"""

from __future__ import annotations

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

from gemsdoe import grid, trackb, validate  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
PARENT_SHA256 = "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
DATE = "20261024"
VALUE = "top12"
REQUIRED = ("sample_submission", "existing_faults", "parent_r0_zeros",
            "parent_r0_nan", "scored_h19_5", "parent_ancestor_d28",
            "parent_ancestor_solo_d28")
ORIGIN_X, ORIGIN_Y, PX = 243350.0, 4508550.0, 100.0


def load_manifest():
    return json.loads((ROOT / "registry" / "data_manifest.json").read_text())


def data_root(manifest):
    return Path(os.environ.get(manifest.get("data_root_env", "GEMSDOE_DATA"),
                               ROOT / manifest.get("data_root_default", "data")))


def verify_inputs(manifest, required):
    root = data_root(manifest)
    bad = []
    for f in manifest["files"]:
        if f.get("unverified") or f["id"] not in required:
            continue
        p = root / f["local"]
        if not p.exists() or grid.sha256_file(p) != f["sha256"]:
            bad.append(f["id"])
    return bad


def ledger_hashes():
    out = set()
    with open(ROOT / "ledger" / "submissions.csv", newline="") as fh:
        for row in csv.DictReader(fh):
            for k in ("sha256", "sha256_zeros"):
                v = (row.get(k) or "").strip()
                if v:
                    out.add(v)
    return out


def to_xy(pt):
    r, c = int(pt[0]), int(pt[1])
    return [ORIGIN_X + (c + 0.5) * PX, ORIGIN_Y - (r + 0.5) * PX]


def _ordinal(n):
    n = int(n)
    if 10 <= n % 100 <= 20:
        suf = "th"
    else:
        suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


def evidence_paragraph(t, credit_pct):
    m = t["metrics"]
    xy = [to_xy(p) for p in t["pts"]]
    (x0, y0), (x1, y1) = xy[0], xy[-1]
    cx, cy = float(np.mean([p[0] for p in xy])), float(np.mean([p[1] for p in xy]))
    return (
        f"**{t['trace_id']}** (centroid E {cx:,.0f} m, N {cy:,.0f} m; endpoints "
        f"E {x0:,.0f}/N {y0:,.0f} to E {x1:,.0f}/N {y1:,.0f}, EPSG:32611): a "
        f"{m['length_km']:.1f} km trace carried by {m['n_dots']} of R0's unit dots at "
        f"{m['mean_spacing_px']:.1f} px mean spacing, striking {m['strike_deg']:05.1f} deg "
        f"(segment-azimuth consistency R = {m['consistency_R']:.2f}, mean deviation "
        f"{m['mean_segment_deviation_deg']:.0f} deg, straightness {m['straightness']:.2f}). "
        f"Every member dot is an R0 dot on the corroborated h19_5 potential-field ridge, "
        f"with member strand credit at the {_ordinal(credit_pct)} percentile of R0 dots and "
        f"catalogue clearance {m['dcat_min_px']:.1f}-{m['dcat_mean_px']:.1f} px (min-mean), "
        f"so the trace parallels -- but never touches -- the masked known-fault catalogue "
        f"and is offered as candidate *new* geometry of the kind the organizers count "
        f"(newly mapped segments of existing systems included). The non-fault mimic to "
        f"exclude on review is a lithologic or cultural linear (contact, dike, road or "
        f"survey-line artefact) that the potential-field ridge follows without surface "
        f"rupture. Falsifier: expert review or field evidence placing the lineament on "
        f"such a mimic, or a mapped fault whose strike departs from "
        f"{m['strike_deg']:05.1f} deg by more than ~25 deg along this corridor, removes it."
    )


def main():
    t_start = time.time()
    manifest = load_manifest()
    bad = verify_inputs(manifest, set(REQUIRED))
    if bad:
        print(json.dumps({"ERROR": "pinned inputs failed verification", "detail": bad}))
        return 2
    print("[ok] pinned inputs verified (7 required ids hash-clean)")

    root = data_root(manifest)
    paths = {f["id"]: root / f["local"] for f in manifest["files"]}
    sample, contract = grid.read_template(paths["sample_submission"])
    footprint = np.isfinite(sample)
    del sample
    catalogue = grid.read_back(paths["existing_faults"])[0]
    cat_mask = (np.isfinite(catalogue) & (catalogue > 0)) & footprint
    parent_arr = grid.read_back(paths["parent_r0_zeros"])[0]
    parent_dots = (parent_arr > 0) & footprint
    assert grid.sha256_file(paths["parent_r0_zeros"]) == PARENT_SHA256
    d_cat = ndi.distance_transform_edt(~cat_mask)
    for pid in ("parent_ancestor_d28", "parent_ancestor_solo_d28"):
        anc = (grid.read_back(paths[pid])[0] > 0) & footprint
        assert np.array_equal(anc & (d_cat > 2.0), parent_dots), f"R0 not reproduced from {pid}"
    print("[ok] parent R0 verified; cell-identical from both pinned ancestors")

    h19 = (grid.read_back(paths["scored_h19_5"])[0] > 0) & footprint
    traces, audit, credit, pts = trackb.build_traces(parent_dots, h19, d_cat)
    if not traces:
        print("[STOP] no qualifying traces")
        return 3
    print(f"[ok] traces: {audit}")

    variant = np.zeros_like(parent_dots)
    for t in traces:
        variant[t["pts"][:, 0], t["pts"][:, 1]] = True
    n_trace_dots = int(variant.sum())
    pct_changed = 100.0 * (int(parent_dots.sum()) - n_trace_dots) / int(parent_dots.sum())

    tmp_nan = ROOT / "releases" / "_tmp_trackb_nan.tif"
    tmp_zeros = ROOT / "releases" / "_tmp_trackb_zeros.tif"
    grid.write_submission(tmp_nan, variant, footprint, encoding="nan")
    grid.write_submission(tmp_zeros, variant, footprint, encoding="zeros")
    sha_nan, sha_zeros = grid.sha256_file(tmp_nan), grid.sha256_file(tmp_zeros)
    sha8 = sha_nan[:8]
    rid = f"{PARENT_ID}-TRACKB{VALUE}-{DATE}-{sha8}"
    final_nan = ROOT / "releases" / f"{rid}.tif"
    final_zeros = ROOT / "releases" / f"{rid}-zeros.tif"
    hashes = ledger_hashes()
    if sha_nan in hashes or sha_zeros in hashes:
        print(f"[STOP] sha already in ledger ({sha8})")
        return 4
    tmp_nan.replace(final_nan)
    tmp_zeros.replace(final_zeros)

    nan_arr = grid.read_back(final_nan)[0]
    zeros_arr = grid.read_back(final_zeros)[0]
    dots_nan = np.nan_to_num(nan_arr) > 0
    ok_nan, res_nan = validate.gate_release(
        final_nan, contract, footprint=footprint, dots_mask=dots_nan,
        require_nan_outside=True, ledger_hashes=hashes, min_clearance_px=0.0,
        clearance_raster=catalogue)
    ok_zeros, res_zeros = validate.gate_release(
        final_zeros, contract, footprint=footprint, dots_mask=zeros_arr > 0,
        require_nan_outside=False, ledger_hashes=hashes, clearance_raster=catalogue)
    twins = bool(np.array_equal(dots_nan, zeros_arr > 0)) and bool(np.array_equal(variant, dots_nan))

    # GeoJSON (EPSG:32611 metres; crs member declared explicitly)
    features = []
    trace_rows = []
    for t in traces:
        m = t["metrics"]
        # percentile of the trace's mean member credit among all R0 dots
        pct_mean = float(100.0 * (credit < m["credit_mean"]).mean())
        t["credit_pct_mean"] = pct_mean
        coords = [to_xy(p) for p in t["pts"]]
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {"trace_id": t["trace_id"], "parent": PARENT_ID,
                           "n_dots": m["n_dots"], "length_km": round(m["length_km"], 3),
                           "strike_deg": round(m["strike_deg"], 2),
                           "consistency_R": round(m["consistency_R"], 3),
                           "straightness": round(m["straightness"], 3),
                           "mean_strand_credit": round(m["credit_mean"], 3),
                           "dcat_min_px": round(m["dcat_min_px"], 2)},
        })
        trace_rows.append({"trace_id": t["trace_id"], **m,
                           "start_xy": coords[0], "end_xy": coords[-1],
                           "centroid_xy": [float(np.mean([c[0] for c in coords])),
                                           float(np.mean([c[1] for c in coords]))]})
    geojson = {"type": "FeatureCollection",
               "crs": {"type": "name", "properties": {"name": "EPSG:32611"}},
               "features": features}
    geo_path = ROOT / "releases" / f"{rid}.geojson"
    geo_path.write_text(json.dumps(geojson, indent=1) + "\n")

    md = ["# TRACKB traces — evidence paragraphs (Phase 2, expert review)",
          "",
          f"Parent: **R0 = {PARENT_ID}** (37,654 unit dots; live 0.2778 = **CLAIM**, no receipt). "
          f"Traces are built from R0's top-ranked dots (strand credit on the h19_5 ridge; "
          f"top two-thirds linked at 4.5 px), filtered to >= 1 km, >= 8 dots, strike "
          f"consistency R >= 0.85 and straightness >= 0.60, and ranked by total member "
          f"strand credit. Coordinates are EPSG:32611 metres (pixel centres). "
          f"This is a Phase-2 review product, **not a weekly-slot candidate**: the companion "
          f"raster `{rid}.tif` keeps only the {n_trace_dots} member dots and would score "
          f"far below R0 if submitted as-is (MODEL, by construction).",
          ""]
    for t in traces:
        md.append(evidence_paragraph(t, t["credit_pct_mean"]))
        md.append("")
    (ROOT / "ledger" / "TRACKB_TRACES.md").write_text("\n".join(md))

    rep = {
        "id": rid, "value": VALUE, "axis": "TRACKB", "role": "PHASE2-REVIEW (not a slot candidate)",
        "parent": PARENT_ID, "parent_sha256": PARENT_SHA256, "seed": None,
        "audit": audit, "traces": trace_rows,
        "stats": {"n_dots": n_trace_dots, "pct_changed": pct_changed,
                  "n_traces": len(traces),
                  "total_length_km": float(sum(t["metrics"]["length_km"] for t in traces))},
        "files": {"nan": str(final_nan.relative_to(ROOT)), "zeros": str(final_zeros.relative_to(ROOT)),
                  "geojson": str(geo_path.relative_to(ROOT)),
                  "sha256": sha_nan, "sha256_zeros": sha_zeros, "sha8": sha8},
        "gates": {"nan": {"ok": ok_nan, "results": res_nan},
                  "zeros": {"ok": ok_zeros, "results": res_zeros}, "twins_identical": twins},
        "predicted_change": "n/a (Phase 2 trace product; do not submit for score)",
        "seconds": round(time.time() - t_start, 1),
    }
    (ROOT / "registry" / "build_trackb_top12.json").write_text(json.dumps(rep, indent=1) + "\n")
    (ROOT / "registry" / "build_reports_trackb.json").write_text(json.dumps([rep], indent=1) + "\n")
    ok = ok_nan and ok_zeros and twins
    print(f"[trackb] {rid} gates nan={ok_nan} zeros={ok_zeros} twins={twins} "
          f"traces={len(traces)} dots={n_trace_dots} len={rep['stats']['total_length_km']:.1f}km")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
