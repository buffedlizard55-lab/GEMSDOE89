# IRREGULARITIES (Decision-Changing Only)

Only items that alter candidate validity, metric interpretation, governance, or slot allocation are listed here.

1. **Parent R0 (`0.2778`) Is a `CLAIM`, Not a `RECEIPT` in This Repo.**
   - *Fact:* `h33-h33-2-b2` (`c55bafc4...` / `baeae321...`) is rebuilt bit-for-bit (`0` pixel diffs across all `12,279,160` grid cells) from pinned `scored_h19_5.tif` + `existing_faults.tif` + `sample_submission.tif`, so parent *geometry* is 100% verified. However, its `0.2778` live number carries `evidence_class = CLAIM` (no organizer receipt is stored in this repo).
   - *Decision impact:* Every predicted live change (`MODEL`) is anchored to `0.2778` only up to `CLAIM` accuracy; if Slot 1 lands far from `0.2778`, parent baseline uncertainty (`CLAIM` vs `RECEIPT`) must be checked before attributing the gap to `SPACING`, `RELIEF`, or `MASS`.

2. **Public Bridge Mirrors Host Competition Rasters (`GEMSDOE`, `GEMSDOE24`, `GEMSDOE86`, `GEMSDOE92`).**
   - *Fact:* Input rasters pinned in `registry/data_manifest.json` were fetched from public GitHub repos under `buffedlizard55-lab/*`. DrivenData rules normally restrict redistributing challenge data publicly.
   - *Decision impact:* `GEMSDOE89` keeps `data/` and `.cache/` strictly git-ignored (zero competition rasters committed to git or `releases/`), and the human team owner should review visibility/licensing of upstream mirror repos before prize audit.

3. **`training_features.tif` Contains `-3.4e38` Float32 Sentinels Inside the Footprint (`IR-DEC-17`).**
   - *Fact:* Bands 1–8 and 18 contain `-3.4028235e38` nodata sentinels inside `sample_submission.tif`'s valid footprint (e.g., `635,517` pixels in band 18 `iso_grav_anom_hg`), where `np.isfinite()` is `True`.
   - *Decision impact:* Any feature computation or leakage canary must mask `band <= -1e30` to `NaN` (`tools/build_spacing.py` enforces this; `SPACING` geometry itself uses only binary `scored_h19_5` and `existing_faults`).

4. **Catalogue Hide-and-Recover `PROXY` Is Structurally Blind to `>=3 px`-Collar Edits on Long Strands.**
   - *Fact:* Because R0 was pruned at `d_cat > 2.0 px` and new variant dots obey `d_cat >= 3.0 px` (the exact 3-pixel DTI kernel radius), moving dots on `>=6`-dot strands leaves DTI on held-out `existing_faults.tif` (`PROXY`) invariant to 6 decimals (`0.038424`, 95% CI `[0.03285, 0.043997]`).
   - *Decision impact:* Never rank or gate `SPACING` (or other `d_cat >= 3 px` collar-respecting edits) by catalogue hide-and-recover `PROXY`; use physical ridge-jitter sensitivity (`MODEL`) and off-catalogue USGS SGMC fault coverage (`PROXY`, `https://doi.org/10.3133/ds1052`) for diagnostic direction, and treat only live `RECEIPT` deltas `>= 0.01` as evidence.

5. **`SPACING` 2D Lateral Arms (`poisson`, `lattice`) Trade Ridge Alignment for Packing Clearance.**
   - *Fact:* On R0's 834 active strands, reducing `<3 px` neighbor pairs by `29%–33%` (`poisson` / `lattice`) forces ~`79%–85%` of moved dots `1–2 px` laterally off the 1-px `h19_5` skeleton, dropping active-strand 3-px ridge coverage from `0.710` to `0.513–0.558` (`MODEL` `-0.010` and `-0.007`).
   - *Decision impact:* Only `alongstrike` (`100%` ridge retention, `MODEL` `+0.002`) is eligible for Slot 1; `poisson` and `lattice` are held strictly conditional on `alongstrike` surprising positively (`>= +0.010`).

6. **Upstream `MASS` Repeat Submissions Show Non-Zero Score Spread or Unverified Claims.**
   - *Fact:* Upstream ledger entries for `h33-h33-2-b2` and `MASS` cousins (`GEMSDOE32` / `GEMSDOE49` / `GEMSDOE55`) are `CLAIM` rows without verified receipts in this repo, and `scored_h19_5.tif` is binary (`{0, 1}`, `121,131` pixels) with no continuous ranking stored in the parent raster.
   - *Decision impact:* Reinforces the brief's `< 0.01 = no evidence` threshold and prevents over-interpreting sub-`0.01` differences across `SPACING`, `MASS`, and `RELIEF`.

7. **Missing Human Operational Inputs (`TOP_PUBLIC`, Weekly Slots, Deadline Verification).**
   - *Fact:* `TOP_PUBLIC`, slots used this rolling week, and organizer confirmation of the `2026-12-03` deadline cannot be fetched without accessing `drivendata.org` (barred by ToS).
   - *Decision impact:* Slot pacing in `SLOT_PLAN.md` and `README.md` leaves explicit placeholders for the human to fill before uploading Slot 1.
