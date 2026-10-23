"""Round-trip and gate tests on a synthetic frame (no competition data)."""

import numpy as np
import pytest

from gemsdoe import grid, validate


@pytest.fixture()
def frame():
    rng = np.random.default_rng(0)
    shape = (512, 512)
    footprint = np.zeros(shape, dtype=bool)
    footprint[20:-20, 20:-20] = True
    dots = np.zeros(shape, dtype=bool)
    idx = rng.choice(np.flatnonzero(footprint.ravel()), size=400, replace=False)
    dots.ravel()[idx] = True
    return footprint, dots


def _contract(path):
    return grid.read_contract_from_tiff(path)


def test_roundtrip_nan_encoding(tmp_path, frame):
    footprint, dots = frame
    p = tmp_path / "a.tif"
    grid.write_submission(p, dots, footprint, encoding="nan")
    arr, contract = grid.read_back(p)
    assert arr.dtype == np.float32
    assert arr.shape == footprint.shape
    assert (arr[dots] == 1.0).all()
    assert np.isnan(arr[~footprint]).all()
    assert np.isfinite(arr[footprint]).all()
    assert contract["geographic_crs"] == "EPSG:32611"


def test_roundtrip_zeros_encoding(tmp_path, frame):
    footprint, dots = frame
    p = tmp_path / "z.tif"
    grid.write_submission(p, dots, footprint, encoding="zeros")
    arr, _ = grid.read_back(p)
    assert (arr[~footprint] == 0).all()
    assert (arr[dots] == 1.0).all()
    assert not np.isnan(arr).any()


def test_writer_is_byte_deterministic(tmp_path, frame):
    footprint, dots = frame
    a, b = tmp_path / "a.tif", tmp_path / "b.tif"
    grid.write_submission(a, dots, footprint, encoding="nan")
    grid.write_submission(b, dots, footprint, encoding="nan")
    assert grid.sha256_file(a) == grid.sha256_file(b)


def test_writer_refuses_dots_outside_footprint(tmp_path, frame):
    footprint, dots = frame
    bad = dots.copy()
    bad[0, 0] = True
    with pytest.raises(ValueError):
        grid.write_submission(tmp_path / "c.tif", bad, footprint)


def test_gate_accepts_good_file(tmp_path, frame):
    footprint, dots = frame
    p = tmp_path / "good.tif"
    grid.write_submission(p, dots, footprint, encoding="nan")
    arr, _ = grid.read_back(p)
    ok, results = validate.gate_release(
        p, _contract(p), footprint=footprint, dots_mask=np.nan_to_num(arr) > 0,
        require_nan_outside=True,
    )
    assert ok, [r for r in results if not r["ok"]]


def test_gate_rejects_value_above_one(tmp_path, frame):
    footprint, dots = frame
    p = tmp_path / "badval.tif"
    grid.write_submission(p, dots, footprint, encoding="zeros")
    arr, _ = grid.read_back(p)
    arr[dots] = 2.0
    import tifffile

    tifffile.imwrite(p, arr.astype(np.float32), extratags=[
        (33550, "d", 3, grid.GRID_TAGS["ModelPixelScaleTag"], False),
        (33922, "d", 6, grid.GRID_TAGS["ModelTiepointTag"], False),
        (34735, "H", len(grid.GRID_TAGS["GeoKeyDirectoryTag"]),
         grid.GRID_TAGS["GeoKeyDirectoryTag"], False),
        (34737, "s", len(grid.GRID_TAGS["GeoAsciiParamsTag"]) + 1,
         grid.GRID_TAGS["GeoAsciiParamsTag"], False),
    ])
    ok, results = validate.gate_release(p, _contract(p), footprint=footprint,
                                       require_nan_outside=False)
    assert not ok
    assert any(r["gate"] == "values_in_0_1" and not r["ok"] for r in results)


def test_gate_rejects_dot_on_catalogue(tmp_path, frame):
    footprint, dots = frame
    catalogue = np.zeros_like(dots)
    catalogue[dots] = True  # pretend every dot sits on a catalogue pixel
    p = tmp_path / "cat.tif"
    grid.write_submission(p, dots, footprint, encoding="nan")
    arr, _ = grid.read_back(p)
    ok, results = validate.gate_release(
        p, _contract(p), footprint=footprint,
        dots_mask=np.nan_to_num(arr) > 0, require_nan_outside=True,
        clearance_raster=catalogue,
    )
    assert not ok
    assert any(r["gate"] == "zero_catalogue_mass" and not r["ok"] for r in results)
