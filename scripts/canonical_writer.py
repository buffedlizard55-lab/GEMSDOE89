#!/usr/bin/env python3
"""Canonical GeoTIFF writer that reproduces the parent's byte stream.

Why this exists
---------------
R0 (``h33-h33-2-b2``) was written as a tiled, deflate/Predictor=3 float32 GTiff
whose deflate streams are **zlib-wrapped libdeflate** output.  The GDAL builds
available from the rasterio wheels (1.3.x/GDAL 3.8.4 and 1.4.x/GDAL 3.9.3) emit
*raw* zlib deflate, so writing with them reproduces every pixel but not the bytes:

    rasterio 3.8.4 zeros  -> c6186b07...   (204,802 B)
    rasterio 3.9.3 zeros  -> c6186b07...   (204,802 B)   identical to each other
    parent                -> c55bafc4...   (219,065 B)   zlib-wrapped libdeflate

The parent's stream is reproducible: ``imagecodecs.deflate_encode(raw, level=9)``
(libdeflate) reproduces its tiles byte for byte.  So this writer

1. lets GDAL lay out the container and apply Predictor=3 (the part whose layout
   must match the parent: header, IFD, tag order, tile order, all unchanged),
2. recompresses every tile's predictor-encoded payload with libdeflate at
   level 10, and
3. patches TileOffsets / TileByteCounts in place and re-emits the body.

The pixel data is produced by the caller; the parent file is never read here.
"""
from __future__ import annotations

import struct
import tempfile
import zlib
from pathlib import Path

import imagecodecs
import numpy as np
import rasterio
import tifffile

LIBDEFLATE_LEVEL = 10
PREDICTOR = 3


def _patch_long_array(head: bytearray, offset: int, values: list[int]) -> None:
    struct.pack_into(f"<{len(values)}I", head, offset, *values)


def write_canonical(path: Path, mask: np.ndarray, grid, *, nan_outside: bool) -> str:
    """Write `mask` as a unit-mass dot raster with the parent's exact byte layout."""
    from gems89.grid import sha256_file

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    prof = grid.profile_nan if nan_outside else grid.profile_zeros
    fill = np.nan if nan_outside else 0.0
    arr = np.where(grid.foot, mask.astype(np.float32), fill).astype(np.float32)

    with tempfile.TemporaryDirectory() as td:
        scratch = Path(td) / "scratch.tif"
        with rasterio.open(scratch, "w", **prof) as dst:
            dst.write(arr, 1)
        raw = scratch.read_bytes()
        with tifffile.TiffFile(scratch) as tf:
            page = tf.pages[0]
            off_tag = page.tags["TileOffsets"]
            cnt_tag = page.tags["TileByteCounts"]
            offsets = list(off_tag.value)
            counts = list(cnt_tag.value)
            off_pos, cnt_pos = int(off_tag.valueoffset), int(cnt_tag.valueoffset)
            block = int(page.tags["TileWidth"].value) * int(page.tags["TileLength"].value) * 4

    head_len = offsets[0]
    head = bytearray(raw[:head_len])
    body = bytearray()
    new_offsets, new_counts = [], []
    for off, cnt in zip(offsets, counts):
        payload = zlib.decompress(raw[off:off + cnt])          # Predictor=3 encoded bytes
        if len(payload) != block:
            raise RuntimeError(f"unexpected tile payload {len(payload)} != {block}")
        packed = imagecodecs.deflate_encode(payload, level=LIBDEFLATE_LEVEL)  # libdeflate, zlib wrapper
        new_offsets.append(head_len + len(body))
        new_counts.append(len(packed))
        body += packed
    _patch_long_array(head, off_pos, new_offsets)
    _patch_long_array(head, cnt_pos, new_counts)
    path.write_bytes(bytes(head) + bytes(body))
    return sha256_file(path)


def inspect(path: Path) -> dict:
    """Container facts used by the gates and by the receipts."""
    import tifffile
    with tifffile.TiffFile(path) as tf:
        page = tf.pages[0]
        comp = int(page.tags["Compression"].value)
        pred = int(page.tags["Predictor"].value) if "Predictor" in page.tags else None
        tiled = "TileWidth" in page.tags
        return {"compression": comp, "predictor": pred, "tiled": tiled,
                "tile_shape": (page.tilewidth, page.tilelength) if tiled else None,
                "n_tiles": len(page.tags["TileOffsets"].value) if tiled else 1}
