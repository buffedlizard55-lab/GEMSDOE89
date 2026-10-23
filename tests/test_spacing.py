"""SPACING axis: invariants that must hold without the competition data.

These tests build a synthetic field on a small grid, so they run in CI where
the pinned rasters are absent.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

from gemsdoe import spacing
from gemsdoe.spacing import (CATALOGUE_CLEARANCE_PX, MIN_SEP_PARENT_PX,
                             coverage_area, hard_disk_independent_set,
                             relocate, strike_orientation)


def _field(rows=70, cols=70, catalogue_col=None):
    """Two diagonal ribbons of dots (a miniature version of the parent field).

    The parent's dots sit on ribbons at the hard-disk spacing, not on a regular
    lattice, so a ribbon field is the right toy model: it has a definite local
    strike and a saturated interior.
    """
    dots = np.zeros((rows, cols), dtype=bool)
    # one diagonal ribbon on a 2*sqrt(2) px stride (the parent's own hard disk),
    # plus a parallel neighbour; both stay >= 2.828 px from every other dot.
    for t in range(6, cols - 6, 2):
        dots[t, t] = True
    for t in range(6, cols - 12, 2):
        dots[t + 6, t] = True
    footprint = np.ones((rows, cols), dtype=bool)
    cat = np.zeros((rows, cols), dtype=bool)
    if catalogue_col is not None:
        cat[:, catalogue_col] = True
        dots[:, catalogue_col] = False
    clearance = ndi.distance_transform_edt(~cat).astype(np.float32)
    return dots, footprint, clearance, cat


def _min_pair(points):
    if len(points) < 2:
        return np.inf
    d, _ = cKDTree(points).query(points, k=2)
    return float(d[:, 1].min())


def test_independent_set_respects_target_and_keeps_order_independent_size():
    dots, _, _, _ = _field()
    pts = spacing.dot_points(dots)
    target = 3.0
    keep = hard_disk_independent_set(pts, target, np.random.default_rng(1))
    assert keep.any() and not keep.all()
    assert _min_pair(pts[keep]) >= target - 1e-9
    # every rejected dot really is inside the target radius of a kept dot
    tree = cKDTree(pts[keep])
    d, _ = tree.query(pts[~keep])
    assert (d < target + 1e-9).all()


def test_relocate_preserves_count_and_disk_invariant():
    dots, footprint, clearance, cat = _field(catalogue_col=20)
    parent = dots.copy()
    rng = np.random.default_rng(7)
    variant, stats = relocate(
        parent_dots=parent, footprint=footprint, clearance_px=clearance,
        target_sep=3.0, mode="poisson", rng=rng, window=3)

    # count fixed
    assert int(variant.sum()) == int(parent.sum()) == stats["n_dots"]
    # nothing new lands on or near the catalogue
    added = variant & ~parent
    assert clearance[added].min() >= CATALOGUE_CLEARANCE_PX
    # never tighter than the parent's own hard disk
    assert _min_pair(spacing.dot_points(variant)) >= MIN_SEP_PARENT_PX - 1e-9
    # the toy field is tiny, so the fraction is not the 1-50 % bound checked on
    # the real parent by tools/build_spacing.py; here only that it moves some.
    assert stats["n_moved"] > 0
    assert 0.0 < stats["pct_changed"] < 100.0
    # and it does not re-cluster the field
    assert stats["nn_median_after_px"] >= stats["nn_median_before_px"]
    assert stats["nn_min_after_px"] >= MIN_SEP_PARENT_PX - 1e-9


def test_relocate_is_deterministic():
    dots, footprint, clearance, _ = _field()
    a, _ = relocate(parent_dots=dots, footprint=footprint, clearance_px=clearance,
                    target_sep=3.0, mode="poisson", rng=np.random.default_rng(5), window=3)
    b, _ = relocate(parent_dots=dots, footprint=footprint, clearance_px=clearance,
                    target_sep=3.0, mode="poisson", rng=np.random.default_rng(5), window=3)
    assert np.array_equal(a, b)


def test_along_strike_mode_runs_and_keeps_count():
    dots, footprint, clearance, _ = _field()
    strike, coherence = strike_orientation(dots)
    assert strike.shape == dots.shape and np.isfinite(strike).all()
    assert 0.0 <= float(coherence.min()) and float(coherence.max()) <= 1.0
    variant, stats = relocate(
        parent_dots=dots, footprint=footprint, clearance_px=clearance,
        target_sep=3.0, mode="along", rng=np.random.default_rng(3),
        window=3, corridor=2, strike=strike)
    assert int(variant.sum()) == int(dots.sum())
    assert stats["mode"] == "along"
    assert stats["n_moved"] > 0
    assert clearance[variant & ~dots].min() >= CATALOGUE_CLEARANCE_PX


def test_relocation_never_leaves_the_footprint():
    dots, footprint, clearance, _ = _field()
    variant, _ = relocate(parent_dots=dots, footprint=footprint, clearance_px=clearance,
                          target_sep=3.0, mode="poisson", rng=np.random.default_rng(2), window=3)
    assert not (variant & ~footprint).any()


def test_coverage_area_counts_union_and_grows_with_spacing():
    lone = np.zeros((40, 40), dtype=bool)
    lone[20, 20] = True
    pair_tight = lone.copy()
    pair_tight[20, 22] = True
    pair_wide = lone.copy()
    pair_wide[20, 25] = True
    a1 = coverage_area(lone)
    a2 = coverage_area(pair_tight)
    a3 = coverage_area(pair_wide)
    assert a1 < a2 < a3          # a redundant neighbour adds little, a far one more
    assert a3 < 2 * a1 + 1e-9    # never twice, because the disks still overlap


def test_prediction_algebra():
    # fixed mass, +2 % coverage, parent DTI 0.2778 -> (1-0.2*DTI)*DTI*0.02
    out = spacing.predict_dti_change(0.2778, 100.0, 102.0)
    assert out["coverage_rel_change"] == pytest.approx(0.02)
    assert out["point"] == pytest.approx((1 - 0.2 * 0.2778) * 0.2778 * 0.02)
    assert out["band"][0] < 0 < out["band"][1]
    # no coverage change -> no predicted change
    flat = spacing.predict_dti_change(0.2778, 100.0, 100.0)
    assert flat["point"] == pytest.approx(0.0)
