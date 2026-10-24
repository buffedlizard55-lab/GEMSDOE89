"""Verify byte-exact SHA-256 pins of the shared `vendor/gems57` evaluator/writer template."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_vendor_gems57_pins_match_manifest() -> None:
    pins_path = ROOT / "registry" / "vendor_pins.json"
    assert pins_path.exists(), "missing registry/vendor_pins.json"
    manifest = json.loads(pins_path.read_text(encoding="utf-8"))
    assert manifest["source_repo"] == "buffedlizard55-lab/GEMSDOE78"
    assert len(manifest["files"]) == manifest["n_files"] >= 20

    actual_files = sorted(
        p.relative_to(ROOT).as_posix()
        for p in (ROOT / "vendor" / "gems57").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    )
    assert actual_files == sorted(manifest["files"].keys())

    for rel, meta in manifest["files"].items():
        p = ROOT / rel
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        assert digest == meta["sha256"], f"vendor pin drift in {rel}"
        assert p.stat().st_size == meta["bytes"], f"vendor size drift in {rel}"
