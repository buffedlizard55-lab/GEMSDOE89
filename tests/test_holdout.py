import numpy as np
import pytest
from scipy import ndimage as ndi

from gemsdoe import holdout


def test_component_holdout_hides_whole_segment_and_buffer():
    cat = np.zeros((80, 100), dtype=bool)
    cat[20, 10:40] = True
    cat[60, 60:90] = True
    fold_map = np.zeros(cat.shape, dtype=np.int8)
    fold_map[:, 50:] = 1
    tiles = [
        {"y0": 0, "y1": 80, "x0": 0, "x1": 50, "fold": 0},
        {"y0": 0, "y1": 80, "x0": 50, "x1": 100, "fold": 1},
    ]
    _, n, rows = holdout.component_holdouts(cat, fold_map, tiles, n_folds=2, buffer_px=3)
    assert n == 2
    assert rows[0]["hidden"].sum() == 30
    assert rows[1]["hidden"].sum() == 30
    assert rows[0]["visible"].sum() == 30
    assert rows[1]["visible"].sum() == 30


def test_empty_prediction_gets_no_phantom_true_positive_credit():
    truth = np.zeros((20, 20), dtype=bool)
    truth[1, 1] = True
    comp = holdout.metric_components(truth, np.zeros_like(truth))
    assert comp["T"] == 0.0
    assert comp["S"] == 0.0
    assert comp["M"] == 0.0
    assert holdout.dti_from_components([comp]) == 0.0


def test_dti_tile_statistics_match_metric():
    from gemsdoe.metric import dti

    truth = np.zeros((40, 40), dtype=bool)
    truth[10:15, 10] = True
    truth[25:30, 30] = True
    pred = np.zeros_like(truth)
    pred[10:15, 12] = True
    pred[25:30, 32] = True
    comp = holdout.metric_components(truth, pred)
    assert holdout.dti_from_components([comp]) == pytest.approx(dti(truth, pred), abs=1e-12)


def test_pooled_dti_equals_full_noninteracting_tile_composition():
    truth1 = np.zeros((30, 30), dtype=bool)
    pred1 = np.zeros_like(truth1)
    truth1[10:14, 10] = True
    pred1[10:14, 11] = True
    truth2 = np.zeros_like(truth1)
    pred2 = np.zeros_like(truth1)
    truth2[10:14, 10] = True
    pred2[10:14, 12] = True
    rows = [holdout.metric_components(truth1, pred1), holdout.metric_components(truth2, pred2)]
    pooled = holdout.dti_from_components(rows)
    full_truth = np.concatenate([truth1, truth2], axis=1)
    full_pred = np.concatenate([pred1, pred2], axis=1)
    from gemsdoe.metric import dti
    assert pooled == pytest.approx(dti(full_truth, full_pred), abs=1e-12)


def test_peak_selection_is_deterministic_spaced_and_fixed_count():
    yy, xx = np.mgrid[:60, :70]
    score = (-((yy - 20) ** 2 + (xx - 25) ** 2) - .01 * xx).astype(np.float32)
    eligible = np.ones(score.shape, dtype=bool)
    a = holdout.select_spaced_peaks(score, eligible, 30, min_sep_px=2.8)
    b = holdout.select_spaced_peaks(score, eligible, 30, min_sep_px=2.8)
    pts = np.argwhere(a)
    assert a.sum() == 30
    assert np.array_equal(a, b)
    ds = np.sqrt(((pts[:, None, :] - pts[None, :, :]) ** 2).sum(axis=2))
    ds[ds == 0] = np.inf
    assert ds.min() > 2.8


def test_holdout_auc_canary_handles_direction_and_flags_only_over_threshold():
    labels = np.zeros((50, 50), dtype=bool)
    labels[:, 25:] = True
    f = np.indices(labels.shape)[1].astype(float)
    domain = np.ones_like(labels)
    out = holdout.auc_strength(f, labels, domain, n_pos=5000, n_neg=5000)
    inv = holdout.auc_strength(-f, labels, domain, n_pos=5000, n_neg=5000)
    assert out["auc"] == pytest.approx(1.0)
    assert inv["strength"] == pytest.approx(1.0)
    assert out["flag_leakage"] and inv["flag_leakage"]


def test_conductivity_edge_ignores_invalid_support():
    field = np.zeros((60, 60), dtype=np.float32)
    field[:, 30:] = 10
    valid = np.ones_like(field, dtype=bool)
    valid[5:10, 5:10] = False
    field[~valid] = np.nan
    score = holdout.conductivity_edge(field, valid, scales=(1.0, 2.0))
    assert np.isfinite(score[30, 30])
    assert np.isnan(score[7, 7])
    assert score[30, 30] > score[20, 20]


def test_registry_drift_audit_detects_duplicate_geometry(tmp_path):
    import rasterio
    from affine import Affine

    ref = np.zeros((30, 30), dtype=np.float32)
    ref[10, 10] = 1
    path = tmp_path / "reference.tif"
    with rasterio.open(path, "w", driver="GTiff", height=30, width=30,
                       count=1, dtype="float32", crs="EPSG:32611",
                       transform=Affine(100, 0, 0, 0, -100, 3000)) as dst:
        dst.write(ref, 1)
    dots = ref > 0
    audit = holdout.surface_registry_audit(ref, np.ones_like(dots), dots, [path],
                                           sample_n=900, surface_label="test final")
    assert audit["duplicate_stop"]
    assert audit["surface_tested"] == "test final"
    assert audit["max_dot_overlap_3px"] == 1.0
