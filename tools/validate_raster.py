#!/usr/bin/env python3
"""Standalone format validation of the release rasters.

Runs without the competition data: the grid contract is the committed
registry/grid_contract.json, extracted from sample_submission.tif at build time.
Used by CI and by the human before uploading.

The gates that need the catalogue (zero catalogue mass, clearance) are run only
when $GEMSDOE_DATA is present; otherwise they are reported as SKIPPED and the
receipt says so explicitly.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe import grid, validate  # noqa: E402


def main():
    contract = json.loads((ROOT / "registry" / "grid_contract.json").read_text())
    files = sorted((ROOT / "releases").glob("*.tif"))
    if not files:
        print("no release rasters found")
        return 1

    data_root = Path(os.environ.get("GEMSDOE_DATA", ROOT / "data"))
    cat_path = data_root / "existing_faults.tif"
    sample_path = data_root / "sample_submission.tif"
    footprint = None
    catalogue = None
    if cat_path.exists() and sample_path.exists():
        footprint = np.isfinite(grid.read_back(sample_path)[0])
        catalogue = grid.read_back(cat_path)[0]
        print(f"[data] footprint and catalogue loaded from {data_root}")
    else:
        print(f"[data] {data_root} absent -> catalogue gates SKIPPED (format-only run)")

    receipts = {}
    all_ok = True
    for path in files:
        arr = grid.read_back(path)[0]
        dots = np.nan_to_num(arr) > 0
        nan_enc = bool(np.isnan(arr).any())
        ok, results = validate.gate_release(
            path, contract,
            footprint=footprint, dots_mask=dots,
            require_nan_outside=True if nan_enc else False,
            min_clearance_px=0.0,
            clearance_raster=catalogue,
        )
        skipped = []
        if catalogue is None:
            skipped = ["zero_catalogue_mass", "catalogue_clearance"]
        all_ok &= ok
        receipts[path.name] = {
            "ok": ok,
            "encoding": "nan" if nan_enc else "zeros",
            "sha256": grid.sha256_file(path),
            "n_dots": int(dots.sum()),
            "gates": results,
            "skipped": skipped,
        }
        print(f"{'PASS' if ok else 'FAIL'}  {path.name}  dots={int(dots.sum())}  "
              f"enc={'nan' if nan_enc else 'zeros'}")
        for r in results:
            if not r["ok"]:
                print(f"      FAILED: {r['gate']}  {r['detail']}")

    (ROOT / "registry" / "format_receipts.json").write_text(
        json.dumps(receipts, indent=1) + "\n")
    print(f"\n{len(files)} file(s); all gates pass: {all_ok}")
    return 0 if all_ok else 2


if __name__ == "__main__":
    sys.exit(main())
