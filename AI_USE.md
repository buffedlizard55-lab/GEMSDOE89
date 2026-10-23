# AI USE — session GEMSDOE89

Required by the competition rules (generative-AI disclosure in
https://docs.nlr.gov/docs/fy26osti/96647.pdf). This file separates what AI
agents wrote and chose from what the human competitor decides.

## What the AI wrote in `GEMSDOE89` (2026-10-23)

- **Core library (`gemsdoe/`):**
  - `gemsdoe/metric.py` — derived DTI algebra (`T`, `S`, `M`, exact `marginal_gain_add` / `marginal_gain_remove`, `pays_threshold`).
  - `gemsdoe/grid.py` — EPSG:32611 100 m GeoTIFF grid contract and byte-deterministic writer.
  - `gemsdoe/spacing.py` — **SPACING** axis (`strike`, `poisson`, `lattice`): ridge structure-tensor orientation, 1-px across-strike NMS crest extraction, shared 610-corridor partitioning on `scored_h19_5` (`d_cat >= 3 px`), and per-corridor count-preserving re-spacing.
  - `gemsdoe/relief.py` — **RELIEF** axis (prior session on disk: equal-area terciles, structured gap-filling relocation).
  - `gemsdoe/validate.py` — binary MUST-pass release gates.
  - `gemsdoe/proxy.py` — REPORT-ONLY diagnostics (catalogue hide-and-recover + Wilson 95 % CI, single-feature leakage canary, counterfactual surrogate DTI, and off-catalogue USGS SGMC fault control).
- **Reproducible scripts & tests (`tools/`, `tests/`):**
  - `tools/fetch_pinned_inputs.py` — SHA-256 + byte-size verified fetcher from `codeload.github.com` only.
  - `tools/rebuild_r0.py` — byte-exact R0 (`h33-h33-2-b2`) rebuild from `parent_base_02708.tif` + `existing_faults.tif` matching both `-zeros` (`c55bafc4…`) and `-nan` (`baeae321…`) SHA-256 pins.
  - `tools/build_spacing.py`, `tools/build_relief.py`, `tools/build_ledger.py`, `tools/validate_raster.py`, `tools/check_ledger.py`.
  - `tests/test_metric.py`, `tests/test_grid_validate.py`, `tests/test_spacing.py`, `.github/workflows/ci.yml`.
- **Documentation & ledger:** `ledger/MECHANISM_CARDS.md`, `ledger/submissions.csv`, `SLOT_PLAN.md`, `IRREGULARITIES.md`, `docs/SUBMIT.md`, `AI_USE.md`, and the `# CURRENT STATE` block of `README.md`.

## What the AI decided (reversible by the human)

- **Session axis = SPACING (`strike`, `poisson`, `lattice`).** Chosen autonomously per prompt instruction after inspecting `ledger/submissions.csv`: `MASS` (3), `PRUNE` (7), `SNAP` (3), `CONCENTRATION` (3), and `RELIEF` (3, built in PR #2) already had recorded `(parent, axis, value)` pairs on R0, whereas `SPACING` had **zero** pairs and is weekly-slot ready at matched dot count (37,654).
- **Per-corridor count-preserving design on `scored_h19_5`.** Verifying that 37,654 / 37,654 R0 dots sit on `scored_h19_5` allowed re-spacing each of R0's 610 widest multi-dot corridors (`d_cat >= 3 px`) to its exact R0 count `n_c`, isolating pure within-corridor dot spacing from `MASS`, `RELIEF`, `CONCENTRATION`, `PRUNE`, and off-ridge false positives.
- **MODEL projections** (`+0.006` for `strike`, `+0.001` for `poisson`, `0.000` for `lattice`) were derived algebraically from crest vs 2-D corridor kernel-credit deltas (`ΔT_crest`, `ΔT_manifold`) and never tuned on local holdouts.

## What the human decided / must decide

- Whether and when to upload any candidate raster from their own registered DrivenData account.
- Supplying `TOP_PUBLIC` + leaderboard date, weekly/total submission quota remaining, confirmation of the 2026-12-03 deadline, and `receipt_score` / `receipt_date` in `ledger/submissions.csv`.
- Whether to privatize upstream public input mirrors (`IRREGULARITIES.md` item 4) and how to package upstream `19GEMSDOE`/`GEMSDOE28` ancestor scripts if requested in final review (`IRREGULARITIES.md` item 1).

## Hard-constraint compliance statement

- Zero requests were made to `drivendata.org` or `dropbox.com`.
- Zero credentials, tokens, or passwords were requested, read, stored, or printed.
- Zero label-probing rasters were built; all edits apply uniform global geometric rules across the entire footprint.
