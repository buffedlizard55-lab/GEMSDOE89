# SUBMIT — GEMSDOE89 (integrated 21-pair queue, 2026-10-23)

The human submits manually from their own registered account. Nothing in this
repository logs in, scrapes, or uploads. Upload one file per slot; use the
NaN-outside `.tif` primary file (`-zeros.tif` is the byte-verified fallback).

## TRACKB (2026-10-24) — Phase-2 evidence play, HELD OUT of the weekly slot queue

`TRACKB` is **not a weekly-slot candidate unless the human decides**. Its primary product is
a geologist-reviewable trace inventory for Phase 2 ($250k expert label expansion); the three
rasters are a nested, count-preserving Phase-1 probe of the same prior, offered so the human
*can* test it. Phase-1 jitter MODEL is a coverage-cost floor (central −0.002 / −0.012 / −0.021);
`|Δ| < 0.01` = no evidence. Do **not** spend a weekly Phase-1 slot on these by default — see
`SLOT_PLAN.md`.

**Phase-2 inventory (not an upload):** `releases/h33-h33-2-b2-TRACKB-traces-20261024.geojson`
(1,520 strike-consistent ≥1 km traces, WGS84, one evidence paragraph each) and
`evidence/TRACKB_trace_atlas_20261024.md` (top-48 readable atlas).

| role | file (NaN primary) | name = stem | fallback `-zeros.tif` | sha256 (`.tif`) | form note (≤140) | predicted (MODEL) |
|---|---|---|---|---|---|---|
| lowest-cost probe | `releases/h33-h33-2-b2-TRACKB-TR10-20261024-32211f1f.tif` | `h33-h33-2-b2-TRACKB-TR10-20261024-32211f1f` | `…-32211f1f-zeros.tif` | `32211f1fa90b…` | `h33-h33-2-b2; TRACKB tr10: 3765 (10%) off-trace -> +-300m of >=1km traces; n=37654; dcat>=3; Phase-2 GeoJSON; pred -0.002` | −0.002 (−0.043…+0.001) |
| dose | `releases/h33-h33-2-b2-TRACKB-TR20-20261024-5da46626.tif` | `h33-h33-2-b2-TRACKB-TR20-20261024-5da46626` | `…-5da46626-zeros.tif` | `5da466262dc7…` | `…tr20: 7531 (20%)… pred -0.012` | −0.012 (−0.091…−0.005) |
| high dose / held | `releases/h33-h33-2-b2-TRACKB-TR30-20261024-c8a264b5.tif` | `h33-h33-2-b2-TRACKB-TR30-20261024-c8a264b5` | `…-c8a264b5-zeros.tif` | `c8a264b5a616…` | `…tr30: 11296 (30%)… pred -0.021` | −0.021 (−0.137…−0.013) |

**Format receipt (this session, `registry/format_receipts.json` + per-arm `registry/build_report_trackb_*.json`):**
all 3 `.tif` + 3 `-zeros.tif` re-read from disk after writing → grid `3730×3292`, 100 m,
EPSG:32611, float32, 1 band; values in [0,1]; unit dots `== 1.0`; NaN / 0 outside footprint
per twin; **zero catalogue mass**; count preserved `37,654`; added dots `d_cat ≥ 3 px`,
`r_sep ≥ 2.83 px`; inherited 1,611-collar dots frozen; exact-hash + `(parent,axis,value)`
dedupe PASS; leakage canary PASS (footprint-masked composite 0.543 < 0.90).

## This session's builds (`12.8 km` fault-interaction + catalogue-free GPS strain `CONCENTRATION`)

