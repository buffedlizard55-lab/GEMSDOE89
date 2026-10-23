#!/usr/bin/env python3
"""AXIS = RELIEF: shift 10% of the parent's mass between det_elev terciles.

Session contract (Brief v2 section 5, AXIS = RELIEF)
----------------------------------------------------
* Parent: R0 = h33-h33-2-b2, 37,654 unit-mass dots, rebuilt byte-exactly.
* Relief: det_elev = training_features Band 12 (detrended elevation, metres),
  split into footprint terciles -> basin (low), piedmont (middle), range-front
  (high).
* Each variant removes k = 10.00 % of the dots (3,765) from the SAME source
  tercile (piedmont, the most populated) and re-inserts k dots in ONE receiving
  tercile.  Count fixed at 37,654.  Dots changed = 2k = 7,530 = 20.00 % of the
  file (inside the 1-50 % band).
* Receiving terciles: basin / range_front / piedmont.  The piedmont arm receives
  where it drained, so its tercile allocation is unchanged: it is the reshuffle
  CONTROL.  Contrasts (basin - control) and (range_front - control) therefore
  isolate the tercile effect from the common remove/insert rule.

Two rules are held CONSTANT across the three variants, so the only variable is
the receiving tercile:

  removal   - the k source-tercile dots with the lowest ``unique_credit``
              (truth-free, from the metric algebra: the credit a dot supplies
              alone).  Ties broken by flat index.  Variants that share a source
              tercile therefore share the removed set exactly.
  insertion - candidates are cells with det_elev_slope >= its footprint 90th
              percentile (sharp ground), inside the receiving tercile, at
              d(catalogue) > 3.0 px, not an existing dot, and >= 2.8284 px
              (2*sqrt2) from every retained dot.  Ranked by distance to the
              nearest retained dot (coverage-greedy, the lineage's own insertion
              rule), accepted in that order with a 2.8284 px lock between added
              dots.

The receiving tercile is NOT allowed to be the source tercile, and the axis is
built once per (parent, axis, value).

Outputs: releases/<id>.tif (+ -zeros twin), releases/<id>.json, and rows in
ledger/submissions.csv.  Rasters are gitignored (competition data-use terms).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems89.grid import Grid, band_names, git_sha, read_band, sha256_file, utc_now, verify_manifest  # noqa: E402
from gems89 import metric  # noqa: E402
from canonical_writer import LIBDEFLATE_LEVEL, write_canonical  # noqa: E402

BAND_DET_ELEV = 12
BAND_DET_ELEV_SLOPE = 19
SLOPE_PCTL = 80.0
MIN_SEP_PX = 2.8284271247461903
COLLAR_PX = 3.0
FRACTION = 0.10
PARENT_ID = "h33-h33-2-b2"
TERCILES = ("basin", "piedmont", "range_front")

# (value, source tercile, receiving tercile)
# All three drain the SAME source tercile, so the only variable is the receiving
# tercile.  `pied10` receives in its own source tercile: a pure reshuffle under an
# unchanged tercile allocation, i.e. the control that measures the common
# remove/insert rule and nothing else.
VARIANTS = (
    ("basin10", "piedmont", "basin"),
    ("rf10", "piedmont", "range_front"),
    ("pied10", "piedmont", "piedmont"),
)


def tercile_grid(det: np.ndarray, foot: np.ndarray, edges) -> np.ndarray:
    terr = np.full(det.shape, -1, np.int8)
    inside = foot & np.isfinite(det)
    terr[inside & (det <= edges[0])] = 0
    terr[inside & (det > edges[0]) & (det <= edges[1])] = 1
    terr[inside & (det > edges[1])] = 2
    return terr


def block(mask: np.ndarray, rows, cols, radius: float) -> None:
    """Mark every cell within `radius` of the given cells (square bounding, disc test)."""
    r = int(np.ceil(radius))
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dy * dy + dx * dx < radius * radius:
                rr, cc = rows + dy, cols + dx
                ok = (rr >= 0) & (rr < mask.shape[0]) & (cc >= 0) & (cc < mask.shape[1])
                mask[rr[ok], cc[ok]] = True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="20261023")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    verified = verify_manifest()
    grid = Grid(verified)
    names = band_names()
    det = read_band(verified, BAND_DET_ELEV)
    slope = read_band(verified, BAND_DET_ELEV_SLOPE)
    r0 = grid.read_mask(verified["parent_r0_zeros"])
    n_parent = int(r0.sum())
    if n_parent != 37_654:
        raise SystemExit(f"parent is not R0: {n_parent} dots")

    fv = det[grid.foot]
    edges = np.percentile(fv[np.isfinite(fv)], [100 / 3, 200 / 3])
    terr = tercile_grid(det, grid.foot, edges)

    sv = slope[grid.foot]
    slope_thr = float(np.percentile(sv[np.isfinite(sv)], SLOPE_PCTL))

    k = int(round(FRACTION * n_parent))
    credit = metric.unique_credit(r0)
    yy, xx = np.nonzero(r0)

    off_sgmc = grid.read_mask(verified["sgmc_faults_control"]) & ~grid.catalogue

    releases = ROOT / "releases"
    releases.mkdir(exist_ok=True)
    rows = []
    for value, src_name, dst_name in VARIANTS:
        src_t, dst_t = TERCILES.index(src_name), TERCILES.index(dst_name)
        in_src = terr[yy, xx] == src_t
        if int(in_src.sum()) < k:
            raise SystemExit(f"source tercile {src_name} holds {int(in_src.sum())} < k={k}")
        # ---- removal: lowest unique credit inside the source tercile
        idx = np.flatnonzero(in_src)
        order = idx[np.lexsort((yy[idx] * 10_000 + xx[idx], credit[idx]))]
        removed = order[:k]
        removed_mask = np.zeros(r0.shape, bool)
        removed_mask[yy[removed], xx[removed]] = True
        retained = r0 & ~removed_mask

        # ---- candidate pool in the receiving tercile
        d_dot = distance_transform_edt(~retained)
        pool = (terr == dst_t) & grid.foot & np.isfinite(slope) & (slope >= slope_thr) \
            & (grid.d_cat > COLLAR_PX) & ~retained & (d_dot >= MIN_SEP_PX)
        py, px = np.nonzero(pool)
        if py.size < k:
            raise SystemExit(f"pool in {dst_name} holds {py.size} < k={k}")
        rank = np.lexsort((py * 10_000 + px, -d_dot[py, px]))
        py, px = py[rank], px[rank]

        # ---- accept in ranked order with the spacing lock
        blocked = np.zeros(r0.shape, bool)
        block(blocked, *np.nonzero(retained), MIN_SEP_PX)
        added = np.zeros(r0.shape, bool)
        accepted = 0
        for y, x in zip(py, px):
            if blocked[y, x]:
                continue
            added[y, x] = True
            block(blocked, np.array([y]), np.array([x]), MIN_SEP_PX)
            accepted += 1
            if accepted == k:
                break
        if accepted != k:
            raise SystemExit(f"only {accepted}/{k} insertions possible in {dst_name}")

        variant = retained | added
        n_var = int(variant.sum())
        if n_var != n_parent:
            raise SystemExit(f"count changed {n_var} != {n_parent}")
        if int((variant & grid.catalogue).sum()) != 0:
            raise SystemExit("variant emits mass on the catalogue")
        d_add = grid.d_cat[added]
        if d_add.min() <= COLLAR_PX:
            raise SystemExit("an added dot violates the 3 px collar")

        # ---- write both encodings with the parent's exact encoder
        tmp = releases / f".tmp-{value}.tif"
        sha_nan = write_canonical(tmp, variant, grid, nan_outside=True)
        rid = f"{PARENT_ID}-RELIEF{value}-{args.date}-{sha_nan[:8]}"
        nan_path = releases / f"{rid}.tif"
        tmp.replace(nan_path)
        zeros_path = releases / f"{rid}-zeros.tif"
        sha_zeros = write_canonical(zeros_path, variant, grid, nan_outside=False)

        gate_nan = grid.validate(nan_path, nan_outside=True)
        gate_zeros = grid.validate(zeros_path, nan_outside=False)

        # ---- parent diff
        removed_px = r0 & ~variant
        added_px = variant & ~r0
        d_ret = grid.d_cat[retained]
        diff = {
            "n_removed": int(removed_px.sum()),
            "n_added": int(added_px.sum()),
            "n_unchanged": int((r0 & variant).sum()),
            "pct_changed": round(100.0 * (int(removed_px.sum()) + int(added_px.sum())) / n_parent, 4),
            "mean_displacement_px_of_changed": None,  # relocation, not displacement
            "added_min_d_cat_px": float(d_add.min()),
            "added_min_nn_px": None,
            "inherited_min_d_cat_px": float(d_ret.min()),
            "inherited_n_within_3px": int((d_ret <= 3.0).sum()),
            "tercile_allocation_before": {name: int((r0 & (terr == t)).sum()) for t, name in enumerate(TERCILES)},
            "tercile_allocation_after": {name: int((variant & (terr == t)).sum()) for t, name in enumerate(TERCILES)},
        }
        # nearest-neighbour distance of the added dots
        from scipy.spatial import cKDTree
        add_pts = np.argwhere(added)
        others = np.argwhere(variant & ~added)
        nn = cKDTree(others).query(add_pts, k=1)[0]
        diff["added_min_nn_px"] = float(nn.min())
        diff["added_mean_nn_px"] = float(nn.mean())

        # ---- report-only instruments (never gates)
        parent_dti_sgmc = metric.dti_binary(r0, off_sgmc)
        variant_dti_sgmc = metric.dti_binary(variant, off_sgmc)
        parent_dti_cat = metric.dti_binary(r0, grid.catalogue)
        variant_dti_cat = metric.dti_binary(variant, grid.catalogue)
        proxy = {
            "instrument": "off-catalogue SGMC control raster (REPORT ONLY)",
            "n_truth_px": int(off_sgmc.sum()),
            "parent_dti": parent_dti_sgmc["dti"],
            "variant_dti": variant_dti_sgmc["dti"],
            "delta": variant_dti_sgmc["dti"] - parent_dti_sgmc["dti"],
            "catalogue_control_parent_dti": parent_dti_cat["dti"],
            "catalogue_control_variant_dti": variant_dti_cat["dti"],
            "catalogue_control_delta": variant_dti_cat["dti"] - parent_dti_cat["dti"],
        }

        receipt = {
            "schema": "gems89.relief-variant.v1",
            "id": rid,
            "parent": PARENT_ID,
            "parent_sha256_zeros": "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
            "axis": "RELIEF",
            "value": value,
            "source_tercile": src_name,
            "receiving_tercile": dst_name,
            "k_dots": k,
            "fraction_of_dots_moved": FRACTION,
            "generated_utc": utc_now(),
            "git_sha": git_sha(),
            "inputs": {"det_elev_band": BAND_DET_ELEV, "det_elev_slope_band": BAND_DET_ELEV_SLOPE,
                       "band_names": {BAND_DET_ELEV: names[BAND_DET_ELEV - 1],
                                      BAND_DET_ELEV_SLOPE: names[BAND_DET_ELEV_SLOPE - 1]}},
            "tercile_edges_m": [float(x) for x in edges],
            "slope_threshold": slope_thr,
            "slope_percentile": SLOPE_PCTL,
            "min_sep_px": MIN_SEP_PX,
            "collar_px": COLLAR_PX,
            "encoder": {"container": "GDAL GTiff tiled 256x256, Predictor=3",
                        "deflate": "libdeflate", "level": LIBDEFLATE_LEVEL},
            "files": {
                "nan": {"path": f"releases/{rid}.tif", "sha256": sha_nan, "bytes": nan_path.stat().st_size},
                "zeros": {"path": f"releases/{rid}-zeros.tif", "sha256": sha_zeros,
                          "bytes": zeros_path.stat().st_size},
            },
            "gate_nan": {k2: v2 for k2, v2 in gate_nan.items()},
            "gate_zeros": {k2: v2 for k2, v2 in gate_zeros.items()},
            "diff_vs_parent": diff,
            "proxy": proxy,
        }
        (releases / f"{rid}.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        rows.append(receipt)
        print(json.dumps({"id": rid, "changed_pct": diff["pct_changed"],
                          "proxy_delta": round(proxy["delta"], 6),
                          "catalogue_control_delta": round(proxy["catalogue_control_delta"], 6),
                          "nan_sha8": sha_nan[:8]}, indent=2))

    (ROOT / "registry" / "relief_build.json").write_text(
        json.dumps({"schema": "gems89.relief-build.v1", "generated_utc": utc_now(),
                    "git_sha": git_sha(), "k": k, "fraction": FRACTION,
                    "tercile_edges_m": [float(x) for x in edges], "slope_threshold": slope_thr,
                    "variants": [r["id"] for r in rows]}, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
