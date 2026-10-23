# SUBMIT — GEMSDOE89 (integrated queue, 2026-10-23)

The human submits from their own registered account. Nothing here logs in,
scrapes, or uploads. Use the NaN-outside file; `-zeros.tif` is the fallback.
One file per slot; do not upload both twins.

## Slot 1 — 5 km CONCENTRATION allocation fork

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-CONC5kmcat10-20261023-2dc19377.tif` |
| **name** | `h33-h33-2-b2-CONC5kmcat10-20261023-2dc19377` |
| **sha256** | `2dc19377e7592f408bf3d3bc67d49bb86b640deedaf2744de12db68f3cc2db52` |
| **fallback** | `releases/h33-h33-2-b2-CONC5kmcat10-20261023-2dc19377-zeros.tif` (`a42e5d1a160c2429…`) |
| **form note** | `R0 h33-h33-2-b2; CONC 5km cat-prior t10: 3765/37654 (10%) zero->top25% fault blocks, n37654; pred +0.009` |
| **predicted** | +0.009 MODEL (−0.010 … +0.038); cards: `ledger/MECHANISM_CARDS.md` Part IV |

## Slot 2 — independent SNAP placement fork

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` |
| **name** | `h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae` |
| **sha256** | `69db3aae7da2311d43a621d0c4d2ab423a3cd39acfea9cf13f666def10fd5c54` |
| **fallback** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae-zeros.tif` (`0fe545f9de5723e2…`) |
| **form note** | `R0 h33-h33-2-b2 + SNAP 2p0px-g0p00: 31,287/37654 dots moved, mean 1.86 px, targets dcat>=3px; pred +0.028` |
| **predicted** | +0.028 MODEL (−0.028 … +0.084); widest sensitivity band in the queue |

## Slot 3 — conditional priority, choose at most one or hold

| condition | file (name = filename minus `.tif`) | predicted MODEL |
|---|---|---|
| slot 1 ≥ **0.2878** | `releases/h33-h33-2-b2-CONC5kmcat20-20261023-4d229938.tif` | +0.019 (−0.010…+0.067) |
| else slot 1 ≤ **0.2678** | `releases/h33-h33-2-b2-CONC5kmcat10away-20261023-f7b8aa28.tif` | −0.009 (−0.038…+0.010); sign control |
| else slot 2 ≥ **0.2878** | `releases/h33-h33-2-b2-snap1p4px-g0p00-20261023-e1474851.tif` | +0.028 (−0.028…+0.083) |
| else | `releases/h33-h33-2-b2-MASSm10uniq-20261023-beed130f.tif` **or HOLD** | +0.002 (−0.010…+0.010) |

## Rest of the gated queue

| axis | value / sha8 | trigger |
|---|---|---|
| CONC 2 km | `m3765` (`da3a4886`), central +0.0024 | held separate H19 mechanism; **not** a clean 5 km scale control |
| CONC 2 km | `m5648` / `m7531` (`51ba9656` / `1e857586`) | held; sequential ≥+0.010 lower-dose receipts required |
| RELIEF | `r10` (`366c87ca`) | independent allocation probe if the queued forks are exhausted |
| RELIEF | `r15` / `r15s` | only after their named r10/alternate triggers |
| MASS | `m20uniq` / `m10rand` | after m10uniq ≥+0.010 / as its count-matched null |
| SPACING | `alongstrike` (`3b263c7a`) | narrow-band independent geometry probe |
| SPACING | `poisson` / `lattice` | held unless alongstrike gains ≥0.010 |
| SNAP | `1p0px-g0p00` (`1add5aa6`) | normally hold; window response saturates |

## Format receipt (all files re-read from disk)

| gate | result |
|---|---|
| grid vs template: 3730×3292, 100 m, EPSG:32611, float32, one band | **PASS ×36 files** |
| values in [0,1]; no NaN inside footprint; NaN/zeros outside by encoding | **PASS** |
| expected per-ledger dot counts; NaN/zeros twins have identical masks | **PASS** (drop-only MASS counts differ by design) |
| zero catalogue mass; new CONC additions ≥3 px from catalogue | **PASS** |
| exact-hash and repeated `(parent, axis, value)` dedupe | **PASS**, 133 ledger rows |
| R0 recipe rebuild vs both parent SHA-256 pins | **PASS** |
| unit tests / leakage canary | **56 passed** / **PASS**, max strength 0.568803 (<0.90) |

Both CONCENTRATION families have per-file build/gate receipts in `registry/`.
Part IV/V cards and `ledger/MECHANISM_CARDS_CONCENTRATION.md` explain why the
2 km files are held separately. SGMC is **NOT RUN / UNVERIFIED** for 2 km.

## Before an upload

```bash
export GEMSDOE_DATA=/path/to/verified/inputs
python tools/fetch_pinned_data.py
python tools/rebuild_r0.py                 # must report byte-identical R0
python -m pytest tests -q
python tools/build_ledger.py               # must preserve 18 GEMSDOE89 rows
python tools/validate_raster.py
python tools/check_ledger.py
sha256sum releases/h33-h33-2-b2-CONC5kmcat10-20261023-2dc19377.tif
```

After each upload, copy the submission-page result into `receipt_score` and
`date`, set `receipt=Y`, and label it `RECEIPT`. Until then a built file is
unscored; an owner-reported number without that receipt is only a `CLAIM`.
