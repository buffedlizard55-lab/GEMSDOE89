# IRREGULARITIES — session GEMSDOE89

Only items that change an engineering, experimental, or compliance decision.

## 1. Parent R0 is now rebuilt bit-for-bit from `scored_h19_5.tif`, while `scored_h19_5.tif` itself remains a pinned upstream artifact

- **Finding.** In PR #2 (`arena/3e9736cf-gemsdoe89`), parent R0 (`h33-h33-2-b2`) was
  verified by SHA-256 download only. In this session, `tools/rebuild_r0.py` (`gemsdoe/parent.py`)
  rebuilds `d28` (44,090 dots) from pinned `scored_h19_5.tif` (`ec1f9b56…`) via exact BFS
  `dot_thin(r_min=2.8)` and applies the `d_cat > 2.0 px` flank prune to reproduce R0
  (37,654 dots), matching **both** upstream GeoTIFF digests byte-for-byte
  (`c55bafc4…` zeros and `baeae321…` NaN; see `registry/parent_verification.json`).
- **Decision impact (reproducibility rule, https://docs.nlr.gov/docs/fy26osti/96647.pdf).**
  The step `scored_h19_5 -> d28 -> R0 -> variants` is 100 % script-reproduced here,
  but if a Phase-1/2 winner audit requires regenerating `scored_h19_5.tif` itself from
  raw `training_features.tif`, the `19GEMSDOE` ridge-extraction script must also be
  bundled in the final prize archive.

## 2. Hard Constraint 4 (`>= 3 px` from catalogue) conflicts with R0's inherited `2 < d_cat < 3 px` ring

- **Finding.** R0's own rule was `d_cat > 2.0 px`, leaving **1,611 dots at `2.236–2.828 px`**
  (`2 < d_cat < 3 px`) and 560 dots at `d_cat == 3.0 px` (`2,171` at `<= 3.0 px`).
- **Decision.** Both `SPACING` and `RELIEF` **freeze** R0's 1,611 inherited `< 3.0 px`
  dots and enforce `d_cat >= 3.00 px` on 100 % of relocated/added dots (verified minimum
  `3.00 px` across all 6 variants). Deleting the inherited `< 3.0 px` ring inside a
  `SPACING` or `RELIEF` build would inject a simultaneous `PRUNE` edit (already tested
  7 times in `ledger/submissions.csv`) and break single-variable attribution.

## 3. `sample_submission.tif` contains 60,988 positive pixels on the fault catalogue

- **Finding.** Despite problem-page wording describing an empty/fault-free template,
  `sample_submission.tif` (`2176d08e…`) has 60,988 pixels equal to `1.0` sitting directly
  on `existing_faults.tif`.
- **Decision.** `sample_submission.tif` is read **strictly** for grid tags and the finite
  footprint mask (`5,167,373` px), never as pixel values or training/exclusion labels.

## 4. Competition rasters are hosted in public sibling GitHub repositories

- **Finding.** Upstream sibling repos (`buffedlizard55-lab/GEMSDOE`, `GEMSDOE24`,
  `GEMSDOE32`) expose mirrors of `training_features.tif`, `sample_submission.tif`, and
  `existing_faults.tif` publicly; competition data-redistribution terms are unchecked.
- **Decision.** This repository commits **zero** competition input rasters (`data/` is
  git-ignored; `tools/fetch_pinned_data.py` fetches into local `data/` and verifies
  SHA-256). The human must decide whether to make those upstream mirror repositories
  private.

## 5. Missing human-only parameters (`TOP_PUBLIC`, slot counts, deadline check, live receipts)

- **Finding.** `TOP_PUBLIC` and remaining weekly/total slots are `____` in the brief, and
  automated access to `drivendata.org` is prohibited by its Terms of Use
  (https://www.drivendata.org/termsofuse/). All historical scores in `ledger/submissions.csv`
  lack submission-page receipts in this repo and are therefore marked `CLAIM`.
- **Decision.** Left as explicit placeholders in `README.md` and `SLOT_PLAN.md`, with
  `2026-12-03` flagged `UNVERIFIED` until the human confirms it on the competition page.

## 6. Opposite signs between the off-catalogue SGMC `PROXY` and centerline-jitter `MODEL` on lateral corridor arms

- **Finding.** On `SPACING`, catalogue hide-and-recover (`0.038424` recall) is invariant
  because `< 3 px` collar dots and `< 6`-dot strands are frozen while relocated dots obey
  `d_cat >= 3.0 px`. Meanwhile, off-catalogue USGS SGMC faults
  (https://doi.org/10.3133/ds1052, `d_cat > 3.0 px`) show *higher* coverage for
  `poisson` (`0.09016`) and `lattice` (`0.08928`) than `R0` (`0.08882`), whereas
  centerline-jitter `MODEL` sensitivity (`σ_⊥ <= 1.5 px` around `h19_5`) shows losses of
  `−0.008` to `−0.040` DTI because shifting dots `1–1.5 px` off a 1-px ridge sacrifices
  `33–50 %` of peak triangular-kernel height.
- **Decision.** SGMC cartographic offsets (`200–500 m` at compilation scale) were **not**
  allowed to flip the predicted sign: `poisson` (`−0.010`) and `lattice` (`−0.007`) carry
  negative central `MODEL` predictions, and `alongstrike` (`+0.002`, zero cross-strike
  loss) is ranked ahead of both in `SLOT_PLAN.md`.

## 7. Block-density CV scale depends strongly on block size (`1 km` vs `5 km`)

- **Finding.** The brief notes `0.51–0.59` block-density CV for top files. On `1 km × 1 km`
  blocks (`10×10 px`, ~0.73 dots/block), Poisson shot noise puts R0 at **1.8704**; on
  `5 km × 5 km` blocks (`50×50 px`), R0 sits at **0.8991** (matching upstream GEMSDOE84's
  5 km scale).
- **Decision.** Both `1 km` and `5 km` block-density CVs are recorded in every
  `SPACING` build report to prove spatial-concentration invariance (`0.8991 -> 0.8984..0.9001`),
  and neither is used as a tuning target or gate.
