# SLOT PLAN — one page, session GEMSDOE89 (2026-10-23, SPACING)

Deadline **2026-12-03** (UNVERIFIED — confirm on the competition page; ≈6 weeks,
41 days). Quota: 3 scored submissions per rolling week per entity + one final
blind submission. Slots used/available: **not supplied** — fill in before
spending any. `TOP_PUBLIC`: **not supplied**.

## The three slots, in order

| # | File | Predicted live change | Submit only if | What the result changes |
|---|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-spacing-strike3-20261023-59029fa7.tif` | **+0.004** MODEL (band −0.013…+0.024) | gates green (verified) | Primary. ≥ +0.010 → strike geometry is a live lever; run slot 2 to separate orientation from redundancy. Inside ±0.010 → close SPACING. ≤ −0.010 → the parent's close pairs are deliberate strands; never re-space again. |
| **2** | `releases/h33-h33-2-b2-spacing-pd3-20261023-6b481dc1.tif` | **+0.003** MODEL (band −0.016…+0.025) | slot 1 scored and informative (any \|Δ\| ≥ 0.010) | Isotropic control. Both ≥ +0.010 → build DEDUPE (no-refill redundancy removal). strike3 ≥ +0.010, pd3 null → orientation is the ingredient; pivot to TRACKB-style traces. |
| **3** | `releases/h33-h33-2-b2-spacing-lat3-t1p5-20261023-0dbab41e.tif` | **−0.001** MODEL (band −0.008…+0.012) | a structure-aware arm lands ≥ +0.010 and a structure-free benchmark is wanted | Null control. ≥ +0.010 here while the others are null would mean parent placement is worthless — contradicting the lineage; expected outcome is no evidence, which retires lattice work. |

Do **not** submit strike3 and pd3 in the same week without a slot to spare:
they share the same 9.2k-dot violator set and answer overlapping questions.
The RELIEF files (`…-relief-r10/r15/r15s…`) remain on disk from the prior
session and still await human submission decisions; do not resubmit twins.

## Weeks to the deadline

| week | dates | plan |
|---|---|---|
| 1 | 10-23 → 10-29 | slot 1 (strike3); slot 2 (pd3) only if slot 1 is informative; otherwise hold |
| 2 | 10-30 → 11-05 | whichever conditional arm week 1 justifies; lattice only as a benchmark; build DEDUPE if both spacing arms win |
| 3-4 | 11-06 → 11-19 | combine the two best axes seen so far, one factor at a time (default: DEDUPE + best placement) |
| 5 | 11-20 → 11-26 | confirm the winner against its own parent; freeze the final file and a fallback |
| 6 | 11-27 → 12-03 | re-validate the format of **both** final files, then submit one blind |

## Proposed better axes (mechanism · confounder · falsifier) — not built this session

**1. DEDUPE (highest expected value; control now exists).** Remove the most
*redundant* dots (exact ΔDTI of removal via `gemsdoe.metric.marginal_gain_remove`)
instead of the lowest-ranked, bottom 15-25 %, **no refill**.
*Mechanism:* the max operator lets a neighbour claim the kernel; the duplicate
still costs 0.2 of denominator. *Confounder:* de-duplication de-clusters — but
`pd3` now provides the matched-removal spacing control, so a DEDUPE win over
`pd3` isolates redundancy from geometry. *Falsifier:* if DEDUPE does not beat
`MASS −10 %` by ≥ 0.005, the redundancy cost model is wrong for this metric.

**2. FLOOR (medium).** The flat-slope tercile holds 33 % of the footprint, 20 %
of catalogue pixels but only 177 R0 dots (0.1 / 1000 px). Add ~2,000 dots there
at catalogue-density proportional spacing. *Confounder:* flat ground has no DEM
edge, so it bets on magnetics/gravity the parent declined. *Falsifier:* a
2,000-dot FLOOR arm below R0 − 0.005 closes the coverage-gap hypothesis.

**3. STRIKE-EXTEND (new; cheap if strike3 wins).** From the top-ranked R0 dots,
extend strike-parallel chains by 1-2 dots into unoccupied ≥ 3 px-clearance
pixels along the local strike field. *Mechanism:* line-like truth lowers the
pay bar along strike. *Confounder:* drainage/hogback fabric mimics fault strike.
*Falsifier:* null result while strike3 itself was null closes the strike family.

**4. DOSE (sanity, any week).** One deliberate byte-identical resubmit per
month measures the score's run-to-run noise and sets the real bar under which a
change is "no evidence" (the brief's 0.01 rule is currently uncalibrated).
