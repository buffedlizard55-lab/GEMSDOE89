"""Automated end-to-end contracts for Lane H89 (`BH-RTP-HABC`) discovery & primary GeoTIFF."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import tifffile

from gemsdoe import discovery_h89 as h89
from gemsdoe import grid as repo_grid
from gemsdoe import validate as repo_validate

ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_h89_feature_manifest_counts() -> None:
    assert len(h89.PHYS_FEATURE_NAMES) == 30
    assert len(h89.NET_FEATURE_NAMES) == 12
    assert len(h89.ALL_FEATURE_NAMES) == 42
    assert len(set(h89.ALL_FEATURE_NAMES)) == 42


def test_h89_analytical_jensen_self_credit_and_prior_calibration() -> None:
    p = np.zeros((25, 25), dtype=np.float32)
    p[12, 12] = 0.8
    p[12, 13] = 0.8
    p[12, 14] = 0.8
    m_raw = h89.g57_emit.expected_credit(p)
    m_repaired = h89.self_credit_from_posterior(p, mu_strand=2.55)
    assert np.all((m_repaired >= 0.0) & (m_repaired <= 1.0))
    # Analytical Jensen repair strictly removes strand sum-vs-max inflation
    assert float(m_repaired[12, 13]) < float(m_raw[12, 13])
    assert np.isclose(float(m_repaired[12, 13]), float(m_raw[12, 13]) / 2.55, atol=1e-5)

    cal = h89.prior_calibrate_prob(np.array([0.25, 0.50, 0.75]), sample_prior=0.25, target_prior=0.01)
    assert cal.shape == (3,)
    assert np.all((cal > 0.0) & (cal < 1.0))
    assert float(cal[0]) < 0.05 and float(cal[2]) > float(cal[1]) > float(cal[0])


def test_h89_primary_download_tif_range_and_twin_equivalence() -> None:
    rc = json.loads((ROOT / "registry" / "h89_run_card.json").read_text(encoding="utf-8"))
    sub = rc["submission"]

    dl_tif = ROOT / sub["download_path"]
    dl_zip = ROOT / sub["zip_path"]
    rel_zeros = ROOT / sub["release_zeros_path"]
    rel_nan = ROOT / sub["release_zeros_path"].replace("-zeros.tif", ".tif")

    assert dl_tif.exists(), f"missing primary download {dl_tif}"
    assert dl_zip.exists(), f"missing zip {dl_zip}"
    assert rel_zeros.exists(), f"missing release zeros twin {rel_zeros}"
    assert rel_nan.exists(), f"missing release nan twin {rel_nan}"

    assert _sha256(dl_tif) == sub["sha256_tif"]
    assert _sha256(dl_zip) == sub["sha256_zip"]
    assert _sha256(rel_zeros) == sub["sha256_release_zeros"]
    assert _sha256(rel_nan) == sub["sha256_release_nan"]

    # Primary competition upload GeoTIFF checks (prevents DrivenData [0, 1] & nodata errors)
    with tifffile.TiffFile(dl_tif) as tf:
        assert len(tf.pages) == 1
        page = tf.pages[0]
        grid_contract = json.loads((ROOT / "registry" / "grid_contract.json").read_text(encoding="utf-8"))
        assert [page.imagelength, page.imagewidth] == grid_contract["shape"]
        # Lipor reference contract: nodata=None on -zeros upload
        assert "GDAL_NODATA" not in page.tags
        arr_dl = page.asarray()

    assert arr_dl.dtype == np.float32
    assert arr_dl.shape == (3730, 3292)
    assert int(np.isnan(arr_dl).sum()) == 0
    assert int(np.isinf(arr_dl).sum()) == 0
    assert float(arr_dl.min()) >= 0.0
    assert float(arr_dl.max()) <= 1.0
    assert int((arr_dl > 0.0).sum()) == sub["n_dots"] == 37654
    assert hashlib.sha256(np.ascontiguousarray(arr_dl, dtype="<f4").tobytes()).hexdigest() == sub["sha256_decoded_float32"]

    # Exact pixel equivalence with CI release twin
    arr_rel = tifffile.imread(rel_zeros)
    assert np.array_equal(arr_dl, arr_rel)
    ok_gate, gate_res = repo_validate.gate_release(rel_zeros, grid_contract)
    assert ok_gate, f"release gate failed: {gate_res}"

    # Optional full 15/15 rasterio check when rasterio + pinned data cache are installed
    data_dir = ROOT / ".cache" / "data"
    try:
        import rasterio  # noqa: F401
        from vendor.gems57 import grid as g57_grid
        from vendor.gems57 import validate as g57_validate
    except ImportError:
        return

    if (data_dir / "sample_submission.tif").exists() and (data_dir / "existing_faults.tif").exists():
        g = g57_grid.load_grid(data_dir)
        v_rep = g57_validate.validate(dl_tif, footprint=g.footprint, catalogue=g.catalogue)
        assert v_rep["all_checks_passed"] is True
        assert sum(bool(v) for v in v_rep["checks"].values()) == 15


def test_h89_leakage_canary_uniqueness_and_run_card_contracts() -> None:
    canary = json.loads((ROOT / "registry" / "leakage_canary_h89.json").read_text(encoding="utf-8"))
    assert canary["any_flagged"] is False
    assert len(canary["features"]) == 42
    assert canary["max_single_feature_strength"] <= 0.90

    rep = json.loads((ROOT / "registry" / "h89_discovery_report.json").read_text(encoding="utf-8"))
    rc = json.loads((ROOT / "registry" / "h89_run_card.json").read_text(encoding="utf-8"))

    assert rc["verdict"] == "promote"
    assert rc["evidence_class"] == "HOLDOUT-DTI"
    assert rc["evaluator_version"] == "gems57-pooled-hide-v2"
    assert rc["withheld_positive_pixels"] == 11321
    assert len(rc["submission"]["form_note"]) <= 140
    assert rc["submission"]["form_note_chars"] == len(rc["submission"]["form_note"])

    # Holdout lift across all 4 spatially blocked quadrants
    hd = rc["holdout_dti"]
    assert hd["candidate"] > hd["r0_fold_fair_control"]
    assert hd["paired_delta_vs_r0_fold_fair"] > 0.04
    assert hd["paired_delta_ci95"][0] > 0.0

    for q in ("NW", "NE", "SW", "SE"):
        assert rep["fold_breakdown"]["E89_2_dual_global_celf"][q]["dti"] > rep["fold_breakdown"]["r0_fold_fair"][q]["dti"]

    # Registry uniqueness thresholds
    reg_corr = rc["registry_uniqueness"]
    assert reg_corr["passed"] is True
    assert reg_corr["unique_reference_rasters_checked"] >= 80
    assert reg_corr["max_abs_surface_spearman"] <= 0.90
    assert reg_corr["max_abs_emitted_spearman"] <= 0.90
    assert reg_corr["max_dot_overlap_3px"] <= 0.70


def test_github_pages_and_readme_links_and_receipts() -> None:
    import html
    import re

    rc = json.loads((ROOT / "registry" / "h89_run_card.json").read_text(encoding="utf-8"))
    sub = rc["submission"]

    assert (ROOT / ".nojekyll").exists()
    assert (ROOT / "docs" / ".nojekyll").exists()

    html_pages = [
        ROOT / "index.html",
        ROOT / "executive-summary.html",
        ROOT / "docs" / "index.html",
        ROOT / "docs" / "executive-summary.html",
    ]
    attr_re = re.compile(r'(?:href|src)=["\']([^"\']+)["\']')

    for page_path in html_pages:
        assert page_path.exists(), f"missing page {page_path}"
        txt = page_path.read_text(encoding="utf-8")
        assert sub["name"] in txt
        assert html.escape(sub["form_note"]) in txt
        assert sub["sha256_tif"] in txt
        assert "15 / 15" in txt or "15/15" in txt

        for ref in attr_re.findall(txt):
            if ref.startswith(("http://", "https://", "#", "mailto:", "javascript:")):
                continue
            clean_ref = ref.split("#", 1)[0].split("?", 1)[0]
            if not clean_ref:
                continue
            target = (page_path.parent / clean_ref).resolve()
            assert target.exists(), f"broken relative link '{ref}' in {page_path} -> {target}"

    readme_txt = (ROOT / "README.md").read_text(encoding="utf-8")
    assert sub["name"] in readme_txt
    assert sub["form_note"] in readme_txt
    assert sub["sha256_tif"] in readme_txt
    for md_ref in re.findall(r"\]\(([^)]+)\)", readme_txt):
        if md_ref.startswith(("http://", "https://", "#")):
            continue
        clean_md = md_ref.split("#", 1)[0]
        if clean_md:
            assert (ROOT / clean_md).exists(), f"broken README link '{md_ref}'"


