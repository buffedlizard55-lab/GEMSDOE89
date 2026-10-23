# SUBMIT — GEMSDOE89 (CONCENTRATION queue, 2026-10-23)

The human submits from their own registered account. Nothing here logs in,
scrapes, or uploads. Use the NaN-outside file; `-zeros.tif` is the fallback.
One file per slot; do not upload both twins.

## Slot 1 — 2 km CONCENTRATION, lowest dose

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-conc2km-b50-t33-m3765-20261023-da3a4886.tif` |
| **name** | `h33-h33-2-b2-conc2km-b50-t33-m3765-20261023-da3a4886` |
| **sha256** | `da3a488620e9f443056f9716386d63f3bacfecde6d051169a1435d6fb6b2c95d` |
| **fallback** | `releases/h33-h33-2-b2-conc2km-b50-t33-m3765-20261023-da3a4886-zeros.tif` (`a45ab1e7935e5a44…`) |
| **form note** (87 chars) | `R0 h33-h33-2-b2; CONC 2km b50->t33 move 3765 (10.0%), H19 greedy, n=37654; MODEL +0.002` |
| **predicted** | +0.0024 MODEL (−0.0127 … +0.0174 sensitivity, not a CI) |

## Slot 2 — independent SNAP placement fork

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` |
| **name** | `h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae` |
| **sha256** | `69db3aae7da2311d43a621d0c4d2ab423a3cd39acfea9cf13f666def10fd5c54` |
| **fallback** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae-zeros.tif` (`0fe545f9de5723e2…`) |
| **form note** | `R0 h33-h33-2-b2 + SNAP 2p0px-g0p00: 31,287/37654 dots moved, mean 1.86 px, targets dcat>=3px; pred +0.028` |
| **predicted** | +0.028 MODEL (−0.028 … +0.084); widest band in the queue |

## Slot 3 — conditional, choose at most one or hold

| condition | file (name = filename minus `.tif`) | predicted MODEL |
|---|---|---|
| slot 1 receipt ≥ **0.2878** | `releases/h33-h33-2-b2-conc2km-b50-t33-m5648-20261023-51ba9656.tif` | −0.0028 (−0.0254…+0.0198); dose test only because slot 1 fired |
| else slot 2 receipt ≥ **0.2878** | `releases/h33-h33-2-b2-snap1p4px-g0p00-20261023-e1474851.tif` | +0.028 (−0.028…+0.083) |
| else | `releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif` **or HOLD** | +0.003 (−0.012…+0.018) |

`CONCENTRATION m7531` (`1e857586`, central −0.0126) is held unless both lower
CONC doses gain ≥0.010. Do not spend two slots on same-question dose arms.

## Rest of the gated queue

| axis | value / sha8 | trigger |
|---|---|---|
| RELIEF | `r15` / `r15s` (`6aa774ce` / `5f0ae851`) | only after the named r10/alternate trigger |
| MASS | `m10uniq` (`beed130f`) | orthogonal probe when allocation/placement forks are null |
| MASS | `m20uniq` (`87ec6213`) | after m10uniq gains ≥0.010 |
| MASS | `m10rand` (`7a4c49b6`) | count-matched null for m10uniq |
| SPACING | `alongstrike` (`3b263c7a`) | narrow-band independent geometry probe |
| SPACING | `poisson` / `lattice` | held unless alongstrike gains ≥0.010 |
| SNAP | `1p0px-g0p00` (`1add5aa6`) | normally hold; window response saturates |

## Format receipt (all files re-read from disk)

| gate | result |
|---|---|
| grid vs template: 3730×3292, 100 m, EPSG:32611, float32, one band | **PASS ×30 files** |
| values in [0,1]; no NaN inside footprint; NaN/zeros outside by encoding | **PASS** |
| expected per-ledger dot counts; NaN/zeros twins have identical masks | **PASS** (drop-only MASS counts differ by design) |
| zero catalogue mass; every new CONC addition ≥3 px from catalogue | **PASS** |
| exact-hash and repeated `(parent, axis, value)` dedupe | **PASS**, 130 ledger rows |
| R0 recipe rebuild vs both parent SHA-256 pins | **PASS** |
| unit tests / leakage canary | **45 passed** / **PASS**, max strength 0.568803 (<0.90) |

CONC parent-diff details, proxy CIs, MODEL arithmetic, and per-file gates are in
`registry/build_report_concentration_*.json`; geological cards are in
`ledger/MECHANISM_CARDS_CONCENTRATION.md`. SGMC is **NOT RUN / UNVERIFIED**.

## Before an upload

```bash
export GEMSDOE_DATA=/path/to/verified/inputs
python tools/fetch_pinned_data.py
python tools/rebuild_r0.py                 # must report byte-identical R0
python -m pytest tests -q
python tools/validate_raster.py
python tools/check_ledger.py
sha256sum releases/h33-h33-2-b2-conc2km-b50-t33-m3765-20261023-da3a4886.tif
```

After each upload, copy the submission-page result into `receipt_score` and
`date`, set `receipt=Y`, and label it `RECEIPT`. Until then a built file is
unscored; an owner-reported number without that receipt is only a `CLAIM`.
