#!/usr/bin/env python3
"""RELIEF axis report: decompose each variant into removal vs addition, on the
report-only instruments, and compute the tercile contrasts against the control.

Writes evidence/relief_axis_report.json.  Nothing here is a gate and nothing
here is a score: the off-catalogue SGMC control is a PROXY and every projection
is a MODEL.

Why decompose: all three arms share one source tercile and one remove/insert
rule, so each arm's total change = (effect of the removal) + (effect of the
insertions).  Only the insertions differ between arms, so only they carry the
tercile signal.  Reporting the total alone would credit the tercile with the
reshuffle effect.
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

OUT = ROOT / "evidence" / "relief_axis_report.json"


def score_dt(mask: np.ndarray, truth: np.ndarray) -> dict:
    r = metric.dti_binary(mask, truth)
    m = r["n_emitted"] - r["fp"]          # M = sum over dots of max_g k
    return {"dti": r["dti"], "T": r["tp"], "M": m, "S": float(r["n_emitted"]),
            "G": float(r["n_truth"])}


def main() -> int:
    verified = verify_manifest()
    grid = Grid(verified)
    r0 = grid.read_mask(verified["parent_r0_zeros"])
    off_sgmc = grid.read_mask(verified["sgmc_faults_control"]) & ~grid.catalogue
    catalogue = grid.catalogue

    arms = []
    for path in sorted((ROOT / "releases").glob("*.json")):
        rec = json.loads(path.read_text(encoding="utf-8"))
        if rec.get("axis") != "RELIEF":
            continue
        var = grid.read_mask(ROOT / rec["files"]["nan"]["path"])
        removed = r0 & ~var
        added = var & ~r0
        intermediate = r0 & ~removed          # = r0 minus the removal
        row = {"id": rec["id"], "value": rec["value"],
               "source_tercile": rec["source_tercile"],
               "receiving_tercile": rec["receiving_tercile"],
               "n_dots": int(var.sum()), "pct_changed": rec["diff_vs_parent"]["pct_changed"],
               "allocation_after": rec["diff_vs_parent"]["tercile_allocation_after"]}
        for label, truth in (("sgmc_proxy", off_sgmc), ("catalogue_control", catalogue)):
            base = score_dt(r0, truth)
            mid = score_dt(intermediate, truth)
            full = score_dt(var, truth)
            row[label] = {
                "parent": base, "after_removal": mid, "variant": full,
                "dT_removal": mid["T"] - base["T"],
                "dT_addition": full["T"] - mid["T"],
                "dM_removal": mid["M"] - base["M"],
                "dM_addition": full["M"] - mid["M"],
                "dDTI_removal": mid["dti"] - base["dti"],
                "dDTI_addition": full["dti"] - mid["dti"],
                "dDTI_total": full["dti"] - base["dti"],
            }
        arms.append(row)

    ctrl = next((a for a in arms if a["receiving_tercile"] == a["source_tercile"]), None)
    for a in arms:
        if ctrl and a is not ctrl:
            a["contrast_vs_control_sgmc"] = a["sgmc_proxy"]["dDTI_total"] - ctrl["sgmc_proxy"]["dDTI_total"]
            a["contrast_vs_control_catalogue"] = a["catalogue_control"]["dDTI_total"] - ctrl["catalogue_control"]["dDTI_total"]
        else:
            a["contrast_vs_control_sgmc"] = 0.0
            a["contrast_vs_control_catalogue"] = 0.0

    report = {
        "schema": "gems89.relief-axis-report.v1",
        "generated_utc": utc_now(),
        "git_sha": git_sha(),
        "parent": "h33-h33-2-b2",
        "axis": "RELIEF",
        "control_arm": ctrl["id"] if ctrl else None,
        "instruments": {
            "sgmc_proxy": "off-catalogue SGMC control raster; PROXY ONLY, never a gate, never a score",
            "catalogue_control": "the known-fault catalogue as truth; a control that must not move",
        },
        "arms": arms,
        "reading": "dDTI_addition is the only quantity that differs between arms; it carries the tercile signal.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"{'arm':16s} {'recv':12s} {'dDTI_rm':>9s} {'dDTI_add':>9s} {'dDTI_tot':>9s} "
          f"{'dT_rm':>8s} {'dT_add':>8s} {'vs ctrl':>9s}  cat_dDTI")
    for a in arms:
        s = a["sgmc_proxy"]
        print(f"{a['value']:16s} {a['receiving_tercile']:12s} {s['dDTI_removal']:+9.5f} "
              f"{s['dDTI_addition']:+9.5f} {s['dDTI_total']:+9.5f} {s['dT_removal']:+8.2f} "
              f"{s['dT_addition']:+8.2f} {a['contrast_vs_control_sgmc']:+9.5f}  "
              f"{a['catalogue_control']['dDTI_total']:+.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
