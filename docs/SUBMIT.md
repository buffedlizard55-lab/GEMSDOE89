# SUBMIT — session GEMSDOE89 (integrated queue, 2026-10-23)

The human submits manually from their own registered account. Nothing in this
repository logs in, scrapes, or uploads. Upload one file per slot; use the
NaN-outside `.tif` primary file (its `-zeros.tif` twin is the byte-verified
fallback with identical interior dot mask).

## This session's builds (`AXIS = CONCENTRATION`, 12.8 km structural blocks)

| role | file | name | sha256 (`.tif` / `-zeros.tif`) | form note (chars) | predicted (`MODEL`) |
|---|---|---|---|---|---|
| **PRIMARY (Slot 1)** | `releases/h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136.tif` | `h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136` | `bcade136bc98295f142eed015f88b2b913ab94dbcafcc5d8400eb1508b143167` / `b1cde6898bf225de6ea77c77a2d169b125489f131458b410276624253586cc92` | `R0 h33-h33-2-b2; CONC 12p8km-int10: move 3765/37654 (10%) low->high interaction 12.8km blocks, CV 0.553->0.553; pred +0.008` (123) | **+0.008** (`−0.006 … +0.018`) |
| **DOSE (cond. Slot 3)** | `releases/h33-h33-2-b2-conc-12p8km-int20-20261023-357b4ac4.tif` | `h33-h33-2-b2-conc-12p8km-int20-20261023-357b4ac4` | `357b4ac4f3384e3b567c6abd1d9013713f8d037f8dbd62d1af615f4449c0e44f` / `050572eb870694aa5648fc4c3fc51b01d224addaa4b3c397b421369ce3cf3e6e` | `R0 h33-h33-2-b2; CONC 12p8km-int20: move 7531/37654 (20%) low->high interaction 12.8km blocks, CV 0.553->0.656; pred +0.009` (123) | **+0.009** (`−0.014 … +0.024`) |
| **DISCRIMINATOR** | `releases/h33-h33-2-b2-conc-12p8km-geod15-20261023-259ea040.tif` | `h33-h33-2-b2-conc-12p8km-geod15-20261023-259ea040` | `259ea040c818a26add94d1a356b0c75b180292bc8c67bcf2cec5776e047f5e45` / `d914868666c45707ccfe570eda343ae3b3774845058c7e02c46cf35f0f3820c3` | `R0 h33-h33-2-b2; CONC 12p8km-geod15: move 5648/37654 (15%) low->high GPS-strain 12.8km blocks, CV 0.553->0.635; pred +0.003` (123) | **+0.003** (`−0.015 … +0.021`) |

## Integrated Next-3 Slot Queue

### Slot 1 (12.8 km structural-concentration fork)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136.tif` |
| **fallback** | `releases/h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136-zeros.tif` |
| **name** | `h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136` |
| **sha256** | `bcade136bc98295f142eed015f88b2b913ab94dbcafcc5d8400eb1508b143167` |
| **form note** (123 chars) | `R0 h33-h33-2-b2; CONC 12p8km-int10: move 3765/37654 (10%) low->high interaction 12.8km blocks, CV 0.553->0.553; pred +0.008` |
| **predicted** | `+0.008 MODEL` (`−0.006 … +0.018`; cards in `ledger/MECHANISM_CARDS.md` Part IV) |

### Slot 2 (orthogonal local-placement fork)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` |
| **fallback** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae-zeros.tif` |
| **name** | `h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae` |
| **sha256** | `69db3aae7da2311d43a621d0c4d2ab423a3cd39acfea9cf13f666def10fd5c54` |
| **form note** (105 chars) | `R0 h33-h33-2-b2 + SNAP 2p0px-g0p00: 31,287/37654 dots moved, mean 1.86 px, targets dcat>=3px; pred +0.028` |
| **predicted** | `+0.028 MODEL` (`−0.028 … +0.084` — widest band; low-variance Slot 2 alternative: `releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif`, `+0.003 MODEL`) |

### Slot 3 (conditional on Week 1 receipts — pick at most one, or hold)

| condition vs R0 `0.2778` (`CLAIM`) | file (`name` = stem) | form note (`<= 140` chars) | predicted (`MODEL`) |
|---|---|---|---|
| Slot 1 `≥ 0.2878` (`+0.010`) | `releases/h33-h33-2-b2-conc-12p8km-int20-20261023-357b4ac4.tif` | `R0 h33-h33-2-b2; CONC 12p8km-int20: move 7531/37654 (20%) low->high interaction 12.8km blocks, CV 0.553->0.656; pred +0.009` | `+0.009` (`−0.014…+0.024`) |
| else Slot 1 `≤ 0.2678` (`−0.010`) | `releases/h33-h33-2-b2-conc-12p8km-geod15-20261023-259ea040.tif` | `R0 h33-h33-2-b2; CONC 12p8km-geod15: move 5648/37654 (15%) low->high GPS-strain 12.8km blocks, CV 0.553->0.635; pred +0.003` | `+0.003` (`−0.015…+0.021`) |
| else Slot 2 `≥ 0.2878` (`+0.010`) | `releases/h33-h33-2-b2-snap1p4px-g0p00-20261023-e1474851.tif` | `R0 h33-h33-2-b2 + SNAP 1p4px-g0p00: 31,233/37654 dots moved, mean 1.35 px, targets dcat>=3px; pred +0.028` | `+0.028` (`−0.028…+0.083`) |
| else | `releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif` or `…-MASSm10uniq-…-beed130f.tif` or **HOLD** | see `ledger/submissions.csv` `form_note` column | `+0.003` / `+0.002` |

## Format receipt (`registry/format_receipts.json` — re-read from disk after writing)

| gate | result |
|---|---|
| grid contract vs `sample_submission.tif` (`3730×3292`, `100 m` px, `EPSG:32611`, `float32`, `1` band) | **PASS ×30 files** (`15` `.tif` + `15` `-zeros.tif`) |
| values in `[0, 1]`; unit dots `== 1.0`; `0` NaN inside `5,167,373`-px footprint; `NaN` / `0.0` outside per twin | **PASS ×30 files** |
| dot count (`37,654` on `CONCENTRATION` / `SNAP` / `RELIEF` / `SPACING`; `33,889` / `30,123` on `MASS`); identical twin masks | **PASS ×15 pairs** |
| zero catalogue mass (`0` dots on `existing_faults.tif`); added-dot clearance `d_cat >= 3.00 px` (`1,611` parent `<3 px` collar dots frozen on `CONCENTRATION`) | **PASS ×30 files** |
| `sha256` unique across ledger; zero duplicate `(parent, axis, value)` triples; all `form_note <= 140` chars | **PASS (`130` ledger rows)** |
| R0 parent rebuild byte-exact vs both `parent_r0_zeros` (`c55bafc4…`) and `parent_r0_nan` (`baeae321…`) | **PASS (`tools/rebuild_r0.py`)** |

## Pre-upload verification (2 minutes)

```bash
export GEMSDOE_DATA=/path/to/verified/inputs
python tools/fetch_pinned_data.py
python -m pytest tests -q
python tools/validate_raster.py
python tools/check_ledger.py
python tools/rebuild_r0.py
sha256sum releases/h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136.tif   # must start bcade136
```

After uploading, record the live receipt in `ledger/submissions.csv` (`receipt=Y`,
`receipt_score`, `date`, `status=SUBMITTED`). Until an organizer receipt is
recorded, every number — including R0's `0.2778` — remains `CLAIM`, `PROXY`, or `MODEL`.
