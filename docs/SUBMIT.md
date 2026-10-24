# SUBMIT — GEMSDOE89 / SNAP factorial completion (2026-10-24)

The human submits manually from their own registered account. Nothing here logs in, scrapes, or uploads. Upload the NaN-outside `.tif`; `-zeros.tif` is only a fallback. **Never upload both twins in separate slots.** Submission name = the file stem.

## This session's three new builds

| role | file / submission name (stem) | sha256 (`.tif` / `-zeros.tif`) | form note (104 chars) |
|---|---|---|---|
| **PRIMARY NEW** | `releases/h33-h33-2-b2-snap1p4px-g0p01-20261024-afc60a25.tif` | `afc60a25d0ceb28295139fb0ad403132da32f07b1da845565326f3db39eb5b01` / `0695a30587b9805b76ccc31d3e54312c061cfdc40055f71351b3a56c9a02d17f` | `R0 h33-h33-2-b2 + SNAP 1p4px-g0p01: 6,767/37654 dots moved, mean 1.37 px, targets dcat>=3px; pred +0.012` |
| **CONDITIONAL WINDOW CONTROL** | `releases/h33-h33-2-b2-snap1p0px-g0p01-20261024-2916ec2d.tif` | `2916ec2d31ebc9c25164686a9dec63f781604cad927869e8aec836143c78652c` / `0b4fad309e26eb49e0ca2707cd5a58f8f675acfbdfff0f0c6192945dcbe163ea` | `R0 h33-h33-2-b2 + SNAP 1p0px-g0p01: 4,265/37654 dots moved, mean 1.00 px, targets dcat>=3px; pred +0.008` |
| **HELD HIGH-GATE BOUNDARY** | `releases/h33-h33-2-b2-snap1p0px-g0p02-20261024-384435e6.tif` | `384435e608fdc6b4a1e8218ef7c3454d6970b4f5149cd3e945082f666761d6ae` / `8592f23b22a29f72bbab714d296b4f14c04276803063d553f2e44d0a41a5511d` | `R0 h33-h33-2-b2 + SNAP 1p0px-g0p02: 1,245/37654 dots moved, mean 1.00 px, targets dcat>=3px; pred +0.002` |

## Next 3 slots

1. **Slot 1 — `afc60a25` primary above.** Prediction `+0.0120 MODEL` (`−0.0060…+0.0301`).
2. **Slot 2 — matched gateless control:**
   - file/name: `releases/h33-h33-2-b2-snap1p4px-g0p00-20261023-e1474851.tif` / stem
   - fallback: `releases/h33-h33-2-b2-snap1p4px-g0p00-20261023-e1474851-zeros.tif`
   - sha256: `e14748519b3fb35c7998d8d4da12014c27374cd13455e1a79730e86fd2e07ab9`
   - form note: `R0 h33-h33-2-b2 + SNAP 1p4px-g0p00: 31,233/37654 dots moved, mean 1.35 px, targets dcat>=3px; pred +0.028`
   - prediction: `+0.0278 MODEL` (`−0.0278…+0.0834`). Compare its receipt directly with Slot 1; only gate differs.
3. **Slot 3 — conditional after Slots 1–2 receipts:**
   - Slot 1 beats Slot 2 by `>=0.010` → `2916ec2d` above (fixed gate, smaller window).
   - Otherwise either SNAP receipt is `>=0.2878` → `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif`; name = stem; note: `R0 h33-h33-2-b2 + SNAP 2p0px-g0p00: 31,287/37654 dots moved, mean 1.86 px, targets dcat>=3px; pred +0.028`.
   - Otherwise both SNAP results are null → `releases/h33-h33-2-b2-CONC5kmcat20-20261023-4d229938.tif` **or HOLD**; name = stem; note: `R0 h33-h33-2-b2; CONC 5km cat-prior t20: 7531/37654 (20%) zero->top25% fault blocks, n37654; pred +0.019`.

## Format receipt — re-read from disk

| gate | result |
|---|---|
| Grid vs pinned `sample_submission.tif`: `3730×3292`, 100 m, EPSG:32611, float32, one band | **PASS ×48 files** |
| Values `[0,1]`; unit dots; no NaN inside footprint; NaN/0 outside by twin | **PASS ×48 files** |
| Dot counts and identical NaN/zeros masks | **PASS ×24 pairs**; all three new pairs = 37,654 |
| Zero catalogue mass; new SNAP moved targets `d_cat>=3.00 px` | **PASS** |
| Exact-hash and `(parent,axis,value)` dedupe; form notes `<=140` chars | **PASS** (`139` ledger rows, `24` local + `115` collapsed upstream) |
| R0 recipe rebuild vs both SHA-256 pins | **PASS** |
| Unit tests / leakage canary | **64 passed** / **PASS** (`SNAP max AUC 0.66538 < 0.90`) |

Machine receipts: `registry/format_receipts.json`, `registry/build_report_snap_<value>.json`, and `registry/report_only_status.json`. PROXY/MODEL diagnostics never gate an upload.

## Pre-upload verification

```bash
export GEMSDOE_DATA=/path/to/verified/inputs
python tools/fetch_pinned_data.py
python tools/rebuild_r0.py
python -m pytest tests -q
python tools/build_ledger.py
python tools/validate_raster.py
python tools/check_ledger.py
sha256sum releases/h33-h33-2-b2-snap1p4px-g0p01-20261024-afc60a25.tif  # must start afc60a25
```

After each upload, the human records `receipt_score` and `date` in `ledger/submissions.csv` (`receipt=Y`, `status=SUBMITTED`).
