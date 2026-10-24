import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from submission_writer import note_length  # noqa: E402


def test_submission_note_limit_allows_140_and_rejects_141():
    assert note_length("x" * 140) == 140
    with pytest.raises(ValueError, match="maximum is 140"):
        note_length("x" * 141)
