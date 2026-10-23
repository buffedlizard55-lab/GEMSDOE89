# SUBMIT — session GEMSDOE89 (2026-10-23), axis MASS

The human submits from their own registered account. Nothing here logs in,
scrapes, or uploads. One file per slot; the **NaN-outside twin** is the one to
upload (the zeros twin is the fallback and scores identically per ledger
history). Every file below was re-read from disk after writing and every MUST
gate re-run on the re-read array.

## Slot 1 (primary)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-MASSm10uniq-20261023-beed130f.tif` |
| **name** | `h33-h33-2-b2-MASSm10uniq-20261023-beed130f` |
| **sha256** | `beed130f09a9c7e292c8a0a9171ac7dd2a8f19023cf41c8a5f855ba541122f06` |
| **fallback** | `releases/…-beed130f-zeros.tif` (`312c7ab47c3a1a02…`) |
| **form note** (82 chars) | `R0 h33-h33-2-b2; MASS m10uniq: drop 3765/37654 dots (10%), none added; pred +0.002` |
| **predicted** | +0.002 MODEL (band −0.010 … +0.010; arithmetic ceiling +0.0105) |

## Slot 2 (conditional: only if slot 1 scores ≥ +0.005)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-MASSm20uniq-20261023-87ec6213.tif` |
| **name** | `h33-h33-2-b2-MASSm20uniq-20261023-87ec6213` |
| **sha256** | `87ec62139e77771157799304fb47ec8322bce0133ba20b048070cb2973f986f8` |
| **fallback** | `releases/…-87ec6213-zeros.tif` (`e00a58e58194574b…`) |
| **form note** (82 chars) | `R0 h33-h33-2-b2; MASS m20uniq: drop 7531/37654 dots (20%), none added; pred +0.004` |
| **predicted** | +0.004 MODEL (band −0.020 … +0.021; ceiling +0.021) |

## Slot 3 (control — or hold)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-MASSm10rand-20261023-7a4c49b6.tif` |
| **name** | `h33-h33-2-b2-MASSm10rand-20261023-7a4c49b6` |
| **sha256** | `7a4c49b6999421b1b47a12ad7f7c77c1499dad983e87f5620469f36e615a90a0` |
| **fallback** | `releases/…-7a4c49b6-zeros.tif` (`4cb61fd574b78407…`) |
| **form note** (82 chars) | `R0 h33-h33-2-b2; MASS m10rand: drop 3765/37654 dots (10%), none added; pred -0.002` |
| **predicted** | −0.002 MODEL (band −0.016 … +0.010) — a decision, not a score |

## Format receipt (all three files, all gates, re-read from disk)

| gate | result |
|---|---|
| readable / re-read after write | pass |
| grid contract vs `sample_submission.tif` (shape 3730×3292, pixel scale 100 m, tiepoint, geokeys, EPSG:32611) | pass |
| dtype float32, single band | pass |
| values in [0,1] | pass (dots exactly 1.0, everything else 0 or NaN) |
| no NaN inside footprint; NaN outside (NaN twin) / zeros outside (zeros twin) | pass |
| dot count 33,889 / 33,889 / 30,123 and raster==mask identity | pass |
| zero catalogue mass | pass (0 dots on catalogue; the parent's own 2.236 px ring is inherited, min distance unchanged) |
| sha256 not already in the ledger | pass |
| twins carry an identical dot mask | pass |
| drop-only parent diff | pass (added vs parent = 0 for all three) |

## Before you upload (2 minutes)

```
export GEMSDOE_DATA=/path/to/verified/inputs     # parent, template, catalogue, 2 ancestors
python -m pytest tests -q                        # 24 tests
python tools/validate_raster.py                  # re-runs every gate on every release
python tools/check_ledger.py                     # ledger <-> disk, no duplicate triples
sha256sum releases/h33-h33-2-b2-MASSm10uniq-20261023-beed130f.tif   # must start beed130f
```

Then fill `receipt_score` and `receipt_date` in `ledger/submissions.csv` from the
submission-page receipt. Until that exists the file has no score — this repo
holds no receipt for any file, including the parent's 0.2778 (CLAIM).

Not needed for these files: `training_features.tif` (419 MB). A drop-only MASS
edit reads no band. Its absence is recorded as NOT FETCHED, not as a failure.
