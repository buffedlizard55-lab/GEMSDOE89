#!/usr/bin/env python3
"""Fetch and SHA-256-verify all inputs pinned in registry/data_manifest.json.

Hard constraints enforced:
  * Contacts ONLY codeload.github.com (never drivendata.org, never dropbox.com).
  * Never reads, requests, stores, or prints credentials.
  * Streams each (repo, ref) tarball once, extracts only pinned paths, assembles
    split parts, and fails closed if any file's SHA-256 or byte size mismatches.
  * Writes into $GEMSDOE_DATA (default ./data/, git-ignored).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tarfile
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe.grid import sha256_file  # noqa: E402

ALLOWED_HOST = "codeload.github.com"


def _tarball_url(repo: str, ref: str) -> str:
    url = f"https://{ALLOWED_HOST}/{repo}/tar.gz/{ref}"
    if ALLOWED_HOST not in url or "dropbox" in url or "drivendata" in url:
        raise ValueError(f"forbidden URL: {url}")
    return url


def fetch_missing(manifest: dict, data_root: Path, only_ids: set[str] | None = None) -> dict:
    data_root.mkdir(parents=True, exist_ok=True)
    entries = [
        f for f in manifest["files"]
        if only_ids is None or f["id"] in only_ids
    ]

    # Check already-present files first
    todo = []
    receipt = {}
    for entry in entries:
        dest = data_root / entry["local"]
        if dest.exists():
            sha = sha256_file(dest)
            size = dest.stat().st_size
            if sha == entry["sha256"] and size == entry["bytes"]:
                receipt[entry["id"]] = {
                    "local": entry["local"],
                    "sha256": sha,
                    "bytes": size,
                    "verified": True,
                    "status": "cached",
                }
                continue
        todo.append(entry)

    by_source: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for entry in todo:
        by_source[(entry["repo"], entry["ref"])].append(entry)

    for (repo, ref), group in by_source.items():
        wanted: dict[str, Path] = {}
        for entry in group:
            if "parts" in entry:
                for p in entry["parts"]:
                    wanted[p] = data_root / f"_part_{entry['id']}_{Path(p).name}"
            else:
                wanted[entry["path"]] = data_root / f"_tmp_{entry['local']}"

        url = _tarball_url(repo, ref)
        t0 = time.time()
        print(f"[fetch] streaming {repo}@{ref[:12]} ({len(wanted)} blob(s)) ...")
        req = urllib.request.Request(url, headers={"User-Agent": "gemsdoe89-manifest-verifier/1.0"})
        found = set()
        with urllib.request.urlopen(req, timeout=300) as resp:
            with tarfile.open(fileobj=resp, mode="r|gz") as tf:
                for member in tf:
                    if not member.isfile():
                        continue
                    rel = member.name.split("/", 1)[1] if "/" in member.name else member.name
                    if rel in wanted:
                        out_p = wanted[rel]
                        src = tf.extractfile(member)
                        assert src is not None
                        with open(out_p, "wb") as out_fh:
                            while True:
                                buf = src.read(1 << 20)
                                if not buf:
                                    break
                                out_fh.write(buf)
                        found.add(rel)
                        if len(found) == len(wanted):
                            break

        missing_blobs = sorted(set(wanted) - found)
        if missing_blobs:
            raise RuntimeError(f"missing {missing_blobs} in {repo}@{ref}")

        for entry in group:
            dest = data_root / entry["local"]
            if "parts" in entry:
                tmp_assembled = data_root / f"_tmp_{entry['local']}"
                with open(tmp_assembled, "wb") as out_fh:
                    for p in entry["parts"]:
                        part_p = wanted[p]
                        with open(part_p, "rb") as in_fh:
                            while True:
                                buf = in_fh.read(1 << 20)
                                if not buf:
                                    break
                                out_fh.write(buf)
                        part_p.unlink()
                tmp_assembled.replace(dest)
            else:
                wanted[entry["path"]].replace(dest)

            sha = sha256_file(dest)
            size = dest.stat().st_size
            if sha != entry["sha256"] or size != entry["bytes"]:
                dest.unlink(missing_ok=True)
                raise RuntimeError(
                    f"hash/size mismatch for {entry['id']}: got {sha} ({size} B), "
                    f"expected {entry['sha256']} ({entry['bytes']} B)"
                )
            receipt[entry["id"]] = {
                "local": entry["local"],
                "sha256": sha,
                "bytes": size,
                "verified": True,
                "status": f"fetched ({time.time() - t0:.1f}s)",
            }
            print(f"[ok] {entry['id']:32s}  sha256={sha[:12]}  bytes={size:,}")

    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ids", nargs="*", default=None, help="subset of manifest ids to fetch")
    args = ap.parse_args()

    manifest = json.loads((ROOT / "registry" / "data_manifest.json").read_text())
    data_root = Path(
        os.environ.get(
            manifest.get("data_root_env", "GEMSDOE_DATA"),
            ROOT / manifest.get("data_root_default", "data"),
        )
    )
    only = set(args.ids) if args.ids else None
    receipt = fetch_missing(manifest, data_root, only_ids=only)
    all_ok = len(receipt) == (len(only) if only else len(manifest["files"])) and all(
        v["verified"] for v in receipt.values()
    )
    print(f"[done] verified {len(receipt)}/{len(manifest['files'])} manifest file(s); ok={all_ok}")
    return 0 if all_ok else 2


if __name__ == "__main__":
    sys.exit(main())
