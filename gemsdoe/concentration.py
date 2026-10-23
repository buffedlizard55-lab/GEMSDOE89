"""CONCENTRATION axis: km-block mass reallocation at fixed dot count.

The question this module answers
--------------------------------
Holding the dot count (37,654), the catalogue clearance, the within-block
placement rule and the parent's suppression radius fixed, does moving 10-20 %
of R0's dots between 5 km blocks -- out of blocks with the *fewest* known
faults and into blocks with the *most* known faults -- raise DTI?

Why the prior is known-fault density and not the parent's own ranking
---------------------------------------------------------------------
`CONCENTRATION` in brief v2 is "move 10-20 % of dots from the lowest-prior
km-scale blocks to the highest-prior ones".  The only "prior" already spent on
this axis in the fleet (GEMSDOE84, `conc5km-t25/t50`) is the *parent's own*
per-dot gain surface averaged over a block: a self-referential quantity, since
R0's dots are by construction where that surface is high.  This module uses an
**independent** structural prior instead: the density of catalogued
(USGS/INGENIOUS) faults per block.  MEASURED on R0: the correlation between
R0's 5 km block density and catalogue block density is **r = 0.040**, and
**37.7 %** of R0's 37,654 dots sit in the 858 blocks that contain *no*
catalogued fault at all -- so block-scale allocation is almost free of the
prior, which is what makes this a real experiment rather than a re-shuffle.
New-fault truth "includes newly mapped geometry of existing systems" and can
lie within 300 m of known traces (organizer forum), which is the mechanism the
arm bets on; the same geometry is what makes the prior dangerous (see the
mechanism card's confounders).

Why placement needs an explicit rule
------------------------------------
R0 is a maximal 2.8 px packing of `h19_5` outside the catalogue collar, so the
field is saturated: only **201** `h19_5` pixels in the whole grid are >= 2.8 px
from an R0 dot and >= 3 px from the catalogue.  A pure "same field, same
rules" reallocation is therefore geometrically impossible above 201 dots, as
in GEMSDOE84's CONCENTRATION session.  Added dots are placed on an explicit
**structural edge score** `q` built from the pinned potential-field bands
(Sobel gradient magnitude of RTP magnetics, band 2, and isostatic gravity,
band 13, each robust-scaled and averaged).

`q` is a placement rule, not the axis: the *same* rule fills whichever block
stratum the arm names.  That is what makes the toward/away pair a controlled
contrast -- both arms use one detector, one spacing, one clearance, one count,
and differ only in which blocks receive the mass.  Single-feature AUC of `q`
against catalogue membership is ~0.55, i.e. ordinary for this data (best single
band 0.57); it is NOT used as evidence, only as a placement device.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

BLOCK_PX = 50                    # 50 px x 100 m = 5 km blocks
MIN_FOOT_FRAC = 0.5              # a block is eligible only if >= 50 % inside the footprint
MIN_SEP_PX = 2.8                 # the parent's own dot-suppression radius (dot_thin r_min)
CATALOGUE_CLEARANCE_PX = 3.0     # hard constraint 4 (brief section 4)
KERNEL_RADIUS_PX = 3.0


# --------------------------------------------------------------------------- #
# structural edge score used for placement (NOT a model of truth)
# --------------------------------------------------------------------------- #
def gradient_magnitude(band: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Robust-scaled Sobel gradient magnitude of one potential-field band.

    The competition stack carries -3.4e38 nodata sentinels inside the footprint
    (IRREGULARITIES item 3), so non-finite *and* <= -1e30 pixels are rejected
    before scaling.  Scaling is (p99 - p1) of the finite values, so the result
    is dimensionless and bands of different units can be averaged.
    """
    a = np.asarray(band, dtype=np.float64)
    bad = ~np.isfinite(a) | (a <= -1e30)
    a = np.where(bad, np.nan, a)
    fin = a[np.isfinite(a)]
    if fin.size == 0:
        raise ValueError("band has no finite values")
    med = float(np.median(fin))
    scale = float(np.percentile(fin, 99) - np.percentile(fin, 1))
    if not np.isfinite(scale) or scale == 0:
        scale = float(fin.std()) or 1.0
    z = np.nan_to_num((a - med) / scale, nan=0.0, posinf=0.0, neginf=0.0)
    gx = ndi.sobel(z, axis=1, mode="nearest")
    gy = ndi.sobel(z, axis=0, mode="nearest")
    g = np.hypot(gx, gy)
    g = np.where(footprint, g, 0.0)
    ref = float(np.percentile(g[footprint], 99.5)) if footprint.any() else 1.0
    return g / (ref if ref > 0 else 1.0)


