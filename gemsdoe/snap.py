"""SNAP axis: relocate parent dots onto the strongest edge response, <= L px away.

This session's values are the *gateless* corner of the upstream 2x2 factorial:
upstream GEMSDOE84 built (window 1.42, gate 0.02), (2.0, 0.02), (2.0, 0.01);
here gate = 0.00 at windows 1.0 / 1.42 / 2.0 px, i.e. the brief's literal
"move each dot <=2 px to the strongest edge/scarp response in its window".
With gate 0 a dot moves iff some allowed pixel in its window is *strictly*
stronger than its own (min gain 1e-9, the upstream convention), so the only
factor that differs from the upstream arms is the gate -- which makes the
cross-session comparison a clean gate ablation at windows 1.42 and 2.0.

Response recipe (replicated exactly from the upstream recorded recipe so the
gate is the only difference): per band, footprint-median nodata fill ->
gaussian sigma = 1.0 px (mode nearest) -> robust_unit (median/IQR z, 1.0 at
the 99.5th percentile of the footprint, clipped at 6 then divided by 6) ->
pixel-wise maximum over the two bands.  The bands are the competition
training_features.tif entries whose identities are pinned via the manifest's
band_identity_source: 3 = tmi_hg (TMI horizontal gradient), 18 =
iso_grav_anom_hg (isostatic gravity anomaly horizontal gradient).  LiDAR
rasters are deliberately NOT used (the brief restricts them to human supply).

Determinism: no RNG.  Dots are processed in row-major order; candidate
offsets are ordered by (distance, dy, dx); ties in response keep the first
(near) candidate; a dot whose best target is already claimed is skipped
(no fallback to second best).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.ndimage import gaussian_filter

EDGE_BANDS: tuple[tuple[int, str], ...] = ((3, "tmi_hg"), (18, "iso_grav_anom_hg"))
SMOOTH_SIGMA_PX = 1.0
ROBUST_PCT = 99.5
CLIP = 6.0
MIN_GAIN = 1e-9  # gate 0 still requires a strictly stronger target


def robust_unit(a: np.ndarray, foot: np.ndarray, pct: float = ROBUST_PCT,
                clip: float = CLIP) -> np.ndarray:
    """Footprint-normalised non-negative score in [0, 1] (median/IQR z at pct)."""
    out = np.zeros(a.shape, dtype=np.float32)
    v = foot & np.isfinite(a)
    if not v.any():
        return out
    vals = a[v]
    med = float(np.median(vals))
    q25, q75 = np.percentile(vals, [25.0, 75.0])
    scale = max(float(q75 - q25) / 1.349, 1e-9)
    z = (a - med) / scale
    hi = max(float(np.percentile(z[v], pct)), 1e-6)
    out[v] = np.clip(z[v] / hi, 0.0, clip) / clip
    return out


def prepare_band(raw: np.ndarray, foot: np.ndarray,
                 sigma: float = SMOOTH_SIGMA_PX) -> np.ndarray:
    """Median-fill -> gaussian smooth -> robust_unit, on the footprint."""
    v = foot & np.isfinite(raw) & (raw > -1e30)
    med = float(np.median(raw[v])) if v.any() else 0.0
    filled = np.where(v, raw, med).astype(np.float32)
    if sigma:
        filled = gaussian_filter(filled, sigma, mode="nearest").astype(np.float32)
    return robust_unit(filled, foot)


def edge_response(bands: dict[int, np.ndarray], foot: np.ndarray) -> tuple[np.ndarray, dict]:
    """Fused (pixel-wise max) edge-response surface in [0, 1] plus diagnostics."""
    per_band: dict[str, np.ndarray] = {}
    diag: dict = {"bands": [], "sigma_px": SMOOTH_SIGMA_PX, "robust_pct": ROBUST_PCT}
    for idx, name in EDGE_BANDS:
        n = prepare_band(bands[idx], foot)
        per_band[name] = n
        v = foot & np.isfinite(bands[idx]) & (bands[idx] > -1e30)
        diag["bands"].append({
            "index": idx, "name": name,
            "nodata_fraction": float(1.0 - v.sum() / max(int(foot.sum()), 1)),
            "mean_in_footprint": float(n[foot].mean()),
            "p99_in_footprint": float(np.percentile(n[foot], 99.0)),
        })
    fused = np.maximum.reduce([per_band[n] for _i, n in EDGE_BANDS]).astype(np.float32)
    fused[~foot] = 0.0
    diag["fused_mean_in_footprint"] = float(fused[foot].mean())
    return fused, {"response": diag, "per_band": per_band}


def _offsets(max_shift: float) -> list[tuple[int, int, float]]:
    """Candidate displacements 0 < |d| <= max_shift, ordered (dist, dy, dx)."""
    r = int(np.ceil(max_shift))
    out = []
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = float(np.hypot(dy, dx))
            if 0.0 < d <= max_shift + 1e-9:
                out.append((dy, dx, d))
    return sorted(out, key=lambda t: (round(t[2], 6), t[0], t[1]))


@dataclass
class SnapResult:
    mask: np.ndarray
    moves: list = field(default_factory=list)
    stats: dict = field(default_factory=dict)


def snap_dots(dots: np.ndarray, resp: np.ndarray, allowed: np.ndarray,
              max_shift: float, margin: float = 0.0) -> SnapResult:
    """Relocate dots onto higher-response pixels within ``max_shift`` px.

    ``margin`` = required response gain in robust-unit space; 0.0 (this
    session) means any strictly positive gain qualifies.  ``allowed`` masks
    pixels a dot may occupy (footprint, >= 3 px off catalogue).  Count is
    preserved exactly: a dot either moves to an unclaimed allowed pixel or
    stays put.
    """
    dots = np.asarray(dots, bool)
    min_gain = max(float(margin), MIN_GAIN)
    offs = _offsets(float(max_shift))
    if not offs:
        raise ValueError("max_shift admits no displacement")
    claimed = dots.copy()
    ys, xs = np.nonzero(dots)
    new = dots.copy()
    moves: list[tuple[int, int, int, int, float, float, float]] = []
    gains: list[float] = []
    n_blocked_feasibility = 0
    n_blocked_claim = 0

    for y0, x0 in zip(ys.tolist(), xs.tolist()):
        r0 = float(resp[y0, x0])
        best = None
        for dy, dx, dist in offs:
            y1, x1 = y0 + dy, x0 + dx
            if not (0 <= y1 < resp.shape[0] and 0 <= x1 < resp.shape[1]):
                continue
            if not allowed[y1, x1]:
                n_blocked_feasibility += 1
                continue
            r1 = float(resp[y1, x1])
            if r1 - r0 < min_gain:
                continue
            if best is None or r1 > best[3] + 1e-12:
                best = (y1, x1, dist, r1)
        if best is None:
            continue
        y1, x1, dist, r1 = best
        if claimed[y1, x1]:
            n_blocked_claim += 1
            continue
        claimed[y0, x0] = False
        claimed[y1, x1] = True
        new[y0, x0] = False
        new[y1, x1] = True
        moves.append((int(y0), int(x0), int(y1), int(x1), r0, r1, dist))
        gains.append(r1 - r0)

    disp = np.array([m[6] for m in moves], dtype=np.float64) if moves else np.zeros(0)
    stats = {
        "max_shift_px": float(max_shift),
        "margin": float(margin),
        "min_gain_applied": float(min_gain),
        "candidate_offsets": len(offs),
        "dots_in": int(dots.sum()),
        "dots_out": int(new.sum()),
        "count_preserved": bool(new.sum() == dots.sum()),
        "dots_moved": int(len(moves)),
        "pct_dots_moved": round(100.0 * len(moves) / max(int(dots.sum()), 1), 3),
        "mean_displacement_px": float(disp.mean()) if disp.size else 0.0,
        "median_displacement_px": float(np.median(disp)) if disp.size else 0.0,
        "max_displacement_px": float(disp.max()) if disp.size else 0.0,
        "mean_response_gain": float(np.mean(gains)) if gains else 0.0,
        "median_response_gain": float(np.median(gains)) if gains else 0.0,
        "candidate_pixels_rejected_infeasible": int(n_blocked_feasibility),
        "candidate_pixels_rejected_already_claimed": int(n_blocked_claim),
        "moved_targets_min_dcat_enforced_by_mask": True,
    }
    return SnapResult(mask=new, moves=moves, stats=stats)


def block_density_cv(mask: np.ndarray, footprint: np.ndarray, block_px: int = 10) -> float:
    """CV of dot density over block_px blocks (report only; SNAP must barely move it)."""
    h, w = mask.shape
    nb_y, nb_x = h // block_px, w // block_px
    m = mask[: nb_y * block_px, : nb_x * block_px].reshape(nb_y, block_px, nb_x, block_px)
    f = footprint[: nb_y * block_px, : nb_x * block_px].reshape(nb_y, block_px, nb_x, block_px)
    counts = m.sum(axis=(1, 3)).astype(np.float64)
    avail = f.sum(axis=(1, 3)).astype(np.float64)
    keep = avail > 0
    dens = counts[keep] / avail[keep]
    mu = float(dens.mean())
    return float(dens.std() / mu) if mu > 0 else 0.0
