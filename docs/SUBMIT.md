# SUBMIT — session GEMSDOE89 (SPACING build, 2026-10-23)

The human submits from their own registered account. Nothing here logs in,
scrapes, or uploads. One file per slot; the NaN-outside twin is the one to
upload (the zeros twin is the fallback and scores identically per ledger
history). Parent R0 for all three: `h33-h33-2-b2`, 0.2778 = **CLAIM**.

## Slot 1 (primary)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-spacing-hd4p0-20261023-0cf9025b.tif` |
| **name** | `h33-h33-2-b2-spacing-hd4p0-20261023-0cf9025b` |
| **sha256** | `0cf9025b510c0a5ed9ed7e9c429e0e72f2a02337c01f33ea6ba980d781ceed7a` |
| **fallback** | `releases/h33-h33-2-b2-spacing-hd4p0-20261023-0cf9025b-zeros.tif` (`e82b846e…`) |
| **form note** (95 chars) | `h33-h33-2-b2; SPACING hd4p0: 13749 dots relocated (36.5%), sep 4.0 px, mean 2.8 px; pred +0.025` |
| **predicted** | +0.025 MODEL (band −0.012 … +0.061) |
| **change** | 13,749/37,654 dots (36.5 %) relocated to enforce a 4.0 px hard disk; count fixed |

## Slot 2 (dose response)

Submit only if slot 1 scores **≥ 0.2878** (parent + 0.010).

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-spacing-hd3p0-20261023-08f80fd3.tif` |
| **name** | `h33-h33-2-b2-spacing-hd3p0-20261023-08f80fd3` |
| **sha256** | `08f80fd3fa247dfd9f45a14845481363edb81b983e3452ce259cdb98ea099b4d` |
| **fallback** | `…-08f80fd3-zeros.tif` (`105a7100…`) |
| **form note** (94 chars) | `h33-h33-2-b2; SPACING hd3p0: 5413 dots relocated (14.4%), sep 3.0 px, mean 1.4 px; pred +0.006` |
| **predicted** | +0.006 MODEL (band −0.003 … +0.015) |
| **change** | 5,413/37,654 dots (14.4 %) relocated to enforce a 3.0 px hard disk |

## Slot 3 (geometry contrast, same dose as slot 2)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-spacing-hd3p0-along-20261023-f3d99d91.tif` |
| **name** | `h33-h33-2-b2-spacing-hd3p0-along-20261023-f3d99d91` |
| **sha256** | `f3d99d91af2f96282ef6d86bcfe8c28fbe3dfa7d2048e30f448f584bcd152d91` |
| **fallback** | `…-f3d99d91-zeros.tif` (`5189d2de…`) |
| **form note** (100 chars) | `h33-h33-2-b2; SPACING hd3p0-along: 5159 dots relocated (13.7%), sep 3.0 px, mean 3.3 px; pred +0.008` |
| **predicted** | +0.008 MODEL (band −0.004 … +0.021) |
| **change** | 5,159/37,654 dots (13.7 %) relocated **along local strike** instead of isotropically |

## Format receipt — identical for all three files, re-read from disk after writing

| gate | result |
|---|---|
| readable / re-read from disk | pass |
| grid contract vs `sample_submission.tif` (shape 3730×3292, pixel scale 100 m, tiepoint, geokeys, EPSG:32611) | pass |
| dtype float32, single band | pass |
| values in [0,1] | pass (dots exactly 1.0; everything else 0 or NaN) |
| no NaN inside footprint; NaN outside | pass |
| dot count exactly 37,654 and mask identity vs build | pass |
| zero catalogue mass | pass (0 dots on catalogue pixels) |
| new positions ≥ 3.00 px from the catalogue | pass (measured min 3.00 px on every arm) |
| no dot pair tighter than the parent's own 2.828 px disk | pass (min 2.828 px) |
| dots changed within 1–50 % of the parent | pass (14.4 % / 36.5 % / 13.7 %) |
| sha256 not already in the ledger | pass |
| twins carry an identical dot mask | pass |

Unchanged caveat: the parent itself carries 1,611 dots at 2.236 px from the
catalogue (its own documented rule was "none within 2 px"). Those are inherited,
not created — see `IRREGULARITIES.md` item 2.

## Before you upload (2 minutes)

```
export GEMSDOE_DATA=/path/to/verified/inputs    # parent, template, catalogue
python -m pytest tests -q                       # 22 tests
python tools/validate_raster.py                 # re-runs every gate on every release
python tools/check_ledger.py                    # ledger <-> disk, no duplicate triples
sha256sum releases/h33-h33-2-b2-spacing-hd4p0-20261023-0cf9025b.tif   # must start 0cf9025b
```

Then fill `receipt_score` and `receipt_date` in `ledger/submissions.csv` from the
submission-page receipt. Until that exists every score in this repo, including
the parent's 0.2778, is **CLAIM or MODEL only**.
