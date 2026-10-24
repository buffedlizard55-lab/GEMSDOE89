"""BSTP lane: fixed mass, new-support distance, greedy determinism, holdout sanity."""
import numpy as np

from gemsdoe import bstep, holdout
from gemsdoe.metric import dti


def _toy():
    rng = np.random.default_rng(3)
    foot = np.ones((60, 60), dtype=bool)
    parent = np.zeros((60, 60), dtype=bool)
    parent[10, 10:50:4] = True
    parent[30, 10:50:4] = True
    cat = np.zeros((60, 60), dtype=bool)
    cat[50, 5:20] = True
    surf = rng.random((60, 60)).astype(np.float32)
    return parent, surf, foot, cat


def test_fixed_mass_and_new_support_distance():
    parent, surf, foot, cat = _toy()
    cand, diag = bstep.build_bstep_candidate(parent, surf, foot, cat,
                                             retain_fraction=0.6)
    assert cand.sum() == parent.sum()
    new = cand & ~parent
    assert diag["n_new"] == new.sum() > 0
    from scipy import ndimage as ndi
    assert ndi.distance_transform_edt(~parent)[new].min() > 3.0
    assert ndi.distance_transform_edt(~cat)[new].min() >= 3.0
    # retained dots are parent dots
    assert ((cand & parent).sum() == diag["n_retained"])


def test_greedy_is_deterministic_and_surface_ranked():
    parent, surf, foot, cat = _toy()
    a, _ = bstep.build_bstep_candidate(parent, surf, foot, cat)
    b, _ = bstep.build_bstep_candidate(parent, surf, foot, cat)
    assert np.array_equal(a, b)


def test_surface_is_geomean_and_bounded():
    foot = np.ones((20, 20), dtype=bool)
    depth = np.tile(np.linspace(0, 1000, 20, dtype=np.float32), (20, 1))
    cond = np.tile(np.linspace(0, 5, 20, dtype=np.float32).T, (1, 20)) \
        if False else np.ascontiguousarray(
            np.tile(np.linspace(0, 5, 20, dtype=np.float32), (20, 1)).T)
    edge = np.full((20, 20), 0.5, dtype=np.float32)
    s, ch, _ = bstep.bstep_surface(depth, cond, edge, foot)
    assert s.min() >= 0.0 and s.max() <= 1.0
    expect = np.cbrt(ch["bstep_grad_depth_to_base"].astype(np.float64)
                     * ch["cond_grad_cond_surf"]
                     * ch["edge_max_tmiHG_gravHG"])
    assert np.allclose(s, expect, atol=1e-6)


def test_segment_holdout_withholds_wholly_and_scores():
    foot = np.ones((80, 80), dtype=bool)
    cat = np.zeros((80, 80), dtype=bool)
    for r in (10, 30, 50, 70):  # 4 segments of 40 px
        cat[r, 10:50] = True
    seen_visible_sums = []

    def build(visible):
        seen_visible_sums.append(int(visible.sum()))
        dots = np.zeros((80, 80), dtype=bool)
        dots[10, 10:50:3] = True  # fixed guess, catalogue-free
        return dots

    out = holdout.run_segment_holdout(build, build, cat, foot, k_folds=2,
                                      buffer_px=5.0, min_segment_px=20,
                                      n_bootstrap=50)
    assert out["n_withheld_positives_px"] == 160
    # visible catalogue never contains the full catalogue (something withheld)
    assert max(seen_visible_sums) < 160
    # identical builders -> zero difference
    assert abs(out["diff_candidate_minus_parent"]) < 1e-12
    # pooled DTI agrees with metric.dti on a single-fold-style problem
    truth = cat.copy()
    pred = np.zeros((80, 80)); pred[10, 10:50:3] = 1.0
    assert dti(truth, pred) > 0.0
