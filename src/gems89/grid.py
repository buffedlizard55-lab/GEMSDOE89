"""Grid, IO and format-gate helpers for the GEMSDOE89 session (DrivenData #306).

The competition grid is fixed by sample_submission.tif:
EPSG:32611, 3292 x 3730, 100 m, transform (100, 0, 243350, 0, -100, 4508550).
The parent's writer profile is reproduced exactly so that an R0 rebuild can be
compared to the published artefact at the byte level, not just the pixel level.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "registry" / "data_manifest.json"

EXPECTED = dict(crs="EPSG:32611", width=3292, height=3730, dtype="float32", count=1)
EXPECTED_BOUNDS = (243350.0, 4504720.0, 572550.0, 4508550.0)  # left, bottom, right, top


# --------------------------------------------------------------------------
# hashing / provenance
# --------------------------------------------------------------------------
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_sha() -> str:
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # pragma: no cover - only when git is absent
        return "unknown"


def utc_now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------
# pinned inputs
# --------------------------------------------------------------------------
def verify_manifest(path: Path | None = None) -> dict[str, Path]:
    """Fail-closed SHA-256 + byte-length check of every pinned input."""
    manifest = json.loads((path or MANIFEST).read_text(encoding="utf-8"))
    out: dict[str, Path] = {}
    problems = []
    for entry in manifest["files"]:
        p = ROOT / entry["dest"]
        if not p.is_file():
            problems.append(f"{entry['id']}: missing {entry['dest']}")
            continue
        if p.stat().st_size != entry["bytes"]:
            problems.append(f"{entry['id']}: bytes {p.stat().st_size} != {entry['bytes']}")
            continue
        if sha256_file(p) != entry["sha256"]:
            problems.append(f"{entry['id']}: sha256 mismatch")
            continue
        out[entry["id"]] = p
    if problems:
        raise SystemExit("PIN VERIFICATION FAILED:\n  " + "\n  ".join(problems))
    return out


# --------------------------------------------------------------------------
# reference grid
# --------------------------------------------------------------------------
class Grid:
    """The competition grid plus footprint, catalogue and catalogue distance."""

    def __init__(self, verified: dict[str, Path]):
        with rasterio.open(verified["sample_submission"]) as ds:
            self.foot = np.isfinite(ds.read(1))
            self.transform = ds.transform
            self.crs = ds.crs
            self.shape = (ds.height, ds.width)
            self.sample_profile = ds.profile.copy()
        with rasterio.open(verified["existing_faults"]) as ds:
            raw = ds.read(1)
            self.faults_profile = ds.profile.copy()
            self.catalogue = (raw > 0) & self.foot
        self.d_cat = distance_transform_edt(~self.catalogue)
        self.profile_zeros = self.faults_profile.copy()
        self.profile_zeros.update(
            driver="GTiff", dtype="float32", count=1, compress="deflate",
            predictor=3, zlevel=9, tiled=True, blockxsize=256, blockysize=256,
            nodata=None,
        )
        self.profile_nan = self.profile_zeros.copy()
        self.profile_nan.update(nodata=np.nan)

    # -- read / write ------------------------------------------------------
    def read_mask(self, path: Path) -> np.ndarray:
        """Binary dot mask from a raster (NaN/inf or <=0 read as no dot)."""
        with rasterio.open(path) as ds:
            a = ds.read(1).astype(np.float64)
        return (np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0) > 0.0) & self.foot

    def write(self, path: Path, mask: np.ndarray, nan_outside: bool) -> str:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        prof = self.profile_nan if nan_outside else self.profile_zeros
        fill = np.nan if nan_outside else 0.0
        arr = np.where(self.foot, mask.astype(np.float32), fill).astype(np.float32)
        with rasterio.open(path, "w", **prof) as dst:
            dst.write(arr, 1)
        return sha256_file(path)

    # -- gates -------------------------------------------------------------
    def validate(self, path: Path, *, nan_outside: bool) -> dict:
        """MUST-pass gates from Brief v2 section 6.  Raises on any failure."""
        path = Path(path)
        with rasterio.open(path) as ds:
            a = ds.read(1)
            prof = ds.profile
            crs, shape, dtype, count = ds.crs, (ds.height, ds.width), ds.dtypes[0], ds.count
            transform, nodata = ds.transform, ds.nodata
        checks: dict[str, object] = {}
        checks["crs"] = (str(crs), str(crs) == EXPECTED["crs"])
        checks["shape"] = (list(shape), shape == (EXPECTED["height"], EXPECTED["width"]))
        checks["dtype"] = (dtype, dtype == EXPECTED["dtype"])
        checks["count"] = (int(count), int(count) == EXPECTED["count"])
        checks["transform"] = (list(transform)[:6], transform == self.transform)
        inside = a[self.foot]
        outside = a[~self.foot]
        checks["no_nan_inside"] = (int(np.isnan(inside).sum()), not np.isnan(inside).any())
        checks["values_in_0_1"] = (float(np.nanmin(inside)), float(np.nanmax(inside)))
        checks["values_in_0_1_ok"] = bool(np.nanmin(inside) >= 0.0 and np.nanmax(inside) <= 1.0)
        if nan_outside:
            checks["outside_nan"] = (int(np.isnan(outside).sum()), bool(np.isnan(outside).all()))
            checks["nodata_is_nan"] = (str(nodata), bool(nodata is not None and np.isnan(nodata)))
        else:
            checks["outside_zero"] = (float(outside.max()), bool((outside == 0.0).all()))
        dots = (np.nan_to_num(a, nan=0.0) > 0) & self.foot
        checks["n_dots"] = (int(dots.sum()), int(dots.sum()) > 0)
        checks["catalogue_mass"] = (int((dots & self.catalogue).sum()),
                                    int((dots & self.catalogue).sum()) == 0)
        dvals = self.d_cat[dots] if dots.any() else np.array([np.inf])
        checks["min_d_cat_px"] = (float(dvals.min()), bool(dvals.min() > 0))
        checks["n_within_2px"] = (int((dvals <= 2.0).sum()), True)
        checks["n_within_3px"] = (int((dvals <= 3.0).sum()), True)
        checks["sha256"] = sha256_file(path)
        bad = [k for k, v in checks.items() if isinstance(v, tuple) and v[1] is False]
        if bad:
            raise AssertionError(f"FORMAT GATE FAILURE on {path.name}: {bad} :: "
                                 f"{ {k: checks[k] for k in bad} }")
        return checks

    def terciles(self, band: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Footprint tercile edges of a continuous band (33.3 / 66.7 percentiles)."""
        vals = band[self.foot]
        vals = vals[np.isfinite(vals)]
        edges = np.percentile(vals, [100.0 / 3.0, 200.0 / 3.0])
        return edges, vals


def band_names() -> list[str]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        if entry["id"] == "training_features":
            return list(entry["band_names"])
    raise KeyError("training_features not in manifest")


def read_band(verified: dict[str, Path], index: int) -> np.ndarray:
    """Read one feature band (1-based index) windowed into memory."""
    with rasterio.open(verified["training_features"]) as ds:
        return ds.read(index).astype(np.float64)
