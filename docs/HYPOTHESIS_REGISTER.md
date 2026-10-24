# GEMS fault-discovery hypothesis register

**Scope for this iteration:** one experiment only: the `COND-EDGE` lane. The other rows are ranked ideas, not implementations or submission candidates. No new external raster is required for the selected experiment; it uses the pinned 19-band GeoDAWN feature stack already fetched by `tools/fetch_pinned_data.py`.

## Research-grounded candidates (ranked before implementation)

| Rank | Hypothesis / feature layers | Targeted physical signature | Why it could find unlabelled fault geometry | Difference from this repository | Expected DTI direction / effort |
|---|---|---|---|---|---|
| **1 — selected: COND-EDGE** | Band 17 `cond_surf`; multi-scale Gaussian gradient magnitude and persistent edge peaks | Linear conductivity/conductance boundaries, especially connected edge segments at more than one smoothing scale | USGS blind-play-fairway work reports low-resistivity anomalies among collocated indicators at a blind Great Basin system; faults can focus fluid circulation and alteration. This is a physically plausible *indirect* target for unmapped structures, including splays/continuations, not a claim that every conductivity edge is a fault. | Current `SNAP` relocates dots on the fused TMI/gravity horizontal-gradient response (bands 3 and 18); this tests a separate conductivity layer and a new multi-scale edge transform. No existing `GEMSDOE89` builder uses band 17. | **Uncertain, positive if fluid/alteration boundaries align; low-to-moderate cost.** Main risk: lithologic, groundwater, and basin-fill conductivity boundaries. |
| **2 — not run** | Bands 7 `geod_shearrate`, 8 `geod_dilaterate`, and 4 `geod_2ndinv`; local tensor-coherence / strain-boundary ridges | Spatially coherent extensional-strain gradients and dilatational/shear transitions | Great Basin geothermal literature links regional extension and structural discontinuities with permeability; locally coherent strain transitions could reveal unmapped active structures or fault splays. | The existing 12.8-km `geod15` arm uses a block-scale geodetic prior (bands 4/7/16); this would be a local, scale-dependent edge/texture transform with a different geometry, not a replay of that block reallocation. | **Uncertain; moderate cost.** Main mimic: interpolation seams and sparse GPS/InSAR support; no additional data needed. |
| **3 — not run** | Bands 3 `tmi_hg`, 18 `iso_grav_anom_hg`, 6 `tc`, with lineament orientation | Potential-field edge termination, bend, or paired-gradient junctions rather than edge amplitude alone | USGS Great Basin studies describe fault intersections, stepovers, terminations, and terminating gravity/magnetic gradients as favorable structural settings; junction-like features may reveal unmapped fault geometry related to a known system. | Existing `SNAP` uses a pixelwise maximum of two gradient magnitudes and relocates an existing ridge inventory. This candidate would score *topology* (orientation continuity and termination/junction geometry), not simply stronger gradient magnitude. | **Plausibly positive, moderate-to-high cost.** Main mimic: dikes, lithologic contacts, cultural magnetic noise, and raster edge artifacts. |
| **4 — not run** | Band 12 `det_elev`, band 19 `det_elev_slope`; signed multi-scale curvature / scarp asymmetry | Paired convex-concave topographic breaks and asymmetric scarps | Surface offsets and scarp geometry can expose unmapped Quaternary faults, including extensions and splays not in a regional catalogue. | The repo's `RELIEF` shifts counts among elevation/slope classes and `SNAP` uses slope direction; neither ranks signed, paired curvature patterns as a fault-scarp morphology detector. | **Uncertain; moderate cost.** Main mimic: fan channels, shorelines, erosional scarps, roads, and volcanic flow margins. |

### Why COND-EDGE is the first test

The top candidate is low-cost, uses a different sensor-derived layer than the existing TMI/gravity ridge-placement arms, and is testable with no external-data dependency. The literature supports testing conductivity as one contextual indicator, not treating it as a direct fault label. Before emission, its conductivity edge surface and final dots are checked against locally available registry rasters; correlation above 0.90 or more than 70% of dots within 3 pixels of any one registry raster is an automatic duplicate-stop. Every feature is also tested alone on the spatial holdout as a leakage canary; an AUC above 0.90 is treated as leakage until disproven.

## Executed lanes (this and prior sessions)

