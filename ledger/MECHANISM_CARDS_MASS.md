# Mechanism cards — MASS axis, session GEMSDOE89 (2026-10-23)

Parent for every card: **R0 = h33-h33-2-b2** (37,654 unit-mass dots, zero on the
catalogue, minimum catalogue distance 2.236 px). Live 0.2778 = **CLAIM**: this
repo holds no receipt for it.

Every arm is a **drop-only** edit of the parent: no dot is added, moved or
re-valued, so the arms differ from R0 in exactly one respect — which dots are
absent. Counts are exact (3,765 / 3,765 / 7,531) and the twins are
mask-identical.

## The rule these arms are built on

The DTI numerator is a **max** over prediction pixels, so a dot whose 3 px
kernel is already covered by a neighbour adds almost nothing to `T` while all of
its mass still enters `S` and `M`. Removing one unit dot of kernel credit `k`
changes the score by

```
dDTI = -(k - 0.2*DTI) / D        D = 0.2T + 0.2(S-M) + 0.8|G|
```

so at 0.2778 every removed dot with `k < 0.0556` is a **gain** and every dot
with `k > 0.0556` is a **loss**. The whole MASS family is that threshold
applied to a chosen subset. `D` is not observable locally; the one measured
mass-removal step in the lineage (2,545 collar dots removed for +0.0070) implies
`D ≈ 1.5–2.0 × 10^4`. At that `D` the *ceiling* of an arm — every dropped dot at
`k = 0` — is

| arm | dropped | ceiling |
|---|---:|---:|
| m10uniq / m10rand | 3,765 | **+0.0105** |
| m20uniq | 7,531 | **+0.021** |

That ceiling is the reason this axis is worth a slot and also the reason to be
sceptical: a 10 % drop cannot beat +0.0105 even under the most favourable
assumption about credit.

## The ranking, and the audit that forced it

The brief asks for "the parent's own ranking (rebuild it from the recorded
recipe if it is not stored)". **There is no recorded recipe**, and the field the
lineage thins from — `h19-5`, the raster the brief calls a 121k-px *continuous*
field — is **binary** (`{0, 1}`, 121,131 set cells, verified this session). It
carries no ordering at all. The fleet ledger shows what happened when previous
sessions needed a ranking anyway: `GEMSDOE88` records its own as
`0.6*clip(d_catalogue_px/50,0,1) + 0.4*uniform`, and 89.4 % of its dropped dots
lay within 10 px of the catalogue — a collar move wearing a MASS label.

This session derives the ranking from the metric instead:

```
u_i = credit dot i would claim if truth were uniform over the footprint,
      counting only pixels where i is the strictly nearest dot.
```

`u_i` is the expected value of the exact per-dot term the DTI algebra
differentiates, i.e. unique (non-duplicated) kernel credit. Measured on R0:
`sum(u) = 289,633.7`, mean `u = 7.692`, median nearest-neighbour distance
3.0 px. It is a **proxy for k, never an estimate of it** — and the next section
shows that the proxy is weak, which is stated up front rather than buried.

### Calibration: the ranking does NOT explain the one measured mass step

Solo-d2.8 (40,199 dots, live 0.2708) → R0 (37,654, live 0.2778) removed 2,545
dots for **+0.0070**. Recomputing `u` on the solo set, the removed dots carry
**8.036** against a set mean of **7.667** — they are *above* average, i.e. the
ranking is blind to whatever made that step work (they are the collar ring,
which `u` cannot see). If credit were proportional to `u`, the model predicts
**−0.0175** for that step; the measurement is +0.0070. The model is wrong by
0.0245 on the only calibration point that exists.

**Consequence.** Predictions below are given as wide bands and are not to be
read as scores. The arms are designed so that the *pattern across the three*
is informative even when each individual delta is inside the noise.

---

## Card 1 — `m10uniq` (primary) — `h33-h33-2-b2-MASSm10uniq-20261023-beed130f`

**Hypothesis.** The 10 % of R0's dots with the smallest unique kernel credit are
mass, not evidence: removing them lowers `S` and `M` while leaving `T` almost
untouched, so the score rises.

**Mechanism.** Along a detected lineament R0's dots sit at the 2.8–3.0 px
suppression radius, so mid-line dots duplicate each other's kernel under the max
operator; between lineaments the same density is spread over ground where no
trace exists. In both cases the dot's unique credit is small. The ranked drop is
deliberately **not** a collar move: only 1.54 % of dropped dots lie within 3 px
of the catalogue (base rate 4.28 %), and their mean catalogue distance is
30.6 px vs the parent's 29.0 px. The ranking selects *distant, clustered* mass
and **keeps the collar ring** that earns the only catalogue-adjacent credit R0
has.

