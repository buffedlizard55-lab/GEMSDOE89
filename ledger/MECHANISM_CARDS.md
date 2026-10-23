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

---

# Mechanism cards — SNAP axis (gateless), session GEMSDOE89 (2026-10-23, branch arena/7efbb7cc)

Parent for every card: **R0 = h33-h33-2-b2**, rebuilt byte-exactly this session
(`tools/rebuild_r0.py` reproduces sha256 `c55bafc4…` from the mask; 37,654 dots).
All three variants hold count, mass and the parent's exclusion rules fixed; only
*which pixel each dot sits on* may change, and only toward a strictly stronger
fused TMI/gravity edge response inside the window. Targets are ≥ 3.0 px off the
catalogue; the parent's inherited 2.236-px collar dots may stay or move out
(they never move closer) — collar count 1,611 → 938 / 666 / 575
(IRREGULARITIES item 2, single-variable control).

**Recipe note (why these are comparable across sessions).** The response is
replicated exactly from the upstream recorded SNAP recipe: bands 3 `tmi_hg` +
18 `iso_grav_anom_hg` (identities pinned via the manifest's
`band_identity_source` → GEMSDOE88 `registry/feature_receipt.json`), median
fill → gaussian σ = 1 px → `robust_unit` (1.0 = footprint 99.5th pct) →
pixel-wise max. Upstream built (1.42 px, gate 0.02), (2.0 px, 0.02),
(2.0 px, 0.01); these cards are **gate 0.00** at windows 1.0 / 1.42 / 2.0 —
so a receipt-vs-receipt comparison against the upstream arms isolates the
*gate* and nothing else. Gate 0.00 = the brief's literal “move each dot
≤ 2 px to the strongest response in its window” (any strictly stronger
pixel qualifies).

**What actually moved (measured):**

| value | window | dots moved (% of 37,654) | mean displacement | mean response gain | nn median before → after | CV 1 km before → after |
|---|---|---|---|---|---|---|
| 1p0px-g0p00 | 1.0 (4-nbr) | 30,434 (80.83 %) | 1.000 px | 0.0054 | 3.0 → 3.0 | 1.883 → 1.889 |
| 1p4px-g0p00 | 1.42 (8-nbr) | 31,233 (82.95 %) | 1.354 px | 0.0075 | 3.0 → 3.0 | 1.883 → 1.894 |
| 2p0px-g0p00 | 2.0 (12-nbr) | 31,287 (83.09 %) | 1.864 px | 0.0103 | 3.0 → 3.0 | 1.883 → 1.908 |

Window-dose **saturates**: 1.0 → 2.0 px adds only 853 moves. At gate 0 the
lever is the *gate*, not the window — which is what the cross-session
comparison against the gated arms prices.

**Shared prediction arithmetic (MODEL, not a score).** Pure position change ⇒
ΔDTI ≈ ΔT / D with D = 18,734.44, T = 5,073.29 from the recorded live-anchor
inversion (upstream `evidence/h33_validation.json`, live pair 0.2600 → 0.2708).
Scenario on moved dots: −0.05 … +0.15 *net* fraction close (or open) one full
pixel to their nearest truth pixel, kernel gain ⅓ each; central +0.05. The
negative side is priced because gateless moves are dominated by micro-gains on
smooth noise; the upper side inherits the coupling the upstream cards assumed
(they used +0.10 … +0.25 with no negative side). Everything under |Δ| = 0.01
is no evidence.

**Shared report-only counter-indicators (never gates, never called scores).**
Hide-and-recover PROXY recall falls 0.0384 → 0.0254 / 0.0181 / 0.0152
(n = 18,296 withheld, Wilson 95 % parent [0.033, 0.044] vs 2p0 variant
[0.012, 0.019]); catalogue-surrogate DTI falls 0.0067 → 0.0049 / 0.0033 /
0.0027. Reading: gateless snap trades *catalogue-adjacent* placement for
*crest-aligned* placement. Catalogue pixels are masked pixel-exactly in live
scoring, but new-fault truth may lie within 300 m of known traces (organizer
answer, brief §2), so catalogue adjacency partially proxies live truth. This
is the strongest reason the bands below carry a symmetric negative side. The
leakage canary PASSES (max single-feature AUC 0.665 vs threshold 0.90); the
SGMC control is not in the manifest (deferred, report-only).

---

## Card S1 — `1p0px-g0p00` (window dose, low end)

**Hypothesis.** R0's dots are the output of a geometric BFS Poisson-disk walk
over the H19-5 lineament field; traversal order, not physics, picks the
surviving pixel, so many dots sit exactly 1 px off the geophysical edge that
nominated their lineament. A minimum decisive snap (4-neighbour disc) recovers
that off-by-one without letting any dot wander.

