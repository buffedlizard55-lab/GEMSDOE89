#!/usr/bin/env python3
"""Submission GeoTIFF writer/validator shared by GEMSDOE89 experiments.

This module writes one single-band float32 GeoTIFF on the pinned submission
grid. It exact-masks known catalogue pixels, keeps every prediction in [0, 1],
and defaults to finite zeros outside the footprint. NaN research twins must
be explicitly requested and are not upload-safe. It never uploads or accesses DrivenData.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe import grid, validate  # noqa: E402


def write_candidate(path: Path, proposed_dots: np.ndarray, footprint: np.ndarray,
                    known_faults: np.ndarray, ledger_hashes=(), *,
                    encoding: str = "zeros") -> tuple[np.ndarray, dict]:
    """Exact-mask catalogue pixels, write TIF, and run mandatory format gates."""
    path = Path(path)
    if encoding not in {"zeros", "nan"}:
        raise ValueError("encoding must be zeros or nan")
    for label, mask in (("dots", proposed_dots), ("footprint", footprint),
                        ("known_faults", known_faults)):
        a = np.asarray(mask)
        if a.ndim != 2 or not np.isfinite(a).all() or not np.isin(a, [0, 1]).all():
            raise ValueError(f"{label} must be a finite binary 2-D mask")
    dots = np.asarray(proposed_dots, dtype=bool).copy()
    foot = np.asarray(footprint, dtype=bool)
    cat = np.asarray(known_faults, dtype=bool)
    if dots.shape != foot.shape or cat.shape != foot.shape:
        raise ValueError("candidate, footprint, and known-fault mask must have equal shape")
    dots &= foot
    dots &= ~cat  # exact-pixel mask only; no proximity collar is imposed
    if int(dots.sum()) == 0:
        raise ValueError("refusing to write an empty submission raster")
    path.parent.mkdir(parents=True, exist_ok=True)
    grid.write_submission(path, dots, foot, encoding=encoding)

    # Re-read from disk; do not validate only the in-memory buffer.
    arr, got = grid.read_back(path)
    contract = json.loads((ROOT / "registry" / "grid_contract.json").read_text())
    if list(arr.shape) != contract["shape"]:
        raise ValueError(f"shape mismatch: got {arr.shape}, expected {contract['shape']}")
    ok, gates = validate.gate_release(
        path, contract, footprint=foot, dots_mask=dots,
        require_nan_outside=(encoding == "nan"), ledger_hashes=ledger_hashes, min_clearance_px=0.0,
        clearance_raster=cat,
    )
    if not ok:
        failed = [g for g in gates if not g["ok"]]
        raise ValueError(f"submission format validation failed: {failed}")
    if np.isnan(arr[foot]).any():
        raise ValueError("NaN found inside submission footprint")
    finite = arr[np.isfinite(arr)]
    if finite.size and (float(finite.min()) < 0.0 or float(finite.max()) > 1.0):
        raise ValueError("finite predictions are outside [0, 1]")
    if encoding == "nan" and not np.isnan(arr[~foot]).all():
        raise ValueError("outside-footprint values are not all NaN")
    if np.any(dots & cat):
        raise ValueError("known fault pixels were not exact-masked")
    return dots, {"passed": True, "encoding": encoding,
                  "all_values_finite": bool(np.isfinite(arr).all()), "gates": gates, "crs": got.get("geographic_crs"),
                  "shape": list(arr.shape), "dtype": str(arr.dtype),
                  "finite_min": float(finite.min()), "finite_max": float(finite.max()),
                  "nan_inside_footprint": int(np.isnan(arr[foot]).sum()),
                  "outside_nan_pixels": int(np.isnan(arr[~foot]).sum()),
                  "dot_count": int(dots.sum()), "sha256": grid.sha256_file(path)}


def note_length(note: str) -> int:
    """Return the competition-note character count and enforce its 140-char cap."""
    n = len(note)
    if n > 140:
        raise ValueError(f"submission note is {n} chars; maximum is 140")
    return n
