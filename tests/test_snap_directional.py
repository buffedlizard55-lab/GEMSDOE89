"""Tests for the directional SNAP corner (gemsdoe.snap_directional).

The load-bearing test is `test_parity_with_snap_dots`: with the direction filter
switched off, the new rule must reproduce `gemsdoe.snap.snap_dots` exactly, so a
release built here differs from the existing SNAP arms by the direction filter
and nothing else.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy import ndimage as ndi

from gemsdoe import snap
from gemsdoe import snap_directional as sd


def _field(seed=0, shape=(60, 70)):
    rng = np.random.default_rng(seed)
    resp = ndi.gaussian_filter(rng.random(shape), 1.2)
    resp = (resp - resp.min()) / (resp.max() - resp.min())
    dots = np.zeros(shape, dtype=bool)
    dots[5:55:3, 6:64:4] = True
    return dots, resp.astype(np.float32)


def _plane(shape=(60, 70), gy=1.0, gx=0.0):
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    return (gy * yy + gx * xx).astype(np.float32)


def test_uphill_field_points_upslope():
    z = _plane(gy=1.0)
    uy, ux, mag = sd.uphill_field(z, np.ones_like(z, dtype=bool))
    assert uy[30, 30] == pytest.approx(1.0, abs=1e-6)   # rows grow southward
    assert ux[30, 30] == pytest.approx(0.0, abs=1e-6)
    assert mag[30, 30] == pytest.approx(1.0, abs=1e-6)


def test_parity_with_snap_dots():
    dots, resp = _field()
    allowed = np.ones_like(dots)
    ref = snap.snap_dots(dots, resp, allowed, 2.0, margin=0.0)
    got = sd.directional_snap(dots, resp, allowed, 2.0, direction="none")
    assert np.array_equal(got.mask, ref.mask)
    assert got.stats["dots_moved"] == ref.stats["dots_moved"]
    assert got.stats["mean_displacement_px"] == pytest.approx(
        ref.stats["mean_displacement_px"], abs=1e-12)


@pytest.mark.parametrize("window", [1.0, 1.42, 2.0])
def test_parity_at_every_release_window(window):
    dots, resp = _field(seed=3)
    allowed = np.ones_like(dots)
    ref = snap.snap_dots(dots, resp, allowed, window, margin=0.0)
    got = sd.directional_snap(dots, resp, allowed, window, direction="none")
    assert np.array_equal(got.mask, ref.mask)
    assert got.stats["count_preserved"]


def test_up_arm_only_moves_upslope_and_mirror_only_downslope():
    dots, resp = _field(seed=1)
    allowed = np.ones_like(dots)
    uy, ux, mag = sd.uphill_field(_plane(gy=5.0), np.ones_like(dots))
    fw = sd.directional_snap(dots, resp, allowed, 2.0, direction="footwall",
                             uy=uy, ux=ux, slope=mag)
    hw = sd.directional_snap(dots, resp, allowed, 2.0, direction="hangingwall",
                             uy=uy, ux=ux, slope=mag)
    audit_fw = sd.upslope_share(fw.moves, uy, ux, mag)
    audit_hw = sd.upslope_share(hw.moves, uy, ux, mag)
    assert audit_fw["share_upslope"] == 1.0
    assert audit_hw["share_downslope"] == 1.0
    # every fw displacement has dy > 0 (plane rises with the row index) ...
    assert all(m[2] - m[0] > 0 for m in fw.moves)
    # ... and every mirror displacement has dy < 0
    assert all(m[2] - m[0] < 0 for m in hw.moves)
    assert 0 < fw.stats["dots_moved"] < int(dots.sum())


def test_count_preserved_and_targets_allowed_and_within_window():
    dots, resp = _field(seed=2)
    allowed = np.zeros_like(dots)
    allowed[3:57, 3:67] = True          # forbid the outer frame
    allowed[5:55:3, 6:64:4] = True      # and keep every original dot placeable
    uy, ux, mag = sd.uphill_field(_plane(gy=5.0), np.ones_like(dots))
    for direction in ("footwall", "hangingwall", "none"):
        res = sd.directional_snap(dots, resp, allowed, 2.0, direction=direction,
                                  uy=uy, ux=ux, slope=mag)
        assert res.mask.sum() == dots.sum()
        assert not (res.mask & ~allowed).any()
        for (y0, x0, y1, x1, _r0, _r1, dist) in res.moves:
            assert ((y0, x0) == (y1, x1)) is False
            assert dist <= 2.0 + 1e-9
            assert dots[y0, x0] and res.mask[y1, x1]
        # removing the dot and adding the target leaves the parent count intact
        removed = dots & ~res.mask
        added = res.mask & ~dots
        assert removed.sum() == added.sum() == res.stats["dots_moved"]


def test_flat_ground_is_a_deadband():
    """No slope -> no defined direction -> nothing moves (conservative arm)."""
    dots, resp = _field(seed=4)
    allowed = np.ones_like(dots)
    flat = np.zeros(dots.shape, dtype=np.float32)
    uy, ux, mag = sd.uphill_field(flat, np.ones_like(dots))
    res = sd.directional_snap(dots, resp, allowed, 2.0, direction="footwall",
                              uy=uy, ux=ux, slope=mag)
    assert res.stats["dots_moved"] == 0
    assert res.stats["dots_ambiguous_slope"] == int(dots.sum())
    assert np.array_equal(res.mask, dots)


def test_determinism():
    dots, resp = _field(seed=5)
    allowed = np.ones_like(dots)
    uy, ux, mag = sd.uphill_field(_plane(gy=5.0), np.ones_like(dots))
    a = sd.directional_snap(dots, resp, allowed, 2.0, "footwall", uy, ux, mag)
    b = sd.directional_snap(dots, resp, allowed, 2.0, "footwall", uy, ux, mag)
    assert np.array_equal(a.mask, b.mask)
    assert a.moves == b.moves


def test_bad_direction_rejected():
    dots, resp = _field()
    with pytest.raises(ValueError):
        sd.directional_snap(dots, resp, np.ones_like(dots), 2.0, direction="upwind")


def test_directional_needs_gradient_arrays():
    dots, resp = _field()
    with pytest.raises(ValueError):
        sd.directional_snap(dots, resp, np.ones_like(dots), 2.0, direction="footwall")
