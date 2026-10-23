# AI USE — session GEMSDOE89

Required by the competition rules (generative-AI disclosure in
https://docs.nlr.gov/docs/fy26osti/96647.pdf as cited in the brief).
This is a factual record of AI-produced work and human decisions.

## What the AI wrote — merged RELIEF work

- `gemsdoe/metric.py`: derived DTI algebra, exact add/remove marginal-gain
  functions and payment-threshold helper; no organizer metric code was read.
- `gemsdoe/grid.py`: grid contract and byte-deterministic writer, with GeoTIFF
  tags copied programmatically from the pinned template.
- `gemsdoe/relief.py`: equal-area relief classes, source/target statistics and
  structure-gated relocation.
- `gemsdoe/proxy.py`, `gemsdoe/validate.py`: REPORT-ONLY instruments and MUST
  gates.
- `tools/build_relief.py`, `tools/build_ledger.py`, `tools/validate_raster.py`,
  `tests/`, `.github/workflows/ci.yml`, the three RELIEF releases, and their
  reports/documentation.

## What the AI wrote — current SPACING continuation (2026-10-23)

- `gemsdoe/spacing.py`: the shared crowded-dot removal, best-candidate
  Poisson-disk anchors, matched 3 px lattice and local-PCA strike placements,
  plus parent-diff statistics.
- `tools/build_spacing.py`: pinned-input verification, exact R0 verification,
  deterministic construction, both TIFF encodings, disk re-read/gates, report-
  only instruments, clean-git provenance and ledger upsert.
- `tests/test_spacing.py`: five synthetic tests of deterministic controls,
  exact parent diffs, catalogue clearance, separation and fraction limits.
- `registry/*spacing*.json`, `registry/input_verification_spacing.json`, the
  three SPACING releases and their ledger rows.
- `ledger/MECHANISM_CARDS_SPACING.md`, and revisions to `README.md` (CURRENT
  STATE only), `SLOT_PLAN.md`, `docs/SUBMIT.md`, `IRREGULARITIES.md` and this
  disclosure.

## What the AI decided (and the human can reverse)

- **Prior axis = RELIEF.** It was selected because no RELIEF `(axis, value)`
  pair existed at that time. The source/target classes and structure gate were
  chosen from the pinned catalogue/features, never test truth.
- **Current axis = SPACING.** After the merged RELIEF work, it was the only
  unused weekly axis on R0; TRACKB was not chosen because it is not a weekly-
  slot candidate without a human decision.
- The SPACING dose is 10% (3,765 dots). All arms share the same crowded-dot
  removals and Poisson gap anchors. A **5 km control block** was selected so
  concentration stays fixed while retaining legal capacity at footprint edges.
- Lattice/Poisson/strike definitions, local PCA strike approximation, fixed
  seed 20261023, and all predicted changes/bands are AI choices. Predictions
  are **MODEL**, not measured scores or calibrated confidence intervals.
- REPORT-ONLY proxy/canary results were not used as gates or to flip predicted
  signs. SGMC was not run because its raster is not pinned in the manifest.

## What the human decided / must decide

- Which files to submit and when. The human submits from their own registered
  account; the agent never submits, logs in, or scrapes the leaderboard.
- `TOP_PUBLIC` and its date, slots used/available, every receipt score/date,
  and confirmation of the 2026-12-03 deadline.
- Whether the pre-existing public competition-data mirrors should be made
  private (`IRREGULARITIES.md` item 4).
- Whether parent-level reproducibility review requires the original R0 recipe;
  this repo verifies the exact parent artifact but does not possess that recipe.

## What no AI did here

- No DrivenData page was fetched (the brief cites terms banning automated
  access), no Dropbox resource was contacted, and no credentials were handled,
  requested, stored or transmitted.
- No test truth was accessed and no region-isolated/patterned file was made to
  locate public-test faults. The only labels used are the pinned USGS/INGENIOUS
  catalogue for mandatory exclusion and REPORT-ONLY measurements.
- No new external dataset was used for SPACING. The 19-band feature stack was
  hash-verified as a pinned input but its pixel values were not read by this
  axis.
