"""Unit tests for the TRACKB module: trace geometry, count preservation,
nested doses, hard gates, determinism, and GeoJSON transform sanity.

These run WITHOUT competition data (synthetic rasters), like the rest of tests/.
"""
from __future__ import annotations

import numpy as np
import pytest
from scipy import ndimage as ndi

from gemsdoe import trackb


def _synthetic_r0():
    """Two long near-straight chains + several isolated dots on a 120x160 grid."""
    rng = np.random.default_rng(0)
    r0 = np.zeros((120, 160), dtype=bool)
    # chain A: shallow diagonal, dots ~3 px apart
    for t in range(0, 30, 3):
        r0[20 + t // 4, 10 + t] = True
    # chain B: near-vertical
    for t in range(0, 28, 3):
        r0[60 + t, 100 + t // 6] = True
    # isolated / short fragments
    for (y, x) in [(5, 5), (8, 8), (100, 20), (105, 24), (30, 140),
                   (90, 5), (110, 120), (15, 150), (70, 30), (95, 150)]:
        r0[y, x] = True
    foot = np.ones_like(r0)
    cat = np.zeros_like(r0)
    cat[65:68, 100:104] = True  # a small mapped patch near chain B
    return r0, foot, cat


def test_build_traces_geometry_and_order():
    r0, foot, cat = _synthetic_r0()
    traces, on_trace = trackb.build_traces(r0)
    assert len(traces) >= 2, "long chains should be kept as traces"
    for t in traces:
        assert t.arc_px >= trackb.MIN_LEN_PX - 1e-9
        assert t.sinuosity <= trackb.MAX_SINUOSITY + 1e-9
        assert t.n_dots == len(t.dot_idx)
        assert len(t.spine) >= 2
        assert t.confidence > 0
    # ordered by structural significance (length x credit), descending
    confs = [t.confidence for t in traces]
    assert confs == sorted(confs, reverse=True)
    assert [t.rank for t in traces] == list(range(1, len(traces) + 1))
    # on_trace only marks dots, subset of r0
    assert np.all(on_trace <= r0)


def test_variant_count_preserved_and_nested():
    r0, foot, cat = _synthetic_r0()
    d_cat = ndi.distance_transform_edt(~cat)
    traces, on_trace = trackb.build_traces(r0)
    corrob = np.full(r0.shape, 0.5, dtype=np.float32)
    corridor = trackb.corridor_mask(traces, r0)
    placements = trackb.placement_list(r0, traces, corridor, corrob, foot, d_cat)
    collar = r0 & (d_cat < 3.0)
    off = trackb.off_trace_order(r0, on_trace, seed=trackb.SEED, protect=collar)

    n = int(r0.sum())
    prev_removed = None
    for frac in (0.10, 0.20, 0.30):
        k = max(2, int(round(frac * n)))
        k = min(k, len(placements), len(off))
        variant, stats = trackb.build_variant(r0, foot, off[:k], placements[:k])
        assert stats["count_preserved"], (frac, stats)
        assert stats["all_dots_inside_footprint"]
        removed = r0 & ~variant
        added = variant & ~r0
        # added dots clear catalogue and are separated
        assert d_cat[added].min() >= 3.0 - 1e-6 if added.any() else True
        assert np.all(variant <= foot)
        # nested: larger dose removes a superset of the smaller dose's sources
        if prev_removed is not None:
            assert np.all(prev_removed <= removed)
        prev_removed = removed


def test_off_trace_protects_collar():
    r0, foot, cat = _synthetic_r0()
    d_cat = ndi.distance_transform_edt(~cat)
    traces, on_trace = trackb.build_traces(r0)
    collar = r0 & (d_cat < 3.0)
    off = trackb.off_trace_order(r0, on_trace, seed=1, protect=collar)
    if len(off):
        assert not np.any(collar[off[:, 0], off[:, 1]]), "protected collar dot in source pool"


def test_determinism():
    r0, foot, cat = _synthetic_r0()
    d_cat = ndi.distance_transform_edt(~cat)
    corrob = np.full(r0.shape, 0.5, dtype=np.float32)

    def run():
        traces, on_trace = trackb.build_traces(r0)
        corridor = trackb.corridor_mask(traces, r0)
        pl = trackb.placement_list(r0, traces, corridor, corrob, foot, d_cat)
        off = trackb.off_trace_order(r0, on_trace, seed=trackb.SEED)
        return traces, pl, off

    t1, p1, o1 = run()
    t2, p2, o2 = run()
    assert np.array_equal(o1, o2), "seeded off-trace order must be deterministic"
    if len(p1):
        assert np.array_equal(p1, p2), "placement list must be deterministic"
    assert [t.confidence for t in t1] == [t.confidence for t in t2]


def test_robust_unit_masks_sentinels():
    b = np.array([[1.0, 2.0, -3.4028235e38], [np.nan, 5.0, 8.0]], dtype=np.float32)
    out = trackb.robust_unit(b)
    assert out.shape == b.shape
    assert np.all(np.isfinite(out))
    assert out[0, 2] == 0.0, "sentinel must map to 0"
    assert out[1, 0] == 0.0, "NaN must map to 0"
    assert out.max() > 0.0


def test_strike_azimuth_range():
    r0, _, _ = _synthetic_r0()
    traces, _ = trackb.build_traces(r0)
    for t in traces:
        a = trackb.strike_azimuth(t, r0)
        assert 0.0 <= a < 180.0


def test_utm_to_lonlat_sane():
    pytest.importorskip("rasterio")  # rebuild_r0.py dependency; skip if a slim CI omits it
    # a point near the tiepoint (EPSG:32611 zone 11N) -> WGS84 in the US Great Basin
    lons, lats = trackb.utm_to_lonlat(np.array([0.0]), np.array([0.0]))
    assert -125 < lons[0] < -110, lons
    assert 39 < lats[0] < 42, lats


def test_corroboration_bounds():
    rng = np.random.default_rng(3)
    bands = {
        "b03_tmi_hg": rng.random((50, 50)).astype(np.float32),
        "b05_iso_grav_anom_slope": rng.random((50, 50)).astype(np.float32),
        "b19_det_elev_slope": rng.random((50, 50)).astype(np.float32),
    }
    c = trackb.corroboration(bands)
    assert c.shape == (50, 50)
    assert float(c.min()) >= 0.0 and float(c.max()) <= 1.0 + 1e-6
