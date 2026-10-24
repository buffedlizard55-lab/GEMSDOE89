"""Unit tests for gemsdoe.prune module (PRUNE axis)."""

from __future__ import annotations

import numpy as np
import pytest

from gemsdoe import prune


def test_compute_catalogue_distance():
    cat = np.zeros((10, 10), dtype=bool)
    cat[5, 5] = True
    d = prune.compute_catalogue_distance(cat)
    assert d[5, 5] == 0.0
    assert np.isclose(d[5, 6], 1.0)
    assert np.isclose(d[6, 6], np.sqrt(2))
    assert np.isclose(d[5, 7], 2.0)
    assert np.isclose(d[5, 8], 3.0)


def test_select_swapin_dots():
    d28 = np.zeros((10, 10), dtype=bool)
    d_cat = np.full((10, 10), 5.0)

    # dot at d=1.0 -> should NOT be included (> 1.0)
    d28[1, 1] = True
    d_cat[1, 1] = 1.0

    # dot at d=1.414 -> should be included (1.0 < d <= 2.0)
    d28[2, 2] = True
    d_cat[2, 2] = 1.414

    # dot at d=2.0 -> should be included
    d28[3, 3] = True
    d_cat[3, 3] = 2.0

    # dot at d=2.5 -> should NOT be included (> 2.0)
    d28[4, 4] = True
    d_cat[4, 4] = 2.5

    res = prune.select_swapin_dots(d28, d_cat, min_dist=1.0, max_dist=2.0)
    assert not res[1, 1]
    assert res[2, 2]
    assert res[3, 3]
    assert not res[4, 4]
    assert res.sum() == 2


def test_refill_greedy_farthest_synthetic():
    h, w = 30, 30
    exist = np.zeros((h, w), dtype=bool)
    exist[5, 5] = True
    exist[25, 25] = True

    cand = np.zeros((h, w), dtype=bool)
    cand[10:20, 10:20] = True

    n_needed = 5
    pts = prune.refill_greedy_farthest(cand, exist, n_needed, min_sep_px=2.0)
    assert len(pts) == n_needed

    # Check pairwise separation >= 2.0
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dy = pts[i, 0] - pts[j, 0]
            dx = pts[i, 1] - pts[j, 1]
            dist_sq = dy * dy + dx * dx
            assert dist_sq >= 4.0 - 1e-6


def test_refill_greedy_farthest_determinism():
    h, w = 40, 40
    exist = np.zeros((h, w), dtype=bool)
    exist[0, 0] = True
    cand = np.zeros((h, w), dtype=bool)
    cand[15:35, 15:35] = True

    pts1 = prune.refill_greedy_farthest(cand, exist, 10, min_sep_px=2.0)
    pts2 = prune.refill_greedy_farthest(cand, exist, 10, min_sep_px=2.0)
    assert np.array_equal(pts1, pts2)


def test_build_prune_synthetic():
    h, w = 50, 50
    footprint = np.ones((h, w), dtype=bool)
    cat = np.zeros((h, w), dtype=bool)
    cat[25, :] = True  # catalogue fault across row 25

    d_cat = prune.compute_catalogue_distance(cat)

    # Ancestor d28 has dots spaced every 3 pixels across the grid
    d28 = np.zeros((h, w), dtype=bool)
    d28[::3, ::3] = True
    d28[cat] = False

    # Parent R0 prunes d28 at d_cat > 2.0
    r0 = d28 & (d_cat > 2.0)
    n_r0 = int(r0.sum())

    # Ridge mask h19
    h19 = np.zeros((h, w), dtype=bool)
    h19[::3, :] = True
    h19[:, ::3] = True
    h19[cat] = False

    # Test c1p0
    v_c1, s_c1 = prune.build_prune("c1p0", r0, d28, h19, cat, footprint, seed=42)
    assert int(v_c1.sum()) == n_r0
    assert s_c1["catalogue_mass"] == 0
    assert (v_c1 & cat).sum() == 0
    assert s_c1["min_catalogue_distance_px"] > 1.0

    # Test c3p0
    v_c3, s_c3 = prune.build_prune("c3p0", r0, d28, h19, cat, footprint, seed=42)
    assert int(v_c3.sum()) == n_r0
    assert s_c3["catalogue_mass"] == 0
    assert (v_c3 & cat).sum() == 0
    assert s_c3["min_catalogue_distance_px"] > 3.0

    # Test c4p0
    v_c4, s_c4 = prune.build_prune("c4p0", r0, d28, h19, cat, footprint, seed=42)
    assert int(v_c4.sum()) == n_r0
    assert s_c4["catalogue_mass"] == 0
    assert (v_c4 & cat).sum() == 0
    assert s_c4["min_catalogue_distance_px"] > 4.0


def test_block_density_cv():
    foot = np.ones((100, 100), dtype=bool)
    dots = np.zeros((100, 100), dtype=bool)
    dots[::5, ::5] = True
    cv = prune.block_density_cv(dots, foot, block_px=20)
    assert np.isfinite(cv)
    assert cv >= 0.0
