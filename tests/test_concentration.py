"""CONCENTRATION block-prior and exact-marginal unit tests."""

import numpy as np
import pytest

from gemsdoe import concentration, metric


def test_marginal_rankings_match_brute_force_metric():
    rng = np.random.default_rng(19)
    truth = np.zeros((70, 70), dtype=bool)
    dots = np.zeros_like(truth)
    truth.flat[rng.choice(truth.size, 95, replace=False)] = True
    dots.flat[rng.choice(dots.size, 16, replace=False)] = True
    free = np.flatnonzero(~dots.ravel())
    candidates = np.column_stack(np.unravel_index(rng.choice(free, 9, replace=False), dots.shape))

    got = concentration.marginal_rankings(truth, dots, candidates)
    pred = dots.astype(np.float64)
    base = metric.dti(truth, pred)
    assert got["base"]["DTI"] == pytest.approx(base, abs=1e-12)

    for i, (y, x) in enumerate(got["points"]):
        brute = metric.marginal_gain_remove(truth, pred, int(y), int(x))
        assert got["remove_delta"][i] == pytest.approx(brute, rel=1e-9, abs=1e-12)
    for i, (y, x) in enumerate(candidates):
        brute = metric.marginal_gain_add(truth, pred, int(y), int(x))
        assert got["add_delta"][i] == pytest.approx(brute, rel=1e-9, abs=1e-12)


def test_marginal_rankings_respect_equal_distance_ties():
    truth = np.zeros((31, 31), dtype=bool)
    dots = np.zeros_like(truth)
    truth[15, 15] = True
    dots[15, 13] = dots[15, 17] = True
    candidates = np.array([[15, 15], [2, 2]])
    got = concentration.marginal_rankings(truth, dots, candidates)
    # Either equidistant dot can be removed without reducing T.
    assert np.allclose(got["remove_unique_truth_credit"], 0.0)
    for i, (y, x) in enumerate(got["points"]):
        brute = metric.marginal_gain_remove(truth, dots.astype(float), int(y), int(x))
        assert got["remove_delta"][i] == pytest.approx(brute, abs=1e-12)


def test_sequential_greedy_matches_brute_force_best_addition():
    rng = np.random.default_rng(7)
    truth = np.zeros((45, 45), dtype=bool)
    truth.flat[rng.choice(truth.size, 55, replace=False)] = True
    dots = np.zeros_like(truth)
    dots.flat[rng.choice(dots.size, 8, replace=False)] = True
    free_truth = np.flatnonzero((truth & ~dots).ravel())
    candidates = np.column_stack(np.unravel_index(
        rng.choice(free_truth, 12, replace=False), truth.shape
    ))
    got = concentration.greedy_on_truth_additions(truth, dots, candidates, 7, seed=5)
    pred = dots.astype(np.float64)
    remaining = set(range(len(candidates)))
    for step, chosen in enumerate(got["indices"]):
        y, x = candidates[chosen]
        brute_chosen = metric.marginal_gain_add(truth, pred, int(y), int(x))
        brute_best = max(
            metric.marginal_gain_add(truth, pred, int(candidates[j, 0]), int(candidates[j, 1]))
            for j in remaining
        )
        assert brute_chosen == pytest.approx(brute_best, rel=1e-9, abs=1e-12)
        assert got["exact_marginal_dti"][step] == pytest.approx(brute_chosen, rel=1e-9, abs=1e-12)
        pred[y, x] = 1.0
        remaining.remove(int(chosen))


def test_block_prior_and_nested_fixed_count_build():
    shape = (80, 80)
    footprint = np.ones(shape, dtype=bool)
    h19 = np.ones(shape, dtype=bool)
    dots = np.zeros(shape, dtype=bool)
    dots[4:80:8, 4:80:8] = True
    catalogue = np.zeros(shape, dtype=bool)
    # One high-prior 2 km block; all other blocks have zero catalogue density.
    catalogue[45:50, 45:50] = True
    # Keep the catalogue itself out of the surrogate/candidate field, as in the real build.
    h19[catalogue] = False
    dots &= h19
    variants, audit = concentration.build_family(
        dots, h19, footprint, catalogue, n_moves=(2, 4), block_px=20, seed=3,
        source_quantile=0.50, target_quantile=0.95,
    )
    assert set(variants) == {2, 4}
    assert audit["block_stats"]["source_cut_per_1000px"] == 0.0
    assert audit["block_stats"]["target_cut_per_1000px"] > 0.0

    removed_sets, added_sets = [], []
    for n in (2, 4):
        variant, stats = variants[n]
        removed = dots & ~variant
        added = variant & ~dots
        removed_sets.append(removed)
        added_sets.append(added)
        assert int(variant.sum()) == int(dots.sum())
        assert int(removed.sum()) == int(added.sum()) == n
        assert not (removed & ~audit["source_mask"]).any()
        assert not (added & ~audit["target_mask"]).any()
        assert not (added & catalogue).any()
        assert not (variant & ~h19).any()
        assert stats["n_moved"] == n
        assert stats["cv_2km_before"] == stats["cv_2km_before"]  # finite/NaN report only
        assert all(stats["mask_gates"].values())
    assert not (removed_sets[0] & ~removed_sets[1]).any()
    assert not (added_sets[0] & ~added_sets[1]).any()


def test_prediction_is_a_transparent_linear_scenario():
    pred = concentration.predicted_delta(1000, -0.001, anchor_d=10000)
    assert pred["lo"] == pytest.approx(-0.006)
    assert pred["central"] == pytest.approx(0.0015)
    assert pred["hi"] == pytest.approx(0.009)
    assert pred["h19_surrogate_counterindicator"] == -0.001
    assert pred["evidence_class"] == "MODEL"
