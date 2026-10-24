# IRREGULARITIES (Decision-Changing Only)

Only items that alter candidate validity, metric interpretation, governance, or slot allocation are listed here.

1. **Parent R0 (`0.2778`) Is a `CLAIM`, Not a `RECEIPT` in This Repo.**
   - *Fact:* `h33-h33-2-b2` (`c55bafc4...` / `baeae321...`) is rebuilt bit-for-bit (`0` pixel diffs across all `12,279,160` grid cells) from pinned `scored_h19_5.tif` + `existing_faults.tif` + `sample_submission.tif`, so parent *geometry* is 100% verified. However, its `0.2778` live number carries `evidence_class = CLAIM` (no organizer receipt is stored in this repo).
   - *Decision impact:* Every predicted live change (`MODEL`) is anchored to `0.2778` only up to `CLAIM` accuracy; if Slot 1 lands far from `0.2778`, parent baseline uncertainty (`CLAIM` vs `RECEIPT`) must be checked before attributing the gap to a single axis.

2. **Public Bridge Mirrors Host Competition Rasters (`GEMSDOE`, `GEMSDOE24`, `GEMSDOE86`, `GEMSDOE92`).**
   - *Fact:* Input rasters pinned in `registry/data_manifest.json` were fetched from public GitHub repos under `buffedlizard55-lab/*`. DrivenData rules restrict redistributing challenge data publicly.
   - *Decision impact:* `GEMSDOE89` keeps `data/` and `.cache/` strictly git-ignored (zero competition rasters committed to git or `releases/`), and the human team owner should review visibility/licensing of upstream mirror repos before prize audit.

3. **`training_features.tif` Contains `-3.4e38` Float32 Sentinels Inside the Footprint (`IR-DEC-17`) and Has `5,164,312` Complete Pixels (Not `9,108,339`).**
   - *Fact:* `sample_submission.tif` has `5,167,373` finite footprint pixels (`42.1%` of `3730×3292`), while `registry/data_manifest.json`'s prose note on `training_features` mistakenly cites `9,108,339`. Inside the `5,167,373`-px footprint, bands 1–8 and 18 store `-3.4028235e38` float32 sentinels where `np.isfinite()` is `True` (leaving `5,164,312` elevation pixels after masking `<= -1e30`).
   - *Decision impact:* Every feature reader (`gemsdoe/concentration.py`, `tools/build_concentration.py`, `gemsdoe/relief.py`, `gemsdoe/snap.py`) masks `band <= -1e30` to `NaN` before smoothing or quantile normalization, and block footprint fractions are computed strictly against `np.isfinite(sample_submission.tif)` (`5,167,373` px).

4. **Pixel-Withheld Catalogue Hide-and-Recover `PROXY` Is Structurally Blind to `d_cat >= 3 px` Edits (`0.038424` Invariant).**
   - *Fact:* Because R0 has `1,611` inherited collar dots at `2.0 < d_cat < 3.0 px` and new variant dots obey `d_cat >= 3.0 px` (the exact `300 m` / `3 px` DTI kernel radius), freezing the `< 3 px` collar leaves pixel-withheld `existing_faults.tif` recall (`PROXY`) invariant at `0.038424` (`95% CI [0.03285, 0.043997]`) across both `SPACING` and `CONCENTRATION`.
   - *Decision impact:* Never rank or gate `d_cat >= 3 px` edits by pixel-withheld catalogue `PROXY`. `tools/build_concentration.py` instead calibrates `MODEL` deltas on **25% connected-strand holdouts** withheld *before* computing `d_cat`, R0, or the block prior, paired with a matched **random-block-shuffle control** (`+0.0052` to `+0.0136` pure block-prior lift).

5. **Unconstrained Block Concentration Suffers Top-Block Hoarding and Circular-Cone Mimics (`CV_12.8km > 0.73`).**
   - *Fact:* Ranking target-tercile candidates globally without per-block quotas lets ~10 steep volcanic range blocks hoard hundreds of dots, spiking `CV_12.8km` from `0.5532` to `0.73–0.83` (far outside the `0.51–0.59` lineage band) and degrading held-out strand DTI on `geodetic` transfers (`−0.0035` to `−0.0062`).
   - *Decision impact:* `gemsdoe/concentration.py` enforces **proportional per-block removal/addition quotas** (`q_split = 40/60`) plus **600 m structure-tensor strike coherence** (`coh_elev`), holding `12p8km-int10`'s `CV_12.8km` at `0.5533` inside `[0.51, 0.59]` while letting `12p8km-int20` (`0.6561`) cleanly test controlled saturation above `0.59`.

6. **`SPACING` 2D Lateral Arms (`poisson`, `lattice`) Trade Ridge Alignment for Packing Clearance.**
   - *Fact:* On R0's 834 active strands, reducing `<3 px` neighbor pairs by `29%–33%` forces ~`79%–85%` of moved dots `1–2 px` off the 1-px `h19_5` skeleton (`MODEL` `−0.010` and `−0.007`).
   - *Decision impact:* `poisson` and `lattice` remain held unless `alongstrike` (`MODEL` `+0.002`) scores `>= +0.010`.

7. **Upstream Repeat Submissions Lack Verified Receipts and `scored_h19_5.tif` Is Binary (`{0, 1}`).**
   - *Fact:* Upstream `GEMSDOE32` / `GEMSDOE49` / `GEMSDOE55` rows are `CLAIM`s without organizer receipts in this repo, and `scored_h19_5.tif` stores binary `{0, 1}` (`121,131` px) rather than continuous probabilities.
   - *Decision impact:* Off-`h19_5` additions (`CONCENTRATION`, `RELIEF`) must synthesize continuous ridge rankings directly from `training_features.tif`, and any live delta `< 0.01` is treated as no evidence.

8. **Manifest Shared-Archive Extraction Bug Fixed; `sgmc_faults_control` Remains `UNVERIFIED`.**
   - *Fact:* Two pairs of `registry/data_manifest.json` pins (`scored_h19_5` / `parent_field_h19_5` and `scored_h27_4_solo` / `parent_ancestor_solo_d28`) share archive member paths inside `GEMSDOE92`, which caused `tools/fetch_pinned_data.py` to overwrite the first destination on clean fetches (`exit_code=2`); fixed via `build_wanted_map` multi-destination extraction and regression-tested in `tests/test_fetch_pinned_data.py`. Separately, `sgmc_faults_control` (`unverified: true`) points to a nonexistent `GEMSDOE84` ref and `data.usgs.gov` is unreachable in the sandbox.
   - *Decision impact:* All 10 fetchable pins verify cleanly on fresh runs; `SGMC` remains strictly skipped (`UNVERIFIED`, report-only) in `SNAP` and `CONCENTRATION` until the human supplies an official USGS DS-1052 raster (`https://doi.org/10.3133/ds1052`).

9. **Missing Human Operational Inputs (`TOP_PUBLIC`, Weekly Slots, Deadline Verification).**
   - *Fact:* `TOP_PUBLIC`, slots used this rolling week, and organizer confirmation of `2026-12-03` cannot be fetched without accessing `drivendata.org` (barred by ToS).
   - *Decision impact:* Explicit placeholders remain in `README.md` and `SLOT_PLAN.md` for the human to fill before uploading Slot 1.
