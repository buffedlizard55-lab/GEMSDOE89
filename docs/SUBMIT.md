# SUBMIT — session GEMSDOE89

The human submits from their own registered account. Nothing here logs in,
scrapes, or uploads. Upload **one** file per slot: the NaN-outside raster is the
spec-exact primary file; the `-zeros.tif` twin is the byte-verified fallback
(identical live scores per ledger history).

---

## Slot 1 (primary — SPACING `strike`)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-spacing-strike-20261023-37910355.tif` |
| **name** | `h33-h33-2-b2-spacing-strike-20261023-37910355` |
| **sha256** | `37910355789dc5a0489aaadf739260d0e0fe057170084ef978d34236ae3c768f` |
| **fallback** | `releases/h33-h33-2-b2-spacing-strike-20261023-37910355-zeros.tif` (`943199db7410b6c8…`) |
| **form note** (115 chars) | `h33-h33-2-b2; SPACING strike (5444/37654=14.46% along-strike on H19 crest, dcat>=3px); pred +0.006 (-0.004..+0.011)` |
| **predicted** | +0.006 MODEL (band −0.004 … +0.011) |

Format receipt — all MUST gates pass after re-reading from disk:

| gate | result |
|---|---|
| readable / re-read from disk | pass |
| grid contract vs `sample_submission.tif` (shape 3730×3292, 100 m scale, tiepoint, EPSG:32611) | pass |
| dtype float32, single band | pass |
| values in [0, 1] | pass (37,654 unit-mass dots == 1.0; all else 0.0 or NaN) |
| no NaN inside footprint; NaN outside (`-zeros` has 0.0 outside) | pass |
| exact dot count (37,654) & twin mask equivalence | pass |
| 100 % of dots on `scored_h19_5` ridge support | pass (37,654 / 37,654) |
| zero catalogue mass (`existing_faults > 0`) | pass (0 dots) |
| newly placed dots clearance ≥ 3.00 px from catalogue | pass (min 3.00 px) |
| `% changed` in [1 %, 50 %] | pass (5,444 moved = 14.46 %; sym diff 28.92 %) |
| sha256 not already in ledger | pass |

---

## Slot 2A (conditional on Slot 1 ≥ +0.010 — SPACING `poisson`)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-spacing-poisson-20261023-95c51e18.tif` |
| **name** | `h33-h33-2-b2-spacing-poisson-20261023-95c51e18` |
| **sha256** | `95c51e182563dba79eec1e8b306fa9b673955c6615a687cdc0f8f35af4cd3b15` |
| **fallback** | `releases/h33-h33-2-b2-spacing-poisson-20261023-95c51e18-zeros.tif` (`dc82177c1fa9c962…`) |
| **form note** (113 chars) | `h33-h33-2-b2; SPACING poisson (4800/37654=12.75% Voronoi/Poisson on H19, dcat>=3px); pred +0.001 (-0.002..+0.004)` |
| **predicted** | +0.001 MODEL (band −0.002 … +0.004) |
| **format receipt** | all MUST gates pass (37,654 dots; 4,800 moved = 12.75 %, sym diff 25.50 %; 0 catalogue mass; min added clearance 3.00 px) |

---

## Crystallographic control (HOLD — SPACING `lattice`)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-spacing-lattice-20261023-dd652665.tif` |
| **name** | `h33-h33-2-b2-spacing-lattice-20261023-dd652665` |
| **sha256** | `dd65266597fc85480445a2bcbea3dd1a3cc6ba00c7d14b3333b0501657eacb93` |
| **fallback** | `releases/h33-h33-2-b2-spacing-lattice-20261023-dd652665-zeros.tif` (`5fe27a0e479d4c92…`) |
| **form note** (116 chars) | `h33-h33-2-b2; SPACING lattice (5195/37654=13.80% hex-lattice a=3.2px on H19, dcat>=3px); pred 0.000 (-0.003..+0.003)` |
| **predicted** | 0.000 MODEL (band −0.003 … +0.003) |
| **format receipt** | all MUST gates pass (37,654 dots; 5,195 moved = 13.80 %, sym diff 27.59 %; 0 catalogue mass; min added clearance 3.00 px) |

---

## Slot 2B / Slot 3 alternates (prior RELIEF arms on disk)

- **Slot 2B (if Slot 1 is inside ±0.010):** `releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif`
  (sha256 `366c87ca62040215…`; fallback `-zeros.tif` `e776fc20873321f7…`; note 122 chars:
  `R0 h33-h33-2-b2 + RELIEF r10: 3765/37654 dots (10%) range->piedmont class, count fixed, dcat>=3px, structured; pred +0.003`; all MUST gates pass).
- **Slot 3 (only if `relief-r10` scores ≥ 0.2878):** `releases/h33-h33-2-b2-relief-r15-20261023-6aa774ce.tif`
  (sha256 `6aa774ce21fe10b3…`; note 122 chars:
  `R0 h33-h33-2-b2 + RELIEF r15: 5648/37654 dots (15%) range->piedmont class, count fixed, dcat>=3px, structured; pred +0.004`; all MUST gates pass).
- **Slope alternate (`relief-r15s`):** `releases/h33-h33-2-b2-relief-r15s-20261023-5f0ae851.tif`
  (sha256 `5f0ae8512e44940b…`; note 111 chars:
  `R0 h33-h33-2-b2 + RELIEF r15s: 5648/37654 dots (15%) high->mid slope class, count fixed, dcat>=3px; pred +0.001`; all MUST gates pass).

---

## Before you upload (2 minutes)

```bash
export GEMSDOE_DATA=/path/to/verified/inputs      # or run: python tools/fetch_pinned_inputs.py
python tools/rebuild_r0.py                        # verifies manifest + byte-exact R0 rebuild
python -m pytest tests -q                         # 18 unit tests
python tools/validate_raster.py                   # re-runs every MUST gate on all 12 release files
python tools/check_ledger.py                      # ledger <-> disk, unique triples, note <= 140 chars
sha256sum releases/h33-h33-2-b2-spacing-strike-20261023-37910355.tif   # starts 37910355
```

After scoring, record `receipt_score` and `receipt_date` in `ledger/submissions.csv`
and flip `receipt` to `Y`.
