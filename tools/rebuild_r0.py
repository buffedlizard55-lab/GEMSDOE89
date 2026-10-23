#!/usr/bin/env python3
"""Rebuild Parent R0 (h33-h33-2-b2) from its recorded recipe and assert SHA-256.

Implements Brief Section 5's start gate:
  "verify manifest hashes; rebuild R0 and match its sha256 (if you cannot, stop
   and report; never approximate the parent)"

Rebuilds d28 (44,090 dots) from scored_h19_5.tif via BFS dot_thin(r_min=2.8),
applies the B=2 px catalogue flank prune (d_cat > 2.0 -> 37,654 dots), emits
both -zeros and -nan GeoTIFFs, and asserts byte-for-bit SHA-256 identity against
c55bafc4... (zeros) and baeae321... (nan).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe import grid, parent  # noqa: E402


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"


def main() -> int:
    t0 = time.time()
    manifest = json.loads((ROOT / "registry" / "data_manifest.json").read_text())
    data_root = Path(
        os.environ.get(
            manifest.get("data_root_env", "GEMSDOE_DATA"),
            ROOT / manifest.get("data_root_default", "data"),
        )
    )

    verified = {}
    for entry in manifest["files"]:
        if entry.get("unverified"):
            print(f"[skip] unverified report-only pin {entry['id']} (IRREGULARITIES item 8)")
            continue
        p = data_root / entry["local"]
        if not p.exists():
            print(f"STOP: missing pinned input {entry['id']} at {p}")
            return 2
        got = grid.sha256_file(p)
        if got != entry["sha256"]:
            print(f"STOP: sha256 mismatch on {entry['id']}: got {got}, expected {entry['sha256']}")
            return 2
        verified[entry["id"]] = got
    print(f"[ok] verified {len(verified)} manifest sha256 pins (unverified entries skipped)")

    sample_arr, _ = grid.read_template(data_root / "sample_submission.tif")
    foot = np.isfinite(sample_arr)
    cat_arr = grid.read_back(data_root / "existing_faults.tif")[0]
    cat = (np.isfinite(cat_arr) & (cat_arr > 0)) & foot
    h19_arr = grid.read_back(data_root / "scored_h19_5.tif")[0]
    h19 = (np.isfinite(h19_arr) & (h19_arr > 0)) & foot
    # the scored d28 ancestor pin lives under manifest id parent_ancestor_d28 (local d28.tif)
    d28_local = next(f["local"] for f in manifest["files"] if f["id"] == "parent_ancestor_d28")
    d28_pin_arr = grid.read_back(data_root / d28_local)[0]
    d28_pin = (np.isfinite(d28_pin_arr) & (d28_pin_arr > 0)) & foot
    r0_pin_arr = grid.read_back(data_root / "parent_r0_zeros.tif")[0]
    r0_pin = (r0_pin_arr > 0) & foot

    r0_mask, d28_mask = parent.rebuild_r0_mask(h19, foot, cat, r_min=2.8, collar_px=2.0)

    d28_equal = bool(np.array_equal(d28_mask, d28_pin))
    r0_mask_equal = bool(np.array_equal(r0_mask, r0_pin))
    if not d28_equal or not r0_mask_equal or int(r0_mask.sum()) != parent.EXPECTED_R0_DOTS:
        print(
            f"STOP: R0 mask rebuild mismatch (d28_equal={d28_equal}, "
            f"r0_mask_equal={r0_mask_equal}, n_dots={int(r0_mask.sum())})"
        )
        return 2

    # Byte-level GeoTIFF SHA-256 check using the upstream GDAL/rasterio profile
    try:
        import rasterio
    except ImportError:
        print("STOP: rasterio is required to verify exact upstream GDAL deflate GeoTIFF bytes")
        return 2

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        with rasterio.open(data_root / "sample_submission.tif") as src:
            prof = src.profile.copy()
        prof.update(
            driver="GTiff",
            dtype="float32",
            count=1,
            compress="deflate",
            predictor=3,
            zlevel=9,
            tiled=True,
            blockxsize=256,
            blockysize=256,
            nodata=None,
        )
        zeros_out = tmp / "r0_zeros.tif"
        nan_out = tmp / "r0_nan.tif"
        with rasterio.open(zeros_out, "w", **prof) as dst:
            dst.write(np.where(foot, r0_mask.astype(np.float32), 0.0).astype(np.float32), 1)
        prof_nan = prof.copy()
        prof_nan["nodata"] = float("nan")
        with rasterio.open(nan_out, "w", **prof_nan) as dst:
            dst.write(np.where(foot, r0_mask.astype(np.float32), np.nan).astype(np.float32), 1)

        rebuilt_zeros_sha = grid.sha256_file(zeros_out)
        rebuilt_nan_sha = grid.sha256_file(nan_out)

    zeros_match = rebuilt_zeros_sha == parent.R0_ZEROS_SHA256
    nan_match = rebuilt_nan_sha == parent.R0_NAN_SHA256
    if not (zeros_match and nan_match):
        print(
            f"STOP: R0 GeoTIFF sha256 mismatch!\n"
            f"  rebuilt zeros = {rebuilt_zeros_sha} (want {parent.R0_ZEROS_SHA256})\n"
            f"  rebuilt nan   = {rebuilt_nan_sha} (want {parent.R0_NAN_SHA256})"
        )
        return 2

    d_cat = distance_transform_edt(~cat)
    receipt = {
        "id": parent.PARENT_ID,
        "rebuilt_from_recipe": True,
        "recipe": "r0 = dot_thin(scored_h19_5, r_min=2.8) & (d_cat > 2.0) & footprint & ~catalogue",
        "git_sha": git_sha(),
        "h19_5_sha256": verified["scored_h19_5"],
        "h19_5_pixels": int(h19.sum()),
        "d28_sha256": verified["parent_ancestor_d28"],
        "d28_dots_rebuilt": int(d28_mask.sum()),
        "d28_exact_mask_match": d28_equal,
        "sha256": rebuilt_zeros_sha,
        "sha256_expected_from_upstream_ledger": parent.R0_ZEROS_SHA256,
        "sha256_nan": rebuilt_nan_sha,
        "sha256_nan_expected": parent.R0_NAN_SHA256,
        "match": bool(zeros_match and nan_match and r0_mask_equal),
        "n_dots": int(r0_mask.sum()),
        "values": {"unique": [0.0, 1.0], "dots_are_unit_mass": True},
        "grid": {"shape": list(r0_mask.shape), "dtype": "float32"},
        "all_dots_inside_footprint": bool((r0_mask & ~foot).sum() == 0),
        "catalogue": {
            "min_distance_px": float(d_cat[r0_mask].min()),
            "dots_within_3px_strict": int((d_cat[r0_mask] < 3.0).sum()),
            "dots_within_3px_inclusive": int((d_cat[r0_mask] <= 3.0).sum()),
            "dots_within_2px": int((d_cat[r0_mask] <= 2.0).sum()),
            "dots_on_catalogue": int((r0_mask & cat).sum()),
        },
        "claimed_live_score": {
            "value": 0.2778,
            "evidence_class": "CLAIM",
            "receipt": "none in this repo",
        },
        "elapsed_seconds": round(time.time() - t0, 2),
        "note": (
            "Rebuilt bit-for-bit from pinned scored_h19_5.tif via BFS dot_thin(2.8) + "
            "B=2 catalogue flank prune, matching both upstream zeros (c55bafc4...) and "
            "nan (baeae321...) GeoTIFF sha256 digests."
        ),
    }
    out_path = ROOT / "registry" / "parent_verification.json"
    out_path.write_text(json.dumps(receipt, indent=1) + "\n")
    print(f"[ok] R0 rebuilt byte-identical: zeros={rebuilt_zeros_sha[:16]}... nan={rebuilt_nan_sha[:16]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
