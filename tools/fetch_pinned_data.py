#!/usr/bin/env python3
"""Fetch and SHA-256-verify pinned inputs declared in registry/data_manifest.json.

Only contacts codeload.github.com (never dropbox.com, never drivendata.org,
never reads/stores credentials). Streams each (repo, ref) tarball at most once,
assembles multi-part files, and fails closed on any SHA-256 mismatch.
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe.grid import sha256_file  # noqa: E402


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
        # One archive member can back multiple manifest aliases (for example
        # scored_h19_5.tif and h19_5.tif).  Keep every destination instead of
        # silently overwriting the first alias in a path-keyed dictionary.
        wanted: dict[str, list[Path]] = defaultdict(list)
        for entry in entries:
            if "parts" in entry:
                for p in entry["parts"]:
                    wanted[p].append(data_root / f"_part_{entry['id']}_{Path(p).name}")
            else:
                wanted[entry["path"]].append(data_root / entry["local"])

        url = f"https://codeload.github.com/{repo}/tar.gz/{ref}"
        print(f"[fetch] {url} ({len(wanted)} member(s))", flush=True)
        req = urllib.request.Request(url, headers={"User-Agent": "GEMSDOE89-ManifestVerify/1.0"})
        found: set[str] = set()
        with urllib.request.urlopen(req, timeout=600) as resp:
            with tarfile.open(fileobj=resp, mode="r|gz") as tf:
                for member in tf:
                    if not member.isfile():
                        continue
                    rel = member.name.split("/", 1)[1] if "/" in member.name else member.name
                    if rel in wanted:
                        src = tf.extractfile(member)
                        if src is None:
                            continue
                        out_paths = wanted[rel]
                        for out_path in out_paths:
                            out_path.parent.mkdir(parents=True, exist_ok=True)
                        primary = out_paths[0]
                        with open(primary, "wb") as out_fh:
                            shutil.copyfileobj(src, out_fh, length=1 << 20)
                        for alias in out_paths[1:]:
                            shutil.copyfile(primary, alias)
                        found.add(rel)

        missing = set(wanted) - found
        if missing:
            print(f"ERROR: missing archive members from {repo}@{ref}: {sorted(missing)}")
            return 2

        for entry in entries:
            if "parts" in entry:
                dest = data_root / entry["local"]
                with open(dest, "wb") as out_fh:
                    for p in entry["parts"]:
                        part_path = data_root / f"_part_{entry['id']}_{Path(p).name}"
                        with open(part_path, "rb") as in_fh:
                            shutil.copyfileobj(in_fh, out_fh, length=1 << 20)
                        part_path.unlink()

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
