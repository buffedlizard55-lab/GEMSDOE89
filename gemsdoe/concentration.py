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

import heapq

import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

from . import mass, metric

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


# ---------------------------------------------------------------------------
# 2 km H19-supported exact-marginal family (arena/0a75dd63)
# ---------------------------------------------------------------------------
ANCHOR_D = 18734.44  # recorded upstream live-anchor MODEL scale; not a receipt


def _kernel(distance):
    return metric.kernel_weight(distance, KERNEL_RADIUS_PX)


def _offsets(radius=KERNEL_RADIUS_PX):
    """All integer offsets inside the kernel, including (0, 0)."""
    r = int(np.floor(radius))
    return [
        (dy, dx, float(np.hypot(dy, dx)), 1.0 - float(np.hypot(dy, dx)) / radius)
        for dy in range(-r, r + 1)
        for dx in range(-r, r + 1)
        if np.hypot(dy, dx) < radius
    ]


def make_block_prior(
    catalogue_mask,
    footprint,
    parent_dots,
    candidate_mask,
    block_px=20,
    source_quantile=0.50,
    target_quantile=0.75,
):
    """Return source/target rasters and an audit of the catalogue block prior.

    Blocks with <=50% footprint coverage and the incomplete right/bottom grid
    fringe are frozen, matching ``mass.block_density_cv``.  Prior units are
    catalogue pixels per 1,000 footprint pixels.  Quantile ties are retained,
    so a zero-heavy bottom half can contain more than half of eligible blocks.
    """
    if not 0 <= source_quantile < target_quantile <= 1:
        raise ValueError("require 0 <= source_quantile < target_quantile <= 1")
    parent_dots = np.asarray(parent_dots, dtype=bool)
    footprint = np.asarray(footprint, dtype=bool)
    catalogue_mask = np.asarray(catalogue_mask, dtype=bool) & footprint
    candidate_mask = np.asarray(candidate_mask, dtype=bool) & footprint
    h, w = parent_dots.shape
    bh, bw = h // block_px, w // block_px
    if bh == 0 or bw == 0:
        raise ValueError("block is larger than the raster")
    sl = np.s_[: bh * block_px, : bw * block_px]

    def sums(a):
        return a[sl].reshape(bh, block_px, bw, block_px).sum(axis=(1, 3))

    area = sums(footprint)
    n_cat = sums(catalogue_mask)
    n_parent = sums(parent_dots)
    n_candidate = sums(candidate_mask)
    active = area > 0.5 * block_px * block_px
    prior = np.full(area.shape, np.nan, dtype=np.float64)
    np.divide(1000.0 * n_cat, area, out=prior, where=active & (area > 0))

    source_eligible = active & (n_parent > 0)
    target_eligible = active & (n_candidate > 0)
    if not source_eligible.any() or not target_eligible.any():
        raise ValueError("empty source- or target-eligible block population")
    source_cut = float(np.quantile(prior[source_eligible], source_quantile))
    target_cut = float(np.quantile(prior[target_eligible], target_quantile))
    source_blocks = source_eligible & (prior <= source_cut)
    target_blocks = target_eligible & (prior >= target_cut)
    if (source_blocks & target_blocks).any():
        raise ValueError("source and target blocks overlap; no concentration contrast")
    if not source_blocks.any() or not target_blocks.any():
        raise ValueError("empty source or target block selection")

    def expand(blocks, fill=False, dtype=None):
        out = np.full(parent_dots.shape, fill, dtype=dtype or blocks.dtype)
        out[sl] = np.repeat(np.repeat(blocks, block_px, axis=0), block_px, axis=1)
        return out

    source_mask = expand(source_blocks) & footprint
    target_mask = expand(target_blocks) & footprint
    prior_raster = expand(prior, fill=np.nan, dtype=np.float64)
    prior_raster[~footprint] = np.nan

    stats = {
        "block_px": int(block_px),
        "block_km": block_px / 10.0,
        "prior": "1000 * catalogue_pixels / footprint_pixels; known-fault prior, not test truth",
        "source_quantile": source_quantile,
        "target_quantile": target_quantile,
        "source_cut_per_1000px": source_cut,
        "target_cut_per_1000px": target_cut,
        "active_blocks": int(active.sum()),
        "source_eligible_blocks": int(source_eligible.sum()),
        "target_eligible_blocks": int(target_eligible.sum()),
        "source_blocks": int(source_blocks.sum()),
        "target_blocks": int(target_blocks.sum()),
        "source_parent_dots": int((parent_dots & source_mask).sum()),
        "target_parent_dots": int((parent_dots & target_mask).sum()),
        "target_candidate_pixels": int((candidate_mask & target_mask).sum()),
        "source_block_prior_mean": float(np.mean(prior[source_blocks])),
        "target_block_prior_mean": float(np.mean(prior[target_blocks])),
        "active_block_prior_mean": float(np.mean(prior[active])),
        "source_parent_prior_mean": float(np.mean(prior_raster[parent_dots & source_mask])),
        "target_parent_prior_mean": float(np.mean(prior_raster[parent_dots & target_mask])),
        "quantile_ties_retained": True,
        "frozen_edge_rule": "incomplete right/bottom fringe and blocks with <=50% footprint are unchanged",
    }
    return source_mask, target_mask, prior_raster, stats


