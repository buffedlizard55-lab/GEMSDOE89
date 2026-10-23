# Mechanism cards — session GEMSDOE89

Two axes were built against the same parent: RELIEF (built 2026-10-23, first
session) and **SPACING** (built 2026-10-23, this session). The RELIEF cards are
kept unchanged below for the record; the SPACING cards follow them.

Parent for every card: **R0 = h33-h33-2-b2** (GEMSDOE32 lineage; 37,654 unit-mass
dots, none within 2 px of the catalogue; live 0.2778 = **CLAIM**, no receipt in
this repo). All three variants hold the dot count at exactly 37,654 and change
only *which relief class the mass sits in*.

Written for a structural geologist. Scores quoted are live DTI values; nothing
here is a prediction expressed as a score.

---

## The measurement the whole axis rests on

Equal-area terciles of `det_elev` (band 12 of the pinned feature stack; cuts at
−142.9 m and +38.8 m), measured over the 5,164,312-px relief domain:

| class | name | area (px) | catalogue px | known-fault density /1000 px | R0 dots | R0 density /1000 px | R0 share ÷ catalogue share |
|---|---|---|---|---|---|---|---|
| 0 | basin | 1,721,438 | 18,499 | 10.75 | 7,692 | 4.47 | 0.67 |
| 1 | piedmont | 1,721,437 | 24,711 | **14.35** | 15,742 | 9.14 | 1.03 |
| 2 | range front | 1,721,437 | 17,684 | 10.27 | 14,204 | 8.25 | **1.30** |

The catalogue is roughly 1.4× denser in the piedmont than in the range front,
yet R0 carries 1.30× *more* mass per unit catalogue density in the range front
than proportional allocation would give, and only 0.67× in the basin.

**The threshold that decides everything.** With the derived algebra
DTI = T / (0.2T + 0.2(S−M) + 0.8|G|), removing or adding one dot of kernel
credit *k* changes DTI in proportion to (k − 0.2·DTI). At the parent's claimed
0.2778 that break-even credit is **0.0556** — a dot must lie within ≈2.8 px
(280 m) of a truth pixel to pay for itself. A dot placed *uniformly at random*
inside a class earns the class-average credit:

| class | P(pixel within 3 px of a catalogue px) | E[k] random placement | pays (>0.0556)? |
|---|---|---|---|
| basin | 0.069 | 0.036 | no |
| piedmont | 0.097 | **0.050** | no — but closest |
| range front | 0.070 | 0.036 | no |
| flat-slope tercile | 0.049 | 0.025 | no |
| mid-slope tercile | 0.105 | 0.054 | no — but closest |

Two conclusions follow, and they bound every prediction below. (i) No relief
class clears the bar on average, so a relief move can only win if the *added*
dots land on structure inside the class rather than at random. (ii) The
within-class placement rule therefore carries as much weight as the between-class
move, which is why every variant writes its added dots only onto ground at least
as structured as a typical parent dot (mean |∇det_elev| at parent dots = 13.6;
the write-in threshold is the 50th percentile, 12.2).

---

## Card 1 — `r10` (primary, slot 1)

**Hypothesis.** R0 over-weights the range-front tercile by 30 % relative to the
known-fault density in that class, and under-weights the piedmont. Moving 10 %
of the mass (3,765 dots) out of the range-front class and onto structured ground
inside the piedmont class raises credit per unit mass.

**Mechanism.** In the northern Great Basin, basin-margin faults place Quaternary
scarps in alluvial-fan deposits, where they are preserved, exposed, and mapped;
range-interior lineaments are more often bedrock fabric — fractures, lithologic
contacts, and topographic grain that a DEM-edge-following model detects but that
does not host a mapped fault trace. R0 was built from such a model, so its
range-front dots should carry a higher non-fault fraction per unit mass than its
piedmont dots. Rebalancing toward measured mappable-fault density should raise
the credit earned per dot.

**The non-fault process that could mimic it.** DEM edge density *peaks* at range
fronts and in bedrock, so R0's range over-weighting may reflect terrain
roughness rather than a fault-distribution error. If the added piedmont dots
land on fan-head channels, bar-and-swale, or the fan/bedrock contact — all of
which produce strong edges and are not faults — the move adds false-positive
mass in a *different* class and the gain disappears. A second mimic: catalogue
density is a *mapping-effort* prior (where geologists had exposure and reason to
map), not a fault-density measurement.

