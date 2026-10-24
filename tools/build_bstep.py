#!/usr/bin/env python3
"""Build + holdout-validate the BSTP lane candidate (GEMSDOE89, 2026-10-24).

Pipeline (reuse, don't rebuild): pinned bands -> bstep surface (snap.py
normalisation) -> leakage canary (proxy.auc) -> protocol segment holdout
(holdout.py; parent rebuilt per fold by parent.rebuild_r0_mask on the
visible catalogue only) -> final fixed-mass candidate -> grid.py writer ->
validate.py hard gates -> uniqueness audit vs every releases/ mask.

Outputs: releases/gems89-bstp40-20261024-<sha8>.tif (+ -zeros.tif),
registry/build_report_{AXIS_VALUE}.json, registry/holdout_{AXIS_VALUE}.json,
registry/run_card_bstep40.json.  Requires data/ from
tools/fetch_pinned_data.py (bands are read from the pinned 19-band stack).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import tifffile
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DATA = ROOT / "data"

from gemsdoe import bstep, holdout, parent as parent_mod  # noqa: E402
from gemsdoe.grid import sha256_file, write_submission  # noqa: E402
from gemsdoe.proxy import auc  # noqa: E402
from gemsdoe.snap import edge_response  # noqa: E402
from gemsdoe.validate import gate_release  # noqa: E402

DATE = "20261024"
AXIS_VALUE = sys.argv[1] if len(sys.argv) > 1 else "bstp40"
RETAIN = float(sys.argv[2]) if len(sys.argv) > 2 else 0.60
CORRIDOR = float(sys.argv[3]) if len(sys.argv) > 3 else None
RETAIN_BY_EDGE = len(sys.argv) > 4 and sys.argv[4] == 'edge'


def load_band(idx: int, name: str) -> np.ndarray:
    cache = DATA / f"band{idx:02d}_{name}.npy"
    if cache.exists():
        return np.load(cache)
    stack = tifffile.imread(DATA / "training_features.tif")
    band = np.ascontiguousarray(stack[:, :, idx - 1])
    np.save(cache, band)
    return band


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    def ranks(v):
        order = np.argsort(v, kind="mergesort")
        r = np.empty(len(v), dtype=np.float64)
        r[order] = np.arange(len(v), dtype=np.float64)
        vs = v[order]
        start = 0
        for i in range(1, len(vs) + 1):
            if i == len(vs) or vs[i] != vs[start]:
                if i - start > 1:
                    r[order[start:i]] = r[order[start:i]].mean()
                start = i
        return r
    rx, ry = ranks(np.asarray(x, dtype=np.float64).ravel()), \
        ranks(np.asarray(y, dtype=np.float64).ravel())
    return float(np.corrcoef(rx, ry)[0, 1])


def block_density(dots: np.ndarray, foot: np.ndarray, block: int = 50):
    h, w = dots.shape
    hb, wb = h // block, w // block
    d = dots[:hb * block, :wb * block].reshape(hb, block, wb, block).sum(axis=(1, 3))
    f = foot[:hb * block, :wb * block].reshape(hb, block, wb, block).sum(axis=(1, 3))
    ok = f >= 0.5 * block * block
    return (d / np.maximum(f, 1))[ok]


def overlap_within_3px(cand: np.ndarray, other: np.ndarray) -> float:
    d = ndi.distance_transform_edt(~other)
    return float((d[cand] <= 3.0).mean())


def main() -> int:
    sample = tifffile.imread(DATA / "sample_submission.tif")
    foot = np.isfinite(sample)
    cat_raw = tifffile.imread(DATA / "existing_faults.tif")
    cat = (cat_raw > 0) & foot
    h19 = (tifffile.imread(DATA / "h19_5.tif") > 0) & foot
    r0 = (tifffile.imread(DATA / "parent_r0_zeros.tif") == 1.0)
    contract = json.loads((ROOT / "registry/grid_contract.json").read_text())

    bands = {3: load_band(3, "tmi_hg"), 18: load_band(18, "grav_hg")}
    edge, _edge_out = edge_response(bands, foot)
    edge_diag = _edge_out["response"]  # per_band arrays are not JSON data
    surface, channels, surf_diag = bstep.bstep_surface(
        load_band(15, "depth_to_base"), load_band(17, "cond_surf"), edge, foot)

    # --- leakage canary: single-feature AUC vs catalogue membership --------
    canary = {}
    feats = dict(channels)
    feats["surface_geomean"] = surface
    for name, arr in feats.items():
        a = auc(np.where(foot, arr, np.nan), cat)
        canary[name] = {"auc": a, "flag_gt_0p90": bool(a is not None and max(a, 1 - a) > 0.90)}
    print("[canary]", json.dumps(canary))

    # --- surface uniqueness (pre-placement, protocol item 1) ---------------
    rng = np.random.default_rng(11)
    idx = rng.choice(np.flatnonzero(foot), size=400_000, replace=False)
    surf_corr_edge = spearman(surface.ravel()[idx], edge.ravel()[idx])
    print(f"[surface] spearman(surface, edge-only) = {surf_corr_edge:.4f}")

    # --- protocol segment holdout -------------------------------------------
    fold_parent_cache = {}

    def build_parent(visible):
        key = int(visible.sum())
        if key not in fold_parent_cache:
            r0_fold, _ = parent_mod.rebuild_r0_mask(h19, foot, visible)
            fold_parent_cache[key] = r0_fold
        return fold_parent_cache[key]

    def build_candidate(visible):
        cand, _ = bstep.build_bstep_candidate(
            build_parent(visible), surface, foot, visible,
            retain_fraction=RETAIN, corridor_px=CORRIDOR,
            retain_score_surface=edge if RETAIN_BY_EDGE else None)
        return cand

    hold = holdout.run_segment_holdout(build_parent, build_candidate, cat, foot)
    print(f"[holdout] parent {hold['pooled_holdout_dti_parent']:.4f} "
          f"candidate {hold['pooled_holdout_dti_candidate']:.4f} "
          f"diff {hold['diff_candidate_minus_parent']:+.4f} "
          f"CI95 {hold['diff_ci95_bootstrap_segments']}")

    # --- final candidate on the full catalogue ------------------------------
    cand, diag = bstep.build_bstep_candidate(r0, surface, foot, cat,
                                         retain_fraction=RETAIN,
                                         corridor_px=CORRIDOR,
                                         retain_score_surface=edge if RETAIN_BY_EDGE else None)
    assert int(cand.sum()) == int(r0.sum()) == 37_654, diag

    stem0 = f"gems89-{AXIS_VALUE}-{DATE}"
    tmp_nan = ROOT / "releases" / f"_tmp_{stem0}.tif"
    write_submission(tmp_nan, cand, foot, encoding="nan")
    sha_nan = sha256_file(tmp_nan)
    stem = f"{stem0}-{sha_nan[:8]}"
    path_nan = ROOT / "releases" / f"{stem}.tif"
    path_zeros = ROOT / "releases" / f"{stem}-zeros.tif"
    tmp_nan.rename(path_nan)
    write_submission(path_zeros, cand, foot, encoding="zeros")
    sha_zeros = sha256_file(path_zeros)

    # --- hard gates (independent of holdout) --------------------------------
    import csv
    ledger_hashes = set()
    with open(ROOT / "ledger/submissions.csv") as fh:
        for row in csv.DictReader(fh):
            for k in ("sha256", "sha256_zeros"):
                if row.get(k):
                    ledger_hashes.add(row[k])
    gates = {}
    for path, enc in ((path_nan, True), (path_zeros, False)):
        ok, results = gate_release(
            path, contract, footprint=foot, dots_mask=cand,
            require_nan_outside=enc, ledger_hashes=ledger_hashes,
            min_clearance_px=0.0,
            clearance_raster=cat_raw)
        gates[path.name] = {"ok": ok, "results": results}
        print(f"[gates] {path.name}: ok={ok}")

    # --- dot uniqueness vs parent + every registry release mask -------------
    overlaps = {"parent_R0": overlap_within_3px(cand, r0)}
    worst_file, worst_val = None, -1.0
    for p in sorted((ROOT / "releases").glob("*-zeros.tif")):
        if p.name == path_zeros.name:
            continue
        other = tifffile.imread(p) == 1.0
        v = overlap_within_3px(cand, other)
        if v > worst_val:
            worst_file, worst_val = p.name, v
    overlaps["worst_releases_file"] = worst_file
    overlaps["worst_releases_overlap"] = worst_val
    dens_corr = spearman(block_density(cand, foot), block_density(r0, foot))
    print(f"[uniqueness] overlap<=3px vs R0 {overlaps['parent_R0']:.3f}; "
          f"worst release {worst_val:.3f} ({worst_file}); "
          f"5km-density spearman vs R0 {dens_corr:.3f}")

    report = {
        "stem": stem, "axis": "BSTP", "value": AXIS_VALUE, "date": DATE,
        "parent": "h33-h33-2-b2", "n_dots": int(cand.sum()),
        "sha256_nan": sha_nan, "sha256_zeros": sha_zeros,
        "build_diag": diag, "surface_diag": surf_diag, "edge_diag": edge_diag,
        "leakage_canary": canary,
        "surface_spearman_vs_edge_only": surf_corr_edge,
        "uniqueness": {**overlaps, "density_spearman_5km_vs_R0": dens_corr},
        "gates_ok": {k: v["ok"] for k, v in gates.items()},
    }
    (ROOT / f"registry/build_report_{AXIS_VALUE}.json").write_text(
        json.dumps(report, indent=1) + "\n")
    (ROOT / f"registry/holdout_{AXIS_VALUE}.json").write_text(
        json.dumps(hold, indent=1) + "\n")
    for name, g in gates.items():
        print(name, json.dumps(g["results"]))
    print(f"[done] {stem}")
    return 0 if all(v["ok"] for v in gates.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
