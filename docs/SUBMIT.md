# SUBMIT — session GEMSDOE89, SPACING (2026-10-23)

The human submits from their own registered account. Nothing here logs in,
scrapes, or uploads. One file per slot; the NaN-outside twin is the one to
upload (the zeros twin is the fallback and scores identically per ledger
history).

## Slot 1 (primary) — along-strike re-spacing

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-spacing-strike3-20261023-59029fa7.tif` |
| **name** | `h33-h33-2-b2-spacing-strike3-20261023-59029fa7` |
| **sha256** | `59029fa7cbb9832c8ab59d1e366206f54a878420622ec62c824b40463479dd44` |
| **fallback** | `…-59029fa7-zeros.tif` (`d42e8531df011c9f…`) |
| **form note** (127 chars) | `R0 h33-h33-2-b2 + SPACING strike3: 9092/37654 dots (24.1%) re-spaced along det_elev strike, hops<=5px, count fixed; pred +0.004` |
| **predicted** | +0.004 MODEL (band −0.013 … +0.024) |

## Slot 2 (conditional) — isotropic Poisson-disk de-clustering

Submit only if slot 1 is informative (any |Δ| ≥ 0.010).

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-spacing-pd3-20261023-6b481dc1.tif` |
| **name** | `h33-h33-2-b2-spacing-pd3-20261023-6b481dc1` |
| **sha256** | `6b481dc1813b84fe22a21943cbf221f53e9367b9c0dd805cec53302eabf9f713` |
| **fallback** | `…-6b481dc1-zeros.tif` (`eaf65e714f5a51be…`) |
| **form note** (126 chars) | `R0 h33-h33-2-b2 + SPACING pd3: 9215/37654 dots (24.5%) de-clustered to NN>=3px, hops<=6px, count fixed, dcat>=3px; pred +0.003` |
| **predicted** | +0.003 MODEL (band −0.016 … +0.025) |

## Slot 3 (hold / control) — partial lattice

Submit only to bracket a positive spacing result.

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-spacing-lat3-t1p5-20261023-0dbab41e.tif` |
| **name** | `h33-h33-2-b2-spacing-lat3-t1p5-20261023-0dbab41e` |
| **sha256** | `0dbab41e2e67e92b5cad68c3dfde0d59c254c0c5b4b2eea511860f7e454d522a` |
| **fallback** | `…-0dbab41e-zeros.tif` (`245f60882240afa0…`) |
| **form note** (120 chars) | `R0 h33-h33-2-b2 + SPACING lat3-t1p5: 4642/37654 dots (12.3%) onto 3px lattice nodes, hops<=4px, count fixed; pred -0.001` |
| **predicted** | −0.001 MODEL (band −0.008 … +0.012) |

## Format receipt — every gate passes, files re-read from disk after writing

| gate | result |
|---|---|
| readable / re-read | pass |
| grid contract vs `sample_submission.tif` (shape, pixel scale, tiepoint, geokeys, EPSG:32611) | pass |
| dtype float32, single band, shape 3730×3292 | pass |
| values in [0,1] | pass (all dots exactly 1.0, all else 0 or NaN) |
| no NaN inside footprint; NaN outside (NaN twin) / zeros outside (fallback) | pass |
| dot count 37,654 and mask identity; twins carry identical masks | pass |
| zero catalogue mass | pass |
| new-pixel clearance from catalogue ≥ 3.00 px (measured min 3.00); parent's inherited 2.236 px ring kept per IRREGULARITIES item 2 | pass |
| no new pair closer than the parent's 2.828 px floor | pass |
| sha256 not already in the ledger | pass |

## Prior-session files

The three RELIEF variants (`…-relief-r10/r15/r15s…`, 2026-10-23) remain in
`releases/` and in the ledger, unscored. Do not upload a spacing file and a
relief file in the same week without checking the rolling quota.

## Before you upload (2 minutes)

```
export GEMSDOE_DATA=/path/to/verified/inputs      # parent, template, catalogue, features
python -m pytest tests -q                          # 21 tests
python tools/validate_raster.py                    # re-runs every gate on every release
python tools/check_ledger.py                       # ledger <-> disk, no duplicate triples
sha256sum releases/h33-h33-2-b2-spacing-strike3-20261023-59029fa7.tif   # must start 59029fa7
```

Then fill `receipt_score` and `receipt_date` in `ledger/submissions.csv` from
the submission-page receipt. Until that exists the file's score is **CLAIM
only** — this repo holds no receipt for any file, including the parent's 0.2778.
