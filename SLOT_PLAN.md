# SLOT PLAN — GEMSDOE89 (integrated after the SNAP-session merge, 2026-10-23)

- **Timeline:** 2026-10-23 → **2026-12-03** (`UNVERIFIED` deadline) ≈ 41 days ≈
  **~18 rolling slots** (1 entity × 3/week) + 1 blind final. Slots used:
  `__ / 3` (human must supply).
- **Baseline:** R0 `h33-h33-2-b2` recipe-rebuilt byte-exact (`c55bafc4…` zeros,
  `baeae321…` nan), **0.2778 = CLAIM** (no receipt here). `TOP_PUBLIC`: `____`.
- **Rule:** any live change `< 0.01` is **no evidence**; report-only instruments
  (PROXY/canary/SGMC) never gate and are never called scores.

## Next 3 slots, in order

| # | File | Predicted live change | Submit only if | What the result changes |
|---|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif` | **+0.003** MODEL (−0.012…+0.018) | gates green (verified) | Allocation fork. ≥ +0.010 → class allocation transfers → slot 3 = r15. Inside ±0.010 → close RELIEF *and* CONCENTRATION. < −0.010 → placement beats allocation, prioritize SNAP. |
| **2** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` | **+0.028** MODEL (−0.028…+0.084) | human knowingly accepts the widest band in the repo | Placement fork, independent of slot 1 (position change at fixed count/CV). ≥ +0.010 → snap mechanism real → slot 3 = 1p4px window dose; receipts vs upstream gated arms isolate the *gate*. Inside ±0.010 → gateless dead; test upstream `2p0px-g0p01` (+0.018…+0.044 MODEL, GEMSDOE84) for selection-vs-dose. ≤ −0.010 → retire SNAP + EM-crest story. |
| **3** | conditional: `…relief-r15…6aa774ce` if slot 1 ≥ **0.2878**; else `…snap1p4px-g0p00…e1474851` if slot 2 ≥ **0.2878**; else `…spacing-alongstrike…3b263c7a` (band −0.003…+0.006) **or HOLD** | +0.004 / +0.028 / +0.002 | the named parent arm scored ≥ +0.010 | Dose-response for whichever fork fired; a null fork makes `alongstrike` the cheapest remaining probe — or hold the slot for a late receipt. |

Same-week: never two same-question files together (no r15+r15s; no two gate-0
snap windows — the window dose saturates at 80.8→83.1 % moved). Negative-Model
arms (`SPACING poisson` −0.010, `lattice` −0.007) stay held unless their own
cards' triggers fire.

## Weeks to the deadline

| week | dates | plan |
|---|---|---|
| 1 | 10-23 → 10-29 | slots 1 + 2; keep 1 spare for late receipts |
| 2 | 10-30 → 11-05 | slot 3 conditional as above; record every receipt |
| 3-4 | 11-06 → 11-19 | combine the axes with receipts ≥ +0.010, one factor at a time (expect one axis only) |
| 5 | 11-20 → 11-26 | confirm winner vs its own parent; freeze final file + fallback |
| 6 | 11-27 → 12-03 | re-validate format of **both**; one blind final submission |

## Proposed better axes (mechanism · confounder · falsifier) — not built

| Axis | Mechanism | Confounder / mimic | Falsifier |
|---|---|---|---|
| **DEDUPE** | drop the most *redundant* dots (exact `marginal_gain_remove`), bottom 15-25 %, no refill: the max operator means a neighbour already claims the credit | de-clusters ≈ spacing effect — `SPACING` at matched removal is its control | fails to beat `MASS −10 %` by ≥ 0.005 |
| **FLOOR** | ~2,000 dots on the flat-slope tercile (33 % of footprint, 0.1 R0 dots/1000 px) at catalogue-proportional spacing | flat ground has no DEM edge — a bet on signal R0's own model declined | score < R0 − 0.005 → coverage gap is correctly empty |
| **DOSE** | one byte-identical re-submission per month | burns a slot with zero expected gain | receipt differs > 0.005 → CLAIM-anchored deltas across the ledger are invalid |
| **RELAY-BRIDGE** | en-echelon strand tips (≤12 px, ≤20°) bridged: mass on unmapped relay faults | bridges channel scarps/dike swarms, inflating P without hitting G | receipt ≤ R0, or withheld multi-segment PROXY loses to random tip pairs |
| **TRACKB-DIP-OFFSET** | range-bounding faults dip 45-60° basinward; shift gravity/mag crest 2-5 px hanging-wall-ward toward the surface trace | sub-vertical faults/volcanic contacts have ~zero dip offset | receipt drops ≥ 0.005 vs R0 |
| **REPEAT-CALIBRATION** | resubmit exact R0 to convert CLAIM → RECEIPT and bound slot noise | costs 1 of ~18 slots, zero expected gain | receipt differs from 0.2778 by > 0.005 |

Future in-axis values (not new axes): SNAP response-surface variants (DEM-scarp
vs EM-only vs fused) — only after one snap receipt shows any sign of life.