**Predicted sign and size (MODEL).** Central **+0.003**, band **−0.012 …
+0.018**. The band is honest, not decorative: it spans u_r (unique credit of a
removed dot) from 0 to 0.25 and the added dot's credit k_a from 0.10 to 0.35.
Break-even k_a ranges 0.033 (fully redundant removals) to 0.24 (removals still
carrying a quarter of a kernel unit). Everything under |Δ| = 0.01 counts as no
evidence.

**Falsifier.** A live change inside ±0.010 in either direction closes the axis:
class-level allocation does not transfer, and the mass should stay where the
parent put it. A live change below −0.010 is stronger evidence still — it says
that *structure-following placement inside the parent's own class* is worth more
than *any* class-level reallocation, which also retires the CONCENTRATION
family. The one result that would open the axis is a change ≥ +0.010, and it
must exceed the `r15` result's dose-consistency test (roughly 1.5× the r10
delta) to be believed as mechanism rather than noise.

---

## Card 2 — `r15` (slot 2, conditional)

**Hypothesis.** Same as Card 1 at 1.5× the dose: 5,648 dots (15 %) moved
range-front → piedmont. This is the second point on the dose-response line; on
its own it is not an independent hypothesis.

**Mechanism.** Identical to Card 1.

**The non-fault process that could mimic it.** Identical, plus one that is
specific to the higher dose: at 15 % the transfer starts to strip the range
front below the density the parent's own model chose there, so a *nonlinear*
loss of unique credit appears that has nothing to do with relief. A linear
dose-response (r15 ≈ 1.5 × r10) is the evidence that the effect is the class
move; a super-linear loss is evidence for the opposite.

**Predicted sign and size (MODEL).** Central **+0.004**, band **−0.017 …
+0.027**. Linearity with r10 is the thing to check, not the absolute number.

**Falsifier.** If r10 lands at or above +0.010 but r15 does *not* exceed it, the
r10 gain was not the class move (it would be a placement effect that saturates).
If both land inside ±0.010, the axis is closed and slot 3 should go elsewhere.

---

## Card 3 — `r15s` (alternate)

**Hypothesis.** The geomorphic piedmont is a *slope* transition, not an elevation
band. Redefining the classes by `det_elev_slope` (band 19; cuts 1.8 and 8.1)
and moving the same 15 % from the high-slope class into the mid-slope class
tests whether the definition or the direction carries the effect.

**Mechanism.** The mid-slope tercile has the highest known-fault density of any
partition measured here (15.34 / 1000 px, vs 14.35 for the elevation piedmont),
consistent with fault scarps being best expressed where fans are steepest.
The high-slope class it is drawn from (12.98 / 1000 px) is much less depleted
than the elevation range-front class (10.27), so the density contrast driving
this move is only 1.18× instead of 1.40×.

**The non-fault process that could mimic it.** Slope is the strongest single
predictor of DEM edge magnitude, so the slope classes and the model's own
edge-response are close to collinear — this variant is the most likely of the
three to be a placement change wearing a relief label. It also has the smallest
mean displacement (49 px ≈ 4.9 km) because slope classes are interleaved at
hundreds of metres, so much of the "move" is local re-shuffling.

**Predicted sign and size (MODEL).** Central **+0.001**, band **−0.007 …
+0.011** — scaled down from r15 by the 1.18/1.40 contrast ratio. This is the
weakest of the three and is an alternate, not a sequential submission.

**Falsifier.** A large change from this variant while r10/r15 do nothing would
indicate the effect is slope-driven edge placement, not relief-class allocation,
and would redirect the session toward the SPACING/placement family rather than
toward more class work.

---

## What these cards deliberately do not claim

* The catalogue proxy (hide-and-recover) **cannot see this axis**. Every added
  dot is ≥3.0 px from every catalogue pixel by construction, so the proxy can
  only register the removal half of the move. Its measured deltas
  (0.0384 → 0.0356 / 0.0348 / 0.0341 recall) are an artefact of that blindness,
  not evidence against the variants, and they are reported as PROXY only.
* The catalogue-surrogate DTI (0.0067 → 0.0062 / 0.0060 / 0.0059) is a
  counterfactual measured on pixels that are *masked* in live scoring. It is not
  a score and it was not used to set a predicted sign.

---

# SPACING axis (built 2026-10-23)

Same parent R0, same 37,654 dots, same catalogue exclusions. Nothing moves
between relief classes, between 1 km blocks, or on/off structure: **only the
local spacing of the dots changes.** Every new position is ≥ 3.00 px from the
catalogue (measured minimum 3.00 px) and no dot pair in any arm is tighter than
the parent's own 2.828 px disk.

## The measurement the axis rests on

