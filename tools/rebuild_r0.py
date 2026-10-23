#!/usr/bin/env python3
"""Rebuild parent R0 from its dot mask and match the recorded sha256.

Start gate of the session brief: "rebuild R0 and match its sha256".  This
script

  1. verifies data/parent_r0_zeros.tif against registry/data_manifest.json,
  2. extracts the dot mask (37,654 unit dots, zeros-outside encoding),
  3. re-emits the raster with the parent writer's exact GeoTIFF profile
     (rasterio, deflate zlevel 9, predictor 3, tiled 256x256, template
     profile for CRS/transform, no nodata tag for the zeros encoding),
  4. requires the emitted bytes to hash to c55bafc470054e8271dcb89347a17e07
     fefe50de6af6e6ba6c4b169ef7ab6fa9 -- the sha256_zeros recorded for
     h33-h33-2-b2 in the upstream ledger -- and to be pixel-identical to the
     pinned parent.

If step 4 fails the script exits non-zero and no variant may be built:
the parent would have to be treated as unreproducible (never approximate).

Note (IRREGULARITIES.md item 1): this reproduces R0's *bytes* from its mask
and encoder.  The recipe that SELECTED the 37,654 pixels still does not exist
in this repo; artifact-level identity is what the ledger pins.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe.grid import sha256_file  # noqa: E402

PARENT_SHA256 = "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
EXPECTED_DOTS = 37654
OUT = ROOT / "data" / "_rebuild_r0_check.tif"


def main() -> int:
    manifest = json.loads((ROOT / "registry" / "data_manifest.json").read_text())
    env = manifest.get("data_root_env", "GEMSDOE_DATA")
    data_root = Path(os.environ.get(env, ROOT / manifest.get("data_root_default", "data")))
    parent_path = data_root / "parent_r0_zeros.tif"
    template_path = data_root / "sample_submission.tif"
    entry = next(f for f in manifest["files"] if f["id"] == "parent_r0_zeros")

    sha_file = sha256_file(parent_path)
    if sha_file != entry["sha256"]:
        print(f"FAIL pinned parent hash mismatch: {sha_file}")
        return 2

    import rasterio
    import tifffile

    parent = tifffile.imread(parent_path)
    dots = parent > 0
    if int(dots.sum()) != EXPECTED_DOTS:
        print(f"FAIL parent has {int(dots.sum())} dots, expected {EXPECTED_DOTS}")
        return 2

    with rasterio.open(template_path) as tpl:
        profile = tpl.profile.copy()
        foot = np.isfinite(tpl.read(1))
    profile.update(driver="GTiff", dtype="float32", count=1, compress="deflate",
                   predictor=3, zlevel=9, tiled=True, blockxsize=256,
                   blockysize=256, nodata=None)
    out = np.where(foot, dots.astype(np.float32), 0.0).astype(np.float32)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(OUT, "w", **profile) as dst:
        dst.write(out, 1)

    sha_rebuild = sha256_file(OUT)
    arr = tifffile.imread(OUT)
    identical = bool(np.array_equal(np.nan_to_num(arr, nan=-1.0),
                                    np.nan_to_num(parent, nan=-1.0)))
    ok = sha_rebuild == PARENT_SHA256 and sha_rebuild == sha_file and identical
    print(f"pinned parent : {sha_file}")
    print(f"rebuilt R0    : {sha_rebuild}")
    print(f"pixel-identical: {identical}   dots: {int(dots.sum())}")
    print("REBUILD MATCH: sha256 c55bafc470054e8271dcb89347a17e07..." if ok else "FAIL: rebuild does not match the parent")
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main())
