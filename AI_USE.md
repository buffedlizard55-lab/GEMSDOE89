# AI_USE — what the AI wrote, what the human decided

Required by the competition rules (NLR rules PDF, reproducible-code and generative-AI disclosure
clauses; https://docs.nlr.gov/docs/fy26osti/96647.pdf). Keep this current.

## Written by the AI agent (this session)

- All code: `scripts/restore_inputs.py`, `scripts/canonical_writer.py`, `scripts/rebuild_r0.py`,
  `scripts/relief_analysis.py`, `scripts/build_relief_variants.py`, `scripts/relief_report.py`,
  `scripts/validate_release.py`, `src/gems89/{metric,grid}.py`, `tests/`, `.github/workflows/ci.yml`.
- All three RELIEF candidates (rasters, hashes, receipts), the ledger merge, `SLOT_PLAN.md`,
  `docs/SUBMIT.md`, `README.md`, `IRREGULARITIES.md`, this file, and the mechanism cards.
- The diagnosis in IR-89-01 (libdeflate level 10 reproduces the parent's tiles; the wheel GDAL builds
  do not), including the level sweep that established it.

## Copied or adapted from the owner's own earlier sessions (not new AI output)

- The R0 rebuild recipe (`dot_thin` geodesic Poisson-disk thinning, the five lineage stages, and the
  GTiff writer profile: tiled 256×256, deflate, Predictor=3, zlevel 9) was read from
  `GEMSDOE88/scripts/build_prune_variants.py` and `GEMSDOE32`'s registry, then re-implemented here and
  re-verified against both published parent hashes.
- The DTI algebra was re-implemented from the competition problem description as transcribed in the
  brief, and cross-checked against `GEMSDOE32/src/gems32/metric.py` and `GEMSDOE88/vendor/gems57/metric.py`.
- The 20 inherited ledger rows are transcribed from `GEMSDOE88/ledger/submissions.csv`.
- The 2.8284 px spacing lock follows the SNAP lane's finding (IR-88-23/25 in that repository).

## Decided by the human (not the AI)

- Which axis the session pursues (the human waived this and asked the agent to choose; the agent
  picked RELIEF — see IR-89-05).
- Every upload, the submission account, `receipt_score`, `receipt_date`, `TOP_PUBLIC`, slots used.
- Whether to accept the collar deviation in IR-89-03 before uploading any RELIEF file.
- Whether the owner's public data mirrors (IR-89-02) should be taken private.
- The 2026-12-03 deadline (carried UNVERIFIED; the agent may not read the competition page).

## Claims the AI did **not** make

- No score was produced, read, estimated from a leaderboard, or claimed. Every live number in the
  lineage is a CLAIM; every local number is labelled PROXY or MODEL.
- No external data was added: the only inputs are the 10 pinned files in `registry/data_manifest.json`,
  all of them competition files or USGS-public-domain derivatives already used by earlier sessions.
- Nothing was submitted, and no code here can log in, scrape or upload.
