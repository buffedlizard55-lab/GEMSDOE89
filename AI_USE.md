# AI USE DISCLOSURE — GEMSDOE89 (2026-10-23)

Maintained contemporaneously with the work so the human competitor can make an
accurate, auditable disclosure at final submission (`https://docs.nlr.gov/docs/fy26osti/96647.pdf`).

## Scope of AI agent work in this repository

An autonomous coding agent (Arena.ai Agent Mode) executed the GEMSDOE89
single-axis build workflows on branch `arena/f6aaa76f-gemsdoe89` (and prior
merged PRs #2 `RELIEF` and #5 `MASS`):

1. **Input pinning & exact R0 rebuild (`registry/data_manifest.json`, `tools/fetch_pinned_inputs.py`, `tools/rebuild_r0.py`):**
   * Pinned 8 artifacts by immutable Git commit SHA, byte length, and SHA-256
     digest; verified all 8 hashes locally in `./data/` (git-ignored).
   * Rebuilt parent R0 (`h33-h33-2-b2`, 37,654 unit-mass dots) from its recorded
     recipe (`parent_base_02708.tif` pruned by Euclidean distance `> 2.0 px` from
     `existing_faults.tif`) and matched **both** pinned SHA-256 digests
     bit-for-bit (`c55bafc4…` zeros and `baeae321…` NaN).
2. **Axis selection & SPACING variant design (`gemsdoe/spacing.py`, `tools/build_spacing.py`):**
   * Audited `ledger/submissions.csv` across all 121 prior rows (`MASS`, `PRUNE`,
     `SNAP`, `CONCENTRATION`, and `RELIEF` already populated; `SPACING` had 0
     entries) and selected `AXIS = SPACING` autonomously.
   * Designed three fixed-count (`37,654` dots), corridor-preserving (`n_c`
     exact in every one of the 610 multi-dot corridors on `scored_h19_5`,
     `d_cat >= 3.0 px` on 100 % of re-spaced pixels) variants:
     - `strike` (`37910355`, 14.46 % moved / 28.92 % sym diff): strike-anisotropic
       crest-first greedy packing (`r_perp = 3.2 px`, `r_along = 2.2 px`).
     - `poisson` (`95c51e18`, 12.75 % moved / 25.50 % sym diff): isotropic
       Poisson-disk (`r = 2.6 px`) + 3-step discrete Voronoi/Lloyd relaxation.
     - `lattice` (`dd652665`, 13.80 % moved / 27.59 % sym diff): strike-aligned
       hexagonal covering lattice (`a = 3.20 px`) with corridor phase search.
   * Retained prior merged `MASS` (`m10uniq`, `m10rand`, `m20uniq`) and `RELIEF`
     (`r10`, `r15`, `r15s`) arms in `releases/` and `ledger/submissions.csv`.
3. **Validation gates, report-only diagnostics, tests & ledger (`gemsdoe/proxy.py`, `tests/test_spacing.py`, `tools/build_ledger.py`):**
   * Verified all 18 GeoTIFFs in `releases/` from disk against `sample_submission.tif`
     and `existing_faults.tif` (`registry/format_receipts.json`).
   * Computed REPORT-ONLY diagnostics (`registry/leakage_canary.json`,
     `registry/report_only_status.json`): single-feature leakage canary
     (`max |AUC| = 0.651 <= 0.90`), 30 % catalogue `hide_and_recover` with 95 %
     CI, and off-catalogue USGS SGMC fault control (`n = 63,121` px at
     `d_cat >= 3.0 px`).
   * Authored mechanism cards (`ledger/MECHANISM_CARDS.md`), 1-page slot plan
     (`SLOT_PLAN.md`), submission checklist (`docs/SUBMIT.md`), and irregularity
     report (`IRREGULARITIES.md`).

## What the AI agent did NOT do

* Did **not** access `drivendata.org` or `dropbox.com`, scrape any leaderboard,
  or read/store/use any credentials.
* Did **not** upload or score any submission, and did **not** generate synthetic
  labels or train an ML model on held-out test feedback.
* Did **not** verify `TOP_PUBLIC`, remaining submission slots, or live portal
  receipts (all marked `CLAIM` or blank for the human competitor).
