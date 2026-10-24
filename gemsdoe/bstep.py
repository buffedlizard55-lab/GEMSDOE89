"""BSTP axis: basement-step x conductivity corroborated blind-fault lineaments.

Lane (single method, GEMSDOE89 session 2026-10-24)
---------------------------------------------------
New-support dots are emitted only where THREE independent physical channels
of the pinned 19-band competition stack coincide (geometric-mean fuzzy AND):

  1. BSTEP  gradient magnitude of band 15 `depth_to_base_surf`
     A buried normal fault offsets the basement surface, so depth-to-
     basement has a step across the fault even where basin fill buries any
     surface scarp.  This is precisely the class of fault a surface-mapping
     catalogue (USGS/INGENIOUS) misses, and precisely what the masked
     scoring rewards.
  2. COND   gradient magnitude of band 17 `cond_surf`
     Fault zones host clay alteration, gouge and saline fluids: a lateral
     conductivity contrast tracks the permeable conduit (the geothermal
     target itself), not just the lithologic offset.
  3. EDGE   pixel-wise max of band 3 `tmi_hg` and band 18 `iso_grav_anom_hg`
     (the existing SNAP response, reused unchanged): the same basement
     offset juxtaposes magnetic / dense lithologies.

Non-fault mimics named in advance: non-fault basement lithologic contacts
(step without faulting), paleochannel and playa-margin conductivity edges,
volcanic flow margins.  Requiring all three channels suppresses any single
mimic family; it does not eliminate coincident mimics.

Emission at fixed mass (DTI mass neutrality): retain the top 60% of parent
R0 dots by the label-free unique-credit ranking (`mass.unique_credit`),
drop the rest, and refill to exactly the parent count with surface-ranked
greedy dots (2.8 px suppression disk, the parent lineage's spacing) that
sit > 3 px from *every* parent dot and >= 3 px from the catalogue.  By
construction 40% of the candidate's dots have no parent dot within the
300 m scoring kernel, so the file is not a re-expression of any registry
raster (parallel-run uniqueness: < 70% of dots within 3 px of R0).

Deterministic: no RNG.  Candidates are ordered by (-surface, flat index).
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi

from .snap import robust_unit

SMOOTH_SIGMA_PX = 1.0
SUPPRESSION_PX = 2.8
RETAIN_FRACTION = 0.60
MIN_DCAT_PX = 3.0
MIN_DPARENT_PX = 3.0  # strict: new dot must satisfy d_parent > 3.0 px


def _filled_smooth(raw: np.ndarray, foot: np.ndarray,
                   sigma: float = SMOOTH_SIGMA_PX) -> np.ndarray:
    """Footprint-median nodata fill, then gaussian smooth (snap.py convention)."""
    v = foot & np.isfinite(raw) & (raw > -1e30)
    med = float(np.median(raw[v])) if v.any() else 0.0
    filled = np.where(v, raw, med).astype(np.float32)
    if sigma:
        filled = ndi.gaussian_filter(filled, sigma, mode="nearest").astype(np.float32)
    return filled


def gradient_channel(raw: np.ndarray, foot: np.ndarray) -> np.ndarray:
    """Robust-normalised gradient magnitude of a band, in [0, 1] on footprint."""
    f = _filled_smooth(raw, foot).astype(np.float64)
    gy = ndi.sobel(f, axis=0, mode="nearest")
    gx = ndi.sobel(f, axis=1, mode="nearest")
    mag = np.hypot(gx, gy).astype(np.float32)
    return robust_unit(mag, foot)


def bstep_surface(depth_to_base: np.ndarray, cond_surf: np.ndarray,
                  edge_response: np.ndarray, foot: np.ndarray):
    """Geometric-mean corroboration surface plus per-channel diagnostics.

    Returns (surface float32 in [0,1], channels dict, diag dict)."""
    ch_step = gradient_channel(depth_to_base, foot)
    ch_cond = gradient_channel(cond_surf, foot)
    ch_edge = np.asarray(edge_response, dtype=np.float32)
    prod = (ch_step.astype(np.float64) * ch_cond.astype(np.float64)
            * ch_edge.astype(np.float64))
    surface = np.where(foot, np.cbrt(np.maximum(prod, 0.0)), 0.0).astype(np.float32)
    channels = {"bstep_grad_depth_to_base": ch_step,
                "cond_grad_cond_surf": ch_cond,
                "edge_max_tmiHG_gravHG": ch_edge}
    diag = {}
    for name, ch in channels.items():
        v = ch[foot]
        diag[name] = {"p50": float(np.percentile(v, 50)),
                      "p99": float(np.percentile(v, 99)),
                      "frac_positive_in_footprint": float((v > 0).mean())}
    v = surface[foot]
    diag["surface_geomean"] = {"p50": float(np.percentile(v, 50)),
                                "p99": float(np.percentile(v, 99)),
                                "frac_positive_in_footprint": float((v > 0).mean())}
    return surface, channels, diag


def _disk_offsets(radius: float):
    r = int(np.floor(radius))
    dys, dxs = np.mgrid[-r:r + 1, -r:r + 1]
    m = (dys * dys + dxs * dxs) <= (radius * radius + 1e-9)
    return dys[m], dxs[m]


def greedy_surface_dots(surface: np.ndarray, eligible: np.ndarray,
                        blocked: np.ndarray, n_want: int,
                        radius: float = SUPPRESSION_PX) -> np.ndarray:
    """Greedy surface-ranked dot placement with a suppression disk.

    Pixels are visited in (-surface, flat-index) order; a pixel is accepted
    iff it is eligible and not inside the suppression disk of an already
    accepted (or pre-blocked, e.g. retained) dot.  Deterministic."""
    surf = np.asarray(surface, dtype=np.float32)
    elig = np.asarray(eligible, dtype=bool) & (surf > 0)
    out = np.zeros(surf.shape, dtype=bool)
    if n_want <= 0 or not elig.any():
        return out
    blocked = np.asarray(blocked, dtype=bool).copy()
    dys, dxs = _disk_offsets(radius)
    h, w = surf.shape
    order = np.argsort(-surf[elig], kind="stable")
    ys, xs = np.nonzero(elig)
    ys, xs = ys[order], xs[order]
    placed = 0
    for y, x in zip(ys, xs):
        if blocked[y, x]:
            continue
        out[y, x] = True
        placed += 1
        ry, rx = y + dys, x + dxs
        ok = (ry >= 0) & (ry < h) & (rx >= 0) & (rx < w)
        blocked[ry[ok], rx[ok]] = True
        if placed >= n_want:
            break
    if placed < n_want:
        raise RuntimeError(f"greedy placement exhausted: placed {placed} < {n_want}")
    return out


def build_bstep_candidate(parent_dots: np.ndarray, surface: np.ndarray,
                            foot: np.ndarray, catalogue: np.ndarray,
                            retain_fraction: float = RETAIN_FRACTION,
                            corridor_px: float | None = None,
                            retain_score_surface: np.ndarray | None = None):
    """Fixed-mass BSTP candidate from parent dots.  Returns (mask, diag).

    corridor_px (experiment 2): if set, new dots must also lie within
    corridor_px of a retained dot (strand-continuation habitat) while still
    > 3 px from every parent dot."""
    from .mass import unique_credit

    parent = np.asarray(parent_dots, dtype=bool) & foot
    n_parent = int(parent.sum())
    n_keep = int(round(retain_fraction * n_parent))
    n_new = n_parent - n_keep

    u, pts = unique_credit(parent)
    if retain_score_surface is not None:
        # Experiment 3 retention: keep the best-centred parent dots (highest
        # edge response at the dot); unique_credit is kept as a diagnostic.
        score = np.asarray(retain_score_surface, dtype=np.float32)[
            pts[:, 0], pts[:, 1]].astype(np.float64)
        score = score + 1e-6 * u  # deterministic near-tie break toward coverage
    else:
        score = u
    order = np.argsort(-score, kind="stable")  # ties: row-major (pts order)
    keep_idx = order[:n_keep]
    retained = np.zeros(parent.shape, dtype=bool)
    retained[pts[keep_idx, 0], pts[keep_idx, 1]] = True

    d_cat = ndi.distance_transform_edt(~(np.asarray(catalogue, dtype=bool) & foot))
    d_parent = ndi.distance_transform_edt(~parent)
    eligible = (foot & (d_cat >= MIN_DCAT_PX) & (d_parent > MIN_DPARENT_PX)
                & ~retained)
    if corridor_px is not None:
        d_ret = ndi.distance_transform_edt(~retained)
        eligible &= d_ret <= corridor_px
    # Suppression blocked-set starts as the 2.8 px disks of retained dots so
    # new dots also respect the lineage spacing against retained dots.
    blocked = ndi.distance_transform_edt(~retained) <= SUPPRESSION_PX
    new_dots = greedy_surface_dots(surface, eligible, blocked, n_new)

    cand = retained | new_dots
    diag = {
        "n_parent": n_parent, "n_retained": int(retained.sum()),
        "n_new": int(new_dots.sum()), "n_candidate": int(cand.sum()),
        "retain_fraction": retain_fraction,
        "unique_credit_retained_min": float(u[keep_idx].min()) if n_keep else None,
        "unique_credit_dropped_max": float(u[order[n_keep]].max())
        if n_keep < len(u) else None,
        "new_dot_surface_min": float(surface[new_dots].min()) if n_new else None,
        "new_dot_surface_median": float(np.median(surface[new_dots])) if n_new else None,
        "eligible_px": int(eligible.sum()),
        "min_dcat_new_px": float(d_cat[new_dots].min()) if n_new else None,
        "min_dparent_new_px": float(d_parent[new_dots].min()) if n_new else None,
    }
    return cand, diag