def marginal_rankings(truth, dots, candidate_points, radius=KERNEL_RADIUS_PX):
    """Exact one-dot removal/addition DTI deltas for a binary prediction.

    Returns parent points and removal deltas, candidate addition deltas, and
    the base T/S/M/G/D components.  Addition candidates must not already be
    dots.  Equal-distance prediction ties cause zero T loss when one tied dot
    is removed, exactly matching the max operator.
    """
    truth = np.asarray(truth, dtype=bool)
    dots = np.asarray(dots, dtype=bool)
    if truth.shape != dots.shape:
        raise ValueError("truth and dots must have the same shape")
    pts = np.argwhere(dots).astype(np.int32)
    truth_pts = np.argwhere(truth).astype(np.int32)
    candidates = np.asarray(candidate_points, dtype=np.int32).reshape(-1, 2)
    if len(candidates) and bool(dots[candidates[:, 0], candidates[:, 1]].any()):
        raise ValueError("addition candidates must be absent from the parent")
    n, g = len(pts), len(truth_pts)
    s = float(n)
    truth_tree = cKDTree(truth_pts) if g else None

    if g:
        if n:
            pred_tree = cKDTree(pts)
            distances, indices = pred_tree.query(truth_pts, k=2 if n > 1 else 1)
            if n == 1:
                d1 = distances
                i1 = indices
                d2 = np.full(g, np.inf)
            else:
                d1, d2 = distances[:, 0], distances[:, 1]
                i1 = indices[:, 0]
            current_credit = _kernel(d1)
            t = float(current_credit.sum())
            unique = d2 > d1 + 1e-9
            unique_credit = np.bincount(
                i1[unique], weights=current_credit[unique], minlength=n
            ).astype(np.float64)
            d_truth_at_pred = truth_tree.query(pts, k=1)[0]
            m_each = _kernel(d_truth_at_pred)
        else:
            current_credit = np.zeros(g, dtype=np.float64)
            t = 0.0
            unique_credit = np.zeros(0, dtype=np.float64)
            m_each = np.zeros(0, dtype=np.float64)
        m = float(m_each.sum())
    else:
        current_credit = np.zeros(0, dtype=np.float64)
        t = m = 0.0
        unique_credit = np.zeros(n, dtype=np.float64)
        m_each = np.zeros(n, dtype=np.float64)

    d = 0.2 * t + 0.2 * (s - m) + 0.8 * g
    if d <= 0:
        raise ValueError("undefined DTI scene: no truth and no prediction mass")
    base = t / d
    d_removed = d - 0.2 * unique_credit - 0.2 * (1.0 - m_each)
    remove_delta = (t - unique_credit) / d_removed - base

    add_truth_credit = np.zeros(len(candidates), dtype=np.float64)
    if len(candidates) and g:
        truth_index = np.full(truth.shape, -1, dtype=np.int32)
        truth_index[truth_pts[:, 0], truth_pts[:, 1]] = np.arange(g, dtype=np.int32)
        h, w = truth.shape
        for dy, dx, _distance, k in _offsets(radius):
            q = candidates + np.array([dy, dx], dtype=np.int32)
            inside = (q[:, 0] >= 0) & (q[:, 0] < h) & (q[:, 1] >= 0) & (q[:, 1] < w)
            ci = np.flatnonzero(inside)
            if not len(ci):
                continue
            ti = truth_index[q[ci, 0], q[ci, 1]]
            valid = ti >= 0
            if valid.any():
                ci_valid = ci[valid]
                gain = np.maximum(0.0, k - current_credit[ti[valid]])
                add_truth_credit[ci_valid] += gain
        m_add = _kernel(truth_tree.query(candidates, k=1)[0])
    else:
        m_add = np.zeros(len(candidates), dtype=np.float64)
    d_added = d + 0.2 * add_truth_credit + 0.2 * (1.0 - m_add)
    add_delta = (t + add_truth_credit) / d_added - base

    return {
        "points": pts,
        "remove_delta": remove_delta,
        "remove_unique_truth_credit": unique_credit,
        "remove_m": m_each,
        "candidate_points": candidates,
        "current_truth_credit": current_credit,
        "add_delta": add_delta,
        "add_truth_credit": add_truth_credit,
        "add_m": m_add,
        "base": {"T": t, "S": s, "M": m, "G": float(g), "D": d, "DTI": base},
    }


