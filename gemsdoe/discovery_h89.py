"""Lane H89 (`BH-RTP-HABC`): Cover-Deconfounded Basement-Hinge, RTP Phase-Symmetry
& Hydrothermal Alteration Boundary Conduit Discovery.

Implements the pre-registered `docs/preregistration-h89.md` pipeline on the
pinned 19-band competition stack (`training_features.tif`, `existing_faults.tif`,
`sample_submission.tif`) while reusing the shared `vendor/gems57` evaluator,
Dinkelbach CELF submodular allocator, uniqueness gate, and fail-closed writer.

Memory budget: streams `training_features.tif` one band at a time and caches the
30 zero-catalogue physical features in a disk-backed float32 memmap (`~620 MB`)
so peak resident RAM stays `< 1.5 GiB` on 3.8 GiB builders.
"""
from __future__ import annotations

import gc
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import tifffile
from scipy.ndimage import (
    convolve,
    distance_transform_edt,
    gaussian_filter,
    label,
)
from scipy.spatial import cKDTree

from vendor.gems57 import emit as g57_emit
from vendor.gems57 import metric as g57_metric

SENTINEL_FLOOR = -1.0e30

PHYS_FEATURE_NAMES: Tuple[str, ...] = (
    # Family I: Buried Pre-Cenozoic Basement-Scarp Hinge & Gravity Tilt (9)
    "f01_log_cover_depth",
    "f02_basement_grad_150m",
    "f03_basement_grad_350m",
    "f04_basement_hinge_inflection",
    "f05_basement_ridge_aniso",
    "f06_verduzco_grav_tilt_zero",
    "f07_grav_abs_b18_corr",
    "f08_grav_slope_b05",
    "f09_grav_vg_abs_b11",
    # Family II: RTP Magnetic Phase-Symmetry & Gallardo-Meju Cross-Gradient (7)
    "f10_rtp_hg_120m",
    "f11_rtp_hg_300m",
    "f12_rtp_tilt_zero",
    "f13_tmi_verduzco_tilt_zero",
    "f14_mag_tc_b06",
    "f15_gallardo_meju_rtp_grav_parallel",
    "f16_flightline_seam_clean_rtp",
    # Family III: Hydrothermal Clay-Cap Conduit, Demag & Transtensional Strain (8)
    "f17_cond_surf_b17",
    "f18_cond_lateral_grad",
    "f19_hydrothermal_demag_conduit",
    "f20_transtensional_releasing_index",
    "f21_geod_strain_2ndinv_b04",
    "f22_geod_dilaterate_b08",
    "f23_seismic_proximity_log_b10",
    "f24_seismic_intensity_log_b16",
    # Family IV: Cover-Deconfounded Piedmont Flexure & Scarp Concavity (6)
    "f25_piedmont_toe_concavity",
    "f26_scarp_crest_convexity",
    "f27_strike_coherence_600m",
    "f28_lrm_elev_500m",
    "f29_cover_deconfounded_slope",
    "f30_cover_deconfounded_rtp_grav",
)

NET_FEATURE_NAMES: Tuple[str, ...] = (
    "f31_tip_beam_short_1p2km",
    "f32_tip_beam_long_3p0km",
    "f33_wingcrack_horsetail_lobe",
    "f34_relay_breach_bridge",
    "f35_aniso_axial_corridor_2km",
    "f36_aniso_axial_corridor_4p5km",
    "f37_dist_vis_clamped_log",
    "f38_district_fault_density_5km",
    "f39_district_tip_junc_density_10km",
    "f40_phys_x_tip_corrob",
    "f41_phys_x_relay_corrob",
    "f42_strike_alignment_cos2",
)

ALL_FEATURE_NAMES: Tuple[str, ...] = PHYS_FEATURE_NAMES + NET_FEATURE_NAMES


def read_clean_band(features_path: Path, band_1based: int, footprint: np.ndarray) -> np.ndarray:
    """Read 1-based band as float32 and fill sentinels smoothly via nearest valid cell."""
    import rasterio

    with rasterio.open(features_path) as src:
        raw = src.read(int(band_1based)).astype(np.float32)
    valid = np.isfinite(raw) & (raw > SENTINEL_FLOOR) & footprint
    if not valid.any():
        raise ValueError(f"Band {band_1based} has zero valid pixels inside footprint")
    if valid.all():
        return raw
    idx = distance_transform_edt(~valid, return_distances=False, return_indices=True)
    filled = raw[idx[0], idx[1]].astype(np.float32, copy=False)
    return filled