| role | file | name | sha256 (`.tif` / `-zeros.tif`) | form note (123 chars each) | predicted (`MODEL`) |
|---|---|---|---|---|---|
| **PRIMARY (Slot 1)** | `releases/h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136.tif` | `h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136` | `bcade136bc98295f142eed015f88b2b913ab94dbcafcc5d8400eb1508b143167` / `b1cde6898bf225de6ea77c77a2d169b125489f131458b410276624253586cc92` | `R0 h33-h33-2-b2; CONC 12p8km-int10: move 3765/37654 (10%) low->high interaction 12.8km blocks, CV 0.553->0.553; pred +0.008` | **+0.008** (`−0.006…+0.018`) |
| **DOSE (cond. Slot 3)** | `releases/h33-h33-2-b2-conc-12p8km-int20-20261023-357b4ac4.tif` | `h33-h33-2-b2-conc-12p8km-int20-20261023-357b4ac4` | `357b4ac4f3384e3b567c6abd1d9013713f8d037f8dbd62d1af615f4449c0e44f` / `050572eb870694aa5648fc4c3fc51b01d224addaa4b3c397b421369ce3cf3e6e` | `R0 h33-h33-2-b2; CONC 12p8km-int20: move 7531/37654 (20%) low->high interaction 12.8km blocks, CV 0.553->0.656; pred +0.009` | **+0.009** (`−0.014…+0.024`) |
| **DISCRIMINATOR** | `releases/h33-h33-2-b2-conc-12p8km-geod15-20261023-259ea040.tif` | `h33-h33-2-b2-conc-12p8km-geod15-20261023-259ea040` | `259ea040c818a26add94d1a356b0c75b180292bc8c67bcf2cec5776e047f5e45` / `d914868666c45707ccfe570eda343ae3b3774845058c7e02c46cf35f0f3820c3` | `R0 h33-h33-2-b2; CONC 12p8km-geod15: move 5648/37654 (15%) low->high GPS-strain 12.8km blocks, CV 0.553->0.635; pred +0.003` | **+0.003** (`−0.015…+0.021`) |

## Integrated Next-3 Slot Queue

### Slot 1 — CONCENTRATION allocation fork (choose ONE 10% arm; never both in Week 1)

| option | file | name | sha256 | form note | predicted (`MODEL`) |
|---|---|---|---|---|---|
| **1A (12.8 km Faulds interaction, tighter band)** | `releases/h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136.tif` | `h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136` | `bcade136bc98295f142eed015f88b2b913ab94dbcafcc5d8400eb1508b143167` | `R0 h33-h33-2-b2; CONC 12p8km-int10: move 3765/37654 (10%) low->high interaction 12.8km blocks, CV 0.553->0.553; pred +0.008` | `+0.008` (`−0.006…+0.018`, Part VI) |
| **1B (5 km raw catalogue prior)** | `releases/h33-h33-2-b2-CONC5kmcat10-20261023-2dc19377.tif` | `h33-h33-2-b2-CONC5kmcat10-20261023-2dc19377` | `2dc19377e7592f408bf3d3bc67d49bb86b640deedaf2744de12db68f3cc2db52` | `R0 h33-h33-2-b2; CONC 5km cat-prior t10: 3765/37654 (10%) zero->top25% fault blocks, n37654; pred +0.009` | `+0.009` (`−0.010…+0.038`, Part IV) |

### Slot 2 — Orthogonal SNAP local-placement fork

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` |
| **fallback** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae-zeros.tif` (`0fe545f9de5723e2…`) |
| **name** | `h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae` |
| **sha256** | `69db3aae7da2311d43a621d0c4d2ab423a3cd39acfea9cf13f666def10fd5c54` |
| **form note** | `R0 h33-h33-2-b2 + SNAP 2p0px-g0p00: 31,287/37654 dots moved, mean 1.86 px, targets dcat>=3px; pred +0.028` |
| **predicted** | `+0.028 MODEL` (`−0.028 … +0.084`; Part III) |

### Slot 3 — Conditional priority (choose at most one after Week 1 receipts, or HOLD)

