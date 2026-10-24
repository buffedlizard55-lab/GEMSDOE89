"""Unit tests for the CONCENTRATION axis (no competition data required)."""

from __future__ import annotations

import numpy as np
import pytest
from scipy.ndimage import distance_transform_edt

from gemsdoe import concentration_12p8km as concentration, parent


def _synthetic_concentration_scene():
    """4x4 grid of 32x32 blocks (128x128 total) with low-prior and high-prior blocks."""
    h, w = 128, 128
    foot = np.ones((h, w), dtype=bool)
    foot[:3, :] = False  # non-trivial outer margin

    # Catalogue faults concentrated in the bottom-right blocks (rows 64..128, cols 64..128):
    # intersecting strands + en-echelon step-overs + terminations
    cat = np.zeros((h, w), dtype=bool)
    cat[75:92, 78] = True
    cat[83, 72:86] = True       # junction + tips
    cat[90:108, 84] = True      # 6-px step-over from strand 1
    cat[102:118, 108] = True
    cat[110, 102:116] = True    # second junction + tips
    # Plus one tiny trace in top-left with an inherited collar dot nearby
    cat[12:16, 12] = True

    # Build a ridge field across all blocks so R0 starts roughly uniform across blocks
    h19 = np.zeros((h, w), dtype=bool)
    for row in (18, 28, 44, 54, 72, 98, 114):
        h19[row, 8:120] = True
    # Add an inherited collar pixel at distance sqrt(5)=2.236 from (15, 12) -> (17, 13)
    h19[17, 13] = True

    r0, _ = parent.rebuild_r0_mask(h19, foot, cat, r_min=2.8, collar_px=2.0)

    # Synthetic feature bands with sentinel nodata and structured linear scarps in bottom-right
    rng = np.random.default_rng(20261023)
    yy, xx = np.indices((h, w), dtype=np.float32)
    scarp_step = 40.0 * np.tanh((yy - 86.0) / 1.5) + 35.0 * np.tanh((xx - 96.0) / 1.5)
    bands = {
        3: np.abs(rng.normal(10.0, 2.0, (h, w))).astype(np.float32),
        4: np.where(yy >= 64, 45.0, 8.0).astype(np.float32) + rng.normal(0, 0.5, (h, w)).astype(np.float32),
        5: np.abs(rng.normal(0.15, 0.03, (h, w))).astype(np.float32),
        7: np.where(xx >= 64, 30.0, 4.0).astype(np.float32) + rng.normal(0, 0.5, (h, w)).astype(np.float32),
        12: scarp_step + rng.normal(0, 0.3, (h, w)).astype(np.float32),
        16: np.where((yy >= 64) & (xx >= 64), 2500.0, 300.0).astype(np.float32),
        19: (np.abs(np.gradient(scarp_step)[0]) + np.abs(np.gradient(scarp_step)[1]) + 2.0).astype(np.float32),
    }
    # Inject -3.4e38 float32 sentinel inside footprint to test sentinel scrubbing
    bands[3][20, 20] = np.float32(-3.4028235e38)
    bands[4][21, 21] = np.float32(-3.4028235e38)
    return foot, cat, h19, r0, bands


def test_integer_quotas_exact_sum_and_caps():
    w = np.array([1.0, 2.0, 3.0, 4.0])
    caps = np.array([2, 3, 10, 10])
    q = concentration._integer_quotas(w, total=12, caps=caps)
    assert int(q.sum()) == 12
    assert np.all(q <= caps)
    with pytest.raises(ValueError):
        concentration._integer_quotas(w, total=30, caps=caps)


def test_corroborated_ridge_scrubs_sentinels_and_respects_footprint():
    foot, _cat, _h19, _r0, bands = _synthetic_concentration_scene()
    corrob, diag = concentration.corroborated_ridge_response(bands, foot)
    assert corrob.dtype == np.float32
    assert np.isfinite(corrob).all()
    assert np.all(corrob[~foot] == 0.0)
    assert np.all((corrob[foot] >= 0.0) & (corrob[foot] <= 1.0))
    assert diag["p99_in_footprint"] > diag["mean_in_footprint"] > 0.0


def test_interaction_and_geodetic_priors_rank_active_blocks():
    foot, cat, _h19, _r0, bands = _synthetic_concentration_scene()
    int_score, int_diag = concentration.interaction_block_prior(cat, foot, block_px=32, stepover_radius_px=8)
    geod_score, geod_diag = concentration.geodetic_block_prior(bands, foot, block_px=32)

    assert len(int_score) == 16 == len(geod_score)
    assert int_diag["catalogue_tips_px"] >= 4
    assert int_diag["catalogue_junctions_px"] >= 2
    assert int_diag["stepover_zone_px"] > 0
    assert geod_diag["uses_catalogue"] is False

    # Bottom-right block (row 2..3, col 2..3 -> indices 10, 11, 14, 15) must beat top-left index 5 (row 1, col 1)
    assert int_score[10] > int_score[5]
    assert geod_score[15] > geod_score[0]


@pytest.mark.parametrize("prior_kind,frac", [("interaction", 0.10), ("interaction", 0.20), ("geodetic", 0.15)])
def test_concentration_build_invariants(prior_kind, frac):
    foot, cat, h19, r0, bands = _synthetic_concentration_scene()
    corrob, _ = concentration.corroborated_ridge_response(bands, foot)
    if prior_kind == "interaction":
        blk_score, _ = concentration.interaction_block_prior(cat, foot, block_px=32, stepover_radius_px=8)
    else:
        blk_score, _ = concentration.geodetic_block_prior(bands, foot, block_px=32)

    v1, stats = concentration.build(
        parent_dots=r0,
        footprint=foot,
        catalogue_mask=cat,
        blk_score=blk_score,
        corrob_ridge=corrob,
        h19_5_mask=h19,
        fraction=frac,
        block_px=32,
        det_elev=bands[12],
    )
    v2, _ = concentration.build(
        parent_dots=r0,
        footprint=foot,
        catalogue_mask=cat,
        blk_score=blk_score,
        corrob_ridge=corrob,
        h19_5_mask=h19,
        fraction=frac,
        block_px=32,
    )

    # Byte-for-bit deterministic
    assert np.array_equal(v1, v2)
    # Exact dot count preserved
    assert int(v1.sum()) == int(r0.sum()) == stats["n_dots"]
    # Exact requested move count
    expect_move = int(round(frac * int(r0.sum())))
    assert stats["n_moved"] == expect_move == stats["n_added"] == stats["n_removed"]
    # Footprint & zero catalogue mass
    assert not (v1 & (~foot)).any()
    assert not (v1 & cat).any()
    # Collar frozen: inherited <3 px dots untouched; newly added dots >= 3.0 px
    d_cat = distance_transform_edt(~cat)
    assert np.array_equal(v1 & (d_cat < 3.0), r0 & (d_cat < 3.0))
    added = v1 & (~r0)
    assert added.any()
    assert float(d_cat[added].min()) >= 3.0 - 1e-6
    # Inter-dot separation >= 2.8 px on newly placed dots
    assert stats["added_min_interdot_sep_px"] >= 2.8 - 1e-5
    # Source blocks lost dots, target blocks gained dots
    assert stats["source_dots_before"] - stats["source_dots_after"] == expect_move
    assert stats["target_dots_after"] - stats["target_dots_before"] == expect_move
