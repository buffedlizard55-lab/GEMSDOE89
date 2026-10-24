"""Offline unit tests for tools/fetch_pinned_data.py duplicate archive-member extraction."""

from __future__ import annotations

import io
import tarfile
from pathlib import Path

from tools.fetch_pinned_data import build_wanted_map, extract_tarball_entries


def _make_targz(members: dict[str, bytes]) -> io.BytesIO:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for name, payload in members.items():
            info = tarfile.TarInfo(name=name)
            info.size = len(payload)
            tf.addfile(info, io.BytesIO(payload))
    buf.seek(0)
    return buf


def test_duplicate_archive_member_extracts_to_all_local_destinations(tmp_path: Path):
    """Regression test: scored_h19_5 and parent_field_h19_5 share one archive path."""
    shared_bytes = b"shared-h19-5-payload"
    entries = [
        {"id": "scored_h19_5", "path": "inputs/h19-5.tif", "local": "scored_h19_5.tif"},
        {"id": "parent_field_h19_5", "path": "inputs/h19-5.tif", "local": "parent_field_h19_5.tif"},
        {
            "id": "split_sample",
            "parts": ["parts/p0.bin", "parts/p1.bin"],
            "local": "assembled.bin",
        },
    ]
    wanted = build_wanted_map(entries, tmp_path)
    assert len(wanted["inputs/h19-5.tif"]) == 2

    stream = _make_targz(
        {
            "repo-sha/inputs/h19-5.tif": shared_bytes,
            "repo-sha/parts/p0.bin": b"hello-",
            "repo-sha/parts/p1.bin": b"world",
        }
    )
    missing = extract_tarball_entries(stream, entries, tmp_path)
    assert missing == []
    assert (tmp_path / "scored_h19_5.tif").read_bytes() == shared_bytes
    assert (tmp_path / "parent_field_h19_5.tif").read_bytes() == shared_bytes
    assert (tmp_path / "assembled.bin").read_bytes() == b"hello-world"
