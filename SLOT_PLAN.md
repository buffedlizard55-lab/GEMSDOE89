# SLOT PLAN — GEMSDOE89 (integrated after CONCENTRATION build, 2026-10-23)

- **Timeline:** 2026-10-23 → **2026-12-03** (`UNVERIFIED` deadline; human must confirm) ≈ 41 days ≈ **~18 rolling slots** (`1 entity × 3/week`) + **1 blind final**. Slots used this week: `__ / 3` (human supplies).
- **Baseline:** Parent R0 `h33-h33-2-b2` rebuilt byte-exact (`c55bafc4…` zeros, `baeae321…` NaN; `37,654` unit dots), live **0.2778 = CLAIM** (no receipt in this repo). `TOP_PUBLIC`: `____` (date `____`).
- **Evidence rule:** any live receipt change `< 0.01` is **no evidence**; report-only instruments (`PROXY` / leakage canary / `SGMC`) never gate a file and are never called scores.

## Next 3 slots, in order

| # | File | Predicted live change (`MODEL`) | Submit only if | What the result changes |
|---|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136.tif` | **+0.008** (`−0.006 … +0.018`; 3-seed strand-holdout `+0.0040`, `+0.0052` over shuffle) | gates green (verified) | **12.8 km structural-concentration fork** (`7.3×` fault-interaction contrast vs `1.4×` in `RELIEF`; keeps `CV_12.8km = 0.5533` inside `0.51–0.59`). `≥ +0.010` (`≥ 0.2878`) → run `int20` dose in Slot 3. `≤ −0.010` (`≤ 0.2678`) → test truth sits in under-mapped basins → run catalogue-free `geod15` in Slot 3. Inside `±0.010` → hold `int20`. |
| **2** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` | **+0.028** (`−0.028 … +0.084`) | human accepts widest band (alt low-variance probe: `…-relief-r10-…-366c87ca.tif`, `+0.003`) | **Orthogonal local-placement fork** (`1.86 px` EM-crest snap at fixed block counts vs Slot 1's `95.5 px` inter-block transfer). `≥ +0.010` → snap real, run `1p4px-g0p00` or upstream gated `2p0px-g0p01` to price gate vs window. `≤ −0.010` → retire EM-crest SNAP. |
| **3** | conditional: `…-conc-12p8km-int20-…-357b4ac4.tif` if Slot 1 `≥ 0.2878`; else `…-conc-12p8km-geod15-…-259ea040.tif` if Slot 1 `≤ 0.2678`; else `…-snap1p4px-g0p00-…-e1474851.tif` if Slot 2 `≥ 0.2878`; else `…-relief-r10-…-366c87ca.tif` / `…-MASSm10uniq-…-beed130f.tif` **or HOLD** | `+0.009` / `+0.003` / `+0.028` / `+0.003` / `+0.002` | Week 1 receipts recorded in `ledger/submissions.csv` | Tests `CV_12.8km = 0.656 > 0.59` saturation (`int20`), catalogue-free active-strain prior (`geod15`), or SNAP window dose (`1p4px`); if both Week 1 forks land inside `±0.010`, probes geomorphic `RELIEF r10` / count `MASS m10uniq` or holds quota. |

Same-week rule: never submit two files testing the same axis in one week (never `int10 + int20`, `r10 + r15`, or two `g0p00` snap windows together). Negative-`MODEL` arms (`SPACING poisson` `−0.010`, `lattice` `−0.007`, `MASS m10rand` `−0.002`) remain held unless their card triggers fire.

## Weeks to the deadline (`2026-12-03`)

| Week | Dates | Plan |
|---|---|---|
| 1 | 10-23 → 10-29 | Submit Slots 1 (`conc-12p8km-int10`) + 2 (`snap2p0px-g0p00`); reserve 1 slot for receipt follow-up |
| 2 | 10-30 → 11-05 | Execute conditional Slot 3 from Week 1 receipts; probe `MASS m10uniq` or `RELIEF r10` if unprobed |
| 3–4 | 11-06 → 11-19 | Combine **only** axes with live receipts `≥ +0.010`, one factor at a time (e.g., `CONCENTRATION` + winning local placement/count) |
| 5 | 11-20 → 11-26 | Confirm composite child vs its direct parent on live receipt; freeze primary + byte-verified fallback |
| 6 | 11-27 → 12-03 | Re-validate format/hashes of final choice + `-zeros` twin; submit **1 blind final** choice |

## Proposed better axes (mechanism · confounder · falsifier) — not built this session

| Axis | Structural mechanism | Non-fault confounder / mimic | Falsifier |
|---|---|---|---|
| **RELAY-BRIDGE** | Bridge co-linear / en-echelon strand tips (`≤ 12 px`, strike diff `≤ 20°`) across step-over ramps where unmapped breaching faults nucleate (https://www.osti.gov/servlets/purl/1249065) | Links aligned stream-incision scarps, Tertiary dike segments, or shoreline benches, adding mass `P` with zero truth `T` | Live receipt `< R0 + 0.010`, or 25% strand-holdout loses to random tip-pair bridges at matched dot count |
| **TRACKB-DIP-OFFSET** | Normal range-front faults dip `45°–60°` basinward, shifting subsurface gravity/magnetic horizontal-gradient crests `2–5 px` into the hanging wall relative to the surface scarp | Sub-vertical strike-slip strands, steep caldera walls, and shallow volcanic flow contacts have near-zero dip offset | Live receipt drops `≥ 0.010` vs R0, or loses to `SNAP` symmetric crest alignment |
| **AZIMUTH-STRESS** | Weight off-`h19_5` candidates by alignment with Great Basin NNE extensional (`010°–035°`) and NW Walker Lane dextral (`315°–335°`) slip-tendency azimuths | Regional glacial/fluvial drainage and tilted volcanic hogbacks share NNE range-parallel strike | Fails to beat strike-agnostic `conc-12p8km-int10` by `≥ 0.005` on strand-holdout `MODEL` or `≥ 0.010` live |
| **REPEAT-CALIBRATION** | Submit byte-exact rebuilt R0 (`baeae321…`) once to convert `0.2778` from `CLAIM` → `RECEIPT` and anchor every single-axis delta | Burns 1 of ~18 rolling slots with zero expected leaderboard climb | Live receipt differs from `0.2778` by `> 0.005`, invalidating `CLAIM`-anchored deltas across the ledger |
