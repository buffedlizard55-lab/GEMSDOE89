# SUBMIT — session GEMSDOE89

The human submits from their own registered account. Nothing here logs in,
scrapes, or uploads. One file per slot; the NaN-outside twin is the one to
upload (the zeros twin is the fallback and scores identically per ledger
history).

## Slot 1 (primary, unchanged)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif` |
| **name** | `h33-h33-2-b2-relief-r10-20261023-366c87ca` |
| **sha256** | `366c87ca620402158cfbbf4911ed8abc8ba2da34f198694c9df7c5ea640ab335` |
| **fallback** | `releases/…-366c87ca-zeros.tif` (`e776fc20873321f7…`) |
| **form note** (122 chars) | `R0 h33-h33-2-b2 + RELIEF r10: 3765/37654 dots (10%) range->piedmont class, count fixed, dcat>=3px, structured; pred +0.003` |
| **predicted** | +0.003 MODEL (band −0.012 … +0.018) |

## Slot 2 (placement fork — built this session)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` |
| **name** | `h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae` |
| **sha256** | `69db3aae7da2311d43a621d0c4d2ab423a3cd39acfea9cf13f666def10fd5c54` |
| **fallback** | `releases/…-69db3aae-zeros.tif` (`0fe545f9de5723e2…`) |
| **form note** (105 chars) | `R0 h33-h33-2-b2 + SNAP 2p0px-g0p00: 31,287/37654 dots moved, mean 1.86 px, targets dcat>=3px; pred +0.028` |
| **predicted** | +0.028 MODEL (band −0.028 … +0.084) — the widest band in the repo; the negative side prices non-fault EM crests |

## Slot 3 (conditional — pick exactly one, or hold)

| condition | file | predicted |
|---|---|---|
| slot 1 scores ≥ **0.2878** | `releases/h33-h33-2-b2-relief-r15-20261023-6aa774ce.tif` (sha `6aa774ce21fe10b3…`, note ≤140 in ledger) | +0.004 MODEL (−0.017 … +0.027) |
| else slot 2 scores ≥ **0.2878** | `releases/h33-h33-2-b2-snap1p4px-g0p00-20261023-e1474851.tif` (sha `e14748519b3fb35c7998d8d4da12014c27374cd13455e1a79730e86fd2e07ab9`) | +0.028 MODEL (−0.028 … +0.083) |
| else | **hold the slot** | — |

Third file kept in reserve: `…-snap1p0px-g0p00-…-1add5aa6.tif` (sha
`1add5aa60487c529eccef3c3a830d7330f36cec0f407cc3fb3d9ceb6bd1b3ef2`,
+0.027 MODEL) — only if two gate-0 receipts are somehow both positive and a
third window point is wanted; the window dose saturates (80.8 → 83.1 % moved),
so prefer holding.

## Format receipt (re-read from disk after writing; data gates live)

| gate | result |
|---|---|
| readable / re-read | pass (all 12 release files) |
| grid contract vs `sample_submission.tif` (shape 3730×3292, pixel scale, tiepoint, geokeys, EPSG:32611) | pass |
| dtype float32, single band | pass |
| values in [0,1]; dots exactly 1.0 | pass |
| no NaN inside footprint; NaN outside (`.tif`) / zeros outside (`-zeros.tif`) | pass |
| dot count 37,654; mask identity across twins | pass |
| zero catalogue mass; moved-target clearance ≥ 3.00 px | pass (inherited 2.236-px parent collar unchanged-or-shrinking: 1,611 → 575 for slot 2) |
| sha256 not already in the ledger | pass (`tools/check_ledger.py`: 121 rows, no duplicate triples, notes ≤140) |

## Before you upload (2 minutes)

```
export GEMSDOE_DATA=/path/to/verified/inputs      # parent, template, catalogue, features
python -m pytest tests -q                          # 25 tests
python tools/validate_raster.py                    # re-runs every gate on every release
python tools/check_ledger.py                       # ledger <-> disk, no duplicate triples
python tools/rebuild_r0.py                         # parent rebuild must print REBUILD MATCH
sha256sum releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif   # must start 69db3aae
```

Then fill `receipt_score` and `receipt_date` in `ledger/submissions.csv` from the
submission-page receipt. Until that exists the file's score is **CLAIM only** —
this repo currently holds no receipt for any file, including the parent's 0.2778.
