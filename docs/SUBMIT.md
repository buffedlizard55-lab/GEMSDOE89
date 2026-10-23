> **2026-10-23 audit: HOLD — do not upload these files.** The start gate failed:
> no local pinned inputs and no recipe rebuild of R0. Historical all-gates-pass
> claims below are superseded: current checks are format-only, and prior records
> report inherited catalogue clearance below the mandatory 3 px for RELIEF.
> Existing predictions are MODEL only. Require a parent receipt before using
> absolute score thresholds; 0.2778 remains CLAIM. No new candidates were built.

# SUBMIT — session GEMSDOE89

The human submits from their own registered account. Nothing here logs in,
scrapes, or uploads. One file per slot; the NaN-outside twin is the one to
upload (the zeros twin is the fallback and scores identically per ledger
history).

## Slot 1 (primary)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif` |
| **name** | `h33-h33-2-b2-relief-r10-20261023-366c87ca` |
| **sha256** | `366c87ca620402158cfbbf4911ed8abc8ba2da34f198694c9df7c5ea640ab335` |
| **fallback** | `releases/h33-h33-2-b2-relief-r10-20261023-366c87ca-zeros.tif` (`e776fc20873321f7…`) |
| **form note** (122 chars) | `R0 h33-h33-2-b2 + RELIEF r10: 3765/37654 dots (10%) range->piedmont class, count fixed, dcat>=3px, structured; pred +0.003` |
| **predicted** | +0.003 MODEL (band −0.012 … +0.018) |

Format receipt — all gates pass, re-read from disk after writing:

| gate | result |
|---|---|
| readable / re-read | pass |
| grid contract vs `sample_submission.tif` (shape, pixel scale, tiepoint, geokeys, EPSG:32611) | pass |
| dtype float32, single band, shape 3730×3292 | pass |
| values in [0,1] | pass (all dots exactly 1.0, all else 0 or NaN) |
| no NaN inside footprint; NaN outside | pass |
| dot count 37,654 and mask identity | pass |
| zero catalogue mass | pass |
| added-dot clearance from catalogue ≥ 3.00 px | pass by construction (measured min 3.00 px) |
| sha256 not already in the ledger | pass |
| twins carry an identical dot mask | pass |

## Slot 2 (conditional)

Submit only if slot 1 scores **≥ 0.2878** (parent 0.2778 + 0.010).

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-relief-r15-20261023-6aa774ce.tif` |
| **name** | `h33-h33-2-b2-relief-r15-20261023-6aa774ce` |
| **sha256** | `6aa774ce21fe10b33672fc4401822eddfc60fc010e7371db6058fd9c38cebd00` |
| **fallback** | `…-6aa774ce-zeros.tif` (`e3b6c2ecfb65c109…`) |
| **form note** (122 chars) | `R0 h33-h33-2-b2 + RELIEF r15: 5648/37654 dots (15%) range->piedmont class, count fixed, dcat>=3px, structured; pred +0.004` |
| **predicted** | +0.004 MODEL (band −0.017 … +0.027) |

## Slot 3 (alternate, not sequential)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-relief-r15s-20261023-5f0ae851.tif` |
| **name** | `h33-h33-2-b2-relief-r15s-20261023-5f0ae851` |
| **sha256** | `5f0ae8512e44940bf02e9fecba94af91d9119450abd45d0b6074a7fc40f0a796` |
| **fallback** | `…-5f0ae851-zeros.tif` (`3b2cbfd13dd4d3fa…`) |
| **form note** (111 chars) | `R0 h33-h33-2-b2 + RELIEF r15s: 5648/37654 dots (15%) high->mid slope class, count fixed, dcat>=3px; pred +0.001` |
| **predicted** | +0.001 MODEL (band −0.007 … +0.011) |

## Before you upload (2 minutes)

```
export GEMSDOE_DATA=/path/to/verified/inputs      # parent, template, catalogue, features
python -m pytest tests -q                          # 15 tests
python tools/validate_raster.py                    # re-runs every gate on every release
python tools/check_ledger.py                       # ledger <-> disk, no duplicate triples
sha256sum releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif   # must start 366c87ca
```

Then fill `receipt_score` and `receipt_date` in `ledger/submissions.csv` from the
submission-page receipt. Until that exists the file's score is **CLAIM only** —
this repo currently holds no receipt for any file, including the parent's 0.2778.
