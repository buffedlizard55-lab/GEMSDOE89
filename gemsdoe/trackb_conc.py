"""TRACKB axis — Phase-2 strike-consistent trace inventory + a controlled,
count-preserving structural concentration of Parent R0.

Parent R0 = ``h33-h33-2-b2`` (37,654 unit-mass dots).  This module has two
linked products, both derived ONLY from R0 + the pinned rasters:

1. **Trace inventory (Phase-2 deliverable).**  R0's dots are linked into
   *chains* across gaps <= ``GAP_PX`` (400 m = one GeoDAWN Area-2 flight-line
   spacing, https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7).
   A chain is kept as a "trace" when its geodesic arc length >= 1 km and its
   sinuosity (arc / endpoint chord) <= ``MAX_SINUOSITY`` — i.e. it is long and
   strike-consistent.  Traces are ordered by their R0 dots' mean metric-derived
   unique credit (the parent's reconstructed ranking, ``gemsdoe.mass``), so the
   inventory is literally *built from R0's top-ranked dots*.  Each trace carries
   one evidence paragraph for a structural geologist (length, strike, band
   corroboration, nearest mapped fault, and an interpretation).

2. **Count-preserving structural concentration (Phase-1 probe).**  A controlled
   fraction (10 / 20 / 30 %) of R0's *off-trace* dots is relocated into a
   +-300 m (3 px) corridor around the traces, at mutual separation >= 2.8 px
   and catalogue clearance >= 3 px.  Total dot count S = 37,654 is held FIXED,
   so the DTI change isolates the structural prior (are long strike-consistent
   structures where test truth sits?) from any MASS effect.  The three doses are
   strictly nested: a single seeded off-trace permutation and a single ranked,
   separation-feasible placement list are truncated at n = 10/20/30 % of R0.

All randomness is seeded (default 20261023). Nothing here reads, logs in,
scrapes, or submits. Report-only instruments live in ``gemsdoe.proxy``.
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field

import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

from .mass import unique_credit

GAP_PX = 4.0            # 400 m step-over link distance (one GeoDAWN line spacing)
MIN_LEN_PX = 10.0       # >= 1 km trace
MAX_SINUOSITY = 1.6     # strike-consistency bound (arc / chord)
CORRIDOR_PX = 3         # +-300 m cross-strike corridor (the DTI kernel radius)
CATALOGUE_CLEARANCE_PX = 3.0
MIN_SEP_PX = 2.8        # never create sub-2.8 px crowding
SEED = 20261023

# sample_submission.tif transform (EPSG:32611, 100 m pixels)
TIE_EAST = 243350.0
TIE_NORTH = 4508550.0
PIXEL_M = 100.0


def _edge_offsets(radius: float) -> list[tuple[int, int, float]]:
    r = int(math.ceil(radius))
    out = []
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = math.hypot(dy, dx)
            if 0.0 < d < radius - 1e-9:
                out.append((dy, dx, d))
    return out


def _adjacency(pts: np.ndarray, gap: float):
    tree = cKDTree(pts)
    pairs = tree.query_pairs(gap)
    adj: list[list[tuple[int, float]]] = [[] for _ in range(len(pts))]
    for i, j in pairs:
        w = float(np.hypot(pts[i, 0] - pts[j, 0], pts[i, 1] - pts[j, 1]))
        adj[i].append((j, w))
        adj[j].append((i, w))
    return adj


def _dijkstra(adj, src: int, n: int, allowed=None):
    """Return (dist, predecessor). Optional boolean `allowed` mask over node idx."""
    dist = np.full(n, np.inf)
    pred = np.full(n, -1, dtype=np.int32)
    dist[src] = 0.0
    pq = [(0.0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if allowed is not None and not allowed[u]:
            continue
        for v, w in adj[u]:
            if allowed is not None and not allowed[v]:
                continue
            if d + w < dist[v]:
                dist[v] = d + w
                pred[v] = u
                heapq.heappush(pq, (d + w, v))
    return dist, pred


def _path_from_pred(pred, a: int, b: int) -> list[int]:
    path = [b]
    cur = b
    seen = set()
    while cur != a and cur != -1 and cur not in seen:
        seen.add(cur)
        cur = int(pred[cur])
        path.append(cur)
    path.reverse()
    return path if path[0] == a else [a, b]


@dataclass
class Trace:
    rank: int = 0
    dot_idx: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=int))
    arc_px: float = 0.0
    chord_px: float = 0.0
    sinuosity: float = 1.0
    spine: list[int] = field(default_factory=list)          # node indices along the diameter path
    mean_credit: float = 0.0
    max_credit: float = 0.0
    n_dots: int = 0
    confidence: float = 0.0


def build_traces(r0: np.ndarray, gap_px: float = GAP_PX,
                 min_len_px: float = MIN_LEN_PX,
                 max_sinuosity: float = MAX_SINUOSITY) -> tuple[list[Trace], np.ndarray]:
    """Link R0 dots into strike-consistent traces; return (traces, on_trace mask).

    `traces` are ordered by mean unique credit (best first). `on_trace` is a
    boolean grid marking R0 dots that belong to at least one qualifying trace.
    """
    r0 = np.asarray(r0, dtype=bool)
    pts = np.argwhere(r0).astype(np.int32)
    n = len(pts)
    u, upts = unique_credit(r0)             # upts == argwhere(r0), same row-major order as pts
    assert np.array_equal(upts, pts)
    credit = u

    adj = _adjacency(pts.astype(float), gap_px)
    seen = np.zeros(n, dtype=bool)
    traces: list[Trace] = []
    on_trace = np.zeros(r0.shape, dtype=bool)

    for s in range(n):
        if seen[s]:
            continue
        comp: list[int] = []
        stack = [s]
        seen[s] = True
        while stack:
            x = stack.pop()
            comp.append(x)
            for v, _ in adj[x]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        if len(comp) < 2:
            continue
        cset = set(comp)
        allowed = np.zeros(n, dtype=bool)
        for c in comp:
            allowed[c] = True
        # geodesic diameter: two Dijkstra sweeps restricted to this component
        d0, _ = _dijkstra(adj, comp[0], n, allowed)
        a = int(np.argmax(np.where(np.isfinite(d0), d0, -1.0)))
        da, pred = _dijkstra(adj, a, n, allowed)
        b = int(np.argmax(np.where(np.isfinite(da), da, -1.0)))
        arc = float(da[b])
        chord = float(np.hypot(pts[a, 0] - pts[b, 0], pts[a, 1] - pts[b, 1]))
        if arc < min_len_px or chord < 1e-6:
            continue
        sinu = arc / chord
        if sinu > max_sinuosity:
            continue
        spine = _path_from_pred(pred, a, b)
        comp_arr = np.array(comp, dtype=int)
        traces.append(Trace(
            dot_idx=comp_arr,
            arc_px=arc, chord_px=chord, sinuosity=sinu,
            spine=spine,
            mean_credit=float(credit[comp_arr].mean()),
            max_credit=float(credit[comp_arr].max()),
            n_dots=len(comp),
        ))
        p = pts[comp_arr]
        on_trace[p[:, 0], p[:, 1]] = True

    # "Built from R0's top-ranked dots": structural significance = length x
    # per-dot metric value. Long chains carrying high-credit dots rank first,
    # which both drives placement priority and orders the Phase-2 inventory.
    for t in traces:
        t.confidence = float(t.arc_px * t.mean_credit)
    traces.sort(key=lambda t: (-t.confidence, -t.arc_px))
    for k, t in enumerate(traces):
        t.rank = k + 1
    return traces, on_trace


def corridor_mask(traces: list[Trace], r0: np.ndarray,
                  corridor_px: int = CORRIDOR_PX) -> np.ndarray:
    """+-corridor_px dilation of the trace dots (a cross-strike uncertainty band)."""
    r0 = np.asarray(r0, dtype=bool)
    pts = np.argwhere(r0)
    seed = np.zeros(r0.shape, dtype=bool)
    for t in traces:
        p = pts[t.dot_idx]
        seed[p[:, 0], p[:, 1]] = True
    return ndi.binary_dilation(seed, iterations=corridor_px)


def robust_unit(band: np.ndarray, lo=2.0, hi=98.0) -> np.ndarray:
    """Mask -3.4e38 sentinels to NaN, winsorise, scale to [0,1]. NaN -> 0."""
    b = np.asarray(band, dtype=np.float64).copy()
    b[b <= -1e30] = np.nan
    finite = np.isfinite(b)
    out = np.zeros(b.shape, dtype=np.float32)
    if not finite.any():
        return out
    plo, phi = np.percentile(b[finite], [lo, hi])
    if phi - plo < 1e-9:
        return out
    out[finite] = np.clip((b[finite] - plo) / (phi - plo), 0.0, 1.0).astype(np.float32)
    return out


def corroboration(bands: dict[str, np.ndarray]) -> np.ndarray:
    """Strike-coherent potential-field / scarp corroboration in [0,1].

    Equal-weight mean of |TMI horizontal gradient| (b03), isostatic-gravity
    anomaly slope (b05) and detrended-elevation slope (b19), each robust-unit
    normalised. Used ONLY to rank legal destination pixels and to describe a
    trace; it never overrides the hard d_cat / separation gates.
    """
    parts = []
    for key in ("b03_tmi_hg", "b05_iso_grav_anom_slope", "b19_det_elev_slope"):
        if key in bands:
            parts.append(robust_unit(np.abs(bands[key])))
    if not parts:
        raise ValueError("corroboration needs at least one of b03/b05/b19")
    return np.mean(np.stack(parts, axis=0), axis=0).astype(np.float32)


def placement_list(r0: np.ndarray, traces: list[Trace], corridor: np.ndarray,
                   corrob: np.ndarray, footprint: np.ndarray, d_cat: np.ndarray,
                   min_sep_px: float = MIN_SEP_PX,
                   clearance_px: float = CATALOGUE_CLEARANCE_PX) -> np.ndarray:
    """Ranked, separation-feasible destination pixels (maximal independent set).

    Candidate pixels lie in the trace corridor, are inside the footprint, clear
    the catalogue by >= clearance_px, and are >= min_sep_px from every R0 dot.
    They are then ranked by (trace mean-credit priority, corroboration) and a
    greedy maximal independent set enforces mutual separation >= min_sep_px.
    Returns an (m,2) int array in priority order (the global placement list).
    """
    r0 = np.asarray(r0, dtype=bool)
    pts = np.argwhere(r0).astype(float)
    tree = cKDTree(pts)

    # per-pixel trace priority: length x credit structural significance
    prio = np.zeros(r0.shape, dtype=np.float32)
    for t in sorted(traces, key=lambda z: z.confidence):  # best overwrites
        p = pts[t.dot_idx].astype(int)
        prio[p[:, 0], p[:, 1]] = t.confidence
    # smooth priority over the corridor so the band shares its trace's rank
    prio = ndi.maximum_filter(prio, size=2 * CORRIDOR_PX + 1)

    d_exist = ndi.distance_transform_edt(~r0)
    cand = corridor & footprint & (d_cat >= clearance_px) & (d_exist >= min_sep_px - 1e-6)
    cy, cx = np.nonzero(cand)
    if len(cy) == 0:
        return np.zeros((0, 2), dtype=int)

    # ranking score — higher is a better destination
    score = 0.6 * robust_unit(prio) + 0.4 * corrob
    order = np.lexsort((cx, cy, -score[cy, cx].astype(np.float64)))

    # greedy maximal independent set with mutual separation
    offsets = _edge_offsets(min_sep_px)
    h, w = r0.shape
    occupied = r0.copy()
    out: list[tuple[int, int]] = []
    for oi in order:
        y = int(cy[oi])
        x = int(cx[oi])
        clash = False
        for dy, dx, _ in offsets:
            yy, xx = y + dy, x + dx
            if 0 <= yy < h and 0 <= xx < w and occupied[yy, xx]:
                clash = True
                break
        if not clash:
            occupied[y, x] = True
            out.append((y, x))
    return np.array(out, dtype=int)


def off_trace_order(r0: np.ndarray, on_trace: np.ndarray, seed: int = SEED,
                    protect: np.ndarray | None = None) -> np.ndarray:
    """Seeded permutation of R0 dots NOT on any qualifying trace (row-major map).

    `protect` is an optional boolean grid of dots to never move (the inherited
    2-3 px catalogue collar) so TRACKB never becomes a PRUNE edit.
    """
    r0 = np.asarray(r0, dtype=bool)
    pts = np.argwhere(r0)
    off = ~on_trace[r0]  # boolean over the row-major dot list
    if protect is not None:
        off = off & ~protect[r0]
    idx = np.flatnonzero(off)
    rng = np.random.default_rng(seed)
    rng.shuffle(idx)
    return pts[idx].astype(int)


def build_variant(r0: np.ndarray, footprint: np.ndarray,
                  sources: np.ndarray, placements: np.ndarray) -> tuple[np.ndarray, dict]:
    """Count-preserving relocation: remove `sources`, add `placements`.

    sources, placements are (k,2) int arrays. Count is preserved exactly.
    """
    r0 = np.asarray(r0, dtype=bool)
    foot = np.asarray(footprint, dtype=bool)
    variant = r0.copy()
    if len(sources):
        variant[sources[:, 0], sources[:, 1]] = False
    if len(placements):
        variant[placements[:, 0], placements[:, 1]] = True
    n_before = int(r0.sum())
    n_after = int(variant.sum())
    added = variant & ~r0
    removed = r0 & ~variant
    stats = {
        "n_before": n_before,
        "n_after": n_after,
        "n_removed": int(removed.sum()),
        "n_added": int(added.sum()),
        "count_preserved": bool(n_after == n_before),
        "all_dots_inside_footprint": bool((variant & ~foot).sum() == 0),
    }
    return variant, stats


def strike_azimuth(trace: Trace, r0: np.ndarray, pts: np.ndarray | None = None) -> float:
    """Bidirectional strike azimuth (deg from north, 0..180) from diameter ends."""
    if pts is None:
        pts = np.argwhere(r0)
    a, b = trace.spine[0], trace.spine[-1]
    ya, xa = pts[a]
    yb, xb = pts[b]
    de = (xb - xa) * PIXEL_M          # easting difference
    dn = -(yb - ya) * PIXEL_M         # northing difference (rows go south)
    ang = math.degrees(math.atan2(de, dn)) % 180.0
    return ang


def utm_to_lonlat(row: np.ndarray, col: np.ndarray):
    """EPSG:32611 pixel centres -> WGS84 lon/lat via GDAL PROJ (no pyproj needed)."""
    from rasterio.warp import transform as _transform
    east = TIE_EAST + (col.astype(float) + 0.5) * PIXEL_M
    north = TIE_NORTH - (row.astype(float) + 0.5) * PIXEL_M
    lons, lats = _transform("EPSG:32611", "EPSG:4326", east.tolist(), north.tolist())
    return np.asarray(lons), np.asarray(lats)
