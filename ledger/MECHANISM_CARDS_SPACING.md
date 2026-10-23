# Mechanism cards — SPACING axis, GEMSDOE89 continuation (2026-10-23)

Evidence labels: **MODEL** is a projection, **PROXY** is a local holdout, and
**RECEIPT** is a submission-page receipt. No file here has a receipt or a live
score. R0's 0.2778 remains **CLAIM**. Metric/format reference supplied in the
brief: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
(not fetched by this agent).

## Shared control and mechanism

R0 already suppresses dots at about the 300 m kernel radius: its minimum
nearest-neighbour distance is 2.828 px, but 11,415 / 37,654 dots (30.3%) are
still <3 px from a neighbour. Under the metric's per-truth-pixel `max`, one
neighbour can claim the same credit while every dot still contributes mass.
The experiment asks whether relocating the most crowded 10% into legal local
gaps earns enough *new-fault* credit to offset any lost explained mass.

All arms use exactly the same 3,765 removed dots and 3,765 Poisson gap anchors.
Every replacement stays in its source dot's **5 km × 5 km block**, so those
block counts are identical to R0 by paired construction. This is a deliberate
control against turning SPACING into CONCENTRATION. New dots are >=3 px from
the catalogue and >=2.8 px from every other dot. Count remains 37,654.

| measurement | lattice10 | poisson10 | strike10 |
|---|---:|---:|---:|
| parent dots changed | 3,765 (9.9989%) | 3,765 (9.9989%) | 3,765 (9.9989%) |
| mean / max displacement | 4.42 / 12.65 px | 4.93 / 9.85 px | 4.67 / 9.49 px |
| mean shift from matched anchor | 1.66 px | 0 px | 1.26 px |
| dots with NN <3 px after | 5,618 | 5,672 | 5,790 |
| median NN before → after | 3.00 → 3.162 px | 3.00 → 3.162 px | 3.00 → 3.162 px |
| 1 km block-density CV before → after | 1.870 → 1.819 | 1.870 → 1.809 | 1.870 → 1.814 |

The 1 km CV is descriptive only. The exact concentration control is the paired
5 km block assignment, not a CV target. The fixed removal SHA-256 is
`ef579d518721…`; the fixed anchor SHA-256 is `3c3dbeeb9d84…` (hashes of int32
coordinate arrays, not raster hashes).

## Card 1 — `poisson10` (primary SPACING arm)

**File.** `h33-h33-2-b2-spacing-poisson10-20261023-986e9365`.

**Hypothesis.** Space-filling, non-lattice placement reduces kernel overlap
without imposing a preferred geological orientation.

**Mechanism.** For each crowded source dot, 16 seeded legal candidates are
drawn in a local window; the candidate with the largest distance to surviving
dots is retained, subject to >=2.8 px separation from every placed dot. This is
best-candidate Poisson-disk placement. It should preserve broad structure while
covering gaps whose credit was previously missed.

**Non-fault mimic.** Alluvial distributaries, discontinuous fracture/joint
swarms, landslide scarps and lithologic boundaries can all create apparent
lineament gaps. Filling those gaps can spread dots onto non-fault terrain; no
new-fault truth is used to distinguish these processes.

**Predicted live change.** **+0.002 MODEL**, with a subjective plausible range
of **−0.008 to +0.012**. This is not a confidence interval. The central effect
is below the brief's 0.01 no-evidence threshold, so a null live result is the
most likely individual outcome.

**Falsifier.** A change ≤−0.010 versus R0 says the moved dots were earning more
placement credit than the new gaps recover. A result inside ±0.010 provides no
evidence. If this arm does not exceed R0 by >=0.010 despite halving the crowded
dot count, generic Poisson de-overlap is not a useful live-score mechanism.

## Card 2 — `strike10` (line-continuity arm)

**File.** `h33-h33-2-b2-spacing-strike10-20261023-442188a4`.

**Hypothesis.** If local R0 geometry approximates fault strike, moving gap
anchors preferentially along that direction should earn more credit on
line-like truth than orientation-neutral Poisson placement.

**Mechanism.** PCA of up to 24 surviving R0 dots within 20 px defines a local
axis. From the *same* Poisson anchor used above, the strike arm minimises
`perpendicular² + (0.25 × along)²`: along-axis movement is four times cheaper
than cross-axis movement. The result is local, not a regional fault trace.
Median absolute anchor-normal shift is 0.25 px (p90 0.47 px); mean absolute
along-axis shift is 1.18 px. Three of 3,765 orientations use the documented
fallback because fewer than two surviving neighbours were available.

**Non-fault mimic.** Bedding/lithologic contacts, fluvial terraces, shorelines,
roads and pipelines can be continuous without being faults. PCA can also
reinforce a smooth artefact already present in R0. This arm does not claim that
the fitted axis is independently mapped fault strike.

**Predicted live change.** **+0.003 MODEL** (subjective range **−0.010 to
+0.016**), modestly above Poisson only if line continuity contributes credit.
It is a projection, never a score.

**Falsifier.** If `strike10 − poisson10` is inside ±0.010, there is no evidence
for an orientation effect. If strike is >=0.010 worse than Poisson, local PCA
orientation is actively harmful; close this mechanism rather than increasing
its dose. A shared positive result would support generic de-overlap instead.

## Card 3 — `lattice10` (regular-geometry control)

**File.** `h33-h33-2-b2-spacing-lattice10-20261023-9d7dc126`.

**Hypothesis.** A fixed 3 px lattice can reduce local kernel overlap as much as
stochastic spacing; if so, elaborate geological orientation is unnecessary.

**Mechanism.** Each replacement is the nearest legal point on the fixed global
3 px lattice to the same Poisson gap anchor, with seeded source ordering and
identical exclusions. Of the 3,765 replacements, 404 anchors already lie on the
lattice and therefore remain matched exactly; this is not treated as a defect
or subjected to any uniqueness gate.

**Non-fault mimic.** Cadastral boundaries, roads, survey/flight-line artefacts
and raster processing can be regular. There is no geological claim that faults
prefer a lattice; this is a metric-geometry control.

**Predicted live change.** **+0.001 MODEL** (subjective range **−0.008 to
+0.010**). A larger effect would be surprising and should first trigger a
format/receipt check, not an immediate dose escalation.

**Falsifier.** If Poisson or strike improves by >=0.010 but lattice does not,
anchor-specific placement matters more than regular de-overlap. If all three
move together, the experiment cannot separate the geometries; if all are null,
SPACING is closed at this dose.

## REPORT-ONLY instruments (not gates, not live-score estimates)

- Catalogue hide-and-recover, seed 20261023, 30% withheld: **n = 18,296**.
  Every SPACING arm has recall **0.0346524**, Wilson 95% interval
  **0.0293488–0.0399559**; R0 is 0.0384237. The identical values are expected:
  the arms share removals, and every added dot is >=3 px from the catalogue,
  so it cannot recover a withheld catalogue pixel inside the kernel.
- Catalogue-as-truth surrogate DTI is also identical across arms and is
  **0.0005965 below R0**. This counterfactual is blind to the placement half of
  the edit and did not set any predicted sign. It is **PROXY**, not a score.
- Leakage canary: distance-to-parent AUC 0.46367 and distance-to-surviving-dot
  AUC 0.46429; neither crosses 0.90. **PASS, REPORT ONLY.** The mandated
  catalogue-distance exclusion is not treated as a predictive feature.
- SGMC control: **NOT RUN** because no SGMC raster is pinned in this session's
  manifest. It is report-only and was not replaced with an invented control.
