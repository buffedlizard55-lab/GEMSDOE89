#!/usr/bin/env python3
"""Assemble ledger/submissions.csv from the recovered upstream history + all
GEMSDOE89 built variants (SPACING + MASS + RELIEF).

Upstream rows come from buffedlizard55-lab/GEMSDOE84 ledger/submissions.csv
(copied verbatim to ledger/upstream_GEMSDOE84.csv). Repeats are collapsed on
sha256: a repeated upload of identical bytes teaches nothing and is recorded
once, with a repeat count.

GEMSDOE89 rows are read from registry/build_reports_spacing.json (this session),
registry/build_mass_reports.json (merged MASS session), and
registry/build_reports.json (merged RELIEF session) so the ledger never drifts
from the release rasters in releases/.
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
    "status", "receipt", "receipt_score", "receipt_date", "predicted_change",
    "date", "form_note", "notes", "source",
]

MASS_META = {
    "m10uniq": (
        "+0.002 (MODEL; band -0.010..+0.010; ceiling +0.0105 if every dropped dot is zero-credit)",
        "R0 h33-h33-2-b2; MASS m10uniq: drop 3765/37654 dots (10%), none added; pred +0.002",
        "SLOT 2B (if SPACING strike inside +-0.010): drop 3765 deepest-redundancy far-field dots, collar preserved.",
    ),
    "m10rand": (
        "-0.002 (MODEL; band -0.016..+0.010; the count-matched null for m10uniq)",
        "R0 h33-h33-2-b2; MASS m10rand: drop 3765/37654 dots (10%), none added; pred -0.002",
        "CONTROL: 3765 dots drawn uniformly. Same count, same legality, only selection differs from m10uniq.",
    ),
    "m20uniq": (
        "+0.004 (MODEL; band -0.020..+0.021; ceiling +0.021 if every dropped dot is zero-credit)",
        "R0 h33-h33-2-b2; MASS m20uniq: drop 7531/37654 dots (20%), none added; pred +0.004",
        "DOSE: 7531 deepest-redundancy far-field dots; submit only after m10uniq reads >= +0.010.",
    ),
}

RELIEF_PREDICTIONS = {
    "r10": "+0.003 (MODEL; band -0.012..+0.018). No-evidence outcome expected.",
    "r15": "+0.004 (MODEL; band -0.017..+0.027). Dose 1.5x of r10.",
    "r15s": "+0.001 (MODEL; band -0.007..+0.011). Weaker density contrast than r10/r15.",
}
RELIEF_FORM_NOTES = {
    "r10": "R0 h33-h33-2-b2 + RELIEF r10: 3765/37654 dots (10%) range->piedmont class, count fixed, dcat>=3px, structured; pred +0.003",
    "r15": "R0 h33-h33-2-b2 + RELIEF r15: 5648/37654 dots (15%) range->piedmont class, count fixed, dcat>=3px, structured; pred +0.004",
    "r15s": "R0 h33-h33-2-b2 + RELIEF r15s: 5648/37654 dots (15%) high->mid slope class, count fixed, dcat>=3px; pred +0.001",
}
RELIEF_RECOMMEND = {
    "r10": "Prior RELIEF arm (hold behind SPACING strike and MASS m10uniq).",
    "r15": "Dose 1.5x of RELIEF r10; submit only if r10 >= +0.010.",
    "r15s": "Slope-defined RELIEF alternate.",
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

    new_rows = []

    spacing_path = ROOT / "registry" / "build_reports_spacing.json"
    if spacing_path.exists():
        for rep in json.loads(spacing_path.read_text()):
            s = rep["stats"]
            spec = rep["spec"]
            new_rows.append({
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
                "axis": "SPACING",
                "value": rep["value"],
                "status": "BUILT",
                "receipt": "N",
                "receipt_score": "",
                "receipt_date": "",
                "predicted_change": spec["predicted_change"],
                "date": "2026-10-23",
                "form_note": spec["form_note"],
                "notes": (
                    f"{s['n_corridors_repacked']} corridors ({s['n_cleared_in_corridors']} R0 dots cleared, "
                    f"{s['n_moved']} moved = {s['pct_changed']:.2f}%, sym diff {s['pct_symmetric_diff']:.2f}%); "
                    f"dT_crest {s['t_crest_delta']:+.1f}, dT_manif {s['t_manifold_delta']:+.1f}; "
                    f"mean disp {s['mean_displacement_px']:.2f} px. {spec['recommend']}"
                ),
                "source": "GEMSDOE89",
            })

    mass_path = ROOT / "registry" / "build_mass_reports.json"
    if mass_path.exists():
        order = {"m10uniq": 0, "m10rand": 1, "m20uniq": 2}
        reps = sorted(json.loads(mass_path.read_text()), key=lambda r: order.get(r["value"], 99))
        for rep in reps:
            value = rep["value"]
            s = rep["stats"]
            pred_txt, form_note, note_txt = MASS_META[value]
            new_rows.append({
                "id": rep["id"],
                "site": "GEMSDOE89",
                "name": rep["id"],
                "score": "",
                "evidence_class": "BUILT (unscored)",
                "encoding": "nan+zeros",
                "n_dots": s["n_after"],
                "pct_changed": f"{s['pct_changed']:.2f}",
                "sha8": rep["files"]["sha8"],
                "sha256": rep["files"]["sha256"],
                "sha256_zeros": rep["files"]["sha256_zeros"],
                "parent": rep["parent"],
                "axis": "MASS",
                "value": value,
                "status": "BUILT",
                "receipt": "N",
                "receipt_score": "",
                "receipt_date": "",
                "predicted_change": pred_txt,
                "date": "2026-10-23",
                "form_note": form_note,
                "notes": note_txt,
                "source": "GEMSDOE89",
            })

    relief_path = ROOT / "registry" / "build_reports.json"
    if relief_path.exists():
        for rep in json.loads(relief_path.read_text()):
            value = rep["value"]
            s = rep["stats"]
            new_rows.append({
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
                "receipt_date": "",
                "predicted_change": RELIEF_PREDICTIONS[value],
                "date": "2026-10-23",
                "form_note": RELIEF_FORM_NOTES[value],
                "notes": (
                    f"source class {s['source_class']} -> target class {s['target_class']}; "
                    f"added dots on structure (mean |grad det_elev| {s['added_mean_gradient']:.1f} vs parent "
                    f"{s['parent_mean_gradient']:.1f}); mean displacement {s['mean_displacement_px']:.0f} px. "
                    + RELIEF_RECOMMEND[value]
                ),
                "source": "GEMSDOE89",
            })

    path = ROOT / "ledger" / "submissions.csv"
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in new_rows + upstream:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    print(f"wrote {path}: {len(new_rows)} GEMSDOE89 + {len(upstream)} collapsed upstream rows")


if __name__ == "__main__":
    main()
