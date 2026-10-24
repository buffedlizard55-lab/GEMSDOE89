# SUBMIT — GEMSDOE89 (integrated 24-pair queue, 2026-10-24)

The human submits manually from their own registered account. Nothing in this
repository logs in, scrapes, or uploads. Upload one file per slot; use the
NaN-outside `.tif` primary file (`-zeros.tif` is the byte-verified fallback).

## This session's builds (`PRUNE` axis: 300 m kernel clearance, 100 m proximal splay, 400 m smear purge)

| role | file | name | sha256 (`.tif` / `-zeros.tif`) | form note (chars <= 140) | predicted (`MODEL`) |
|---|---|---|---|---|---|
| **FULL CLEARANCE** | `releases/h33-h33-2-b2-prune-c3p0-20261024-7b101829.tif` | `h33-h33-2-b2-prune-c3p0-20261024-7b101829` | `7b101829ca5c0c92ecab3b6e80b2a3fa7a3c333a36db553648eb11fe2ea9d3c5` / `15f212a231bde25f69c5e5ce4b0253457a44f808778f566dd55d64e9a0eeebcc` | `h33-h33-2-b2; PRUNE c3p0: collar >3px, prune 2171 ring dots, refill on H19-5, n37654; pred +0.003 (-0.005..+0.012)` (113 chars) | **+0.003** (`−0.005…+0.012`) |
| **PROXIMAL SPLAY** | `releases/h33-h33-2-b2-prune-c1p0-20261024-85cf176a.tif` | `h33-h33-2-b2-prune-c1p0-20261024-85cf176a` | `85cf176a485997b5e80d4c82b998cfbc96bf71b3e9a56cba260c609fae792e3a` / `a5f846b69cf925b0fc4b0a40ca385e04ae4bfb56372fa7e5684ca788bc277c26` | `h33-h33-2-b2; PRUNE c1p0: collar >1px, swap in 2545 ring dots, drop 2545 low-gain, n37654; pred -0.004 (-0.015..+0.008)` (116 chars) | **−0.004** (`−0.015…+0.008`) |
| **SMEAR PURGE** | `releases/h33-h33-2-b2-prune-c4p0-20261024-d681292b.tif` | `h33-h33-2-b2-prune-c4p0-20261024-d681292b` | `d681292b540073e97914f6b864a7da8305ff4b10b067a99ea7b427844081ef77` / `7112c58ebe56e0cbfeb191d84bca280ec53787a7d4d7f00f576e2cbb83a31bf6` | `h33-h33-2-b2; PRUNE c4p0: collar >4px, prune 3825 ring dots, refill on H19-5, n37654; pred -0.001 (-0.018..+0.015)` (113 chars) | **−0.001** (`−0.018…+0.015`) |

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
| else | `releases/h33-h33-2-b2-prune-c3p0-20261024-7b101829.tif` (300 m kernel clearance), `…-MASSm10uniq-…-beed130f.tif`, or `…-relief-r10-…-366c87ca.tif` **or HOLD** | `+0.003` / `+0.002` / `+0.003` |

## Rest of the gated queue (`ledger/submissions.csv`, `status = BUILT`)

- **PRUNE (`c3p0` `7b101829`, `c1p0` `85cf176a`, `c4p0` `d681292b`):** 300 m kernel clearance vs 100 m proximal splay vs 400 m smear envelope.
- **CONC 12.8 km (`bcade136` / `357b4ac4` / `259ea040`):** Faulds fault-interaction & catalogue-free GPS strain family.
- **CONC 5 km (`2dc19377` / `4d229938` / `f7b8aa28`):** 5 km raw catalogue density prior & away sign control.
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
| zero catalogue mass (`0` dots on `existing_faults.tif`); all non-PRUNE additions `d_cat >= 3.00 px` | **PASS ×48 files** |
| exact-hash and repeated `(parent, axis, value)` dedupe; all `form_note <= 140` chars | **PASS (`139` ledger rows: `24` `GEMSDOE89` + `115` upstream)** |
| R0 recipe rebuild vs both parent SHA-256 pins (`c55bafc4…`, `baeae321…`) | **PASS (`tools/rebuild_r0.py`)** |
| unit tests / leakage canary | **69 passed** / **PASS** (`max <= 0.5995 < 0.90`) |

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
