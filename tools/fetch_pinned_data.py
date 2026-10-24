#!/usr/bin/env python3
"""Fetch and SHA-256-verify pinned inputs declared in registry/data_manifest.json.

Only contacts codeload.github.com (never dropbox.com, never drivendata.org,
never reads/stores credentials). Streams each (repo, ref) tarball at most once,
assembles multi-part files, copies shared archive members to all declared local
destinations, and fails closed on any SHA-256 mismatch.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tarfile
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import BinaryIO

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe.grid import sha256_file  # noqa: E402


def build_wanted_map(entries: list[dict], data_root: Path) -> dict[str, list[Path]]:
    """Map each archive-relative member path to ALL local destination paths."""
    wanted: dict[str, list[Path]] = defaultdict(list)
    for entry in entries:
        if "parts" in entry:
            for p in entry["parts"]:
                wanted[p].append(data_root / f"_part_{entry['id']}_{Path(p).name}")
        else:
            wanted[entry["path"]].append(data_root / entry["local"])
    return wanted


def extract_tarball_entries(stream: BinaryIO, entries: list[dict], data_root: Path) -> list[str]:
    """Stream-extract `entries` from a `.tar.gz` stream into `data_root`.

    Returns sorted missing archive-relative paths (empty list on full success).
    """
    wanted = build_wanted_map(entries, data_root)
    found: set[str] = set()
    with tarfile.open(fileobj=stream, mode="r|gz") as tf:
        for member in tf:
            if not member.isfile():
                continue
            rel = member.name.split("/", 1)[1] if "/" in member.name else member.name
            if rel in wanted:
                src = tf.extractfile(member)
                if src is None:
                    continue
                dests = wanted[rel]
                first = dests[0]
                first.parent.mkdir(parents=True, exist_ok=True)
                with open(first, "wb") as out_fh:
                    shutil.copyfileobj(src, out_fh, length=1 << 20)
                for extra in dests[1:]:
                    extra.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(first, extra)
                found.add(rel)

    missing = sorted(set(wanted) - found)
    if missing:
        return missing

    for entry in entries:
        if "parts" in entry:
            dest = data_root / entry["local"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "wb") as out_fh:
                for p in entry["parts"]:
                    part_path = data_root / f"_part_{entry['id']}_{Path(p).name}"
                    with open(part_path, "rb") as in_fh:
                        shutil.copyfileobj(in_fh, out_fh, length=1 << 20)
                    part_path.unlink()
    return []


def main() -> int:
    manifest = json.loads((ROOT / "registry" / "data_manifest.json").read_text())
    data_root = Path(
        os.environ.get(
            manifest.get("data_root_env", "GEMSDOE_DATA"),
            ROOT / manifest.get("data_root_default", "data"),
        )
    )
    data_root.mkdir(parents=True, exist_ok=True)

    by_repo_ref: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for entry in manifest["files"]:
        if entry.get("unverified"):
            print(f"[skip] unverified report-only pin {entry['id']} (IRREGULARITIES item 8)")
            continue
        dest = data_root / entry["local"]
        if dest.exists() and sha256_file(dest) == entry["sha256"]:
            print(f"[cached-ok] {entry['id']} -> {dest.name} ({entry['sha256'][:12]})")
            continue
        by_repo_ref[(entry["repo"], entry["ref"])].append(entry)

    for (repo, ref), entries in by_repo_ref.items():
        wanted = build_wanted_map(entries, data_root)
        url = f"https://codeload.github.com/{repo}/tar.gz/{ref}"
        print(f"[fetch] {url} ({len(wanted)} member(s))", flush=True)
        req = urllib.request.Request(url, headers={"User-Agent": "GEMSDOE89-ManifestVerify/1.0"})
        with urllib.request.urlopen(req, timeout=600) as resp:
            missing = extract_tarball_entries(resp, entries, data_root)
        if missing:
            print(f"ERROR: missing archive members from {repo}@{ref}: {missing}")
            return 2

    all_ok = True
    for entry in manifest["files"]:
        if entry.get("unverified"):
            print(f"[skip] unverified report-only pin {entry['id']} (IRREGULARITIES item 8)")
            continue
        dest = data_root / entry["local"]
        if not dest.exists():
            print(f"FAIL {entry['id']}: missing {dest}")
            all_ok = False
            continue
        got = sha256_file(dest)
        ok = got == entry["sha256"] and dest.stat().st_size == entry["bytes"]
        print(f"{'PASS' if ok else 'FAIL'} {entry['id']}: sha256={got[:16]} bytes={dest.stat().st_size}")
        if not ok:
            print(f"   expected sha256={entry['sha256']} bytes={entry['bytes']}")
            all_ok = False

    return 0 if all_ok else 2


if __name__ == "__main__":
    sys.exit(main())
