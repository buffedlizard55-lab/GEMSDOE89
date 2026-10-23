#!/usr/bin/env python3
"""Fail-closed startup gate: verify every pin, then rebuild R0 byte-exactly.

Parent R0 = h33-h33-2-b2 (GEMSDOE32): 37,654 unit-mass dots, none within 2 px of
the known-fault catalogue, live score 0.2778 recorded as a CLAIM (no receipt).

The recorded lineage (GEMSDOE32 README + GEMSDOE88 scripts/build_prune_variants.py)
is re-executed end to end:

    H19-5 continuous field (121,131 px)
      -- Poisson-disk thinning, min_dist = 1.5 px -->  D1.5   (60,069 px, CLAIM 0.2477)
      -- Poisson-disk thinning, min_dist = 2.8 px -->  D2.8   (44,090 px, CLAIM 0.2600)
      -- delete dots with d(catalogue) <= 1 px    -->  SOLO   (40,199 px, CLAIM 0.2708)
      -- delete dots with d(catalogue) <= 2 px    -->  R0     (37,654 px, CLAIM 0.2778)

Both published encodings of R0 must match their recorded SHA-256.  If they do
not, this script exits nonzero and no candidate is built: the parent is never
approximated.

Usage: python3 scripts/rebuild_r0.py
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gems89.grid import ROOT, Grid, git_sha, sha256_file, utc_now, verify_manifest  # noqa: E402
from canonical_writer import LIBDEFLATE_LEVEL, write_canonical  # noqa: E402
from gems89 import metric  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
PARENT_SHA_ZEROS = "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
PARENT_SHA_NAN = "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd"
PARENT_DOTS = 37_654
OUT = ROOT / "registry" / "r0_verification.json"


def dot_thin(mask: np.ndarray, min_dist: float) -> np.ndarray:
    """Deterministic geodesic Poisson-disk thinning (GEMSDOE25 exact algorithm).

    Reimplemented here from the recorded recipe: seeded breadth-first walk in
    row-major order over 8-connected components; a kept dot blocks the disc of
    radius min_dist around itself.
    """
    from collections import deque
    from scipy.ndimage import label as ndi_label

    mask = np.asarray(mask, dtype=bool)
    if min_dist <= 1.0 or not mask.any():
        return mask.copy()
    H, W = mask.shape
    pad = int(np.ceil(min_dist)) + 1
    Wp, Hp = W + 2 * pad, H + 2 * pad
    padded = np.zeros((Hp, Wp), dtype=bool)
    padded[pad:pad + H, pad:pad + W] = mask
    flat = bytearray(padded.tobytes())
    visited, blocked, kept = bytearray(Hp * Wp), bytearray(Hp * Wp), bytearray(Hp * Wp)
    r = int(np.ceil(min_dist))
    lim = min_dist * min_dist
    disc = [dy * Wp + dx for dy in range(-r, r + 1) for dx in range(-r, r + 1)
            if dy * dy + dx * dx < lim]
    nbr = (-Wp - 1, -Wp, -Wp + 1, -1, 1, Wp - 1, Wp, Wp + 1)
    comp, _ = ndi_label(padded, structure=np.ones((3, 3), dtype=int))
    fc = comp.ravel()
    order = np.flatnonzero(fc)
    _, first = np.unique(fc[order], return_index=True)
    for seed in order[np.sort(first)].tolist():
        if visited[seed]:
            continue
        visited[seed] = 1
        queue = deque((seed,))
        while queue:
            q = queue.popleft()
            if not blocked[q]:
                kept[q] = 1
                for o in disc:
                    blocked[q + o] = 1
            for o in nbr:
                nb = q + o
                if flat[nb] and not visited[nb]:
                    visited[nb] = 1
                    queue.append(nb)
    out = np.frombuffer(bytes(kept), dtype=np.uint8).reshape(Hp, Wp).astype(bool)
    return out[pad:pad + H, pad:pad + W]


def main() -> int:
    verified = verify_manifest()
    grid = Grid(verified)

    h19_5 = grid.read_mask(verified["anc_h19_5"])
    d15_ref = grid.read_mask(verified["anc_d1_5"])
    d28_ref = grid.read_mask(verified["anc_d2_8"])
    solo_ref = grid.read_mask(verified["anc_solo_d2_8"])
    r0_ref = grid.read_mask(verified["parent_r0_zeros"])
    r0_ref_nan = grid.read_mask(verified["parent_r0_nan"])

    d15 = dot_thin(h19_5, 1.5)
    d28 = dot_thin(h19_5, 2.8)
    solo = d28 & (grid.d_cat > 1.0)
    r0 = d28 & (grid.d_cat > 2.0)

    stages = {
        "H19-5": (int(h19_5.sum()), 121_131),
        "D1.5": (int(d15.sum()), 60_069),
        "D2.8": (int(d28.sum()), 44_090),
        "SOLO-D2.8": (int(solo.sum()), 40_199),
        "R0": (int(r0.sum()), PARENT_DOTS),
    }
    pixel_checks = {
        "D1.5": bool(np.array_equal(d15, d15_ref)),
        "D2.8": bool(np.array_equal(d28, d28_ref)),
        "SOLO-D2.8": bool(np.array_equal(solo, solo_ref)),
        "R0": bool(np.array_equal(r0, r0_ref)),
        "R0_nan_twin": bool(np.array_equal(r0_ref_nan, r0_ref)),
    }

    with tempfile.TemporaryDirectory() as td:
        p_z = Path(td) / "r0_zeros.tif"
        p_n = Path(td) / "r0_nan.tif"
        sha_z = write_canonical(p_z, r0, grid, nan_outside=False)
        sha_n = write_canonical(p_n, r0, grid, nan_outside=True)

    dvals = grid.d_cat[r0]
    report = {
        "schema": "gems89.r0-verification.v1",
        "generated_utc": utc_now(),
        "git_sha": git_sha(),
        "parent": PARENT_ID,
        "method": "full recorded H19-5 -> D1.5 -> D2.8 -> SOLO-D2.8 -> R0 recipe, re-executed",
        "manifest_verified": True,
        "stages": {k: {"rebuilt": v[0], "expected": v[1], "ok": v[0] == v[1]} for k, v in stages.items()},
        "pixel_checks": pixel_checks,
        "writer_profile": {k: str(v) for k, v in grid.profile_zeros.items()},
        "encoder": {"container": "GDAL GTiff tiled 256x256, Predictor=3", "deflate": "libdeflate", "libdeflate_level": LIBDEFLATE_LEVEL},
        "r0_zeros_sha256": sha_z,
        "r0_zeros_sha256_expected": PARENT_SHA_ZEROS,
        "r0_zeros_byte_exact": sha_z == PARENT_SHA_ZEROS,
        "r0_nan_sha256": sha_n,
        "r0_nan_sha256_expected": PARENT_SHA_NAN,
        "r0_nan_byte_exact": sha_n == PARENT_SHA_NAN,
        "parent_geometry": {
            "footprint_px": int(grid.foot.sum()),
            "catalogue_px": int(grid.catalogue.sum()),
            "dots": int(r0.sum()),
            "zero_catalogue_mass": bool(int((r0 & grid.catalogue).sum()) == 0),
            "min_d_cat_px": float(dvals.min()),
            "n_within_2px": int((dvals <= 2.0).sum()),
            "n_within_3px": int((dvals <= 3.0).sum()),
        },
        "dti_self_check": metric.dti_binary(r0, grid.catalogue & grid.foot),
        "note": "R0 equality is mandatory and never approximated. The 0.2778 live score remains a CLAIM without a submission receipt.",
    }
    ok = (all(v["ok"] for v in report["stages"].values())
          and all(pixel_checks.values())
          and report["r0_zeros_byte_exact"] and report["r0_nan_byte_exact"]
          and report["parent_geometry"]["zero_catalogue_mass"]
          and report["parent_geometry"]["n_within_2px"] == 0
          and report["parent_geometry"]["dots"] == PARENT_DOTS)
    report["ok"] = bool(ok)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": report["ok"],
        "stages": {k: v["rebuilt"] for k, v in report["stages"].items()},
        "pixel_checks": pixel_checks,
        "zeros_byte_exact": report["r0_zeros_byte_exact"],
        "nan_byte_exact": report["r0_nan_byte_exact"],
        "min_d_cat_px": report["parent_geometry"]["min_d_cat_px"],
        "n_within_3px": report["parent_geometry"]["n_within_3px"],
        "report": str(OUT.relative_to(ROOT)),
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
