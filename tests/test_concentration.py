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
