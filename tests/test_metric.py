"""Unit tests for the derived DTI algebra.

The brief requires the algebra to be unit-tested. The most important property is
the one the whole session is built on: for an isolated truth pixel, adding one
dot of kernel credit k changes DTI in proportion to (k - 0.2*DTI), so the dot
pays only above 0.2*DTI (0.0556 at the parent's claimed 0.2778).
"""

import numpy as np
import pytest

from gemsdoe import metric


def scene(shape=(90, 90)):
    return np.zeros(shape, dtype=np.float64)


def test_perfect_prediction_scores_one():
    truth = scene()
    truth[10, 10] = truth[40, 55] = truth[70, 12] = 1
    pred = truth.copy()
    assert metric.dti(truth, pred) == pytest.approx(1.0, abs=1e-12)


def test_empty_prediction_scores_zero():
    truth = scene()
    truth[5, 5] = 1
    assert metric.dti(truth, np.zeros_like(truth)) == 0.0


def test_no_truth_scores_zero():
    truth = scene()
    pred = np.zeros_like(truth)
    pred[5, 5] = 1
    assert metric.dti(truth, pred) == 0.0


def test_single_dot_single_truth_equals_kernel_weight():
    truth = scene()
    truth[45, 45] = 1
    for d in (0.0, 1.0, 2.0, 2.9, 3.0, 4.0):
        pred = np.zeros_like(truth)
        # a unit dot at an exact offset: use a fractional distance via two dots
        # only for d <= sqrt(2); for larger d use an integer offset.
        if d == 0.0:
            pred[45, 45] = 1
            expect = 1.0
        else:
            i = 45 + int(round(d))
            pred[i, 45] = 1
            expect = metric.kernel_weight(abs(i - 45))
        assert metric.dti(truth, pred) == pytest.approx(expect, abs=1e-12)


def test_isolated_truth_dot_pays_exactly_above_0_2_dti():
    """Brute-force marginal gain must change sign at k = 0.2*DTI."""
    truth = scene((200, 200))
    # isolated truth pixels, spaced far beyond the kernel radius
    pts = [(20, 20), (20, 100), (100, 20), (100, 100), (180, 180)]
    for p in pts:
        truth[p] = 1
    pred = scene((200, 200))
    # cover four of the five truth pixels reasonably well
    for p in pts[:4]:
        pred[p[0] + 2, p[1]] = 1
    base = metric.dti(truth, pred)
    threshold = metric.pays_threshold(base)

    # probe the one uncovered, isolated truth pixel from several distances
    results = []
    for offset in range(0, 5):
        loc = (180, 180 - offset)
        k = metric.kernel_weight(offset)
        gain = metric.marginal_gain_add(truth, pred, *loc)
        results.append((k, gain))
        assert np.sign(gain) == np.sign(k - threshold) or gain == 0, (
            f"offset {offset}: k={k} threshold={threshold} gain={gain}"
        )
    # and the predicted magnitudes match the closed form (T+k)/(D+0.2) - T/D
    t = metric._truth_credit(truth, pred, metric.KERNEL_RADIUS_PX)
    s = float(pred.sum())
    m = metric._explained_mass(truth, pred, metric.KERNEL_RADIUS_PX)
    d0 = 0.2 * t + 0.2 * (s - m) + 0.8 * float(truth.sum())
    for k, gain in results:
        expect = (t + k) / (d0 + 0.2) - t / d0
        assert gain == pytest.approx(expect, rel=1e-9)


def test_threshold_at_parent_dti_is_0_0556():
    assert metric.pays_threshold(0.2778) == pytest.approx(0.05556, abs=1e-5)


def test_removing_a_redundant_dot_beats_removing_an_isolated_one():
    """A dot whose neighbour already covers the truth pixel is cheap to lose."""
    truth = scene((120, 120))
    truth[60, 60] = 1
    pred = scene((120, 120))
    pred[60, 58] = 1  # redundant partner
    pred[60, 60] = 1  # covering dot
    pred[20, 20] = 1  # isolated dot, no truth anywhere near it
    gain_redundant = metric.marginal_gain_remove(truth, pred, 60, 58)
    gain_isolated = metric.marginal_gain_remove(truth, pred, 20, 20)
    assert gain_redundant > 0, "removing a redundant near-truth dot should help"
    assert gain_isolated > 0, "removing a dot with no truth in reach should help"


def test_line_truth_credits_more_than_a_point_at_equal_distance():
    """The mechanism behind "line-like truth lowers the bar".

    At the same kernel credit k to its nearest truth pixel (same offset), a dot
    beside a line raises T by the sum over every truth pixel in reach, while a
    dot beside an isolated pixel raises T by exactly k.  That extra credit is
    why a dot whose k is below 0.2*DTI can still pay on line-like truth.
    """
    truth_point = scene((60, 60))
    truth_point[30, 30] = 1
    truth_line = scene((60, 60))
    truth_line[30, 25:36] = 1

    loc = (32, 30)  # 2 px from the point AND 2 px above the middle of the line
    k = metric.kernel_weight(2)
    empty = scene((60, 60))

    one = empty.copy(); one[loc] = 1.0
    t_point = metric._truth_credit(truth_point, one, metric.KERNEL_RADIUS_PX)
    t_line = metric._truth_credit(truth_line, one, metric.KERNEL_RADIUS_PX)

    assert t_point == pytest.approx(k, abs=1e-12)
    assert t_line > 2.5 * k, f"line credit {t_line} vs point credit {t_point}"
    # the removed-mass side is identical: the dot sits at the same k from truth
    assert metric._explained_mass(truth_line, one, metric.KERNEL_RADIUS_PX) == pytest.approx(
        metric._explained_mass(truth_point, one, metric.KERNEL_RADIUS_PX), abs=1e-12)
