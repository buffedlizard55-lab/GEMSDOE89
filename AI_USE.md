# AI Use Disclosure (`AI_USE.md`)

This repository was developed with an autonomous coding agent on Arena.ai Agent Mode for the GEMS Prize (DrivenData challenge #306).

## Scope of AI Contributions (`GEMSDOE89`)

1. **Parent Verification & Exact Rebuild (`gemsdoe/parent.py`, `tools/rebuild_r0.py`, `tools/fetch_pinned_data.py`):**
   - Verified SHA-256 hashes of all 10 fetchable pinned inputs in `registry/data_manifest.json` (`sgmc_faults_control` flagged `UNVERIFIED` and skipped; fixed shared-archive multi-destination extraction in `tools/fetch_pinned_data.py` with offline regression test `tests/test_fetch_pinned_data.py`).
   - Rebuilt parent R0 (`h33-h33-2-b2`, 37,654 unit-mass dots) bit-for-bit from `scored_h19_5.tif` (`dot_thin(r=2.8)` + `d_cat > 2.0` prune on `sample_submission.tif` grid), matching both `c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9` (`-zeros.tif`) and `baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd` (`.tif`).
2. **Candidate Generation Across Orthogonal Axes (`gemsdoe/concentration.py`, `gemsdoe/snap.py`, `gemsdoe/spacing.py`, `gemsdoe/relief.py`, `gemsdoe/mass.py`):**
   - **`CONCENTRATION` session (2026-10-23, branch `arena/6e810001-gemsdoe89`):** Implemented deterministic (zero-RNG) `12.8 km` (`128 px`) structural-domain reallocation (`gemsdoe/concentration.py`, `tools/build_concentration.py`, `tests/test_concentration.py`) and built 3 count-preserving (`n=37,654`) variants (`12p8km-int10`, `12p8km-int20`, `12p8km-geod15`) with added-dot clearance `d_cat >= 3.00 px`, frozen `<3 px` parent collar (`1,611` dots), inter-dot separation `r_sep >= 2.80 px`, proportional block quotas (`40/60` quantile split), and strike-coherent corroborated scarp/potential-field ridge placement (bands `3, 5, 12, 19`). Authored Part IV mechanism cards in `ledger/MECHANISM_CARDS.md` and `registry/build_report_conc_*.json`.
   - **`SNAP` session (merged PR #10):** Built gateless (`g0p00`) SNAP variants (`1p0px`, `1p4px`, `2p0px`) at fixed count (`n=37,654`).
   - **Earlier `GEMSDOE89` sessions preserved in `releases/` and `ledger/submissions.csv`:** `SPACING` (`alongstrike`, `poisson`, `lattice`), `RELIEF` (`r10`, `r15`, `r15s`), and drop-only `MASS` (`m10uniq`, `m10rand`, `m20uniq`; `ledger/MECHANISM_CARDS_MASS.md`). Updated `tools/build_ledger.py` so all 5 axes assemble without clobbering human receipts.
3. **Validation, Canary & Report-Only Controls (`gemsdoe/validate.py`, `gemsdoe/proxy.py`, `tests/`):**
   - Verified all 30 GeoTIFFs in `releases/` (`6 CONCENTRATION + 6 SNAP + 6 SPACING + 6 RELIEF + 6 MASS`) against every MUST gate after re-reading from disk (`tools/validate_raster.py` + `tools/check_ledger.py` + 47 unit tests).
   - Ran single-feature leakage canary (`max = 0.5688` across 20 inputs; `0.5995` including `corrob_ridge`; threshold `0.90`), pixel-withheld catalogue `PROXY` (`0.0384`, 95% CI `[0.0329, 0.0440]`), and 3-seed 25% connected-strand holdout + matched random-block-shuffle `MODEL` calibration (`registry/report_only_status.json`).
4. **Session-Specific Decisions the Human Can Reverse (`CONCENTRATION`):**
   - Axis choice (`CONCENTRATION` at `12.8 km` scale — unprobed in `GEMSDOE89`, distinct from upstream `GEMSDOE84` `5 km` blocks, and addressing R0's `3.67×` Low-tercile / `0.52×` High-tercile accommodation-zone misallocation).
   - Promoting `conc-12p8km-int10` (`+0.008 MODEL`, `CV_12.8km = 0.5533`) ahead of `relief-r10` (`+0.003 MODEL`) as Slot 1's spatial-allocation probe (`relief-r10` remains validated in `releases/` if preferred).
   - Using `corrob_ridge` (unsupervised DEM concavity + slope break + gravity slope + TMI HG × 600 m strike coherence) for off-`h19_5` additions because `scored_h19_5.tif` is binary (`{0, 1}`).

## Guardrails Enforced

- Zero automated access to `drivendata.org` or `dropbox.com`; zero submissions executed; zero credentials accessed or stored.
- Zero competition input rasters committed to git or `releases/`.
- Strict separation of `RECEIPT`, `CLAIM`, `PROXY`, and `MODEL` labels throughout code, ledger, and documentation.
