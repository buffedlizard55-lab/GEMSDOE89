# Project charter (session prompt, condensed — read at the start of every session)

**Mission.** Generate a *unique*, format-validated GeoTIFF submission for
the DOE GEMS prize (DrivenData #306, blind-fault / geothermal exploration,
NW Great Basin) that can beat the fleet best `h33-h33-2-b2` = 0.2778
(CLAIM) — with its submit / do-not-submit status obvious on the site's
executive summary, no human inspection step, and no hallucinations:
every number labelled, every claim traceable to a file, hash, or
official link verified line by line.

**Parallel-run protocol (binding).**
1. One lane per session. Rank-correlation ≥ 0.90 with, or > 70% of dots
   within 3 px of, any registry raster ⇒ duplicate: log and stop.
   Check the surface before placement and the final dots.
2. Reuse the cached feature stack, `evaluate_holdout` and
   `submission_writer` equivalents (`gemsdoe/holdout.py`,
   `gemsdoe/grid.py`). Holdout = withhold whole fault segments with a
   buffer; catalogue features from visible faults only; visible faults
   masked pixel-exactly; pooled DTI (α 0.2, β 0.8, 300 m triangular).
   Fix shared tools once, never fork privately.
3. Label every number HOLDOUT-DTI (evaluator version, withheld n, 95%
   CI) or ORGANIZER-CONFIRMED (receipt). A projection is never a score.
4. Leakage canary: single-feature AUC > 0.90 ⇒ leakage until disproven.
5. End with one JSON run card (hypothesis, mechanism, named mimic,
   holdout DTI + CI, registry correlation/overlap, raster sha256,
   validator output, name + ≤140-char note, verdict promote/negative).
   Negative results are deliverables.
6. Budget: 3 experiments or 2 hours. Promotion to a real (weekly-capped)
   slot is a separate human selector step.

**Hypothesis discipline.** Before implementing, rank 3–5 untried
geological hypotheses (layers, physical signature, why catalogue-missing,
difference vs repo) by expected DTI ÷ cost (`docs/HYPOTHESES.md`).
Validate the top candidate on the segment holdout before any slot.
Ideas needing new external data must name a specific free official
source and be obtainable (the LiDAR rank-5 item fails this in-sandbox
and is labelled as such).

**Core values.** *Maximize P(Win)* — weigh tradeoffs by win probability,
not comfort. *Own the Outcome* — end-to-end accountability; act without
waiting for permission; treat failure and success as signals.

**Standing facts.** Fleet best 0.2778 = CLAIM (no receipts anywhere in
the ledger). Public-top figures in circulation (0.4413, 0.3195) conflict
⇒ UNVERIFIED until a human supplies value + date from
https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ .
Competition: https://www.drivendata.org/competitions/306/competition-doe-gems/ ·
rules https://docs.nlr.gov/docs/fy26osti/96647.pdf · reference
https://github.com/drivendataorg/gems-prize-reference-solution ·
GeoDAWN https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and ·
INGENIOUS https://gbcge.org/current-projects/ingenious/ · GDR
https://gdr.openei.org/submissions/1391 · CRS https://epsg.io/32611 ·
metric family https://en.wikipedia.org/wiki/Tversky_index .
**Submission-format caution.** The official problem description requires a
single-band float32 GeoTIFF on the provided grid, with probabilities in
[0, 1] and null/NaN outside the bounds. The checked-in sample itself uses a
NaN nodata mask outside its finite footprint. A previous form attempt
reported “Predicted values must be in range [0, 1]”; that message alone does
not establish whether NaN, an out-of-range sentinel, or another file issue
caused the rejection. Never claim the portal accepts a file unless an
organizer receipt or verified portal validation is recorded. For this run,
the GeoTIFF validator verifies finite values in [0, 1] inside the footprint,
no NaN inside, and NaN only outside the footprint. The candidate is still
**DO NOT SUBMIT** because its HOLDOUT-DTI verdict is negative.

This charter is the repository's persistent, operative project prompt; the
README links to it and it must be read at the start of each session. The
user-supplied fleet annex is recorded in `ledger/submissions.csv` with
unconfirmed external scores labelled CLAIM, not copied into organizer
receipts. See `docs/SUBMIT.md` for the current exact file status and
submission workflow.
