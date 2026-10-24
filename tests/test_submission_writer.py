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


def test_writer_defaults_to_finite_zeros(tmp_path, monkeypatch):
    import json
    import numpy as np
    import submission_writer as writer
    from gemsdoe import grid
    foot = np.zeros((32, 32), bool)
    foot[2:-2, 2:-2] = True
    dots = foot.copy()
    cat = np.zeros_like(foot)
    cat[10, 10] = True
    template = tmp_path / 'template.tif'
    grid.write_submission(template, dots, foot)
    (tmp_path / 'registry').mkdir()
    (tmp_path / 'registry/grid_contract.json').write_text(json.dumps(grid.read_contract_from_tiff(template)))
    monkeypatch.setattr(writer, 'ROOT', tmp_path)
    output = tmp_path / 'candidate.tif'
    masked, receipt = writer.write_candidate(output, dots, foot, cat)
    arr, _ = grid.read_back(output)
    assert np.isfinite(arr).all()
    assert np.all(arr[~foot] == 0)
    assert not masked[10, 10]
    assert receipt['encoding'] == 'zeros'
    assert receipt['all_values_finite']


@pytest.mark.parametrize('bad', [float('nan'), float('inf'), -1, 0.5, 2])
def test_writer_rejects_invalid_masks(tmp_path, bad):
    import numpy as np
    from submission_writer import write_candidate
    mask = np.zeros((4, 4))
    mask[1, 1] = bad
    with pytest.raises(ValueError, match='finite binary'):
        write_candidate(tmp_path / 'bad.tif', mask, np.ones((4, 4)), np.zeros((4, 4)))
