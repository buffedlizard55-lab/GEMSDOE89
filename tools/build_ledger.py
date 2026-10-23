#!/usr/bin/env python3
"""Assemble ledger/submissions.csv from the recovered upstream history + this
session's built variants.

Upstream rows come from buffedlizard55-lab/GEMSDOE84 ledger/submissions.csv
(copied verbatim to ledger/upstream_GEMSDOE84.csv).  Repeats are collapsed on
sha256: a repeated upload of identical bytes teaches nothing and is recorded
once, with a repeat count.

This session's rows are read from registry/build_reports.json so that the
ledger can never drift from the files on disk.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "ledger" / "upstream_GEMSDOE84.csv"

FIELDS = [
    "id", "site", "name", "score", "evidence_class", "encoding", "n_dots",
    "pct_changed", "sha8", "sha256", "sha256_zeros", "parent", "axis", "value",
    "status", "receipt", "receipt_score", "predicted_change", "date", "form_note",
    "notes", "source",
]

PREDICTIONS = {
    "r10": "+0.003 (MODEL; band -0.012..+0.018). No-evidence outcome expected.",
    "r15": "+0.004 (MODEL; band -0.017..+0.027). Dose 1.5x of r10.",
    "r15s": "+0.001 (MODEL; band -0.007..+0.011). Weaker density contrast than r10/r15.",
}
FORM_NOTES = {
    "r10": "R0 h33-h33-2-b2 + RELIEF r10: 3765/37654 dots (10%) range->piedmont class, count fixed, dcat>=3px, structured; pred +0.003",
    "r15": "R0 h33-h33-2-b2 + RELIEF r15: 5648/37654 dots (15%) range->piedmont class, count fixed, dcat>=3px, structured; pred +0.004",
    "r15s": "R0 h33-h33-2-b2 + RELIEF r15s: 5648/37654 dots (15%) high->mid slope class, count fixed, dcat>=3px; pred +0.001",
}
RECOMMEND = {
    "r10": "SLOT 1 (primary). Lowest dose, smallest downside band.",
    "r15": "SLOT 2 only if r10 lands >= 0.2878 (+0.010); otherwise HOLD.",
    "r15s": "ALTERNATE / fallback twin for the same slot as r10 if the human prefers the slope definition.",
}


def collapse(rows):
    """Collapse exact repeats on sha256 (or sha8 when sha256 is absent)."""
    out, index = [], {}
    for r in rows:
        key = (r.get("sha256") or "").strip() or (r.get("sha8") or "").strip() or r.get("id")
        if key in index:
            prev = out[index[key]]
            prev["notes"] = (prev.get("notes") or "") + " [repeat upload collapsed]"
            n = int(prev.get("_repeats") or 1) + 1
            prev["_repeats"] = n
            if r.get("score") and not prev.get("score"):
                prev["score"] = r["score"]
            continue
        index[key] = len(out)
        r = dict(r)
        r["_repeats"] = 1
        r["source"] = "upstream:GEMSDOE84"
        out.append(r)
    for r in out:
        n = r.pop("_repeats", 1)
        if n > 1:
            r["notes"] = (r.get("notes") or "") + f" (uploaded {n}x)"
    return out


def main():
    with open(UPSTREAM, newline="") as fh:
        upstream = collapse(list(csv.DictReader(fh)))

    mine = json.loads((ROOT / "registry" / "build_reports.json").read_text())
    new_rows = []
    for rep in mine:
        value = rep["value"]
        s = rep["stats"]
        row = {
            "id": rep["id"],
            "site": "GEMSDOE89",
            "name": rep["id"],
            "score": "",
            "evidence_class": "BUILT (unscored)",
            "encoding": "nan+zeros",
            "n_dots": s["n_dots"],
            "pct_changed": f"{s['pct_changed']:.2f}",
            "sha8": rep["files"]["sha8"],
            "sha256": rep["files"]["sha256"],
            "sha256_zeros": rep["files"]["sha256_zeros"],
            "parent": rep["parent"],
            "axis": "RELIEF",
            "value": value,
            "status": "BUILT",
            "receipt": "N",
            "receipt_score": "",
            "predicted_change": PREDICTIONS[value],
            "date": "2026-10-23",
            "form_note": FORM_NOTES[value],
            "notes": (
                f"source class {s['source_class']} -> target class {s['target_class']}; "
                f"added dots on structure (mean |grad det_elev| {s['added_mean_gradient']:.1f} vs parent "
                f"{s['parent_mean_gradient']:.1f}); mean displacement {s['mean_displacement_px']:.0f} px. "
                + RECOMMEND[value]
            ),
            "source": "GEMSDOE89",
        }
        new_rows.append(row)

    path = ROOT / "ledger" / "submissions.csv"
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in new_rows + upstream:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    print(f"wrote {path}: {len(new_rows)} new + {len(upstream)} collapsed upstream rows")


if __name__ == "__main__":
    main()
