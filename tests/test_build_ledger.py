from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_ledger  # noqa: E402


def test_negative_run_card_artifacts_are_included_in_ledger_rows():
    rows = build_ledger._negative_run_card_rows()
    by_id = {row["id"]: row for row in rows}

    assert len(rows) == 2
    assert {row["axis"] for row in rows} == {"ANNULUS", "PF-PEAKS"}
    for row in rows:
        assert row["status"] == "NEGATIVE (do not submit)"
        assert row["evidence_class"] == "HOLDOUT-DTI"
        assert row["encoding"] == "nan"
        assert row["receipt"] == "N"
        assert len(row["form_note"]) <= 140
        assert len(row["sha256"]) == 64
        assert "HOLDOUT-DTI" in row["predicted_change"]

    assert any("annulus" in name for name in by_id)
    assert any("pfpeaks" in name for name in by_id)
