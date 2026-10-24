# GEMSDOE project brief — read at the start of every work session

This is the compact, maintained operating brief for the original project request. Read it together with `README.md`, `IRREGULARITIES.md`, `SLOT_PLAN.md`, and `docs/SUBMIT.md` before proposing work. New facts must be tagged by evidence class and tied to an auditable artifact.

## Mission

Build a scientifically defensible, reproducible system for discovering previously unmapped faults relevant to geothermal exploration in the DOE GEMS/DrivenData challenge. Maximize probability of winning by prioritizing honest out-of-sample evidence over attractive narratives; own outcomes from research through validation and record failures as useful results. Do not promise a leaderboard score without an organizer receipt.

## Operating values

- **Maximize P(Win):** compare likely benefit, uncertainty, cost, leakage risk, and the weekly submission budget before acting.
- **Own the Outcome:** verify all inputs and outputs, repair shared defects in this repo, publish limitations, and retain negative results.
- **No hallucinations:** distinguish verified source statements, measurements, claims, projections, and unknowns. Cite primary sources, preserve hashes, and flag conflicts rather than reconciling them by guesswork.

## Required research-and-build sequence

1. Review this brief and current repo state; confirm the active branch; audit existing implementations, releases, and the full local ledger before suggesting a new lane.
2. Before implementation, register three to five distinct geological hypotheses. Each must state exact layer(s), physical signature/transform, why it might find a fault absent from the USGS/INGENIOUS catalogue, what already-built method it differs from, a named non-fault mimic, evidence needed, expected direction of DTI change, and implementation cost. Rank them; choose one lane only for an experiment.
3. Use the pinned/cacheable feature stack and shared holdout/evaluator/writer tools. Withhold whole connected fault segments in spatial blocks; remove a 300 m (3 px at 100 m) buffer from visible-fault-derived features; mask visible fault pixels exactly; test every feature alone as a leakage canary; pool exact DTI contributions (alpha 0.2, beta 0.8, 300 m triangular kernel) and provide a spatial 95% confidence interval. A single-feature AUC strength above 0.90 is leakage until disproven.
4. Compare a candidate to the best comparable holdout baseline before any slot recommendation. Pre-placement surface and final raster must be checked against registry rasters for absolute rank correlation >0.90 and >70% of candidate dots within 3 px of one registry raster. If a threshold trips, record a duplicate and stop. Test available exact hashes too.
5. Validate a single-band GeoTIFF against the sample template: CRS, shape, transform, dtype, prediction range [0,1], no NaN inside the scoring footprint, and the chosen nodata encoding outside. Create a unique, human-readable filename and a form note no longer than 140 characters. Display plainly whether the artifact is **OK TO SUBMIT** or **DO NOT SUBMIT**.
6. Run no more than three experiments or two hours. Negative holdouts are deliverables. A `promote` result means it passed research gates only; a separate selector decides whether to use a weekly slot. Never upload, access credentials, or submit on the user's behalf.
7. Finish with one JSON run card containing hypothesis, mechanism, non-fault mimic, holdout DTI/evaluator/withheld-positive count/95% CI, registry correlation and overlap, raster SHA-256, validator results, submission name/note, and `promote` or `negative` verdict.

## Evidence labels

- **ORGANIZER-CONFIRMED:** exact score copied from a DrivenData submission receipt; store receipt provenance.
- **CLAIM:** user- or owner-reported live score without receipt in this checkout.
- **HOLDOUT-DTI:** local blocked holdout score, always with evaluator version, withheld positives, and confidence interval; never a live score.
- **PROXY:** catalogue-based or external-control diagnostic, not the competition score.
- **MODEL:** projection/scenario, never a score.

## Competition/research boundaries

- Competition source data in `data/` are pinned owner-supplied mirrors, ignored by Git, and are not verified as organizer-authenticated. Do not commit or republish them.
- Do not access DrivenData or Dropbox automatically, and do not use credentials. The user manually submits only after the artifact is explicitly cleared and chooses a slot.
- USGS SGMC is UNVERIFIED in this checkout and must remain report-only until restored from an official source and hash-verified.
- Current leaderboard and deadline must be dated and source-verified. User-provided conflicting values are not silently treated as current truth.
- Always review official competition rules, official USGS/DOE data and publications, and the organizer's clarification on known-fault masking. The official staff clarification states the mask is pixel-exact; do not invent a proximity exclusion around known faults.

## Starting links

- [Competition overview, metric, rules and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Competition data tab (login required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Competition submission/technical guide (NLR/DOE PDF)](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [Competition About page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [USGS blind geothermal play-fairway publication](https://www.usgs.gov/publications/discovering-blind-geothermal-systems-great-basin-region-integrated-geologic-and)
- [Official known-fault pixel mask clarification](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516)
- [EPSG:32611](https://epsg.io/32611)
- [Submission instructions for this repository](SUBMIT.md)

## Known score-provenance issue to keep visible

The repository reconstructs `h33-h33-2-b2` byte-for-byte from its recorded predecessor. Its `0.2778` value is `CLAIM`, not `ORGANIZER-CONFIRMED`. The user's prompt mentions multiple leaderboard snapshots (`0.3195` and `0.4413`) without dates or receipts; they are unverified snapshots, not a validated current target. The artifact's geometric identity is verified; the causal reason it scored as it did cannot be established from one score alone.