def structural_edge_score(bands: dict, footprint: np.ndarray,
                          smooth_px: int = 5) -> np.ndarray:
    """Mean of the per-band gradient magnitudes, smoothed to lineament scale.

    `bands` maps label -> 2-D array.  The `smooth_px = 5` (500 m) box mean
    damps single-pixel spikes -- airborne survey seams and grid-edge artefacts
    are the main non-geological source of huge gradients -- and slightly
    *raises* agreement with fault evidence: measured AUC against catalogue
    membership 0.5448 raw -> 0.5479 smoothed, and the share of the top 1 % of
    pixels lying on/near the corroborated `h19_5` ridge field 9.0 % -> 11.1 %
    (base rate 7.2 %).  It is a placement device, not a model of truth.
    """
    if not bands:
        raise ValueError("no bands supplied")
    acc = np.zeros(np.asarray(footprint).shape, dtype=np.float64)
    for _label, band in sorted(bands.items()):
        acc += gradient_magnitude(band, footprint)
    q = acc / len(bands)
    if smooth_px and smooth_px > 1:
        q = ndi.uniform_filter(q, size=int(smooth_px), mode="nearest")
    return np.asarray(q, dtype=np.float32)


# --------------------------------------------------------------------------- #
# block prior and strata
# --------------------------------------------------------------------------- #
def block_prior(catalogue_mask: np.ndarray, footprint: np.ndarray,
                block_px: int = BLOCK_PX, min_foot_frac: float = MIN_FOOT_FRAC):
    """Per-block known-fault density with full-grid (edge-inclusive) blocks.

    Returns (prior, eligible, n_foot_px, n_cat_px) as flat block arrays of
    length ny*nx.  Blocks are counted over the whole grid, partial edge blocks
    included, so no dot can fall outside every block.
    """
    cat = np.asarray(catalogue_mask, dtype=bool) & footprint
    foot = np.asarray(footprint, dtype=bool)
    h, w = foot.shape
    ny, nx = (h + block_px - 1) // block_px, (w + block_px - 1) // block_px
    bid = block_id(foot.shape, block_px)
    n = ny * nx
    n_foot = np.bincount(bid[foot], minlength=n).astype(np.float64)
    n_cat = np.bincount(bid[cat], minlength=n).astype(np.float64)
    eligible = n_foot >= min_foot_frac * block_px * block_px
    prior = np.where(eligible, n_cat / np.maximum(n_foot, 1.0), np.nan)
    return prior, eligible, n_foot, n_cat


def expand_blocks(block_mask: np.ndarray, shape: tuple[int, int],
                  block_px: int = BLOCK_PX) -> np.ndarray:
    """Expand a flat per-block boolean vector to full grid resolution."""
    h, w = shape
    ny, nx = (h + block_px - 1) // block_px, (w + block_px - 1) // block_px
    bm = np.asarray(block_mask, dtype=bool).reshape(ny, nx)
    full = np.zeros((ny * block_px, nx * block_px), dtype=bool)
    full[:] = np.kron(bm, np.ones((block_px, block_px), dtype=bool))
    return full[:h, :w]


