"""Unit tests for the CONCENTRATION axis (synthetic grids only).

The competition rasters are not present in CI, so every test here builds its
own tiny grid and checks the invariants the axis claims: block prior, disjoint
strata, count preservation, catalogue clearance, donor/recipient containment,
placement spacing and byte-level determinism.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy.spatial import cKDTree

from gemsdoe import concentration as C


def _grid(n=60, block=10, cat_cols=(2, 3), dot_rng=None):
    foot = np.ones((n, n), dtype=bool)
    cat = np.zeros((n, n), dtype=bool)
    for x in cat_cols:
        cat[:, x] = True
    dots = np.zeros((n, n), dtype=bool)
    if dot_rng is not None:
        ys, xs = dot_rng
        dots[ys, xs] = True
    rank = np.zeros((n, n), dtype=np.float64)
    edge = np.zeros((n, n), dtype=np.float32)
    return foot, cat, dots, rank, edge


def test_block_prior_density_and_eligibility():
    foot, cat, *_ = _grid(n=20, block=5, cat_cols=(1,))
    prior, eligible, n_foot, n_cat = C.block_prior(cat, foot, block_px=5)
    assert prior.size == 4 * 4
    assert n_foot[0] == 25 and n_cat[0] == 5          # block (0,0): 5 catalogue px
    assert prior[0] == pytest.approx(5 / 25)
    assert prior[1] == 0.0                            # block (0,1): none
    assert eligible.all()
    # a block 40 % inside the footprint is not eligible
    foot2 = foot.copy()
    foot2[0:3, 0:5] = False                           # 40 % of block (0,0) removed
    _p, elig2, nf2, _nc = C.block_prior(cat, foot2, block_px=5)
    assert nf2[0] == 10 and not elig2[0]


def test_expand_blocks_roundtrip():
    bm = np.zeros(16, dtype=bool)
    bm[[0, 5, 15]] = True
    full = C.expand_blocks(bm, (20, 20), block_px=5)
    assert full[0, 0] and full[4, 4] and not full[0, 5]
    assert full.sum() == 3 * 25


def test_strata_disjoint_and_named():
    foot, cat, *_ = _grid(n=40, block=10)
    cat[30:40, 30:40] = True                          # make one block prior-high
    prior, eligible, _, _ = C.block_prior(cat, foot, block_px=20)
    st = C.strata(prior, eligible, 0.75)
    assert not (st["zero"] & st["high"]).any()
    assert st["zero"].sum() > 0 and st["high"].sum() > 0
    assert prior[st["high"]].min() >= st["high_cut"]


def test_greedy_place_spacing_count_and_determinism():
    legal = np.ones((30, 30), dtype=bool)
    score = np.random.default_rng(0).random((30, 30)).astype(np.float32)
    pts = C.greedy_place(score, legal, 25, min_sep=2.8)
    assert len(pts) == 25
    d, _ = cKDTree(pts).query(pts, k=2)
    assert d[:, 1].min() >= 2.8 - 1e-9
    again = C.greedy_place(score, legal, 25, min_sep=2.8)
    assert np.array_equal(pts, again)
    # the highest-scoring legal pixel is always taken first
    assert tuple(pts[0]) == tuple(np.unravel_index(np.argmax(score), score.shape))


def test_greedy_place_refuses_impossible_count():
    legal = np.zeros((10, 10), dtype=bool)
    legal[0, 0] = True
    with pytest.raises(ValueError):
        C.greedy_place(np.zeros((10, 10)), legal, 2)


def test_select_donor_dots_rank_order():
    dots = np.zeros((20, 20), dtype=bool)
    dots[2, 2] = dots[2, 8] = dots[2, 14] = dots[10, 10] = True
    rank = np.zeros((20, 20))
    rank[2, 2], rank[2, 8], rank[2, 14], rank[10, 10] = 0.9, 0.1, 0.5, 0.3
    region = np.zeros((20, 20), dtype=bool)
    region[:, :] = True
    rng = np.random.default_rng(7)
    pts = C.select_donor_dots(dots, region, rank, 2, rng)
    got = sorted(rank[y, x] for y, x in pts)
    assert got == [0.1, 0.3]
    again = C.select_donor_dots(dots, region, rank, 2, np.random.default_rng(7))
    assert np.array_equal(pts, again)


def _build_fixture(n=120, block=20):
    """Synthetic landscape with both strata populated and room to place dots.

    Catalogue: a 3-px-wide band at x = 100..102, so the right-most block column
    (x >= 100) is the only high-prior stratum and the rest is zero-prior.
    Parent dots: a 6 px lattice over the left half (zero-prior blocks) plus a
    few dots beside the band (high-prior blocks), so both arms have donors.
    """
    foot = np.ones((n, n), dtype=bool)
    cat = np.zeros((n, n), dtype=bool)
    cat[:, 100:103] = True
    dots = np.zeros((n, n), dtype=bool)
    ys = np.arange(3, n, 6)
    for x in range(3, 60, 6):
        dots[ys, x] = True
    for x in (108, 114):
        dots[ys, x] = True
    rng = np.random.default_rng(3)
    rank = rng.random((n, n))
    edge = rng.random((n, n)).astype(np.float32)
    return foot, cat, dots, rank, edge


def test_build_toward_preserves_count_and_containment():
    foot, cat, dots, rank, edge = _build_fixture()
    variant, stats = C.build(dots, foot, cat, edge, rank, fraction=0.10,
                             direction="toward", rng=np.random.default_rng(11),
                             block_px=20)
    assert variant.sum() == dots.sum()
    assert stats["n_moved"] == int(round(0.10 * dots.sum()))
    # zero catalogue mass and full clearance
    assert not (variant & cat).any()
    from scipy import ndimage as ndi
    clearance = ndi.distance_transform_edt(~cat)
    added_only = variant & ~dots
    assert clearance[added_only].min() >= C.CATALOGUE_CLEARANCE_PX - 1e-9
    # removed dots are all inside the donor (zero-prior) blocks, added all inside recipients
    prior, eligible, _, _ = C.block_prior(cat, foot, block_px=20)
    st = C.strata(prior, eligible, 0.75)
    donor = C.expand_blocks(st["zero"], dots.shape, 20)
    recip = C.expand_blocks(st["high"], dots.shape, 20)
    removed = dots & ~variant
    added = variant & ~dots
    assert (removed & ~donor).sum() == 0
    assert (added & ~recip).sum() == 0
    # added dots respect the parent's suppression radius
    surv = dots & ~removed
    d, _ = cKDTree(np.argwhere(surv)).query(np.argwhere(added))
    assert d.min() >= C.MIN_SEP_PX - 1e-9


def test_build_is_deterministic():
    foot, cat, dots, rank, edge = _build_fixture()
    a, sa = C.build(dots, foot, cat, edge, rank, 0.10, "toward",
                    np.random.default_rng(5), block_px=20)
    b, sb = C.build(dots, foot, cat, edge, rank, 0.10, "toward",
                    np.random.default_rng(5), block_px=20)
    assert np.array_equal(a, b)
    assert sa["n_moved"] == sb["n_moved"]


def test_build_away_reverses_strata():
    foot, cat, dots, rank, edge = _build_fixture()
    toward, st_t = C.build(dots, foot, cat, edge, rank, 0.05, "toward",
                           np.random.default_rng(2), block_px=20)
    away, st_a = C.build(dots, foot, cat, edge, rank, 0.05, "away",
                         np.random.default_rng(2), block_px=20)
    assert st_t["dots_in_zero_blocks_after"] < st_t["dots_in_zero_blocks_before"]
    assert st_a["dots_in_zero_blocks_after"] > st_a["dots_in_zero_blocks_before"]
    assert not np.array_equal(toward, away)


def test_predicted_delta_sign_and_null():
    t = C.predicted_delta(3765, "toward")
    a = C.predicted_delta(3765, "away")
    assert t["null_dp_0p00"] == 0.0
    assert t["central"] == pytest.approx(-a["central"])
    assert t["central"] == pytest.approx(3765 * 2.5 / 2.0e4 * 0.02)
    assert C.predicted_delta(7530, "toward")["central"] == pytest.approx(2 * t["central"])


def test_edge_score_rejects_nodata_sentinel():
    band = np.zeros((20, 20), dtype=np.float32)
    band[:, 10:] = -3.4028235e38                     # the stack's nodata sentinel
    foot = np.ones((20, 20), dtype=bool)
    g = C.gradient_magnitude(band, foot)
    assert np.isfinite(g).all()
    assert g[:, 10:].max() == 0.0                    # sentinel must not create an edge


# 2 km exact-marginal family
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
    pred = concentration.predicted_delta_h19(1000, -0.001, anchor_d=10000)
    assert pred["lo"] == pytest.approx(-0.006)
    assert pred["central"] == pytest.approx(0.0015)
    assert pred["hi"] == pytest.approx(0.009)
    assert pred["h19_surrogate_counterindicator"] == -0.001
    assert pred["evidence_class"] == "MODEL"
