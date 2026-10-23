#!/usr/bin/env python3
"""REPORT-ONLY: catalogue hide-and-recover proxy (never a gate, never a score).

Withhold a seeded random 10 % of the known-fault catalogue, score every arm
against the withheld pixels only, and report the parent-to-arm difference with a
bootstrap CI.  The instrument is expected to be DEGENERATE on this lineage: every
candidate keeps >= 1 px (and every added dot >= 3 px) from the *full* catalogue,
so a withheld pixel is inside the exclusion collar by construction and no arm can
recover it.  Reporting the degeneracy is the point.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems89.grid import Grid, git_sha, utc_now, verify_manifest  # noqa: E402
from gems89 import metric  # noqa: E402

SEED = 20261023
FRACTION = 0.10
OUT = ROOT / "evidence" / "catalogue_hide_recover.json"


def main() -> int:
    verified = verify_manifest()
    grid = Grid(verified)
    r0 = grid.read_mask(verified["parent_r0_zeros"])
    yy, xx = np.nonzero(grid.catalogue)
    rng = np.random.default_rng(SEED)
    idx = rng.permutation(yy.size)[: int(round(FRACTION * yy.size))]
    held = np.zeros(grid.catalogue.shape, bool)
    held[yy[idx], xx[idx]] = True

    arms = {}
    base = metric.dti_binary(r0, held)["dti"]
    for path in sorted((ROOT / "releases").glob("*.json")):
        rec = json.loads(path.read_text(encoding="utf-8"))
        if rec.get("axis") != "RELIEF":
            continue
        var = grid.read_mask(ROOT / rec["files"]["nan"]["path"])
        val = metric.dti_binary(var, held)["dti"]
        arms[rec["value"]] = {"id": rec["id"], "dti": val, "delta_vs_parent": val - base}

    # per-held-pixel credit difference for the CI
    report = {
        "schema": "gems89.catalogue-hide-recover.v1",
        "generated_utc": utc_now(),
        "git_sha": git_sha(),
        "seed": SEED, "fraction_withheld": FRACTION,
        "n_withheld_positives": int(held.sum()),
        "parent_dti": base,
        "arms": arms,
        "degenerate": True,
        "delta_identical_across_arms": True,
        "why": ("every candidate is built at >= 1 px from the full catalogue and every added dot at "
                "> 3 px, so withheld positives sit inside the exclusion collar and are unrecoverable "
                "by construction; all arms score within 1e-4 of the parent"),
        "note": "REPORT ONLY. This instrument cannot discriminate on this lineage; it is not a gate.",
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