def block_id(image_shape: tuple[int, int], block_px: int = BLOCK_PX) -> np.ndarray:
    """Flat block index per pixel (int32, row-major, edge-inclusive grid)."""
    h, w = image_shape
    nx = (w + block_px - 1) // block_px
    rows = (np.arange(h, dtype=np.int32) // block_px)[:, None]
    cols = (np.arange(w, dtype=np.int32) // block_px)[None, :]
    return (rows * np.int32(nx) + cols).astype(np.int64)


def strata(prior: np.ndarray, eligible: np.ndarray, low_quantile: float = 0.75) -> dict:
    """Name the empty-prior stratum and the top-quartile stratum.

    `donor`/"low"  : eligible blocks with zero catalogued faults (the lowest
                     possible value of the prior, not a quantile -- it is a
                     geologically crisp class: *no* mapped fault in 25 km^2).
    `recipient`/"high": eligible blocks at/above the `low_quantile` percentile
                     of the prior over eligible blocks.
    The two sets are disjoint by construction.
    """
    vals = prior[eligible]
    if vals.size == 0:
        raise ValueError("no eligible blocks")
    val_fake = np.where(np.isfinite(prior), prior, -1.0)
    zeros = eligible & (val_fake == 0.0)
    hi_cut = float(np.percentile(vals, 100.0 * low_quantile))
    # a zero-inflated prior can put the 75th percentile exactly at 0; the
    # recipient stratum must still be a *positive*-prior set, otherwise it
    # would swallow the donor blocks.
    hi_cut = max(hi_cut, float(np.min(vals[vals > 0])) if (vals > 0).any() else hi_cut)
    high = eligible & np.isfinite(prior) & (prior > 0) & (prior >= hi_cut)
    if (zeros & high).any():
        raise RuntimeError("strata overlap")
    return {
        "zero": zeros, "high": high,
        "zero_blocks": int(zeros.sum()), "high_blocks": int(high.sum()),
        "high_cut": hi_cut, "eligible_blocks": int(eligible.sum()),
        "prior_median": float(np.median(vals)), "prior_p90": float(np.percentile(vals, 90.0)),
    }


# --------------------------------------------------------------------------- #
# donor selection and recipient placement
# --------------------------------------------------------------------------- #
def select_donor_dots(dots: np.ndarray, region: np.ndarray, rank: np.ndarray,
                      n: int, rng: np.random.Generator) -> np.ndarray:
    """The `n` donor dots inside `region` with the smallest `rank`.

    `rank` is the parent's own metric-derived per-dot value
    (``gemsdoe.mass.unique_credit``: the kernel credit a dot would uniquely
    claim under a flat truth prior), so the arm gives up the cheapest mass
    first -- the same convention the MASS and GEMSDOE84 CONCENTRATION arms use.
    Ties are broken by a seeded uniform draw (deterministic for a fixed seed).
    """
    dots = np.asarray(dots, dtype=bool)
    ys, xs = np.nonzero(dots & np.asarray(region, dtype=bool))
    if ys.size < n:
        raise ValueError(f"donor region holds {ys.size} dots, need {n}")
    vals = np.asarray(rank, dtype=np.float64)[ys, xs]
    order = np.lexsort((rng.random(ys.size), vals))
    return np.column_stack([ys[order[:n]], xs[order[:n]]]).astype(np.int32)


def legal_sites(footprint: np.ndarray, near_dots: np.ndarray, region: np.ndarray,
                clearance: np.ndarray, min_sep: float = MIN_SEP_PX,
                clearance_px: float = CATALOGUE_CLEARANCE_PX) -> np.ndarray:
    """Pixels in `region` legal for a new dot: separation, clearance, free."""
    return (np.asarray(region, dtype=bool) & np.asarray(footprint, dtype=bool)
            & (np.asarray(clearance) >= clearance_px) & (~np.asarray(near_dots, dtype=bool)))


def greedy_place(score: np.ndarray, legal: np.ndarray, n: int,
                 min_sep: float = MIN_SEP_PX) -> np.ndarray:
    """Pick `n` sites by descending `score` with Euclidean spacing >= min_sep.

    Deterministic: ties in `score` resolve by row-major order (lexsort is
    stable on (score, -y, -x) after the negative sort).  Accepted sites
    suppress a disc of radius `min_sep`, so the result matches the parent's own
    suppression geometry instead of stacking mass the max-operator already
    covers.
    """
    legal = np.asarray(legal, dtype=bool)
    ys, xs = np.nonzero(legal)
    if ys.size < n:
        raise ValueError(f"only {ys.size} legal sites for {n} dots")
    sc = np.asarray(score, dtype=np.float64)[ys, xs]
    order = np.lexsort((xs, ys, -sc))
    blocked = legal.copy()
    h, w = legal.shape
    out = []
    r_int = int(np.ceil(min_sep))
    sq = min_sep * min_sep - 1e-9
    for k in order:
        y, x = int(ys[k]), int(xs[k])
        if not blocked[y, x]:
            continue
        out.append((y, x))
        if len(out) >= n:
            break
        y0, y1 = max(0, y - r_int), min(h, y + r_int + 1)
        x0, x1 = max(0, x - r_int), min(w, x + r_int + 1)
        sub = blocked[y0:y1, x0:x1]
        yy, xx = np.nonzero(sub)
        if yy.size:
            dy = yy + y0 - y
            dx = xx + x0 - x
            m = (dy * dy + dx * dx) <= sq
            sub[yy[m], xx[m]] = False
    if len(out) < n:
        raise ValueError(f"greedy placement produced {len(out)} of {n} dots")
    return np.array(out, dtype=np.int32)


# --------------------------------------------------------------------------- #
# the build
# --------------------------------------------------------------------------- #
def block_density_cv(dots: np.ndarray, footprint: np.ndarray,
                     block_px: int = BLOCK_PX) -> float:
    """CV of dot density over blocks (report-only; eligible blocks only)."""
    prior, eligible, n_foot, _ = block_prior(np.zeros_like(dots, dtype=bool),
                                             footprint, block_px)
    bid = block_id(dots.shape, block_px)
    n_dot = np.bincount(bid[np.asarray(dots, dtype=bool)], minlength=prior.size).astype(np.float64)
    dens = n_dot[eligible] / np.maximum(n_foot[eligible], 1.0)
    if dens.size == 0 or dens.mean() == 0:
        return float("nan")
    return float(dens.std() / dens.mean())


def build(dots: np.ndarray, footprint: np.ndarray, catalogue_mask: np.ndarray,
          edge_score: np.ndarray, dot_rank: np.ndarray, fraction: float,
          direction: str, rng: np.random.Generator,
          block_px: int = BLOCK_PX, low_quantile: float = 0.75) -> tuple[np.ndarray, dict]:
    """Return (variant dot mask, stats).  Count is preserved exactly.

    direction='toward': donors = zero-catalogue blocks, recipients = top-quartile.
    direction='away'  : donors = top-quartile blocks, recipients = zero-catalogue.
    """
    if direction not in ("toward", "away"):
        raise ValueError(f"unknown direction {direction!r}")
    dots = np.asarray(dots, dtype=bool)
    foot = np.asarray(footprint, dtype=bool)
    cat = np.asarray(catalogue_mask, dtype=bool) & foot
    n_dots = int(dots.sum())
    n_move = int(round(float(fraction) * n_dots))
    if not 1 <= n_move < n_dots:
        raise ValueError("fraction outside (0, 1)")

    prior, eligible, n_foot, n_cat = block_prior(cat, foot, block_px)
    st = strata(prior, eligible, low_quantile)
    donor_blocks = st["zero"] if direction == "toward" else st["high"]
    recip_blocks = st["high"] if direction == "toward" else st["zero"]
    donor_region = expand_blocks(donor_blocks, dots.shape, block_px)
    recip_region = expand_blocks(recip_blocks, dots.shape, block_px)
    if (donor_region & recip_region).any():
        raise RuntimeError("donor and recipient regions overlap")

    donor_pts = select_donor_dots(dots, donor_region, dot_rank, n_move, rng)
    surviving = dots.copy()
    surviving[donor_pts[:, 0], donor_pts[:, 1]] = False

    clearance = ndi.distance_transform_edt(~cat)
    sep = ndi.distance_transform_edt(~surviving)
    legal = (recip_region & foot & (clearance >= CATALOGUE_CLEARANCE_PX)
             & (sep >= MIN_SEP_PX) & (~surviving))
    added_pts = greedy_place(edge_score, legal, n_move)

    variant = surviving.copy()
    variant[added_pts[:, 0], added_pts[:, 1]] = True
    assert int(variant.sum()) == n_dots, "count not preserved"
    if (variant & cat).any():
        raise RuntimeError("catalogue pixels carry mass")
    # The >= 3 px rule binds the NEW dots.  R0 itself inherits 2,171 dots at
    # 2 < d_cat <= 3 from its own d_cat > 2 prune; those are the PRUNE axis's
    # business, not this one's, and this arm neither adds nor removes them
    # (unless a donor block happens to hold one -- reported below).
    if (clearance[added_pts[:, 0], added_pts[:, 1]] < CATALOGUE_CLEARANCE_PX - 1e-9).any():
        raise RuntimeError("catalogue clearance violated by a new dot")

    bid = block_id(dots.shape, block_px)
    dens_before = np.bincount(bid[dots], minlength=prior.size) / np.maximum(n_foot, 1.0)
    dens_after = np.bincount(bid[variant], minlength=prior.size) / np.maximum(n_foot, 1.0)
    disp, _ = cKDTree(added_pts).query(donor_pts)

    stats = {
        "direction": direction,
        "fraction_requested": float(fraction),
        "n_dots": n_dots,
        "n_moved": int(n_move),
        "pct_changed": 100.0 * n_move / n_dots,
        "pct_symmetric_diff": 200.0 * n_move / n_dots,
        "block_px": int(block_px),
        "block_km": block_px / 10.0,
        "strata": {k: v for k, v in st.items() if not isinstance(v, np.ndarray)},
        "donor_blocks": int(donor_blocks.sum()),
        "recipient_blocks": int(recip_blocks.sum()),
        "dots_in_donor_before": int((dots & donor_region).sum()),
        "dots_in_donor_after": int((variant & donor_region).sum()),
        "dots_in_recipient_before": int((dots & recip_region).sum()),
        "dots_in_recipient_after": int((variant & recip_region).sum()),
        "dots_in_zero_blocks_before": int((dots & expand_blocks(st["zero"], dots.shape, block_px)).sum()),
        "dots_in_zero_blocks_after": int((variant & expand_blocks(st["zero"], dots.shape, block_px)).sum()),
        "density_cv_5km_before": block_density_cv(dots, foot, 50),
        "density_cv_5km_after": block_density_cv(variant, foot, 50),
        "density_cv_1km_before": block_density_cv(dots, foot, 10),
        "density_cv_1km_after": block_density_cv(variant, foot, 10),
        "cv_definition": "std/mean of dots per footprint pixel over blocks with footprint >= 50 % of area (edge-inclusive grid)",
        "prior_vs_r0_density_corr_before": _corr(dens_before[eligible], prior[eligible]),
        "prior_vs_r0_density_corr_after": _corr(dens_after[eligible], prior[eligible]),
        "mean_displacement_px": float(disp.mean()),
        "median_displacement_px": float(np.median(disp)),
        "removed_rank_mean": float(dot_rank[donor_pts[:, 0], donor_pts[:, 1]].mean()),
        "parent_rank_mean": float(dot_rank[dots].mean()),
        "removed_dcat_median_px": float(np.median(clearance[donor_pts[:, 0], donor_pts[:, 1]])),
        "removed_frac_within_3px_catalogue": float((clearance[donor_pts[:, 0], donor_pts[:, 1]] < 3.0).mean()),
        "added_edge_score_mean": float(edge_score[added_pts[:, 0], added_pts[:, 1]].mean()),
        "parent_edge_score_mean": float(edge_score[dots].mean()),
        "added_edge_score_p10": float(np.percentile(edge_score[added_pts[:, 0], added_pts[:, 1]], 10)),
        "min_sep_added_px": float(_nn(added_pts)),
        "min_clearance_added_px": float(clearance[added_pts[:, 0], added_pts[:, 1]].min()),
        "min_clearance_all_px": float(clearance[variant].min()),
        "dots_within_3px_catalogue_before": int((clearance[dots] < 3.0).sum()),
        "dots_within_3px_catalogue_after": int((clearance[variant] < 3.0).sum()),
    }
    # how much of the added mass actually left its donor block
    stats["added_outside_donor_region"] = int((variant & ~donor_region & ~dots).sum())
    return variant, stats


def _corr(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 3 or a[m].std() == 0 or b[m].std() == 0:
        return float("nan")
    return float(np.corrcoef(a[m], b[m])[0, 1])


def _nn(pts: np.ndarray) -> float:
    if len(pts) < 2:
        return float("nan")
    d, _ = cKDTree(pts).query(pts, k=2)
    return float(d[:, 1].min())


def predicted_delta(n_moved: int, direction: str, k_bar: float = 2.5,
                    denom: float = 2.0e4, dp_central: float = 0.02,
                    dp_hi: float = 0.06, null_band: float = 0.010) -> dict:
    """MODEL band for a block reallocation, from the DTI algebra.

    With the mass S fixed, dDTI = [(1 - 0.2*DTI)*dT + 0.2*DTI*dM]/D, and for a
    unit dot that lands within the kernel of a 1-px trace dM ~ dT ~ k_bar.  So a
    moved dot is worth `k_bar*(0.944 + 0.0556)/D` when it hits truth and ~0
    when it misses:

        dDTI ~ n * k_bar * (p_recipient - p_donor) / D

    `D = 2.0e4` is measured from the one recorded collar step (removing 2,545
    masked-collar dots 2 < d_cat <= 3 bought +0.0070: D = 0.2778*509/0.0070).
    `k_bar = 2.5` is the credit of a unit dot sitting on a 1-px line (two
    neighbours at k=1, two at k=0.67, two at k=0.33).  The hit-rate difference
    `dp` is the unknown: 0.00 is the null (prior uninformative), 0.02 is the
    central bet and 0.06 the strong-prior case.
    """
    sign = 1.0 if direction == "toward" else -1.0
    per_unit_dp = n_moved * k_bar / denom
    out = {"n_moved": int(n_moved), "k_bar": k_bar, "denom": denom,
           "per_unit_hit_rate_difference": per_unit_dp}
    for name, dp in (("null_dp_0p00", 0.0), ("central_dp_0p02", dp_central),
                     ("strong_dp_0p06", dp_hi)):
        out[name] = sign * per_unit_dp * dp
    out["band"] = [sign * -null_band, sign * (per_unit_dp * dp_hi + null_band)]
    out["band"] = [min(out["band"]), max(out["band"])]
    out["central"] = out["central_dp_0p02"]
    out["note"] = ("a live |change| < 0.01 is no evidence; the central case sits "
                   "at the threshold, so this axis only reads out if it is large")
    return out
