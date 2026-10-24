# SLOT PLAN — GEMSDOE89 (2026-10-24, after TRACKB session)

- **Baseline:** Parent R0 `h33-h33-2-b2`, byte-exact (`c55bafc4…` zeros / `baeae321…` NaN; 37,654 unit dots), live **0.2778 = CLAIM** (no receipt here). **TOP_PUBLIC = ____** (date ____). **Slots this week: __ / 3** (human fills). Deadline **2026-12-03 UNVERIFIED** (pages barred; human confirms) → ≈6 weeks ≈ 18 rolling slots + 1 blind final.
- **Evidence rule:** `|Δlive| < 0.01` is no evidence. `PROXY`/`MODEL`/canary never gate and are never scores.
- **This session built TRACKB** (Phase-2 trace inventory + 3 held structural-concentration rasters, `ledger/MECHANISM_CARDS_TRACKB.md`). It is **not a weekly-slot candidate unless the human decides**; its Phase-1 jitter MODEL is a coverage-cost floor (−0.002 / −0.012 / −0.021 central). **The 21 scored-axis pairs remain `BUILT (unscored)` — live receipts are the bottleneck, not more files.**

## Next 3 slots, in order (scored axes; TRACKB held out)

| # | File | Predicted (MODEL) | What the result changes |
|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136.tif` *(alt `…-CONC5kmcat10-…-2dc19377.tif`)* | **+0.008** (−0.006…+0.018) *(alt +0.009)* | Spatial-prior fork. `≥ 0.2878` → matched 20 % dose (`12p8km-int20` / `cat20`) in Slot 3. `≤ 0.2678` → catalogue-free `12p8km-geod15` / sign-control `cat10away`. |
| **2** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` | **+0.028** (−0.028…+0.084) | Orthogonal local-placement fork (≤2 px EM-crest snap, fixed count). `≥ 0.2878` → snap live, earn `snap1p4px`; `≤ 0.2678` → retire SNAP. |
| **3** | conditional: dose/control from Slot 1; else `snap1p4px` if Slot 2 `≥ 0.2878`; else `MASSm10uniq` / `relief-r10` or **HOLD** | +0.009 / +0.003 / +0.028 / +0.002 | Confirm concentration dose, active-strain vs map bias, or SNAP dose; if both Week-1 forks are inside ±0.010, pivot to count/geomorphology or hold quota. |

**Strong alternative for any Slot 1:** submit byte-exact rebuilt R0 (`baeae321…`) once to convert `0.2778` from **CLAIM → RECEIPT**. It de-risks every MODEL delta anchored to 0.2778 (see "better axes" below); costs one slot with zero expected climb. The human decides.

## Weeks to the deadline (2026-12-03)

| Week | Plan |
|---|---|
| 1 (10-24→10-29) | Slots 1 + 2 (one prior fork + one placement fork); keep 1 spare for receipts. Record every `receipt_score`+`date`. |
| 2 (10-30→11-05) | Conditional Slot 3; if all ±0.010, prioritize a REPEAT-CALIBRATION receipt before spending more. |
| 3–4 (11-06→11-19) | Combine **only** axes with live receipts `≥ +0.010`, one factor at a time; decide whether any TRACKB trace earns a Phase-2-oriented submission. |
| 5 (11-20→11-26) | Confirm composite child vs its direct parent; freeze primary + `-zeros.tif` fallback. |
| 6 (11-27→12-03) | Re-validate format/hashes of both final twins; choose **1 blind final**. |

## Proposed better axes (mechanism · confounder · falsifier) — not built

| Axis | Mechanism | Confounder / mimic | Falsifier |
|---|---|---|---|
| **REPEAT-CALIBRATION** | Resubmit byte-exact R0 to verify the 0.2778 anchor that all MODELs use | Burns a slot; if the true leaderboard differs, deltas were mis-anchored | Receipt differs from 0.2778 by > 0.005 → re-anchor all predictions |
| **RELAY-BRIDGE** | Bridge co-linear / en-echelon tips (≤ 12 px, strike diff ≤ 20°) across step-over ramps where breaching faults nucleate (https://www.osti.gov/servlets/purl/1249065) | Bridges stream scarps / dike swarms (P with zero T) | Live receipt < R0 + 0.010, or loses to random tip pairs on a 25 % strand holdout |
| **TRACKB-DIP-OFFSET** | Normal range-front faults dip 45–60° basinward, offsetting gravity/magnetic crests 2–5 px into the hanging wall | Strike-slip / volcanic contacts have ~zero dip offset | Drops ≥ 0.010 vs R0, or loses to symmetric SNAP |
| **COVERAGE-NEUTRAL CONC** | Shift block mass while holding H19 `ΔT ≈ 0` so the prior gain never trades centerline retention | Joint optimization also alters local spacing | Fails to beat `conc-12p8km-int10` / `cat10` by ≥ 0.005 |
| **TRACKB-NULL (control)** | Move the same 10 % of dots to random legal corridor pixels (matched count) to isolate structure from "any relocation" | Legality/collar effects | TRACKB-`tr10` fails to beat the null → the structure, not the move, is unproven |
