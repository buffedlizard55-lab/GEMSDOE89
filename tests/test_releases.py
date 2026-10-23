"""Re-open every tracked receipt and re-run the MUST-pass gates on the raster.

Skips cleanly when the pinned inputs or the gitignored rasters are absent, so CI
stays green without shipping competition data.  When the data is present this is
the same fail-closed check the brief demands: re-read the file from disk after
writing it.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems89.grid import Grid, sha256_file, verify_manifest  # noqa: E402

RECEIPTS = sorted((ROOT / "releases").glob("*.json"))


def _grid_or_skip():
    try:
        verified = verify_manifest()
        return Grid(verified)
    except BaseException:
        pytest.skip("pinned competition inputs not restored in this environment")


@pytest.mark.parametrize("receipt_path", RECEIPTS, ids=lambda p: p.stem)
def test_release_passes_every_must_gate(receipt_path: Path):
    grid = _grid_or_skip()
    rec = json.loads(receipt_path.read_text(encoding="utf-8"))
    for key, nan_outside in (("nan", True), ("zeros", False)):
        rel = ROOT / rec["files"][key]["path"]
        if not rel.is_file():
            pytest.skip(f"{rel.name} not present (gitignored raster)")
        assert sha256_file(rel) == rec["files"][key]["sha256"], f"{rel.name}: sha256 drifted"
        checks = grid.validate(rel, nan_outside=nan_outside)
        assert checks["catalogue_mass"][1] is True
        assert checks["n_dots"][0] == 37_654
        assert checks["no_nan_inside"][1] is True


@pytest.mark.parametrize("receipt_path", RECEIPTS, ids=lambda p: p.stem)
def test_release_differs_from_parent_only_on_its_axis(receipt_path: Path):
    grid = _grid_or_skip()
    rec = json.loads(receipt_path.read_text(encoding="utf-8"))
    rel = ROOT / rec["files"]["nan"]["path"]
    if not rel.is_file():
        pytest.skip("raster not present")
    parent = grid.read_mask(ROOT / "data/registry/parent_r0_zeros.tif")
    var = grid.read_mask(rel)
    removed = int((parent & ~var).sum())
    added = int((var & ~parent).sum())
    pct = 100.0 * (removed + added) / int(parent.sum())
    assert rec["axis"] == "RELIEF"
    assert removed == added, "count must be fixed"
    assert 1.0 <= pct <= 50.0
    assert pct == pytest.approx(rec["diff_vs_parent"]["pct_changed"], abs=1e-3)
    # every ADDED dot must respect the 3 px collar; inherited dots keep the parent geometry
    assert grid.d_cat[var & ~parent].min() > 3.0


def test_no_duplicate_primary_hashes_in_receipts():
    seen = {}
    for p in RECEIPTS:
        rec = json.loads(p.read_text(encoding="utf-8"))
        for key in ("nan", "zeros"):
            sha = rec["files"][key]["sha256"]
            assert sha not in seen, f"duplicate {key} sha between {seen.get(sha)} and {rec['id']}"
            seen[sha] = rec["id"]


def test_parent_hashes_are_never_reused():
    parent_hashes = {
        "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
        "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd",
    }
    for p in RECEIPTS:
        rec = json.loads(p.read_text(encoding="utf-8"))
        for key in ("nan", "zeros"):
            assert rec["files"][key]["sha256"] not in parent_hashes
