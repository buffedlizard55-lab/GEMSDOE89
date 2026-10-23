# AI Use Disclosure (`AI_USE.md`)

This repository was developed with an autonomous coding agent on Arena.ai Agent Mode for the GEMS Prize (DrivenData challenge #306).

## Scope of AI Contributions (`GEMSDOE89`)

1. **Parent Verification & Exact Rebuild (`gemsdoe/parent.py`, `tools/rebuild_r0.py`):**
   - Verified SHA-256 hashes of all pinned inputs in `registry/data_manifest.json`.
   - Rebuilt parent R0 (`h33-h33-2-b2`, 37,654 unit-mass dots) bit-for-bit from `scored_h19_5.tif` (`dot_thin(r=2.8)` + `d_cat > 2.0` prune on `sample_submission.tif` grid), matching both `c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9` (`-zeros.tif`) and `baeae321d33f676473d31a158da4e4eb15ca55897d2d9c9af3a38de0cb48fc04` (`.tif`), plus independent ancestor subset verification (`h27_4_solo.tif`, `d28.tif`).
2. **Candidate Generation Across Orthogonal Axes (`gemsdoe/spacing.py`, `gemsdoe/relief.py`, `gemsdoe/mass.py`, `gemsdoe/snap.py`):**
   - **`SNAP` session (merged 2026-10-23, branch `arena/7efbb7cc-gemsdoe89`):** built the gateless (`g0p00`) corner of the SNAP factorial — `1p0px` / `1p4px` / `2p0px` windows at fixed count (`n=37,654`), deterministic (no RNG), targets `d_cat >= 3.0 px`, with `tools/rebuild_r0.py` re-run as the start gate and an independent mask-to-byte rebuild check (`registry/build_report_snap_*.json`, mechanism cards in `ledger/MECHANISM_CARDS.md` Part III). Manifest pins were re-verified: three broken pins corrected and one marked UNVERIFIED (`IRREGULARITIES.md` items 1/8).
   - **`SPACING` session:** Designed and built 3 deterministic (`seed=20261023`), count-preserving (`n=37,654`) variants (`alongstrike`, `poisson`, `lattice`) on R0's 834 multi-dot fault strands (`>=6` dots), plus structural-geologist mechanism cards (`ledger/MECHANISM_CARDS.md`).
   - **Earlier `GEMSDOE89` sessions preserved in `releases/` and `ledger/submissions.csv`:** `RELIEF` (`r10`, `r15`, `r15s`) and drop-only `MASS` (`m10uniq`, `m10rand`, `m20uniq`, `ledger/MECHANISM_CARDS_MASS.md`).
3. **Validation, Canary & Report-Only Controls (`gemsdoe/validate.py`, `gemsdoe/proxy.py`, `tests/`):**
   - Verified all 24 GeoTIFFs in `releases/` (`6 SNAP + 6 SPACING + 6 RELIEF + 6 MASS`) against every MUST gate after re-reading from disk (`tools/validate_raster.py` + `tools/check_ledger.py` + 25 unit tests).
   - Computed 20-feature single-feature leakage canary (`max = 0.5688 <= 0.90`), catalogue hide-and-recover `PROXY` (`0.0384`, 95% CI `[0.0329, 0.0440]`), USGS SGMC off-catalogue external fault `PROXY` (`https://doi.org/10.3133/ds1052`, US Public Domain), and lateral-jitter DTI `MODEL` curves.
4. **Documentation & Slot Planning:**
   - Authored `SLOT_PLAN.md`, `README.md` (`CURRENT STATE`), `docs/SUBMIT.md`, `IRREGULARITIES.md`, and `ledger/submissions.csv` (the `SNAP` session merged the parallel `SPACING`/`MASS` sessions' outputs into one queue and wrote the integrated next-3 slot plan).
   - **Session-specific decisions the human can reverse (SNAP):** axis choice (SNAP gateless — MASS ±10 % and PRUNE ≤1/≤2/≤3 px were already built upstream, RELIEF/SPACING/MASS-drop were complete on `main`); the response recipe was replicated exactly from the upstream recorded recipe (bands 3 `tmi_hg` + 18 `iso_grav_anom_hg`) so a cross-session receipt comparison isolates only the gate; prediction bands use the upstream live-anchor inversion (`D = 18,734.44`) with an explicit negative side (−0.05/+0.05/+0.15 scenario) that upstream bands omitted — evidence class `MODEL`, never a score.

## Guardrails Enforced

- Zero automated access to `drivendata.org` or `dropbox.com`; zero submissions executed; zero credentials accessed or stored.
- Zero competition input rasters committed to git or `releases/`.
- Strict separation of `RECEIPT`, `CLAIM`, `PROXY`, and `MODEL` labels throughout code, ledger, and documentation.