| property | R0 (measured) | Poisson field at the same density |
|---|---|---|
| dots | 37,654 (0.729 % of 5,167,373 footprint px) | same |
| minimum nearest-neighbour distance | **2.828 px** (= √8, the (2,2) diagonal) | — |
| dots at exactly 2.828 px | 11,415 (**30.3 %**) | ~0 |
| median nearest-neighbour distance | **3.0 px** | ≈ 5.5 px |
| dots closer than 4 px | 79.5 % | ≈ 33 % |
| 1 km block density CV | 1.87 | ≈ 1.0 |

R0 is therefore a *saturated hard disk on ribbons*: inside a ribbon the dots are
packed at the suppression radius, between ribbons the map is empty. The
structure fraction is not a rendering artefact — it is the strongest single
statement one can make about this parent.

**Why spacing can pay, from the algebra.** DTI = T / (0.2T + 0.2(S−M) + 0.8|G|)
and T = Σ_truth max_i p_i·k(i,g). The max means T depends on the **union** of the
kernel disks. Two dots 2.83 px apart each cost 1.0 of mass S but their 3 px
disks overlap by a wide lens, so part of that mass buys no new coverage.
Relocating the redundant member of such a pair into a nearby gap holds S fixed
and cannot shrink the union — so dT ≥ 0 is the geometric prediction, and
dDTI = (1 − 0.2·DTI)·DTI·(dT/T) with dDTI/dT > 0.

**Quantified, label-free.** Union coverage = Σ_pixels max(0, 1 − d/3) with d the
distance to the nearest dot. This is exactly T under spatially uniform truth, so
its relative change is the assumption-light proxy for dT/T. Parent value
303,053 (dimensionless kernel-area units). At the claimed DTI 0.2778, a +1 %
coverage change is worth **+0.0026 DTI**.

## Card 1 — `hd3p0` (mild dose, slot 2)

| | |
|---|---|
| **file** | `releases/h33-h33-2-b2-spacing-hd3p0-20261023-08f80fd3.tif` |
| **change** | 5,413 of 37,654 dots relocated (14.4 %), hard-disk radius 3.0 px, mean displacement 1.38 px, median 1.0 px, p95 3.16 px |
| **predicted** | **+0.0058** MODEL (band −0.0029 … +0.0145) |

**Hypothesis.** Part of the parent's local clustering is metric waste, not
geology: at the 3 px kernel radius a neighbour 2.8 px away already claims most
of the same credit. Separating such pairs by ~1.4 px converts redundant mass
into new area of kernel coverage without adding a dot.

**Mechanism.** Greedy hard-disk independent set at 3.0 px (dots ordered by
ascending nearest-neighbour distance, seeded tie-break), then each rejected dot
moves to the admissible free pixel in its 7×7 window that maximises distance to
the nearest surviving dot (≥ 3.0 px from kept and from already-placed dots,
≥ 3.0 px from the catalogue, inside footprint). 123 had no admissible
destination and stayed put; 18 placements were reverted by the repair pass
because they landed next to a stayer. Coverage +2.20 %, block CV 1.87 → 1.85,
median nearest-neighbour distance 3.0 → 3.16 px.

**Non-fault process that could mimic it.** The parent's clustering may be
*real*: strands of a fault zone are genuinely 100–300 m apart, and the 3 px
kernel is wide enough that two true strands inside one kernel produce exactly
the pair pattern we call "redundant". If so, the moved dot leaves a real fault
pixel uncovered and the gain is zero or negative. A second mimic: 400 m flight
line spacing means lineament positions carry ~150–200 m uncertainty
(https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7), so a
1.4 px (140 m) relocation is inside the survey noise and should be nearly
score-neutral *unless* the kernel-coverage argument is doing real work.

**Predicted sign and size.** Positive but small, +0.006 (MODEL). At 140 m the
displacement is within the documented positional noise, so this arm is the
safe one: it should be hard to lose from, and it is the reference against which
the along-strike arm is compared at matched dose.

**Falsifier.** A live change below −0.010 (beyond the band) kills the
coverage-area argument for the mild dose; combined with a null hd4p0 it closes
the axis.

## Card 2 — `hd4p0` (strong dose, slot 1)

| | |
|---|---|
| **file** | `releases/h33-h33-2-b2-spacing-hd4p0-20261023-0cf9025b.tif` |
| **change** | 13,749 dots relocated (36.5 %), hard-disk radius 4.0 px, mean displacement 2.78 px, median 2.83 px, p95 5.66 px |
| **predicted** | **+0.0245** MODEL (band −0.0123 … +0.0613) |

**Hypothesis.** If coverage area converts to T at all, a 4× larger dose must
show it. This is the only arm whose predicted effect (+0.025) clears the
brief's 0.01 evidence bar with room to spare, which is why it takes slot 1.

