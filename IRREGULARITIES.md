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

## 8. The SPACING axis as specified presumes a field with free spacing; R0 has none

The brief defines SPACING as "lattice vs Poisson-disk vs along-strike at matched
count". Measured on the pinned parent, R0 is already a hard-disk field: the
minimum dot-to-dot distance is **2.828 px** (√8, the (2,2) diagonal), 11,415 dots
(30.3 %) sit at exactly that distance, the median nearest-neighbour distance is
3.0 px, and no pair is closer. (The 1,611 dots "at 2.236 px" in item 2 are the
catalogue clearance ring — a different quantity; this item's numbers are
dot-to-dot.)

**Consequence.** A lattice or a freshly sampled Poisson field at 37,654 dots
would move essentially every dot — far outside the brief's 1–50 % change
constraint — and would also destroy the single-variable control. The axis only
has room to *coarsen* an already-saturated disk.

**Decision.** Three arms were built instead, all at exactly 37,654 dots:
hard-disk relaxation at 3.0 px (14.4 % of dots moved), at 4.0 px (36.5 %), and
along the local strike at 3.0 px (13.7 %). The dose arms answer "does
kernel-coverage area convert to T at fixed mass"; the along-strike arm answers
the geometry question the brief's lattice arm would have answered less cleanly.
The lattice arm is **not built and should not be built**: it is not available
inside the constraint.

**Overrule path.** If a lattice arm is required anyway, it must be registered as
a > 50 % change and the brief's constraint waived explicitly for that file.

### Correction to item 8 (same day, after rebasing my view onto `main`)

`main` now carries a SPACING `lattice` arm
(`h33-h33-2-b2-spacing-lattice-20261023-454c9098`) that moves 7,305 dots
(19.4 %) by snapping to an isometric hexagonal lattice inside a ±200 m corridor.
So the lattice construction **is** available inside the 1–50 % constraint; what
is not available is a *global* lattice or a *global* re-sampled Poisson field.
Item 8's conclusion (build dose + geometry arms rather than a global rebuild)
stands; its claim that a lattice arm cannot be built is wrong and is withdrawn.

## 9. A parallel session already built the SPACING axis on the same parent

At branch time (commit 5875e05) the recovered ledger had no `(SPACING, value)`
pair, which is why this session chose SPACING. `main` has since advanced to
3bededd and now contains three SPACING arms built on the same parent R0:

| main arm | dots moved | mean displacement |
|---|---|---|
| `spacing-poisson-…-ff167173` (2D Bridson Poisson-disk) | 7,639 (20.3 %) | 1.53 px |
| `spacing-lattice-…-454c9098` (hex lattice, 3.5 px pitch) | 7,305 (19.4 %) | 1.54 px |
| `spacing-alongstrike-…-3b263c7a` | 5,222 (13.9 %) | 1.17 px |

**What this means for this session's files.** My `hd3p0` / `hd4p0` / `hd3p0-along`
arm names do not collide on the `(parent, axis, value)` key, so the dedupe rule
as written does not catch them — but in substance `hd3p0`/`hd4p0` are a
hard-disk Poisson relaxation and `hd3p0-along` is an along-strike relaxation,
i.e. the same two experiments as main's `poisson` and `alongstrike`, at
different doses (14.4 % / 36.5 % / 13.7 % versus 20.3 % / 13.9 %).

**Decision.** These three files are labelled BUILT and remain valid, gate-passing
rasters, but they are **not independent evidence** and must not be spent as if
they were: submitting one of mine after one of main's tests the dose, not the
axis. If the human submits from this session at all, the only genuinely additive
question is the **dose contrast** (`hd3p0` 14.4 % vs `hd4p0` 36.5 %) against
main's 20.3 % poisson arm.

**Overrule path.** If the human prefers one lineage, the cheapest defensible
choice is to submit the collision-free half of this set once and delete the
rest — I did not delete files or rows, because that decision is the human's and
the files are cheap to keep.
