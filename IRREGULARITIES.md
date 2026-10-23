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

## 7. The catalogue proxy is structurally blind to this axis

Every added dot is ≥ 3 px from every catalogue pixel by construction, so the
hide-and-recover proxy can only register the removal half of a RELIEF move. Its
deltas (0.0384 → 0.0356 / 0.0348 / 0.0341) are an artefact of that blindness.

**Decision.** The proxy is reported and is **not** used to set the predicted
sign. Doing so would have flipped the sign of every variant for a reason that
has nothing to do with the live score.

## 8. SPACING session (2026-10-23): proxy blindness extends, and two alignment
## statistics disagree by construction

Two measurement quirks change how the SPACING results must be read.

**8a. The proxy is blind to SPACING for the same reason as item 7.** Every new
pixel is at d_cat ≥ 3 px, so its catalogue kernel credit is exactly zero; the
hide-and-recover deltas (0.0384 → 0.0326 / 0.0323 / 0.0232) register removals
only. **Decision:** report in `registry/report_only_status.json`, never use to
set a predicted sign.

**8b. Global vs local strike alignment move in opposite directions for
`strike3`.** The global nearest-neighbour statistic falls (0.7666 → 0.6728)
while the controlled mover–anchor statistic rises (0.7636 → 0.9440). They do
not contradict: a moved dot's nearest neighbour after the hop is often a
different dot, so global NN identities re-wire. **Decision:** the arm is
evaluated on the local statistic it actually controls; the global one is
reported for completeness. A live result must not be interpreted through the
global number alone.

## 9. A first SPACING build created 1 px pairs; it was discarded before logging

The first implementation measured nearest-occupied distance on a raster patch
that ended exactly at the displacement-window edge, so an anchor one pixel
outside the window was invisible; movers landed 1.0 px from neighbours — far
inside the parent's 2.828 px suppression floor. Those files were deleted, the
EDT is now computed on a margin-extended patch with a conservative padded
border, and every arm enforces the parent's 2.828 px minimum separation as an
acceptance floor (unit-tested, including a non-vacuous "the arm must move at
least one dot" guard, because the broken build had passed the original tests
by moving nothing). **Decision:** only the corrected builds (sha8 `59029fa7`,
`6b481dc1`, `0dbab41e`) exist in `releases/` and the ledger; no gate-failed
artifact is retained.
