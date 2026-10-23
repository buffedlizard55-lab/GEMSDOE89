"""Unit tests for the gateless SNAP construction (no competition data needed)."""

import numpy as np
import pytest

from gemsdoe.snap import (EDGE_BANDS, _offsets, block_density_cv, edge_response,
                          prepare_band, robust_unit, snap_dots)


def _toy_field(h=40, w=40, foot=None):
    rng = np.random.default_rng(3)
    a = rng.normal(size=(h, w)).astype(np.float32)
    return a, (np.ones((h, w), bool) if foot is None else foot)


def test_offsets_windows():
    assert len(_offsets(1.0)) == 4 and all(abs(d - 1.0) < 1e-9 for *_x, d in _offsets(1.0))
    assert len(_offsets(1.42)) == 8
    assert len(_offsets(2.0)) == 12
    # deterministic order: by (distance, dy, dx)
    offs = _offsets(2.0)
    assert offs == sorted(offs, key=lambda t: (round(t[2], 6), t[0], t[1]))
    assert _offsets(0.0) == []  # no displacement candidates


def test_robust_unit_bounds_and_footprint():
    a, foot = _toy_field()
    foot[:10] = False
    out = robust_unit(a, foot)
    assert out.dtype == np.float32
    assert np.all(out >= 0) and np.all(out <= 1)
    assert np.all(out[~foot] == 0)
    assert out[foot].max() > 0
    # convention check: out = clip(z / p99.5(z), 0, 6) / 6 inside the footprint
    v = a[foot]
    med = np.median(v)
    q25, q75 = np.percentile(v, [25.0, 75.0])
    z = (v - med) / max((q75 - q25) / 1.349, 1e-9)
    hi = max(np.percentile(z, 99.5), 1e-6)
    expect = np.clip(z / hi, 0.0, 6.0) / 6.0
    assert np.allclose(out[foot], expect, atol=1e-6)


def test_prepare_band_handles_nodata():
    a, foot = _toy_field()
    a[a < np.percentile(a, 5)] = -3.4028235e38  # nodata sentinel
    out = prepare_band(a, foot)
    assert np.isfinite(out[foot]).all()
    assert np.all(out >= 0)


def test_edge_response_is_max_fusion():
    h, w = 30, 30
    foot = np.ones((h, w), bool)
    bands = {3: np.full((h, w), 1.0, np.float32), 18: np.full((h, w), 2.0, np.float32)}
    resp, diag = edge_response(bands, foot)
    assert resp.shape == (h, w)
    assert [b["name"] for b in diag["response"]["bands"]] == [n for _i, n in EDGE_BANDS]
    # constant bands: robust scaling of a zero-IQR field is handled (scale floor)
    assert np.isfinite(resp).all()


def _setup():
    h = w = 50
    foot = np.ones((h, w), bool)
    resp = np.zeros((h, w), np.float32)
    resp[20:30, 20:30] = 0.5           # a strong plateau
    resp[21, 22] = 0.9                 # strongest pixel in reach of the dot
    dots = np.zeros((h, w), bool)
    dots[20, 21] = True                # next to the plateau edge
    dots[40, 40] = True                # flat ground, nowhere better
    allowed = foot.copy()
    return dots, resp, allowed


def test_snap_moves_only_to_stronger_and_preserves_count():
    dots, resp, allowed = _setup()
    res = snap_dots(dots, resp, allowed, max_shift=2.0, margin=0.0)
    assert res.stats["count_preserved"]
    assert int(res.mask.sum()) == int(dots.sum())
    for (y0, x0, y1, x1, r0, r1, d) in res.moves:
        assert r1 - r0 >= 1e-9, "must move only to a strictly stronger pixel"
        assert np.hypot(y1 - y0, x1 - x0) <= 2.0 + 1e-9
    # the plateau dot jumps to the strongest pixel in reach; the flat dot stays
    assert res.mask[21, 22], "dot must land on the strongest allowed pixel"
    assert not res.mask[20, 21]
    assert res.mask[40, 40], "flat-ground dot must not move"


def test_snap_gate_blocks_everything_when_margin_huge():
    dots, resp, allowed = _setup()
    res = snap_dots(dots, resp, allowed, max_shift=2.0, margin=9.0)
    assert res.stats["dots_moved"] == 0
    assert np.array_equal(res.mask, dots)


def test_snap_respects_allowed_mask():
    dots, resp, allowed = _setup()
    allowed[21, 22] = False  # forbid the strongest pixel in reach
    res = snap_dots(dots, resp, allowed, max_shift=2.0, margin=0.0)
    assert not res.mask[21, 22], "forbidden target must not be claimed"
    for (y0, x0, y1, x1, *_r) in res.moves:
        assert allowed[y1, x1], "targets must be inside the allowed mask"


def test_snap_deterministic():
    dots, resp, allowed = _toy_setup_larger()
    a = snap_dots(dots, resp, allowed, max_shift=2.0, margin=0.0)
    b = snap_dots(dots, resp, allowed, max_shift=2.0, margin=0.0)
    assert np.array_equal(a.mask, b.mask)
    assert a.moves == b.moves


def _toy_setup_larger():
    rng = np.random.default_rng(9)
    h = w = 120
    foot = np.ones((h, w), bool)
    resp, _ = edge_response({3: rng.normal(size=(h, w)).astype(np.float32),
                            18: rng.normal(size=(h, w)).astype(np.float32)}, foot)
    dots = np.zeros((h, w), bool)
    pts = rng.choice(h * w, size=400, replace=False)
    dots.ravel()[pts] = True
    allowed = foot.copy()
    allowed[0, :] = False
    return dots, resp, allowed


def test_count_preserved_under_random_response():
    dots, resp, allowed = _toy_setup_larger()
    res = snap_dots(dots, resp, allowed, max_shift=2.0, margin=0.0)
    assert res.stats["dots_in"] == res.stats["dots_out"] == 400
    moved = {m[:4] for m in res.moves}
    targets = [(m[2], m[3]) for m in res.moves]
    assert len(targets) == len(set(targets)), "one dot per target pixel"


def test_block_density_cv_matches_manual():
    dots = np.zeros((40, 40), bool)
    dots[:20] = True
    foot = np.ones((40, 40), bool)
    # block=20 -> two blocks: density 1.0 and 0.0 -> CV = 1.0
    cv = block_density_cv(dots, foot, block_px=20)
    assert cv == pytest.approx(1.0)
