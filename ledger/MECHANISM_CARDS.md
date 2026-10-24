# Mechanism cards — session GEMSDOE89 (`SPACING` + `RELIEF` + `SNAP` + `CONCENTRATION`)

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

# Part IV — `CONCENTRATION` axis (`12p8km-int10` · `12p8km-int20` · `12p8km-geod15`) — session GEMSDOE89 (branch `arena/6e810001-gemsdoe89`, 2026-10-23)

Parent for every card: **R0 = `h33-h33-2-b2`**, rebuilt byte-identically this session via `tools/rebuild_r0.py` (`c55bafc4…` zeros, `baeae321…` NaN; `37,654` unit-mass dots; live **0.2778 = CLAIM**).

## Structural measurement the `CONCENTRATION` axis rests on

1. **R0's 12.8 km (`128 px`) structural misallocation.** Across the `318` interior `12.8 km × 12.8 km` (`128 × 128 px`) blocks (`>= 50%` inside the `5,167,373`-px valid footprint), R0's dot density is **spatially uncorrelated** with mapped fault density (`Spearman(r0_dens, cat_dens) = −0.0019`), whereas physical fault indicators correlate strongly (`Spearman = +0.4758` for `b19_det_elev_slope`, `+0.3957` for `b03_tmi_hg`). Along R0's own winning lineage (`d28` `0.2600` CLAIM → `solo_d28` `0.2708` CLAIM → `R0` `0.2778` CLAIM), `12.8 km` block-density CV climbed monotonically **`0.5181 → 0.5369 → 0.5532`**, sitting squarely inside the `0.51–0.59` reference band where the best Great Basin discrete-dot files reside.
2. **Accommodation-zone & fault-interaction physics (Faulds & Hinz 2015).** In Great Basin geothermal and extensional structural provinces, unmapped secondary splays, relay ramps, horsetail terminations, and synthetic/antithetic step-over faults cluster in **10–15 km structural complexity blocks** around mapped fault tips, Y-junctions, and multi-strand step-overs rather than inside structurally simple basin interiors (Faulds & Hinz, 2015, *Structural and Stratigraphic Controls of Geothermal Activity in the Great Basin Region*, NBMG/OSTI #1249065: https://www.osti.gov/servlets/purl/1249065; DrivenData organizer guidance on unmapped splay/segment truth and pixel-exact catalogue masking: https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516, https://community.drivendata.org/t/where-do-you-draw-the-line/11536). Across `318` interior `12.8 km` blocks ranked by fault-interaction density (`6,747` skeleton tips, `5,943` junctions, `554,371` multi-strand `<= 1 km` step-over pixels), R0 places **6.96 dots/kpx** in the lowest interaction tercile (`3.07` cat px/kpx: **3.67× over-allocated**) and only **7.18 dots/kpx** in the highest tercile (`22.53` cat px/kpx: **0.52× under-allocated** — a **7.3×** fault-density contrast vs `1.40×` in `RELIEF`).
3. **Single-variable isolation & proportional block quotas.** Upstream `GEMSDOE84` built only `5 km` (`50 px`) block variants (`5km-t25-move2400`, `5km-t50-move3765`, `spread5km-move2400`). Here we test the **`12.8 km` (`128 px`) structural-domain scale** while holding total count (`37,654`), unit mass (`1.0`), inherited `2.0 < d_cat < 3.0 px` collar count (`1,611` frozen), added-dot clearance (`d_cat >= 3.00 px`), minimum inter-dot spacing (`r_sep >= 2.80 px`, median NN `3.00 → 3.16 px`), and geomorphic relief terciles (`[7692, 15742, 14204] → [7657, 15048, 14909]` on `int10`) tightly controlled. Removals and additions are apportioned **proportionally across the bottom-40% (`151` source blocks) and top-40% (`146` target blocks)** so ~10 steep range blocks cannot hoard the moved budget; within each target block, candidate pixels (`d_cat >= 3.0 px`) are ranked deterministically by an unsupervised strike-coherent corroborated scarp/potential-field ridge operator (`corrob_ridge`, bands `3, 5, 12, 19`; leakage canary max `0.5995 <= 0.90`).
4. **Out-of-sample 25% connected-strand holdout & shuffled-block control (`MODEL`, never a score).** Pixel-withheld catalogue recall (`PROXY`) is identically `0.038424` (`95% CI [0.0329, 0.0440]`) because `d_cat >= 3.0 px` freezes the 3-pixel DTI collar (`IRREGULARITIES.md` item 4), and `sgmc_faults_control` is `UNVERIFIED` (`item 8`). To price both the km-scale block prior and the within-block placement operator without circularity, we withheld **25% of 8-connected catalogue fault strands** *before* computing `d_cat`, rebuilding R0, or computing `interaction_block_prior`, across 3 seeds (`20261023, 7, 42`; base DTI `0.1063`), alongside a matched **random-block-shuffle control** using the identical `corrob_ridge` operator (`registry/report_only_status.json`):

| Variant | Moved (% R0) | `CV_12.8km` | `CV_5km` | Mean disp | 3-seed strand-holdout `ΔDTI` (`MODEL`) | Matched shuffle `ΔDTI` | Pure block-prior lift |
|---|---|---|---|---|---|---|---|
| `12p8km-int10` (`bcade136`) | 3,765 (10.00%) | `0.5532 → 0.5533` | `0.8991 → 0.8874` | 95.5 px | **+0.0040** (`+3.8%`) | −0.0012 | **+0.0052** |
| `12p8km-int20` (`357b4ac4`) | 7,531 (20.00%) | `0.5532 → 0.6561` | `0.8991 → 0.9782` | 87.5 px | **+0.0051** (`+4.8%`) | −0.0086 | **+0.0136** |
| `12p8km-geod15` (`259ea040`) | 5,648 (15.00%) | `0.5532 → 0.6355` | `0.8991 → 0.9467` | 1020.8 px | **−0.0004** (`−0.3%`) | −0.0042 | **+0.0038** |

---

## Card C1 — `12p8km-int10` (`h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136`) — PRIMARY

**Hypothesis.** Unmapped Great Basin test faults cluster inside `12.8 km` accommodation, relay-ramp, and branch-point domains around known fault systems (Faulds & Hinz 2015: https://www.osti.gov/servlets/purl/1249065), whereas R0 over-allocates 38% of its mass (`14,354` dots) into the lowest-40% fault-interaction blocks (`3.67×` over-allocation in `T1`). Reallocating 10% of R0 (`3,765` dots) from the lowest-40% to the highest-40% `12.8 km` interaction blocks — while holding `CV_12.8km` invariant inside the `0.51–0.59` reference band (`0.5532 → 0.5533`) — increases kernel hits `T` per unit mass at fixed `S = 37,654`.

**Mechanism.** Computes `interaction_block_prior` on `128 × 128 px` (`12.8 km`) blocks as the equal-weight rank-mean of catalogue fault-tip density (`1`-neighbor skeleton endpoints), fault-junction density (`>= 3`-neighbor branch points), and multi-strand `<= 10 px` (`1 km`) step-over zone fraction. Proportionally removes `3,765` weakest-ridge non-collar dots (`d_cat >= 3.0 px`, mean `corrob_ridge = 0.0345`) from the `151` bottom-40% blocks (`14,354 → 10,589` dots) and adds `3,765` strike-coherent corroborated scarp/gravity/magnetic ridge dots (`d_cat >= 3.00 px`, `r_sep >= 2.828 px`, mean `corrob_ridge = 0.1658`) across the `146` top-40% blocks (`15,113 → 18,878` dots; mean displacement `95.5 px`).

**The non-fault process that could mimic it.** Mapped fault tips and junctions are enriched in well-exposed Cenozoic volcanic ranges where erosional hogbacks, welded-tuff cooling joints, caldera-margin scarps, and dike swarms generate dense linear topographic/aeromagnetic ridges (`corrob_ridge`) adjacent to known faults without hosting Quaternary slip; conversely, if the organizer's test split deliberately targeted *previously unmapped* basins (`T1`) rather than under-mapped splays in complex zones (`T3`), shifting 10% out of `T1` sacrifices blind-basin coverage.

**Predicted sign and size (MODEL).** Central **+0.008**, band **−0.006 … +0.018** (anchored to R0 `0.2778` CLAIM: 3-seed 25% strand-holdout delta is `+0.0040` on `0.1063` base = `+3.8%` relative, scaling to `+0.010` at `0.278` before discounting for `h19_5` vs `corrob_ridge` precision; pure block-prior lift over random-block shuffle is `+0.0052`, positive on all 3 seeds: `+0.0042, +0.0028, +0.0050`).

**Falsifier.** Live receipt delta inside `±0.010` (`0.2678 … 0.2878`) counts as **no evidence** and closes 10%-dose catalogue-interaction block reallocation (`int20` stays held unless `int10 >= +0.010`). Live receipt `<= −0.010` (`<= 0.2678`) falsifies the accommodation-zone clustering prior on the test split (proving test truth sits preferentially in quiet/unmapped `T1` basins) and triggers the catalogue-free `12p8km-geod15` arm if km-scale allocation is tested again.

---

## Card C2 — `12p8km-int20` (`h33-h33-2-b2-conc-12p8km-int20-20261023-357b4ac4`) — DOSE

**Hypothesis.** If `12p8km-int10` gains `>= +0.010`, R0's `2.1×` High-tercile deficit (`15,113` parent dots in top-40% blocks vs `22,644` needed to match relative fault concentration) is only half-closed at 10% transfer; doubling the transfer to 20% (`7,531` dots, `symmetric diff = 40.00%`) tests whether pushing `CV_12.8km` (`0.5532 → 0.6561`) **above** the `0.51–0.59` lineage reference band yields continued linear gain or hits secondary-ridge false-positive saturation.

**Mechanism.** Identical `12.8 km` `interaction_block_prior`, `40/60` quantile split, and `corrob_ridge` operator as `12p8km-int10`; only `fraction` doubles (`0.10 → 0.20`, moving `7,531` dots: source `14,354 → 6,823`, target `15,113 → 22,644`, `added_min_dcat = 3.00 px`, `r_sep >= 2.828 px`, mean displacement `87.5 px`). Mean added `corrob_ridge` eases slightly from `0.1658` (`int10`) to `0.1450` (`int20`) as deeper secondary ridges inside top-40% blocks are recruited.

**The non-fault process that could mimic it.** Moving `7,531` dots into `146` blocks raises mean target-block density by `+50%` (`103.5 → 155.1` dots/block), forcing recruitment of second-tier topographic/potential-field lineaments (pediment-fan incision scarps, tilted Tertiary strata, pluton roof contacts) once primary unmapped splays in each block are already covered within `300 m`. Look at the shuffled-block control: moving 20% off `h19_5` onto random blocks costs `−0.0086` DTI vs `−0.0012` at 10%, quantifying exact secondary-ridge dilution (`+0.0136` pure block-prior lift only partially offsets steeper off-`h19_5` cost: net strand-holdout `+0.0051` vs `+0.0040` at 10%).

**Predicted sign and size (MODEL).** Central **+0.009**, band **−0.014 … +0.024** (sub-linear `1.27×` gain over `int10` on strand holdouts: `+0.0051` vs `+0.0040`). Submit **only** if `12p8km-int10` scores `>= +0.010` (`>= 0.2878`).

**Falsifier.** Given `12p8km-int10 >= +0.010`, if `12p8km-int20` fails to beat `12p8km-int10` by `>= +0.005` (or regresses), the `0.51–0.59` `CV_12.8km` ceiling is empirically confirmed as a real saturation boundary (`CV_12.8km = 0.656` over-concentrates mass onto secondary non-fault ridges), locking optimal concentration dose near `10%`.

---

## Card C3 — `12p8km-geod15` (`h33-h33-2-b2-conc-12p8km-geod15-20261023-259ea040`) — DISCRIMINATOR

**Hypothesis.** The USGS/INGENIOUS fault catalogue under-samples blind and playaward active faults beneath Quaternary basin fill (e.g., Walker Lane transtensional domains, Carson Sink / Humboldt structural belt) where active crustal deformation is nonetheless directly measured by GPS strain rate and microseismicity (Kreemer et al., 2012, Nevada Bureau of Mines and Geology / UNR Geodetic Laboratory strain-rate synthesis reflected in INGENIOUS inputs: https://www.osti.gov/servlets/purl/1987729). A **100% catalogue-free** `12.8 km` block prior built solely from geodetic shear rate (`b07`), second invariant of strain rate (`b04`), and earthquake density (`b16`) reallocates 15% of R0 (`5,648` dots) into actively deforming tectonic belts (`Spearman(geod, interact) = +0.2458`) without inheriting historical mapping bias.

**Mechanism.** Scores each `12.8 km` block by the footprint mean of `(robust_unit(b04_geod_2ndinv) + robust_unit(b07_geod_shearrate) + robust_unit(log1p(b16_ieq_n100a15))) / 3`, completely independent of `existing_faults.tif` (`catalogue_components` never read by the block prior). Proportionally moves `5,648` dots (`15.00%`, `symmetric diff = 30.00%`) from the `141` lowest-strain blocks (`14,102 → 8,454` dots) to the `158` highest-strain/seismicity blocks (`16,699 → 22,347` dots; `CV_12.8km: 0.5532 → 0.6355`; province-scale mean displacement `1020.8 px = 102.1 km`) onto strike-coherent `corrob_ridge` maxima (`mean = 0.1610`, `d_cat >= 3.00 px`, `r_sep >= 2.828 px`).

**The non-fault process that could mimic it.** Geodetic strain-rate grids (`b04, b07`) are smooth continuum interpolations across `20–50 km` GPS station spacing, and `b16_ieq_n100a15` includes diffuse off-fault seismic swarms, geothermal/mining seismicity, and post-seismic relaxation haloes; high regional strain in a `12.8 km` block does not guarantee discrete surface-rupturing or geophysically mappable `100 m` fault traces inside that block, so regional transfers (`102 km` mean jump) can land on non-tectonic volcanic or erosional ridges that happen to sit inside the Walker Lane strain halo.

**Predicted sign and size (MODEL).** Central **+0.003**, band **−0.015 … +0.021**. On catalogue-derived strand holdouts (`−0.0004` mean delta vs `−0.0042` random-block shuffle = `+0.0038` pure block-prior lift), `geod15` is neutral by construction because withheld *catalogue* strands share the catalogue's historical mapping footprint; its upside (`+0.010 … +0.021`) materializes specifically if the organizer's hidden test set prioritizes newly mapped faults in high-strain, historically under-mapped Walker Lane / Humboldt blocks.

**Falsifier.** Paired against `12p8km-int10`: if `int10` is null/negative (`<= 0.000`) while `geod15` gains `>= +0.010`, live test truth follows **active crustal strain rather than existing-map proximity** (mandating catalogue-free strain weighting for the final blind submission). Conversely, if `geod15 <= −0.010`, continuum GPS/seismicity fields are too coarse (`20–50 km`) to guide `100 m` discrete fault emission and regional tectonic priors are retired.
