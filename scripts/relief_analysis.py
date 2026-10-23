#!/usr/bin/env python3
"""AXIS = RELIEF: measure the parent's tercile allocation before building anything.

Produces evidence/relief_analysis.json:
  * det_elev (training_features Band 12) tercile edges over the footprint,
  * how the parent's 37,654 dots are allocated across basin / piedmont / range-front,
  * the size of the legal insertion pool in each tercile,
  * off-catalogue SGMC density per tercile (REPORT-ONLY control prior),
  * a leakage canary: single-band AUC of the tercile membership against the
    catalogue and against the off-catalogue SGMC control.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
from scipy.ndimage import distance_transform_edt
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gems89.grid import ROOT, Grid, band_names, git_sha, read_band, utc_now, verify_manifest  # noqa: E402

OUT = ROOT / "evidence" / "relief_analysis.json"
BAND_DET_ELEV = 12
BAND_DET_ELEV_SLOPE = 19
MIN_SEP_PX = 2.8284271247461903  # 2*sqrt(2): the spacing lock the SNAP lane proved necessary
COLLAR_PX = 3.0


def main() -> int:
    verified = verify_manifest()
    grid = Grid(verified)
    names = band_names()
    det = read_band(verified, BAND_DET_ELEV)
    slope = read_band(verified, BAND_DET_ELEV_SLOPE)
    r0 = grid.read_mask(verified["parent_r0_zeros"])
    h19_5 = grid.read_mask(verified["anc_h19_5"])

    names_by_idx = {i + 1: n for i, n in enumerate(names)}
    vals = det[grid.foot]
    finite = np.isfinite(vals)
    edges = [float(x) for x in np.percentile(vals[finite], [100 / 3, 200 / 3])]

    # tercile index per footprint cell: 0 = basin (low), 1 = piedmont, 2 = range-front (high)
    terr = np.full(det.shape, -1, np.int8)
    inside = grid.foot & np.isfinite(det)
    terr[inside & (det <= edges[0])] = 0
    terr[inside & (det > edges[0]) & (det <= edges[1])] = 1
    terr[inside & (det > edges[1])] = 2

    with __import__("rasterio").open(verified["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & grid.foot
    sgmc_off = sgmc & ~grid.catalogue

    d_dot = distance_transform_edt(~r0)
    pool_base = h19_5 & grid.foot & (grid.d_cat > COLLAR_PX) & ~r0 & (d_dot >= MIN_SEP_PX)

    labels = ["basin", "piedmont", "range_front"]
    rows = []
    for t, label in enumerate(labels):
        m = terr == t
        n_cells = int(m.sum())
        dots = int((r0 & m).sum())
        rows.append({
            "tercile": label,
            "det_elev_range_m": [None if t == 0 else edges[t - 1], None if t == 2 else edges[t]],
            "footprint_cells": n_cells,
            "parent_dots": dots,
            "parent_dot_density": dots / n_cells if n_cells else 0.0,
            "h19_5_px": int((h19_5 & m).sum()),
            "insertion_pool_px": int((pool_base & m).sum()),
            "sgmc_off_catalogue_px": int((sgmc_off & m).sum()),
            "sgmc_off_density": float((sgmc_off & m).sum() / n_cells) if n_cells else 0.0,
            "mean_det_elev_m": float(det[m].mean()) if n_cells else None,
            "mean_det_elev_slope": float(np.nanmean(slope[m])) if n_cells else None,
        })

    # leakage canary: can any single band separate truth from background at AUC > 0.90?
    def auc(score: np.ndarray, pos: np.ndarray) -> float:
        m = grid.foot & np.isfinite(score)
        y = pos[m]
        if y.all() or not y.any():
            return float("nan")
        return float(roc_auc_score(y, score[m]))

    canary = {
        "det_elev_vs_catalogue": auc(det, grid.catalogue),
        "det_elev_vs_sgmc_off_catalogue": auc(det, sgmc_off),
        "det_elev_slope_vs_catalogue": auc(slope, grid.catalogue),
        "tercile_vs_catalogue_auc": auc(terr.astype(np.float64), grid.catalogue),
        "threshold": 0.90,
        "verdict": "PASS" if max(abs(auc(det, grid.catalogue) - 0.5),
                                 abs(auc(det, sgmc_off) - 0.5)) < 0.40 else "INVESTIGATE",
    }

    report = {
        "schema": "gems89.relief-analysis.v1",
        "generated_utc": utc_now(),
        "git_sha": git_sha(),
        "band": {"index": BAND_DET_ELEV, "name": names_by_idx[BAND_DET_ELEV],
                 "slope_index": BAND_DET_ELEV_SLOPE, "slope_name": names_by_idx[BAND_DET_ELEV_SLOPE]},
        "tercile_edges_m": edges,
        "terciles": rows,
        "invariants": {"min_sep_px": MIN_SEP_PX, "collar_px": COLLAR_PX,
                       "footprint_px": int(grid.foot.sum()), "catalogue_px": int(grid.catalogue.sum())},
        "canary": canary,
        "note": "PROXY control = off-catalogue SGMC only. It is never a gate and never a score.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
