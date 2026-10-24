"""Grid contract for GEMS submissions (EPSG:32611, 100 m, sample grid).

Copied tag-for-tag from sample_submission.tif so that a release is
georeferenced exactly like the competition template.  Everything here is
unit-agnostic about the competition data: the template is passed in, and the
resulting contract is stored as JSON so that CI can re-check releases without
the competition rasters present.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import tifffile

# GeoTIFF tags that define the grid.  Values are the ones in
# sample_submission.tif (sha256 2176d08e...), read at build time and pinned in
# registry/grid_contract.json.
GRID_TAGS = {
    "ModelPixelScaleTag": (100.0, 100.0, 0.0),
    "ModelTiepointTag": (0.0, 0.0, 0.0, 243350.0, 4508550.0, 0.0),
    "GeoAsciiParamsTag": "WGS 84 / UTM zone 11N|WGS 84|",
    "GeoKeyDirectoryTag": (
        1, 1, 0, 7,
        1024, 0, 1, 1, 1025, 0, 1, 1,
        1026, 34737, 22, 0, 2049, 34737, 7, 22,
        2054, 0, 1, 9102, 3072, 0, 1, 32611, 3076, 0, 1, 9001,
    ),
}
NODATA = np.float32("nan")


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_template(path):
    """Return (array, contract dict) for the grid template."""
    a = tifffile.imread(path)
    contract = read_contract_from_tiff(path)
    return a, contract


def read_contract_from_tiff(path) -> dict:
    with tifffile.TiffFile(path) as t:
        p = t.pages[0]
        tags = p.tags
        get = lambda n: list(tags[n].value) if n in tags else None
        scale = tuple(get("ModelPixelScaleTag"))
        tie = tuple(get("ModelTiepointTag"))
        keys = tuple(int(v) for v in get("GeoKeyDirectoryTag"))
        ascii_ = tags["GeoAsciiParamsTag"].value if "GeoAsciiParamsTag" in tags else ""
        nodata_tag = tags["GDAL_NODATA"].value if "GDAL_NODATA" in tags else None
        return {
            "shape": list(p.shape),
            "dtype": str(np.dtype(p.dtype)),
            "bands": int(1 if p.shape == (p.imagewidth, p.imagelength) or len(p.shape) == 2 else p.shape[-1]),
            "pixel_scale": list(scale),
            "tiepoint": list(tie),
            "geokeys": list(keys),
            "geographic_crs": "EPSG:32611" if 32611 in keys else "unknown",
            "ascii_params": ascii_,
            "nodata_tag": str(nodata_tag),
        }


def write_submission(path, dots_mask, footprint, encoding="nan", compress="zlib"):
    """Write a submission raster from a boolean dot mask.

    encoding='nan'   -> NaN outside the footprint (matches the provided template)
    encoding='zeros' -> finite 0 outside the footprint (no nodata tag; useful
                        for portals that reject nonfinite values; acceptance
                        must still be confirmed by the competition platform)

    Dots are written as exactly 1.0.  Output is byte-deterministic: fixed tile
    geometry, fixed compression level, no timestamps or free-text metadata.
    """
    if encoding not in ("nan", "zeros"):
        raise ValueError(f"unknown encoding {encoding!r}")
    dots_mask = np.asarray(dots_mask, dtype=bool)
    footprint = np.asarray(footprint, dtype=bool)
    if dots_mask.shape != footprint.shape:
        raise ValueError("dots_mask and footprint shapes differ")
    if (dots_mask & ~footprint).any():
        raise ValueError("dots outside the footprint: refusing to write")

    out = np.zeros(dots_mask.shape, dtype=np.float32)
    out[dots_mask] = np.float32(1.0)
    if encoding == "nan":
        out[~footprint] = np.float32("nan")

    geokeys = GRID_TAGS["GeoKeyDirectoryTag"]
    ascii_ = GRID_TAGS["GeoAsciiParamsTag"]
    extratags = [
        (33550, "d", 3, GRID_TAGS["ModelPixelScaleTag"], False),
        (33922, "d", 6, GRID_TAGS["ModelTiepointTag"], False),
        (34735, "H", len(geokeys), geokeys, False),
        (34737, "s", len(ascii_) + 1, ascii_, False),
    ]
    # Zero is a valid probability, not a nodata sentinel. Omit the tag for
    # the upload-safe all-finite encoding; only NaN output declares NaN nodata.
    if encoding == "nan":
        nodata_str = "nan"
        extratags.append((42113, "s", len(nodata_str) + 1, nodata_str, False))
    tifffile.imwrite(
        path,
        out,
        dtype=np.float32,
        photometric="minisblack",
        compression=compress,
        compressionargs={"level": 6} if compress in ("zlib", "deflate") else None,
        tile=(256, 256),
        predictor=3 if compress else None,
        extratags=extratags,
        metadata=None,
        software=None,
    )
    return path


def read_back(path):
    """Re-read a written release from disk (gate: never trust the buffer)."""
    a = tifffile.imread(path)
    contract = read_contract_from_tiff(path)
    return a, contract


def write_contract(contract: dict, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(contract, indent=1, sort_keys=True) + "\n")
