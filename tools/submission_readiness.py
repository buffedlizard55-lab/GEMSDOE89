#!/usr/bin/env python3
"""Fail-closed automated release audit. Never selects a slot or uploads.

Exit 0 means eligible for a separate selector, not organizer acceptance.
Exit 2 means DO_NOT_SUBMIT. Stored assertions alone cannot pass format checks.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gemsdoe import grid, validate


def scientific_blockers(card: dict) -> list[str]:
    reasons = []
    hp = card.get("holdout_protocol", {})
    candidate = hp.get("candidate", {})
    baseline = hp.get("visible_only_R0_baseline", {})
    delta = hp.get("paired_delta_candidate_minus_R0", {})

    def finite_number(value):
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)

    values = [candidate.get("value"), baseline.get("value"),
              delta.get("ci95", {}).get("lower_95")]
    if not all(finite_number(v) for v in values) or not (values[0] > values[1] and values[2] > 0):
        reasons.append("No supported paired holdout improvement over comparator")
    for result in (candidate, baseline):
        ci = result.get("ci95", {})
        lo, hi, value = ci.get("lower_95"), ci.get("upper_95"), result.get("value")
        if (result.get("evidence_class") != "HOLDOUT-DTI" or
                not all(finite_number(v) for v in (lo, hi, value)) or
                not 0 <= lo <= value <= hi <= 1):
            reasons.append("Missing or invalid HOLDOUT-DTI confidence interval")
    if not hp.get("evaluator_version") or not hp.get("withheld_positive_pixels", 0) > 0:
        reasons.append("Missing evaluator version or withheld positives")
    # The comparator must be the locked current best on this exact split,
    # not merely a convenient ancestor. Existing cards do not establish this.
    if hp.get("comparator_is_locked_current_best") is not True:
        reasons.append("Current-best comparator on identical split is not established")
    canary = card.get("leakage_canary", {})
    features = canary.get("features_tested", {})
    if (canary.get("verdict") != "PASS" or not features or
            any(not finite_number(v.get("strength")) or v["strength"] > .90
                for v in features.values())):
        reasons.append("Missing or failed single-feature leakage canary")
    audit = card.get("registry_uniqueness", {})
    for stage in ("before_placement", "prewrite", "postwrite"):
        row = audit.get(stage) or {}
        rho, overlap = row.get("max_abs_surface_spearman"), row.get("max_dot_overlap_3px")
        if (not row.get("n_reference_geometries", 0) > 0 or
                not all(finite_number(v) for v in (rho, overlap)) or
                not 0 <= rho <= .90 or not 0 <= overlap <= .70 or
                row.get("duplicate_stop") is not False):
            reasons.append(f"Missing or failed registry {stage} audit")
    if audit.get("complete_registry_coverage") is not True:
        reasons.append("Global registry coverage is incomplete; local uniqueness is not global proof")
    if audit.get("exact_sha256_against_ledger", {}).get("unique") is not True:
        reasons.append("No exact-hash uniqueness evidence")
    if card.get("verdict") != "promote":
        reasons.append("Scientific run verdict is negative or missing")
    note = card.get("submission", {}).get("note")
    if not isinstance(note, str) or not note or len(note) > 140:
        reasons.append("Submission note missing or exceeds 140 characters")
    return reasons


def audit_card(card: dict, root: Path = ROOT) -> dict:
    blockers = scientific_blockers(card)
    raster = card.get("raster", {})
    checks = []
    sha = None
    try:
        path = (root / raster["path"]).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError("raster path escapes repository")
        sha = grid.sha256_file(path)
        if sha != raster.get("sha256"):
            blockers.append("Raster hash differs from run card")
        contract = json.loads((root / "registry/grid_contract.json").read_text())
        ok, checks = validate.gate_release(path, contract, require_nan_outside=False)
        if not ok:
            blockers.append("Upload-safe format validation failed")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        blockers.append(f"Cannot validate raster: {exc}")
    return {"schema_version": 1, "status": "DO_NOT_SUBMIT" if blockers else "ELIGIBLE_FOR_SELECTOR",
            "safe_to_submit": False, "slot_selected": False,
            "explanation": "Eligibility never selects a weekly slot or confirms organizer acceptance.",
            "blockers": blockers, "raster_sha256": sha, "format_gates": checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("card", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = audit_card(json.loads(args.card.read_text()))
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        report = {"status": "DO_NOT_SUBMIT", "safe_to_submit": False, "blockers": [str(exc)]}
    text = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")
    return 0 if report["status"] == "ELIGIBLE_FOR_SELECTOR" else 2


if __name__ == "__main__":
    raise SystemExit(main())
