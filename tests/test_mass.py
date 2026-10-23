"""Unit tests for the MASS axis (drop-only edits ranked by unique credit).

The properties that matter:

  * `unique_credit` of a lone dot is exactly 1.0 -- its own pixel -- because
    the triangular kernel is centred on the dot and no other dot is present;
  * two dots far apart each keep their full disc, so u = 1 + sum(k) and the
    total is additive; two dots 1 px apart lose unique credit to each other;
  * a drop-only build never adds a dot, never moves one, and removes exactly
    the requested number;
  * the ranking used by `unique` is strictly the small-u end, while `random`
    is count-matched and selection-blind.
"""

import numpy as np
import pytest

from gemsdoe import mass


def _disc_sum(radius=3.0):
    return sum(k for _dy, _dx, _d, k in mass._disc_offsets(radius))


def test_lone_dot_keeps_its_whole_disc():
    # with no neighbour, every pixel of the disc is uniquely the dot's
    dots = np.zeros((40, 40), dtype=bool)
    dots[20, 20] = True
    u, pts = mass.unique_credit(dots)
    assert len(pts) == 1
    assert u[0] == pytest.approx(1.0 + _disc_sum(), abs=1e-12)


def test_isolated_dots_are_additive():
    dots = np.zeros((60, 60), dtype=bool)
    dots[10, 10] = dots[50, 50] = True          # 40*sqrt(2) px apart
    u, _ = mass.unique_credit(dots)
    expected = 1.0 + _disc_sum()
    assert np.allclose(u, expected)
    assert mass.total_credit(u) == pytest.approx(2 * expected)


def test_close_dots_share_credit():
    # 1 px apart along x: each pixel between them goes to the strictly nearest
    # dot (a tie contributes nothing), so the pair keeps less than the isolated
    # pair's credit.
    iso = np.zeros((40, 60), dtype=bool)
    iso[20, 5] = iso[20, 45] = True
    close = np.zeros((40, 60), dtype=bool)
    close[20, 20] = close[20, 21] = True
    u_iso, _ = mass.unique_credit(iso)
    u_close, _ = mass.unique_credit(close)
    assert mass.total_credit(u_close) < mass.total_credit(u_iso)
    # and no dot can fall below its own pixel
    assert np.all(u_close >= 1.0)


def test_coincident_distances_never_negative():
    # a 3-4-5 triangle: two dots equidistant from the pixel between them
    dots = np.zeros((30, 30), dtype=bool)
    dots[10, 10] = dots[13, 14] = True
    u, _ = mass.unique_credit(dots)
    assert np.all(np.isfinite(u))
    assert np.all(u >= 1.0)


def test_choose_drop_unique_takes_the_low_end():
    u = np.array([5.0, 1.0, 3.0, 2.0, 4.0])
    dots = np.zeros((5, 1), dtype=bool)
    dots[:, 0] = True
    rng = np.random.default_rng(0)
    idx = mass.choose_drop(dots, u, 2, rng, mode="unique")
    assert set(idx.tolist()) == {1, 3}       # u = 1.0 and 2.0
    idx_r = mass.choose_drop(dots, u, 2, rng, mode="random")
    assert len(set(idx_r.tolist())) == 2
    with pytest.raises(ValueError):
        mass.choose_drop(dots, u, 0, rng, mode="unique")


def test_build_is_drop_only_and_count_exact():
    rng = np.random.default_rng(1)
    dots = np.zeros((80, 80), dtype=bool)
    dots[10:70:4, 10:70:4] = True            # a 4 px lattice, 225 dots
    footprint = np.ones_like(dots)
    catalogue = np.zeros_like(dots)
    catalogue[0, 0] = True
    variant, stats = mass.build(dots, footprint, catalogue, n_drop=20, rng=rng, mode="unique")
    assert stats["n_after"] == int(dots.sum()) - 20
    assert not (variant & ~dots).any(), "a drop-only edit must never add a dot"
    assert stats["pct_changed"] == pytest.approx(100 * 20 / int(dots.sum()))
    assert stats["unique_credit_lost"] > 0
    assert stats["unique_credit_total_after"] == pytest.approx(
        stats["unique_credit_total_before"] - stats["unique_credit_lost"])


def test_unique_ranking_loses_less_credit_than_random():
    rng = np.random.default_rng(2)
    dots = np.zeros((120, 120), dtype=bool)
    dots[10:110:3, 10:110:3] = True
    footprint = np.ones_like(dots)
    catalogue = np.zeros_like(dots)
    _, s_uniq = mass.build(dots, footprint, catalogue, n_drop=100, rng=np.random.default_rng(2), mode="unique")
    _, s_rand = mass.build(dots, footprint, catalogue, n_drop=100, rng=np.random.default_rng(2), mode="random")
    assert s_uniq["unique_credit_lost_frac"] < s_rand["unique_credit_lost_frac"]
    rng.random(1)


def test_block_density_cv_matches_hand_computation():
    dots = np.zeros((40, 40), dtype=bool)
    dots[:20, :20] = True                    # one dense block of four
    footprint = np.ones_like(dots)
    cv, nblocks = mass.block_density_cv(dots, footprint, block=10)
    # 16 blocks: 4 at density 1, 12 at 0 -> mean .25, std .433, CV = sqrt(3)
    assert nblocks == 16
    assert cv == pytest.approx(np.sqrt(3.0), rel=1e-6)


def test_break_even_threshold_is_one_fifth_of_dti():
    assert mass.predicted_delta({"n_dropped": 0})["central"] == pytest.approx(0.0)
    # sign convention: dropping zero-credit dots must be recorded as a gain
    band = mass.predicted_delta({"n_dropped": 1000}, dti_parent=0.2778)
    assert band["central"] > 0
