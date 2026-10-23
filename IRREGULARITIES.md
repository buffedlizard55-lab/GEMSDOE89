# IRREGULARITIES — session GEMSDOE89

Only items that change a decision. Each entry says what was found, what was
decided, and what the human may need to overrule.

## 1. The assigned repository was empty — the lineage was recovered, and R0's dot set is now reproducible

`buffedlizard55-lab/GEMSDOE89` contained a single one-line `README.md`: no
manifest, no `ledger/`, no `SLOT_PLAN.md`, no parent raster, and no recipe.

**Decision (earlier session).** Pinned inputs were recovered from the owner's
earlier repos (`GEMSDOE83/84/86/88/92`, `GEMSDOE24`, `GEMSDOE`) and every byte
verified against its recorded sha256.

**Update (2026-10-23, this session).** The parent's **dot set is rebuilt
cell-for-cell** from two independent pinned ancestors:
`solo-d2.8` (40,199 dots) and `d2.8` (44,090 dots), each minus every dot within
2.0 px of the catalogue, both give exactly R0's 37,654 dots with **0 differing
cells** (`tools/build_mass.py` asserts this on every run). What still cannot be
done is re-encoding the parent's *file bytes*: the same dot mask written through
`gemsdoe.grid.write_submission` gives `5d2b191f…` / 233,368 B instead of the
pinned `c55bafc4…` / 219,065 B, because the original writer's compression and
tile settings are not recorded. **Consequence:** the parent is referenced by
sha256, never regenerated; every variant here is reproducible from
`tools/build_mass.py` + `registry/data_manifest.json` + one seed.

## 2. Hard constraint 4 (≥ 3 px from the catalogue) conflicts with the parent's own collar

The brief requires ≥ 3 px from catalogue pixels unless the axis is PRUNE. The
parent has **1,611 dots within 3 px** of the catalogue — 941 at the √5 diagonal
(2.236 px) and 670 further out but still inside 3 px — and **2,171 at ≤ 3 px**
(the extra 560 sit exactly on 3.0 px). Its own documented rule was "none within
2 px".

**Decision.** Variants **inherit** the ring and enforce ≥ 3 px only on newly
placed dots. This session's arms are **drop-only**, so they can only reduce that
number (m10uniq removes 58 ring dots, m10rand 171, m20uniq 147; the remaining
minimum distance is still 2.236 px).

**Overrule path.** If strict ≥ 3 px is mandatory, the correct construction is a
two-factor arm (mass drop + collar top-up), registered as a new `(axis, value)`
pair rather than folded into these files.

## 3. `sample_submission.tif` is not fault-free

60,988 of its pixels equal 1 and sit exactly on the catalogue, and its
`GDAL_NODATA` tag is `nan`. The problem page advertises a fault-free template.

**Decision.** Used **only** for grid geometry and the footprint mask, never as
content and never as a label source.

## 4. Competition rasters are already exposed in public GitHub repositories

The owner's own repos host the competition feature stack (419 MB in 5 parts),
the template, and the USGS/INGENIOUS label raster as **public** blobs.

**Decision.** This repo stores no competition input: everything is fetched to
`$GEMSDOE_DATA` (default `./data/`, git-ignored) and verified by sha256.
`releases/` contains only derived candidate rasters.

**Action for the human.** Decide whether the pre-existing public mirrors should
be taken private. This agent did not modify any other repository.

## 5. Two numbers the brief requires are blank and cannot be derived locally

`TOP_PUBLIC` and slots used/available are `____` in the brief. The competition
page cannot be fetched under its own terms (automated access is banned), so the
agent will not guess them. The **2026-12-03 deadline is likewise UNVERIFIED**.
Note that the fleet ledger already contains self-recorded "best public" rows
(rank-1 `DARD` 0.3195 down to rank-19 0.2449), but those are the owner's own
notes of a leaderboard snapshot with **no date**, so they are not a valid
`TOP_PUBLIC`.

## 6. The quoted block-density CV benchmark is not reproducible from the data

The brief cites 0.51-0.59 CV for the best files (CONCENTRATION axis); upstream
GEMSDOE86 reports 0.62-0.76. Measured on R0 this session: **1.87** at 1 km
blocks, **1.24** at 2.5 km, **0.90** at 5 km, **0.64** at 10 km. At 2.5 km the
Poisson floor for R0's density is ≈0.47, so the benchmark, if it means 2.5 km,
describes a file that is almost exactly Poisson-uniform — which R0 is not.

