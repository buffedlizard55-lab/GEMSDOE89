"""Unit tests for Parent R0 recipe operators, SPACING variants, and SGMC control."""

import numpy as np
import pytest
from scipy.ndimage import distance_transform_edt

from gemsdoe import parent, proxy, spacing


def _synthetic_ridge_scene(shape=(140, 140)):
    foot = np.zeros(shape, dtype=bool)
    foot[8:-8, 8:-8] = True
    cat = np.zeros(shape, dtype=bool)
    cat[15:25, 15] = True

    h19 = np.zeros(shape, dtype=bool)
    # Three long fault strands (each >= 25 px -> >= 7 dots after dot_thin(2.8))
    h19[35, 25:60] = True
    for k in range(32):
        h19[55 + k, 30 + k] = True
    # Branched Y-splay strand
    h19[100, 25:55] = True
    for k in range(15):
        h19[100 - k, 55 + k] = True
        h19[100 + min(k, 12), 55 + k] = True
    # Plus isolated short fragments (< 6 dots, should stay frozen)
    h19[25, 95:100] = True
    h19[50, 105] = True
    # And one dot near catalogue (2 < d_cat < 3 -> inherited collar dot, frozen)
    h19[20, 18] = True  # d_cat == 3? Wait: (20, 17) + (21, 17):
    h19[20, 17] = False
    h19[21, 17] = True  # distance sqrt((21-21)^2 + (17-15)^2) = 2.0 -> pruned!
    # At (20, 18) distance is 3.0; put one at distance sqrt(5)=2.236 from tip (24,15) -> (26,16)
    h19[26, 16] = True

    r0, d28 = parent.rebuild_r0_mask(h19, foot, cat, r_min=2.8, collar_px=2.0)
    return foot, cat, h19, r0, d28


def test_dot_thin_enforces_euclidean_radius():
    foot, cat, h19, r0, d28 = _synthetic_ridge_scene()
    pts = np.argwhere(d28)
    assert len(pts) > 20
    diff = pts[:, None, :] - pts[None, :, :]
    dist = np.hypot(diff[..., 0], diff[..., 1])
    np.fill_diagonal(dist, 99.0)
    assert dist.min() > 2.8, f"min separation {dist.min()} <= 2.8"

    d_cat = distance_transform_edt(~cat)
    assert not (r0 & (d_cat <= 2.0)).any()
    assert (r0 & (d_cat < 3.0)).sum() >= 1  # inherited sqrt(5) dot preserved in R0


@pytest.mark.parametrize("mode", ["alongstrike", "poisson", "lattice"])
def test_spacing_invariants_and_collar(mode):
    foot, cat, h19, r0, _ = _synthetic_ridge_scene()
    det_elev = np.linspace(-100.0, 100.0, foot.size, dtype=np.float32).reshape(foot.shape)

    v1, stats = spacing.build(
        mode=mode,
        parent_dots=r0,
        h19_5_mask=h19,
        footprint=foot,
        catalogue_mask=cat,
        seed=20261023,
        min_component_dots=6,
        det_elev=det_elev,
    )
    v2, _ = spacing.build(
        mode=mode,
        parent_dots=r0,
        h19_5_mask=h19,
        footprint=foot,
        catalogue_mask=cat,
        seed=20261023,
        min_component_dots=6,
    )
    # Deterministic
    assert np.array_equal(v1, v2)
    # Exact count preserved
    assert int(v1.sum()) == int(r0.sum()) == stats["n_dots"]
    # Inside footprint, zero catalogue mass
    assert not (v1 & (~foot)).any()
    assert not (v1 & cat).any()
    # Inherited <3 px collar dots untouched, newly added dots >= 3.0 px
    d_cat = distance_transform_edt(~cat)
    inherited_close = r0 & (d_cat < 3.0)
    assert np.array_equal(v1 & (d_cat < 3.0), inherited_close)
    added = v1 & (~r0)
    assert added.any()
    assert float(d_cat[added].min()) >= 3.0 - 1e-6


def test_alongstrike_improves_ridge_kernel_coverage():
    foot, cat, h19, r0, _ = _synthetic_ridge_scene()
    v, stats = spacing.build(
        mode="alongstrike",
        parent_dots=r0,
        h19_5_mask=h19,
        footprint=foot,
        catalogue_mask=cat,
        seed=20261023,
        min_component_dots=6,
    )
    assert (v & (~h19)).sum() == 0, "alongstrike must stay strictly on H19-5 ridges"
    assert stats["active_ridge_kernel_cov_after"] >= stats["active_ridge_kernel_cov_before"]


def test_sgmc_control_excludes_catalogue_collar():
    foot, cat, h19, r0, _ = _synthetic_ridge_scene()
    sgmc = np.zeros_like(foot)
    sgmc[35, 30:50] = True   # off-catalogue SGMC trace overlapping strand 1
    sgmc[18, 15] = True      # on-catalogue pixel -> must be excluded
    res = proxy.sgmc_off_catalogue_control(r0, foot, cat, sgmc, collar_px=3.0)
    assert res["evidence_class"] == "PROXY"
    assert res["sgmc_off_catalogue_truth_px"] == 20
    assert res["sgmc_coverage"] > 0.5
    assert 0.0 < res["sgmc_raw_dti"] <= 1.0
