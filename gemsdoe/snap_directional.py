"""SNAP axis, directional corner: snap only across-strike, toward one side.

Why this is a new cell of the SNAP design, not a dose repeat
-----------------------------------------------------------
The fleet's SNAP cells are a {window} x {gate} factorial over one response
surface (bands 3 `tmi_hg` + 18 `iso_grav_anom_hg`, fused by pixel-wise max):

    window 1.0 / 1.42 / 2.0 px  x  gate 0.00 (this repo) and 0.01 / 0.02
    (upstream GEMSDOE84)

Every one of those six arms lets a dot move in *any* direction inside the
window, and every one of them lands the dot on the local maximum of a
horizontal-gradient (HG) field.  That is a placement rule with a known
geometric bias: over a dipping contact the HG maximum is displaced from the
outcrop of the contact toward the hanging wall (the down-dip side), by roughly
depth / tan(dip).  Basin-and-Range normal faults dip ~50-60 deg and GeoDAWN
Area 2 was flown at 400 m line spacing (150-200 m above terrain), so the
displacement scale is 1-4 px and the sign is systematic, not random.

So there are two competing placement hypotheses for the same response surface,
and no arm in the ledger separates them:

  H_crest : the HG maximum IS the fault trace; the undirected snap is correct.
  H_dip   : the HG maximum sits on the hanging-wall (basin) side; a dot should
            be moved *up-slope* (toward the footwall / range front) instead.

`directional_snap` implements exactly the same rule as `snap.snap_dots`
(strongest allowed response inside the window, count preserved, targets
>= 3 px off the catalogue, row-major order, same tie-breaking, no fallback)
with ONE added filter: a candidate displacement must point into one half of
the window, defined by the local up-slope direction of the *detrended
elevation* band (band 12, the same pinned input the RELIEF axis uses).

    direction="footwall"    -> displacement has cos >= MIN_COS with up-slope
    direction="hangingwall" -> displacement has cos <= -MIN_COS with up-slope
    direction="none"        -> no filter; byte-identical to snap.snap_dots
                               (asserted by tests/test_snap_directional.py)

"footwall" and "hangingwall" at the same window are exact mirrors of each
other, so their two receipts bracket the sign of the parent's placement bias
while sharing identical displacement statistics (same offsets, same counts by
construction up to the response surface itself).  `direction="none"` exists
only as the parity control for the tests; no release uses it.

Slope deadband
--------------
On ground flatter than MIN_SLOPE_M_PER_PX (2% grade) "up-slope" is not a
geologically meaningful direction, so a dot there is left exactly where the
parent put it (no move, no fallback).  That keeps the directional arms
conservative and reportable: every moved dot moved toward a real slope.

No RNG anywhere: same parent + same response + same mode -> same bytes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy import ndimage as ndi

from .snap import MIN_GAIN, _offsets

DIRECTIONS = ("none", "footwall", "hangingwall")
MIN_COS = 0.5                 # displacement must be within +-60 deg of up-slope
MIN_SLOPE_M_PER_PX = 2.0      # 2 % grade: below this, up-slope is undefined
SMOOTH_SIGMA_PX = 2.0         # DEM de-noise before differencing


def uphill_field(detrended_elev: np.ndarray, foot: np.ndarray,
                 sigma: float = SMOOTH_SIGMA_PX) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Unit up-slope direction (uy, ux) and slope magnitude (m/px).

    Rows increase southward and columns eastward, so the up-slope unit vector
    is the normalised Sobel gradient in (row, col) index space.  Pixels with
    zero slope get (0, 0) and magnitude 0.
    """
    e = np.asarray(detrended_elev, dtype=np.float64)
    finite = np.isfinite(e)
    fill = float(np.median(e[foot & finite])) if (foot & finite).any() else 0.0
    e = np.where(finite, e, fill)
    s = ndi.gaussian_filter(e, sigma, mode="nearest")
    gy = ndi.sobel(s, axis=0) / 8.0
    gx = ndi.sobel(s, axis=1) / 8.0
    mag = np.hypot(gy, gx)
    safe = mag > 0
    uy = np.zeros_like(mag)
    ux = np.zeros_like(mag)
    uy[safe] = gy[safe] / mag[safe]
    ux[safe] = gx[safe] / mag[safe]
    return uy, ux, mag


@dataclass
class DirectionalSnapResult:
    mask: np.ndarray
    moves: list = field(default_factory=list)
    stats: dict = field(default_factory=dict)