| condition vs R0 `0.2778` (`CLAIM`) | file (`name` = stem) | predicted (`MODEL`) |
|---|---|---|
| Slot 1 `≥ 0.2878` (`+0.010`) | matched 20% dose: `releases/h33-h33-2-b2-conc-12p8km-int20-20261023-357b4ac4.tif` (if 1A) or `…-CONC5kmcat20-20261023-4d229938.tif` (if 1B) | `+0.009` (`−0.014…+0.024`) / `+0.019` (`−0.010…+0.067`) |
| else Slot 1 `≤ 0.2678` (`−0.010`) | catalogue-free active strain `releases/h33-h33-2-b2-conc-12p8km-geod15-20261023-259ea040.tif` or sign control `…-CONC5kmcat10away-20261023-f7b8aa28.tif` | `+0.003` (`−0.015…+0.021`) / `−0.009` (`−0.038…+0.010`) |
| else Slot 2 `≥ 0.2878` (`+0.010`) | `releases/h33-h33-2-b2-snap1p4px-g0p00-20261023-e1474851.tif` | `+0.028` (`−0.028…+0.083`) |
| else | `releases/h33-h33-2-b2-MASSm10uniq-20261023-beed130f.tif` or `…-relief-r10-20261023-366c87ca.tif` **or HOLD** | `+0.002` / `+0.003` |

## Rest of the gated queue (`ledger/submissions.csv`, `status = BUILT`)

- **CONC 2 km (`da3a4886` / `51ba9656` / `1e857586`):** held separate on-H19 mechanism (`+0.0024` / `−0.0028` / `−0.0126`).
- **RELIEF (`r10` `366c87ca`, `r15` `6aa774ce`, `r15s` `5f0ae851`):** geomorphic elevation/slope tercile probes.
- **MASS (`m10uniq` `beed130f`, `m20uniq` `87ec6213`, `m10rand` `7a4c49b6`):** drop-only denominator probes + random null.
- **SPACING (`alongstrike` `3b263c7a`, held `poisson` `ff167173` / `lattice` `454c9098`):** strand stationing & lateral corridor probes.
- **SNAP (`1p0px-g0p00` `1add5aa6`):** saturated window point; hold unless two gate-0 receipts both fire.

## Format receipt (`registry/format_receipts.json` — all 48 files re-read from disk)

| gate | result |
|---|---|
| grid vs `sample_submission.tif`: `3730×3292`, `100 m`, `EPSG:32611`, `float32`, `1` band | **PASS ×48 files** (`24` `.tif` + `24` `-zeros.tif`) |
| values in `[0, 1]`; unit dots `== 1.0`; `0` NaN inside footprint; `NaN` / `0.0` outside per twin | **PASS ×48 files** |
| expected per-ledger dot counts; NaN/zeros twins carry identical masks | **PASS ×24 pairs** |
| zero catalogue mass (`0` dots on `existing_faults.tif`); all new CONC/TRACKB additions `d_cat >= 3.00 px` | **PASS ×48 files** |
| exact-hash and repeated `(parent, axis, value)` dedupe; all `form_note <= 140` chars | **PASS (`139` ledger rows: `24` `GEMSDOE89` + `115` upstream)** |
| R0 recipe rebuild vs both parent SHA-256 pins (`c55bafc4…`, `baeae321…`) | **PASS (`tools/rebuild_r0.py`)** |
| unit tests / leakage canary | **71 passed** / **PASS** (`max <= 0.5688 < 0.90`; footprint-masked composite 0.543) |

## Pre-upload verification

```bash
export GEMSDOE_DATA=/path/to/verified/inputs
python tools/fetch_pinned_data.py
python tools/rebuild_r0.py
python -m pytest tests -q
python tools/build_ledger.py
python tools/validate_raster.py
python tools/check_ledger.py
sha256sum releases/h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136.tif   # must start bcade136
```

After each upload, record `receipt_score` and `date` in `ledger/submissions.csv` (`receipt=Y`, `status=SUBMITTED`).
