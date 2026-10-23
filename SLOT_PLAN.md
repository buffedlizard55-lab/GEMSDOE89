# SLOT PLAN — GEMSDOE89 (CONCENTRATION session, 2026-10-23)

- **Timeline:** 2026-10-23 → **2026-12-03** (`UNVERIFIED` deadline; automated
  competition-page access is barred by the site terms) ≈ 41 days ≈ **~18 rolling
  slots** (1 entity × 3/week) + 1 blind final. Slots used: `__ / 3` (human fills).
- **Baseline:** R0 `h33-h33-2-b2` recipe-rebuilt byte-exact (`c55bafc4…` zeros,
  `baeae321…` nan), **0.2778 = CLAIM** (no receipt in this repo). `TOP_PUBLIC`:
  `____` — still the only valid target number.
- **Rule:** any live change `< 0.01` is **no evidence**; report-only instruments
  (PROXY / canary / SGMC) never gate and are never called scores.

## What this session added

Three `CONCENTRATION` arms with an **independent** block prior (catalogued-fault
density over 5 km blocks). The two facts that motivate them, both measured here:
R0's block density is uncorrelated with catalogue density (r = **0.039**), and
**37.9 %** of R0's mass sits in the 862 blocks that contain no catalogued fault
at all. Cards: `ledger/MECHANISM_CARDS.md` Part IV.

| value | file | moved | predicted (MODEL) | role |
|---|---|---|---|---|
| `cat10` | `…-CONC5kmcat10-20261023-2dc19377.tif` | 3,765 (10 %) | **+0.009** (−0.010…+0.038) | primary |
| `cat20` | `…-CONC5kmcat20-20261023-4d229938.tif` | 7,531 (20 %) | **+0.019** (−0.010…+0.067) | dose |
| `cat10away` | `…-CONC5kmcat10away-20261023-f7b8aa28.tif` | 3,765 (10 %) | **−0.009** (−0.038…+0.010) | sign control |

## Next 3 slots, in order

| # | File | Predicted live change | Submit only if | What the result changes |
|---|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-CONC5kmcat10-20261023-2dc19377.tif` | **+0.009** MODEL (−0.010…+0.038) | gates green (verified) | First read on whether *block allocation* — not placement, not mass — is worth anything. ≥ +0.010 → slot 2 = `cat20` dose; ≤ −0.010 → prior inverted, slot 2 = `cat10away`; inside ±0.010 → slot 2 shifts to `snap2p0px` (below) and the prior needs a mechanism fix before another slot. |
| **2** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` | **+0.028** MODEL (−0.028…+0.084) | human accepts the widest band in the repo | Placement fork, independent of slot 1 (position change at fixed count and clearance). ≥ +0.010 → snap mechanism real → slot 3 = `snap1p4px` dose; ≤ −0.010 → retire SNAP; inside ±0.010 → gate ablation vs upstream gated arms. |
| **3** | conditional: `cat20` if slot 1 ≥ +0.010; `cat10away` if slot 1 ≤ −0.010; else `MASSm10uniq` (`beed130f`, +0.002, ceiling +0.0105) **or HOLD** | +0.019 / −0.009 / +0.002 | the named condition fired | Either the dose/sign confirmation of the only axis with headroom, or the cheapest positive-drift file in the repo (drop 10 % of the least valuable dots, nothing new placed). Holding keeps a slot for late receipts. |

Never two same-question files in one week. All three arms share one placement
rule, one spacing and one clearance, so a receipt on any of them is comparable
to the others and to R0 without a second confound.

## Weeks to the deadline

| week | dates | plan |
|---|---|---|
| 1 | 10-23 → 10-29 | slot 1 + slot 2; keep 1 spare for late receipts; record `receipt_score`/`receipt_date` |
| 2 | 10-30 → 11-05 | slot 3 conditional; close whichever axis read null inside ±0.010 |
| 3-4 | 11-06 → 11-19 | combine the one axis with a receipt ≥ +0.010, one factor at a time (expect one axis, not two) |
| 5 | 11-20 → 11-26 | confirm winner against its own parent; freeze final file + fallback |
| 6 | 11-27 → 12-03 | re-validate the format of **both**; one blind final submission |

## Proposed better axes (mechanism · confounder · falsifier) — not built

| Axis | Mechanism | Confounder / mimic | Falsifier |
|---|---|---|---|
| **FRONTIER** | mass into blocks with *no* catalogued fault but high structural-edge density: the away arm's mechanism, upgraded from a control to a first-class axis | edge density also marks contacts and basin fill | fails to beat `cat10away`'s receipt by ≥ 0.005 |
| **DEDUPE** | drop the most redundant dots by exact marginal removal (no refill) | de-clusters ≈ spacing effect; `SPACING` at matched removal is the control | fails to beat `MASS −10 %` by ≥ 0.005 |
| **FLOOR** | ~2,000 dots on the flat-slope tercile at catalogue-proportional spacing | flat ground has no DEM edge — a bet against R0's own model | score < R0 − 0.005 |
| **REPEAT-CALIBRATION** | resubmit exact R0 once to convert CLAIM → RECEIPT and bound slot noise | costs 1 of ~18 slots, zero expected gain | receipt differs from 0.2778 by > 0.005 |
| **PLACEMENT-FIX** | rebuild `cat10` with added dots restricted to `h19_5`-dilated support (≤ 2 px off-ridge) instead of potential-field maxima | confounds allocation with a second placement change | does not beat `cat10` by ≥ 0.005 at equal moved count |

Future in-axis values (not new axes): `cat10` at 3 km and 10 km blocks (scale
response), `cat10` with the *inverse* prior (frontier-weighted), and a
`cat10`-on-`h19_5`-support variant — each only after one CONCENTRATION receipt
exists, because a null at 5 km does not settle the scale question.