def directional_snap(dots: np.ndarray, resp: np.ndarray, allowed: np.ndarray,
                     max_shift: float, direction: str = "footwall",
                     uy: np.ndarray | None = None, ux: np.ndarray | None = None,
                     slope: np.ndarray | None = None,
                     min_slope: float = MIN_SLOPE_M_PER_PX,
                     min_cos: float = MIN_COS,
                     margin: float = 0.0) -> DirectionalSnapResult:
    """Relocate dots onto the strongest allowed response on ONE side only.

    The movement rule, the ordering, the tie-breaking, the claim test and the
    count preservation are those of :func:`gemsdoe.snap.snap_dots`; the only
    added predicate is the directional one.  With ``direction="none"``,
    ``min_slope=0.0`` the output matches ``snap.snap_dots`` exactly.
    """
    if direction not in DIRECTIONS:
        raise ValueError(f"unknown direction {direction!r}")
    dots = np.asarray(dots, dtype=bool)
    min_gain = max(float(margin), MIN_GAIN)
    offs = _offsets(float(max_shift))
    if not offs:
        raise ValueError("max_shift admits no displacement")
    directional = direction != "none"
    if directional:
        if uy is None or ux is None or slope is None:
            raise ValueError("directional snap needs uy/ux/slope")
        sign = 1.0 if direction == "footwall" else -1.0

    claimed = dots.copy()
    ys, xs = np.nonzero(dots)
    new = dots.copy()
    moves: list[tuple[int, int, int, int, float, float, float]] = []
    gains: list[float] = []
    projs: list[float] = []
    n_blocked_feasibility = 0
    n_blocked_claim = 0
    n_blocked_direction = 0
    n_ambiguous = 0

    for y0, x0 in zip(ys.tolist(), xs.tolist()):
        r0 = float(resp[y0, x0])
        if directional:
            if float(slope[y0, x0]) < min_slope:
                n_ambiguous += 1
                continue
            vy, vx = float(uy[y0, x0]), float(ux[y0, x0])
        best = None
        for dy, dx, dist in offs:
            y1, x1 = y0 + dy, x0 + dx
            if not (0 <= y1 < resp.shape[0] and 0 <= x1 < resp.shape[1]):
                continue
            if directional and sign * (dy * vy + dx * vx) < min_cos * dist:
                n_blocked_direction += 1
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
        if directional:
            projs.append(sign * ((y1 - y0) * vy + (x1 - x0) * vx) / dist)

    disp = np.array([m[6] for m in moves], dtype=np.float64) if moves else np.zeros(0)
    dy_all = np.array([m[2] - m[0] for m in moves], dtype=np.float64) if moves else np.zeros(0)
    dx_all = np.array([m[3] - m[1] for m in moves], dtype=np.float64) if moves else np.zeros(0)
    stats = {
        "direction": direction,
        "max_shift_px": float(max_shift),
        "margin": float(margin),
        "min_gain_applied": float(min_gain),
        "min_cos": float(min_cos) if directional else None,
        "min_slope_m_per_px": float(min_slope) if directional else None,
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
        "mean_displacement_row": float(dy_all.mean()) if dy_all.size else 0.0,
        "mean_displacement_col": float(dx_all.mean()) if dx_all.size else 0.0,
        "mean_direction_cosine": float(np.mean(projs)) if projs else None,
        "dots_ambiguous_slope": int(n_ambiguous),
        "candidate_offsets_rejected_direction": int(n_blocked_direction),
        "candidate_pixels_rejected_infeasible": int(n_blocked_feasibility),
        "candidate_pixels_rejected_already_claimed": int(n_blocked_claim),
    }
    return DirectionalSnapResult(mask=new, moves=moves, stats=stats)


def upslope_share(moves, uy: np.ndarray, ux: np.ndarray,
                  slope: np.ndarray, min_slope: float = MIN_SLOPE_M_PER_PX) -> dict:
    """Report-only: of the moves, what share went up-slope (footwall-ward)?

    A real direction restriction should give ~1.00 for the footwall arm, ~0.00
    for its mirror, and ~0.5 for the undirected arms.  This is the audit that
    proves the two arms are mirrors rather than dose repeats.
    """
    if not moves:
        return {"n": 0, "share_upslope": None, "share_downslope": None}
    up = down = flat = 0
    for (y0, x0, y1, x1, *_r) in moves:
        if float(slope[y0, x0]) < min_slope:
            flat += 1
            continue
        p = (y1 - y0) * float(uy[y0, x0]) + (x1 - x0) * float(ux[y0, x0])
        if p > 0:
            up += 1
        elif p < 0:
            down += 1
        else:
            flat += 1
    n = up + down + flat
    return {
        "n": int(n),
        "n_upslope": int(up),
        "n_downslope": int(down),
        "n_flat_or_ambiguous": int(flat),
        "share_upslope": up / max(n, 1),
        "share_downslope": down / max(n, 1),
    }
