# AI Use Disclosure (`AI_USE.md`)

This repository was developed with an autonomous coding agent on Arena.ai Agent Mode for the GEMS Prize (DrivenData challenge #306).

## Scope of AI Contributions (`GEMSDOE89`)

1. **Parent Verification & Exact Rebuild (`gemsdoe/parent.py`, `tools/rebuild_r0.py`):**
   - Verified SHA-256 hashes of all pinned inputs in `registry/data_manifest.json`.
   - Rebuilt parent R0 (`h33-h33-2-b2`, 37,654 unit-mass dots) bit-for-bit from `scored_h19_5.tif` (`dot_thin(r=2.8)` + `d_cat > 2.0` prune on `sample_submission.tif` grid), matching both `c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9` (`-zeros.tif`) and `baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd` (`.tif`), plus independent ancestor subset verification (`h27_4_solo.tif`, `d28.tif`).
2. **Candidate Generation Across Orthogonal Axes (`gemsdoe/spacing.py`, `gemsdoe/relief.py`, `gemsdoe/mass.py`, `gemsdoe/snap.py`, `gemsdoe/concentration.py`):**
   - **`SNAP` session (merged 2026-10-23, branch `arena/7efbb7cc-gemsdoe89`):** built the gateless (`g0p00`) corner of the SNAP factorial — `1p0px` / `1p4px` / `2p0px` windows at fixed count (`n=37,654`), deterministic (no RNG), targets `d_cat >= 3.0 px`, with `tools/rebuild_r0.py` re-run as the start gate and an independent mask-to-byte rebuild check (`registry/build_report_snap_*.json`, mechanism cards in `ledger/MECHANISM_CARDS.md` Part III). Manifest pins were re-verified: three broken pins corrected and one marked UNVERIFIED (`IRREGULARITIES.md` items 1/8).
   - **`SPACING` session:** Designed and built 3 deterministic (`seed=20261023`), count-preserving (`n=37,654`) variants (`alongstrike`, `poisson`, `lattice`) on R0's 834 multi-dot fault strands (`>=6` dots), plus structural-geologist mechanism cards (`ledger/MECHANISM_CARDS.md`).
   - **Earlier `GEMSDOE89` sessions preserved in `releases/` and `ledger/submissions.csv`:** `RELIEF` (`r10`, `r15`, `r15s`) and drop-only `MASS` (`m10uniq`, `m10rand`, `m20uniq`, `ledger/MECHANISM_CARDS_MASS.md`).
3. **Validation, Canary & Report-Only Controls (`gemsdoe/validate.py`, `gemsdoe/proxy.py`, `tests/`):**
   - Verified all 36 GeoTIFFs in `releases/` (`6 SNAP + 6 SPACING + 6 RELIEF + 6 MASS + 12 CONCENTRATION`) against every MUST gate after re-reading from disk (`tools/validate_raster.py` + `tools/check_ledger.py` + 56 unit tests).
   - Computed 20-feature single-feature leakage canary (`max = 0.5688 <= 0.90`), catalogue hide-and-recover `PROXY` (`0.0384`, 95% CI `[0.0329, 0.0440]`), and lateral-jitter DTI `MODEL` curves. Earlier USGS SGMC numbers (`https://doi.org/10.3133/ds1052`) remain UNVERIFIED provenance and were not used for the 2 km family.
4. **Documentation & Slot Planning:**
   - Authored `SLOT_PLAN.md`, `README.md` (`CURRENT STATE`), `docs/SUBMIT.md`, `IRREGULARITIES.md`, and `ledger/submissions.csv` (the `SNAP` session merged the parallel `SPACING`/`MASS` sessions' outputs into one queue and wrote the integrated next-3 slot plan).
   - **Session-specific decisions the human can reverse (SNAP):** axis choice (SNAP gateless — MASS ±10 % and PRUNE ≤1/≤2/≤3 px were already built upstream, RELIEF/SPACING/MASS-drop were complete on `main`); the response recipe was replicated exactly from the upstream recorded recipe (bands 3 `tmi_hg` + 18 `iso_grav_anom_hg`) so a cross-session receipt comparison isolates only the gate; prediction bands use the upstream live-anchor inversion (`D = 18,734.44`) with an explicit negative side (−0.05/+0.05/+0.15 scenario) that upstream bands omitted — evidence class `MODEL`, never a score.

5. **`CONCENTRATION` session (2026-10-23, branch `arena/dda04afa-gemsdoe89`):**
   - Re-ran the full start gate in a clean sandbox (10/10 fetchable pins hash-verified after fixing a duplicate-pin fetch bug; R0 rebuilt byte-identical in 8.6 s), then chose the axis itself (the brief reserves it to the human; the user directed the agent not to ask, so the choice is logged here as reversible).
   - Added `gemsdoe/concentration.py` (+ `tests/test_concentration.py`, 11 tests) and `tools/build_concentration.py`, building three count-preserving 5 km block-reallocation arms on an **independent** prior (catalogued-fault density) with a single shared placement rule on the R2P-magnetic / isostatic-gravity Sobel gradient: `cat10`, `cat20`, `cat10away` (sign control). Measured the axis's headroom first (R0 block density vs catalogue density `r = 0.039`; 37.9 % of mass in zero-catalogue blocks) and recorded the brief's CV-band ambiguity in `IRREGULARITIES.md` item 9.
   - Fixed three tooling defects that would have silently corrupted the record (`tools/build_mass.py`'s dead `session_gate` read, `tools/build_ledger.py` dropping the SNAP axis on rebuild, `tools/fetch_pinned_data.py` collapsing duplicate pins) — items 10-11.
   - **What the human decides, not the agent:** whether slot 1 is `cat10` rather than the previous queue head (`relief-r10`); whether to spend a slot on the sign-control arm at all; `TOP_PUBLIC`; slots used; the deadline; and whether the known-fault prior is acceptable at all given item 9's sibling concern about the truth being a *new-fault* inventory (the agent's reading: it is the only released fault data and the organizers state new faults include newly mapped geometry of existing systems, so it is admissible but must be falsified by the away arm).

6. **Independent 2 km `CONCENTRATION` session and merge integration (2026-10-23, branch `arena/0a75dd63-gemsdoe89`):**
   - Built nested 10% / 15% / 20% transfers from bottom-half to top-third catalogue-prior blocks, with all additions on H19-5 and destinations ranked by exact sequential DTI marginals. AI wrote the brute-force tests, release driver, predictions, and `ledger/MECHANISM_CARDS_CONCENTRATION.md`. A dry run exposed addition-on-addition redundancy, so independent ranks were replaced by exact lazy greedy selection before any release.
   - After PR #12 merged the separate 5 km family, AI preserved both APIs and all six experiments: `tools/build_concentration.py` remains the 5 km driver, `tools/build_concentration_2km.py` is the H19 driver, and `predicted_delta_h19` avoids a naming collision. No raster bytes changed during integration. `tools/build_ledger.py` now regenerates both families (18 GEMSDOE89 rows, 133 total).
   - **Human decision preserved:** the 5 km `cat10` arm stays queue head on its stronger central MODEL and matched away control. The 2 km arms are held as a different H19/placement mechanism, not a clean scale-only ablation; the human decides whether they ever merit a slot.

## Guardrails Enforced

- Zero automated access to `drivendata.org` or `dropbox.com`; zero submissions executed; zero credentials accessed or stored.
- Zero competition input rasters committed to git or `releases/`.
- Strict separation of `RECEIPT`, `CLAIM`, `PROXY`, and `MODEL` labels throughout code, ledger, and documentation.
