# SUBMIT — GEMSDOE89 SPACING continuation

The human submits from their own registered account. Nothing here logs in,
scrapes, or uploads. Use **one file per slot**: the NaN-outside TIFF is primary;
its zeros twin is only a fallback. Predictions are **MODEL**, not scores.
Follow the conditional order in `SLOT_PLAN.md`.

## Slot 1 — primary SPACING arm

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-spacing-poisson10-20261023-986e9365.tif` |
| **name** | `h33-h33-2-b2-spacing-poisson10-20261023-986e9365` |
| **sha256** | `986e93658ed87d542b9e8552344cfc17745288da00804d07ef6b96d1d4ec3be5` |
| **fallback** | `releases/h33-h33-2-b2-spacing-poisson10-20261023-986e9365-zeros.tif` (`7e919b2c815f7582…`) |
| **form note** (95 chars) | `R0 h33-h33-2-b2 + SPACING poisson10: 3765 dots (10.0%), same 5km blocks, dcat>=3px; pred +0.002` |

## Slot 2 — conditional line-continuity arm

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-spacing-strike10-20261023-442188a4.tif` |
| **name** | `h33-h33-2-b2-spacing-strike10-20261023-442188a4` |
| **sha256** | `442188a419f49154c4e4647dfc8354458a0fbe9773852c33df8d6c9468bd6005` |
| **fallback** | `releases/h33-h33-2-b2-spacing-strike10-20261023-442188a4-zeros.tif` (`e7d19614724e566c…`) |
| **form note** (94 chars) | `R0 h33-h33-2-b2 + SPACING strike10: 3765 dots (10.0%), same 5km blocks, dcat>=3px; pred +0.003` |

## Slot 3 — conditional regular-geometry control

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-spacing-lattice10-20261023-9d7dc126.tif` |
| **name** | `h33-h33-2-b2-spacing-lattice10-20261023-9d7dc126` |
| **sha256** | `9d7dc126634c0a66cca27b16f6eac770a8c6d36459f235fdfd11c3c3bcc3c11a` |
| **fallback** | `releases/h33-h33-2-b2-spacing-lattice10-20261023-9d7dc126-zeros.tif` (`b2705fa90d5f6fff…`) |
| **form note** (95 chars) | `R0 h33-h33-2-b2 + SPACING lattice10: 3765 dots (10.0%), same 5km blocks, dcat>=3px; pred +0.001` |

## Format receipt — all three variants, both encodings

All files were re-read from disk after writing and pass every MUST gate.
Machine receipts: `registry/format_receipts.json` and
`registry/build_report_spacing_<value>.json`.

| gate | result |
|---|---|
| grid vs `sample_submission.tif`: shape 3730×3292, one band, float32, EPSG:32611, 100 m, transform/geokeys | pass |
| values in [0,1]; no NaN inside footprint; NaN outside on primary files; zeros outside on fallbacks | pass |
| 37,654 unit dots; identical masks between twins | pass |
| zero catalogue mass; **added** dots >=3.00 px from catalogue | pass |
| parent diff: exactly 3,765 removed + 3,765 added (9.9989%); minimum new-dot NN 2.828 px | pass |
| paired 5 km block counts unchanged; same removal set and anchors across arms | pass |
| sha256 unseen at build; no duplicate `(parent, SPACING, value)` | pass |

Mean displacement is 4.93 px (Poisson), 4.67 px (strike), and 4.42 px
(lattice). The inherited R0 collar exception is documented in
`IRREGULARITIES.md` item 2; these builds did not silently add a PRUNE change.

## Before upload (2 minutes)

```bash
export GEMSDOE_DATA=/path/to/verified/inputs
python -m pytest tests -q                    # 20 tests
python tools/validate_raster.py              # all 12 current release TIFFs
python tools/check_ledger.py
sha256sum releases/h33-h33-2-b2-spacing-poisson10-20261023-986e9365.tif
```

The final hash must start `986e9365`. After a submission, copy the receipt into
`ledger/submissions.csv`: fill `receipt_score`, set `receipt=Y` and
`evidence_class=RECEIPT`, and update `date` with the receipt date. Until then,
the variant is **BUILT / unscored**. R0's 0.2778 remains **CLAIM**.
