# Mechanism cards — SPACING axis, session GEMSDOE89 (2026-10-23)

Parent for every card: **R0 = h33-h33-2-b2** (GEMSDOE32 lineage; 37,654 unit-mass
dots, none within 2 px of the catalogue; live 0.2778 = **CLAIM**, no receipt in
this repo). All three variants hold the count at exactly 37,654 and change only
the *geometry* of the point set: no mass, ranking, relief-class or catalogue-
collar change. Every moved dot hops to a free pixel inside a bounded window and
every NEW pixel is ≥ 3 px from the catalogue. The parent's 1,611 inherited
2.236 px collar dots are untouched unless they move (IRREGULARITIES item 2).

Written for a structural geologist. Nothing here is a prediction expressed as a
score; the predictions are MODEL projections with stated assumptions.

---

## The measurement the whole axis rests on

R0's nearest-neighbour (NN) geometry, measured directly from the parent raster:

| statistic | value |
|---|---|
| minimum NN | 2.828 px (the √8 diagonal; the parent's suppression radius) |
| dots at exactly NN = 2.828 px | 11,415 (30.3 %) |
| median / mean NN | 3.00 / 3.74 px |
| dots with NN < 3.162 px (the √10 ring) | 50.5 % |
| density-equivalent lattice spacing | ≈ 11.7 px (1.17 km) |

A seeded greedy split at r_min = 3.0 px yields **28,394 mutually separated
anchors and 9,260 violator dots** — one in four R0 dots sits inside one kernel
radius of another R0 dot. The triangular kernel (R = 3 px) of two dots 2.828 px
apart overlaps almost completely, so under the metric's **max operator** the
second dot can add little truth credit *T* while still adding its full mass to
*S*. That is the redundancy the first two arms attack; the third arm is the
structure-agnostic control.

**The algebra scale.** With the catalogue as a counterfactual truth, the parent
has T = 378.0, S = 37,654, M = 277.9, G = 60,988, denominator D = 56,341, so
c = 1/(D + 0.2) = **1.78 × 10⁻⁵ DTI per kernel unit per dot**. A live change of
0.01 across ~9,000 moved dots therefore needs an average per-dot credit swing of
≈ 0.063 kernel units — a sixth of a full kernel. The live denominator uses the
undisclosed new-fault count, so the true scale can differ; all bands below use
this scale as an order-of-magnitude anchor, not a measurement.

| arm | dots moved | mean / max hop | NN < 3 px share | 1 km block CV | surrogate ΔDTI (catalogue) |
|---|---|---|---|---|---|
| parent | — | — | 0.303 | 1.870 | — |
| `pd3` | 9,215 (24.5 %) | 5.57 / 6 px | 0.001 | 1.670 | −0.00102 |
| `strike3` | 9,092 (24.1 %) | 4.12 / 5 px | 0.015 | 1.799 | −0.00110 |
| `lat3-t1p5` | 4,642 (12.3 %) | 3.03 / 4 px | 0.260 | 1.851 | −0.00273 |

The surrogate is computed on catalogue pixels that are **masked in live
scoring**; it is a coverage diagnostic, never a score.

---

## Card 1 — `strike3` (primary, slot 1)

**Hypothesis.** R0's sub-kernel close pairs are redundant only when they sit
across strike. Re-spacing the violators **along the local structural strike**
keeps every dot on its own lineament while converting overlapping kernel
coverage into distinct, strike-parallel coverage, which is how a mapped fault
trace actually occupies pixels.

**Mechanism.** Faults are line-like truth, and line-like truth lowers the
break-even bar because a dot earns credit from every truth pixel in reach, not
just one. The parent's close pairs are already strongly strike-organised
(mean |cos(pair, strike)| = 0.77), consistent with a ridge-following builder.
The arm takes each greedy violator and, relative to the anchor it crowds,
moves it to the best free pixel within 5 px whose anchor–dot direction is
within 60° of the local strike (detrended-elevation gradient rotated 90°,
Gaussian-smoothed at 1 px). The controlled local statistic moves decisively:
mover–anchor alignment **0.764 → 0.944**. Minimum separation never drops below
the parent's own 2.828 px floor, and 98.5 % of sub-3 px pairs are resolved.

**The non-fault process that could mimic it.** The strike field is
geomorphic, not geologic: drainage-parallel hogbacks, bedrock joint sets,
lithologic contacts and terrace risers all produce gradient-perpendicular
fabric at 300–600 m. Aligning dots to that fabric strengthens non-fault
lineament coverage just as efficiently as fault coverage. The brief also
records GeoDAWN Area 2 lineament uncertainty of about one kernel radius
(400 m flight-line spacing), which bounds how much a ≤ 500 m hop can gain —
and how much it can lose.

**Predicted sign and size (MODEL).** Central **+0.004**, band **−0.013 …
+0.024** (9,092 dots × c × per-dot swing −0.10 … +0.15 kernel units; the
0.944 alignment and shorter hops trim the pessimistic tail relative to `pd3`).
A change inside ±0.010 is no evidence.

**Falsifier.** A live change inside ±0.010 closes the whole SPACING axis.
A change ≤ −0.010 says the parent's close pairs are deliberately placed
strands whose geometry must not be touched. A change ≥ +0.010 that is *not*
matched by `pd3` identifies strike orientation as the active ingredient and
redirects effort toward trace-building (TRACKB) rather than de-clustering.

---

## Card 2 — `pd3` (slot 2, conditional)

**Hypothesis.** The redundancy is isotropic: a crowded dot's cheapest
improvement is simply the farthest free pixel in its 6 px window, with no
directional assumption. This is the purest test of the max-kernel redundancy
story and the pre-registered de-clustering control for the proposed DEDUPE
axis (SLOT_PLAN.md).

**Mechanism.** Each of the 9,260 greedy violators moves only if a free pixel
strictly improves its NN distance; 9,215 do, 45 cannot and keep their parent
pixel. The result is nearly a blue-noise point set: sub-3 px pairs fall from
30.3 % to 0.1 %, median NN rises 3.0 → 4.12 px, and the 1 km block-density CV
drops 1.870 → 1.670 (the largest uniformity gain of the three), while the
global strike alignment is essentially unchanged (0.7666 → 0.7634), as an
isotropic operation predicts.

**The non-fault process that could mimic it.** De-clustering assumes two close
dots cover the same target. Where truth is a narrow, curving fault strand, two
dots 2.8 px apart along strike instead cover *different* truth pixels;
spreading them isotropically can pull one off the strand into barren ground.
The arm cannot tell redundancy from strand geometry — that is exactly what the
contrast with `strike3` measures.

**Predicted sign and size (MODEL).** Central **+0.003**, band **−0.016 …
+0.025** (9,215 dots × c × per-dot swing −0.10 … +0.15; the longest hops and
no directional protection give the widest downside).

**Falsifier.** If `strike3` is positive but `pd3` lands inside ±0.010 or below,
orientation, not redundancy, is the lever — close DEDUPE and keep only
strike-aware construction. If *both* reach ≥ +0.010, redundancy is real and
the no-refill DEDUPE arm becomes the highest-value next build. If `pd3`
reaches ≤ −0.010, the parent's suppression radius is already optimal.

---

## Card 3 — `lat3-t1p5` (hold / control)

**Hypothesis.** A regular square lattice is the null geometry: if structure-
free spacing performs as well as the two structure-aware arms, the parent's
ridge-following placement contributes nothing at this scale and coverage
uniformity is the whole game.

**Mechanism.** Phase (2,1) of a 3 px lattice is chosen once, deterministically,
to minimise total snap distance over R0. The 31,791 dots already within 1.5 px
of a node keep their exact pixel (the intervention is deliberately partial, to
stay inside the 1–50 % change rule); the other 4,642 move to the nearest free
valid node within 4 px, refusing any node closer than 2.828 px to an occupied
pixel. Block CV barely moves (1.870 → 1.851): a partial lattice at one quarter
of the density-equivalent spacing cannot homogenise the parent's ridge
clusters, and 13.1 % of the dots it moves carried catalogue kernel credit
before (mean 0.024) — the most of any arm — because its mover selection is
geometry-only.

**The non-fault process that could mimic it.** Cultural fabric: Nevada
section-grid roads, drains and property lines are themselves near-regular
orthogonal patterns, so lattice energy has no fault-specific meaning. The
historical control is GEMSDOE13's full-lattice file (CLAIM 0.0904): wholesale
replacement destroyed the structural signal. This arm is the bounded,
matched-count counterpart, not a repetition of that experiment.

**Predicted sign and size (MODEL).** Central **−0.001**, band **−0.008 …
+0.012** (4,642 dots, shorter hops, no placement signal of its own; the
negative centre reflects the catalogue-credit its geometry-only mover
selection surrenders).

**Falsifier.** A result ≥ +0.010 here while both structure-aware arms are null
would be the surprising outcome: it would mean parent placement is worthless
and uniform coverage wins, contradicting the entire lineage. A result inside
±0.010 is the expected no-evidence outcome and retires the lattice construction
without further doses.

---

## What these cards deliberately do not claim

* The hide-and-recover proxy can only see the removal half of every move:
  every new pixel is ≥ 3 px from the catalogue and therefore carries zero
  catalogue kernel. Its recall falls (0.0384 → 0.0326 / 0.0323 / 0.0232) by
  construction; the numbers are reported in `registry/report_only_status.json`
  and were not used to set a predicted sign (IRREGULARITIES item 8).
* The global NN-based strike-alignment statistic falls for `strike3`
  (0.7666 → 0.6728) even though the controlled mover–anchor statistic rises to
  0.944, because nearest-neighbour identities re-wire after a move. The local
  quantity is what the arm controls; both are reported, neither is a score.
