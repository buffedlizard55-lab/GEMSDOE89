#!/usr/bin/env python3
"""Ledger ↔ filesystem consistency checks (no competition data needed).

Fails if
  * a release raster's sha256 is missing from the ledger,
  * a ledger row with status BUILT has no file on disk,
  * a (parent, axis, value) triple appears twice,
  * any form_note exceeds 140 characters.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe.grid import sha256_file  # noqa: E402


def main():
    rows = list(csv.DictReader(open(ROOT / "ledger" / "submissions.csv", newline="")))
    mine = [r for r in rows if r.get("source") == "GEMSDOE89"]
    problems = []

    known = {(r.get("sha256") or "").strip() for r in rows}
    known |= {(r.get("sha256_zeros") or "").strip() for r in rows}
    known.discard("")

    on_disk = {p.name: sha256_file(p) for p in sorted((ROOT / "releases").glob("*.tif"))}
    disk_hashes = set(on_disk.values())

    for name, sha in on_disk.items():
        if sha not in known:
            problems.append(f"release {name} has sha256 {sha[:12]} that is not in the ledger")

    for r in mine:
        for col in ("sha256", "sha256_zeros"):
            h = (r.get(col) or "").strip()
            if h and h not in disk_hashes:
                problems.append(f"ledger row {r['id']} {col} has no file on disk")

    triples = [(r.get("parent"), (r.get("axis") or "").upper(), r.get("value")) for r in rows]
    seen = {}
    for t in triples:
        seen[t] = seen.get(t, 0) + 1
    for t, n in seen.items():
        if n > 1 and t[1]:
            problems.append(f"repeated (parent, axis, value) {t} x{n}")

    for r in mine:
        note = r.get("form_note") or ""
        if len(note) > 140:
            problems.append(f"{r['id']} form_note is {len(note)} chars (max 140)")

    print(f"ledger rows: {len(rows)} ({len(mine)} this session); release files: {len(on_disk)}")
    if problems:
        for p in problems:
            print("PROBLEM:", p)
        return 2
    print("ledger consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
