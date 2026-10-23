# GEMSDOE89 — DrivenData #306 (DOE GEMS Prize), AXIS = RELIEF

<!-- CURRENT STATE — edit only this block -->

**CURRENT STATE (2026-10-23)**

- **Parent:** `R0 = h33-h33-2-b2` — 37,654 unit-mass dots, 0 within 2 px of the catalogue.
  **Rebuild: byte-exact** (`zeros c55bafc4…`, `nan baeae321…`), re-executed from the recorded
  H19-5 → D1.5 → D2.8 → SOLO-D2.8 → R0 recipe; see `registry/r0_verification.json`.
- **Best receipt:** none. 0.2778 is a **CLAIM**; no submission receipt exists for any file in this
  lineage.
- **TOP_PUBLIC:** `____` (human fills, with date; sibling session recorded 0.4413 on 2026-10-22, CLAIM).
- **Slots left this week:** `__ / 3` (human fills).
- **Next 3 slots:** 1) `…RELIEFbasin10…d1a3b00d` · 2) `…RELIEFpied10…b0285b17` (reshuffle control)
  · 3) `…RELIEFrf10…7d62b548`. Predicted live change ≈ +0.008 each (MODEL); tercile contrast
  ≈ ±0.002 → below the 0.01 evidence bar. Files, names, notes, receipts: `docs/SUBMIT.md`.

<!-- END CURRENT STATE -->

## What this repository is

One session of a controlled climb on a fixed parent, for one human competitor. Three RELIEF
variants of R0 that differ **only** in which detrended-elevation tercile receives the shifted mass.
Nothing here is submitted automatically and nothing here is a score.

| Path | Contents |
|---|---|
| `registry/data_manifest.json` | 10 SHA-256-pinned inputs, frozen commit refs, provenance, licences |
| `registry/r0_verification.json` | the byte-exact parent rebuild, stage by stage |
| `registry/relief_build.json` | the RELIEF build parameters (tercile edges, slope threshold, k) |
| `scripts/` | restore → rebuild → analyse → build → report → validate |
| `src/gems89/` | DTI algebra (`metric.py`), grid/format gates (`grid.py`) |
| `releases/<id>.json` | per-variant receipts: hashes, gates, parent diff, proxy |
| `ledger/submissions.csv` | 23 rows: 20 inherited, 3 built here; receipts are the human's to fill |
| `evidence/` | RELIEF analysis, canary, axis report (report-only instruments) |
| `SLOT_PLAN.md` | the next three slots and the weeks to 2026-12-03 |
| `docs/SUBMIT.md` | file, name, note, format receipt for each slot |
| `IRREGULARITIES.md` | only items that change a decision |
| `AI_USE.md` | what AI wrote, what the human decided |

## Reproduce

```bash
pip install -r requirements.txt
python3 scripts/restore_inputs.py        # api.github.com only; sha256 + byte length fail-closed
python3 scripts/rebuild_r0.py            # must print ok:true with both parent hashes exact
python3 scripts/build_relief_variants.py
python3 scripts/validate_release.py      # exit 0 = every MUST gate passes
pytest -q
```

Competition rasters are **never** tracked here: `data/` and `releases/*.tif` are gitignored.
The entity uploads one file per slot from their own account; this repository only builds candidates
and records receipts.
