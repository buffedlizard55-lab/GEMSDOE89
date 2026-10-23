#!/usr/bin/env python3
"""Rebuild parent R0 (h33-h33-2-b2) from its recorded recipe and match its SHA-256.

Session start gate (brief sec.5):
  "verify manifest hashes; rebuild R0 and match its sha256 (if you cannot, stop
   and report; never approximate the parent)"

Recorded upstream recipe (buffedlizard55-lab/GEMSDOE32):
  * footprint = np.isfinite(sample_submission.tif)
  * catalogue = (existing_faults.tif > 0) & footprint   (byte-identical to labels.tif)
  * base      = (parent_base_02708.tif > 0)             (GEMSDOE28 h27-4-r1-solo-d2-8, 40,199 dots)
  * mask      = base & (distance_transform_edt(~catalogue) > 2) & footprint & ~catalogue
  * emit      = GTiff float32, deflate/predictor=3/zlevel=9/tiled 256x256,
                nodata=None (zeros twin) or nodata=NaN (nan twin).

Fails closed (exit code 2) if any manifest hash or either rebuilt R0 SHA-256
differs from the pinned values.
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
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe.grid import sha256_file  # noqa: E402

EXPECTED_R0_DOTS = 37_654
EXPECTED_BASE_DOTS = 40_199
EXPECTED_FOOTPRINT_PX = 5_167_373
EXPECTED_R0_ZEROS_SHA256 = "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
EXPECTED_R0_NAN_SHA256 = "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd"
EXPECTED_BASE_SHA256 = "ab02300152248fdda04e988e2cd2a0c13f35eec42fcf670a15e8b76b19e24a73"


def _git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def verify_manifest(manifest: dict, data_root: Path) -> dict:
    out = {}
    for entry in manifest["files"]:
        p = data_root / entry["local"]
        if not p.exists():
            out[entry["id"]] = {"present": False, "ok": False}
            continue
        sha = sha256_file(p)
        size = p.stat().st_size
        out[entry["id"]] = {
            "present": True,
            "ok": sha == entry["sha256"] and size == entry["bytes"],
            "sha256": sha,
            "expected_sha256": entry["sha256"],
            "bytes": size,
            "expected_bytes": entry["bytes"],
        }
    return out


def main() -> int:
    t0 = time.time()
    manifest = json.loads((ROOT / "registry" / "data_manifest.json").read_text())
    data_root = Path(
        os.environ.get(
            manifest.get("data_root_env", "GEMSDOE_DATA"),
            ROOT / manifest.get("data_root_default", "data"),
        )
    )
    ver = verify_manifest(manifest, data_root)
    bad = {k: v for k, v in ver.items() if not v.get("ok")}
    if bad:
        print(json.dumps({"ERROR": "manifest verification failed", "failed": bad}, indent=1))
        return 2
    print(f"[ok] verified all {len(ver)} manifest hashes in {data_root}")

    with rasterio.open(data_root / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(data_root / "existing_faults.tif") as ds:
        cat_raw = ds.read(1)
        catalogue = np.isfinite(cat_raw) & (cat_raw > 0) & foot
        template_profile = ds.profile.copy()
    with rasterio.open(data_root / "parent_base_02708.tif") as ds:
        base_raw = ds.read(1)
        base = np.isfinite(base_raw) & (base_raw > 0)
    with rasterio.open(data_root / "scored_h19_5.tif") as ds:
        h19 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot

    d_cat = distance_transform_edt(~catalogue)
    mask = base & (d_cat > 2.0) & foot & ~catalogue

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        rebuilt_hashes = {}
        for mode, nodata_val in [("zeros", None), ("nan", float("nan"))]:
            prof = template_profile.copy()
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
                nodata=nodata_val,
            )
            arr = np.where(
                foot,
                mask.astype(np.float32),
                np.nan if mode == "nan" else 0.0,
            ).astype(np.float32)
            out_p = tmp / f"r0_{mode}.tif"
            with rasterio.open(out_p, "w", **prof) as dst:
                dst.write(arr, 1)
            rebuilt_hashes[mode] = sha256_file(out_p)

    checks = {
        "manifest_all_8_verified": not bad,
        "footprint_px_5167373": int(foot.sum()) == EXPECTED_FOOTPRINT_PX,
        "base_dots_40199": int(base.sum()) == EXPECTED_BASE_DOTS,
        "r0_dots_37654": int(mask.sum()) == EXPECTED_R0_DOTS,
        "all_dots_on_h19_5_ridge_support": int((mask & h19).sum()) == EXPECTED_R0_DOTS,
        "zero_dots_on_catalogue": int((mask & catalogue).sum()) == 0,
        "zero_dots_within_2px_of_catalogue": int((d_cat[mask] <= 2.0).sum()) == 0,
        "rebuilt_zeros_matches_pin": rebuilt_hashes["zeros"] == EXPECTED_R0_ZEROS_SHA256,
        "rebuilt_nan_matches_pin": rebuilt_hashes["nan"] == EXPECTED_R0_NAN_SHA256,
        "base_sha256_matches_pin": ver["parent_base_02708"]["sha256"] == EXPECTED_BASE_SHA256,
    }
    ok = all(checks.values())

    report = {
        "id": "h33-h33-2-b2",
        "sha256": rebuilt_hashes["zeros"],
        "sha256_nan": rebuilt_hashes["nan"],
        "sha256_expected_from_upstream_ledger": EXPECTED_R0_ZEROS_SHA256,
        "sha256_nan_expected_from_upstream_audit": EXPECTED_R0_NAN_SHA256,
        "match": ok,
        "rebuilt_from_recipe": True,
        "git_sha": _git_sha(),
        "recipe": {
            "base": "parent_base_02708.tif (GEMSDOE28 h27-4-r1-solo-d2-8, sha256 ab0230015224..., 40,199 dots)",
            "ridge_support": "scored_h19_5.tif (19GEMSDOE h19-5, sha256 ec1f9b56b83c..., 121,131 px; contains 37,654/37,654 R0 dots)",
            "collar_prune": "mask = base & (distance_transform_edt(~catalogue) > 2.0) & footprint & ~catalogue",
            "writer": "GTiff float32, deflate/predictor=3/zlevel=9/tiled 256x256",
            "upstream_source": "buffedlizard55-lab/GEMSDOE32@078f3cea1bc7 src/gems32/hypotheses33.py:307-329",
        },
        "n_dots": int(mask.sum()),
        "values": {"unique": [0.0, 1.0], "dots_are_unit_mass": True},
        "grid": {"shape": list(mask.shape), "dtype": "float32"},
        "all_dots_inside_footprint": bool((mask & ~foot).sum() == 0),
        "catalogue": {
            "min_distance_px": float(d_cat[mask].min()),
            "dots_below_3px": int((d_cat[mask] < 3.0).sum()),
            "dots_at_or_below_3px": int((d_cat[mask] <= 3.0).sum()),
            "dots_within_2px": int((d_cat[mask] <= 2.0).sum()),
            "dots_on_catalogue": int((mask & catalogue).sum()),
        },
        "claimed_live_score": {
            "value": 0.2778,
            "evidence_class": "CLAIM",
            "receipt": "none in this repo",
        },
        "checks": checks,
        "elapsed_s": round(time.time() - t0, 2),
    }
    out_json = ROOT / "registry" / "parent_verification.json"
    out_json.write_text(json.dumps(report, indent=1) + "\n")

    for k, v in checks.items():
        print(f"  {'PASS' if v else 'FAIL'}  {k}")
    print(f"[r0] rebuilt zeros sha256 = {rebuilt_hashes['zeros']}")
    print(f"[r0] rebuilt nan   sha256 = {rebuilt_hashes['nan']}")
    if not ok:
        print("[ERROR] R0 rebuild check failed -- stopping as required by brief sec.5.")
        return 2
    print(f"[ok] R0 rebuilt byte-identically from recipe ({report['elapsed_s']}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
