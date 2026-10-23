# Mechanism cards — session GEMSDOE89 (`SPACING` + prior `RELIEF`)

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