def _grad_xy(arr: np.ndarray, sigma: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Gaussian first derivatives (gy, gx) and gradient magnitude."""
    gy = gaussian_filter(arr, sigma=sigma, order=(1, 0), mode="nearest").astype(np.float32)
    gx = gaussian_filter(arr, sigma=sigma, order=(0, 1), mode="nearest").astype(np.float32)
    mag = np.hypot(gy, gx).astype(np.float32)
    return gy, gx, mag


def _hessian_ridge_aniso(arr: np.ndarray, sigma: float, sign: float = 1.0) -> np.ndarray:
    """Elongated 1D ridge/valley response: max(0, sign*lambda_perp - 0.5*|lambda_par|)."""
    hyy = gaussian_filter(arr, sigma=sigma, order=(2, 0), mode="nearest").astype(np.float32)
    hxx = gaussian_filter(arr, sigma=sigma, order=(0, 2), mode="nearest").astype(np.float32)
    hyx = gaussian_filter(arr, sigma=sigma, order=(1, 1), mode="nearest").astype(np.float32)
    tr = 0.5 * (hyy + hxx)
    rad = np.hypot(0.5 * (hyy - hxx), hyx)
    l1 = tr + rad
    l2 = tr - rad
    if sign >= 0:
        # Concave-up break-in-slope (positive maximum principal curvature, small along-strike curvature)
        perp = l1
        par = l2
        resp = np.maximum(0.0, perp - 0.5 * np.abs(par))
    else:
        # Convex-up crest (negative minimum principal curvature)
        perp = -l2
        par = l1
        resp = np.maximum(0.0, perp - 0.5 * np.abs(par))
    return resp.astype(np.float32)


def _robust_z_fp(vec: np.ndarray) -> np.ndarray:
    med = float(np.median(vec))
    iqr = float(np.quantile(vec, 0.75) - np.quantile(vec, 0.25))
    scale = max(iqr / 1.349, 1e-6)
    return ((vec - med) / scale).astype(np.float32)


def _robust_unit_fp(vec: np.ndarray, q_lo: float = 0.05, q_hi: float = 0.98) -> np.ndarray:
    lo = float(np.quantile(vec, q_lo))
    hi = float(np.quantile(vec, q_hi))
    if hi <= lo + 1e-12:
        return np.zeros_like(vec, dtype=np.float32)
    return np.clip((vec - lo) / (hi - lo), 0.0, 1.0).astype(np.float32)


def _cover_decile_rank(values_fp: np.ndarray, cover_fp: np.ndarray, n_bins: int = 10) -> np.ndarray:
    """Empirical percentile rank [0, 1] of `values_fp` stratified within cover-depth deciles."""
    edges = np.quantile(cover_fp, np.linspace(0.0, 1.0, n_bins + 1))
    edges[0] -= 1.0
    edges[-1] += 1.0
    out = np.empty(values_fp.shape, dtype=np.float32)
    bins = np.digitize(cover_fp, edges[1:-1], right=False)
    for b in range(n_bins):
        m = bins == b
        n_m = int(m.sum())
        if n_m <= 1:
            out[m] = 0.5
            continue
        sub = values_fp[m]
        order = np.argsort(sub, kind="mergesort")
        ranks = np.empty(n_m, dtype=np.float32)
        ranks[order] = np.linspace(0.0, 1.0, n_m, dtype=np.float32)
        out[m] = ranks
    return out


def build_or_load_physical_stack(
    features_path: Path,
    footprint: np.ndarray,
    cache_dir: Path,
) -> Dict[str, np.ndarray]:
    """Compute (or load cached) 30 zero-catalogue multi-physics features on footprint."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    n_fp = int(footprint.sum())
    n_phys = len(PHYS_FEATURE_NAMES)
    mm_path = cache_dir / "phys30_fp.f32"
    meta_path = cache_dir / "phys30_meta.json"
    cover_path = cache_dir / "cover_depth_fp.npy"
    ridge_path = cache_dir / "phys_ridge_2d.npy"
    c2_path = cache_dir / "phys_orient_c2_2d.npy"
    s2_path = cache_dir / "phys_orient_s2_2d.npy"

    if (
        mm_path.is_file()
        and meta_path.is_file()
        and cover_path.is_file()
        and ridge_path.is_file()
        and c2_path.is_file()
        and s2_path.is_file()
        and mm_path.stat().st_size == n_fp * n_phys * 4
    ):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("feature_names") == list(PHYS_FEATURE_NAMES) and meta.get("n_fp") == n_fp:
            mm = np.memmap(mm_path, dtype=np.float32, mode="r", shape=(n_fp, n_phys))
            return {
                "phys_mm": mm,
                "cover_fp": np.load(cover_path),
                "phys_ridge_2d": np.load(ridge_path),
                "phys_c2_2d": np.load(c2_path),
                "phys_s2_2d": np.load(s2_path),
            }

    fp = np.asarray(footprint, dtype=bool)
    H, W = fp.shape
    mm = np.memmap(mm_path, dtype=np.float32, mode="w+", shape=(n_fp, n_phys))

    # --- Family I: Basement Hinge & Gravity Tilt ---
    z_base = np.maximum(read_clean_band(features_path, 15, fp), 0.0)
    cover_fp = z_base[fp].astype(np.float32, copy=True)
    np.save(cover_path, cover_fp)

    mm[:, 0] = np.log10(np.maximum(cover_fp, 1.0)).astype(np.float32)
    _, _, g_zb_15 = _grad_xy(z_base, 1.5)
    mm[:, 1] = g_zb_15[fp]
    del g_zb_15
    _, _, g_zb_35 = _grad_xy(z_base, 3.5)
    mm[:, 2] = g_zb_35[fp]
    del g_zb_35

    _, _, g_zb_20 = _grad_xy(z_base, 2.0)
    lap_zb = (
        gaussian_filter(z_base, sigma=2.0, order=(2, 0), mode="nearest")
        + gaussian_filter(z_base, sigma=2.0, order=(0, 2), mode="nearest")
    ).astype(np.float32)
    iqr_lap = float(np.quantile(np.abs(lap_zb[fp]), 0.75)) + 1e-5
    hinge_2d = (g_zb_20 * np.exp(-np.abs(lap_zb) / iqr_lap)).astype(np.float32)
    mm[:, 3] = hinge_2d[fp]
    del g_zb_20, lap_zb

    base_aniso_2d = np.maximum(
        _hessian_ridge_aniso(z_base, 2.5, sign=1.0),
        _hessian_ridge_aniso(z_base, 2.5, sign=-1.0),
    )
    mm[:, 4] = base_aniso_2d[fp]
    del z_base, base_aniso_2d
    gc.collect()

    b05_grav_slope = np.maximum(read_clean_band(features_path, 5, fp), 0.0)
    b11_grav_vg = np.abs(read_clean_band(features_path, 11, fp))
    cg = float(np.median(b05_grav_slope[fp]) / (np.median(b11_grav_vg[fp]) + 1e-6))
    grav_tilt_zero = (b05_grav_slope / np.sqrt(b05_grav_slope ** 2 + (cg * b11_grav_vg) ** 2 + 1e-10)).astype(np.float32)
    mm[:, 5] = grav_tilt_zero[fp]
    mm[:, 7] = b05_grav_slope[fp]
    mm[:, 8] = b11_grav_vg[fp]
    del b11_grav_vg, grav_tilt_zero

    b18_abs = np.abs(read_clean_band(features_path, 18, fp))
    mm[:, 6] = b18_abs[fp]
    del b18_abs
    gc.collect()

    # --- Family II: RTP Magnetic Phase-Symmetry & Gallardo-Meju Cross-Gradient ---
    b02_rtp = read_clean_band(features_path, 2, fp)
    rtp_gy, rtp_gx, rtp_hg_12 = _grad_xy(b02_rtp, 1.2)
    mm[:, 9] = rtp_hg_12[fp]
    _, _, rtp_hg_30 = _grad_xy(b02_rtp, 3.0)
    mm[:, 10] = rtp_hg_30[fp]
    del rtp_hg_30

    _, _, rtp_hg_15 = _grad_xy(b02_rtp, 1.5)
    rtp_lap = np.abs(
        gaussian_filter(b02_rtp, sigma=1.5, order=(2, 0), mode="nearest")
        + gaussian_filter(b02_rtp, sigma=1.5, order=(0, 2), mode="nearest")
    ).astype(np.float32)
    cs_rtp = float(np.median(rtp_hg_15[fp]) / (np.median(rtp_lap[fp]) + 1e-6))
    rtp_tilt_2d = (rtp_hg_15 / np.sqrt(rtp_hg_15 ** 2 + (cs_rtp * rtp_lap) ** 2 + 1e-10)).astype(np.float32)
    mm[:, 11] = rtp_tilt_2d[fp]
    del rtp_hg_15, rtp_lap, rtp_tilt_2d

    b03_tmi_hg = np.maximum(read_clean_band(features_path, 3, fp), 0.0)
    b09_tmi_vg = np.abs(read_clean_band(features_path, 9, fp))
    cm = float(np.median(b03_tmi_hg[fp]) / (np.median(b09_tmi_vg[fp]) + 1e-6))
    mm[:, 12] = (b03_tmi_hg[fp] / np.sqrt(b03_tmi_hg[fp] ** 2 + (cm * b09_tmi_vg[fp]) ** 2 + 1e-10)).astype(np.float32)
    del b03_tmi_hg, b09_tmi_vg

    b06_tc = read_clean_band(features_path, 6, fp)
    mm[:, 13] = b06_tc[fp]
    del b06_tc

    b13_grav = read_clean_band(features_path, 13, fp)
    grav_gy, grav_gx, grav_hg = _grad_xy(b13_grav, 2.0)
    dot_rg = rtp_gy * grav_gy + rtp_gx * grav_gx
    cos2_rg = (dot_rg ** 2) / ((rtp_hg_12 ** 2 + 1e-8) * (grav_hg ** 2 + 1e-8))
    gm_par_fp = (
        np.sqrt(_robust_unit_fp(rtp_hg_12[fp]) * _robust_unit_fp(grav_hg[fp]))
        * cos2_rg[fp]
    ).astype(np.float32)
    mm[:, 14] = gm_par_fp
    del b13_grav, dot_rg, cos2_rg, gm_par_fp

    # Flight-line seam-cleaned RTP ridge (damping pure N-S / E-W leveling seams)
    psi = np.arctan2(rtp_gy, rtp_gx)
    seam_weight = (1.0 - 0.35 * (np.cos(2.0 * psi) ** 8)).astype(np.float32)
    rtp_aniso = np.maximum(
        _hessian_ridge_aniso(b02_rtp, 1.8, sign=1.0),
        _hessian_ridge_aniso(b02_rtp, 1.8, sign=-1.0),
    )
    seam_clean_rtp = (rtp_aniso * seam_weight).astype(np.float32)
    mm[:, 15] = seam_clean_rtp[fp]
    del psi, seam_weight, rtp_aniso

    # --- Family III: Hydrothermal Clay-Cap Conduit, Demag & Transtension ---
    b17_cond = read_clean_band(features_path, 17, fp)
    mm[:, 16] = b17_cond[fp]
    _, _, cond_grad = _grad_xy(b17_cond, 4.0)
    mm[:, 17] = cond_grad[fp]
    del cond_grad

    # Hydrothermal magnetite-destruction conduit: high conductivity x local RTP magnetic low x 1D RTP edge
    rtp_lrm_low = np.maximum(0.0, gaussian_filter(b02_rtp, sigma=8.0, mode="nearest") - b02_rtp).astype(np.float32)
    cond_pos = np.maximum(0.0, _robust_z_fp(b17_cond[fp]))
    demag_conduit = (cond_pos * _robust_unit_fp(rtp_lrm_low[fp]) * _robust_unit_fp(rtp_hg_12[fp])).astype(np.float32)
    mm[:, 18] = demag_conduit
    del b02_rtp, b17_cond, rtp_lrm_low, cond_pos, demag_conduit
    gc.collect()

    b07_shear = read_clean_band(features_path, 7, fp)
    b08_dil = read_clean_band(features_path, 8, fp)
    z_sh = np.maximum(0.0, _robust_z_fp(b07_shear[fp]) + 1.0)
    z_di = np.maximum(0.0, _robust_z_fp(b08_dil[fp]) + 0.5)
    mm[:, 19] = (z_sh * z_di).astype(np.float32)
    mm[:, 21] = b08_dil[fp]
    del b07_shear, b08_dil, z_sh, z_di

    b04_inv = read_clean_band(features_path, 4, fp)
    mm[:, 20] = b04_inv[fp]
    del b04_inv

    b10_deq = read_clean_band(features_path, 10, fp)
    mm[:, 22] = (-np.log10(np.maximum(b10_deq[fp], 50.0))).astype(np.float32)
    del b10_deq

    b16_ieq = read_clean_band(features_path, 16, fp)
    mm[:, 23] = np.log10(np.maximum(b16_ieq[fp], 1.0)).astype(np.float32)
    del b16_ieq
    gc.collect()

    # --- Family IV: Cover-Deconfounded Piedmont Flexure & Scarp Concavity ---
    b12_elev = read_clean_band(features_path, 12, fp)
    b19_slope = np.maximum(read_clean_band(features_path, 19, fp), 0.0)

    conc_1 = _hessian_ridge_aniso(b12_elev, 1.2, sign=1.0)
    conc_2 = _hessian_ridge_aniso(b12_elev, 2.2, sign=1.0)
    conc_3 = _hessian_ridge_aniso(b12_elev, 3.5, sign=1.0)
    piedmont_conc_2d = np.maximum(
        np.maximum(conc_1, conc_2 * 1.6),
        conc_3 * 2.4,
    ).astype(np.float32)
    mm[:, 24] = piedmont_conc_2d[fp]
    del conc_1, conc_2, conc_3

    scarp_crest_2d = _hessian_ridge_aniso(b19_slope, 1.5, sign=-1.0)
    mm[:, 25] = scarp_crest_2d[fp]
    del scarp_crest_2d

    # Multi-physics 600 m structure tensor for strike coherence + axial strike angle theta_phys
    el_gy, el_gx, _ = _grad_xy(b12_elev, 1.5)
    # Fuse normalized elevation gradient + RTP gradient + gravity gradient into joint structure tensor
    s_el = float(np.percentile(np.hypot(el_gy[fp], el_gx[fp]), 90)) + 1e-6
    s_rt = float(np.percentile(rtp_hg_12[fp], 90)) + 1e-6
    s_gr = float(np.percentile(grav_hg[fp], 90)) + 1e-6
    jyy = gaussian_filter(
        (el_gy / s_el) ** 2 + 0.6 * (rtp_gy / s_rt) ** 2 + 0.6 * (grav_gy / s_gr) ** 2,
        sigma=6.0,
        mode="nearest",
    ).astype(np.float32)
    jxx = gaussian_filter(
        (el_gx / s_el) ** 2 + 0.6 * (rtp_gx / s_rt) ** 2 + 0.6 * (grav_gx / s_gr) ** 2,
        sigma=6.0,
        mode="nearest",
    ).astype(np.float32)
    jyx = gaussian_filter(
        (el_gy * el_gx) / (s_el ** 2)
        + 0.6 * (rtp_gy * rtp_gx) / (s_rt ** 2)
        + 0.6 * (grav_gy * grav_gx) / (s_gr ** 2),
        sigma=6.0,
        mode="nearest",
    ).astype(np.float32)
    del el_gy, el_gx, rtp_gy, rtp_gx, grav_gy, grav_gx, grav_hg

    diff = jyy - jxx
    rad = np.hypot(diff, 2.0 * jyx)
    coh_2d = (rad / (jyy + jxx + 1e-8)).astype(np.float32)
    mm[:, 26] = coh_2d[fp]

    # Gradient normal angle is 0.5*atan2(2*jyx, jyy - jxx) in (y, x) frame;
    # Ridge strike tangent is perpendicular (+90 deg => negate cos(2*theta), sin(2*theta)!)
    # Specifically, if gradient vector has 2*phi_grad = atan2(2*jyx, jxx - jyy) in (x, y) convention:
    # Let's keep a single exact convention in (y, x):
    # Gradient dominant eigenvector u_grad satisfies (cos 2a_g, sin 2a_g) = ((jyy - jxx)/rad, 2*jyx/rad)
    # Strike tangent u_strike = (-u_grad_x, u_grad_y) has (cos 2a_s, sin 2a_s) = (-(jyy - jxx)/rad, -2*jyx/rad)!
    inv_rad = 1.0 / (rad + 1e-8)
    phys_c2_2d = (-diff * inv_rad).astype(np.float32)
    phys_s2_2d = (-2.0 * jyx * inv_rad).astype(np.float32)
    np.save(c2_path, phys_c2_2d)
    np.save(s2_path, phys_s2_2d)
    del jyy, jxx, jyx, diff, rad, inv_rad, coh_2d

    lrm_elev = (b12_elev - gaussian_filter(b12_elev, sigma=5.0, mode="nearest")).astype(np.float32)
    mm[:, 27] = np.abs(lrm_elev[fp])
    del b12_elev, lrm_elev

    mm[:, 28] = _cover_decile_rank(b19_slope[fp], cover_fp, n_bins=10)
    pot_combo_fp = _robust_unit_fp(rtp_hg_12[fp]) + _robust_unit_fp(b05_grav_slope[fp])
    mm[:, 29] = _cover_decile_rank(pot_combo_fp, cover_fp, n_bins=10)

    # Composite 2D physical conduit ridge map for interaction features f40, f41
    phys_ridge_2d = np.zeros((H, W), dtype=np.float32)
    phys_ridge_2d[fp] = (
        0.30 * mm[:, 28]
        + 0.25 * mm[:, 29]
        + 0.25 * _robust_unit_fp(piedmont_conc_2d[fp])
        + 0.20 * _robust_unit_fp(hinge_2d[fp])
    ).astype(np.float32)
    np.save(ridge_path, phys_ridge_2d)

    del b19_slope, b05_grav_slope, rtp_hg_12, seam_clean_rtp, piedmont_conc_2d, hinge_2d, pot_combo_fp
    mm.flush()
    meta_path.write_text(
        json.dumps({"feature_names": list(PHYS_FEATURE_NAMES), "n_fp": n_fp}, indent=2),
        encoding="utf-8",
    )
    gc.collect()

    mm_ro = np.memmap(mm_path, dtype=np.float32, mode="r", shape=(n_fp, n_phys))
    return {
        "phys_mm": mm_ro,
        "cover_fp": cover_fp,
        "phys_ridge_2d": phys_ridge_2d,
        "phys_c2_2d": phys_c2_2d,
        "phys_s2_2d": phys_s2_2d,
    }


def _extract_tips_and_tangents(vis_clean: np.ndarray, lbl: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return tip coordinates (ty, tx), outward unit vectors (uy, ux), and component ids."""
    H, W = vis_clean.shape
    nb = convolve(vis_clean.astype(np.int16), np.ones((3, 3), dtype=np.int16), mode="constant", cval=0) - 1
    tips_mask = vis_clean & (nb == 1)
    ty, tx = np.nonzero(tips_mask)
    n_tips = ty.size
    uy = np.zeros(n_tips, dtype=np.float32)
    ux = np.zeros(n_tips, dtype=np.float32)
    cids = lbl[ty, tx].astype(np.int32)

    R = 8
    for k in range(n_tips):
        y0, x0 = int(ty[k]), int(tx[k])
        cid = int(cids[k])
        ya, yb = max(0, y0 - R), min(H, y0 + R + 1)
        xa, xb = max(0, x0 - R), min(W, x0 + R + 1)
        patch = lbl[ya:yb, xa:xb] == cid
        py, px = np.nonzero(patch)
        dy = (ya + py) - y0
        dx = (xa + px) - x0
        r2 = dy * dy + dx * dx
        # Use interior strand pixels 2..8 px behind the tip
        sel = (r2 >= 4) & (r2 <= 64)
        if not sel.any():
            sel = r2 >= 1
        if sel.any():
            vy = float(y0 - (y0 + dy[sel].mean()))
            vx = float(x0 - (x0 + dx[sel].mean()))
            nrm = float(np.hypot(vy, vx)) + 1e-8
            uy[k] = vy / nrm
            ux[k] = vx / nrm
    return ty.astype(np.int32), tx.astype(np.int32), uy, ux, cids


def compute_network_features_fp(
    visible_mask: np.ndarray,
    footprint: np.ndarray,
    phys_ridge_2d: np.ndarray,
    phys_c2_2d: np.ndarray,
    phys_s2_2d: np.ndarray,
) -> np.ndarray:
    """Compute all 12 fold-safe visible-network structural features strictly from `visible_mask`."""
    vis = np.asarray(visible_mask, dtype=bool)
    fp = np.asarray(footprint, dtype=bool)
    H, W = vis.shape
    n_fp = int(fp.sum())
    out = np.zeros((n_fp, len(NET_FEATURE_NAMES)), dtype=np.float32)

    lbl, _ = label(vis, structure=np.ones((3, 3), dtype=int))
    sizes = np.bincount(lbl.ravel())
    keep = sizes >= 5
    keep[0] = False
    vis_clean = keep[lbl]
    if not vis_clean.any():
        return out

    # 1. Tip beams (short 1.2 km, long 3.0 km) + horsetail/wing-crack lobes (+-22 deg)
    ty, tx, uy, ux, cids = _extract_tips_and_tangents(vis_clean, lbl)
    beam_short = np.zeros((H, W), dtype=np.float32)
    beam_long = np.zeros((H, W), dtype=np.float32)
    wing_lobe = np.zeros((H, W), dtype=np.float32)

    R_BEAM = 34
    oy, ox = np.mgrid[-R_BEAM : R_BEAM + 1, -R_BEAM : R_BEAM + 1].astype(np.float32)
    rr = np.hypot(oy, ox).astype(np.float32)
    valid_r = (rr >= 1.0) & (rr <= float(R_BEAM))

    for k in range(ty.size):
        y0, x0 = int(ty[k]), int(tx[k])
        uyk, uxk = float(uy[k]), float(ux[k])
        if uyk == 0.0 and uxk == 0.0:
            continue
        ya, yb = max(0, y0 - R_BEAM), min(H, y0 + R_BEAM + 1)
        xa, xb = max(0, x0 - R_BEAM), min(W, x0 + R_BEAM + 1)
        p_oy = oy[ya - (y0 - R_BEAM) : yb - (y0 - R_BEAM), xa - (x0 - R_BEAM) : xb - (x0 - R_BEAM)]
        p_ox = ox[ya - (y0 - R_BEAM) : yb - (y0 - R_BEAM), xa - (x0 - R_BEAM) : xb - (x0 - R_BEAM)]
        p_rr = rr[ya - (y0 - R_BEAM) : yb - (y0 - R_BEAM), xa - (x0 - R_BEAM) : xb - (x0 - R_BEAM)]
        p_vr = valid_r[ya - (y0 - R_BEAM) : yb - (y0 - R_BEAM), xa - (x0 - R_BEAM) : xb - (x0 - R_BEAM)]

        s_par = p_oy * uyk + p_ox * uxk
        s_perp = -p_oy * uxk + p_ox * uyk
        fwd = p_vr & (s_par > 0.5)
        if not fwd.any():
            continue

        w1 = 0.28 * np.maximum(s_par, 0.0) + 1.2
        b1 = np.where(fwd, np.exp(-p_rr / 12.0) * np.exp(-((s_perp / w1) ** 2)), 0.0).astype(np.float32)
        np.maximum(beam_short[ya:yb, xa:xb], b1, out=beam_short[ya:yb, xa:xb])

        w2 = 0.34 * np.maximum(s_par, 0.0) + 1.5
        b2 = np.where(fwd, np.exp(-p_rr / 28.0) * np.exp(-((s_perp / w2) ** 2)), 0.0).astype(np.float32)
        np.maximum(beam_long[ya:yb, xa:xb], b2, out=beam_long[ya:yb, xa:xb])

        # Twin Andersonian +-22 deg (tan 22 deg ~ 0.404) horsetail splay lobes
        w_sp = 0.18 * np.maximum(s_par, 0.0) + 1.2
        lobe_pos = np.exp(-(((s_perp - 0.404 * s_par) / w_sp) ** 2))
        lobe_neg = np.exp(-(((s_perp + 0.404 * s_par) / w_sp) ** 2))
        bw = np.where(fwd, np.exp(-p_rr / 22.0) * np.maximum(lobe_pos, lobe_neg), 0.0).astype(np.float32)
        np.maximum(wing_lobe[ya:yb, xa:xb], bw, out=wing_lobe[ya:yb, xa:xb])

    # 2. Mutual Tip-to-Tip En-Echelon Relay-Ramp Breaching Bridge
    relay_bridge = np.zeros((H, W), dtype=np.float32)
    if ty.size >= 2:
        pts = np.column_stack([ty.astype(np.float64), tx.astype(np.float64)])
        tree = cKDTree(pts)
        pairs = tree.query_pairs(r=38.0, output_type="ndarray")
        for i, j in pairs:
            dy_ij = float(ty[j] - ty[i])
            dx_ij = float(tx[j] - tx[i])
            dist = float(np.hypot(dy_ij, dx_ij))
            if dist < 4.0:
                continue
            if cids[i] == cids[j] and dist < 14.0:
                continue
            ey, ex = dy_ij / dist, dx_ij / dist
            # Facing each other across an en-echelon step-over or gap:
            f_i = float(uy[i] * ey + ux[i] * ex)
            f_j = float(-(uy[j] * ey + ux[j] * ex))
            anti_par = float(-(uy[i] * uy[j] + ux[i] * ux[j]))
            if f_i <= 0.35 or f_j <= 0.35 or anti_par <= 0.35:
                continue
            # Average strike direction of the pair
            sy = float(uy[i] - uy[j])
            sx = float(ux[i] - ux[j])
            sn = float(np.hypot(sy, sx)) + 1e-8
            sy, sx = sy / sn, sx / sn
            step_perp = abs(-dy_ij * sx + dx_ij * sy)
            if step_perp > 18.0:
                continue

            cy_m = 0.5 * (ty[i] + ty[j])
            cx_m = 0.5 * (tx[i] + tx[j])
            pad = int(np.ceil(0.5 * dist + 6.0))
            ya, yb = max(0, int(cy_m) - pad), min(H, int(cy_m) + pad + 1)
            xa, xb = max(0, int(cx_m) - pad), min(W, int(cx_m) + pad + 1)
            gy, gx = np.mgrid[ya:yb, xa:xb].astype(np.float32)
            ry = gy - cy_m
            rx = gx - cx_m
            along = ry * ey + rx * ex
            across = -ry * ex + rx * ey
            half_len = max(0.5 * dist, 2.0)
            sig_perp = max(2.0, 0.35 * step_perp + 1.5)
            amp = float(np.exp(-dist / 26.0) * min(1.0, 0.5 * (f_i + f_j)))
            br = (
                amp
                * np.exp(-((np.maximum(0.0, np.abs(along) - half_len) / 2.5) ** 2))
                * np.exp(-((across / sig_perp) ** 2))
            ).astype(np.float32)
            np.maximum(relay_bridge[ya:yb, xa:xb], br, out=relay_bridge[ya:yb, xa:xb])

    # 3. Nearest-strand EDT + Strike-Steered Axial Continuation & Tectonic Strike Alignment
    vis_blur = gaussian_filter(vis_clean.astype(np.float32), sigma=2.0, mode="nearest")
    vgy, vgx, _ = _grad_xy(vis_blur, 1.2)
    jyy = gaussian_filter(vgy * vgy, sigma=3.0, mode="nearest")
    jxx = gaussian_filter(vgx * vgx, sigma=3.0, mode="nearest")
    jyx = gaussian_filter(vgy * vgx, sigma=3.0, mode="nearest")
    diff = jyy - jxx
    rad = np.hypot(diff, 2.0 * jyx) + 1e-8
    # Strike tangent 2*theta_net in (y, x) frame (matching phys_c2_2d / phys_s2_2d convention):
    net_c2_on = (-diff / rad).astype(np.float32)
    net_s2_on = (-2.0 * jyx / rad).astype(np.float32)
    # Unit tangent vector (ty_hat, tx_hat) from (cos 2a, sin 2a):
    # cos(2a) = ty^2 - tx^2, sin(2a) = 2*ty*tx
    ang = 0.5 * np.arctan2(net_s2_on, net_c2_on)
    t_hat_y = np.cos(ang).astype(np.float32)
    t_hat_x = np.sin(ang).astype(np.float32)
    del vis_blur, vgy, vgx, jyy, jxx, jyx, diff, rad, ang

    d_vis, nearest_idx = distance_transform_edt(~vis_clean, return_distances=True, return_indices=True)
    d_vis = d_vis.astype(np.float32)
    ny_fp = nearest_idx[0][fp]
    nx_fp = nearest_idx[1][fp]
    fy, fx = np.nonzero(fp)
    dy_fp = (fy - ny_fp).astype(np.float32)
    dx_fp = (fx - nx_fp).astype(np.float32)
    ty_fp = t_hat_y[ny_fp, nx_fp]
    tx_fp = t_hat_x[ny_fp, nx_fp]

    d_par = np.abs(dy_fp * ty_fp + dx_fp * tx_fp)
    d_perp = np.abs(-dy_fp * tx_fp + dx_fp * ty_fp)
    d_fp = d_vis[fp]
    # Clamp inside 3.5 px so collar proximity is completely flat and non-leaky
    d_par_c = np.maximum(d_par, 3.5)

    corridor_2km = np.exp(-0.5 * ((d_par_c / 20.0) ** 2 + (d_perp / 3.5) ** 2)).astype(np.float32)
    corridor_4p5km = np.exp(-0.5 * ((d_par_c / 45.0) ** 2 + (d_perp / 6.0) ** 2)).astype(np.float32)

    net_c2_fp = net_c2_on[ny_fp, nx_fp]
    net_s2_fp = net_s2_on[ny_fp, nx_fp]
    strike_align_cos2 = np.clip(
        0.5 * (1.0 + phys_c2_2d[fp] * net_c2_fp + phys_s2_2d[fp] * net_s2_fp),
        0.0,
        1.0,
    ).astype(np.float32)

    # 4. Regional district density priors (clamped smoothly across local blind zone)
    vis_f = vis_clean.astype(np.float32)
    dens_5km = gaussian_filter(vis_f, sigma=50.0, mode="nearest").astype(np.float32)
    nb_all = convolve(vis_clean.astype(np.int16), np.ones((3, 3), dtype=np.int16), mode="constant", cval=0) - 1
    tips_junc = ((vis_clean & (nb_all == 1)).astype(np.float32) + 2.0 * (vis_clean & (nb_all >= 3)).astype(np.float32))
    dens_tj_10km = gaussian_filter(tips_junc, sigma=100.0, mode="nearest").astype(np.float32)

    ridge_fp = phys_ridge_2d[fp]
    out[:, 0] = beam_short[fp]
    out[:, 1] = beam_long[fp]
    out[:, 2] = wing_lobe[fp]
    out[:, 3] = relay_bridge[fp]
    out[:, 4] = corridor_2km
    out[:, 5] = corridor_4p5km
    out[:, 6] = np.log10(np.maximum(d_fp, 3.5)).astype(np.float32)
    out[:, 7] = dens_5km[fp]
    out[:, 8] = dens_tj_10km[fp]
    out[:, 9] = (beam_long[fp] * ridge_fp).astype(np.float32)
    out[:, 10] = (relay_bridge[fp] * ridge_fp).astype(np.float32)
    out[:, 11] = strike_align_cos2

    return out


def compute_kernel_target(truth_mask: np.ndarray) -> np.ndarray:
    """Exact continuous DTI kernel proximity target q(x) = max_{g in truth} k(d(x, g)) in [0, 1]."""
    t = np.asarray(truth_mask, dtype=bool)
    if not t.any():
        return np.zeros(t.shape, dtype=np.float32)
    d = distance_transform_edt(~t).astype(np.float32)
    return np.maximum(0.0, 1.0 - d / float(g57_metric.RADIUS_PX)).astype(np.float32)


def make_self_masked_training_splits(
    visible_mask: np.ndarray,
    train_region: np.ndarray,
    footprint: np.ndarray,
    *,
    n_draws: int = 3,
    hide_frac: float = 0.22,
    buffer_px: int = 3,
    seed: int = 20261024,
) -> List[Dict[str, np.ndarray]]:
    """Create internal whole-component self-masked splits strictly inside `train_region`.

    Never touches `~train_region` or held-out test components. Ensures network
    continuation features have identical missing-segment geometry during training
    and testing (zero on-trace memorization).
    """
    vis_train = np.asarray(visible_mask, dtype=bool) & np.asarray(train_region, dtype=bool)
    lbl, n_comp = label(vis_train, structure=np.ones((3, 3), dtype=int))
    if n_comp < 4:
        raise ValueError("Too few visible components inside training region")
    comp_sizes = np.bincount(lbl.ravel())[1:]
    target_hide = float(hide_frac) * float(comp_sizes.sum())

    draws: List[Dict[str, np.ndarray]] = []
    for d_idx in range(n_draws):
        rng = np.random.default_rng(seed + 97 * d_idx)
        perm = rng.permutation(n_comp) + 1
        acc = 0.0
        picked = np.zeros(n_comp + 1, dtype=bool)
        for cid in perm:
            picked[cid] = True
            acc += float(comp_sizes[cid - 1])
            if acc >= target_hide:
                break
        pseudo_hidden = picked[lbl]
        d_ph = distance_transform_edt(~pseudo_hidden)
        context_vis = (np.asarray(visible_mask, dtype=bool) & (~pseudo_hidden) & (d_ph > float(buffer_px)))
        d_ctx = distance_transform_edt(~context_vis)
        # Active training domain matches holdout scoring outside the 3 px collar of context_vis
        active_train = np.asarray(footprint, dtype=bool) & np.asarray(train_region, dtype=bool) & (d_ctx > float(buffer_px))
        draws.append(
            {
                "context_vis": context_vis,
                "pseudo_hidden": pseudo_hidden & active_train,
                "active_train": active_train,
            }
        )
    return draws


def _sample_balanced_indices(
    pos_fp: np.ndarray,
    active_fp: np.ndarray,
    cover_fp: np.ndarray,
    *,
    max_pos: int = 35_000,
    neg_ratio: int = 3,
    seed: int = 101,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Sample stratified positive/negative footprint indices with cover-depth propensity weights."""
    rng = np.random.default_rng(seed)
    pos_idx = np.flatnonzero(pos_fp & active_fp)
    neg_idx = np.flatnonzero((~pos_fp) & active_fp)
    if pos_idx.size == 0 or neg_idx.size == 0:
        raise ValueError("Empty positive or negative training pool")
    if pos_idx.size > max_pos:
        pos_idx = rng.choice(pos_idx, size=max_pos, replace=False)
    n_neg = min(neg_idx.size, int(pos_idx.size * neg_ratio))
    neg_idx = rng.choice(neg_idx, size=n_neg, replace=False)

    idx = np.concatenate([pos_idx, neg_idx])
    y = np.concatenate([np.ones(pos_idx.size, dtype=np.int32), np.zeros(neg_idx.size, dtype=np.int32)])

    # Cover-depth inverse-exposure propensity weighting: boosts concealed deep-cover positives
    # so the classifier does not merely learn bedrock exposure (`B15 < 50 m`).
    cov = cover_fp[idx]
    q_edges = np.quantile(cover_fp[active_fp], [0.25, 0.50, 0.75])
    strata = np.digitize(cov, q_edges)
    w = np.ones(idx.size, dtype=np.float32)
    overall_pos_rate = float(pos_fp[active_fp].mean()) + 1e-8
    for s in range(4):
        m_all = (np.digitize(cover_fp[active_fp], q_edges) == s)
        if m_all.any():
            s_rate = float(pos_fp[active_fp][m_all].mean()) + 1e-8
            # Gentle square-root inverse propensity ratio clamped to [0.65, 1.85]
            boost = float(np.clip(np.sqrt(overall_pos_rate / s_rate), 0.65, 1.85))
            w[(strata == s) & (y == 1)] *= boost
    return idx, y, w


def prior_calibrate_prob(raw_prob: np.ndarray, sample_prior: float, target_prior: float) -> np.ndarray:
    """Exact Bayes prior-shift calibration from training sample prevalence to true hidden fault prevalence."""
    p = np.clip(np.asarray(raw_prob, dtype=np.float64), 1e-6, 1.0 - 1e-6)
    sp = float(np.clip(sample_prior, 1e-6, 1.0 - 1e-6))
    tp = float(np.clip(target_prior, 1e-6, 1.0 - 1e-6))
    odds = (p / (1.0 - p)) * ((tp / (1.0 - tp)) / (sp / (1.0 - sp)))
    cal = odds / (1.0 + odds)
    return np.clip(cal, 0.0, 1.0).astype(np.float32)


def strand_multiplicity_factor(truth_mask: np.ndarray, footprint: np.ndarray) -> float:
    """Exact empirical ratio sum(Y * k) / sum(max_g Y_g k) on visible strands (~2.55).

    Fixes `IR-78-EMIT-JENSEN` from first principles with zero extra regressor trees.
    """
    y_f = (np.asarray(truth_mask, dtype=bool) & np.asarray(footprint, dtype=bool)).astype(np.float32)
    conv_sum = float(g57_emit.expected_credit(y_f)[footprint].sum())
    max_cov = float(compute_kernel_target(y_f > 0)[footprint].sum())
    if max_cov <= 1e-6:
        return 2.60
    return float(np.clip(conv_sum / max_cov, 1.50, 4.00))


def self_credit_from_posterior(p_2d: np.ndarray, mu_strand: float = 2.60) -> np.ndarray:
    """Convert calibrated pixel posterior `p_2d` into Jensen-repaired kernel self-credit `m_2d`."""
    ek = g57_emit.expected_credit(np.asarray(p_2d, dtype=np.float32))
    return np.clip(ek / float(max(mu_strand, 1.0)), 0.0, 1.0).astype(np.float32)


def fit_expert_a_phys_loqo(
    phys_mm: np.ndarray,
    cover_fp: np.ndarray,
    folds: Dict[str, dict],
    footprint: np.ndarray,
    *,
    seed: int = 20261024,
) -> Dict[str, object]:
    """Fit Leave-One-Quadrant-Out zero-catalogue Multi-Physics Expert A (`30` features)."""
    from sklearn.ensemble import HistGradientBoostingClassifier

    fp = np.asarray(footprint, dtype=bool)
    n_fp = int(fp.sum())
    oof_p_fp = np.zeros(n_fp, dtype=np.float32)
    models_p = []
    mu_list = []

    for f_i, (qname, fold) in enumerate(folds.items()):
        train_quad_2d = fold.get("train_quad", ~fold["region"])
        train_reg_fp = train_quad_2d[fp]
        pred_quad_fp = fold.get("full_quad", fold["region"])[fp]
        vis_train_2d = fold["visible"] & train_quad_2d
        vis_train_fp = vis_train_2d[fp]
        mu_list.append(strand_multiplicity_factor(vis_train_2d, train_quad_2d))

        idx, y, w = _sample_balanced_indices(
            vis_train_fp,
            train_reg_fp,
            cover_fp,
            max_pos=36_000,
            neg_ratio=3,
            seed=seed + 11 * f_i,
        )
        X_tr = np.asarray(phys_mm[idx], dtype=np.float32)

        clf = HistGradientBoostingClassifier(
            max_iter=180,
            learning_rate=0.06,
            max_depth=6,
            min_samples_leaf=80,
            l2_regularization=4.0,
            random_state=seed + 11 * f_i,
        )
        clf.fit(X_tr, y, sample_weight=w)

        sample_prior = float(np.average(y, weights=w))
        target_prior = 0.0022
        del X_tr
        gc.collect()

        pred_idx = np.flatnonzero(pred_quad_fp)
        X_te = np.asarray(phys_mm[pred_idx], dtype=np.float32)
        oof_p_fp[pred_idx] = prior_calibrate_prob(clf.predict_proba(X_te)[:, 1], sample_prior, target_prior)
        del X_te
        gc.collect()

        models_p.append((clf, sample_prior, target_prior))

    return {
        "oof_p_fp": oof_p_fp,
        "mu_strand": float(np.mean(mu_list)),
        "models_p": models_p,
    }


def fit_expert_b_dual_loqo(
    phys_mm: np.ndarray,
    cover_fp: np.ndarray,
    phys_ridge_2d: np.ndarray,
    phys_c2_2d: np.ndarray,
    phys_s2_2d: np.ndarray,
    folds: Dict[str, dict],
    footprint: np.ndarray,
    *,
    seed: int = 20261024,
) -> Dict[str, object]:
    """Fit Leave-One-Quadrant-Out Self-Masked Dual Expert B (`42` features: `30` phys + `12` net)."""
    from sklearn.ensemble import HistGradientBoostingClassifier

    fp = np.asarray(footprint, dtype=bool)
    n_fp = int(fp.sum())
    oof_p_fp = np.zeros(n_fp, dtype=np.float32)
    models_p = []
    mu_list = []

    shared_vis = next(iter(folds.values()))["visible"]
    global_draws = make_self_masked_training_splits(
        shared_vis,
        fp,
        fp,
        n_draws=2,
        hide_frac=0.22,
        buffer_px=3,
        seed=seed + 777,
    )
    draw_nets = []
    for dr in global_draws:
        net_d = compute_network_features_fp(
            dr["context_vis"], fp, phys_ridge_2d, phys_c2_2d, phys_s2_2d
        )
        draw_nets.append((net_d, dr["pseudo_hidden"][fp], dr["active_train"][fp]))

    oof_net_fp = compute_network_features_fp(
        shared_vis, fp, phys_ridge_2d, phys_c2_2d, phys_s2_2d
    )
    oof_dvis_fp = (10.0 ** oof_net_fp[:, 6]).astype(np.float32)

    for f_i, (qname, fold) in enumerate(folds.items()):
        full_test_quad = fold.get("full_quad", fold["region"])
        safe_train_2d = fp & (distance_transform_edt(~full_test_quad) > 36.0)
        safe_train_fp = safe_train_2d[fp]
        pred_quad_fp = full_test_quad[fp]
        mu_list.append(strand_multiplicity_factor(shared_vis & safe_train_2d, safe_train_2d))

        X_chunks = []
        y_chunks = []
        w_chunks = []
        target_priors = []

        for d_j, (net_d, pos_d_fp, act_d_fp) in enumerate(draw_nets):
            act_fold_fp = act_d_fp & safe_train_fp
            target_priors.append(float(pos_d_fp[act_fold_fp].mean()))
            idx, y, w = _sample_balanced_indices(
                pos_d_fp,
                act_fold_fp,
                cover_fp,
                max_pos=20_000,
                neg_ratio=3,
                seed=seed + 100 * f_i + d_j,
            )
            X_part = np.hstack([np.asarray(phys_mm[idx], dtype=np.float32), net_d[idx]])
            X_chunks.append(X_part)
            y_chunks.append(y)
            w_chunks.append(w)

        X_tr = np.vstack(X_chunks)
        y_tr = np.concatenate(y_chunks)
        w_tr = np.concatenate(w_chunks)
        del X_chunks, y_chunks, w_chunks
        gc.collect()

        clf = HistGradientBoostingClassifier(
            max_iter=190,
            learning_rate=0.055,
            max_depth=6,
            min_samples_leaf=90,
            l2_regularization=5.0,
            random_state=seed + 53 * f_i,
        )
        clf.fit(X_tr, y_tr, sample_weight=w_tr)

        sample_prior = float(np.average(y_tr, weights=w_tr))
        target_prior = float(np.mean(target_priors))
        del X_tr, y_tr, w_tr
        gc.collect()

        pred_idx = np.flatnonzero(pred_quad_fp)
        X_te = np.hstack([np.asarray(phys_mm[pred_idx], dtype=np.float32), oof_net_fp[pred_idx]])
        oof_p_fp[pred_idx] = prior_calibrate_prob(clf.predict_proba(X_te)[:, 1], sample_prior, target_prior)
        del X_te
        gc.collect()

        models_p.append((clf, sample_prior, target_prior))

    del draw_nets
    gc.collect()

    return {
        "oof_p_fp": oof_p_fp,
        "oof_dvis_fp": oof_dvis_fp,
        "oof_net_fp": oof_net_fp,
        "mu_strand": float(np.mean(mu_list)),
        "models_p": models_p,
    }


def predict_full_catalogue_ensemble(
    phys_mm: np.ndarray,
    cover_fp: np.ndarray,
    phys_ridge_2d: np.ndarray,
    phys_c2_2d: np.ndarray,
    phys_s2_2d: np.ndarray,
    catalogue: np.ndarray,
    footprint: np.ndarray,
    expert_a: Dict[str, object],
    expert_b: Dict[str, object],
) -> Dict[str, np.ndarray]:
    """Run all 4 LOQO Expert A + Expert B models across the full footprint for competition export."""
    fp = np.asarray(footprint, dtype=bool)
    n_fp = int(fp.sum())

    p_a = np.zeros(n_fp, dtype=np.float64)
    chunk = 800_000
    for start in range(0, n_fp, chunk):
        end = min(n_fp, start + chunk)
        Xc = np.asarray(phys_mm[start:end], dtype=np.float32)
        for clf, sp, tp in expert_a["models_p"]:
            p_a[start:end] += prior_calibrate_prob(clf.predict_proba(Xc)[:, 1], sp, tp)
    p_a = (p_a / float(len(expert_a["models_p"]))).astype(np.float32)

    net_full_fp = compute_network_features_fp(
        catalogue, fp, phys_ridge_2d, phys_c2_2d, phys_s2_2d
    )
    p_b = np.zeros(n_fp, dtype=np.float64)
    for start in range(0, n_fp, chunk):
        end = min(n_fp, start + chunk)
        Xc = np.hstack([np.asarray(phys_mm[start:end], dtype=np.float32), net_full_fp[start:end]])
        for clf, sp, tp in expert_b["models_p"]:
            p_b[start:end] += prior_calibrate_prob(clf.predict_proba(Xc)[:, 1], sp, tp)
    p_b = (p_b / float(len(expert_b["models_p"]))).astype(np.float32)
    dcat_fp = (10.0 ** net_full_fp[:, 6]).astype(np.float32)
    del net_full_fp
    gc.collect()

    return {
        "p_a_fp": p_a,
        "p_b_fp": p_b,
        "dcat_fp": dcat_fp,
    }


def fuse_dual_experts(
    p_a_fp: np.ndarray,
    p_b_fp: np.ndarray,
    cover_fp: np.ndarray,
    dist_fp: np.ndarray,
    *,
    blind_basin_boost: float = 0.0,
) -> np.ndarray:
    """Cover-depth & distance adaptive fusion of Zero-Catalogue Expert A and Network Expert B."""
    g_dist = np.exp(-np.maximum(dist_fp - 12.0, 0.0) / 40.0)
    g_cov = 1.0 / (1.0 + (np.maximum(cover_fp, 0.0) / 600.0))
    w_b = np.clip(0.35 + 0.50 * (0.65 * g_dist + 0.35 * g_cov) - blind_basin_boost, 0.25, 0.85).astype(np.float32)
    w_a = (1.0 - w_b).astype(np.float32)
    return np.clip(w_b * p_b_fp + w_a * p_a_fp, 0.0, 1.0).astype(np.float32)


def allocate_regime_stratified_celf(
    p_2d: np.ndarray,
    m_2d: np.ndarray,
    allowed_2d: np.ndarray,
    cover_2d: np.ndarray,
    *,
    total_budget: int = 37_654,
    shares: Tuple[float, float, float] = (0.34, 0.36, 0.30),
    depth_splits_m: Tuple[float, float] = (80.0, 400.0),
    min_spacing_px: float = 2.5,
    k_truth: float = 14_200.0,
) -> np.ndarray:
    """3-Regime Cover-Depth Stratified CELF Submodular DTI Allocation (`Bedrock / Piedmont / Basin`)."""
    r0 = allowed_2d & (cover_2d <= depth_splits_m[0])
    r1 = allowed_2d & (cover_2d > depth_splits_m[0]) & (cover_2d <= depth_splits_m[1])
    r2 = allowed_2d & (cover_2d > depth_splits_m[1])

    b0 = int(round(total_budget * shares[0]))
    b1 = int(round(total_budget * shares[1]))
    b2 = int(total_budget - b0 - b1)

    emitted = np.zeros(p_2d.shape, dtype=bool)
    for mask_r, bud_r, sh_r in ((r0, b0, shares[0]), (r1, b1, shares[1]), (r2, b2, shares[2])):
        if bud_r <= 0 or not mask_r.any():
            continue
        alloc = g57_emit.dinkelbach_allocate(
            p_2d,
            m_2d,
            mask_r,
            budget=bud_r,
            k_truth=max(k_truth * sh_r, 500.0),
            min_spacing_px=min_spacing_px,
            candidate_cap=240_000,
            dinkelbach_iters=2,
        )
        emitted |= alloc.emitted

    # Top up exact remainder globally if any regime had fewer candidates or boundary collisions
    rem = int(total_budget - int(emitted.sum()))
    if rem > 0:
        blocked = g57_emit.dilate_zone(emitted, 2)
        alloc_rem = g57_emit.dinkelbach_allocate(
            p_2d,
            m_2d,
            allowed_2d & (~blocked),
            budget=rem,
            k_truth=k_truth * 0.1,
            min_spacing_px=min_spacing_px,
            candidate_cap=120_000,
            dinkelbach_iters=1,
        )
        emitted |= alloc_rem.emitted
    return emitted


def run_leakage_canary_42(
    phys_mm: np.ndarray,
    oof_net_fp: np.ndarray,
    folds: Dict[str, dict],
    footprint: np.ndarray,
    *,
    sample_px: int = 400_000,
    seed: int = 11,
) -> Dict[str, object]:
    """Run symmetric single-feature AUC leakage canary (`<= 0.90`) on all 42 H89 features."""
    from sklearn.metrics import roc_auc_score

    fp = np.asarray(footprint, dtype=bool)
    # Pooled withheld hidden truth across all 4 active fold masks
    withheld_2d = np.zeros(fp.shape, dtype=bool)
    active_2d = np.zeros(fp.shape, dtype=bool)
    for fold in folds.values():
        act = fp & fold["region"] & (~fold["masked_known"])
        active_2d |= act
        withheld_2d |= act & fold["truth"]

    act_fp = active_2d[fp]
    y_all = withheld_2d[fp][act_fp].astype(np.int32)
    act_indices = np.flatnonzero(act_fp)

    rng = np.random.default_rng(seed)
    pos_i = np.flatnonzero(y_all == 1)
    neg_i = np.flatnonzero(y_all == 0)
    n_neg_sample = min(neg_i.size, max(sample_px - pos_i.size, pos_i.size * 10))
    sub = np.concatenate([pos_i, rng.choice(neg_i, size=n_neg_sample, replace=False)])
    fp_sub = act_indices[sub]
    y_sub = y_all[sub]

    results = {}
    max_strength = 0.0
    any_flag = False
    n_phys = len(PHYS_FEATURE_NAMES)

    for j, name in enumerate(ALL_FEATURE_NAMES):
        if j < n_phys:
            vals = np.asarray(phys_mm[fp_sub, j], dtype=np.float64)
        else:
            vals = np.asarray(oof_net_fp[fp_sub, j - n_phys], dtype=np.float64)
        vals = np.nan_to_num(vals, nan=0.0, posinf=0.0, neginf=0.0)
        if np.all(vals == vals[0]):
            auc = 0.5
        else:
            auc = float(roc_auc_score(y_sub, vals))
        strength = float(max(auc, 1.0 - auc))
        flag = bool(strength > 0.90)
        any_flag = any_flag or flag
        max_strength = max(max_strength, strength)
        results[name] = {
            "auc": round(auc, 6),
            "symmetric_auc": round(strength, 6),
            "flag": flag,
        }

    return {
        "instrument": "H89 42-feature leakage canary (single-feature AUC vs pooled withheld hidden truth on gems57-pooled-hide-v2)",
        "threshold": 0.90,
        "withheld_positive_pixels": int(pos_i.size),
        "sampled_negative_pixels": int(n_neg_sample),
        "seed": seed,
        "max_single_feature_strength": round(max_strength, 6),
        "any_flagged": any_flag,
        "verdict": "PASS: no single feature exceeds 0.90" if not any_flag else "FAIL: feature exceeded 0.90",
        "features": results,
    }
