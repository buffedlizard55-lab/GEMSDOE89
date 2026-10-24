# SUBMIT — GEMSDOE89 (32-pair queue, 2026-10-24)

## ⚠ Encoding rule (fixes “Predicted values must be in range [0, 1]”)

Always upload the **`-zeros.tif`** twin (0 NaN pixels anywhere; finite
min 0.0 / max 1.0). The NaN-outside twin is the archive copy; NaN fails
range checks that do not special-case it. Fleet history scores the two
encodings identically. **Never upload both twins.** Steps + copy-paste
name/note blocks: `docs/index.html` (executive summary at the top).

## BSTP session build (2026-10-24) — BUILT, **negative**, no slot

| role | file / stem | sha256 (`.tif` / `-zeros.tif`) | form note (110 chars) | evidence |
|---|---|---|---|---|
| **DO NOT SLOT** (format-safe if human overrides) | `releases/gems89-bstp40-20261024-2e7e8a8f.tif` | `2e7e8a8f52ccf46de43169891c7c4cf6e697cdd694592df1ef6c7cb8abebf596` / `4b86c16d11f13ff0e65d09e020969fd365b545a504e18ae34f3d7a71479caa33` | `gems89 bstp40: R0 top60% u-credit + 40% basement-step x cond x edge dots >3px off-parent; n=37654; HOLDOUT-NEG` | HOLDOUT-DTI −0.0254 [−0.0296,−0.0210] (`segment-holdout-v1`, 39,310 px); verdict negative — see `registry/run_card_bstp40.json` |

Siblings `bstp40corr` (`e3b6d3d2`) and `bstp40corrE` (`598993b2`) were
withdrawn; their TIFs are deleted and they have no ledger row — do not
re-register those sha8s.

---
The human submits manually from their own registered account. Nothing here logs in,
scrapes, or uploads. Upload the NaN-outside `.tif`; `-zeros.tif` is only a fallback.
**Never upload both twins in separate slots.** Submission name = the file stem.

## This session's builds (`SNAP` directional corner, 2026-10-24) — upload as a PAIR

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

## Phase-2 TRACKB products (held off weekly slots unless human decides; Week 5–6 blind-final candidates)

Dual-phase R0-consolidating 150-trace builds (`3.76%–4.21%` of R0 changed, preserving Phase 1 DTI while consolidating `150` strike-consistent `>= 1.00 km` continuous fault traces + RFC 7946 WGS84 `LineString` GeoJSON dossiers + per-trace geologist paragraphs in `docs/TRACKB_EVIDENCE.md`; cards in `ledger/MECHANISM_CARDS.md` Part IX):

| role | raster (`.tif`) & dossier (`.geojson`) | sha256 (`.tif` / `-zeros.tif`) | form note (`<= 140` chars) | predicted (`MODEL`) |
|---|---|---|---|---|
| **Phase 2 Primary (zero R0 drop)** | `releases/h33-h33-2-b2-TRACKBt150add-20261024-5a09404f.tif`<br>`releases/h33-h33-2-b2-TRACKBt150add-20261024-5a09404f.geojson` | `5a09404ffe905e3a3d809ba0cb1ebcd5dc2ccdb66f9d2911ef9bc6ab2c3034e9` / `f28c74a5d6de08420c123d58e2f63087d4eb0a54f744348d59bf8c660e37bf62` | `R0 h33-h33-2-b2; TRACKB t150add: +1415px (3.8%) 150 >=1km traces, n=39069; P1 +0.000 / P2 +0.012 MODEL` | P1 **+0.000** (`−0.004…+0.004`)<br>P2 **+0.012** (`+0.004…+0.024`) |
| **Phase 2 Mass-Neutral (`S=37,654`)** | `releases/h33-h33-2-b2-TRACKBt150swap-20261024-8cfcbe4c.tif`<br>`releases/h33-h33-2-b2-TRACKBt150swap-20261024-8cfcbe4c.geojson` | `8cfcbe4ca7da5c0493020d897c10a771422894b3b7546848215c260e736ba1b9` / `4766d3431c1394f47ec441fa5d5b3e7f3a18d71a79d7edbd21922521600c554d` | `R0 h33-h33-2-b2; TRACKB t150swap: 1415px (3.8%) >=1km traces swap speckles, n=37654; P1 -0.002 / P2 +0.011 MODEL` | P1 **−0.002** (`−0.008…+0.004`)<br>P2 **+0.011** (`+0.002…+0.022`) |
| **Phase 2 Wash-Bridged (`S=37,654`)** | `releases/h33-h33-2-b2-TRACKBt150link-20261024-eded7713.tif`<br>`releases/h33-h33-2-b2-TRACKBt150link-20261024-eded7713.geojson` | `eded7713a9f65cc95c5049e4742080643ab00accd5c04296f4fd3bd756396b04` / `6a00e101f442a080ba945a471b1df637af453540a57f9a09f635da4158b1f24f` | `R0 h33-h33-2-b2; TRACKB t150link: 1586px (4.2%) wash-bridged >=1km traces swap speckles, n=37654; P1 -0.003 / P2 +0.009 MODEL` | P1 **−0.003** (`−0.010…+0.005`)<br>P2 **+0.009** (`+0.001…+0.021`) |
| **Review-Only 12-Trace Extract (DO NOT SUBMIT FOR SCORE)** | `releases/h33-h33-2-b2-TRACKBtop12-20261024-fb156257.tif`<br>`releases/h33-h33-2-b2-TRACKBtop12-20261024-fb156257.geojson` | `fb15625714547a192da792b26466085c5ce849854c8af35206450b5c332bc370` / `2e3c8fa115e096f6b369766323e425f6d313ef9372fa70d7524bfbe0a16b0266` | `R0 h33-h33-2-b2; TRACKB top12: 12 strike-consistent traces >=1km, 145 member dots, GeoJSON; Phase 2 only` | `n/a` (`145` dots only; `ledger/TRACKB_TRACES.md`) |

