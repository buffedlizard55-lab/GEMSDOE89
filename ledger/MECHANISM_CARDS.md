# Mechanism cards — RELIEF axis, session GEMSDOE89

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
