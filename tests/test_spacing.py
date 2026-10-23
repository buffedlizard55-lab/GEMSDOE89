"""Synthetic controls for the matched SPACING construction (no competition data)."""

import numpy as np
import pytest

from gemsdoe import spacing


@pytest.fixture(scope="module")
def synthetic_control():
    shape = (160, 160)
    footprint = np.zeros(shape, dtype=bool)
    footprint[4:-4, 4:-4] = True
    catalogue = np.zeros(shape, dtype=bool)
    catalogue[10:-10, 30] = True
    catalogue[80, 10:25] = True
    parent = np.zeros(shape, dtype=bool)
    for y in range(8, 152, 4):
        for x in range(8, 152, 4):
            if footprint[y, x] and not catalogue[y, x]:
                parent[y, x] = True
    control = spacing.prepare_control(parent, footprint, catalogue, fraction=0.10, seed=42)
    return control


def test_all_arms_share_controls_and_pass_parent_diff_invariants(synthetic_control):
    control = synthetic_control
    n_parent = int(control["parent_dots"].sum())
    n_move = len(control["removed_pts"])
    assert n_move == round(0.10 * n_parent)

    for pattern in spacing.PATTERNS:
        variant, stats = spacing.build_from_control(control, pattern)
        assert int(variant.sum()) == n_parent
        assert int((variant & ~control["parent_dots"]).sum()) == n_move
        assert int((control["parent_dots"] & ~variant).sum()) == n_move
        assert stats["pct_changed"] == pytest.approx(100.0 * n_move / n_parent)
        assert stats["removed_sha256"] == control["removed_sha256"]
        assert stats["anchors_sha256"] == control["anchors_sha256"]
        assert stats["control_block_counts_preserved"]
        assert stats["catalogue_mass"] == 0
        assert stats["added_min_catalogue_clearance_px"] >= 3.0
        assert stats["added_min_nearest_dot_px"] >= 2.8 - 1e-6
        assert not (variant & ~control["footprint"]).any()


def test_control_and_every_pattern_are_seed_deterministic(synthetic_control):
    first = synthetic_control
    second = spacing.prepare_control(
        first["parent_dots"], first["footprint"], first["catalogue_mask"],
        fraction=0.10, seed=42,
    )
    assert np.array_equal(first["removed_pts"], second["removed_pts"])
    assert np.array_equal(first["anchors"], second["anchors"])
    assert first["removed_sha256"] == second["removed_sha256"]
    assert first["anchors_sha256"] == second["anchors_sha256"]
    for pattern in spacing.PATTERNS:
        a, stats_a = spacing.build_from_control(first, pattern)
        b, stats_b = spacing.build_from_control(second, pattern)
        assert np.array_equal(a, b)
        assert stats_a == stats_b


def test_poisson_arm_uses_the_shared_anchors_exactly(synthetic_control):
    variant, stats = spacing.build_from_control(synthetic_control, "poisson")
    added = variant & ~synthetic_control["parent_dots"]
    expected = np.zeros_like(variant)
    anchors = synthetic_control["anchors"]
    expected[anchors[:, 0], anchors[:, 1]] = True
    assert np.array_equal(added, expected)
    assert stats["anchor_exact_matches"] == len(anchors)
    assert stats["mean_anchor_shift_px"] == 0.0


def test_rejects_too_small_an_edit(synthetic_control):
    with pytest.raises(ValueError, match="1-50%"):
        spacing.prepare_control(
            synthetic_control["parent_dots"], synthetic_control["footprint"],
            synthetic_control["catalogue_mask"], fraction=0.001, seed=42,
        )


def test_rejects_parent_with_catalogue_mass(synthetic_control):
    parent = synthetic_control["parent_dots"].copy()
    parent[20, 30] = True
    with pytest.raises(ValueError, match="catalogue mass"):
        spacing.prepare_control(
            parent, synthetic_control["footprint"], synthetic_control["catalogue_mask"],
            fraction=0.10, seed=42,
        )
