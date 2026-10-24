"""Unit tests for the Phase 2 TRACKB axis (no competition data required)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from scipy.ndimage import distance_transform_edt

from gemsdoe import parent, trackb_150 as trackb

ROOT = Path(__file__).resolve().parents[1]


def _synthetic_trackb_scene():
    """Synthetic 96x96 grid (9.6 km x 9.6 km) with unbroken ridges, a wash-gapped
    corridor, an inherited <3 px collar dot, and low-score 1-dot speckles.
    """
    h, w = 96, 96
    foot = np.ones((h, w), dtype=bool)
    foot[:2, :] = False

    cat = np.zeros((h, w), dtype=bool)
    cat[10:26, 10] = True  # mapped N-S fault on western margin

    h19 = np.zeros((h, w), dtype=bool)
    # Two unbroken >=1.8 km N-S / diagonal strike-consistent ridges
    h19[16:40, 28] = True
    for k in range(22):
        h19[18 + k, 46 + k // 2] = True

    # A wash-interrupted fault corridor at col 74: two 8-px segments separated by a 3-px wash gap
    h19[18:26, 74] = True
    h19[29:38, 74] = True

    # Inherited collar dot at sqrt(5)=2.236 px from cat pixel (25, 10) -> (27, 11)
    h19[27, 11] = True

    # Plenty of isolated 1-dot speckles in the southern half (rows 56..92)
    for r in range(56, 92, 5):
        for c in range(16, 90, 5):
            h19[r, c] = True

    r0, _ = parent.rebuild_r0_mask(h19, foot, cat, r_min=2.8, collar_px=2.0)

    rng = np.random.default_rng(20261024)
    yy, xx = np.indices((h, w), dtype=np.float32)
    # Strong geophysical/scarp ridge along cols 28, 46..56, and continuous basement step along col 74
    ridge_sig = (
        np.exp(-((xx - 28.0) ** 2) / 3.0) * ((yy >= 14) & (yy <= 42))
        + np.exp(-((xx - (46.0 + np.maximum(yy - 18.0, 0.0) * 0.5)) ** 2) / 3.0) * ((yy >= 16) & (yy <= 42))
        + 1.3 * np.exp(-((xx - 74.0) ** 2) / 2.5) * ((yy >= 16) & (yy <= 40))
    ).astype(np.float32)

    bands = {
        3: (20.0 * ridge_sig + np.abs(rng.normal(2.0, 0.3, (h, w)))).astype(np.float32),
        4: (15.0 * ridge_sig + 3.0).astype(np.float32),
        5: (0.40 * ridge_sig + 0.04).astype(np.float32),
        7: (12.0 * ridge_sig + 2.0).astype(np.float32),
        9: (8.0 * ridge_sig - 1.0).astype(np.float32),
        12: (50.0 * np.tanh((xx - 28.0) / 2.0) + 40.0 * np.tanh((xx - 74.0) / 2.0)).astype(np.float32),
        15: np.full((h, w), 480.0, dtype=np.float32),
        16: (800.0 * ridge_sig + 100.0).astype(np.float32),
        17: (0.25 * ridge_sig + 0.02).astype(np.float32),
        18: (0.45 * ridge_sig + 0.03).astype(np.float32),
        19: (18.0 * ridge_sig + 1.5).astype(np.float32),
    }
    # Inject -3.4e38 float32 sentinels inside footprint (including on band 18 to test band-5 fallback)
    bands[18][26:30, 72:77] = np.float32(-3.4028235e38)
    bands[3][5, 5] = np.float32(-3.4028235e38)
    return foot, cat, h19, r0, bands


def test_coordinate_transforms_and_strike_conventions():
    e0, n0 = trackb.pixel_to_utm11n(0, 0)
    assert (float(e0), float(n0)) == (243400.0, 4508500.0)

    # Central meridian of UTM Zone 11N is -117.0 deg at 500,000 m Easting
    lon_cm, lat_eq = trackb.utm11n_to_lonlat(500000.0, 0.0)
    assert abs(float(lon_cm) - (-117.0)) < 1e-9
    assert abs(float(lat_eq) - 0.0) < 1e-9

    lon_nv, lat_nv = trackb.utm11n_to_lonlat(408000.0, 4322000.0)
    assert -120.5 < float(lon_nv) < -117.0
    assert 38.5 < float(lat_nv) < 39.5

    # N-S trace: strike = 0 deg; E-W trace: strike = 90 deg; NNE trace: ~26.6 deg
    ns_geom = trackb.trace_geometry_metrics([(30, 10), (15, 10)])
    ew_geom = trackb.trace_geometry_metrics([(10, 10), (10, 25)])
    nne_geom = trackb.trace_geometry_metrics([(30, 10), (10, 20)])
    assert abs(ns_geom["strike_deg"] - 0.0) < 1e-6
    assert abs(ew_geom["strike_deg"] - 90.0) < 1e-6
    assert 26.0 < nne_geom["strike_deg"] < 27.0
    assert ns_geom["chord_km"] == pytest.approx(1.5)
    assert trackb.axial_diff_deg(5.0, 175.0) == pytest.approx(10.0)


def test_split_strike_consistent_breaks_sharp_hinge():
    # L-shaped 8-connected chain: 14 px North then 14 px East (90 deg corner)
    leg1 = [(30 - k, 10) for k in range(15)]
    leg2 = [(16, 11 + k) for k in range(14)]
    bent = leg1 + leg2
    segs = trackb.split_strike_consistent(bent, min_chord_px=10.0)
    assert len(segs) == 2
    for seg in segs:
        g = trackb.trace_geometry_metrics(seg)
        assert g["chord_km"] >= 1.0 - 1e-6
        assert g["cross_strike_max_m"] <= 250.0 + 1e-6


def test_physical_stack_scrubs_sentinels_and_falls_back_on_b18():
    foot, _cat, _h19, _r0, bands = _synthetic_trackb_scene()
    phys = trackb.compute_physical_stack(bands, foot)
    sc = phys["score_px"]
    assert sc.dtype == np.float32
    assert np.isfinite(sc).all()
    assert np.all(sc[~foot] == 0.0)
    assert np.all((sc[foot] >= 0.0) & (sc[foot] <= 1.0))
    # Wash gap at (27, 74) had band 18 = -3.4e38 sentinel, but band 5 fallback keeps u_grav strong
    assert float(phys["u_grav"][27, 74]) > float(phys["u_grav"][70, 50])


@pytest.mark.parametrize(
    "trace_mode,mass_mode",
    [("skeleton", "add"), ("skeleton", "swap"), ("dotlink", "swap")],
)
def test_build_variant_and_geojson_invariants(trace_mode, mass_mode):
    foot, cat, h19, r0, bands = _synthetic_trackb_scene()
    phys = trackb.compute_physical_stack(bands, foot)
    cat_kin = trackb.catalogue_kinematic_field(cat, foot)

    v1, traces1, stats1 = trackb.build_variant(
        parent_dots=r0,
        h19_mask=h19,
        footprint=foot,
        catalogue_mask=cat,
        score_px=phys["score_px"],
        n_traces=5,
        trace_mode=trace_mode,
        mass_mode=mass_mode,
        det_elev=phys["clean_bands"][12],
    )
    v2, _, _ = trackb.build_variant(
        parent_dots=r0,
        h19_mask=h19,
        footprint=foot,
        catalogue_mask=cat,
        score_px=phys["score_px"],
        n_traces=5,
        trace_mode=trace_mode,
        mass_mode=mass_mode,
    )

    assert np.array_equal(v1, v2)
    assert not (v1 & (~foot)).any()
    assert not (v1 & cat).any()

    d_cat = distance_transform_edt(~cat)
    # Inherited <3 px collar dot frozen untouched
    assert np.array_equal(v1 & (d_cat < 3.0), r0 & (d_cat < 3.0))
    added = v1 & (~r0)
    assert added.any()
    assert float(d_cat[added].min()) >= 3.0 - 1e-6

    if mass_mode == "add":
        assert stats1["n_removed"] == 0
        assert int(v1.sum()) == int(r0.sum()) + stats1["n_added"]
    else:
        assert stats1["n_added"] == stats1["n_removed"]
        assert int(v1.sum()) == int(r0.sum())

    if trace_mode == "dotlink":
        assert stats1["n_bridged_traces"] >= 1

    # Every trace is 8-connected, pixel-disjoint, >= 1.0 km, and strike-consistent
    seen_px: set[tuple[int, int]] = set()
    for tr in traces1:
        px = tr["pixels"]
        assert len(px) >= 8
        for a, b in zip(px[:-1], px[1:]):
            assert max(abs(a[0] - b[0]), abs(a[1] - b[1])) == 1
        assert seen_px.isdisjoint(px)
        seen_px.update(px)
        assert tr["geometry"]["chord_km"] >= 1.0 - 1e-6
        assert tr["geometry"]["cross_strike_max_m"] <= 250.0 + 1e-6

    gj = trackb.build_trace_geojson(
        variant_id="test-trackb",
        value="test",
        traces=traces1,
        r0_mask=r0,
        phys=phys,
        cat_kin=cat_kin,
        raster_sha256="0" * 64,
    )
    assert gj["type"] == "FeatureCollection"
    assert len(gj["features"]) == len(traces1)
    for feat in gj["features"]:
        assert feat["geometry"]["type"] == "LineString"
        props = feat["properties"]
        assert props["length_chord_km"] >= 1.0
        assert len(props["evidence"]) >= 200
        assert "Primary non-fault mimic:" in props["evidence"]


def test_committed_trackb_geojson_releases():
    gj_files = sorted((ROOT / "releases").glob("*TRACKBt150*.geojson"))
    assert len(gj_files) == 3
    for path in gj_files:
        doc = json.loads(path.read_text(encoding="utf-8"))
        assert doc["type"] == "FeatureCollection"
        assert len(doc["features"]) == 150
        for feat in doc["features"]:
            p = feat["properties"]
            assert p["length_chord_km"] >= 1.0
            assert p["cross_strike_rms_m"] <= 250.0
            assert len(p["evidence"]) >= 200
