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
