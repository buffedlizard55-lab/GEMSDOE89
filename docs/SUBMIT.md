# SUBMIT — GEMSDOE89 (submission guide and current candidate status)

## Executive status — read before downloading

**All session candidates: DO NOT SUBMIT.** Three holdout experiments (ANNULUS, PF-PEAKS, TC-UNION) plus the prior COND-EDGE lane were run against the spatially blocked segment holdout; every candidate scored far below the visible-only R0 baseline (HOLDOUT-DTI `0.161230 [0.142648, 0.180061]`). None is cleared for a competition slot. All GeoTIFFs below are format-validated research artifacts with verdict `negative` — **do not upload them to DrivenData**. No organizer submission receipt exists for any file in this repo.

| candidate | run card | holdout DTI (95% CI) vs R0 | format | download / submit status |
|---|---|---|---|---|
| `releases/h89-annulus-splay-20261024-e9b2bec1-candidate.tif` | `registry/run_card_annulus_20261024.json` | `0.001202 [0.000455, 0.002061]`; delta −0.160028 [−0.180591, −0.139843] | PASS (sha256 `e9b2bec1…`, 38,897 dots) | **DO NOT SUBMIT** — negative |
| `releases/h89-pfpeaks-20261024-18f0316a-candidate.tif` | `registry/run_card_pfpeaks_20261024.json` | `0.068825 [0.042551, 0.095776]`; delta −0.092405 [−0.136201, −0.049139] | PASS (sha256 `18f0316a…`, 38,897 dots) | **DO NOT SUBMIT** — negative |
| `h89-tcunion-20261024-…` (no TIF emitted) | `registry/run_card_tcunion_20261024.json` | `0.070181 [0.043417, 0.097668]`; delta −0.091049 [−0.135214, −0.047593] | blocked by duplicate guard (100% of dots within 3 px of PF-PEAKS raster) | **no file** — negative |
| `releases/h89-condedge-s2-4-20261024-829cc418-candidate.tif` (prior session) | `registry/run_card_condedge_20261024.json` | `0.049875 [0.036830, 0.061751]`; delta −0.111355 [−0.133218, −0.087864] | PASS (sha256 `829cc418…`) | **DO NOT SUBMIT** — negative |
| `releases/gems89-bstp40-20261024-2e7e8a8f.tif` (upstream lane) | `registry/run_card_bstp40.json` | segment-holdout candidate 0.06598 vs parent 0.09143; diff −0.02545 CI excludes 0 | PASS | **DO NOT SUBMIT** — negative |

**Incumbent (parent R0, recipe byte-verified):** `h33-h33-2-b2` — 37,654 unit-mass dots; live `0.2778 = CLAIM` with no organizer receipt in this repo. Its holdout on this data is `0.161230 [0.142648, 0.180061]`, the comparator no session candidate beat.

**Why `h33-h33-2-b2-zeros` (0.2778) leads the GEMSDOE sites:** it is the fleet's best *claim* — a potential-field ridge skeleton (TMI + gravity horizontal gradient) with sparse fixed-mass placement (37,654 unit dots) and a >2 px catalogue prune. The value itself is unverified (no receipt), and the competing public snapshots `0.4413` / `0.3195` are undated and conflict. No mechanism has been isolated, and no session candidate has beaten R0 on holdout, so no submission can honestly be presented as an improvement yet.

## How to submit a future promoted GeoTIFF

Only use a file that has a `promote` verdict in its run card and is explicitly marked **OK TO SUBMIT** by the separate selector. No file in this repository currently meets that bar. A machine-format PASS alone is insufficient.

## How to submit a future promoted GeoTIFF

Only use a file that has a `promote` verdict in its run card and is explicitly marked **OK TO SUBMIT** by the separate selector. A machine-format PASS alone is insufficient. The current file is explicitly **DO NOT SUBMIT**.

1. Open the DrivenData GEMS Prize page and confirm the rules, current deadline, entity quota, and remaining rolling-week slots: [competition page](https://www.drivendata.org/competitions/306/competition-doe-gems/).
2. On the submission form choose the promoted single-band GeoTIFF `.tif` (or a zip containing exactly one GeoTIFF). Do not submit a zeros twin and NaN twin as separate attempts.
3. Copy the promoted filename stem as the submission name, and paste its run-card note (maximum 140 characters) into the optional Note field.
4. Submit through the user's registered account. This repository never logs in or uploads automatically.
5. Save the submission-page receipt and exact score. Record it in `ledger/submissions.csv` as `ORGANIZER-CONFIRMED`; do not replace a receipt with a leaderboard screenshot or a projection.


The human submits manually from their own registered account. Nothing here logs in,
scrapes, or uploads. Upload the NaN-outside `.tif`; `-zeros.tif` is only a fallback.
**Never upload both twins in separate slots.** Submission name = the file stem.

## Previous unscored build inventory (historical; not a current slot recommendation)

The tables below were inherited from the prior SNAP session. Their predictions are `MODEL`, their entries have no stored organizer receipts, and the old queue order is not a current selector decision. Do not infer that any file is cleared to submit from its appearance below. The present candidate's explicit `DO NOT SUBMIT` status above takes precedence.

### Prior SNAP-directional builds (historical pair; no receipt stored)

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

## Format receipt (`registry/format_receipts.json` — all 56 files re-read from disk)

| gate | result |
|---|---|
| grid vs pinned `sample_submission.tif`: `3730×3292`, `100 m`, `EPSG:32611`, `float32`, `1` band | **PASS ×56 files** (`28` `.tif` + `28` `-zeros.tif`) |
| values in `[0, 1]`; unit dots `== 1.0`; `0` NaN inside footprint; `NaN` / `0.0` outside per twin | **PASS ×56 files** |
| expected per-ledger dot counts; NaN/zeros twins carry identical masks | **PASS ×28 pairs** (SNAP / CONC / RELIEF / MASS / SPACING = 37,654; TRACKB = 145) |
| zero catalogue mass (`0` dots on `existing_faults.tif`); moved/added targets `d_cat >= 3.00 px` | **PASS ×56 files** |
| exact-hash and repeated `(parent, axis, value)` dedupe; all `form_note <= 140` chars | **PASS (`143` ledger rows: `28` `GEMSDOE89` + `115` upstream)** |
| R0 recipe rebuild vs both parent SHA-256 pins (`c55bafc4…`, `baeae321…`) | **PASS (`tools/rebuild_r0.py`, 2026-10-24)** |
| unit tests / leakage canary | **PASS** / **PASS** (`max AUC 0.665 < 0.90`) |

Machine receipts: `registry/format_receipts.json`, `registry/build_report_snap_<value>.json`,
`registry/build_report_snap_directional.json`, `registry/report_only_status.json`.
PROXY/MODEL diagnostics never gate an upload.

## Pre-upload verification

```bash
export GEMSDOE_DATA=/path/to/verified/inputs
python tools/fetch_pinned_data.py
python tools/rebuild_r0.py
python -m pytest tests -q
python tools/build_ledger.py
python tools/validate_raster.py
python tools/check_ledger.py
sha256sum releases/h33-h33-2-b2-snapdirfw2p0-20261024-dc578b2f.tif  # must start dc578b2f
sha256sum releases/h33-h33-2-b2-snapdirhw2p0-20261024-5cccfc1d.tif  # must start 5cccfc1d
```

After each upload, the human records `receipt_score` and `date` in `ledger/submissions.csv` (`receipt=Y`, `status=SUBMITTED`).