**Decision.** Reported for every variant (before/after) but never used as a
target or a gate, and no variant was tuned toward it. This session's arms lower
the 2.5 km CV slightly (1.242 → 1.199 / 1.253 / 1.179); that is a side effect of
dropping clustered dots, not a design goal.

## 7. The catalogue proxy is structurally blind to this axis

The hide-and-recover proxy can only see dots near catalogue pixels. For RELIEF
every *added* dot is ≥ 3 px away by construction, so the proxy saw only half the
move. For MASS the blindness is worse: it sees the *dropped* dots but cannot see
their true credit, because that depends on new-fault truth the proxy does not
have.

**Decision.** The proxy is reported (m10uniq 0.0370, m10rand 0.0340,
m20uniq 0.0346, parent 0.0384, random null 0.0000) and is **never** used to set a
sign, a gate, or a slot order.

## 8. The parent's ranking does not exist — the MASS arm had to derive one

The brief defines MASS by "the parent's own ranking (rebuild it from the recorded
recipe if it is not stored)". **Neither exists.** There is no build script for
`h33-h33-2-b2`, and the ancestor the lineage thins from — `h19-5`, called a
"121k-px continuous field" in the brief — is **binary**: `{0, 1}`, 121,131 set
cells, verified by hash this session. It cannot rank anything.

The fleet shows the consequence: `GEMSDOE88`'s own ledger records its MASS
ranking as `0.6*clip(d_catalogue_px/50,0,1) + 0.4*uniform` with "89.4 % within
10 px of the catalogue", i.e. that arm is a collar/prune move, and the two MASS
rows in this repo's ledger are the same construction.

**Decision.** This session derives the ranking from the metric itself — the
expected *unique* kernel credit under a flat truth prior (`gemsdoe.mass`) — and
registers new pairs `(MASS, m10uniq / m10rand / m20uniq)`. `m10rand` is the
count-matched null, so the ranking can be judged rather than assumed.

**Overrule path.** If the human finds the original ranking artefact (a scored
field raster for this lineage), the honest move is to rebuild these three values
from it and record them as new pairs; the current files should then be retired.

## 9. The ranking's own statistic mis-predicts the one measured mass step by 0.025

Calibrating on solo-d2.8 → R0 (2,545 dots removed, **+0.0070** live): the
removed dots' unique credit `u` is **8.036** against a set mean of **7.667** —
*above* average. A credit-proportional model built on `u` therefore predicts
**−0.0175** for a step that gained +0.0070.

**Decision.** Every prediction in this session is a **wide band**, and the
mechanism cards say plainly that `u` is a proxy that failed its only calibration.
The arms are a falsification test of the count hypothesis, not a modelled gain.
The family's *arithmetic* ceiling (all dropped dots at zero credit, `D ≈ 0.2D`
calibrated from that same step) is +0.0105 for a 10 % drop and +0.021 for 20 %.

## 10. Fleet evidence says "far from the catalogue" scores better — confounded, but decision-changing

Across the 12 fleet rasters whose live scores can be matched to a file, the
mass-weighted mean distance to the catalogue correlates with live score at
Pearson **+0.94** / Spearman **+0.96**, and the fraction of mass within 10 px of
the catalogue at **−0.61** / **−0.64**. Six of those twelve are one lineage
(`h27-4-*` → `h33-*`), so the correlation is confounded by field, and n = 12 is
small. It is nevertheless the only cross-file evidence available.

**Decision.** It argues *against* building a CONCENTRATION arm toward the
catalogue prior (the obvious next-axis candidate), and it argues against the
RELIEF arms' assumption that the catalogue-dense piedmont is under-weighted.
`SLOT_PLAN.md` therefore proposes FLOOR-BY-MASS and DIP_ASYMMETRY instead, and
keeps the RELIEF files as alternates rather than favourites. It does **not**
justify over-weighting the MASS prediction: the arms drop dots across the whole
distance range, not preferentially near the catalogue.

## 11. Manifest verification is 6 / 7, and that is deliberate

`training_features.tif` (419 MB, 19 bands) was **not fetched** this session: a
drop-only MASS edit reads no band, computes no gradient, and needs no field. Its
absence is recorded as NOT FETCHED in `registry/data_manifest.json`
(`session_gate.required_ids` lists exactly the five files this axis reads, all of
which verified). The three ancestor rasters used for the parent identity proof
(`h27_4_solo`, `d28`, `h19_5`, from `GEMSDOE92@baefa4d6`) were added to the
manifest with their sha256 before use.