**The non-fault process that could mimic a win.** Clustered dots are also what a
genuine fault *zone* looks like — several sub-parallel strands, relay ramps and
step-overs inside a few hundred metres. If truth is a zone rather than a single
trace, the "duplicated" dots are each covering a different strand, their `u` is
an artefact of the flat-prior assumption, and removing them removes recall. The
count-matched random arm is the control for exactly this: if `m10rand` scores
the same as `m10uniq`, the ranking is not doing any work and only the count
matters.

**Confounder.** De-clustering. A win here cannot be separated from a spacing
effect (the 2.5 km block-density CV falls 1.24 → 1.20). That is why the effect
must be read against `m10rand`, not against R0 alone.

**Predicted sign and size.** Central **+0.002**, band **−0.010 … +0.010**,
ceiling +0.0105. Measured inputs: unique credit lost 7.46 % for 10.0 % of mass
(25 % less credit per unit mass than the random control); dropped-dot mean
`u` 5.74 vs 7.91 kept.

**Falsifier.** A live delta ≥ **+0.005** says mass outside the collar is waste
and licenses the 20 % arm. **|Δ| < 0.005** says the count is not a lever at this
dose and closes the MASS family for the remaining slots. A delta ≤ **−0.005**
says the far field is credit-bearing: then no future arm may remove mass except
inside the catalogue collar, and the FLOOR/DEDUPE proposals in `SLOT_PLAN.md`
must be dropped.

---

## Card 2 — `m10rand` (control) — `h33-h33-2-b2-MASSm10rand-20261023-7a4c49b6`

**Hypothesis (null).** The ranking carries no information: R0's dots are
exchangeable with respect to the metric, so dropping 10 % of them at random
captures the whole count effect.

**Mechanism.** None — that is the point. This arm is the count-matched null for
Card 1: same 3,765 drops, same footprint, same legality, only the selection
differs. It also samples the collar proportionally (4.54 % of drops within
3 px vs the 4.28 % base rate), so it removes slightly more of the ring that the
measured collar step says is net-negative.

**The non-fault process that could mimic a win.** Every process: this arm cannot
attribute anything. Its only job is to price the count.

**Predicted sign and size.** Central **−0.002**, band **−0.016 … +0.010**. The
lower bound is the proportional-credit model (all dots earn alike → −0.016); the
upper bound is the "far field is free" model (+0.0105 ceiling, slightly reduced
by the collar draw).

**Falsifier / use.** If `m10rand` ≈ `m10uniq` (within ±0.005), the unique-credit
ranking is worthless and every future mass/prune arm must be justified
geometrically, not by `u`. If `m10rand` beats `m10uniq`, the ranking is
*anti*-predictive and should be inverted or abandoned.

---

## Card 3 — `m20uniq` (dose) — `h33-h33-2-b2-MASSm20uniq-20261023-87ec6213`

**Hypothesis.** Same as Card 1 at 2× dose: 7,531 dots (20 %) by the same
ranking.

**Mechanism.** Identical. The dose is what separates "the count is a lever" from
"the first decile happened to be empty ground": at 20 % the 2.5 km block-density
CV falls 1.24 → 1.18 and the 5 km CV 0.90 → 0.86, i.e. the file becomes visibly
smoother than the parent, and unique credit lost reaches 15.9 % for 20 % of
mass (the ranking's selectivity degrades from 25 % to 20 % — deeper in the
stack it finds less obvious duplication).

**The non-fault process that could mimic it.** At 20 % the arm starts to strip
the *tail* of the parent's own lineament network — low-density areas where a
single dot per lineament is all the recall there is. That is the "super-linear
loss" failure mode, and it is why this arm is conditional on Card 1.

**Predicted sign and size.** Central **+0.004**, band **−0.020 … +0.021**,
ceiling +0.021.

**Falsifier.** If `m20uniq − m10uniq` is strongly negative while `m10uniq` is
positive, the count optimum lies between 33.9k and 37.6k and the next test is a
5 % rung, not a 30 % one. If both are positive and roughly additive, the count
optimum is below 30k and the next session should push the dose.

---

## What these cards deliberately do not claim

* The catalogue hide-and-recover **PROXY** is reported for each arm (0.0370 /
  0.0340 / 0.0346 vs the parent's 0.0384, random null 0.0000). It cannot see the
  dropped dots' true credit and it is **not** used to set any sign here; see
  `IRREGULARITIES.md` item 7.
* The catalogue-surrogate DTI (a counterfactual measured on pixels that are
  masked in live scoring) moves by −0.0002 / −0.0006 / −0.0004. That is an
  artefact of where the catalogue happens to sit, not evidence.
* No claim is made that `u` estimates `k`. The calibration section says the
  opposite, with the number.
