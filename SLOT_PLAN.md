# SLOT PLAN — GEMSDOE89 (integrated CONCENTRATION + SNAP + PRUNE + MASS + RELIEF + SPACING, 2026-10-24)

- **Timeline:** 2026-10-24 → **2026-12-03** (`UNVERIFIED` deadline; human confirms) ≈ 40 days ≈ **~17 rolling slots** (`1 entity × 3/week`) + **1 blind final**. Slots used: `__ / 3` (human supplies).
- **Baseline:** Parent R0 `h33-h33-2-b2`, byte-exact (`c55bafc4…` zeros, `baeae321…` NaN; `37,654` unit dots), live **0.2778 = CLAIM** (no receipt here). `TOP_PUBLIC`: `____` (date `____`).
- **Evidence rule:** `|Δ| < 0.01` is **no evidence**; report-only instruments (`PROXY` / canary / `SGMC`) never gate a file and are never called scores.
- **Completed fleet:** 24 variant pairs (48 `.tif` files) spanning all 6 core axes in `releases/`.

## Core experimental families in `releases/`

| Axis / Family | Values (`sha8`) | Central `MODEL`s | Mechanism & role |
|---|---|---|---|
| **CONCENTRATION 12.8 km** | `12p8km-int10` (`bcade136`) / `int20` (`357b4ac4`) / `geod15` (`259ea040`) | `+0.008` / `+0.009` / `+0.003` | Faulds accommodation-zone prior (`CV_12.8km = 0.5533`, 3-seed holdout `+0.0040`) + catalogue-free GPS strain (`geod15`) |
| **CONCENTRATION 5 km & 2 km** | `cat10` (`2dc19377`) / `cat20` (`4d229938`) / `cat10away` (`f7b8aa28`); `m3765`..`m7531` | `+0.009` / `+0.019` / `−0.009`; `+0.002`..`−0.013` | Zero→top25% catalogue blocks + away sign control; independent 2 km sequential H19 marginals |
| **SNAP (gateless)** | `2p0px-g0p00` (`69db3aae`) / `1p4px` (`e1474851`) / `1p0px` (`1add5aa6`) | `+0.028` / `+0.028` / `+0.027` | Physical EM/gravity HG crest alignment (`1.86 px` displacement, fixed block counts) |
| **PRUNE (catalogue collar)** | `c3p0` (`7b101829`) / `c1p0` (`85cf176a`) / `c4p0` (`d681292b`) | `+0.003` / `−0.004` / `−0.001` | 300 m full kernel clearance (`c3p0`), 100 m proximal splay swap-in (`c1p0`), 400 m flight-line smear purge (`c4p0`) |
| **MASS & RELIEF** | `m10uniq` (`beed130f`) / `m20uniq` (`87ec6213`); `r10` (`366c87ca`) / `r15` (`6aa774ce`) | `+0.002` / `+0.004`; `+0.003` / `+0.004` | Prune low-credit far-field mass (`m10uniq`); transfer 10–15% mass from range to piedmont (`r10`/`r15`) |
| **SPACING** | `alongstrike` (`3b263c7a`) / `poisson` (`ff167173`) / `lattice` (`454c9098`) | `+0.002` / `−0.010` / `−0.007` | On-ridge 1D geodesic equipartition (`alongstrike`); 2D corridor blue noise and hex lattice controls |

## Next 3 slots, in order

| # | File | Predicted live change (`MODEL`) | What the result changes |
|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136.tif` *(or 5 km `…-CONC5kmcat10-…-2dc19377.tif`, `+0.009`)* | **+0.008** (`−0.006…+0.018`) *(alt `+0.009`, `−0.010…+0.038`)* | **Spatial-concentration fork** (pick ONE 10% arm). `≥ 0.2878` (`+0.010`) → run matched 20% dose (`12p8km-int20` or `CONC5kmcat20`) in Slot 3. `≤ 0.2678` (`−0.010`) → catalogue bias inverted → run catalogue-free `12p8km-geod15` (GPS strain) or `CONC5kmcat10away`. |
| **2** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` | **+0.028** (`−0.028…+0.084`) | **Orthogonal local-placement fork** (`1.86 px` EM-crest snap at fixed block counts). `≥ 0.2878` → snap live, earns `snap1p4px-g0p00` if Slot 1 is null; `≤ 0.2678` → retire EM-crest SNAP. |
| **3** | conditional: `…-conc-12p8km-int20-…-357b4ac4.tif` if Slot 1 `≥ 0.2878`; `…-conc-12p8km-geod15-…-259ea040.tif` if Slot 1 `≤ 0.2678`; `…-snap1p4px-g0p00-…-e1474851.tif` if Slot 2 `≥ 0.2878`; else **`…-prune-c3p0-20261024-7b101829.tif`** / `…-MASSm10uniq-…-beed130f.tif` **or HOLD** | `+0.009` / `+0.003` / `+0.028` / **+0.003** / `+0.002` | Tests `CV_12.8km > 0.59` saturation (`int20`), active strain vs map bias (`geod15`), or SNAP window dose (`1p4px`); if both Week 1 forks are within `±0.010`, pivots to **300 m full kernel collar clearance (`prune-c3p0`)** or dot count (`MASS`) / quota hold. |

## Weeks to the deadline (`2026-12-03`)

| Week | Dates | Plan |
|---|---|---|
| 1 | 10-24 → 10-29 | Slots 1 + 2 (one concentration fork + one local-placement fork); keep 1 slot spare for receipts |
| 2 | 10-30 → 11-05 | Conditional Slot 3 from Week 1 receipts; test PRUNE `c3p0` or MASS `m10uniq` if Week 1 is flat |
| 3–4 | 11-06 → 11-19 | Combine **only** axes with live receipts `≥ +0.010`, one factor at a time |
| 5 | 11-20 → 11-26 | Confirm composite child vs its direct parent; freeze primary + `-zeros.tif` fallback |
| 6 | 11-27 → 12-03 | Re-validate format/hashes of both final twins; submit **1 blind final** choice |

## Proposed better axes (mechanism · confounder · falsifier) — not built this session

| Axis | Structural mechanism | Non-fault confounder / mimic | Falsifier |
|---|---|---|---|
| **RELAY-BRIDGE** | Bridge co-linear / en-echelon strand tips (`≤ 12 px`, strike diff `≤ 20°`) across step-over ramps where breaching faults nucleate (https://www.osti.gov/servlets/purl/1249065) | Bridges aligned stream scarps or dike swarms, adding `P` with zero `T` | Live receipt `< R0 + 0.010`, or 25% strand-holdout loses to random tip pairs |
| **TRACKB-DIP-OFFSET** | Normal range-front faults dip `45°–60°` basinward, shifting gravity/magnetic HG crests `2–5 px` into the hanging wall relative to surface scarps | Sub-vertical strike-slip faults and volcanic contacts have near-zero dip offset | Live receipt drops `≥ 0.010` vs R0, or loses to symmetric `SNAP` |
| **COVERAGE-NEUTRAL CONC** | Shift block mass while constraining H19 `ΔT ≈ 0` so km-scale prior gain never trades off centerline retention | Joint optimization simultaneously alters local spacing | Fails to beat `conc-12p8km-int10` / `CONC5kmcat10` by `≥ 0.005` |
| **REPEAT-CALIBRATION** | Submit byte-exact rebuilt R0 (`baeae321…`) once to convert `0.2778` from `CLAIM` → `RECEIPT` | Burns 1 of ~18 slots with zero expected leaderboard climb | Receipt differs from `0.2778` by `> 0.005`, invalidating `CLAIM`-anchored deltas |