**Mechanism.** Each dot moves to the strictly strongest fused tmi_hg /
iso_grav_anom_hg pixel at distance ≤ 1 px (mean response gain 0.0054 robust
units), targets ≥ 3 px off the catalogue, one dot per pixel, deterministic.
Under the triangular kernel a 1 px correction on the dot nearest a truth pixel
recovers up to ⅓ of the credit available from that pixel.

**Non-fault mimic.** Fan-head channels, bar-and-swale and lithologic contacts
produce 1-px-scale horizontal-gradient maxima too; at 80.8 % moved, most moves
are micro-noise on a smooth surface — the arm can be a 30-thousand-dot random
walk dressed as a correction. Tie-line seams in the aeromagnetic survey add
structured false crests.

**Predicted sign and size (MODEL).** Central **+0.027**, band **−0.027 …
+0.081**. The band is the honest consequence of pricing the mimic: at gate 0
the coupling between EM-crest alignment and new-fault truth is the whole bet.

**Falsifier.** Live ≤ −0.010 falsifies the snap mechanism outright (crests R0
was pulled onto are non-fault contacts). Inside ±0.010 = no evidence; the
window-dose question then collapses to the cross-session *gate* comparison.
≥ +0.010 opens the family: compare against the gated arms' receipts
(1.42 px-g0p02 moved 6.4 %, 2.0 px-g0p01 moved 26.5 %) to see whether the
gate adds selection or just removes dose.

## Card S2 — `1p4px-g0p00` (gate ablation at 1.42 px)

**Hypothesis.** Same as S1 with the 8-neighbour disc: the diagonal pixel is
often the true edge (a lineament at 45° to the grid), so window 1.42 should
beat window 1.0 *if* the correction mechanism is real. Compared with upstream
`1p4px-g0p02` (same window, same response, gate 0.02, 6.4 % moved) this arm
isolates the gate exactly.

**Mechanism.** Identical rule, offsets ≤ 1.42 px (adds the four diagonals);
31,233 moves, mean displacement 1.354 px, mean gain 0.0075.

**Non-fault mimic.** Identical to S1; the diagonals also double the chance of
landing on a fan/bedrock contact that runs obliquely through the window.

**Predicted sign and size (MODEL).** Central **+0.028**, band **−0.028 …
+0.083**.

**Falsifier.** Receipt ≈ the 1.42-g0p02 receipt (±0.010) ⇒ the gate does
nothing at this window and upstream's arms can be read as pure dose. Receipt
≥ 0.010 *below* the gated arm ⇒ the gate is filtering harmful noise, i.e.
selection matters more than dose — run windows at a *nonzero* gate next, not
more gate 0. Below −0.010 ⇒ S1's falsifier fires for the whole family.

## Card S3 — `2p0px-g0p00` (gate ablation at the physical window)

**Hypothesis.** GeoDAWN Area 2 was flown at ~400 m line spacing
(https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7), so
lineament positions are uncertain by about the 300 m kernel radius — the
physical correction scale is 2 px, not 1. This is the full-disc gateless arm
and the direct ablation of upstream `2p0px-g0p01` (26.5 % moved) and
`2p0px-g0p02` (11 %).

**Mechanism.** Identical rule, Euclidean disc ≤ 2.0 px (12 offsets); 31,287
moves (83.09 %), mean displacement 1.864 px, mean gain 0.0103 — the largest
response harvest of the three. Moved targets never come closer than 3.00 px
to the catalogue (measured); spacing statistics barely move (nn median 3.0 →
3.0, CV 1 km 1.883 → 1.908): this axis changes *position*, not *arrangement*.

**Non-fault mimic.** The wider disc reaches further off the mapped lineament
onto parallel unrelated gradients — buried paleo-topographic steps, Lahontan
shoreline breaks, pluton margins — and it is the arm with the most cumulative
micro-noise (83 % of all dots move). The falling catalogue PROXY (0.0384 →
0.0152) is this arm's own warning label: crest alignment and fault-proximity
placement are being traded against each other.

**Predicted sign and size (MODEL).** Central **+0.028**, band **−0.028 …
+0.084**.

**Falsifier.** ≥ +0.010 with a *tighter-band* gated receipt also positive ⇒
snap mechanism confirmed; then choose dose by receipt, not by principle.
≥ +0.010 while the gated arms' receipts are null ⇒ upstream over-gated (the
gate, not the snap, was destroying the gain). ≤ −0.010 ⇒ retire SNAP and the
EM-crest story with it: R0's lineament placement beats EM-crest placement and
the response surface should be rebuilt from DEM/lineament structure instead.
