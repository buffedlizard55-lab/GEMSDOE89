# SUBMIT — GEMSDOE89 (Promoted `H89 BH-RTP-HABC` + 29-Pair Queue, 2026-10-24)

The human selector submits manually from their own registered DrivenData account. Nothing here logs in,
scrapes, or uploads. **Primary recommended upload:** `docs/downloads/gemsdoe89-bh-rtp-habc-20261024-d7e1507c-zeros.tif`
(`nodata = None`, strict `[0.0, 1.0]` `float32`, zero `NaN` anywhere, matching Lipor's official reference writer; `IR-89-18`).
**Never upload both twins in separate slots.**

## Primary Promoted Discovery Submission (`H89 = BH-RTP-HABC`, 2026-10-24)

| role | download file & submission name | sha256 (`docs/downloads/...-zeros.tif` / `releases/...-zeros.tif`) | form note (98 chars <= 140) | holdout (`HOLDOUT-DTI`, `gems57-pooled-hide-v2`, `K=11,321`) |
|---|---|---|---|---|
| **PROMOTED (Slot 1)** | `docs/downloads/gemsdoe89-bh-rtp-habc-20261024-d7e1507c-zeros.tif`<br>Name: `gemsdoe89-bh-rtp-habc-20261024-d7e1507c-zeros` | `715c8b862c50af4218cdfb201869f743e9b85585b840180486f947bbd64d8361` / `33372a75e04f486bdd7ef9dd51b39d99c385c51df53fc521de8c24f1cb1064c3` | `H89 BH-RTP-HABC dual-LOQO+CELF300m: 37654 dots, dcat>=3px; HOLDOUT-DTI 0.1603 (+0.0642 vs R0 fair)` | **`0.16027` (`[0.14498, 0.17553]`)**, `+0.06418` (`+66.8%`) vs `R0` fold-fair (`0.09609`) |

## Secondary R0-Perturbation Diagnostic Pair (`SNAP` directional corner, 2026-10-24) — optional within quota

| role | file / submission name (stem) | sha256 (`.tif` / `-zeros.tif`) | form note (110 chars) | predicted (`MODEL`) |
|---|---|---|---|---|
| **PAIR A (slot 1)** | `releases/h33-h33-2-b2-snapdirfw2p0-20261024-dc578b2f.tif` | `dc578b2f556dfd94cf29da6327ffa8b323166511a76548bf8e49308b74dbf993` / `91bed5aad415fb95bb5c9f66aff598a4bac960eac3ce35045646b37f350e9265` | `R0 h33-h33-2-b2 + SNAP dirfw2p0: 20,853/37654 footwall-only, mean 1.74px, dcat>=3px; pred -0.019..+0.056 MODEL` | **−0.019 … +0.056** |
| **PAIR B (slot 2)** | `releases/h33-h33-2-b2-snapdirhw2p0-20261024-5cccfc1d.tif` | `5cccfc1d2174677b46100e5b78db4d011b359b2a65b3d5d7b171ee6feccfaf69` / `fd75dd4be8f193f1a3bae77873388c3db33e442c65e159b8c2eea4b525f25cc3` | `R0 h33-h33-2-b2 + SNAP dirhw2p0: 21,399/37654 hangwall-only, mean 1.74px, dcat>=3px; pred -0.019..+0.057 MODEL` | **−0.019 … +0.057** |
| **DOSE (cond. slot 3)** | `releases/h33-h33-2-b2-snapdirfw1p0-20261024-373c8fd6.tif` | `373c8fd67ec464210a699f833a5b3c9f516196da25b0c136a8490f7b88e82f32` / `938aee5bc705ff5e652c0664946bfecfd24f758982c767f5d0996828bffebdb3` | `R0 h33-h33-2-b2 + SNAP dirfw1p0: 16,632/37654 footwall-only, mean 1.00px, dcat>=3px; pred -0.015..+0.044 MODEL` | **−0.015 … +0.044** |

**Read them as a difference, not as scores.** `dirfw2p0` and `dirhw2p0` are exact mirrors:
same response surface (bands 3 `tmi_hg` + 18 `iso_grav_anom_hg`), same 2.0 px window, same
gain gate 0.00, same allowed targets, same count 37,654, same offset set. The only change is
which half of the window a dot may move into (±60° about the local up-slope direction of
pinned band 12 `det_elev`; deadband 2 m/px, 36 dots). `fw − hw ≥ +0.010` ⇒ the surface trace
sits footwall-side of the HG maximum; reverse ⇒ hanging-wall side; both `≤ R0 − 0.010` ⇒ the
crest is right and position work stops. `dirfw1p0` is the 1 px dose of the footwall rule.
Cards and the pre-registered read-out: `ledger/MECHANISM_CARDS.md` Part VIII.

## Same-day alternative week — the completed SNAP gate cells (do not run both weeks)

| role | file / stem | sha256 (`.tif` / `-zeros.tif`) | form note | predicted (`MODEL`) |
|---|---|---|---|---|
| **gate head** | `releases/h33-h33-2-b2-snap1p4px-g0p01-20261024-afc60a25.tif` | `afc60a25d0ceb28295139fb0ad403132da32f07b1da845565326f3db39eb5b01` / `0695a30587b9805b76ccc31d3e54312c061cfdc40055f71351b3a56c9a02d17f` | `R0 h33-h33-2-b2 + SNAP 1p4px-g0p01: 6,767/37654 dots moved, mean 1.37 px, targets dcat>=3px; pred +0.012` | **+0.0120** (−0.0060…+0.0301) |
| **matched gateless control** | `releases/h33-h33-2-b2-snap1p4px-g0p00-20261023-e1474851.tif` | `e14748519b3fb35c7998d8d4da12014c27374cd13455e1a79730e86fd2e07ab9` | `R0 h33-h33-2-b2 + SNAP 1p4px-g0p00: 31,233/37654 dots moved, mean 1.35 px, targets dcat>=3px; pred +0.028` | **+0.0278** (−0.0278…+0.0834) |
| **held boundary** | `releases/h33-h33-2-b2-snap1p0px-g0p02-20261024-384435e6.tif` | `384435e608fdc6b4a1e8218ef7c3454d6970b4f5149cd3e945082f666761d6ae` / `8592f23b22a29f72bbab714d296b4f14c04276803063d553f2e44d0a41a5511d` | `R0 h33-h33-2-b2 + SNAP 1p0px-g0p02: 1,245/37654 dots moved, mean 1.00 px, targets dcat>=3px; pred +0.002` | **+0.0022** — minimum-dose control, not a default slot |

This pair reads **selectivity vs dose** (only the gate differs). Gated and gateless arms use
different MODEL scenario fractions (`IRREGULARITIES.md` item 15): compare the two **receipts**,
never the central MODELs. `1p0px-g0p01` (`2916ec2d`, +0.0076) is the fixed-gate window control.

## Phase-2 TRACKB product (NOT for upload as a scored slot)

| field | value |
|---|---|
| **GeoJSON** | `releases/h33-h33-2-b2-TRACKBtop12-20261024-fb156257.geojson` (12 traces, EPSG:32611) |
| **raster** | `releases/h33-h33-2-b2-TRACKBtop12-20261024-fb156257.tif` (145 member dots; sha256 `fb15625714547a192da792b26466085c5ce849854c8af35206450b5c332bc370`) |
| **evidence** | `ledger/TRACKB_TRACES.md` (one paragraph per trace); card `ledger/MECHANISM_CARDS_TRACKB.md` |
| **warning** | Phase-2 expert-review product only. Scored as-is it would fall far below R0 (145/37,654 dots). Do **not** spend a weekly slot on it. |

## Rest of the gated queue (`ledger/submissions.csv`, `status = BUILT`)

- **CONCENTRATION 12.8 km:** `int10` (`bcade136`, +0.008), `int20` (`357b4ac4`, +0.009), `geod15` (`259ea040`, +0.003).
- **CONCENTRATION 5 km:** `cat10` (`2dc19377`, +0.009), `cat20` (`4d229938`, +0.019), `cat10away` (`f7b8aa28`, −0.009 sign control).
- **CONCENTRATION 2 km:** `da3a4886` / `51ba9656` / `1e857586` — separate on-H19 mechanism (`+0.0024` / `−0.0028` / `−0.0126`).
- **RELIEF** `r10` `366c87ca`, `r15` `6aa774ce`, `r15s` `5f0ae851`; **MASS** `m10uniq` `beed130f`, `m20uniq` `87ec6213`, `m10rand` `7a4c49b6`; **SPACING** `alongstrike` `3b263c7a` (held `poisson` `ff167173`, `lattice` `454c9098`).
- **SNAP factorial** (`{window} × {gate}`, complete): `1p0px-g0p00` `1add5aa6`, `1p0px-g0p01` `2916ec2d`, `1p0px-g0p02` `384435e6`, `1p4px-g0p00` `e1474851`, `1p4px-g0p01` `afc60a25`, upstream `1p4px-g0p02` `0b6a2ab2`, `2p0px-g0p00` `69db3aae`, `2p0px-g0p01` `7bdaa58b`, `2p0px-g0p02` `b2019f55`.
- **PRUNE:** upstream already covers the brief collars at 1–4 px; not rebuilt (`IRREGULARITIES.md` item 14).

## Format receipt (`registry/format_receipts.json` — all 58 release files + primary `docs/downloads/` `.tif` re-read from disk)

| gate | result |
|---|---|
| grid vs pinned `sample_submission.tif`: `3730×3292`, `100 m`, `EPSG:32611`, `float32`, `1` band | **PASS ×58 release files** (`29` `.tif` + `29` `-zeros.tif`) + **`15/15` PASS** on `docs/downloads/gemsdoe89-bh-rtp-habc-20261024-d7e1507c-zeros.tif` |
| values in `[0, 1]`; unit dots `== 1.0`; `0` NaN inside footprint; `NaN` / `0.0` outside per twin | **PASS ×58 release files** + **`0` NaN anywhere** on primary download `.tif` |
| expected per-ledger dot counts; NaN/zeros twins carry identical masks | **PASS ×29 pairs** (`H89` / SNAP / CONC / RELIEF / MASS / SPACING = 37,654; TRACKB = 145) |
| zero catalogue mass (`0` dots on `existing_faults.tif`); moved/added targets `d_cat >= 3.00 px` | **PASS ×58 release files** (`H89` `min d_cat = 3.000 px`) |
| exact-hash and repeated `(parent, axis, value)` dedupe; all `form_note <= 140` chars | **PASS (`144` ledger rows: `29` `GEMSDOE89` + `115` upstream)** |
| R0 recipe rebuild vs both parent SHA-256 pins (`c55bafc4…`, `baeae321…`) | **PASS (`tools/rebuild_r0.py`, 2026-10-24)** |
| unit tests / leakage canary / 84-raster uniqueness | **PASS (`85+` tests)** / **PASS** (`H89` `max AUC 0.7829 <= 0.90`; `max |ρ| 0.1118 <= 0.90`; `max 3-px overlap 0.5866 <= 0.70`) |

Machine receipts: `registry/h89_run_card.json`, `registry/h89_discovery_report.json`, `registry/leakage_canary_h89.json`, `registry/format_receipts.json`.
`HOLDOUT-DTI`/`PROXY`/`MODEL` diagnostics never substitute for a live DrivenData receipt.

## Pre-upload verification

```bash
export GEMSDOE_DATA=/path/to/verified/inputs
python tools/fetch_pinned_data.py
python tools/rebuild_r0.py
python -m pytest tests -q
python tools/build_ledger.py
python tools/validate_raster.py
python tools/check_ledger.py
sha256sum docs/downloads/gemsdoe89-bh-rtp-habc-20261024-d7e1507c-zeros.tif  # must start 715c8b86
```

After each upload, the human records `receipt_score` and `date` in `ledger/submissions.csv` (`receipt=Y`, `status=SUBMITTED`).
