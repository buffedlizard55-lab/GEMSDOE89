"""Exact recipe rebuild of Parent R0 (h33-h33-2-b2, GEMSDOE32 lineage).

Lineage verified byte-for-byte:
  1. h19_5 : 121,131-px multi-layer corroborated ridge mask (19GEMSDOE, 0.1922 CLAIM)
  2. d28   : dot_thin(h19_5, r_min=2.8) -> 44,090 unit dots (GEMSDOE25, 0.2600 CLAIM)
  3. R0    : d28 & (d_cat > 2.0) & footprint & ~catalogue -> 37,654 unit dots
             (GEMSDOE32 h33-h33-2-b2, 0.2778 CLAIM; zeros sha256 c55bafc4...,
              nan sha256 baeae321...)
"""

from __future__ import annotations

from collections import deque

import numpy as np
from scipy.ndimage import distance_transform_edt, label as ndi_label

PARENT_ID = "h33-h33-2-b2"
EXPECTED_D28_DOTS = 44_090
EXPECTED_R0_DOTS = 37_654
R0_ZEROS_SHA256 = "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
R0_NAN_SHA256 = "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd"
D28_SHA256 = "91eae1ca42ec845eaa8c2ba32da49806e24751743459b8a10017c479bbe639b8"
H19_5_SHA256 = "ec1f9b56b83ce33cad781ceb9f104b18fb4f2ff785263a4e89616af4aabdee8d"


def dot_thin(ridge_mask: np.ndarray, r_min: float = 2.8) -> np.ndarray:
    """Deterministic row-major BFS component thinning with Euclidean disk r_min.

    Reproduces GEMSDOE24/25 d28 (44,090 dots) bit-for-bit from h19_5.
    """
    rm = np.asarray(ridge_mask, dtype=bool)
    h, w = rm.shape
    labels, _ = ndi_label(rm, structure=np.ones((3, 3), dtype=np.int8))
    out = np.zeros((h, w), dtype=bool)
    blocked = np.zeros((h, w), dtype=bool)

    r_int = int(np.floor(r_min))
    dys, dxs = np.mgrid[-r_int : r_int + 1, -r_int : r_int + 1]
    disk = (dys * dys + dxs * dxs) <= (r_min * r_min + 1e-9)
    disk_dy = dys[disk]
    disk_dx = dxs[disk]

    nbrs = (
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1),
    )
    visited = np.zeros((h, w), dtype=bool)
    ys, xs = np.nonzero(rm)
    order = np.lexsort((xs, ys))
    for y0, x0 in zip(ys[order], xs[order]):
        if visited[y0, x0]:
            continue
        cid = labels[y0, x0]
        q = deque([(int(y0), int(x0))])
        visited[y0, x0] = True
        while q:
            r, c = q.popleft()
            if not blocked[r, c]:
                out[r, c] = True
                ry = r + disk_dy
                rx = c + disk_dx
                valid = (ry >= 0) & (ry < h) & (rx >= 0) & (rx < w)
                blocked[ry[valid], rx[valid]] = True
            for dr, dc in nbrs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w and not visited[nr, nc] and labels[nr, nc] == cid:
                    visited[nr, nc] = True
                    q.append((nr, nc))
    return out


def rebuild_r0_mask(
    h19_5_mask: np.ndarray,
    footprint: np.ndarray,
    catalogue_mask: np.ndarray,
    r_min: float = 2.8,
    collar_px: float = 2.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Rebuild (r0_mask, d28_mask) from h19_5, footprint, and catalogue."""
    foot = np.asarray(footprint, dtype=bool)
    cat = np.asarray(catalogue_mask, dtype=bool) & foot
    h19 = np.asarray(h19_5_mask, dtype=bool) & foot
    d28 = dot_thin(h19, r_min=r_min)
    d_cat = distance_transform_edt(~cat)
    r0 = d28 & (d_cat > collar_px) & foot & (~cat)
    return r0, d28
