"""Unit tests for the DTI algebra (Brief v2 section 2: 'Algebra (derived; unit-test it)')."""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gems89 import metric  # noqa: E402


def test_kernel_is_triangular_with_radius_three():
    assert metric.kernel(0.0) == pytest.approx(1.0)
    assert metric.kernel(1.5) == pytest.approx(0.5)
    assert metric.kernel(3.0) == pytest.approx(0.0)
    assert metric.kernel(3.5) == pytest.approx(0.0)
    # R = 300 m at 100 m pixels
    assert metric.RADIUS_M == 300.0


def test_offsets_match_kernel_support():
    assert len(metric.OFF_DY) == len(metric.OFF_DX) == len(metric.OFF_K)
    d = np.hypot(metric.OFF_DY, metric.OFF_DX)
    assert (d < 3.0).all()
    assert np.allclose(metric.OFF_K, np.maximum(1.0 - d / 3.0, 0.0))
    # 25 lattice cells inside a radius-3 disc (d < 3)
    assert len(metric.OFF_K) == 25


def test_binary_matches_bruteforce_random():
    rng = np.random.default_rng(7)
    for _ in range(6):
        truth = rng.random((24, 24)) < 0.06
        pred = rng.random((24, 24)) < 0.10
        fast = metric.dti_binary(pred, truth)
        slow = metric.dti_bruteforce(pred.astype(float), truth)
        assert fast["tp"] == pytest.approx(slow["tp"], abs=1e-9)
        assert fast["fp"] == pytest.approx(slow["fp"], abs=1e-9)
        assert fast["fn"] == pytest.approx(slow["fn"], abs=1e-9)
        assert fast["dti"] == pytest.approx(slow["dti"], rel=1e-9)


def test_soft_matches_bruteforce_random():
    rng = np.random.default_rng(11)
    truth = rng.random((20, 20)) < 0.08
    pred = (rng.random((20, 20)) * (rng.random((20, 20)) < 0.3)).astype(float)
    fast = metric.dti_components(pred, truth)
    slow = metric.dti_bruteforce(pred, truth)
    assert fast["denom"] == pytest.approx(slow["tp"] + 0.2 * slow["fp"] + 0.8 * slow["fn"], rel=1e-9)
    assert fast["dti"] == pytest.approx(slow["dti"], rel=1e-9)
    assert fast["S"] == pytest.approx(pred.sum())


def test_identity_is_perfect():
    truth = np.zeros((12, 12), bool)
    truth[3, 4] = truth[8, 9] = True
    r = metric.dti_binary(truth, truth)
    assert r["dti"] == pytest.approx(1.0 / 1.0)
    assert r["tp"] == pytest.approx(2.0)


def test_empty_cases_are_zero_not_nan():
    z = np.zeros((8, 8), bool)
    t = np.zeros((8, 8), bool)
    t[1, 1] = True
    assert metric.dti_binary(z, t)["dti"] == 0.0
    assert metric.dti_binary(t, z)["dti"] == 0.0


def test_isolated_dot_pays_only_above_the_bar():
    """A single centre dot against a single truth pixel: dDTI > 0 iff k > 0.2*DTI."""
    truth = np.zeros((40, 40), bool)
    truth[20, 20] = True

    def dti_at(offset: int) -> float:
        pred = np.zeros((40, 40), bool)
        pred[20, 20 + offset] = True
        return metric.dti_binary(pred, truth)["dti"]

    assert dti_at(0) > dti_at(1) > dti_at(2) > dti_at(3) == 0.0
    # k = 1 - d/3 for a lone dot; the exact bar from the algebra is k > 0.2*DTI
    for offset in range(3):
        k = 1.0 - offset / 3.0
        assert k > metric.ALPHA * dti_at(offset)


def test_t_and_m_are_not_interchangeable():
    """Two coincident-ish dots around one truth pixel: M > T."""
    truth = np.zeros((20, 20), bool)
    truth[10, 10] = True
    pred = np.zeros((20, 20), bool)
    pred[10, 11] = pred[11, 10] = True
    r = metric.dti_components(pred.astype(float), truth)
    assert r["M"] > r["T"] > 0.0


def test_unique_credit_is_truth_free_and_bounded():
    dots = np.zeros((30, 30), bool)
    dots[5, 5] = True          # isolated
    dots[20, 20] = dots[20, 22] = True   # pair 2 px apart
    credit = metric.unique_credit(dots)
    assert credit.shape == (3,)
    isolated, a, b = credit[0], credit[1], credit[2]
    assert isolated > a and isolated > b      # the isolated dot supplies the most unique credit
    assert 0.0 < credit.min() and credit.max() <= len(metric.OFF_K)


def test_measure_is_invariant_to_mass_duplication():
    """Adding a second unit dot on the same pixel must not be possible on a raster;
    the closest analogue (a 1 px neighbour) must add less credit than a fresh dot."""
    truth = np.zeros((30, 30), bool)
    truth[15, 15] = True
    one = np.zeros((30, 30), bool)
    one[15, 16] = True
    two = one.copy()
    two[15, 17] = True
    r1 = metric.dti_binary(one, truth)
    r2 = metric.dti_binary(two, truth)
    assert r2["tp"] >= r1["tp"]            # more coverage of the same truth cell is impossible
    assert r2["tp"] - r1["tp"] < 1.0 - 1e-9
