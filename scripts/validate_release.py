#!/usr/bin/env python3
"""Fail-closed validator over every tracked release receipt.

Re-opens each raster from disk, re-runs every MUST-pass gate from Brief v2
section 6, re-checks the parent diff, and checks the ledger for duplicate
hashes and repeated (parent, axis, value) triples.

Exit codes: 0 = all gates pass, 1 = a gate failed, 2 = the pinned inputs are
not present in this environment (nothing can be verified, nothing is claimed).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems89.grid import Grid, sha256_file, verify_manifest  # noqa: E402

PARENT_HASHES = {
    "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
    "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd",
}


def main() -> int:
    try:
        grid = Grid(verify_manifest())
    except SystemExit as exc:
        print(f"inputs absent: {exc}")
        return 2

    parent = grid.read_mask(ROOT / "data/registry/parent_r0_zeros.tif")
    receipts = sorted((ROOT / "releases").glob("*.json"))
    if not receipts:
        print("no release receipts found")
        return 1

    failures: list[str] = []
    seen: dict[str, str] = {}
    for path in receipts:
        rec = json.loads(path.read_text(encoding="utf-8"))
        rid = rec["id"]
        for key, nan_outside in (("nan", True), ("zeros", False)):
            rel = ROOT / rec["files"][key]["path"]
            if not rel.is_file():
                failures.append(f"{rid}: missing {rel.name}")
                continue
            if sha256_file(rel) != rec["files"][key]["sha256"]:
                failures.append(f"{rid}: {key} sha256 drifted on disk")
            if rec["files"][key]["sha256"] in PARENT_HASHES:
                failures.append(f"{rid}: {key} reuses a parent hash")
            if rec["files"][key]["sha256"] in seen:
                failures.append(f"{rid}: duplicate {key} sha with {seen[rec['files'][key]['sha256']]}")
            seen[rec["files"][key]["sha256"]] = rid
            try:
                checks = grid.validate(rel, nan_outside=nan_outside)
            except AssertionError as exc:
                failures.append(str(exc))
                continue
            if checks["n_dots"][0] != int(parent.sum()):
                failures.append(f"{rid}: {key} n_dots {checks['n_dots'][0]} != parent")
        var = grid.read_mask(ROOT / rec["files"]["nan"]["path"])
        removed, added = int((parent & ~var).sum()), int((var & ~parent).sum())
        pct = 100.0 * (removed + added) / int(parent.sum())
        if rec["axis"] != "SNAP" and not (1.0 <= pct <= 50.0):
            failures.append(f"{rid}: changed {pct:.3f}% outside the 1-50% band")
        if rec["axis"] == "RELIEF" and removed != added:
            failures.append(f"{rid}: RELIEF must hold the count (removed {removed} != added {added})")
        if (var & ~parent).any() and grid.d_cat[var & ~parent].min() <= 3.0:
            failures.append(f"{rid}: an added dot violates the 3 px collar")
        print(f"{rid}: {rec['axis']} {rec['value']:8s} changed {pct:6.3f}%  "
              f"added_min_d_cat {float(grid.d_cat[var & ~parent].min()) if added else float('nan'):.4f}  OK")

    ledger = ROOT / "ledger" / "submissions.csv"
    if ledger.is_file():
        rows = list(csv.DictReader(ledger.open(encoding="utf-8")))
        hashes = [r["sha256"] for r in rows] + [r["sha256_zeros"] for r in rows]
        dupes = {h for h in hashes if hashes.count(h) > 1}
        if dupes:
            failures.append(f"ledger: duplicate sha256 {sorted(dupes)}")
        triples = [(r["parent"], r["axis"], r["value"]) for r in rows]
        rep = {t for t in triples if triples.count(t) > 1}
        if rep:
            failures.append(f"ledger: repeated (parent, axis, value) {sorted(rep)}")
        print(f"ledger: {len(rows)} rows, no duplicate hashes, no repeated (parent, axis, value)")

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print("  -", f)
        return 1
    print("\nALL GATES PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
