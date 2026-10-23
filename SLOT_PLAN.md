# SLOT PLAN — GEMSDOE89 (CONCENTRATION session, 2026-10-23)

- **Timeline:** 2026-10-23 → **2026-12-03** (`UNVERIFIED`) ≈ 41 days ≈ **18 rolling slots** (one entity × 3/week) + one blind final. Slots used: `__ / 3` (human supplies).
- **Baseline:** R0 `h33-h33-2-b2`, byte-exact (`c55bafc4…` zeros; `baeae3219…` NaN), **0.2778 = CLAIM**. Best receipt: none. `TOP_PUBLIC`: `____` (human + date).
- **Rule:** any live change with `|Δ| < 0.01` is **no evidence**. PROXY/MODEL/canary/SGMC never gate a file and are never called scores.

## Next 3 slots, in order

| # | File | Predicted live change | What the result changes |
|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-conc2km-b50-t33-m3765-20261023-da3a4886.tif` | **+0.0024** MODEL (−0.0127…+0.0174) | ≥ +0.010 → 2 km prior can pay its H19 coverage cost; slot 3 = m5648. Inside ±0.010 → no evidence, hold both larger doses. ≤ −0.010 → close this CONCENTRATION recipe. |
| **2** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` | **+0.028** MODEL (−0.028…+0.084) | ≥ +0.010 → placement mechanism is live; use snap1p4 as the conditional third arm if slot 1 did not fire. ≤ −0.010 → retire SNAP/EM-crest placement. |
| **3** | conditional: `…conc2km-b50-t33-m5648…51ba9656` if slot 1 ≥ **0.2878**; else `…snap1p4px-g0p00…e1474851` if slot 2 ≥ **0.2878**; else `…relief-r10…366c87ca` **or HOLD** | −0.0028 / +0.028 / +0.003 MODEL | Tests dose only after a ≥ +0.010 receipt. Otherwise preserves one independent RELIEF probe—or the slot for late receipts. C3/m7531 stays held unless both CONC doses fire. |

Do not submit two same-question dose arms together. The 15%/20% CONC central
MODELs are negative because H19 coverage and crowding worsen; a positive C1
receipt is the only reason to override that hold. Existing negative-Model
SPACING `poisson`/`lattice` arms remain held.

## Weeks to the deadline

| week | dates | plan |
|---|---|---|
| 1 | 10-23 → 10-29 | slots 1 + 2; keep one spare for late receipts |
| 2 | 10-30 → 11-05 | conditional slot 3; record every receipt and exact file hash |
| 3-4 | 11-06 → 11-19 | combine only axes with receipts ≥ +0.010, one factor at a time |
| 5 | 11-20 → 11-26 | confirm winner against its parent; freeze final + fallback |
| 6 | 11-27 → 12-03 | re-validate both final candidates; one blind final submission |

## Proposed better axes — mechanism · confounder · falsifier (not built)

| Axis | Mechanism | Confounder / mimic | Falsifier |
|---|---|---|---|
| **COVERAGE-NEUTRAL CONC** | Joint swaps shift 2 km block mass while constraining H19 ΔT ≈ 0 | multi-pixel optimization also changes spacing | cannot beat C1 by ≥0.005, or fails the neutral-coverage construction |
| **DEDUPE** | remove dots with least exact unique credit; no refill | de-clustering is also a spacing edit | fails to beat count-matched MASS by ≥0.005 |
| **RELAY-BRIDGE** | connect compatible en-echelon H19 tips on likely unmapped relay faults | channels/dike swarms bridge tips too | receipt ≤ R0, or multi-segment PROXY loses to random tip pairs |
| **TRACKB-DIP-OFFSET** | shift potential-field crests basinward for dipping range-front faults | vertical faults/volcanic contacts have no such offset | receipt drops ≥0.005 vs R0 |
| **REPEAT-CALIBRATION** | exact R0 resubmission converts CLAIM to RECEIPT and bounds upload noise | costs a slot; no expected raster gain | receipt differs from 0.2778 by >0.005 |
