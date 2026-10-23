# AI USE — session GEMSDOE89

Required by the competition rules (generative-AI disclosure in
https://docs.nlr.gov/docs/fy26osti/96647.pdf as cited in the brief).
This file separates what the AI agent wrote and decided from what the human
competitor decided and must supply.

## What the AI wrote in this repository (2026-10-23)

- `gemsdoe/parent.py` and `tools/rebuild_r0.py` — exact BFS `dot_thin(r_min=2.8)`
  and `d_cat > 2.0 px` flank-prune recipe rebuilding Parent R0 (`h33-h33-2-b2`,
  37,654 dots) bit-for-bit from `scored_h19_5.tif` and verifying both upstream
  GeoTIFF SHA-256 digests (`c55bafc4…` zeros, `baeae321…` NaN).
- `gemsdoe/spacing.py` and `tools/build_spacing.py` — the three `SPACING`
  operators (`alongstrike`, `poisson`, `lattice`) at fixed global and
  per-corridor dot count, 20-feature leakage canary, and cross-strike jitter
  `MODEL` sensitivity analysis.
- `tools/fetch_pinned_data.py` — SHA-256-verified streamer from pinned
  `codeload.github.com` tarballs (`registry/data_manifest.json`).
- `gemsdoe/metric.py`, `gemsdoe/grid.py`, `gemsdoe/relief.py`, `gemsdoe/proxy.py`
  (including the USGS SGMC off-catalogue `PROXY` control), `gemsdoe/validate.py`,
  `tools/build_relief.py`, `tools/build_ledger.py`, `tools/check_ledger.py`,
  `tools/validate_raster.py`, unit tests in `tests/`, and `.github/workflows/ci.yml`.
- Documentation and registries: `ledger/MECHANISM_CARDS.md`, `SLOT_PLAN.md`,
  `IRREGULARITIES.md`, `docs/SUBMIT.md`, `README.md` (`CURRENT STATE`), and
  `registry/*.json`.

## What the AI decided (reversible by the human)

- **Axis selection = `SPACING`** (following the prior merged PR #2 on `RELIEF`).
  The brief instructed the agent to pick its own axis without prompting. Checking
  `ledger/submissions.csv` showed existing `(AXIS, value)` pairs on `MASS` (3),
  `CONCENTRATION` (3), `SNAP` (3), `PRUNE` (7), and `RELIEF` (3), leaving
  `SPACING` as the sole unbuilt Phase-1 weekly-slot axis (`0` prior pairs).
- **Single-variable scope (`min_component_dots = 6`, `d_cat >= 3.0 px`).** Freezing
  short (`< 6`-dot) fragments and R0's 1,611 inherited `2 < d_cat < 3 px` collar
  dots while holding integer dot count fixed on each of the 834 major `h19_5`
  strands (`>= ~1.8 km`) keeps `% changed` strictly inside `1–50 %` under both
  relocation (`13.87–20.29 %`) and symmetric-difference (`27.74–40.57 %`) metrics,
  with zero `MASS`, `CONCENTRATION`, `RELIEF`, `SNAP`, or `PRUNE` confounding.
- **Honest `MODEL` signs (`+0.002` `alongstrike`, `−0.010` `poisson`, `−0.007`
  `lattice`).** Derived from the DTI kernel algebra across cross-strike jitter
  `σ_⊥ = 0..2.2 px`, rather than adopting the positive SGMC `PROXY` delta at face
  value.

## What the human decided / must supply

- Every submission upload decision and account action on DrivenData.
- `TOP_PUBLIC` + leaderboard date, weekly/total slots remaining, confirmation of
  the `2026-12-03` deadline, and `receipt_score` + `date` for each scored upload.
- Visibility of public upstream mirror repositories (`IRREGULARITIES.md` item 4).

## Hard-constraint compliance check

- Zero contact with `dropbox.com` or `drivendata.org`; zero credential reads,
  prompts, or storage; zero automated submission or leaderboard scraping.
- Zero mass emitted on `existing_faults.tif`; all newly placed dots satisfy
  `d_cat >= 3.00 px`.
- No competition input rasters committed to Git.