def _greedy_on_truth_from_ranking(truth, candidates, ranking, n_select, seed):
    """Lazy exact greedy additions for candidates that lie on surrogate truth.

    Coverage gains only decrease as accepted dots raise current kernel credit.
    A max-heap of stale gains therefore supplies upper bounds: a popped candidate
    is re-scored until its current gain equals its bound, at which point it is
    the exact greedy maximizer.  Since every candidate has m=1, exact DTI gain
    is monotone in this coverage gain at each step.
    """
    candidates = np.asarray(candidates, dtype=np.int32).reshape(-1, 2)
    if len(candidates) and not truth[candidates[:, 0], candidates[:, 1]].all():
        raise ValueError("greedy_on_truth requires every candidate to be on truth")
    if not 0 <= n_select <= len(candidates):
        raise ValueError("invalid greedy selection count")
    current_credit = ranking["current_truth_credit"].copy()
    truth_index = np.full(truth.shape, -1, dtype=np.int32)
    truth_points = np.argwhere(truth).astype(np.int32)
    truth_index[truth_points[:, 0], truth_points[:, 1]] = np.arange(len(truth_points))
    neighbor_ids = [[] for _ in range(len(candidates))]
    neighbor_weights = [[] for _ in range(len(candidates))]
    h, w = truth.shape
    for dy, dx, _distance, k in _offsets():
        q = candidates + np.array([dy, dx], dtype=np.int32)
        inside = (q[:, 0] >= 0) & (q[:, 0] < h) & (q[:, 1] >= 0) & (q[:, 1] < w)
        ci = np.flatnonzero(inside)
        if not len(ci):
            continue
        ti = truth_index[q[ci, 0], q[ci, 1]]
        valid = ti >= 0
        for c, t in zip(ci[valid], ti[valid]):
            neighbor_ids[int(c)].append(int(t))
            neighbor_weights[int(c)].append(k)
    neighbor_ids = [np.asarray(v, dtype=np.int32) for v in neighbor_ids]
    neighbor_weights = [np.asarray(v, dtype=np.float64) for v in neighbor_weights]

    def gain(i):
        ids = neighbor_ids[i]
        if not len(ids):
            return 0.0
        return float(np.maximum(0.0, neighbor_weights[i] - current_credit[ids]).sum())

    rng = np.random.default_rng(seed)
    tie = rng.random(len(candidates))
    heap = [(-float(g), float(tie[i]), i) for i, g in enumerate(ranking["add_truth_credit"])]
    heapq.heapify(heap)
    selected, gains, deltas = [], [], []
    t, d = ranking["base"]["T"], ranking["base"]["D"]
    while len(selected) < n_select:
        if not heap:
            raise RuntimeError("greedy heap exhausted before requested selection")
        negative_bound, _tie, i = heapq.heappop(heap)
        bound = -negative_bound
        current = gain(i)
        if current < bound - 1e-12:
            heapq.heappush(heap, (-current, float(tie[i]), i))
            continue
        # current <= bound always; equality means every other stale heap key is
        # an upper bound no greater than this candidate's current exact gain.
        selected.append(i)
        gains.append(current)
        deltas.append((t + current) / (d + 0.2 * current) - t / d)
        ids = neighbor_ids[i]
        if len(ids):
            current_credit[ids] = np.maximum(current_credit[ids], neighbor_weights[i])
        t += current
        d += 0.2 * current  # S and M both increase by one (m=1)
    return {
        "indices": np.asarray(selected, dtype=np.int32),
        "truth_credit": np.asarray(gains, dtype=np.float64),
        "exact_marginal_dti": np.asarray(deltas, dtype=np.float64),
    }


def greedy_on_truth_additions(truth, dots, candidate_points, n_select, seed=20261023):
    """Public tested wrapper for exact sequential on-truth greedy additions."""
    ranking = marginal_rankings(truth, dots, candidate_points)
    return _greedy_on_truth_from_ranking(
        np.asarray(truth, dtype=bool), candidate_points, ranking, n_select, seed
    )


