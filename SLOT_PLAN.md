# SLOT PLAN — session GEMSDOE89 (updated 2026-10-23, SNAP branch)

Deadline **2026-12-03** (UNVERIFIED — confirm on the competition page; ≈6 weeks).
Quota: 3 scored submissions per rolling week per entity + one final blind
submission. Slots used/available: **not supplied** — fill in before spending any.
Parent: **R0 `h33-h33-2-b2`, rebuilt byte-exactly this session** (`tools/rebuild_r0.py`,
sha256 `c55bafc4…`), 37,654 dots, live 0.2778 = CLAIM (no receipt in this repo).

## The three slots, in order

| # | File | Predicted live change | Submit only if | What the result changes |
|---|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif` | **+0.003** MODEL (−0.012…+0.018) | gates green (verified) | The allocation fork. ≥ +0.010 → class allocation transfers → slot 3 = r15. Inside ±0.010 → allocation dead, close RELIEF *and* the CONCENTRATION family. < −0.010 → placement dominates allocation. |
| **2** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` | **+0.028** MODEL (−0.028…+0.084) | gates green (verified); human knowingly accepts the widest band in the repo | The placement fork, independent of slot 1. ≥ +0.010 → snap mechanism real → slot 3 = 1p4px-g0p00 window dose. Inside ±0.010 → gateless snap dead; the *gated* upstream arm `2p0px-g0p01` (GEMSDOE84, +0.018…+0.044 MODEL) still tests selection-vs-dose. ≤ −0.010 → retire SNAP and the EM-crest story. |
| **3** | conditional: `…-relief-r15-…-6aa774ce.tif` if slot 1 ≥ **0.2878**; else `…-snap1p4px-g0p00-…-e1474851.tif` if slot 2 ≥ **0.2878**; else **hold** | +0.004 / +0.028 MODEL | the named parent-arm scored ≥ +0.010 | Dose-response for whichever axis woke up; holding keeps one slot free for evidence received later in the week. |

Same-week rule: never submit r15 and r15s together (same question, 1.5× dose);
never submit two gate-0 snap windows together (window dose saturates — 80.8 % →
83.1 % moved from 1.0 → 2.0 px — so one gate-0 receipt answers the family).

## Weeks to the deadline

| week | dates | plan |
|---|---|---|
| 1 | 10-23 → 10-29 | slots 1 + 2 (keep 1 spare for a late-breaking receipt) |
| 2 | 10-30 → 11-05 | slot 3 conditional as above; record every receipt in the ledger |
| 3-4 | 11-06 → 11-19 | combine the two axes with receipts ≥ +0.010, one factor at a time (default expectation: one axis only — most results will be < 0.01) |
| 5 | 11-20 → 11-26 | confirm the winner against its own parent; freeze final file + fallback |
| 6 | 11-27 → 12-03 | re-validate format of **both** final files; one blind final submission |

## Proposed better axes (mechanism · confounder · falsifier) — not built this session

**1. DEDUPE (highest expected value).** Remove the *most redundant* dots
(exact ΔDTI via `gemsdoe.metric.marginal_gain_remove`), drop bottom 15-25 %,
no refill. *Mechanism:* the max operator means a neighbour already claims the
credit; duplicates cost 0.2 of denominator each. *Confounder:* de-clustering
≈ spacing effect — the SPACING arm at matched removal is its control.
*Falsifier:* if it does not beat MASS −10 % by ≥ 0.005, redundancy is the
wrong cost model here.

**2. FLOOR (medium).** ~2,000 dots on the flat-slope tercile (33 % of footprint,
0.1 R0 dots/1000 px) at catalogue-density-proportional spacing.
*Confounder:* no DEM edge response on flat ground — a bet on non-DEM signal R0's
own model declined. *Falsifier:* score < R0 − 0.005 ⇒ the coverage gap is
correctly empty.

**3. DOSE (cheap).** Re-submit one byte-identical twin per month: upstream
history wasted ≥8 slots on accidental repeats; a deliberate repeat is the only
measurement of the score's own run-to-run noise, which sets the real bar for
“under 0.01 is no evidence”.

**Future SNAP values (inside the existing axis, not new axes):** response-surface
variants — DEM-scarp gradient vs EM-only vs fused — only after one gate-0 or
gated receipt has shown the mechanism any sign of life.
