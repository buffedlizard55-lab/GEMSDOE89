"""Unit tests for the SPACING-axis mechanics (synthetic frames, no data)."""

import numpy as np
import pytest

from gemsdoe import spacing


@pytest.fixture()
def frame():
    rng = np.random.default_rng(0)
    shape = (120, 120)
    footprint = np.zeros(shape, dtype=bool)
    footprint[10:-10, 10:-10] = True
    catalogue = np.zeros(shape, dtype=bool)
    catalogue[60, :] = True  # a catalogue line through the middle
    capacity = spacing.capacity_mask(footprint, catalogue)
    return shape, footprint, catalogue, capacity, rng


def _dots(shape, coords):
    m = np.zeros(shape, dtype=bool)
    for y, x in coords:
        m[y, x] = True
    return m


def test_greedy_violators_partition_and_separation(frame):
    shape, footprint, catalogue, capacity, rng = frame
    # two close pairs (2.828 px diagonal) plus one isolated dot
    coords = [(30, 30), (32, 32), (50, 80), (52, 82), (90, 90)]
    dots = _dots(shape, coords)
    pts = np.argwhere(dots)
    is_anchor, movers, violated = spacing.greedy_violators(pts, shape, 3.0, rng)
    assert is_anchor.sum() + len(movers) == len(pts)
    anchors = pts[is_anchor]
    # anchors are mutually at least 3 px apart
    for i in range(len(anchors)):
        for j in range(i + 1, len(anchors)):
            assert np.hypot(*(anchors[i] - anchors[j])) >= 3.0 - 1e-9
    # every mover points at a real anchor within r_min
    for k in movers:
        a = violated[k]
        assert is_anchor[a]
        assert np.hypot(*(pts[k] - pts[a])) < 3.0


def test_poisson_disk_keeps_count_and_never_degrades(frame):
    shape, footprint, catalogue, capacity, rng = frame
    coords = [(30, 30), (32, 32), (34, 30), (80, 25), (82, 27)]
    dots = _dots(shape, coords)
    pts = np.argwhere(dots)
    nn0, _ = spacing.nearest_neighbour_distance(dots)
    is_anchor, movers, _ = spacing.greedy_violators(pts, shape, 3.0,
                                                    np.random.default_rng(0))
    out, moved = spacing.place_poisson_disk(pts, movers, nn0, capacity, 6.0,
                                            np.random.default_rng(1))
    assert moved.sum() >= 1                                 # the arm must act
    assert len(out) == len(pts)
    assert len(np.unique(out, axis=0)) == len(out)          # no collisions
    assert capacity[out[:, 0], out[:, 1]].all()             # all on valid pixels
    nn1, _ = spacing.nearest_neighbour_distance(spacing.mask_from_pts(out, shape))
    for k in range(len(pts)):
        assert nn1[k] >= nn0[k] - 1e-9                      # monotone per dot
    assert nn1.min() >= np.sqrt(8) - 1e-9                   # global parent floor
    # deterministic under fresh, identical seeded streams
    _, movers2, _ = spacing.greedy_violators(pts, shape, 3.0,
                                             np.random.default_rng(0))
    out2, moved2 = spacing.place_poisson_disk(pts, movers2, nn0, capacity, 6.0,
                                              np.random.default_rng(1))
    assert np.array_equal(out, out2) and np.array_equal(moved, moved2)


def test_along_strike_respects_cos_gate_and_count(frame):
    shape, footprint, catalogue, capacity, rng = frame
    # elevation ramp increasing with x -> gradient along x -> strike along y
    det = np.broadcast_to(np.arange(shape[1], dtype=np.float32), shape).copy()
    uy, ux = spacing.strike_field(det)
    coords = [(30, 30), (32, 32), (80, 80), (82, 82)]
    dots = _dots(shape, coords)
    pts = np.argwhere(dots)
    _a, movers, violated = spacing.greedy_violators(pts, shape, 3.0, rng)
    out, moved, no_strike = spacing.place_along_strike(
        pts, movers, violated, uy, ux, capacity, 5.0, 0.5, rng)
    assert moved.sum() >= 1                                 # the arm must act
    assert len(out) == len(pts)
    assert len(np.unique(out, axis=0)) == len(out)
    assert capacity[out[:, 0], out[:, 1]].all()
    nn1, _ = spacing.nearest_neighbour_distance(spacing.mask_from_pts(out, shape))
    assert nn1.min() >= np.sqrt(8) - 1e-9                   # global parent floor
    for k in np.flatnonzero(moved):
        a = violated[k]
        vy, vx = out[k] - pts[a]
        cos = abs(vy * uy[pts[a, 0], pts[a, 1]] + vx * ux[pts[a, 0], pts[a, 1]]) \
            / np.hypot(vy, vx)
        assert cos >= 0.5 - 1e-9


def test_strike_field_orientation_on_ramp(frame):
    shape = frame[0]
    det = np.broadcast_to(np.arange(shape[0], dtype=np.float32)[:, None], shape).copy()
    uy, ux = spacing.strike_field(det, sigma=0.0)
    # gradient along y -> strike along x: ux ~ +/-1, uy ~ 0
    assert abs(ux[60, 60]) == pytest.approx(1.0, abs=1e-6)
    assert abs(uy[60, 60]) == pytest.approx(0.0, abs=1e-6)


def test_lattice_movers_land_on_nodes(frame):
    shape, footprint, catalogue, capacity, rng = frame
    coords = [(30, 31), (32, 33), (70, 71), (72, 73), (95, 40)]
    dots = _dots(shape, coords)
    pts = np.argwhere(dots)
    out, moved, (oy, ox), n_anchored = spacing.place_lattice(
        pts, capacity, spacing=3, tol=1.5, window=4.0, rng=rng)
    assert moved.sum() >= 1                                 # the arm must act
    assert len(out) == len(pts)
    assert len(np.unique(out, axis=0)) == len(out)
    assert capacity[out[:, 0], out[:, 1]].all()
    nn1, _ = spacing.nearest_neighbour_distance(spacing.mask_from_pts(out, shape))
    assert nn1.min() >= np.sqrt(8) - 1e-9                   # global parent floor
    for k in np.flatnonzero(moved):
        y, x = out[k]
        assert (y - oy) % 3 == 0 and (x - ox) % 3 == 0     # exact lattice node
    # every dot is either anchored, moved, or unchanged for lack of a node
    assert n_anchored + moved.sum() <= len(pts)


def test_capacity_mask_enforces_footprint_and_collar(frame):
    shape, footprint, catalogue, capacity, rng = frame
    assert not capacity[0, 0]                       # outside footprint
    assert not capacity[60, 30]                     # catalogue pixel
    assert not capacity[58, 30]                     # inside 3 px collar
    assert capacity[55, 30]                         # 5 px away: valid
