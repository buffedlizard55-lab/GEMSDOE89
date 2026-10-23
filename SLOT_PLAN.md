# SLOT PLAN — one page, session GEMSDOE89 (updated 2026-10-23, SPACING build)

Deadline **2026-12-03** (UNVERIFIED — confirm on the competition page; ≈6 weeks,
41 days). Quota: 3 scored submissions per rolling week per entity + one final
blind submission. Slots used/available: **not supplied** — fill in before
spending any. Parent for every file: **R0 = h33-h33-2-b2**, live 0.2778 =
**CLAIM** (no receipt in this repo).

Two axes are built and unsubmitted: **RELIEF** (r10 / r15 / r15s, first session)
and **SPACING** (hd3p0 / hd4p0 / hd3p0-along, this session). The plan below puts
SPACING first because it is the axis with no prior `(axis, value)` pair anywhere
in the recovered ledger, and because one of its arms has the largest predicted
effect this repo has produced.

> **Before using this plan:** `main` now also carries SPACING arms (`poisson`,
> `lattice`, `alongstrike`) from a parallel session on the same parent — see
> `IRREGULARITIES.md` item 9. The files below are valid and gate-passing but
> duplicate those experiments at different doses. If both lineages are live,
> the only additive question left in this set is the dose contrast
> (`hd3p0` 14.4 % vs `hd4p0` 36.5 %) against main's 20.3 % poisson arm.

## The three slots, in order

| # | File | Predicted live change | Submit only if | What the result changes |
|---|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-spacing-hd4p0-20261023-0cf9025b.tif` | **+0.025** MODEL (band −0.012 … +0.061) | gates green (already verified) | The decisive arm: 36.5 % of the dots relocated. **≥ +0.010** → kernel-coverage area converts to score; run slot 2 for dose scaling and start combining. **Inside ±0.010** → the axis is untested, not closed; spend slot 2 elsewhere (RELIEF r10). **≤ −0.012** → at fixed mass this metric does not reward coverage area; close SPACING *and* CONCENTRATION and move to a mass/placement question. |
| **2** | `releases/h33-h33-2-b2-spacing-hd3p0-20261023-08f80fd3.tif` | **+0.006** MODEL (band −0.003 … +0.015) | slot 1 scored and ≥ +0.010 | Dose-response at 1/2.5 of slot 1's dose: delta ≈ 0.4 × slot 1 → the effect is the spacing, not a fluke of the big perturbation; delta ≫ linear → the strong arm is over-moving dots (positional drift). |
| **3** | `releases/h33-h33-2-b2-spacing-hd3p0-along-20261023-f3d99d91.tif` | **+0.008** MODEL (band −0.004 … +0.021) | slot 1 scored | Geometry contrast at matched dose (5,413 vs 5,159 dots moved). along **>** isotropic by ≥ 0.01 → faults are trending and TRACKB becomes the next axis; along **≤** isotropic → the local strike field adds nothing. |

Do **not** spend two slots in the same week on hd3p0 and hd3p0-along: they
answer overlapping questions at the same dose. If only one slot is available,
take `hd4p0`.

## Weeks to the deadline

| week | dates | plan |
|---|---|---|
| 1 | 10-23 → 10-29 | slot 1 (hd4p0). Read the sign before anything else. |
| 2 | 10-30 → 11-05 | slot 2: hd3p0 if slot 1 ≥ +0.010; hd3p0-along if slot 1 is inside ±0.010; RELIEF r10 if slot 1 ≤ −0.012. |
| 3-4 | 11-06 → 11-19 | combine the two best axes seen so far, one factor at a time (default expectation: best spacing dose + RELIEF r10). |
| 5 | 11-20 → 11-26 | confirm the winner against its own parent; freeze the final file and a fallback. |
| 6 | 11-27 → 12-03 | re-validate the format of **both** final files, then submit one blind. |

## Proposed better axes (mechanism · confounder · falsifier) — not built this session

The hard-disk measurement (min nearest-neighbour distance 2.828 px, 30.3 % of the
dots at exactly that distance, median 3.0 px against 5.5 px for a Poisson field
at the same density) sharpens all three proposals from the first session:

**1. DEDUPE / MASS-AT-DISK (highest expected value; still untested).** Remove —
do not relocate — the redundant member of every pair below 2.828 px *along
strike only*, i.e. the dots whose removal leaves the union of kernel disks
unchanged but drops S. Algebra: with T unchanged and ΔS = −1, ΔM = −m, the
denominator falls by 0.2(1 − m) per dot, and DTI = T/D rises. *Mechanism:* mass
whose credit a neighbour already claims is pure cost in the S−M term.
*Confounder:* removal also de-clusters, so a win cannot be separated from the
spacing effect measured this session — use the SPACING arm at matched removal as
the control. *Falsifier:* if removing genuinely redundant dots does not beat
`MASS −10 %` by ≥ 0.005, the redundancy measure is the wrong cost model.

**2. FLOOR (medium).** The flat-slope tercile holds 33 % of the footprint and
20 % of the catalogue (12,150 px) but only 177 of R0's 37,654 dots. Add ~2,000
dots there at catalogued-fault-density proportional spacing. *Mechanism:* the
third of the map the parent never surveyed is empty by construction, not by
evidence. *Confounder:* flat ground has no DEM edge response, so any dot there
is a bet on a signal the parent's model declined to use. *Falsifier:* if a
2,000-dot FLOOR arm scores below R0 − 0.005, flat-ground truth is not
recoverable from the supplied bands.

**3. TRACKB (Phase 2, conditional on slot 3).** Strike-consistent traces ≥ 1 km
built from the top-ranked dots, as GeoJSON + raster with one evidence paragraph
per trace. Only worth building if `hd3p0-along` beats its isotropic twin at
matched dose; otherwise the strike field has no demonstrated information.

**4. DOSE (cheap sanity check, any week).** Re-submit a byte-identical twin of a
scored file once per month. Upstream history shows ≥ 8 slots went to exact
repeats by accident; a *deliberate* repeat is the only way to measure the score's
own run-to-run noise, which sets the real bar for "under 0.01 is no evidence".
