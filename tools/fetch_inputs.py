#!/usr/bin/env python3
"""Fetch the pinned competition inputs from the owner's GitHub mirrors.

The sandbox has no DrivenData access and must never contact it; every input
listed in registry/data_manifest.json is an owner-supplied mirror pinned by
repo@ref + sha256. This script downloads exactly those blobs via the GitHub
contents API (gh, already authenticated) and verifies every byte.

Multi-part blobs are downloaded part by part and concatenated in order.
Nothing here can guess a hash: a mismatch exits non-zero and leaves the
partial output in place for inspection, never marked verified.

Usage:
    python tools/fetch_inputs.py                 # fetch whatever is missing
    python tools/fetch_inputs.py --force         # re-download everything
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe.grid import sha256_file  # noqa: E402
import json  # noqa: E402


def gh_raw(repo: str, ref: str, path: str, dest: Path) -> None:
    """Download one blob via the GitHub contents API (raw media type)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = f"repos/{repo}/contents/{path}?ref={ref}"
    with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False, suffix=".partdl") as fh:
        tmp = Path(fh.name)
    try:
        # this gh build has no `gh api -o`; stream the raw body to the file
        with open(tmp, "wb") as out:
            # raw accept header makes gh stream the blob bytes to stdout
            subprocess.run(
                ["gh", "api", url, "-H", "Accept: application/vnd.github.raw"],
                check=True, stdout=out,
            )
        tmp.replace(dest)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def fetch_entry(entry: dict, data_root: Path, force: bool) -> dict:
    local = data_root / entry["local"]
    if local.exists() and not force:
        sha = sha256_file(local)
        if sha == entry["sha256"]:
            return {"id": entry["id"], "action": "cached", "ok": True, "sha256": sha}
    if "parts" in entry:
        chunks = []
        try:
            for part in entry["parts"]:
                p = data_root / (entry["local"] + "." + part.rsplit(".", 1)[-1] + ".dl")
                gh_raw(entry["repo"], entry["ref"], part, p)
                chunks.append(p)
            with open(local, "wb") as out:
                for p in chunks:
                    out.write(p.read_bytes())
        finally:
            for p in chunks:
                p.unlink(missing_ok=True)
    else:
        gh_raw(entry["repo"], entry["ref"], entry["path"], local)
    sha = sha256_file(local)
    ok = sha == entry["sha256"]
    return {"id": entry["id"], "action": "downloaded", "ok": ok,
            "sha256": sha, "expected": entry["sha256"], "bytes": local.stat().st_size}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    manifest = json.loads((ROOT / "registry" / "data_manifest.json").read_text())
    data_root = Path(os.environ.get(manifest.get("data_root_env", "GEMSDOE_DATA"),
                                    ROOT / manifest.get("data_root_default", "data")))
    data_root.mkdir(parents=True, exist_ok=True)
    print(f"[data root] {data_root}")
    all_ok = True
    for entry in manifest["files"]:
        r = fetch_entry(entry, data_root, args.force)
        flag = "ok" if r["ok"] else "SHA MISMATCH"
        print(f"[{flag}] {entry['id']:18s} {r['action']:10s} {r['sha256'][:16]}")
        all_ok &= r["ok"]
    if not all_ok:
        print("ERROR: at least one pinned input failed verification")
        return 2
    print("[done] all pinned inputs verified against registry/data_manifest.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
