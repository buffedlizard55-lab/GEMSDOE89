# Mechanism cards — session GEMSDOE89 (`SPACING` + `RELIEF` + `SNAP`)

Parent for every card: **R0 = `h33-h33-2-b2`** (`GEMSDOE32` lineage; 37,654 unit-mass
dots, zero on catalogue and zero at `d_cat <= 2.0 px`; rebuilt byte-identically from
`scored_h19_5.tif` via `tools/rebuild_r0.py`, matching `c55bafc4…` zeros and `baeae321…`
NaN; owner-reported live **0.2778 = CLAIM**, no submission receipt in this repo).

Written for a structural geologist. Every projection below is labelled **MODEL** and
every local holdout measurement is labelled **PROXY**; neither is a live score. Any
live public-leaderboard change with `|Δ| < 0.01` counts as **no evidence** (public
chunks cover only part of the region:
https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).

---

# Part I — `SPACING` axis (`alongstrike` · `poisson` · `lattice`)

## Physical and algebraic premise of the `SPACING` experiment

1. **How R0 actually spaces dots.** R0 is `dot_thin(h19_5, r_min=2.8) & (d_cat > 2.0)` on
   the 121,131-px `h19_5` corroborated ridge skeleton (99.9 % 1-px wide). `dot_thin`
   starts a breadth-first search at the **northernmost (`min y`) pixel** of each
   8-connected ridge component and greedily suppresses Euclidean radius `2.8 px`.
   Because `sqrt(2^2 + 2^2) = 2.828 > 2.8`, **11,415 of R0's 37,654 dots (30.3 %)** sit
   at `d = 2.828 px` — *inside* the `R = 300 m` (`3.0 px`) triangular DTI kernel
   (`k(d) = max(0, 1 - d/3)`:
   https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) — while
   leaving asymmetric uncovered remainders (`<= 2.8 px`) at southern and eastern fault
   terminations.
