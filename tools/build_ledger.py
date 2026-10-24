#!/usr/bin/env python3
"""Assemble ledger/submissions.csv from the recovered upstream history + built
variants in this repository (SPACING + RELIEF + MASS + SNAP + both
CONCENTRATION families).

Upstream rows come from buffedlizard55-lab/GEMSDOE84 ledger/submissions.csv
(copied verbatim to ledger/upstream_GEMSDOE84.csv). Repeats are collapsed on
sha256: a repeated upload of identical bytes teaches nothing and is recorded
once, with a repeat count.

This repository's rows are read from registry/build_reports_spacing.json,
registry/build_reports.json, and registry/build_mass_reports.json so that the
ledger never drifts from the files on disk in releases/.  Each new axis/family
must have a reader here; the 2 km reader uses build_reports_concentration.json.
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

SPACING_PREDICTIONS = {
    "alongstrike": "+0.002 (MODEL; band -0.003..+0.006). No-evidence (<0.01) outcome expected.",
    "poisson": "-0.010 (MODEL; band -0.032..+0.004). Negative unless test truth sits >=250 m off H19-5.",
    "lattice": "-0.007 (MODEL; band -0.025..+0.003). Hex lattice cover; negative if truth hugs H19-5.",
}
SPACING_FORM_NOTES = {
    "alongstrike": "h33-h33-2-b2; SPACING alongstrike: 5222/37654 (13.9%) geodesic 1-swap on >=6-dot strands, n=37654; pred +0.002 (-0.003..+0.006)",
    "poisson": "h33-h33-2-b2; SPACING poisson: 7639/37654 (20.3%) 2D blue-noise disk in +-150m corridor, n=37654; pred -0.010 (-0.032..+0.004)",
    "lattice": "h33-h33-2-b2; SPACING lattice: 7305/37654 (19.4%) 3.5px hex lattice in +-200m corridor, n=37654; pred -0.007 (-0.025..+0.003)",
}
SPACING_RECOMMEND = {
    "alongstrike": "On-ridge 1D geodesic equipartition + exact kernel 1-swap (active ridge cov 0.7101->0.7195); primary SPACING probe.",
    "poisson": "2D Bridson Poisson-disk in d<=1.5px corridor (nn<3px 11415->8119; SGMC cov 0.0888->0.0902); GeoDAWN jitter test.",
    "lattice": "Isometric 3.5px hex lattice in d<=2.0px corridor (nn<3px 11415->7667; SGMC cov 0.0888->0.0893); periodic cover control.",
}

CONCENTRATION_PREDICTIONS = {
    "cat10": "+0.009 (MODEL; band -0.010..+0.038). At the no-evidence line: reads out only if the block prior is real.",
    "cat20": "+0.019 (MODEL; band -0.010..+0.067). 2x dose of cat10.",
    "cat10away": "-0.009 (MODEL; band -0.038..+0.010). Sign control: if the prior is real, this arm must lose.",
}
CONCENTRATION_FORM_NOTES = {
    "cat10": "R0 h33-h33-2-b2; CONC 5km cat-prior t10: 3765/37654 (10%) zero->top25% fault blocks, n37654; pred +0.009",
    "cat20": "R0 h33-h33-2-b2; CONC 5km cat-prior t20: 7531/37654 (20%) zero->top25% fault blocks, n37654; pred +0.019",
    "cat10away": "R0 h33-h33-2-b2; CONC 5km cat-prior t10 AWAY: 3765 (10%) top25%->zero fault blocks; pred -0.009",
}
CONCENTRATION_RECOMMEND = {
    "cat10": "PRIMARY: block prior is catalogued-fault density (r=0.04 with R0 block density); 37.9% of R0 mass sits in zero-fault blocks.",
    "cat20": "DOSE: same rule at 2x. Submit only after cat10 shows a change, or as the single large-effect probe.",
    "cat10away": "SIGN CONTROL: identical placement rule, reversed strata. A gain here falsifies the known-fault prior.",
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
    "r10": "SLOT 1 (RELIEF arm). Lowest dose, smallest downside band.",
    "r15": "Conditional dose-response arm only if r10 lands >= 0.2878 (+0.010); otherwise HOLD.",
    "r15s": "ALTERNATE slope-tercile RELIEF arm.",
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


def _spacing_rows() -> list[dict]:
    p = ROOT / "registry" / "build_reports_spacing.json"
    if not p.exists():
        return []
    rows = []
    for rep in json.loads(p.read_text()):
        value = rep["value"]
        s = rep["stats"]
        rows.append(
            {
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
                "value": value,
                "status": "BUILT",
                "receipt": "N",
                "receipt_score": "",
                "predicted_change": SPACING_PREDICTIONS[value],
                "date": "2026-10-23",
                "form_note": SPACING_FORM_NOTES[value],
                "notes": (
                    f"built 2026-10-23; {s['n_moved']} relocated ({s['pct_changed']:.2f}%, symdiff "
                    f"{s['pct_symmetric_diff']:.2f}%) across {s['active_components']} strands; "
                    f"mean disp {s['mean_displacement_px']:.2f} px; dcat>=3px; 5km CV "
                    f"{s['block_cv_5km_before']:.4f}->{s['block_cv_5km_after']:.4f}. "
                    + SPACING_RECOMMEND[value]
                ),
                "source": "GEMSDOE89",
            }
        )
    return rows


def _relief_rows() -> list[dict]:
    p = ROOT / "registry" / "build_reports.json"
    if not p.exists():
        return []
    rows = []
    for rep in json.loads(p.read_text()):
        value = rep["value"]
        s = rep["stats"]
        rows.append(
            {
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
            }
        )
    return rows


def _snap_rows() -> list[dict]:
    """SNAP (gateless) rows. Added 2026-10-23: without this reader a ledger
    rebuild silently dropped the whole SNAP axis from submissions.csv
    (IRREGULARITIES item 11)."""
    p = ROOT / "registry" / "build_reports_snap.json"
    if not p.exists():
        return []
    rows = []
    for rep in json.loads(p.read_text()):
        s = rep["stats"]
        m = rep["model_prediction"]
        band = m["band"]
        rows.append(
            {
                "id": rep["id"],
                "site": "GEMSDOE89",
                "name": rep["id"],
                "score": "",
                "evidence_class": "BUILT (unscored)",
                "encoding": "nan+zeros",
                "n_dots": s["dots_out"],
                "pct_changed": f"{s['pct_dots_moved']:.2f}",
                "sha8": rep["files"]["sha8"],
                "sha256": rep["files"]["nan"]["sha256"],
                "sha256_zeros": rep["files"]["zeros"]["sha256"],
                "parent": rep["parent"],
                "axis": "SNAP",
                "value": rep["value"],
                "status": "BUILT",
                "receipt": "N",
                "receipt_score": "",
                "predicted_change": (
                    f"{band[0]:+.4f}..{band[2]:+.4f} "
                    f"(MODEL central {m['central']:+.4f}; band prices the mimic)"
                ),
                "date": rep.get("build_date", "20261023"),
                "form_note": rep["form_note"],
                "notes": (
                    f"window {round(rep['spec']['window_px'], 2)} px, gate {rep['spec']['margin']:.2f}, "
                    f"{s['dots_moved']:,} dots moved, mean displacement "
                    f"{s['mean_displacement_px']:.3f} px, moved-target min dcat "
                    f"{s['moved_targets_min_dcat_px']:.2f} px, cv1km "
                    f"{s['block_cv_1km_before']:.3f}->{s['block_cv_1km_after']:.3f}"
                ),
                "source": "GEMSDOE89",
            }
        )
    return rows



def _snap_directional_rows() -> list[dict]:
    """Directional SNAP rows (2026-10-24 session). Same failure mode as
    IRREGULARITIES item 11: an axis without a reader disappears on a rebuild.
    Field strings are reproduced verbatim from tools/build_snap_directional.py."""
    p = ROOT / "registry" / "build_reports_snap_directional.json"
    if not p.exists():
        return []
    rows = []
    for rep in json.loads(p.read_text()):
        s = rep["stats"]
        m = rep["model_prediction"]
        band = m["band"]
        rise = s["elevation_rise_per_move_m"]["mean"] or 0.0
        rows.append(
            {
                "id": rep["id"],
                "site": "GEMSDOE89",
                "name": rep["id"],
                "score": "",
                "evidence_class": "BUILT (unscored)",
                "encoding": "nan+zeros",
                "n_dots": str(s["dots_out"]),
                "pct_changed": f"{s['pct_dots_moved']:.2f}",
                "sha8": rep["files"]["sha8"],
                "sha256": rep["files"]["nan"]["sha256"],
                "sha256_zeros": rep["files"]["zeros"]["sha256"],
                "parent": rep["parent"],
                "axis": "SNAP",
                "value": rep["value"],
                "status": "BUILT",
                "receipt": "N",
                "receipt_score": "",
                "predicted_change": (
                    f"{band[0]:+.4f}..{band[2]:+.4f} "
                    f"(MODEL central {m['central']:+.4f}; sign prior weak, "
                    "read the fw-hw difference)"
                ),
                "date": "20261024",
                "form_note": rep["form_note"],
                "notes": (
                    f"{rep['spec']['direction']} half-window, "
                    f"{rep['spec']['window_px']} px, gate 0.00, "
                    f"{s['dots_moved']:,} dots moved, mean displacement "
                    f"{s['mean_displacement_px']:.3f} px, up-slope share "
                    f"{s['upslope_audit']['share_upslope']}, moved-target min dcat "
                    f"{s['moved_targets_min_dcat_px']:.2f} px, mean elevation rise "
                    f"{rise:+.2f} m, cv1km "
                    f"{s['block_cv_1km_before']:.3f}->{s['block_cv_1km_after']:.3f}"
                ),
                "source": "GEMSDOE89",
            }
        )
    return rows

def _concentration_rows() -> list[dict]:
    p = ROOT / "registry" / "build_concentration_reports.json"
    if not p.exists():
        return []
    rows = []
    for rep in json.loads(p.read_text()):
        value = rep["value"]
        s = rep["stats"]
        rows.append(
            {
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
                "axis": "CONCENTRATION",
                "value": value,
                "status": "BUILT",
                "receipt": "N",
                "receipt_score": "",
                "predicted_change": CONCENTRATION_PREDICTIONS[value],
                "date": "2026-10-23",
                "form_note": CONCENTRATION_FORM_NOTES[value],
                "notes": (
                    f"5km blocks; {s['direction']}: {s['n_moved']} dots moved "
                    f"(symdiff {s['pct_symmetric_diff']:.2f}%), zero-fault-block mass "
                    f"{s['dots_in_zero_blocks_before']}->{s['dots_in_zero_blocks_after']}; "
                    f"CV5km {s['density_cv_5km_before']:.4f}->{s['density_cv_5km_after']:.4f}; "
                    f"corr(prior,density) {s['prior_vs_r0_density_corr_before']:.3f}->"
                    f"{s['prior_vs_r0_density_corr_after']:.3f}; new dots dcat>=3px, sep>=2.8px. "
                    + CONCENTRATION_RECOMMEND[value]
                ),
                "source": "GEMSDOE89",
            }
        )
    return rows


def _concentration_2km_rows() -> list[dict]:
    """Preserve the independent H19-supported 2 km family on every rebuild."""
    p = ROOT / "registry" / "build_reports_concentration.json"
    if not p.exists():
        return []
    rows = []
    for rep in json.loads(p.read_text()):
        s = rep["stats"]
        pred = rep["model_prediction"]
        files = rep["files"]
        rows.append({
            "id": rep["id"], "site": "GEMSDOE89", "name": rep["id"], "score": "",
            "evidence_class": "BUILT (unscored)", "encoding": "nan+zeros",
            "n_dots": s["n_dots"], "pct_changed": f"{s['pct_changed']:.2f}",
            "sha8": files["sha8"], "sha256": files["nan"]["sha256"],
            "sha256_zeros": files["zeros"]["sha256"], "parent": rep["parent"],
            "axis": "CONCENTRATION", "value": rep["value"], "status": "BUILT",
            "receipt": "N", "receipt_score": "",
            "predicted_change": (
                f"MODEL central {pred['central']:+.4f}; sensitivity "
                f"{pred['lo']:+.4f}..{pred['hi']:+.4f} (not a CI)"
            ),
            "date": "20261023", "form_note": rep["form_note"],
            "notes": (
                f"{rep['role']}; 2km CV {s['cv_2km_before']:.4f}->{s['cv_2km_after']:.4f}; "
                f"5km CV {s['cv_5km_before']:.4f}->{s['cv_5km_after']:.4f}; "
                f"H19 counterindicator {s['h19_surrogate_delta']:+.6f}; "
                f"added min dcat {s['added_min_catalogue_clearance_px']:.2f}px"
            ),
            "source": "GEMSDOE89",
        })
    return rows


def _mass_rows() -> list[dict]:
    p = ROOT / "registry" / "build_mass_reports.json"
    if not p.exists():
        return []
    return [
        {
            "id": "h33-h33-2-b2-MASSm10uniq-20261023-beed130f",
            "site": "GEMSDOE89",
            "name": "h33-h33-2-b2-MASSm10uniq-20261023-beed130f",
            "score": "",
            "evidence_class": "BUILT (unscored)",
            "encoding": "nan+zeros",
            "n_dots": 33889,
            "pct_changed": "10.00",
            "sha8": "beed130f",
            "sha256": "beed130f09a9c7e292c8a0a9171ac7dd2a8f19023cf41c8a5f855ba541122f06",
            "sha256_zeros": "312c7ab47c3a1a02894e3ca29e9b93c9e44a387384e5720d8995f22d45ab501c",
            "parent": "h33-h33-2-b2",
            "axis": "MASS",
            "value": "m10uniq",
            "status": "BUILT",
            "receipt": "N",
            "receipt_score": "",
            "predicted_change": "+0.002 (MODEL; band -0.010..+0.010; ceiling +0.0105 if every dropped dot is zero-credit)",
            "date": "2026-10-23",
            "form_note": "R0 h33-h33-2-b2; MASS m10uniq: drop 3765/37654 dots (10%), none added; pred +0.002",
            "notes": "PRIMARY: drop 3765 deepest-redundancy far-field dots, collar preserved (1.5% of drops <3px vs 4.28% base). Predicted small positive; read the m20 dose against it.",
            "source": "GEMSDOE89",
        },
        {
            "id": "h33-h33-2-b2-MASSm10rand-20261023-7a4c49b6",
            "site": "GEMSDOE89",
            "name": "h33-h33-2-b2-MASSm10rand-20261023-7a4c49b6",
            "score": "",
            "evidence_class": "BUILT (unscored)",
            "encoding": "nan+zeros",
            "n_dots": 33889,
            "pct_changed": "10.00",
            "sha8": "7a4c49b6",
            "sha256": "7a4c49b6999421b1b47a12ad7f7c77c1499dad983e87f5620469f36e615a90a0",
            "sha256_zeros": "4cb61fd574b7840729312156f8b5bff5fa0e8d48b3dcb2e06be7ed8dd7dcfa9d",
            "parent": "h33-h33-2-b2",
            "axis": "MASS",
            "value": "m10rand",
            "status": "BUILT",
            "receipt": "N",
            "receipt_score": "",
            "predicted_change": "-0.002 (MODEL; band -0.016..+0.010; the count-matched null for m10uniq)",
            "date": "2026-10-23",
            "form_note": "R0 h33-h33-2-b2; MASS m10rand: drop 3765/37654 dots (10%), none added; pred -0.002",
            "notes": "CONTROL: 3765 dots drawn uniformly. Same count, same legality, only the selection differs from m10uniq. Differences the ranking, not the count.",
            "source": "GEMSDOE89",
        },
        {
            "id": "h33-h33-2-b2-MASSm20uniq-20261023-87ec6213",
            "site": "GEMSDOE89",
            "name": "h33-h33-2-b2-MASSm20uniq-20261023-87ec6213",
            "score": "",
            "evidence_class": "BUILT (unscored)",
            "encoding": "nan+zeros",
            "n_dots": 30123,
            "pct_changed": "20.00",
            "sha8": "87ec6213",
            "sha256": "87ec62139e77771157799304fb47ec8322bce0133ba20b048070cb2973f986f8",
            "sha256_zeros": "e00a58e58194574b9458a1e1433baa1d9eb97af3c8d68913383824d404b27e45",
            "parent": "h33-h33-2-b2",
            "axis": "MASS",
            "value": "m20uniq",
            "status": "BUILT",
            "receipt": "N",
            "receipt_score": "",
            "predicted_change": "+0.004 (MODEL; band -0.020..+0.021; ceiling +0.021 if every dropped dot is zero-credit)",
            "date": "2026-10-23",
            "form_note": "R0 h33-h33-2-b2; MASS m20uniq: drop 7531/37654 dots (20%), none added; pred +0.004",
            "notes": "DOSE: 7531 deepest-redundancy far-field dots. Largest ceiling in the family; submit only after m10uniq reads positive.",
            "source": "GEMSDOE89",
        },
    ]


def _concentration_12p8km_rows() -> list[dict]:
    """Preserve the 12.8 km Faulds fault-interaction + catalogue-free GPS strain family."""
    p = ROOT / "registry" / "build_reports_concentration_12p8km.json"
    if not p.exists():
        return []
    rows = []
    for rep in json.loads(p.read_text()):
        s = rep["stats"]
        spec = rep["spec"]
        rows.append(
            {
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
                "axis": "CONCENTRATION",
                "value": rep["value"],
                "status": "BUILT",
                "receipt": "N",
                "receipt_score": "",
                "predicted_change": spec["predicted_change_text"],
                "date": "",
                "form_note": rep["form_note"],
                "notes": (
                    f"built 2026-10-23; 12.8km (128px) blocks; move {s['n_moved']} dots ({s['pct_changed']:.2f}%, "
                    f"symdiff {s['pct_symmetric_diff']:.2f}%) bot40->top40 {spec['prior']} prior; "
                    f"count fixed 37,654; dcat_added>=3.00px (collar<3px frozen at 1611); "
                    f"r_sep>=2.80px; CV12.8km {s['block_cv_12p8km_before']:.4f}->{s['block_cv_12p8km_after']:.4f} "
                    f"(CV5km {s['block_cv_5km_before']:.4f}->{s['block_cv_5km_after']:.4f}); "
                    f"mean disp {s['mean_displacement_px']:.1f}px"
                ),
                "source": "GEMSDOE89",
            }
        )
    return rows


def _trackb_rows() -> list[dict]:
    """TRACKB (Phase 2) rows. Added 2026-10-24: without a reader here a
    ledger rebuild would drop the TRACKB row while its release files stay
    on disk (the SNAP failure mode, IRREGULARITIES item 11)."""
    p = ROOT / "registry" / "build_reports_trackb.json"
    if not p.exists():
        return []
    rows = []
    for rep in json.loads(p.read_text()):
        s = rep["stats"]
        rows.append(
            {
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
                "axis": "TRACKB",
                "value": rep["value"],
                "status": "BUILT",
                "receipt": "N",
                "receipt_score": "",
                "predicted_change": "n/a (Phase 2 trace product; not a weekly-slot candidate; do not submit for score)",
                "date": "2026-10-24",
                "form_note": "R0 h33-h33-2-b2; TRACKB top12: 12 strike-consistent traces >=1km, 145 member dots, GeoJSON; Phase 2 only",
                "notes": (
                    f"built 2026-10-24; {s['n_traces']} traces, {s['total_length_km']:.1f} km total, "
                    f"{s['n_dots']} member dots (all R0 dots, zero catalogue mass); "
                    "strand-credit top-2/3 dots linked 4.5px, R>=0.85, straightness>=0.60; "
                    "evidence paragraphs in ledger/TRACKB_TRACES.md; GeoJSON EPSG:32611 in releases/."
                ),
                "source": "GEMSDOE89",
            }
        )
    return rows


def _trackb_150_rows() -> list[dict]:
    """R0-consolidating 150-trace TRACKB arms (t150add, t150swap, t150link)."""
    p = ROOT / "registry" / "build_reports_trackb_150.json"
    if not p.exists():
        return []
    rows = []
    for rep in json.loads(p.read_text()):
        s = rep["stats"]
        rows.append(
            {
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
                "axis": "TRACKB",
                "value": rep["value"],
                "status": "BUILT",
                "receipt": "N",
                "receipt_score": "",
                "predicted_change": rep["spec"]["predicted_change_text"],
                "date": "",
                "form_note": rep["form_note"],
                "notes": (
                    f"built 2026-10-24 (Phase 2 TRACKB); {s['n_traces_emitted']} strike-consistent traces >=1.0km "
                    f"({s['total_trace_chord_km']:.1f}km chord, {s['n_bridged_traces']} wash-bridged); "
                    f"add {s['n_added']}/drop {s['n_removed']} ({s['pct_changed']:.2f}%, symdiff {s['pct_symmetric_diff']:.2f}%); "
                    f"n={s['n_dots']}; dcat_added>=3.00px (collar<3px frozen at 1611); "
                    f"CV12.8km {s['block_cv_12p8km_before']:.4f}->{s['block_cv_12p8km_after']:.4f}; "
                    f"GeoJSON={rep['files']['geojson']}"
                ),
                "source": "GEMSDOE89",
            }
        )
    return rows


def main():
    path = ROOT / "ledger" / "submissions.csv"
    existing_by_id: dict[str, dict] = {}
    if path.exists():
        try:
            with open(path, newline="") as fh:
                for r in csv.DictReader(fh):
                    if r.get("id") and not str(r.get("id")).startswith(("<<<<<<<", "=======", ">>>>>>>")):
                        existing_by_id[r["id"]] = r
        except Exception:
            existing_by_id = {}

    with open(UPSTREAM, newline="") as fh:
        upstream = collapse(list(csv.DictReader(fh)))

    new_rows = (
        _spacing_rows()
        + _relief_rows()
        + _mass_rows()
        + _snap_rows()
        + _snap_directional_rows()
        + _concentration_rows()
        + _concentration_2km_rows()
        + _concentration_12p8km_rows()
        + _trackb_rows()
        + _trackb_150_rows()
    )
    for r in new_rows:
        prev = existing_by_id.get(r["id"])
        if prev:
            for human_col in ("status", "receipt", "receipt_score", "date", "score"):
                if prev.get(human_col) and not r.get(human_col):
                    r[human_col] = prev[human_col]

    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in new_rows + upstream:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    print(f"wrote {path}: {len(new_rows)} GEMSDOE89 + {len(upstream)} collapsed upstream rows")


if __name__ == "__main__":
    main()
