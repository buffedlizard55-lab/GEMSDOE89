# GEMSDOE project charter

**Read this document before every project session.** This is the durable, auditable version of the project's working brief; README.md is the operational front door, while this page records the enduring objectives, scientific guardrails, and release rules.

## Mission

Find faults in the GeoDAWN / northwestern Great Basin region that are indicative of geothermal resources and are absent from the supplied USGS / INGENIOUS fault catalogue. Produce a scientifically defensible, reproducible, single-band GeoTIFF in the official competition grid, with an unambiguous download/submit decision and a short submission name and note. Maximize the probability of a real improvement, not the number of experiments or uploads.

The competition labels are incomplete and the final round uses an expanded expert-reviewed label set. Therefore, matching the known catalogue is not equivalent to discovering an unmapped fault. Be candid about what each validation method can and cannot establish.

## Values and operating rules

- **Maximize P(Win):** treat each scarce submission slot as a preregistered experiment; do not spend one on a hypothesis that has not beaten the incumbent on an appropriate spatial holdout.
- **Own the outcome:** verify every data input, calculation, output byte, format constraint, and evidence label. Log defects and negative results rather than hiding them.
- **Stay in the assigned lane:** one session/parallel run, one named method. Compare its raster against the local registry before placement and again after placement. Stop and log a duplicate if rank correlation with any registry raster exceeds 0.90 or if more than 70% of its dots are within 3 pixels of one registry raster's dots.
- **Reuse shared infrastructure:** use the template's cached feature stack and shared holdout evaluator / submission writer. Fix a shared-tool defect in the template rather than maintaining a private fork. If those tools or inputs are absent, stop the experiment and document the blocker; do not imitate the protocol with a weaker proxy and call it equivalent.
- **Leakage first:** evaluate each feature alone on the holdout before trusting it. AUC above 0.90 is a leakage alarm until explained.
- **Correct validation:** hide whole catalogue fault segments with a buffer; derive catalogue-based features only from visible segments; mask visible catalogue pixels exactly; evaluate pooled distance-weighted Tversky (alpha 0.2, beta 0.8, 300 m triangular kernel). Report the evaluator version, number of withheld positives, and 95% confidence interval. A pixel-random catalogue recall proxy is not this test.
- **Evidence labels:** label every competition score only as **HOLDOUT-DTI** (with evaluator version, withheld-positive count and 95% CI) or **ORGANIZER-CONFIRMED** (copied from a submission-page receipt). A model projection is never a score. A public mirror, personal website, copied leaderboard, or local proxy is not an organizer receipt.
- **Experiment budget:** stop at three experiments or two hours, whichever comes first. Do not select/present a file as promoted: a separate selector must respect the current weekly cap and blind-final rules.
- **Submission contract:** single-band float32 GeoTIFF, EPSG:32611, same shape, bounds, resolution and affine transform as the official template, in-footprint predictions finite and within [0,1], and outside-footprint null/NaN as specified by the official problem page. Re-open the written file and validate the bytes. Do not mistake a locally passing file-format gate for a proven score improvement.
- **Artifact safety:** visibly state whether a file is format-valid, whether its method passed the required holdout, and whether it is cleared for competition upload. Put an easy-to-click download at the top of the README/site only with that status next to it. Include a unique submission name and a note of at most 140 characters, but do not promote a candidate just because a TIFF can be built.

## Required workflow

1. Read this charter, README.md, `IRREGULARITIES.md`, `SLOT_PLAN.md`, relevant mechanism cards, the submission-format guide, and the current registry/ledger state.
2. Verify the competition's official rules, metric, data and format sources; preserve direct links and provenance. Distinguish official sources from owner-maintained mirrors.
3. Review the latest official receipt and leaderboard only when genuinely available; resolve date and provenance conflicts. Never infer an organizer score from a site score claim.
4. Before implementation, produce a ranked slate of three to five untried geological hypotheses. For each, name the exact layers, physical signature, why it could find an unmapped rather than merely catalogue-known fault, differences from code already present, non-fault mimics, expected relative benefit and cost, and external-data acquisition status if applicable.
5. Select at most one method within the session's assigned lane. Confirm both leakage and registry-duplicate tests before placement. Evaluate with the shared, buffered whole-segment holdout before preparing an upload candidate.
6. Generate a deterministic, uniquely hashed raster with the shared writer. Run hard format gates and the full validation report. Keep failed / negative results as research artifacts, not promoted files.
7. End every experiment record with one JSON run card containing hypothesis, mechanism, named non-fault mimic, HOLDOUT-DTI plus CI (or explicit not-run blocker), registry correlation/overlap, raster SHA-256, validator output, submission name, <=140-character note, and `promote` or `negative` verdict.

## Official references

- [DrivenData — problem description, metric, and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData — competition overview and rules](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [DrivenData — data download page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) (requires account access)
- [DrivenData — official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project, Great Basin Center for Geothermal Energy](https://gbcge.org/current-projects/ingenious/)
- [EPSG:32611 — WGS 84 / UTM zone 11N](https://epsg.io/32611)
- [USGS State Geologic Map Compilation, DS-1052](https://doi.org/10.3133/ds1052) — external control only if the actual artifact and provenance are verified; currently flagged unverified in this repository.

## Current limitations to carry forward

The manifest says the competition rasters are owner-supplied mirrors, not organizer-authenticated, and are deliberately not committed. In the inspected checkout, `data/` is absent; the registry's cached feature stack, labels/catalogue raster and sample template are therefore not available locally. This checkout also has no shared `evaluate_holdout.py` or `submission_writer.py`. Existing proxy reports are not a substitute for the required buffered segment holdout. The SGMC pin is explicitly unverified and cannot be used to gate a candidate. DrivenData authentication is not present in this repository, and the official data page requires an account. Until the correct inputs and shared evaluator are available and verified, no new scientific candidate can be honestly cleared for upload.