2. **Survey uncertainty vs centerline fidelity.** GeoDAWN Area 2 aeromagnetics and
   radiometrics were flown at **400 m line spacing, 150–200 m above terrain**, so
   potential-field lineament positions carry cross-strike uncertainty comparable to the
   300 m kernel radius
   (https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7).
   New-fault truth includes unmapped fault traces and newly mapped geometry of existing
   systems, with known USGS/INGENIOUS pixels masked pixel-exactly
   (https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516,
   https://community.drivendata.org/t/where-do-you-draw-the-line/11536).
3. **Strict single-variable isolation.** Spacing is only geometrically distinct on
   extended multi-dot strands. All three `SPACING` variants freeze R0's 29,413 dots on
   short (`< 6`-dot) fragments and the 1,611 inherited `2 < d_cat < 3 px` collar dots,
   and re-space only the **834 major fault strands** (`>= 6` R0 dots at `d_cat >= 3.0 px`,
   trace length `>= ~1.8 km`, holding **8,241 R0 dots = 21.89 %** of R0). Every strand
   keeps its **exact integer R0 dot budget `k_c`**, holding total count (`37,654`),
   5 km block-density CV (`0.8991 -> 0.8984..0.9001`), and elevation-tercile shares
   (`< 0.18 %` drift) invariant. At fixed mass `S = 37,654` (`ΔS = 0`),
   `ΔDTI ≈ ((1 - 0.2·DTI)·ΔT + 0.2·DTI·ΔM) / D ≈ (0.944·ΔT + 0.056·ΔM) / D`.

---

## Card S1 — `alongstrike` (`h33-h33-2-b2-spacing-alongstrike-20261023-3b263c7a`)

**Hypothesis.** Unmapped Quaternary and range-bounding fault segments captured by `h19_5`
lie within `<= 100 m` (`1 px`) of the `h19_5` ridge centerline, and R0 leaks kernel
credit at southern/eastern strand terminations and Y-splays because its row-major BFS
starts arbitrarily at northern component pixels. Equalizing stationing along strike on
the 1-px ridge skeleton increases truth kernel credit `T` at zero mass cost.

**Mechanism.** On each of the 834 major strands, graph-geodesic arc-length `s` is
computed between diameter endpoints, `k_c` stations are initialized at uniform geodesic
quantiles `(j + 0.5)·L / k_c` (preferring `r >= 3.0 px`, fallback `2.8 px`), and 1-swap
local search maximizes exact DTI kernel coverage `T` on the strand. Relocates **5,222
dots (13.87 %; symmetric diff 27.74 %)** by a mean of **1.17 px (117 m)** strictly along
`h19_5`, lifting mean kernel coverage on the 834 strands from **0.71014 to 0.71952**
(+280 kernel-credit units).

**The non-fault process that could mimic it.** Erosional ridge crests, tilted volcanic
flow margins, and linear tonal contacts also form continuous 1-px `h19_5` skeletons.
Uniform geodesic stationing distributes kernel height more evenly along *every* long
lineament, whether tectonic scarp or erosional hogback; if most `>= 1.8 km` unmasked
`h19_5` strands are lithologic/erosional strike ridges rather than faults, the extra
strand coverage earns zero truth credit (`ΔT ≈ 0`).

**Predicted sign and size (MODEL).** Central **+0.002**, band **−0.003 … +0.006**
(calibrated from off-catalogue strand jitter sensitivity: `+0.0017` at `σ_⊥ = 0 px`,
`−0.0006` at `σ_⊥ = 0.8 px`, `−0.0016` at `σ_⊥ = 2.2 px`). A **no-evidence outcome
(`|Δ| < 0.01`) is expected** because R0's BFS already captures `0.7101 / 0.7195 = 98.7 %`
of the along-strike optimum on those 834 strands.

**Falsifier.** A live change inside `±0.010` confirms that 1-D phase/termination defects
in `dot_thin(2.8)` cost less than 0.01 DTI and need no further slot expenditure. A gain
`>= +0.010` would imply test faults concentrate disproportionately at strand tips and
relay terminations where northern-root BFS left `2–3 px` overhangs.

---

## Card S2 — `poisson` (`h33-h33-2-b2-spacing-poisson-20261023-ff167173`)

**Hypothesis.** Because GeoDAWN Area 2 was flown at 400 m line spacing (150–200 m AGL)
and Basin-and-Range Quaternary fan scarps commonly step `100–300 m` basinward of the
steepest gravity/magnetic basement gradient, true unmapped fault traces are laterally
displaced from `h19_5` centerlines. Staggering each strand's `k_c` dots in a 2-D
Poisson-disk blue-noise arrangement across a `±150 m` (`d <= 1.5 px`) uncertainty
corridor widens cross-strike capture while eliminating `< 3.0 px` kernel crowding.

**Mechanism.** Within each active strand's Voronoi corridor (`d <= 1.5 px`, `d_cat >= 3.0 px`),
seeded Bridson/dart-throwing packing (`r_disk = 3.4 -> 3.2 -> 3.0 -> 2.8 px`, `seed = 20261023`)
relocates **7,639 dots (20.29 %; symmetric diff 40.57 %)** by a mean of **1.53 px (153 m)**.
Crowded `< 3.0 px` nearest-neighbour pairs drop from **11,415 to 8,119**, and coverage of
independent off-catalogue USGS SGMC faults (`d_cat > 3.0 px`,
https://doi.org/10.3133/ds1052) rises from **0.08882 to 0.09016** (**PROXY**), at the
direct cost of reducing on-centerline `h19_5` coverage from **0.71014 to 0.51347**.

**The non-fault process that could mimic it.** Alluvial-fan distributary channels,
shoreline terraces (Lake Lahontan), and pediment-fan contacts parallel range-front
lineaments at `100–300 m` offset; furthermore, SGMC 1:500k–1:250k compilation traces carry
cartographic generalization offsets of `200–500 m` that inflate off-ridge **PROXY**
overlap even when actual 100 m fault scarps sit directly on the topographic/geophysical
break.

**Predicted sign and size (MODEL).** Central **−0.010**, band **−0.032 … +0.004**.
Under `k(d) = 1 - d/3`, stepping `1–1.5 px` off a 1-px ridge costs `0.33–0.50` of peak
kernel height whenever true faults sit within `<= 1.5 px` of `h19_5` (`−0.022` at
`σ_⊥ = 0.8 px`, `−0.012` at `σ_⊥ = 1.5 px`, `−0.005` at `σ_⊥ = 2.2 px`); the sign turns
positive only if unmapped test faults sit systematically `>= 250 m` off `h19_5`.

**Falsifier.** A live score drop `<= −0.010` falsifies the wide-corridor uncertainty
hypothesis and proves `h19_5` pins test faults tighter than `~150 m` (validating narrow
ridge emission). Conversely, a live gain `>= +0.010` proves systematic cross-strike
offset between `h19_5` and unmapped test faults and opens 2-D corridor emission.

---

## Card S3 — `lattice` (`h33-h33-2-b2-spacing-lattice-20261023-454c9098`)

**Hypothesis.** For radial triangular kernels of radius `R = 3.0 px`, periodic
equilateral-triangular (hexagonal) disk packing maximizes minimum 2-D coverage per dot
(Kershner covering theorem). Sampling each active fault corridor (`d <= 2.0 px`) on an
isometric hexagonal lattice (`pitch a = 3.5 px`, row step `3.031 px`, staggered rows)
eliminates stochastic gaps left by random Poisson-disk dart throwing while maintaining
cross-strike corridor reach.

**Mechanism.** Candidate corridor pixels (`d <= 2.0 px`, `d_cat >= 3.0 px`) in each of
the 834 major strands are ranked by distance to the global hexagonal lattice (with minor
`0.15 × d_ridge` centerline tie-breaking and inter-dot separation `>= 3.0 -> 2.8 px`),
relocating **7,305 dots (19.40 %; symmetric diff 38.80 %)** by a mean of **1.54 px**.
Achieves the largest reduction in `< 3.0 px` pair crowding (**11,415 -> 7,667**),
retains higher centerline coverage than `poisson` (**0.55832** vs `0.51347`), and raises
off-catalogue SGMC coverage to **0.08928** (**PROXY**). Unlike `13GEMSDOE`
(`r13-lattice-s5`, live `0.0904` CLAIM), which placed a blind regional lattice across
the entire basin, this arm confines 100 % of mass to R0's exact fault corridors and
per-corridor dot budgets.

**The non-fault process that could mimic it.** A globally phase-fixed Cartesian/hexagonal
lattice beats or loses to strike-following chains depending on accidental alignment
between Great Basin NNE-striking (`010°–030°`) fault azimuths and the `0° / 60° / 120°`
hexagonal axes; an apparent difference vs `poisson` could reflect azimuth aliasing on
`060°` Humboldt-structural-zone segments rather than periodic covering optimality.

**Predicted sign and size (MODEL).** Central **−0.007**, band **−0.025 … +0.003**
(`−0.017` at `σ_⊥ = 0.8 px`, `−0.008` at `σ_⊥ = 1.5 px`, `−0.001` at `σ_⊥ = 2.2 px`).

**Falsifier.** Do not submit in the same week as `poisson`: both test lateral corridor
spreading. If `poisson` drops `<= −0.010`, `lattice` is retired without spending a slot.
If `poisson` gains `>= +0.010`, `lattice` tests whether periodic hexagonal covering adds a
further `>= +0.005` over stochastic blue-noise packing; otherwise periodic grid phase adds
nothing on curvilinear faults.

---

# Part II — Prior `RELIEF` axis cards (preserved from PR #2)

## The measurement the `RELIEF` axis rests on

Equal-area terciles of `det_elev` (band 12 of the pinned feature stack; cuts at
−142.9 m and +38.8 m), measured over the 5,164,312-px relief domain:

| class | name | area (px) | catalogue px | known-fault density /1000 px | R0 dots | R0 density /1000 px | R0 share ÷ catalogue share |
|---|---|---|---|---|---|---|---|
| 0 | basin | 1,721,438 | 18,499 | 10.75 | 7,692 | 4.47 | 0.67 |
| 1 | piedmont | 1,721,437 | 24,711 | **14.35** | 15,742 | 9.14 | 1.03 |
| 2 | range front | 1,721,437 | 17,684 | 10.27 | 14,204 | 8.25 | **1.30** |

At R0's claimed `0.2778`, an isolated dot must earn kernel credit `> 0.2 × DTI = 0.0556`
to pay for itself; every `RELIEF` variant writes added dots onto ground with
`|∇det_elev| >= 12.2` (50th percentile of parent dots).

## Card R1 — `r10` (`h33-h33-2-b2-relief-r10-20261023-366c87ca`)
- **Hypothesis:** Moving 10 % of R0 (3,765 dots) from over-weighted range-front (`class 2`) to structured piedmont ground (`class 1`) raises credit per unit mass.
- **Mechanism:** Quaternary basin-margin scarps are preserved and mappable in piedmont fans, whereas range-interior DEM edges frequently reflect bedrock fracture/contact grain.
- **Non-fault mimic:** Fan-head incisive channels, bar-and-swale roughness, or mapping-exposure bias in the piedmont catalogue prior.
- **Predicted sign and size (MODEL):** Central **+0.003**, band **−0.012 … +0.018**.
- **Falsifier:** Live delta inside `±0.010` closes `RELIEF`; `< −0.010` proves parent ridge placement outweighs class reallocation.

## Card R2 — `r15` (`h33-h33-2-b2-relief-r15-20261023-6aa774ce`)
- **Hypothesis:** 1.5× dose (`5,648` dots, 15 %) of `r10` along the same range-front → piedmont transfer.
- **Mechanism:** Linear dose-response check (`Δr15 ≈ 1.5 × Δr10`) conditional on `r10 >= +0.010`.
- **Non-fault mimic:** Stripping 15 % from range fronts may remove non-redundant range-bounding scarps nonlinearly.
- **Predicted sign and size (MODEL):** Central **+0.004**, band **−0.017 … +0.027**.
- **Falsifier:** Failure of `r15` to exceed `r10` when `r10 >= +0.010` falsifies linear class-allocation gain.

## Card R3 — `r15s` (`h33-h33-2-b2-relief-r15s-20261023-5f0ae851`)
- **Hypothesis:** Defining piedmont by `det_elev_slope` terciles (band 19; cuts `1.8` and `8.1`) and shifting 15 % (`5,648` dots) high-slope → mid-slope isolates slope transition from elevation band.
- **Mechanism:** Mid-slope fans carry 15.34 catalogue px / 1000 px vs 12.98 in high-slope (1.18× contrast).
- **Non-fault mimic:** Slope strongly covaries with DEM edge magnitude, risking a local placement confound (`mean disp = 49 px`).
- **Predicted sign and size (MODEL):** Central **+0.001**, band **−0.007 … +0.011**.
- **Falsifier:** Moving `>= +0.010` when `r10` is null points to slope-conditioned edge placement rather than geomorphic relief class.

---

# Part III — SNAP axis, gateless `g0p00` corner (`1p0px` · `1p4px` · `2p0px`) — session GEMSDOE89 (branch arena/7efbb7cc, 2026-10-23)

Parent for every card: **R0 = h33-h33-2-b2**, rebuilt byte-exactly this session
(`tools/rebuild_r0.py` reproduces sha256 `c55bafc4…` from the mask; 37,654 dots).
All three variants hold count, mass and the parent's exclusion rules fixed; only
*which pixel each dot sits on* may change, and only toward a strictly stronger
fused TMI/gravity edge response inside the window. Targets are ≥ 3.0 px off the
catalogue; the parent's inherited 2.236-px collar dots may stay or move out
(they never move closer) — collar count 1,611 → 938 / 666 / 575
(IRREGULARITIES item 2, single-variable control).

**Recipe note (why these are comparable across sessions).** The response is
replicated exactly from the upstream recorded SNAP recipe: bands 3 `tmi_hg` +
18 `iso_grav_anom_hg` (identities pinned via the manifest's
`band_identity_source` → GEMSDOE88 `registry/feature_receipt.json`), median
fill → gaussian σ = 1 px → `robust_unit` (1.0 = footprint 99.5th pct) →
pixel-wise max. Upstream built (1.42 px, gate 0.02), (2.0 px, 0.02),
(2.0 px, 0.01); these cards are **gate 0.00** at windows 1.0 / 1.42 / 2.0 —
so a receipt-vs-receipt comparison against the upstream arms isolates the
*gate* and nothing else. Gate 0.00 = the brief's literal “move each dot
≤ 2 px to the strongest response in its window” (any strictly stronger
pixel qualifies).

**What actually moved (measured):**

| value | window | dots moved (% of 37,654) | mean displacement | mean response gain | nn median before → after | CV 1 km before → after |
|---|---|---|---|---|---|---|
| 1p0px-g0p00 | 1.0 (4-nbr) | 30,434 (80.83 %) | 1.000 px | 0.0054 | 3.0 → 3.0 | 1.883 → 1.889 |
| 1p4px-g0p00 | 1.42 (8-nbr) | 31,233 (82.95 %) | 1.354 px | 0.0075 | 3.0 → 3.0 | 1.883 → 1.894 |
| 2p0px-g0p00 | 2.0 (12-nbr) | 31,287 (83.09 %) | 1.864 px | 0.0103 | 3.0 → 3.0 | 1.883 → 1.908 |

Window-dose **saturates**: 1.0 → 2.0 px adds only 853 moves. At gate 0 the
lever is the *gate*, not the window — which is what the cross-session
comparison against the gated arms prices.

**Shared prediction arithmetic (MODEL, not a score).** Pure position change ⇒
ΔDTI ≈ ΔT / D with D = 18,734.44, T = 5,073.29 from the recorded live-anchor
inversion (upstream `evidence/h33_validation.json`, live pair 0.2600 → 0.2708).
Scenario on moved dots: −0.05 … +0.15 *net* fraction close (or open) one full
pixel to their nearest truth pixel, kernel gain ⅓ each; central +0.05. The
negative side is priced because gateless moves are dominated by micro-gains on
smooth noise; the upper side inherits the coupling the upstream cards assumed
(they used +0.10 … +0.25 with no negative side). Everything under |Δ| = 0.01
is no evidence.

**Shared report-only counter-indicators (never gates, never called scores).**
Hide-and-recover PROXY recall falls 0.0384 → 0.0254 / 0.0181 / 0.0152
(n = 18,296 withheld, Wilson 95 % parent [0.033, 0.044] vs 2p0 variant
[0.012, 0.019]); catalogue-surrogate DTI falls 0.0067 → 0.0049 / 0.0033 /
0.0027. Reading: gateless snap trades *catalogue-adjacent* placement for
*crest-aligned* placement. Catalogue pixels are masked pixel-exactly in live
scoring, but new-fault truth may lie within 300 m of known traces (organizer
answer, brief §2), so catalogue adjacency partially proxies live truth. This
is the strongest reason the bands below carry a symmetric negative side. The
leakage canary PASSES (max single-feature AUC 0.665 vs threshold 0.90); the
SGMC control is not in the manifest (deferred, report-only).

---

## Card SN1 — `1p0px-g0p00` (window dose, low end)

**Hypothesis.** R0's dots are the output of a geometric BFS Poisson-disk walk
over the H19-5 lineament field; traversal order, not physics, picks the
surviving pixel, so many dots sit exactly 1 px off the geophysical edge that
nominated their lineament. A minimum decisive snap (4-neighbour disc) recovers
that off-by-one without letting any dot wander.

**Mechanism.** Each dot moves to the strictly strongest fused tmi_hg /
iso_grav_anom_hg pixel at distance ≤ 1 px (mean response gain 0.0054 robust
units), targets ≥ 3 px off the catalogue, one dot per pixel, deterministic.
Under the triangular kernel a 1 px correction on the dot nearest a truth pixel
recovers up to ⅓ of the credit available from that pixel.

**Non-fault mimic.** Fan-head channels, bar-and-swale and lithologic contacts
produce 1-px-scale horizontal-gradient maxima too; at 80.8 % moved, most moves
are micro-noise on a smooth surface — the arm can be a 30-thousand-dot random
walk dressed as a correction. Tie-line seams in the aeromagnetic survey add
structured false crests.

**Predicted sign and size (MODEL).** Central **+0.027**, band **−0.027 …
+0.081**. The band is the honest consequence of pricing the mimic: at gate 0
the coupling between EM-crest alignment and new-fault truth is the whole bet.

**Falsifier.** Live ≤ −0.010 falsifies the snap mechanism outright (crests R0
was pulled onto are non-fault contacts). Inside ±0.010 = no evidence; the
window-dose question then collapses to the cross-session *gate* comparison.
≥ +0.010 opens the family: compare against the gated arms' receipts
(1.42 px-g0p02 moved 6.4 %, 2.0 px-g0p01 moved 26.5 %) to see whether the
gate adds selection or just removes dose.

## Card SN2 — `1p4px-g0p00` (gate ablation at 1.42 px)

**Hypothesis.** Same as S1 with the 8-neighbour disc: the diagonal pixel is
often the true edge (a lineament at 45° to the grid), so window 1.42 should
beat window 1.0 *if* the correction mechanism is real. Compared with upstream
`1p4px-g0p02` (same window, same response, gate 0.02, 6.4 % moved) this arm
isolates the gate exactly.

**Mechanism.** Identical rule, offsets ≤ 1.42 px (adds the four diagonals);
31,233 moves, mean displacement 1.354 px, mean gain 0.0075.

**Non-fault mimic.** Identical to S1; the diagonals also double the chance of
landing on a fan/bedrock contact that runs obliquely through the window.

**Predicted sign and size (MODEL).** Central **+0.028**, band **−0.028 …
+0.083**.

**Falsifier.** Receipt ≈ the 1.42-g0p02 receipt (±0.010) ⇒ the gate does
nothing at this window and upstream's arms can be read as pure dose. Receipt
≥ 0.010 *below* the gated arm ⇒ the gate is filtering harmful noise, i.e.
selection matters more than dose — run windows at a *nonzero* gate next, not
more gate 0. Below −0.010 ⇒ SN1's falsifier fires for the whole family.

## Card SN3 — `2p0px-g0p00` (gate ablation at the physical window)

**Hypothesis.** GeoDAWN Area 2 was flown at ~400 m line spacing
(https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7), so
lineament positions are uncertain by about the 300 m kernel radius — the
physical correction scale is 2 px, not 1. This is the full-disc gateless arm
and the direct ablation of upstream `2p0px-g0p01` (26.5 % moved) and
`2p0px-g0p02` (11 %).

**Mechanism.** Identical rule, Euclidean disc ≤ 2.0 px (12 offsets); 31,287
moves (83.09 %), mean displacement 1.864 px, mean gain 0.0103 — the largest
response harvest of the three. Moved targets never come closer than 3.00 px
to the catalogue (measured); spacing statistics barely move (nn median 3.0 →
3.0, CV 1 km 1.883 → 1.908): this axis changes *position*, not *arrangement*.

**Non-fault mimic.** The wider disc reaches further off the mapped lineament
onto parallel unrelated gradients — buried paleo-topographic steps, Lahontan
shoreline breaks, pluton margins — and it is the arm with the most cumulative
micro-noise (83 % of all dots move). The falling catalogue PROXY (0.0384 →
0.0152) is this arm's own warning label: crest alignment and fault-proximity
placement are being traded against each other.

**Predicted sign and size (MODEL).** Central **+0.028**, band **−0.028 …
+0.084**.

**Falsifier.** ≥ +0.010 with a *tighter-band* gated receipt also positive ⇒
snap mechanism confirmed; then choose dose by receipt, not by principle.
≥ +0.010 while the gated arms' receipts are null ⇒ upstream over-gated (the
gate, not the snap, was destroying the gain). ≤ −0.010 ⇒ retire SNAP and the
EM-crest story with it: R0's lineament placement beats EM-crest placement and
the response surface should be rebuilt from DEM/lineament structure instead.
---

# Part IV — `CONCENTRATION` axis (`cat10` · `cat20` · `cat10away`)

## Premise: what the metric rewards, and what R0 does instead

`DTI = T / (0.2T + 0.2(S - M) + 0.8|G|)` (brief §2). The mass `S` is a penalty
in the denominator; a unit dot earns its place only through the kernel credit
`T` it adds on truth or the mass `M` it gets explained, and at the parent's
`0.2778` the break-even is `k > 0.0556`. Every one of R0's 37,654 dots costs
the same 0.2 of denominator; they differ only in where they sit.

**Measured on R0 (5 km blocks, edge-inclusive grid, 2,063 eligible blocks):**

| quantity | value |
|---|---|
| blocks containing catalogue pixels | 1,201 of 2,063 |
| blocks with **zero** catalogued fault | 862 (41.8 %) |
| R0 dots in those zero-fault blocks | **14,257 = 37.9 %** |
| R0 dots in the top-prior quartile (519 blocks) | 9,845 = 26.1 % |
| corr(R0 block density, catalogue block density) | **0.039** |

So block-scale allocation is essentially independent of where faults are known
to exist. That is the free parameter this axis spends.

**Why this is a new question, not a repeat.** `GEMSDOE84` spent
`5km-t25-move2400`, `5km-t50-move3765` and `spread5km-move2400` on this axis
using the *parent's own* per-dot gain surface, averaged per block, as the
prior. That surface is the one that placed R0's dots, so those arms moved mass
from blocks the parent already ranks low into blocks it already ranks high --
nearly a re-shuffle of a self-referential quantity (their own CV moves the
wrong way against the brief's band). The prior here is **independent**: the
density of catalogued (USGS/INGENIOUS) faults, the only fault data the
organizers release, and the data set that the truth is defined against
("new fault" = any fault pixel not already captured by USGS/INGENIOUS,
including newly mapped geometry of existing systems:
https://community.drivendata.org/t/where-do-you-draw-the-line/11536 ;
new-fault truth can lie within 300 m of known traces:
https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516).

## The placement rule (identical in all three arms)

R0 saturates its own field: only **201** `h19_5` pixels in the whole grid are
>= 2.8 px from an R0 dot *and* >= 3 px from the catalogue, so a
"same-field-same-rules" reallocation cannot be built above 201 dots. Added
dots are therefore placed on a structural edge score `q` = mean of the
Sobel gradient magnitudes of RTP magnetics (band 2) and isostatic gravity
(band 13), each robust-scaled, averaged, then smoothed with a 500 m box mean.
Candidates are ranked by `q` inside the recipient blocks and accepted greedily
at Euclidean spacing >= 2.8 px (the parent's own suppression radius).

What `q` is and is not (all MEASURED, all report-only): single-feature AUC
against catalogue membership **0.548** (the best single band in the stack is
0.572); 11.1 % of the top 1 % of `q` lies on or within 1 px of the corroborated
`h19_5` ridge field against a 7.2 % base rate; the top 1 % is spread over 484
of the 2,063 blocks (largest single-block share 3.0 %), so it is not a handful
of survey seams. R0's own dots sit at `q = 0.201` against a footprint mean of
0.180, while the added dots land at 0.49-0.70. **The added dots are on a
different structural class than R0's dots** -- that is the confound this axis
carries and it is why the sign-control arm exists.

---

## Card C1 — `cat10` (`h33-h33-2-b2-CONC5kmcat10-20261023-2dc19377`) — PRIMARY

**Hypothesis.** At 5 km scale, the density of *new* fault truth tracks the
density of *known* faults, so mass moved out of blocks with no catalogued
fault into the top-prior quartile earns more kernel credit than it gives up.

**Mechanism.** A 3,765-dot move (10.0 %; symmetric difference
20.0 %) at fixed count 37,654. Donors: all 862 zero-catalogue blocks, taking
the dots with the smallest unique kernel credit `u` (the parent's own
metric-derived redundancy ranking; removed mean `u = 6.27` vs parent 7.69).
Recipients: the 519 top-quartile blocks (cut 0.0184 catalogue px per footprint
px), filled on `q` at 2.8 px spacing, all new dots >= 3.0 px from the
catalogue (achieved minimum exactly 3.00 px). Zero-fault-block mass falls
14,257 -> 10,492; top-quartile mass rises 9,845 -> 13,610; 5 km density CV
0.901 -> 0.949 (1 km: 1.870 -> 1.905); corr(prior, density) 0.039 -> 0.269.
Mean displacement 128 px (12.8 km), so this is a block-scale move, not a snap.

**The non-fault process that could mimic it.** Catalogue density is a proxy
for *mapping effort*, not for fault density: well-surveyed corridors have both
more mapped faults and more published structure, so concentrating into them
reproduces the map's history rather than the geology. Second mimic: known
faults in this region include Mesozoic bedrock structures with no Quaternary
expression, and the truth is a *new-fault* inventory; a high catalogue-density
block can be systematically *old*-fault terrain. Third: the added dots sit on
potential-field gradients (AUC 0.548) that also mark lithological contacts,
volcanic margins and basin fill -- a strong-gradient "win" would be a
detector effect that the away arm shares, not a prior effect. Fourth: truth
pixels on the catalogue are masked, so a high-prior block has a larger
credit-dead ring (dots must sit >= 3 px away, and the mask removes the first
3 px of any trace); the true upside is smaller than raw fault density implies.

**Predicted sign and size (MODEL).** Central **+0.009**, band **-0.010 …
+0.038**. Derivation: with `S` fixed, `dDTI ~ n * k_bar * (p_recipient -
p_donor) / D`, `k_bar = 2.5` credit units for a unit dot on a 1-px trace,
`D = 2.0e4` measured from the lineage's own collar step (removing 2,545
masked-collar dots bought +0.0070 -> `D = 0.2778 * 509 / 0.0070`), and a hit-rate
difference of 2 percentage points. At 6 points it is +0.028; at 0 it is 0.
**The central case sits on the brief's no-evidence line**, so this arm only
reads out if the prior is real and strong.

**Falsifier.** A live change inside `±0.010` at 10 % *and* at 20 % means the
known-fault prior carries no usable block-scale signal; the axis closes and
`cat20`'s receipts become the bound on how much block allocation can be worth.
A live change <= -0.010 means the allocation actively hurts -- new faults
avoid known-fault corridors at 5 km scale -- and the away arm becomes the
candidate.

---

## Card C2 — `cat20` (`h33-h33-2-b2-CONC5kmcat20-20261023-4d229938`) — DOSE

**Hypothesis.** Same as C1; the dose asks whether the effect is monotone in
the moved count, which separates "allocation matters" from "10 % is inside the
noise of the public chunks".

**Mechanism.** Identical recipe at 20 %: 7,531 dots moved (symmetric
difference 40.0 %), donors the same 862 zero-catalogue blocks, same recipient
quartile, same `q` placement and the same 3.0 px clearance. Zero-fault-block
mass 14,257 -> 6,726; top-quartile mass 9,845 -> 17,376; 5 km CV 0.901 ->
1.132; corr(prior, density) 0.039 -> 0.404; mean displacement 108 px.

**The non-fault process that could mimic it.** Everything in C1, plus a
dose-specific one: at 20 % the arm removes almost a fifth of the parent's
dots from its own corroborated ridge field, so a null or negative result
cannot distinguish "prior is uninformative" from "the `q` placement is worse
than `h19_5`". Read the pair, never this arm alone.

**Predicted sign and size (MODEL).** Central **+0.019**, band **-0.010 …
+0.067** (2x the C1 arithmetic, same `D`, same `k_bar`, same 2-point hit-rate
difference; the width doubles with `n`).

**Falsifier.** If `cat20` lands within ±0.010 of R0 while `cat10` is also null,
block allocation is dead at this prior and this placement. If `cat20` lands
*below* `cat10 - 0.010`, the loss is coming from the placement (mass leaving
`h19_5`), not from the allocation, and the axis needs a placement fix before
another slot.

---

## Card C3 — `cat10away` (`h33-h33-2-b2-CONC5kmcat10away-20261023-f7b8aa28`) — SIGN CONTROL

**Hypothesis.** If the mechanism in C1 is the *prior*, then moving the same
number of dots with the same rule in the opposite direction must lose
approximately what C1 gains. If direction does not matter, the mechanism is
the placement or the mere act of moving mass, not the catalogue.

**Mechanism.** Exact mirror of C1: donors are the 519 top-quartile blocks
(same `u` ranking), recipients are the 862 zero-catalogue blocks, same `q`
placement, same spacing and clearance, same 3,765 dots. Zero-fault-block mass
rises 14,257 -> 18,022; corr(prior, density) falls 0.039 -> -0.165; 5 km CV
0.901 -> 1.049.

**The non-fault process that could mimic it.** Zero-catalogue blocks are not
fault-free; they are *unmapped* blocks, which in this region include the
basin interiors and the volcanic fields. If new-fault truth is frontier-heavy
(new traces drawn where nothing was mapped before), this arm is the winner and
the "known-fault prior" story is simply wrong.

**Predicted sign and size (MODEL).** Central **-0.009**, band **-0.038 …
+0.010** -- the exact negation of C1 under the same scenario.

**Falsifier.** A *gain* here (>= +0.010) falsifies the known-fault prior at
block scale and says the frontier is where the remaining truth is; that is a
decision-changing result worth one slot because it redirects every later arm.
A loss of the same size as C1's gain is the cleanest confirmation the axis can
give short of a receipt on the parent itself.

---

## Decision table for this axis (live changes are public-chunk only)

| cat10 | cat20 | cat10away | reading | next |
|---|---|---|---|---|
| >= +0.010 | >= +0.010 | <= 0 | known-fault prior works and scales | combine: raise the moved share or add a second, finer prior; keep `q` placement |
| inside ±0.010 | inside ±0.010 | inside ±0.010 | allocation at 5 km is worth less than 0.01 either way | close CONCENTRATION; spend slots on MASS/SPACING where the ceiling is measurable |
| <= -0.010 | <= -0.010 | >= +0.010 | the prior is inverted at this scale | submit `cat10away` as the candidate; propose a FRONTIER axis in `SLOT_PLAN.md` |
| >= +0.010 | inside ±0.010 | inside ±0.010 | effect saturates below 20 % | hold the 10 % dose, do not spend the 20 % |

Any single live change below 0.01 is **no evidence** (brief §5); the table
reads the three receipts as one experiment, not three independent scores.

---

# Part V — 2 km H19-supported CONCENTRATION (separate session)

The independent `arena/0a75dd63` session added three non-duplicate values:
`2km-b50-t33-m3765` (`da3a4886`, MODEL central +0.0024),
`2km-b50-t33-m5648` (`51ba9656`, −0.0028), and
`2km-b50-t33-m7531` (`1e857586`, −0.0126). They keep every added dot on H19-5
and use exact sequential DTI marginals rather than Part IV's potential-field
`q` placement. Their full hypothesis / mechanism / mimic / prediction /
falsifier cards are in **`ledger/MECHANISM_CARDS_CONCENTRATION.md`**.

These are **not clean scale-only controls** for Part IV: block size and
placement both differ. Negative H19 coverage and crowding counter-indicators
hold the 15% and 20% arms; the integrated queue keeps `cat10` as the primary
allocation probe and the 2 km family as a separate, currently held mechanism.

---

# Part VI — `12.8 km` (`128 px`) structural-interaction & catalogue-free GPS strain `CONCENTRATION` (`12p8km-int10` · `12p8km-int20` · `12p8km-geod15`) — session `arena/6e810001-gemsdoe89` (2026-10-23)

Parent for every card: **R0 = `h33-h33-2-b2`**, rebuilt byte-identically this session via `tools/rebuild_r0.py` (`c55bafc4…` zeros, `baeae321…` NaN; `37,654` unit-mass dots; live **0.2778 = CLAIM**).

## Why this `12.8 km` family is structurally orthogonal to Parts IV (`5 km` raw catalogue) and V (`2 km` H19)

1. **Accommodation-zone interaction complexity vs raw fault length, plus a 100% catalogue-free GPS/seismicity arm.** In Great Basin extensional and transtensional provinces, unmapped secondary splays, relay ramps, and horsetail terminations nucleate in **10–15 km fault-interaction zones** around fault tips, branch junctions, and `<= 1 km` multi-strand step-overs rather than along simple mid-segment traces (Faulds & Hinz, 2015, NBMG/OSTI #1249065: https://www.osti.gov/servlets/purl/1249065; organizer truth guidance: https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516, https://community.drivendata.org/t/where-do-you-draw-the-line/11536). Across the `318` interior `12.8 km` (`128 px`) blocks (`>= 50%` inside the `5,167,373`-px footprint), R0 has `Spearman(r0_dens, cat_dens) = −0.0019` (**3.67× over-allocated** in the lowest interaction tercile `T1`, **0.52× under-allocated** in `T3`), while R0's lineage (`d28` `0.2600` → `solo_d28` `0.2708` → `R0` `0.2778` CLAIM) climbed **`0.5181 → 0.5369 → 0.5532`** in `12.8 km` block-density CV. Separately, **`12p8km-geod15` never reads `existing_faults.tif` in its block prior at all**, testing active crustal strain (`b04_geod_2ndinv` + `b07_geod_shearrate` + `b16_ieq_n100a15`; INGENIOUS synthesis: https://www.osti.gov/servlets/purl/1987729) free of historical mapping bias (`Spearman(geod, interact) = +0.2458`).
2. **Proportional per-block quotas + strike-coherent scarp/potential-field placement (`corrob_ridge`).** Removals (`d_cat >= 3.0 px`, `<3 px` collar frozen at `1,611`) and additions (`d_cat >= 3.00 px`, `r_sep >= 2.80 px`, zero `<2.8 px` crowding) are apportioned **proportionally across bottom-40% and top-40% blocks** so ~10 steep volcanic blocks cannot hoard the moved budget (`IRREGULARITIES.md` item 13), and candidate pixels are ranked deterministically by strike-coherent DEM concavity + slope break + gravity slope + TMI HG (`corrob_ridge`, bands `3, 5, 12, 19`; leakage canary max `0.5995 <= 0.90`).
3. **Out-of-sample 25% connected-strand holdout + matched random-block-shuffle calibration (`MODEL`, never a score).** Withholding 25% of 8-connected catalogue strands *before* computing `d_cat`, R0, or `interaction_block_prior` across 3 seeds (`20261023, 7, 42`, base DTI `0.1063`) and comparing against a matched random-block shuffle using the identical `corrob_ridge` operator (`registry/report_only_status.json`):
   - `12p8km-int10` (`bcade136`, `3,765` moved = `10.00%`, `CV_12.8km: 0.5532 → 0.5533`): mean strand-holdout **`+0.0040`** (positive on all 3 seeds), shuffle `−0.0012`, pure block-prior lift **`+0.0052`**.
   - `12p8km-int20` (`357b4ac4`, `7,531` moved = `20.00%`, `CV_12.8km: 0.5532 → 0.6561`): mean strand-holdout **`+0.0051`** (positive on all 3 seeds), shuffle `−0.0086`, pure block-prior lift **`+0.0136`**.
   - `12p8km-geod15` (`259ea040`, `5,648` moved = `15.00%`, `CV_12.8km: 0.5532 → 0.6355`, `mean disp = 1020.8 px`): mean strand-holdout **`−0.0004`**, shuffle `−0.0042`, pure block-prior lift **`+0.0038`**.

## Card C6.1 — `12p8km-int10` (`h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136`) — PRIMARY 12.8 km INTERACTION PROBE
- **Hypothesis:** Moving 10% (`3,765` dots) from bottom-40% (`151` blocks) to top-40% (`146` blocks) `12.8 km` fault-interaction blocks (`6,747` tips, `5,943` junctions, `554,371` `<=1 km` step-over px) — while holding `CV_12.8km` invariant at `0.5533` inside `[0.51, 0.59]` and relief terciles nearly fixed (`[7657, 15048, 14909]`) — raises truth kernel hits `T` at fixed `S = 37,654`.
- **Mechanism:** Proportional per-block quotas; drops weakest `corrob_ridge` dots (`mean 0.0345`) in bottom-40% blocks and adds strike-coherent `corrob_ridge` dots (`mean 0.1658`, `d_cat >= 3.00 px`, `r_sep >= 2.828 px`, `mean disp = 95.5 px`) in top-40% blocks.
- **Non-fault mimic:** Welded-tuff cooling joints, caldera margins, and erosional hogbacks in well-exposed Cenozoic ranges co-locate with dense mapped fault junctions without hosting Quaternary slip; or test truth may sample unmapped quiet basins (`T1`).
- **Predicted sign and size (`MODEL`):** Central **+0.008**, band **−0.006 … +0.018**.
- **Falsifier:** Receipt inside `±0.010` closes `12.8 km` interaction reallocation (`int20` stays held); `<= −0.010` falsifies map-interaction clustering on the test split and triggers catalogue-free `12p8km-geod15` (or `5km cat10away`).

## Card C6.2 — `12p8km-int20` (`h33-h33-2-b2-conc-12p8km-int20-20261023-357b4ac4`) — 2× DOSE / CV SATURATION TEST
- **Hypothesis:** Conditional on `12p8km-int10 >= +0.010`, doubling transfer to 20% (`7,531` dots, `CV_12.8km: 0.5532 → 0.6561`) tests whether pushing concentration above `0.59` scales linearly or saturates on secondary ridges.
- **Mechanism:** Identical `interaction_block_prior`, `40/60` split, and `corrob_ridge` operator at `fraction = 0.20` (`source 14,354 → 6,823`, `target 15,113 → 22,644`, `mean disp = 87.5 px`, `added corrob_ridge = 0.1450`).
- **Non-fault mimic:** `+50%` target-block dot density recruits second-tier pediment/incision ridges after primary unmapped splays are already covered (`−0.0086` shuffled-block dilution vs `−0.0012` at 10%).
- **Predicted sign and size (`MODEL`):** Central **+0.009**, band **−0.014 … +0.024** (hold until `12p8km-int10 >= +0.010`).
- **Falsifier:** Failure to beat `12p8km-int10` by `>= +0.005` when `int10 >= +0.010` confirms secondary-ridge saturation above `CV_12.8km ≈ 0.59`.

## Card C6.3 — `12p8km-geod15` (`h33-h33-2-b2-conc-12p8km-geod15-20261023-259ea040`) — CATALOGUE-FREE ACTIVE-STRAIN DISCRIMINATOR
- **Hypothesis:** Active unmapped faults in playaward / Walker Lane / Humboldt basins track **crustal strain rate and seismicity** rather than historical fault-map density (https://www.osti.gov/servlets/purl/1987729); reallocating 15% (`5,648` dots) into top-40% GPS shear/strain + seismicity `12.8 km` blocks captures blind/unmapped active belts without catalogue bias.
- **Mechanism:** `100%` catalogue-free block score `mean(robust_unit(b04), robust_unit(b07), robust_unit(log1p(b16)))`; proportional transfer `14,102 → 8,454` (`141` low-strain blocks) to `16,699 → 22,347` (`158` high-strain blocks; `CV_12.8km: 0.5532 → 0.6355`, `mean disp = 1020.8 px = 102.1 km`) onto strike-coherent `corrob_ridge` (`mean 0.1610`, `d_cat >= 3.00 px`, `r_sep >= 2.828 px`).
- **Non-fault mimic:** Smooth `20–50 km` GPS continuum interpolation and off-fault geothermal/mining seismic swarms elevate entire blocks where local `100 m` ridges are non-tectonic volcanic or shoreline landforms.
- **Predicted sign and size (`MODEL`):** Central **+0.003**, band **−0.015 … +0.021**.
- **Falsifier:** If catalogue-based concentration (`cat10` / `12p8km-int10`) is `<= 0` while `12p8km-geod15 >= +0.010`, live truth tracks active strain rather than mapped-fault proximity; `<= −0.010` retires continuum geodetic block priors.

---

# Part VII — SNAP factorial completion (`1p0px-g0p01` · `1p0px-g0p02` · `1p4px-g0p01`) — session `arena/fb0c15d6-gemsdoe89` (2026-10-24)

Parent for every card: **R0 = `h33-h33-2-b2`**, rebuilt byte-identically at the start gate (`c55bafc4…` zeros and `baeae321…` NaN; `37,654` unit dots; `0.2778` remains **CLAIM**). These are exactly the three missing cells in the ledger's 3-window × 3-gate design; no prior `(SNAP, value)` was rebuilt. All use the same TMI-HG / isostatic-gravity-HG response as Part III, fixed count and deterministic row-major placement. Every moved target has `d_cat >= 3.00 px`; inherited collar dots can only stay or move outward.

| value | moved / changed | mean displacement | mean response gain | inherited `<3 px` collar before → after | central MODEL (band) |
|---|---:|---:|---:|---:|---:|
| `1p0px-g0p01` (`2916ec2d`) | 4,265 / 11.327% | 1.000 px | 0.01933 | 1,611 → 1,556 | +0.0076 (−0.0038…+0.0190) |
| `1p0px-g0p02` (`384435e6`) | 1,245 / 3.306% | 1.000 px | 0.03304 | 1,611 → 1,595 | +0.0022 (−0.0011…+0.0055) |
| `1p4px-g0p01` (`afc60a25`) | 6,767 / 17.972% | 1.370 px | 0.02136 | 1,611 → 1,497 | +0.0120 (−0.0060…+0.0301) |

**Shared MODEL arithmetic and caution.** Pure relocation gives `ΔDTI ≈ ΔT/D`, with the previously recorded anchor `D=18,734.44`. Each moved dot is assumed to close (or open) one pixel with net fractions `−0.05 / +0.10 / +0.25` for low/central/high scenarios and triangular-kernel gain `1/3`. The positive gated scenarios reuse the upstream gated arms' assumptions; they are not fitted effects. The negative scenario prices non-fault crests. Gateless cells retain their different `−0.05 / +0.05 / +0.15` scenarios, so central MODELs across gates are not measurements and must not substitute for the matched live comparisons. A live `|Δ| < 0.01` is no evidence.

**Shared report-only diagnostics.** Withheld-catalogue recall (`n=18,296`, 95% Wilson CI) is `0.03810 [0.03255,0.04365]`, `0.03826 [0.03270,0.04382]`, and `0.03646 [0.03102,0.04189]`, respectively, versus parent `0.03842 [0.03285,0.04400]`. These are **PROXY**, overlap the parent, and never gate. The SNAP-response leakage canary passes (`max AUC=0.66538 < 0.90`). SGMC is skipped because its raster pin is UNVERIFIED.

## Card SN4 — `1p0px-g0p01` (`h33-h33-2-b2-snap1p0px-g0p01-20261024-2916ec2d`)
- **Hypothesis:** A four-neighbour, `>=0.01` response-gain gate repairs genuine off-by-one BFS placements while rejecting the micro-noise that moved 80.83% of dots in the gateless arm.
- **Mechanism:** Move 4,265 dots exactly 100 m onto the strongest qualifying TMI/gravity edge; fixed mass, spacing median `3.0→3.0 px`, and 1 km CV `1.88341→1.88198` isolate local position rather than concentration.
- **Non-fault mimic:** Fan-head rills, lithologic contacts, and aeromagnetic tie-line seams can all exceed the same unsigned-gradient gate without being faults.
- **Predicted sign and size (MODEL):** Positive central **+0.0076**, band **−0.0038…+0.0190**; a no-evidence live result is entirely plausible.
- **Falsifier:** Against `1p0px-g0p00`, a `>=0.010` loss means the gate removes useful dose; a `>=0.010` gain over both R0 and that matched gateless cell supports selectivity. Inside `±0.010`, spend no further slot on this cell.

## Card SN5 — `1p0px-g0p02` (`h33-h33-2-b2-snap1p0px-g0p02-20261024-384435e6`)
- **Hypothesis:** The highest-gain four-neighbour corrections are the cleanest subset: if fault edges nominate R0 lineaments, these 1,245 moves should carry the highest precision per moved dot.
- **Mechanism:** Require `>=0.02` fused-response improvement and move only 3.306% of R0 by 100 m; the larger mean gain (`0.03304`) tests selectivity at minimum dose, not a new response surface.
- **Non-fault mimic:** Sharp dike margins, welded-tuff contacts, and survey-processing steps often have stronger gradients than diffuse fault scarps, so the high gate can preferentially select non-faults.
- **Predicted sign and size (MODEL):** Positive central **+0.0022**, band **−0.0011…+0.0055**; the central expectation is below the live no-evidence threshold, so this is a held boundary/control, not a default weekly slot.
- **Falsifier:** A `>=0.010` gain would reject the dose-scaled MODEL and justify high-gate investigation; a `<=−0.010` loss despite only 1,245 moves would strongly implicate sharp non-fault contacts. Anything smaller teaches no live lesson.

## Card SN6 — `1p4px-g0p01` (`h33-h33-2-b2-snap1p4px-g0p01-20261024-afc60a25`) — PRIMARY NEW ARM
- **Hypothesis:** At 400 m GeoDAWN line spacing (USGS: https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7), diagonal as well as cardinal neighbours contain real edge corrections; an intermediate gate retains that dose while rejecting weak crest noise.
- **Mechanism:** Move 6,767 dots (17.972%) within the eight-neighbour `<=1.42 px` window, mean `1.370 px`, with the same `>=0.01` gate as SN4. This is the exact missing intermediate-gate counterpart to local `1p4px-g0p00` and upstream `1p4px-g0p02`.
- **Non-fault mimic:** Oblique fan distributaries, shoreline terraces, and pluton contacts become available when diagonals are added; unsigned max-fusion cannot distinguish them from fault scarps.
- **Predicted sign and size (MODEL):** Positive central **+0.0120**, band **−0.0060…+0.0301**, the only new arm whose central assumption exceeds the `0.01` evidence threshold.
- **Falsifier:** Submit against matched `1p4px-g0p00`: gated lower by `>=0.010` falsifies selectivity-over-dose; gated higher by `>=0.010` supports it and earns the fixed-gate window control SN4. A result within `±0.010` of R0 is no evidence, not validation.


---

# Part VIII — `SNAP` directional corner (`dirfw2p0` · `dirhw2p0` · `dirfw1p0`) — session `arena/a641bd79-gemsdoe89` (2026-10-24)

## The gap this session fills, and the measurement that opened it

Every `SNAP` arm in the ledger is a cell of a `{window} x {gain-gate}` factorial on one
response surface — bands 3 `tmi_hg` + 18 `iso_grav_anom_hg`, median-fill, gaussian
`sigma = 1.0 px`, `robust_unit` at `p99.5`, fused by pixel-wise max (`gemsdoe/snap.py`):

| window | gate 0.00 (this repo) | gate 0.01 / 0.02 (upstream `GEMSDOE84`) |
|---|---|---|
| 1.0 px | `1p0px-g0p00` `1add5aa6` | `1p0px-g0p01` `2916ec2d`, `1p0px-g0p02` `384435e6` |
| 1.42 px | `1p4px-g0p00` `e1474851` | `1p4px-g0p01` `afc60a25`, `1p4px-g0p02` `0b6a2ab2` |
| 2.0 px | `2p0px-g0p00` `69db3aae` | `2p0px-g0p01` `7bdaa58b`, `2p0px-g0p02` `b2019f55` |

All nine cells (the factorial was completed the same day, Part VII) allow a dot to move in
**any** direction inside the window and all nine land it on the local maximum of a
horizontal-gradient (HG) field. None of them can say **which side
of that maximum the surface trace sits on**, which is the first question a potential-field
worker asks about an HG maximum.

The obvious correction — "the HG maximum over a dipping contact is displaced toward the
hanging wall by roughly `depth / tan(dip)`, so subtract that displacement" — turns out to
be *unnecessary in the mean*: **measured here**, the undirected `2p0px-g0p00` arm's 31,287
moves split **15,585 up-slope / 15,670 down-slope / 32 flat** (`share_upslope = 0.498`,
`gemsdoe/snap_directional.py::upslope_share`). R0's dots are **direction-neutral** with
respect to the HG crest, so the undirected snap is not a biased arm and the dip-offset
correction (proposed as `TRACKB-DIP-OFFSET` in `SLOT_PLAN.md`) is **not** what a 2 px
correction should do.

What remains open, and is cheap to settle: conditional on a dot snapping to the crest at
all, is truth more often **up-slope (footwall)** of the crest, **down-slope (hanging
wall)**, or **on** it? Three arms, one predicate apart from `69db3aae`, answer it.

**Design invariant.** Each arm below reproduces `snap.snap_dots` exactly when the direction
filter is switched off (`tests/test_snap_directional.py::test_parity_with_snap_dots`, and
at every released window): same response recipe, same offsets and ordering
`(dist, dy, dx)`, same tie-breaking, same claim/no-fallback rule, same allowed targets
(footprint, `d_cat >= 3.00 px`), same count `n = 37,654`, no RNG. The single changed
predicate: a candidate displacement must have `cos >= +0.5` with the local up-slope unit
vector (footwall arm) or `cos <= -0.5` (hanging-wall arm), where up-slope is the Sobel
gradient of pinned band 12 `det_elev` after `sigma = 2.0 px` smoothing
(`gemsdoe/snap_directional.py::uphill_field`). Ground flatter than `2.0 m/px` (2 % grade)
is a deadband — the dot does not move — and only **36** of R0's dots fall in it (slope at
parent dots: p10 5.71, p50 11.01, p90 19.62 m/px), so the deadband cannot carry the result.

**Why the pair, not the arm.** The sign prior of this hypothesis is weak (≈50/50: the
basin-side case and the range-side case are both geologically ordinary), so a single arm's
`MODEL` band (`−0.019…+0.057`) is unreadable. `dirfw2p0` and `dirhw2p0` are exact mirrors
with near-identical displacement statistics (20,853 vs 21,399 moves, mean displacement
1.738 vs 1.737 px, mean directional cosine 0.815 vs 0.813) — their **difference** isolates
the sign, and their **sum** isolates "any local re-shuffle off the crest" (the null that
the existing SNAP arms cannot exclude).

## Card D1 — `dirfw2p0` (`h33-h33-2-b2-snapdirfw2p0-20261024-dc578b2f`) — MECHANISM ARM

- **Hypothesis:** Where R0's dots are pulled onto a fused TMI/gravity HG maximum, the mapped surface trace sits **up-slope** (footwall / range side) of that maximum; snapping only up-slope therefore raises credit per unit mass.
- **Mechanism:** Normal faults in the Basin & Range dip 45–60° basinward, so the potential-field contact edge sits in the hanging wall, displaced from the surface outcrop by `depth / tan(dip)` — for a 200–500 m deep basement contact that is 170–420 m = **1.7–4.2 px**, i.e. the 2 px window. Supportive geometry measured here: the up-slope moves gain **+23.89 m** mean elevation (median +20.2, p10/p90 +6.2/+47.3) while the mirrored down-slope moves lose only **−13.28 m** (median −11.95) — the HG crest sits on the *basin-side toe* of a steep rise, not on its shoulder, which is the asymmetry H_dip predicts.
- **Rule:** 20,853 of 37,654 dots (55.4 %) moved, mean displacement 1.738 px, mean response gain 0.0091, mean directional cosine 0.815; up-slope share of the moves **1.000** by construction (audited, not assumed).
- **Non-fault mimic:** Alluvial-fan and basin-floor gradients carry no fault: the direction filter is satisfied by any regional slope, so a share of these moves lands on fan-head channels or bedrock contacts that happen to sit up-slope of a magnetic edge. Strike-slip faults have no dip offset, so for them the up-slope restriction is arbitrary (it dilutes, not flips, the effect).
- **Predicted sign and size (`MODEL`):** band **−0.019 … +0.057**, central **+0.019** — but the *sign prior is weak*; the arm is built to be read against its mirror, not on its own. Evidence class `MODEL`, never a score.
- **Falsifier:** `dirfw2p0 − dirhw2p0 < +0.010` ⇒ no measurable crest-side bias at 2 px; retire the directional corner and the dip-offset story with the rest of SNAP. Receipt `<= −0.010` **while the mirror is also `<= −0.010`** ⇒ moving off the crest is what hurts, i.e. R0's crest placement is already right and neither side is favoured.

## Card D2 — `dirhw2p0` (`h33-h33-2-b2-snapdirhw2p0-20261024-5cccfc1d`) — EXACT MIRROR / CONTROL

- **Hypothesis:** The mirror of D1: if the trace sits on the hanging-wall side of the HG maximum, snapping down-slope should gain and the footwall arm should lose by a similar amount.
- **Mechanism:** Identical rule with `cos <= −0.5`; 21,399 moves (56.8 %), mean displacement 1.737 px, mean response gain 0.0066, mean directional cosine 0.813, up-slope share **0.000**; mean elevation change **−13.28 m**.
- **Why it is a control and not a dose repeat:** same window, same gate, same response surface, same count, same allowed targets, same offset set — only the half of the window differs. Its job is to convert D1's receipt from an unreadable absolute number into a signed comparison, and to price "any 2 px re-shuffle off the crest" (both arms carry that cost).
- **Non-fault mimic:** Mirror-image of D1's; it is the arm that snaps *toward* the basin fill, where alluvial and playa edges and basement-top steps produce HG maxima with no surface fault.
- **Predicted sign and size (`MODEL`):** band **−0.019 … +0.057** (same construction, same anchor), central **+0.019** by formula only — declaration in advance: if H_dip is right this arm must land **below** `dirfw2p0` by `>= 0.010`.
- **Falsifier:** `dirhw2p0 > dirfw2p0 + 0.010` reverses the sign of the dip story (trace on the hanging-wall side) — informative, not a failure of the design; it would immediately re-aim the direction filter and be the basis of the next session's dose.

## Card D3 — `dirfw1p0` (`h33-h33-2-b2-snapdirfw1p0-20261024-373c8fd6`) — DOSE

- **Hypothesis:** Half the correction distance (1.0 px instead of 2.0 px) should retain most of D1's gain if the effect is a monotone function of distance from the crest, and should beat D1 if 2 px overshoots onto the steep footwall slope.
- **Mechanism:** Identical rule at window 1.0 px (4-neighbour): 16,632 moves (44.2 %), mean displacement exactly 1.000 px, mean response gain 0.0051, mean directional cosine 0.852, up-slope share **1.000**, mean elevation change **+13.30 m**.
- **Non-fault mimic:** As D1, with less reach; its 1 px step is smaller than GeoDAWN's own ±1 px positional noise (400 m line spacing), so a null here does not clear the 2 px mechanism.
- **Predicted sign and size (`MODEL`):** band **−0.015 … +0.044**, central **+0.015**; conditional arm — spend the slot only if the D1−D2 difference is `>= +0.010`.
- **Falsifier:** `dirfw1p0 >= dirfw2p0` while both are positive ⇒ the gain is a *sign* effect, not a distance effect, and larger windows are wasted mass; `dirfw1p0 ≈ dirhw2p0` ⇒ the effect is dose, not direction, and the whole corner collapses back to the `{window} x {gate}` factorial.

## Pre-registered read-out (public chunks only; `|Δ| < 0.01` is no evidence)

| receipts | reading | next action |
|---|---|---|
| `fw2p0 − hw2p0 >= +0.010` | surface trace is on the **footwall** side of the HG crest | run the matched 4 px arm and re-aim every future placement rule up-slope |
| `hw2p0 − fw2p0 >= +0.010` | trace on the **hanging-wall** side | same, mirrored; the dip-offset axis is confirmed with the opposite sign and becomes the slot-1 candidate |
| both `<= R0 − 0.010` | **crest is right**; leaving it in either direction costs credit | retire the directional corner and the dip-offset proposal; SNAP keeps only the `{window} x {gate}` arms |
| both inside `±0.010`, `fw − hw` inside `±0.010` | no measurable crest-side bias at 1–2 px | SNAP is saturated at this scale; move the slots to the block-concentration fork (`SLOT_PLAN.md`) |

**Report-only instruments (never gates, never scores).** Catalogue hide-and-recover `PROXY`
(30 % seeded holdout, `n ≈ 18.3k`): parent `0.0384`; `dirfw2p0` `0.0316`, `dirhw2p0`
`0.0237`, `dirfw1p0` `0.0357`, undirected `2p0px-g0p00` `0.0152` — the ordering follows the
mechanism, but the proxy's correlation with live scores is `−0.87…+0.54`, so this is a
consistency check, **not** evidence. Leakage canary: `tmi_hg` AUC `0.665`,
`iso_grav_anom_hg` AUC `0.647` — both below the `0.90` stop line. Surrogate (catalogue-as-
truth, counterfactual) DTI: parent `0.00671` → `0.00529` / `0.00433` / `0.00627`; every
directional arm trades catalogue-fitted coverage for off-catalogue position, exactly as
the mechanism implies. SGMC control: **not run** (pin UNVERIFIED, `IRREGULARITIES.md`
item 8). Block density CV: `1 km` `1.883 → 1.904 / 1.893 / 1.889`, `5 km` `0.899 → 0.906 /
0.894 / 0.902` — a position-only axis, as required.