## Rest of the gated queue (`ledger/submissions.csv`, `status = BUILT`)

- **CONCENTRATION 12.8 km:** `int10` (`bcade136`, +0.008), `int20` (`357b4ac4`, +0.009), `geod15` (`259ea040`, +0.003).
- **CONCENTRATION 5 km:** `cat10` (`2dc19377`, +0.009), `cat20` (`4d229938`, +0.019), `cat10away` (`f7b8aa28`, −0.009 sign control).
- **CONCENTRATION 2 km:** `da3a4886` / `51ba9656` / `1e857586` — separate on-H19 mechanism (`+0.0024` / `−0.0028` / `−0.0126`).
- **RELIEF** `r10` `366c87ca`, `r15` `6aa774ce`, `r15s` `5f0ae851`; **MASS** `m10uniq` `beed130f`, `m20uniq` `87ec6213`, `m10rand` `7a4c49b6`; **SPACING** `alongstrike` `3b263c7a` (held `poisson` `ff167173`, `lattice` `454c9098`).
- **SNAP factorial** (`{window} × {gate}`, complete): `1p0px-g0p00` `1add5aa6`, `1p0px-g0p01` `2916ec2d`, `1p0px-g0p02` `384435e6`, `1p4px-g0p00` `e1474851`, `1p4px-g0p01` `afc60a25`, upstream `1p4px-g0p02` `0b6a2ab2`, `2p0px-g0p00` `69db3aae`, `2p0px-g0p01` `7bdaa58b`, `2p0px-g0p02` `b2019f55`.
- **PRUNE:** upstream already covers the brief collars at 1–4 px; not rebuilt (`IRREGULARITIES.md` item 14).

## Format receipt (`registry/format_receipts.json` — all 62 files re-read from disk)

| gate | result |
|---|---|
| grid vs pinned `sample_submission.tif`: `3730×3292`, `100 m`, `EPSG:32611`, `float32`, `1` band | **PASS ×62 files** (`31` `.tif` + `31` `-zeros.tif`) |
| values in `[0, 1]`; unit dots `== 1.0`; `0` NaN inside footprint; `NaN` / `0.0` outside per twin | **PASS ×62 files** |
| expected per-ledger dot counts; NaN/zeros twins carry identical masks | **PASS ×31 pairs** (`t150add` = 39,069; `t150swap`/`t150link`/SNAP/CONC/RELIEF/SPACING = 37,654; `MASS` = 33,889 / 30,123; `top12` = 145) |
| zero catalogue mass (`0` dots on `existing_faults.tif`); moved/added targets `d_cat >= 3.00 px` | **PASS ×62 files** |
| Phase-2 GeoJSON dossiers (`releases/*TRACKB*.geojson`, all traces `>= 1.0 km` + geologist evidence) | **PASS ×4 GeoJSONs** |
| exact-hash and repeated `(parent, axis, value)` dedupe; all `form_note <= 140` chars | **PASS (`146` ledger rows: `31` `GEMSDOE89` + `115` upstream)** |
| R0 recipe rebuild vs both parent SHA-256 pins (`c55bafc4…`, `baeae321…`) | **PASS (`tools/rebuild_r0.py`, 2026-10-24)** |
| unit tests (`86 passed`) / leakage canary | **PASS** / **PASS** (`max AUC 0.665 < 0.90`) |

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
