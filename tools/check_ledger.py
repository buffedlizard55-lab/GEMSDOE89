#!/usr/bin/env python3
"""Ledger ↔ filesystem consistency checks (no competition data needed).

Fails if
  * a release raster's sha256 is missing from the ledger,
  * a ledger row with status BUILT has no file on disk,
  * a (parent, axis, value) triple appears twice,
  * any form_note exceeds 140 characters.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gemsdoe.grid import sha256_file  # noqa: E402


def main():
    rows = list(csv.DictReader(open(ROOT / "ledger" / "submissions.csv", newline="")))
    mine = [r for r in rows if r.get("source") == "GEMSDOE89"]
    problems = []

    known = {(r.get("sha256") or "").strip() for r in rows}
    known |= {(r.get("sha256_zeros") or "").strip() for r in rows}
    known.discard("")

    on_disk = {p.name: sha256_file(p) for p in sorted((ROOT / "releases").glob("*.tif"))}
    disk_hashes = set(on_disk.values())

    for name, sha in on_disk.items():
        if sha not in known:
            problems.append(f"release {name} has sha256 {sha[:12]} that is not in the ledger")

    for r in mine:
        for col in ("sha256", "sha256_zeros"):
            h = (r.get(col) or "").strip()
            if h and h not in disk_hashes:
                problems.append(f"ledger row {r['id']} {col} has no file on disk")

    triples = [(r.get("parent"), (r.get("axis") or "").upper(), r.get("value")) for r in rows]
    seen = {}
    for t in triples:
        seen[t] = seen.get(t, 0) + 1
    for t, n in seen.items():
        if n > 1 and t[1]:
            problems.append(f"repeated (parent, axis, value) {t} x{n}")

    for r in mine:
        note = r.get("form_note") or ""
        if len(note) > 140:
            problems.append(f"{r['id']} form_note is {len(note)} chars (max 140)")
        if (r.get("axis") or "").upper() == "TRACKB":
            gj = ROOT / "releases" / f"{r['id']}.geojson"
            if not gj.exists():
                problems.append(f"{r['id']} missing TRACKB GeoJSON {gj.name}")
            else:
                doc = json.loads(gj.read_text(encoding="utf-8"))
                feats = doc.get("features") if isinstance(doc, dict) else None
                if doc.get("type") != "FeatureCollection" or not feats:
                    problems.append(f"{r['id']} invalid FeatureCollection in {gj.name}")
                else:
                    for idx, feat in enumerate(feats):
                        geom = feat.get("geometry") or {}
                        coords = geom.get("coordinates") or []
                        props = feat.get("properties") or {}
                        if geom.get("type") != "LineString" or len(coords) < 2:
                            problems.append(f"{r['id']} feature {idx} invalid LineString")
                            break
                        x0 = float(coords[0][0])
                        is_meters = abs(x0) > 180.0
                        seg_km = 0.0
                        for a, b in zip(coords[:-1], coords[1:]):
                            if is_meters:
                                seg_km += math.hypot(float(b[0]) - float(a[0]), float(b[1]) - float(a[1])) / 1000.0
                            else:
                                latm = math.radians(0.5 * (float(a[1]) + float(b[1])))
                                km_per_deg_lat = 111.13292 - 0.55982 * math.cos(2.0 * latm) + 0.001175 * math.cos(4.0 * latm)
                                km_per_deg_lon = 111.41284 * math.cos(latm) - 0.0935 * math.cos(3.0 * latm)
                                seg_km += math.hypot(
                                    (float(b[0]) - float(a[0])) * km_per_deg_lon,
                                    (float(b[1]) - float(a[1])) * km_per_deg_lat,
                                )
                        if seg_km < 1.0 - 2e-3:
                            problems.append(f"{r['id']} feature {idx} arc length {seg_km:.3f} km < 1.0 km")
                            break
                        if str(r.get("value") or "").startswith("t150") and not str(props.get("evidence") or "").strip():
                            problems.append(f"{r['id']} feature {idx} missing geologist evidence")
                            break

    print(f"ledger rows: {len(rows)} ({len(mine)} this session); release files: {len(on_disk)}")
    if problems:
        for p in problems:
            print("PROBLEM:", p)
        return 2
    print("ledger consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
