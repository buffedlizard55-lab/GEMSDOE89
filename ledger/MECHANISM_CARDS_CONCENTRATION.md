# CONCENTRATION mechanism cards — GEMSDOE89, 2026-10-23

Parent: **R0 `h33-h33-2-b2`**, 37,654 unit dots, rebuilt byte-identically before
construction (`c55bafc4…` zeros; `baeae3219…` NaN). Its live **0.2778 is CLAIM**,
not a receipt. Every projection below is **MODEL**, not a score. A live public
change with `|Δ| < 0.01` is **no evidence**.

## Shared structural-geology hypothesis and controlled recipe

Faults interact through step-overs, relays, intersections, and terminations, so
newly mapped geometry may cluster in km-scale neighbourhoods with many known
fault pixels. Organizer clarification permits new-fault truth within 300 m of
known traces, while known pixels themselves are masked pixel-exactly:
https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516
and https://community.drivendata.org/t/where-do-you-draw-the-line/11536 .

The prior is **known-catalogue pixels / footprint pixels** in **2 km blocks**
(20 × 20 pixels), reported per 1,000 footprint pixels. Source blocks are the
bottom half among blocks containing R0 dots; zero ties are retained (4,507
blocks, 24,571 available R0 dots, prior = 0). Target blocks are the top third
among blocks with unused H19-5 candidates (2,072 blocks, 18,778 candidates;
cut ≥ 5, block-mean prior 40.28). Incomplete edge blocks and blocks with ≤50%
footprint are frozen. This is a mapping prior, **not test-truth information**.

Each arm removes the least harmful source dots and adds H19-5 pixels in target
blocks. Destination selection is lazy **sequential exact greedy**: after every
accepted dot, its triangular-kernel credit updates the next dot's marginal.
The computation includes `T`, `S`, `M`, `|G|`, and the denominator in the DTI
algebra (metric/page: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ ),
and is unit-tested against brute-force one-dot metric edits. This avoids the
independent-ranking failure in which added dots became redundant with each
other. All variants hold count at 37,654, stay on H19-5, emit zero catalogue
mass, and place every **added** dot at `d_cat >= 3 px`; inherited parent collar
dots do not increase (1,611 → 1,609).

## Measured parent differences and report-only diagnostics

| arm | moved (sym. diff) | added mean prior | H19 ΔDTI MODEL | 2 km CV before → after | 5 km CV before → after | nn <3 px before → after |
|---|---:|---:|---:|---:|---:|---:|
| C1 / m3765 | 3,765 = 10.00% (20.00%) | 38.58 | **−0.002674** | 1.3676 → 1.4528 | 0.8991 → 0.9252 | 11,415 → 17,014 |
| C2 / m5648 | 5,648 = 15.00% (30.00%) | 37.64 | **−0.010344** | 1.3676 → 1.5326 | 0.8991 → 0.9546 | 11,415 → 19,453 |
| C3 / m7531 | 7,531 = 20.00% (40.00%) | 37.14 | **−0.022643** | 1.3676 → 1.6250 | 0.8991 → 0.9917 | 11,415 → 21,929 |

Mean removed→nearest-added displacement is 42.08 / 40.56 / 39.35 px for
C1/C2/C3. The negative H19 counter-indicator and growing crowding are why C2
and C3 are **held**, despite the prior transfer. The catalogue hide-and-recover
**PROXY** withholds 18,296 positives: parent recall 0.038424 (95% CI
[0.032850, 0.043997]); every variant 0.038369 ([0.032799, 0.043939]). This is
not evidence of live equivalence and was never a gate. The 20-feature leakage
canary passes (maximum single-feature strength 0.568803 < 0.90). SGMC was not
run because its raster pin is UNVERIFIED; it remains report-only.

The live MODEL adds the measured H19 counter-indicator to an uncalibrated
block-prior sensitivity of −0.050 / +0.025 / +0.100 effective credit per moved
dot, scaled by the previously recorded anchor `D = 18,734.44`. The low/central/
high values are a **sensitivity band, not a confidence interval**.

## Card C1 — `2km-b50-t33-m3765` (`da3a4886`)

**Hypothesis.** A restrained 10% transfer from zero-catalogue 2 km blocks to
high-prior blocks can gain enough new-fault kernel credit to offset the small
H19 coverage cost.

**Mechanism.** Move 3,765 dots while retaining the same H19 physical signal and
count. Exact sequential additions fill the best remaining H19 coverage in the
target blocks; mean new H19 credit is 0.902 per addition versus 1.000 unique
H19 credit lost per removal. This is the least saturated arm and the only one
with a positive central projection.

**Non-fault process / confounder.** Catalogue density partly measures mapping
effort and exposure, not fault-system prospectivity. H19 also contains volcanic
or intrusive contacts, fan-head channels, shoreline breaks, and erosional
ridges; concentrating on those near well-mapped faults can add non-fault mass.
The same catalogue defines both the prior and the PROXY, so the PROXY cannot
independently validate the mechanism.

**Predicted live change (MODEL).** Central **+0.0024**, sensitivity
**−0.0127 … +0.0174**. A no-evidence result is entirely plausible.

**Falsifier.** A live change `≤ −0.010` falsifies the claim that this block
prior pays for its coverage cost; retire all three arms. Inside ±0.010 is no
evidence: do not escalate dose. A gain `≥ +0.010` supports testing C2 once.

## Card C2 — `2km-b50-t33-m5648` (`51ba9656`)

**Hypothesis.** If C1 demonstrates a real prior effect, a 1.5× transfer could
increase it before target saturation dominates.

**Mechanism.** Adds the next 1,883 nested source/destination edits to C1. New
H19 credit per added dot falls to 0.758 and the H19 counter-indicator reaches
−0.010344, directly measuring diminishing target coverage.

**Non-fault process / confounder.** At this dose, repeated fan/channel or
lithologic lineaments in already dense target blocks can look like a
concentration gain while merely increasing kernel overlap. Mapping-intensity
bias remains; the increased `<3 px` neighbour count (19,453) is a spacing cost.

**Predicted live change (MODEL).** Central **−0.0028**, sensitivity
**−0.0254 … +0.0198**. **HOLD** unless C1 has a receipt ≥ 0.2878.

**Falsifier.** Conditional on C1 ≥ +0.010, failure of C2 to improve on C1 by at
least 0.005 falsifies useful dose scaling and confirms saturation. A result
inside ±0.010 of R0 remains no evidence, not confirmation.

## Card C3 — `2km-b50-t33-m7531` (`1e857586`)

**Hypothesis.** Only a strong, persistent block-prior effect could support a
20% transfer; this arm tests the high-dose boundary after C1 and C2 succeed.

**Mechanism.** Adds the next 1,883 nested edits to C2. Mean new H19 credit falls
to 0.682 per addition, source removals begin losing more than their own-pixel
credit, and the H19 counter-indicator reaches −0.022643. This is an explicit
saturation test, not a recommended default upload.

**Non-fault process / confounder.** Forced concentration into well-mapped
blocks can over-sample non-fault contacts and redundant lineament pixels. It
also conflates allocation with crowding: 21,929 dots have a neighbour <3 px.
Any loss may therefore reflect spacing rather than falsify geological
clustering generally.

**Predicted live change (MODEL).** Central **−0.0126**, sensitivity
**−0.0427 … +0.0176**. **HOLD** unless both lower doses have live gains ≥0.010.

**Falsifier.** If C2 gains but C3 drops ≥0.010 relative to C2, the high-dose
hypothesis is falsified and the useful transfer is bounded below 20%. Do not
combine C3 with another axis unless a receipt first overturns this prediction.
