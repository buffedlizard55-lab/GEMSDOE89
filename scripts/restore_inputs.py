#!/usr/bin/env python3
"""Restore and verify every pinned input in registry/data_manifest.json.

Transport is api.github.com only (the sandbox allowlist excludes
raw.githubusercontent.com and dropbox.com).  Every download is pinned to a
frozen commit ref and must match the recorded SHA-256 and byte length; a
mismatch is fail-closed.

Usage:
    python3 scripts/restore_inputs.py                 # everything
    python3 scripts/restore_inputs.py --only sample_submission,existing_faults
    python3 scripts/restore_inputs.py --check         # verify present files only
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry" / "data_manifest.json"
RECEIPT = ROOT / "registry" / "restore_receipt.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def gh_raw(repo: str, ref: str, path: str, out: Path) -> None:
    """Download one blob through api.github.com at a frozen ref."""
    out.parent.mkdir(parents=True, exist_ok=True)
    api = f"repos/{repo}/contents/{path}?ref={ref}"
    tmp = out.with_suffix(out.suffix + ".part")
    with tmp.open("wb") as fh:
        proc = subprocess.run(
            ["gh", "api", "-H", "Accept: application/vnd.github.raw", api],
            stdout=fh,
            stderr=subprocess.PIPE,
            check=False,
        )
    if proc.returncode != 0:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"gh api failed for {repo}@{ref}:{path}: {proc.stderr.decode()[:300]}")
    tmp.replace(out)


def restore_entry(entry: dict, check_only: bool) -> dict:
    dest = ROOT / entry["dest"]
    want_sha, want_bytes = entry["sha256"], entry["bytes"]
    status = "present"
    if not (dest.is_file() and dest.stat().st_size == want_bytes and sha256_file(dest) == want_sha):
        if check_only:
            raise FileNotFoundError(f"missing or unverifiable pin {entry['id']}: {dest}")
        dest.unlink(missing_ok=True)
        sources = entry["sources"]
        if len(sources) == 1 and "sha256" not in sources[0]:
            gh_raw(sources[0]["repo"], sources[0]["ref"], sources[0]["path"], dest)
            status = "downloaded"
        else:
            # split blob: verify each part, then concatenate in recorded order
            part_dir = dest.parent / (dest.name + ".parts")
            part_dir.mkdir(parents=True, exist_ok=True)
            paths = []
            for i, part in enumerate(sources):
                p = part_dir / f"{i:03d}.part"
                gh_raw(part["repo"], part["ref"], part["path"], p)
                got = sha256_file(p)
                if got != part["sha256"]:
                    raise ValueError(f"part {part['path']} sha mismatch: {got} != {part['sha256']}")
                paths.append(p)
            with dest.open("wb") as out:
                for p in paths:
                    with p.open("rb") as fh:
                        for chunk in iter(lambda: fh.read(1 << 22), b""):
                            out.write(chunk)
            for p in paths:
                p.unlink(missing_ok=True)
            part_dir.rmdir()
            status = "downloaded+assembled"
    got_sha, got_bytes = sha256_file(dest), dest.stat().st_size
    if got_sha != want_sha or got_bytes != want_bytes:
        raise ValueError(f"PIN FAILURE {entry['id']}: sha {got_sha} bytes {got_bytes} != {want_sha} / {want_bytes}")
    return {"id": entry["id"], "dest": entry["dest"], "status": status,
            "sha256": got_sha, "bytes": got_bytes, "ok": True}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    wanted = {s.strip() for s in args.only.split(",") if s.strip()}
    rows = []
    for entry in manifest["files"]:
        if wanted and entry["id"] not in wanted:
            continue
        print(f"[restore] {entry['id']} -> {entry['dest']}", flush=True)
        rows.append(restore_entry(entry, args.check))
    payload = {"schema": "gems89.restore.v1", "manifest": "registry/data_manifest.json",
               "checked_only": args.check, "files": rows,
               "all_ok": all(r["ok"] for r in rows)}
    RECEIPT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({r["id"]: r["status"] for r in rows}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
