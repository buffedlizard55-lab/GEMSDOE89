# IRREGULARITIES — session GEMSDOE89

Only items that change a decision. Each entry records what was found, what was
decided, and what the human may need to overrule.

## 1. Parent R0 rebuilt byte-exact from its recorded `GEMSDOE32` step; earlier ancestors are pinned rasters

`tools/rebuild_r0.py` verifies all 8 SHA-256 pins in `registry/data_manifest.json`
and rebuilds R0 (`h33-h33-2-b2`, 37,654 unit-mass dots) from its recorded
upstream step (`mask = base & (distance_transform_edt(~catalogue) > 2.0) & footprint & ~catalogue`
applied to `parent_base_02708.tif`), matching **both** pinned R0 digests byte-for-byte
(`c55bafc470054e82…` for `-zeros` and `baeae3219bba6a19…` for `-nan`).

**Remaining provenance scope (rules reproducibility clause, https://docs.nlr.gov/docs/fy26osti/96647.pdf).**
`parent_base_02708.tif` (`GEMSDOE28`) and `scored_h19_5.tif` (`19GEMSDOE`) are
consumed as SHA-256-pinned raster artifacts here; if Phase 1/2 code review
requires end-to-end training code back to raw `training_features.tif` for the
`19GEMSDOE` ancestor, the human must bundle the `19GEMSDOE` / `GEMSDOE28` build
scripts alongside this repository.

## 2. Hard constraint 4 (≥ 3 px from the catalogue) conflicts with the parent's own collar

The brief requires ≥ 3 px from catalogue pixels unless the axis is PRUNE. Parent
R0 has **1,611 dots at `2 < d_cat < 3` px** (minimum 2.236 px = √5) and 2,171 at
≤ 3 px, because R0's defining rule was `d_cat > 2 px`.

**Decision.** Both SPACING and RELIEF variants **inherit** R0's 1,611 diagonal-collar
dots untouched and enforce `d_cat >= 3.0 px` strictly on **100 % of newly placed /
re-spaced dots** (measured min added clearance = 3.00 px). Pruning those 1,611
inherited dots simultaneously would inject a second change (`PRUNE d_cat>=3px`,
already built upstream in `GEMSDOE84`) and break single-variable control.

**Overrule path.** If strict global `d_cat >= 3.0 px` is desired, combine the
winning single-axis variant with `PRUNE d_cat>=3px` in Weeks 3–4 as an explicit
two-factor arm.

## 3. `sample_submission.tif` is not fault-free

60,988 of its pixels equal `1.0` and sit directly on the `existing_faults.tif`
catalogue, despite template wording suggesting fault absence.

**Decision.** `sample_submission.tif` is used **only** for grid tags and the
`np.isfinite` footprint mask, never as pixel content.

## 4. Competition rasters are already exposed in public GitHub repositories

Upstream sibling repositories (`GEMSDOE`, `GEMSDOE24`, etc.) host mirrors of the
competition feature stack, template, and fault mask as public git blobs.

**Decision.** `GEMSDOE89` commits **zero** competition inputs: `tools/fetch_pinned_inputs.py`
downloads verified bytes into `./data/` (git-ignored). `releases/` holds only
derived candidate dot rasters (~3.6 MB total).

**Action for the human.** Verify DrivenData data-use terms and decide whether
the pre-existing public mirrors in earlier repos should be made private.

## 5. Missing human-only fields (`TOP_PUBLIC`, quota used, deadline confirmation)

`TOP_PUBLIC` (with date) and weekly/total slots remaining are `____` in the
brief, and `drivendata.org` cannot be fetched automatically under its terms of
use (`https://www.drivendata.org/termsofuse/`). Placeholders remain in
`README.md` and `SLOT_PLAN.md`; the human must also confirm the **2026-12-03**
deadline on the competition page.

## 6. Block-density CV depends strongly on block size (1 km vs 5 km)

The brief cites 0.51–0.59 block-density CV for top files without stating block
width. On R0, 1 km × 1 km blocks give CV = **1.870** (dominated by ~0.73
dots/block Poisson discreteness), whereas 5 km × 5 km blocks give CV = **0.899**.

**Decision.** Both 1-km and 5-km block-density CVs are reported before/after for
every SPACING variant (`registry/report_only_status.json`), and neither is used
as a tuning target or gate.

## 7. Local proxies are blind or weakly aligned on `d_cat >= 3 px` edits

Because every newly placed dot satisfies `d_cat >= 3.0 px` (`R = 3.0 px`),
catalogue `hide_and_recover` cannot credit any added dot: it stays identically
`0.0384` across R0 and all three SPACING arms (`d_cat < 3.0` dots locked) and
drops mechanically on RELIEF (`0.0356 / 0.0348 / 0.0341`). Off-catalogue USGS
SGMC bedrock faults (`https://doi.org/10.3133/ds1052`, `n = 63,121` px) are now
evaluated as a REPORT-ONLY sanity check (`0.2003–0.2015` 3-px recall vs `0.1764`
random null), never as a gate or predicted live change.