ANNULUS, PF-PEAKS and TC-UNION were evaluated with `GEMSDOE89-spatial-segment-holdout-v1`. The existing
COND-EDGE lane was subsequently re-evaluated with corrected `GEMSDOE89-spatial-segment-holdout-v3`; its
rounded metrics were unchanged. All use alpha 0.2, beta 0.8, the 300 m triangular kernel and pinned
SHA-256-verified inputs; the visible-only R0 comparator is HOLDOUT-DTI `0.161230 [0.142648, 0.180061]`.
All verdicts remain `negative`; no slot was used and no file is cleared to submit. Current COND-EDGE
leakage canaries max at 0.5698 (<0.90). Local uniqueness checks do not cover remote public registries.

| lane | layers / transform | holdout DTI (95% CI) | paired delta vs R0 | artifact | status |
|---|---|---|---|---|---|
| COND-EDGE (existing lane, v3 re-evaluation) | b17 `cond_surf`, max Gaussian gradient sigma 2, 4 px | 0.049875 [0.036830, 0.061751] | −0.111355 [−0.133218, −0.087864] | `releases/h89-condedge-s2-4-20261024-b5e502f0-zeros.tif` | negative, DO NOT SUBMIT |
| ANNULUS | b3 `tmi_hg` + b18 `iso_grav_anom_hg` gradient ridges, 200–800 m annulus around visible faults (splay/stepover targeting) | 0.001202 [0.000455, 0.002061] | −0.160028 [−0.180591, −0.139843] | `releases/h89-annulus-splay-20261024-e9b2bec1-candidate.tif` | negative, DO NOT SUBMIT |
| PF-PEAKS | b3 + b18 gradient ridges, fixed-mass spaced peaks, R0's >2 px visible-fault prune | 0.068825 [0.042551, 0.095776] | −0.092405 [−0.136201, −0.049139] | `releases/h89-pfpeaks-20261024-18f0316a-candidate.tif` | negative, DO NOT SUBMIT |
| TC-UNION | b3 `tmi_hg` + b6 `tc` (tilt/total curvature) + b18 `iso_grav_anom_hg` gradient ridges, same prune | 0.070181 [0.043417, 0.097668] | −0.091049 [−0.135214, −0.047593] | none emitted — blocked as duplicate of PF-PEAKS (100% of dots within 3 px) | negative |

Interpretation: held-out truth sits 8–12 km from visible faults, so only the geophysical ridge surface
carries usable local signal; R0's skeleton placement is the strongest local baseline and none of the
tested surfaces improved on it. Per the parallel-run protocol, promotion to a weekly slot requires a
`promote` holdout verdict first — no lane reached it. Remaining untested hypotheses from this register:
rank 2 (geodetic strain boundaries, bands 4/7/8), rank 3 (potential-field junction topology, bands 3/6/18),
rank 4 (topographic scarp curvature, bands 12/19) — each would need its own holdout run before any slot
decision; note the segment holdout is acknowledged (BSTP run card) as unable to validate blind
off-catalogue fault discovery, only catalogue-habitat placement.

## Trusted sources for manual review

| Claim used here | Primary source |
|---|---|
| GeoDAWN magnetic/radiometric survey context and purpose | [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) |
| Survey metadata, flight-line spacing and DOI | [USGS ScienceBase/USGS Data Catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7) |
| Blind geothermal play-fairway: structural setting, gravity/magnetic gradients, low-resistivity anomaly, and temperature evidence | [USGS publication](https://www.usgs.gov/publications/discovering-blind-geothermal-systems-great-basin-region-integrated-geologic-and) |
| Structural discontinuities, fault intersections, stepovers and terminations in Great Basin hydrothermal systems | [USGS publication](https://www.usgs.gov/publications/structural-discontinuities-and-their-control-hydrothermal-systems-great-basin-usa) |
| USGS 3DEP one-meter DEM availability for the topographic-scarp hypothesis | [USGS National Map 3DEP data collection](https://data.usgs.gov/datacatalog/data/USGS:4f34caac-f28f-4ea0-8d82-eafb2b8f9a5d) |
| Competition metric and submission specification | [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) |
| Pixel-exact masking clarification (staff response) | [DrivenData community clarification](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516) |

## Source/data limitations

- The selected test uses the competition's pinned local feature stack, not new USGS downloads. The official sources establish scientific plausibility and survey metadata; they do **not** establish that band 17 is a direct measure of geothermal fluid pathways or that conductivity boundaries are faults.
- SGMC is not used: its local artifact pin is explicitly UNVERIFIED in `registry/data_manifest.json` and is report-only.
- Public leaderboard values are not local submission receipts. The repository's 0.2778 parent number remains `CLAIM` until an organizer submission receipt is recorded.
