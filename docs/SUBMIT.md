# SUBMIT — session GEMSDOE89

The human submits from their own registered account. Nothing in this repository
logs in, scrapes, or uploads. Upload **one** file per slot: the NaN-outside `.tif`
is the primary spec file; the `-zeros.tif` twin is the byte-verified fallback
(identical dot mask; scores identically per ledger history).

---

## `SPACING` candidates built this session (parent `h33-h33-2-b2`, 37,654 dots)

### 1. `SPACING = alongstrike` (Slot 1 — primary `SPACING` probe)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-spacing-alongstrike-20261023-3b263c7a.tif` |
| **name** | `h33-h33-2-b2-spacing-alongstrike-20261023-3b263c7a` |
| **sha256** | `3b263c7aa90ee0928d8ad8b2a81e42bc99decc7c881f46204af36b877d8bdbaa` |
| **fallback** | `releases/h33-h33-2-b2-spacing-alongstrike-20261023-3b263c7a-zeros.tif` (`d18297a5192f0590…`) |
| **form note** (127 chars) | `h33-h33-2-b2; SPACING alongstrike: 5222/37654 (13.9%) geodesic 1-swap on >=6-dot strands, n=37654; pred +0.002 (-0.003..+0.006)` |
| **predicted** | **+0.002 MODEL** (band −0.003 … +0.006; no-evidence `<0.01` outcome expected) |

### 2. `SPACING = poisson` (Slot 3 conditional — GeoDAWN `±150 m` uncertainty-corridor test)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-spacing-poisson-20261023-ff167173.tif` |
| **name** | `h33-h33-2-b2-spacing-poisson-20261023-ff167173` |
| **sha256** | `ff167173aa2b8e45187d123db0193ad8da7e16a6e65c0f466630be9db7cfea34` |
| **fallback** | `releases/h33-h33-2-b2-spacing-poisson-20261023-ff167173-zeros.tif` (`f04da689f1da475c…`) |
| **form note** (126 chars) | `h33-h33-2-b2; SPACING poisson: 7639/37654 (20.3%) 2D blue-noise disk in +-150m corridor, n=37654; pred -0.010 (-0.032..+0.004)` |
| **predicted** | **−0.010 MODEL** (band −0.032 … +0.004; negative unless test truth sits `>=250 m` off `h19_5`) |

### 3. `SPACING = lattice` (Hold / periodic hexagonal-covering control — do not submit in same week as `poisson`)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-spacing-lattice-20261023-454c9098.tif` |
| **name** | `h33-h33-2-b2-spacing-lattice-20261023-454c9098` |
| **sha256** | `454c909877ddd82b91cfb6b6b2f71710524b1d76d37a0f72d0d33107b0f0431d` |
| **fallback** | `releases/h33-h33-2-b2-spacing-lattice-20261023-454c9098-zeros.tif` (`56c77db28955ebaa…`) |
| **form note** (125 chars) | `h33-h33-2-b2; SPACING lattice: 7305/37654 (19.4%) 3.5px hex lattice in +-200m corridor, n=37654; pred -0.007 (-0.025..+0.003)` |
| **predicted** | **−0.007 MODEL** (band −0.025 … +0.003) |

---

## Prior `RELIEF` candidates in `releases/` (Slot 2 orthogonal probe + dose follow-ups)

| role | file | sha256 | form note (chars) | predicted (MODEL) |
|---|---|---|---|---|
| **Slot 2 (`r10`)** | `releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif` | `366c87ca620402158cfbbf4911ed8abc8ba2da34f198694c9df7c5ea640ab335` | `R0 h33-h33-2-b2 + RELIEF r10: 3765/37654 dots (10%) range->piedmont class, count fixed, dcat>=3px, structured; pred +0.003` (122) | +0.003 (−0.012…+0.018) |
| **Cond. (`r15`)** | `releases/h33-h33-2-b2-relief-r15-20261023-6aa774ce.tif` | `6aa774ce21fe10b33672fc4401822eddfc60fc010e7371db6058fd9c38cebd00` | `R0 h33-h33-2-b2 + RELIEF r15: 5648/37654 dots (15%) range->piedmont class, count fixed, dcat>=3px, structured; pred +0.004` (122) | +0.004 (−0.017…+0.027) |
| **Alt. (`r15s`)** | `releases/h33-h33-2-b2-relief-r15s-20261023-5f0ae851.tif` | `5f0ae8512e44940bf02e9fecba94af91d9119450abd45d0b6074a7fc40f0a796` | `R0 h33-h33-2-b2 + RELIEF r15s: 5648/37654 dots (15%) high->mid slope class, count fixed, dcat>=3px; pred +0.001` (111) | +0.001 (−0.007…+0.011) |

---

## Format receipt (verified on all 12 files in `releases/`, re-read from disk)

| MUST gate | `alongstrike` | `poisson` | `lattice` | `r10 / r15 / r15s` |
|---|---|---|---|---|
| Re-read from disk after writing | PASS | PASS | PASS | PASS |
| Grid contract vs `sample_submission.tif` (`EPSG:32611`, `3730×3292`, 100 m, tiepoint) | PASS | PASS | PASS | PASS |
| Single band, `float32`, values in `[0, 1]` (unit dots `1.0`) | PASS | PASS | PASS | PASS |
| No NaN inside footprint (`5,167,373` px); NaN outside (`.tif`) / `0` outside (`-zeros.tif`) | PASS | PASS | PASS | PASS |
| Exact dot count `37,654` and twin mask identity | PASS | PASS | PASS | PASS |
| Zero catalogue mass (`0` dots on `existing_faults.tif`) | PASS | PASS | PASS | PASS |
| Relocated/added dot clearance `d_cat >= 3.00 px` | PASS (`3.00 px`) | PASS (`3.00 px`) | PASS (`3.00 px`) | PASS (`3.00 px`) |
| `% changed` inside `1–50 %` (relocated / symmetric diff) | `13.87 % / 27.74 %` | `20.29 % / 40.57 %` | `19.40 % / 38.80 %` | `10.00–15.00 %` |
| `sha256` unique against ledger prior to registration | PASS | PASS | PASS | PASS |

## Pre-upload verification commands

```bash
python -m pytest tests -q                 # 21 unit tests (DTI algebra, R0 recipe, SPACING, gates)
python tools/validate_raster.py           # re-reads all 12 release GeoTIFFs and runs MUST gates
python tools/check_ledger.py              # verifies ledger <-> disk sha256s, unique triples, <=140-char notes
sha256sum releases/h33-h33-2-b2-spacing-alongstrike-20261023-3b263c7a.tif
```

After scoring on DrivenData, enter `receipt_score` and `date` in `ledger/submissions.csv`
and set `receipt=Y` and `evidence_class=RECEIPT`.
