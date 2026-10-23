# IRREGULARITIES — session GEMSDOE89

Only items that change a decision. Each entry says what was found, what was
decided, and what the human may need to overrule.

## 1. The assigned repository was empty — the lineage was recovered, not rebuilt

`buffedlizard55-lab/GEMSDOE89` contained a single one-line `README.md`: no
manifest, no `ledger/`, no `SLOT_PLAN.md`, no parent raster, and no recipe.

**Decision.** The pinned inputs were recovered from the owner's earlier repos
(`GEMSDOE83/84/86/88`, `GEMSDOE24`, `GEMSDOE`) and every byte was verified
against the sha256 recorded in the upstream manifest and ledger. The parent R0
was restored from `GEMSDOE86 data/scored_fleet/GEMSDOE32__…-e5eb6e7e-zeros.tif`
and its sha256 equals `c55bafc4…`, the `sha256_zeros` recorded for
`h33-h33-2-b2` in `GEMSDOE84 ledger/submissions.csv`.

**Consequence (matters for the rules' reproducibility clause).** Parent identity
is exact at the artifact level, but this session did **not** re-derive R0 from a
script. If a reviewer asks for reproducible code *for the parent*, that code
still does not exist in this repo; every *variant* here is reproducible from
`tools/build_relief.py` + `registry/data_manifest.json`.

## 2. Hard constraint 4 (≥ 3 px from the catalogue) conflicts with the parent's own collar

The brief requires ≥ 3 px from catalogue pixels unless the axis is PRUNE. The
parent has **1,611 dots at 2.236 px** (the √5 diagonal ring) and 2,171 at
≤ 3 px — its own documented rule was "none within 2 px".

**Decision.** The variants **inherit** the parent's 2.236 px dots and enforce
≥ 3.0 px only on the *newly placed* dots (measured: minimum added-dot clearance
= 3.00 px). Removing the inherited ring would have been a second simultaneous
change (a PRUNE ≤3 px move, already built three times upstream) and would have
destroyed the single-variable control the brief asks for.

**Overrule path.** If strict ≥ 3 px compliance is mandatory, the correct
construction is a two-factor arm (RELIEF + collar top-up), which must be
registered as a new `(axis, value)` pair rather than folded into these files.

## 3. `sample_submission.tif` is not fault-free

60,988 of its pixels equal 1 and sit exactly on the catalogue, and its
`GDAL_NODATA` tag is `nan`. The problem page advertises a fault-free template.

**Decision.** The template is used **only** for grid geometry and the footprint
mask, never as content and never as a label source. Flagged because anyone
copying the template as a starting raster would be emitting catalogue mass.

## 4. Competition rasters are already exposed in public GitHub repositories

The owner's own repos host the competition feature stack (419 MB in 5 parts),
the template, and the USGS/INGENIOUS label raster as **public** blobs. The
brief says to keep competition rasters out of public repos and flags that the
data-use terms are unchecked.

**Decision.** This repo stores no competition input: everything is fetched to
`$GEMSDOE_DATA` (default `./data/`, git-ignored) and verified by sha256.
`releases/` contains only derived candidate rasters, matching the owner's
established pattern.

**Action for the human.** Decide whether the pre-existing public mirrors should
be taken private. This agent did not modify any other repository.

## 5. Two numbers the brief requires are blank and cannot be derived locally

`TOP_PUBLIC` (leaderboard, with date) and slots used/available are `____` in the
brief. The competition page cannot be fetched under its own terms (automated
access is banned), so the agent will not guess them; `README.md` and
`SLOT_PLAN.md` carry placeholders. **The 2026-12-03 deadline is likewise
UNVERIFIED** and must be confirmed on the competition page.

## 6. The quoted block-density CV benchmark is not reproducible from the data

The brief cites 0.51-0.59 CV for the best files (CONCENTRATION axis), and the
upstream GEMSDOE86 arm reports 0.62-0.76 for the same statistic. Measured here
on 1 km × 1 km blocks (density = dots / footprint px per block, blocks with
≥ 50 % footprint), R0's CV is **1.87** — a factor of three outside both figures,
because at ~0.73 dots per block Poisson noise alone gives ≈ 1.2.

**Decision.** The statistic is reported for every variant (before/after) but is
**not** used as a target or a gate, and no variant was tuned toward it.

## 7. The catalogue proxy is structurally blind to RELIEF and SPACING

Every added dot is ≥ 3 px from every catalogue pixel by construction, so the
hide-and-recover proxy can register only the removal half of these edits. Its
RELIEF deltas (0.0384 → 0.0356 / 0.0348 / 0.0341) are an artefact of that
blindness. All three SPACING arms instead have identical proxy and catalogue-
surrogate values because they share removals and their additions have zero
catalogue-kernel credit; those instruments cannot rank lattice/Poisson/strike.

**Decision.** The proxy is reported and is **not** used to set a predicted sign
or select an arm. Doing so would penalise variants for a reason that has nothing
to do with new-fault live credit.