def _dti_from_distances(truth, dots, distance_to_truth):
    distance_to_pred = ndi.distance_transform_edt(~dots)
    t = float(_kernel(distance_to_pred[truth]).sum())
    s = float(dots.sum())
    m = float(_kernel(distance_to_truth[dots]).sum())
    g = float(truth.sum())
    d = 0.2 * t + 0.2 * (s - m) + 0.8 * g
    return {"T": t, "S": s, "M": m, "G": g, "D": d, "DTI": t / d if d else 0.0}


def build_family(
    parent_dots,
    h19_mask,
    footprint,
    catalogue_mask,
    n_moves,
    block_px=20,
    seed=20261023,
    source_quantile=0.50,
    target_quantile=0.75,
):
    """Build nested fixed-count transfers; return ``(variants, audit)``.

    ``variants`` maps each requested move count to ``(mask, stats)``.  Source
    ranks are computed once on R0 and destinations are exact sequential greedy
    additions, so every lower-dose edit is an exact subset of the higher-dose
    edit.  No minimum-separation rule is imposed: local crowding is
    a measured consequence of concentration, while exact marginal ranking
    penalizes redundant destinations under the H19 surrogate.
    """
    parent_dots = np.asarray(parent_dots, dtype=bool)
    h19_mask = np.asarray(h19_mask, dtype=bool)
    footprint = np.asarray(footprint, dtype=bool)
    catalogue_mask = np.asarray(catalogue_mask, dtype=bool) & footprint
    if (parent_dots & ~h19_mask).any():
        raise ValueError("parent contains dots outside the H19 physical field")
    moves = sorted(set(int(n) for n in n_moves))
    n_dots = int(parent_dots.sum())
    if not moves or moves[0] < 1 or moves[-1] >= n_dots:
        raise ValueError("invalid move counts")

    d_cat = ndi.distance_transform_edt(~catalogue_mask)
    candidate_mask = (
        h19_mask & footprint & ~catalogue_mask & ~parent_dots
        & (d_cat >= CATALOGUE_CLEARANCE_PX)
    )
    source_mask, target_mask, prior_raster, block_stats = make_block_prior(
        catalogue_mask, footprint, parent_dots, candidate_mask,
        block_px=block_px, source_quantile=source_quantile,
        target_quantile=target_quantile,
    )
    source_pool = parent_dots & source_mask
    target_candidates = candidate_mask & target_mask
    if int(source_pool.sum()) < moves[-1] or int(target_candidates.sum()) < moves[-1]:
        raise ValueError("source or target pool is too small for the largest dose")

    # Off-catalogue H19 is a MODEL surrogate for line-like fault truth.
    truth = h19_mask & footprint & ~catalogue_mask
    parent_flat = np.flatnonzero(parent_dots.ravel())
    source_flat = np.flatnonzero(source_pool.ravel())
    source_indices = np.searchsorted(parent_flat, source_flat)
    candidate_points = np.argwhere(target_candidates).astype(np.int32)
    ranking = marginal_rankings(truth, parent_dots, candidate_points)
    rng = np.random.default_rng(seed)
    source_order = np.lexsort((
        rng.random(len(source_indices)),
        -ranking["remove_delta"][source_indices],
    ))
    target_sequence = _greedy_on_truth_from_ranking(
        truth, candidate_points, ranking, moves[-1], seed + 1
    )
    ranked_source_indices = source_indices[source_order]
    ranked_source_points = ranking["points"][ranked_source_indices]
    ranked_target_points = candidate_points[target_sequence["indices"]]
    distance_to_truth = ndi.distance_transform_edt(~truth)

    audit = {
        "source_mask": source_mask,
        "target_mask": target_mask,
        "candidate_mask": candidate_mask,
        "prior_raster": prior_raster,
        "truth": truth,
        "block_stats": block_stats,
        "base_h19_surrogate": ranking["base"],
        "seed": int(seed),
    }
    variants = {}
    previous_removed = previous_added = None
    for n_move in moves:
        chosen_source = ranked_source_indices[:n_move]
        removed_points = ranked_source_points[:n_move]
        added_points = ranked_target_points[:n_move]
        variant = parent_dots.copy()
        variant[removed_points[:, 0], removed_points[:, 1]] = False
        variant[added_points[:, 0], added_points[:, 1]] = True
        added = variant & ~parent_dots
        removed = parent_dots & ~variant
        if previous_removed is not None:
            if not (previous_removed <= removed).all() or not (previous_added <= added).all():
                raise AssertionError("dose series is not nested")
        previous_removed, previous_added = removed, added

        pct = 100.0 * n_move / n_dots
        pct_sym = 100.0 * int((variant ^ parent_dots).sum()) / n_dots
        added_min_dcat = float(d_cat[added].min())
        mask_gates = {
            "count_preserved": int(variant.sum()) == n_dots,
            "exact_removed_and_added": int(removed.sum()) == n_move and int(added.sum()) == n_move,
            "inside_footprint": not (variant & ~footprint).any(),
            "zero_catalogue_mass": not (variant & catalogue_mask).any(),
            "added_dcat_ge_3px": added_min_dcat >= CATALOGUE_CLEARANCE_PX,
            "all_mass_on_h19": not (variant & ~h19_mask).any(),
            "removed_from_low_prior": not (removed & ~source_mask).any(),
            "added_to_high_prior": not (added & ~target_mask).any(),
            "pct_changed_in_1_50": 1.0 <= pct <= 50.0 and 1.0 <= pct_sym <= 50.0,
            "differs_from_parent": not np.array_equal(variant, parent_dots),
        }
        if not all(mask_gates.values()):
            raise ValueError(f"concentration mask gate failed: {mask_gates}")

        surrogate = _dti_from_distances(truth, variant, distance_to_truth)
        nn_before = mass.nn_distances(parent_dots)
        nn_after = mass.nn_distances(variant)
        displacement = cKDTree(added_points).query(removed_points, k=1)[0]
        stats = {
            "n_dots": n_dots,
            "n_moved": n_move,
            "pct_changed": pct,
            "symmetric_difference": int((variant ^ parent_dots).sum()),
            "pct_symmetric_diff": pct_sym,
            "block_px": block_px,
            "block_km": block_px / 10.0,
            "source_prior_per_1000px": block_stats["source_cut_per_1000px"],
            "target_prior_per_1000px": block_stats["target_cut_per_1000px"],
            "removed_mean_block_prior": float(prior_raster[removed].mean()),
            "added_mean_block_prior": float(prior_raster[added].mean()),
            "removed_mean_exact_marginal_dti": float(ranking["remove_delta"][chosen_source].mean()),
            "removed_min_exact_marginal_dti": float(ranking["remove_delta"][chosen_source].min()),
            "added_mean_exact_marginal_dti": float(target_sequence["exact_marginal_dti"][:n_move].mean()),
            "added_min_exact_marginal_dti": float(target_sequence["exact_marginal_dti"][:n_move].min()),
            "removed_mean_unique_h19_credit": float(ranking["remove_unique_truth_credit"][chosen_source].mean()),
            "added_mean_new_h19_credit": float(target_sequence["truth_credit"][:n_move].mean()),
            "h19_surrogate_parent": ranking["base"],
            "h19_surrogate_variant": surrogate,
            "h19_surrogate_delta": surrogate["DTI"] - ranking["base"]["DTI"],
            "mean_displacement_px": float(displacement.mean()),
            "median_displacement_px": float(np.median(displacement)),
            "nn_median_before_px": float(np.median(nn_before)),
            "nn_median_after_px": float(np.median(nn_after)),
            "nn_lt_3px_before": int((nn_before < 3.0).sum()),
            "nn_lt_3px_after": int((nn_after < 3.0).sum()),
            "collar_lt3px_before": int((d_cat[parent_dots] < 3.0).sum()),
            "collar_lt3px_after": int((d_cat[variant] < 3.0).sum()),
            "added_min_catalogue_clearance_px": added_min_dcat,
            "mask_gates": mask_gates,
        }
        for km, bp in ((1, 10), (2, 20), (5, 50)):
            cv_before, nb = mass.block_density_cv(parent_dots, footprint, bp)
            cv_after, _ = mass.block_density_cv(variant, footprint, bp)
            stats[f"cv_{km}km_before"] = cv_before
            stats[f"cv_{km}km_after"] = cv_after
            stats[f"cv_{km}km_blocks"] = nb
        variants[n_move] = (variant, stats)
    return variants, audit


def predicted_delta_h19(n_move, h19_surrogate_delta, anchor_d=ANCHOR_D):
    """Additive MODEL sensitivity, charging the measured H19 counter-indicator.

    Block-prior scenarios are effective live credit per moved dot: -0.050,
    +0.025, +0.100, scaled by the recorded upstream anchor D.  The measured
    H19 surrogate delta is added unchanged as a structural coverage cost.  The
    two components have different truth sets, so this is deliberately an
    uncalibrated sensitivity band, not a confidence interval or live score.
    """
    credits = {"lo": -0.050, "central": 0.025, "hi": 0.100}
    out = {
        key: h19_surrogate_delta + n_move * value / anchor_d
        for key, value in credits.items()
    }
    out["effective_credit_per_moved_dot"] = credits
    out["h19_surrogate_counterindicator"] = h19_surrogate_delta
    out["anchor_d"] = anchor_d
    out["evidence_class"] = "MODEL"
    return out