**Mechanism.** Same selection rule and same placement rule, one radius step
coarser: median nearest-neighbour distance 3.0 → 4.12 px, coverage +9.34 %,
block CV 1.87 → 1.73 (the coarsening also flattens the km-scale density a
little, which is reported but **not** the mechanism — see the confounder below).
1,256 dots had no admissible destination and stayed; 905 placements were
reverted by the repair pass.

**Non-fault process that could mimic it.** Three, in order of danger.
(i) *Geological saturation*: if truth really is packed along strands at ~2.8 px,
the arm strips coverage exactly where the faults are; the predicted band's
negative side is that scenario.
(ii) *Positional drift*: a 2.8 px (280 m) mean displacement exceeds the
150–200 m survey uncertainty, so systematic mistuning of the field's registration
would show up here and nowhere else — a uniform shift in one direction would
cost T without any spacing effect.
(iii) *Km-scale confounding*: moving 36.5 % of the dots also lowers block CV
from 1.87 to 1.73. If the result is negative, that is still informative for
CONCENTRATION; if positive, the win cannot be cleanly attributed to sub-km
spacing rather than to a small de-clustering.

**Predicted sign and size.** Positive, +0.025 (MODEL) — the largest predicted
effect of any file this repo has built, and the most likely to be wrong in
either direction because it carries every confounder at once.

**Falsifier.** A live change below −0.012 (the band's floor) at 36.5 % of the
field is a hard stop: it would say that at fixed mass this metric does not
reward kernel-coverage area at all, and the parent's saturation is geological.
A change inside ±0.010 leaves the axis untested rather than closed, and the
next slot should go to a non-spacing question.

## Card 3 — `hd3p0-along` (geometry contrast, slot 3)

| | |
|---|---|
| **file** | `releases/h33-h33-2-b2-spacing-hd3p0-along-20261023-f3d99d91.tif` |
| **change** | 5,159 dots relocated (13.7 %), hard-disk radius 3.0 px, destinations restricted to the local strike corridor, mean displacement 3.32 px |
| **predicted** | **+0.0084** MODEL (band −0.0042 … +0.0211) |

**Hypothesis.** Same selection as card 1, different destination geometry. Faults
are lines: two dots 2.83 px apart are already both inside one kernel of the
*across-strike* gap between them, so the cheapest place to spend a redundant dot
is further along the trend, where the kernel runs out sooner. The strike is
estimated from the parent's own dot density (structure tensor, σ = 2 px / 4 px;
median coherence at the moved dots 0.48), so the arm uses no external dataset.

**Mechanism.** Identical independent set at 3.0 px, destinations restricted to
integer offsets within ±2 px perpendicular of the local strike, 1–3 px along it,
scored like card 1 (admissible separation first, then farthest along strike).
Coverage +3.22 % — slightly more than the isotropic arm at the same dose, which
is what the trend argument predicts.

**Non-fault process that could mimic it.** The strike field is derived from the
dots themselves, so it inherits the parent's errors: where the parent is wrong
about a lineament, the arm confidently extends the wrong line. Land-use and
topographic grain (drainage, ridge crests) also produce linear density patterns
that the structure tensor cannot distinguish from faults — a "trend-following"
win could be nothing more than following the parent's own artefacts.

**Predicted sign and size.** Positive, +0.008 (MODEL) — the same order as the
isotropic arm. The **difference** between this and card 1 at matched dose
(5,413 vs 5,159 dots moved) is the actual measurement; the absolute score is
secondary.

**Falsifier.** If along ≤ isotropic at matched dose, local trend carries no
information beyond the dot positions themselves, and the TRACKB axis (Phase 2,
strike-consistent traces) loses its prior. If along > isotropic by ≥ 0.01, the
next axis should be TRACKB, and the strike field is worth building into the
production pipeline.

## What these cards deliberately do not claim

- No card is a score. Predicted changes are MODEL outputs from a geometric
  coverage integral, with the uniform-truth assumption stated where it is used.
- The REPORT-ONLY catalogue proxy **cannot** speak to this axis: every new
  position is ≥ 3 px from the catalogue, where the kernel weight is exactly 0,
  so the proxy can only register the removal half of the move (it reads
  0.0384 → 0.0349 / 0.0289 / 0.0355 for the three arms). Its sign is an artefact
  and was not used to set any prediction — see IRREGULARITIES item 7.
- The leakage canary on the only two features this axis looks at (the parent dot
  indicator, AUC 0.499; distance to the nearest dot, AUC 0.193) shows no
  catalogue leakage, and no external data of any kind was used.
