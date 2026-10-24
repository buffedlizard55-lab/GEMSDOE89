# SLOT PLAN — GEMSDOE89 (integrated 3-family CONCENTRATION + SNAP/MASS/RELIEF/SPACING, 2026-10-23)

- **Timeline:** 2026-10-23 → **2026-12-03** (`UNVERIFIED` deadline; human confirms) ≈ 41 days ≈ **~18 rolling slots** (`1 entity × 3/week`) + **1 blind final**. Slots used: `__ / 3` (human supplies).
- **Baseline:** Parent R0 `h33-h33-2-b2`, byte-exact (`c55bafc4…` zeros, `baeae321…` NaN; `37,654` unit dots), live **0.2778 = CLAIM** (no receipt here). `TOP_PUBLIC`: `____` (date `____`).
- **Evidence rule:** `|Δ| < 0.01` is **no evidence**; report-only instruments (`PROXY` / canary / `SGMC`) never gate a file and are never called scores.

## Three distinct `CONCENTRATION` families in `releases/` (not pure scale ablations — priors & placements differ)

| Family | Values (`sha8`) | Central `MODEL`s | Mechanism & queue role |
|---|---|---|---|
| **12.8 km (`128 px`) interaction & GPS strain** | `12p8km-int10` (`bcade136`) / `int20` (`357b4ac4`) / `geod15` (`259ea040`) | `+0.008` / `+0.009` / `+0.003` | Faulds tip/junction/step-over prior (`CV_12.8km = 0.5533` inside `0.51–0.59`, 3-seed strand-holdout `+0.0040`, tighter band `−0.006…+0.018`) + **only catalogue-free GPS/seismicity arm** (`geod15`) |
| **5 km (`50 px`) raw catalogue + Sobel `q`** | `cat10` (`2dc19377`) / `cat20` (`4d229938`) / `cat10away` (`f7b8aa28`) | `+0.009` / `+0.019` / `−0.009` | Zero→top25% catalogue-pixel blocks (`−0.010…+0.038`) + exact sign-reversed control (`cat10away`) |
| **2 km (`20 px`) catalogue + H19 marginals** | `m3765` (`da3a4886`) / `m5648` (`51ba9656`) / `m7531` (`1e857586`) | `+0.0024` / `−0.0028` / `−0.0126` | Held separate on-H19 mechanism (`<3 px` crowding counter-indicator at 15%/20%) |

## Next 3 slots, in order

| # | File | Predicted live change (`MODEL`) | What the result changes |
|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136.tif` *(or 5 km `…-CONC5kmcat10-…-2dc19377.tif`, `+0.009`)* | **+0.008** (`−0.006…+0.018`) *(alt `+0.009`, `−0.010…+0.038`)* | **Spatial-concentration fork** (pick ONE 10% arm — never both in Week 1). `≥ 0.2878` (`+0.010`) → run matched 20% dose (`12p8km-int20` or `CONC5kmcat20`) in Slot 3. `≤ 0.2678` (`−0.010`) → catalogue bias inverted → run catalogue-free `12p8km-geod15` (active GPS strain) or `CONC5kmcat10away` (frontier sign control). |
| **2** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` | **+0.028** (`−0.028…+0.084`) | **Orthogonal local-placement fork** (`1.86 px` EM-crest snap at fixed block counts). `≥ 0.2878` → snap live, earns `snap1p4px-g0p00` if Slot 1 is null; `≤ 0.2678` → retire EM-crest SNAP. |
| **3** | conditional: `…-conc-12p8km-int20-…-357b4ac4.tif` (or `CONC5kmcat20`) if Slot 1 `≥ 0.2878`; else `…-conc-12p8km-geod15-…-259ea040.tif` (or `CONC5kmcat10away`) if Slot 1 `≤ 0.2678`; else `…-snap1p4px-g0p00-…-e1474851.tif` if Slot 2 `≥ 0.2878`; else `…-MASSm10uniq-…-beed130f.tif` / `…-relief-r10-…-366c87ca.tif` **or HOLD** | `+0.009` (`+0.019`) / `+0.003` (`−0.009`) / `+0.028` / `+0.002` | Tests `CV_12.8km > 0.59` saturation (`int20`), active crustal strain vs catalogue bias (`geod15`), or SNAP window dose (`1p4px`); if both Week 1 forks are inside `±0.010`, pivots to count (`MASS`) / geomorphic class (`RELIEF`) or holds quota. |

## Weeks to the deadline (`2026-12-03`)

| Week | Dates | Plan |
|---|---|---|
| 1 | 10-23 → 10-29 | Slots 1 + 2 (one concentration fork + one local-placement fork); keep 1 slot spare for receipts |
| 2 | 10-30 → 11-05 | Conditional Slot 3 from Week 1 receipts; record every `receipt_score` + `date` in `ledger/submissions.csv` |
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
