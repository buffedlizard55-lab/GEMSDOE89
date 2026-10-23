"""Unit tests for the SPACING axis and SGMC report-only control."""

import numpy as np
import pytest
from scipy import ndimage as ndi

from gemsdoe import proxy, spacing


@pytest.fixture()
def synthetic_ridge_scene():
    """Synthetic 3-px-wide linear fault corridors with flank-crowded parent dots."""
    shape = (120, 120)
    footprint = np.zeros(shape, dtype=bool)
    footprint[6:-6, 6:-6] = True

    catalogue = np.zeros(shape, dtype=bool)
    catalogue[12, 12:35] = True  # known fault trace at top-left

    ridge = np.zeros(shape, dtype=bool)
    # Corridor A: N-S linear 3-px-wide corridor (crest at x=50, flanks at 49, 51)
    ridge[20:100, 49:52] = True
    # Corridor B: E-W linear 3-px-wide corridor (crest at y=85, flanks at 84, 86)
    ridge[84:87, 65:108] = True
    # Near-catalogue segment (within 2.5 px of catalogue -> inherited collar lock)
    ridge[14, 15:30] = True

    parent = np.zeros(shape, dtype=bool)
    # Place flank-dominated parent dots on Corridor A (alternating shoulders 49 & 51)
    for y in range(22, 98, 4):
        parent[y, 49] = True
        parent[y + 1, 51] = True
    # Place flank-dominated parent dots on Corridor B
    for x in range(67, 106, 4):
        parent[84, x] = True
        parent[86, x + 1] = True
    # Inherited diagonal-collar dot at sqrt(5)=2.236 px from catalogue[12, 20]
    parent[14, 21] = True

    return ridge, parent, catalogue, footprint


def test_spacing_modes_preserve_exact_count_and_support(synthetic_ridge_scene):
    ridge, parent, catalogue, footprint = synthetic_ridge_scene
    ctx = spacing.prepare_manifold(
        ridge, parent, catalogue, footprint,
        target_clear_dots=100, min_corridor_dots=4,
    )
    d_cat = ndi.distance_transform_edt(~catalogue)

    outputs = {}
    for mode in ("strike", "poisson", "lattice"):
        v, stats = spacing.build(mode, ctx, parent, footprint, np.random.default_rng(42))
        outputs[mode] = (v, stats)
        assert int(v.sum()) == int(parent.sum())
        # 100% of dots remain on the ridge support and inside footprint
        assert not (v & ~ridge).any()
        assert not (v & ~footprint).any()
        # Zero catalogue mass and >= 3 px clearance on all added dots
        assert not (v & catalogue).any()
        added = v & ~parent
        if added.any():
            assert float(d_cat[added].min()) >= 3.0 - 1e-6
        # Inherited d_cat < 3.0 collar dot is preserved untouched
        assert bool(v[14, 21]) is True
        assert 1.0 <= stats["pct_changed"] <= 100.0

    # All three modes are deterministic and distinct
    v_again, _ = spacing.build("strike", ctx, parent, footprint, np.random.default_rng(42))
    assert np.array_equal(outputs["strike"][0], v_again)
    assert not np.array_equal(outputs["strike"][0], outputs["poisson"][0])
    assert not np.array_equal(outputs["strike"][0], outputs["lattice"][0])


def test_strike_increases_crest_credit_over_flank_crowded_parent(synthetic_ridge_scene):
    ridge, parent, catalogue, footprint = synthetic_ridge_scene
    ctx = spacing.prepare_manifold(
        ridge, parent, catalogue, footprint,
        target_clear_dots=100, min_corridor_dots=4,
    )
    _, stats_strike = spacing.build("strike", ctx, parent, footprint, np.random.default_rng(7))
    assert stats_strike["crest_dots_after"] > stats_strike["crest_dots_before"]
    assert stats_strike["t_crest_after"] > stats_strike["t_crest_before"]
    assert stats_strike["across_strike_twins_after"] < stats_strike["across_strike_twins_before"]


def test_sgmc_off_catalogue_excludes_collar():
    shape = (60, 60)
    footprint = np.ones(shape, dtype=bool)
    catalogue = np.zeros(shape, dtype=bool)
    catalogue[10, 10] = True
    sgmc = np.zeros(shape, dtype=bool)
    sgmc[10, 11] = True   # within 1 px of catalogue -> excluded from off-cat control
    sgmc[40, 40] = True   # far from catalogue -> included
    dots = np.zeros(shape, dtype=bool)
    dots[40, 41] = True   # within 3 px of (40, 40)
    res = proxy.sgmc_off_catalogue(dots, sgmc, catalogue, footprint, clearance_px=3.0)
    assert res["n_sgmc_offcat_px"] == 1
    assert res["recall_within_3px"] == pytest.approx(1.0)
    assert res["surrogate_dti_sgmc_offcat"] > 0.5
