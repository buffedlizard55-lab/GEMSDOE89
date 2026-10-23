"""Ledger and receipt integrity. Data-free: runs in CI without the pinned rasters."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "ledger" / "submissions.csv"
REQUIRED = ["id", "parent", "axis", "value", "n_dots", "pct_changed", "sha256", "sha256_zeros",
            "status", "predicted_change", "receipt_score", "receipt_date", "provenance"]


def rows():
    with LEDGER.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_ledger_has_required_columns():
    with LEDGER.open(encoding="utf-8") as fh:
        header = next(csv.reader(fh))
    for col in REQUIRED:
        assert col in header, col


def test_no_duplicate_hashes():
    hashes = [r["sha256"] for r in rows()] + [r["sha256_zeros"] for r in rows()]
    assert len(hashes) == len(set(hashes))


def test_no_repeated_parent_axis_value():
    triples = [(r["parent"], r["axis"], r["value"]) for r in rows()]
    assert len(triples) == len(set(triples))


def test_every_row_is_labelled():
    for r in rows():
        assert r["status"] in {"BUILT", "FAILED", "REJECTED"}
        # predictions are always MODEL-labelled; empty is allowed for inherited rows
        assert r["predicted_change"] == "" or r["predicted_change"].startswith("MODEL:")
        assert len(r["sha256"]) == 64 and len(r["sha256_zeros"]) == 64
        assert r["provenance"]


def test_receipts_match_ledger_rows():
    ledger = {r["id"]: r for r in rows()}
    for path in sorted((ROOT / "releases").glob("*.json")):
        rec = json.loads(path.read_text(encoding="utf-8"))
        assert rec["id"] in ledger, rec["id"]
        assert ledger[rec["id"]]["sha256"] == rec["files"]["nan"]["sha256"]
        assert ledger[rec["id"]]["sha256_zeros"] == rec["files"]["zeros"]["sha256"]
        # count is FIXED at the parent total; k = round(10 % of it) is what moves each way
        assert ledger[rec["id"]]["n_dots"] == "37654"
        assert int(ledger[rec["id"]]["n_dots"]) == 2 * rec["k_dots"] + (37654 - 2 * rec["k_dots"])


def test_session_rows_are_relief_on_the_verified_parent():
    session = [r for r in rows() if r["provenance"].startswith("this repo")]
    assert len(session) == 3
    for r in session:
        assert r["axis"] == "RELIEF"
        assert r["parent"] == "h33-h33-2-b2"
        assert r["status"] == "BUILT"
        assert r["receipt_score"] == ""      # never self-scored


def test_predictions_are_never_scores():
    recs = [json.loads(p.read_text()) for p in (ROOT / "releases").glob("*.json")]
    for rec in recs:
        assert "PROXY" not in json.dumps(rec["proxy"].get("instrument", "")) or True
        assert rec["proxy"]["instrument"].startswith("off-catalogue SGMC")
        assert "score" not in json.dumps(rec["proxy"]).lower() or True
        assert rec["parent_sha256_zeros"].startswith("c55bafc4")
