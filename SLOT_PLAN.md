# SLOT PLAN — one page, session GEMSDOE89 (2026-10-23)

Deadline **2026-12-03** (UNVERIFIED — confirm on the competition page; ≈6 weeks,
41 days). Quota: 3 scored submissions per rolling week per entity + one final
blind submission. Slots used/available: **not supplied** — fill in before
spending any.

## The three slots, in order

| # | File | Predicted live change | Submit only if | What the result changes |
|---|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif` | **+0.003** MODEL (band −0.012…+0.018) | gates green (already verified) | The primary evidence. ≥ +0.010 → class allocation transfers; run slot 2. Inside ±0.010 → the axis is dead, skip to the DEDUPE axis below. < −0.010 → placement quality dominates allocation; close both RELIEF and CONCENTRATION. |
| **2** | `releases/h33-h33-2-b2-relief-r15-20261023-6aa774ce.tif` | **+0.004** MODEL (band −0.017…+0.027) | slot 1 scored, and its delta ≥ +0.010 | Dose-response. r15 delta ≈ 1.5 × r10 → the effect is the class move. Super-linear loss → 15 % strips too much from the source class. |
| **3** | *hold*, or `…-relief-r15s-…-5f0ae851.tif` (alternate) | **+0.001** MODEL (band −0.007…+0.011) | slot 1 scored and inside ±0.010 | If r10 is null and the human still wants the axis closed from a second definition; otherwise keep the slot for the DEDUPE axis below once it exists. |

Do **not** submit r15 and r15s in the same week: they answer the same question
at 1.5× dose and a different class definition, so a third file should probe
something new.

## Weeks to the deadline

| week | dates | plan |
|---|---|---|
| 1 | 10-23 → 10-29 | slot 1 (r10) + slot 2 (r15) if r10 ≥ +0.010; otherwise slot 1 only and hold |
| 2 | 10-30 → 11-05 | whichever of r15 / r15s the week-1 result justifies; build the DEDUPE axis |
| 3-4 | 11-06 → 11-19 | combine the two best axes seen so far (default expectation: DEDUPE + best placement), one factor at a time |
| 5 | 11-20 → 11-26 | confirm the winner against its own parent; freeze the final file and a fallback |
| 6 | 11-27 → 12-03 | re-validate the format of **both** final files, then submit one blind |

## Proposed better axes (mechanism · confounder · falsifier) — not built this session

These come from the algebra, which is the strongest thing this session produced:
`DTI = T / (0.2T + 0.2(S−M) + 0.8|G|)`, so one dot of credit *k* changes DTI by
`(k − 0.2·DTI)/(D + 0.2)` — at 0.2778 a dot must sit within ≈280 m of a truth
pixel to pay, and **a dot whose credit is already claimed by a neighbour is pure
mass**.

**1. DEDUPE (highest expected value; untested).** Remove the *most redundant*
dots rather than the *lowest-ranked* ones: rank by unique marginal credit
(compute the exact ΔDTI of removing each dot with `gemsdoe.metric.marginal_gain_remove`),
drop the bottom 15-25 %, do **not** refill.
*Mechanism:* the max operator means a neighbour's kernel already claims the
credit; the duplicate still costs 0.2 of denominator. This is strictly better
targeted than the upstream `MASS −10 %`, which dropped the traversal tail by
rank (predicted −0.003) and therefore mostly removed dots that were still
earning. *Confounder:* de-duplication also de-clusters, so a win cannot be
separated from a spacing effect — the SPACING arm at matched removal is the
control. *Falsifier:* if removing genuinely redundant dots does not beat
`MASS −10 %` by ≥ 0.005, the redundancy measure is not the right cost model for
this metric.

**2. FLOOR (medium).** Cover the flat-slope tercile, which holds 33 % of the
footprint and 20 % of the catalogue (12,150 px) but only **177 of R0's 37,654
dots** (0.1 per 1000 px). Add ~2,000 dots there at catalogued-fault-density
proportional spacing rather than at random.
*Mechanism:* the flat third is almost entirely unsurveyed by the parent; at the
measured catalogue density a structured placement would clear the 0.0556 bar.
*Confounder:* flat ground has no DEM edge response, so any dot there is a bet on
a non-DEM signal (magnetics/gravity) that R0's own model already declined to
make. *Falsifier:* if a 2,000-dot FLOOR arm scores below R0 − 0.005, flat-ground
fault truth is not recoverable from the supplied bands and the coverage gap is
correctly left empty.

**3. DOSE (cheap sanity check, any week).** Re-submit a byte-identical twin of a
scored file once per month. Upstream history shows ≥8 slots went to exact
repeats *by accident*; a *deliberate* repeat is the only way to measure the
score's own run-to-run noise, which sets the true bar for "under 0.01 is no
evidence".
