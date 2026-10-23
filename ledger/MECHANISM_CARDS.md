# Mechanism cards — session GEMSDOE89 (SPACING & RELIEF axes)

Parent for every card: **R0 = h33-h33-2-b2** (GEMSDOE32 lineage; 37,654 unit-mass
dots, none within 2 px of the catalogue, rebuilt byte-identically by
`tools/rebuild_r0.py` to sha256 `c55bafc470054e82…` zeros / `baeae3219bba6a19…`
nan; live 0.2778 = **CLAIM**, no receipt in this repo).

Written for a structural geologist. Every projection below is labelled **MODEL**
and is never called a score. Under brief sec.5, any live change within ±0.010 on
the public chunks counts as **no evidence**.

---

# Part I — SPACING axis (current session: `strike`, `poisson`, `lattice`)

## Structural & metric foundation of the SPACING axis

Every one of R0's 37,654 dots lies on the binary multi-physics ridge network
`scored_h19_5` (121,131 px; live 0.1922 = **CLAIM**). The entire +0.0856 climb
from `h19-5` (0.1922) to `d1-5` (0.2477) to `d2-8` (0.2600) to `solo-d2-8`
(0.2708) to `h33-h33-2-b2` (0.2778) came from **how dots are spaced on that
ridge support**.

Why R0's isotropic `r = 2.8 px` greedy thinning is suboptimal on geological
structures:

1. **Corridor width vs fault-core width.** Quaternary/geothermal fault traces in
   the Great Basin localize slip in cores metres to tens of metres wide (≤1 px
   at 100 m), whereas GeoDAWN Area 2 potential-field data were flown at 400 m
   line spacing and 150–200 m terrain clearance
   (https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7),
   upward-continuing basement steps into 200–400 m (2–4 px) gradient corridors.
2. **Across-strike flank doublets.** On a 3-px-wide ridge corridor, scanline
   greedy thinning at `r = 2.8 px` leaves 12,963 of R0's 37,654 dots (34.4 %) off
   the 1-px across-strike non-maximum-suppression (NMS) crest and creates 4,802
   across-strike dot pairs (`|Δ⊥| > |Δ∥|` inside `(2.2, 4.2)` px). Under the DTI
   `max` operator (`https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/`),
   a flank twin beside a crest dot adds almost zero incremental truth credit `T`
   to a crest-centered fault trace while paying up to +0.2 in `0.2(S − M)`.
3. **Along-strike crest troughs.** Conversely, 9,147 pixels of R0's own 1-px
   ridge crest receive kernel weight `k < 0.40` (and 3,448 receive `k = 0`).

**Single-variable experimental control.** All three SPACING variants clear the
same 610 widest multi-dot fault corridors at `d_cat >= 3.0 px` (8,508 R0 dots on
26,156 manifold px; 13,253 crest px) and re-pack **each corridor to its own
exact R0 dot count `n_c`**. All 29,146 remaining R0 dots (including all 1,611
inherited `2 < d_cat < 3` diagonal-collar dots) stay untouched; 100 % of dots
remain on `scored_h19_5`; 5-km block-density CV holds at 0.899 across all arms.

| arm | n_dots | moved (`% R0`) | sym diff (`% R0`) | dots on 1-px crest | `ΔT_crest` (1-D) | `ΔT_manifold` (2-D) | across-strike twins |
|---|---|---|---|---|---|---|---|
| Parent R0 | 37,654 | 0 (0.00 %) | 0.00 % | 24,691 | 0.0 (base 52,607.6) | 0.0 (base 76,725.9) | 4,802 |
| **`strike`** | 37,654 | 5,444 (14.46 %) | 28.92 % | **26,755** (+2,064) | **+1,119.1** | −109.9 | **3,859** (−943) |
| **`poisson`** | 37,654 | 4,800 (12.75 %) | 25.50 % | 25,286 (+595) | +240.1 | **+286.3** | 4,921 (+119) |
| **`lattice`** | 37,654 | 5,195 (13.80 %) | 27.59 % | 25,095 (+404) | +138.1 | −27.3 | 4,961 (+159) |

---

## Card S1 — `strike` (`h33-h33-2-b2-spacing-strike-20261023-37910355`, primary Slot 1)

**Hypothesis.** Unmapped test fault traces (`G`) behave as 1-D curvilinear
features concentrated near the medial crest of R0's multi-physics corridors.
Replacing across-strike flank twins (`r_across = 4.2 px`) with tighter
along-strike crest dots (`r_along = 2.0 px`, ranked by exact submodular marginal
kernel gain `ΔT_crest`) raises live DTI at fixed dot count 37,654.

**Mechanism.** Along a continuous 1-px fault trace, tightening dot pitch from
~3.0 px to ~2.0–2.2 px raises mid-span kernel weights `1 − d/3` across 3–5
adjacent fault pixels simultaneously ("line-like truth lowers that bar", brief
sec.2) and cushions against ~100–150 m cross-strike uncertainty. Suppressing
flank twins within 420 m across strike eliminates redundant coverage of single
400 m-spaced GeoDAWN potential-field anomalies.

**The non-fault / structural process that could mimic or defeat it.**
1. *Dipping normal-fault offset (structural defeat mode):* Basin-and-Range
   normal faults dip 45°–60° basinward. Airborne gravity and magnetic horizontal
   gradients peak over the hanging-wall basement step 200–500 m downdip of the
   surface scarp. Where `h19-5` merges the updip scarp ridge and downdip
   potential-field ridge into one wide corridor, collapsing dots onto the medial
   crest can pull mass *away* from the updip surface fault trace.
2. *Non-fault linear mimic:* Range-interior dikes, welded-tuff cooling joints,
   or incised alluvial fan-head channels produce coherent 1-D crests that earn
   zero test credit regardless of along-strike packing.

**Predicted sign and size (MODEL).** Central **+0.006**, band **−0.004 … +0.011**
DTI change relative to R0 (calibrated from R0's ~12 % active-corridor truth
fraction: `+1,119.1` crest kernel units yields +0.006 under crest-localized
truth, +0.011 if damage-zone corridors carry 1.8× fault prevalence, and −0.004
if dipping-fault surface traces sit systematically on corridor flanks).

**Falsifier.** A live delta inside ±0.010 shows corridor-level crest/anisotropic
re-spacing is below public-chunk resolution; a delta ≤ −0.010 falsifies medial
crest localization in favor of dip-offset or distributed multi-strand geometry.
If `strike` gains ≥ +0.010, Slot 2 runs `poisson` to verify the gain exceeds
isotropic de-clustering by ≥ 0.005.

---

## Card S2 — `poisson` (`h33-h33-2-b2-spacing-poisson-20261023-95c51e18`, conditional Slot 2)

**Hypothesis.** Because GeoDAWN's 400 m line spacing introduces ~150–300 m
positional uncertainty across the full 2-D width of `h19-5` corridors, uniform
isotropic 2-D blue-noise covering (farthest-point Poisson-disk seeding + 6
discrete Voronoi/Lloyd medoid iterations per corridor) raises 2-D kernel
coverage without betting on crest centrality.

**Mechanism.** Greedy scanline NMS leaves uneven inter-dot gaps and boundary
crowding. Centroidal Voronoi relaxation equalizes Voronoi cell radii across all
26,156 corridor pixels, raising total 2-D corridor kernel coverage by `+286.3`
units (the highest 2-D manifold coverage of any arm, including R0).

**The non-fault process that could mimic it.** Broad corridors frequently reflect
coalesced alluvial fan aprons, pediment-basin transitions, or wide aeromagnetic
pluton aureoles rather than distributed fault zones; spreading dots uniformly
across those 2-D footprints dilutes crest density where sharp Quaternary scarps
do exist.

**Predicted sign and size (MODEL).** Central **+0.001**, band **−0.002 … +0.004**
DTI change (no-evidence regime expected; serves as the exact isotropic spacing
control against `strike` and any future `DEDUPE` arm).

**Falsifier.** Beating `strike` by ≥ 0.008 falsifies 1-D medial-crest
localization and proves test fault truth is scattered across the full 2–4 px
corridor width. Scoring below R0 by ≥ 0.010 falsifies centroidal relaxation over
R0's original rank-greedy traversal.

---

## Card S3 — `lattice` (`h33-h33-2-b2-spacing-lattice-20261023-dd652665`, crystallographic control — hold)

**Hypothesis.** Snapping multi-dot corridors onto an equilateral triangular /
hexagonal covering lattice (`a = 3.20 px`, row pitch `2.771 px` — Kershner's
optimal disk-covering geometry for `R = 3.0 px` kernels) removes scanline
packing defects while avoiding the catastrophic off-ridge false positives of
upstream `13GEMSDOE` `r13-lattice-s5` (0.0904 = **CLAIM**).

**Mechanism.** In an infinite 2-D region, a hexagonal lattice minimizes worst-case
distance to the nearest dot (`a / √3 = 1.85 px`, `k ≥ 0.38`). Intersecting that
lattice strictly with `scored_h19_5` corridors at matched per-corridor count
isolates pure periodic lattice geometry from support drift.

**The non-fault process that could mimic it.** Sinuous Basin-and-Range fault
traces curve across range-front salients and relay ramps at wavelengths of
0.5–3 km; a rigid UTM-aligned periodic lattice beats in and out of phase with
curved 2–3 px corridors (`ΔT_manifold = −27.3` vs `+286.3` for adaptive Voronoi
`poisson`), creating periodic coverage Moiré along oblique strikes.

**Predicted sign and size (MODEL).** Central **0.000**, band **−0.003 … +0.003**
DTI change. Hold unsubmitted unless both `strike` and `poisson` move ≥ 0.010.

**Falsifier.** Matching or beating `poisson` on live score would show periodic
covering suffices and adaptive Voronoi relaxation adds nothing; losing by ≥ 0.010
confirms lattice phase mismatch on curved geological traces.

---

# Part II — RELIEF axis (prior session on disk: `r10`, `r15`, `r15s`)

Equal-area terciles of `det_elev` (band 12; cuts at −142.9 m and +38.8 m) over
the 5,164,312-px relief domain:

| class | name | area (px) | catalogue px | known-fault density /1000 px | R0 dots | R0 density /1000 px | R0 share ÷ catalogue share |
|---|---|---|---|---|---|---|---|
| 0 | basin | 1,721,438 | 18,499 | 10.75 | 7,692 | 4.47 | 0.67 |
| 1 | piedmont | 1,721,437 | 24,711 | **14.35** | 15,742 | 9.14 | 1.03 |
| 2 | range front | 1,721,437 | 17,684 | 10.27 | 14,204 | 8.25 | **1.30** |

## Card R1 — `r10` (`h33-h33-2-b2-relief-r10-20261023-366c87ca`)
* **Hypothesis:** Moving 10 % of R0's dots (3,765) from range-front to structured piedmont (`|∇det_elev| ≥ 12.2`, `d_cat ≥ 3 px`) aligns mass with mapped fault density.
* **Mechanism:** Quaternary basin-margin scarps are preserved and mapped in piedmont alluvial fans, whereas range-interior DEM edges often reflect bedrock fabric/fractures.
* **Non-fault mimic:** Fan-head incisions, bar-and-swale roughness, and fan-bedrock contacts mimic scarp edges; catalogue density also reflects mapping exposure bias.
* **Predicted change (MODEL):** **+0.003** (band **−0.012 … +0.018**).
* **Falsifier:** Live delta inside ±0.010 closes RELIEF; delta ≤ −0.010 proves leaving R0's `scored_h19_5` ridge support loses more placement precision than class reallocation gains.

## Card R2 — `r15` (`h33-h33-2-b2-relief-r15-20261023-6aa774ce`)
* **Hypothesis & Mechanism:** Same range-front → piedmont move at 1.5× dose (5,648 dots = 15 %) to test dose linearity.
* **Non-fault mimic:** Same as `r10`, plus super-linear depletion of true range-front faults at 15 % removal.
* **Predicted change (MODEL):** **+0.004** (band **−0.017 … +0.027**).
* **Falsifier:** Failure to scale ~1.5× above a positive `r10` result falsifies class allocation.

## Card R3 — `r15s` (`h33-h33-2-b2-relief-r15s-20261023-5f0ae851`)
* **Hypothesis & Mechanism:** Redefines terciles by `det_elev_slope` (band 19; cuts 1.8 and 8.1), moving 15 % (5,648 dots) from high-slope to mid-slope (15.34 vs 12.98 catalogue px / 1000 px).
* **Non-fault mimic:** Slope is collinear with DEM edge strength, confounding geomorphic class with local edge magnitude.
* **Predicted change (MODEL):** **+0.001** (band **−0.007 … +0.011**).
* **Falsifier:** Moving ≥ 0.010 while `r10` is null proves slope-edge placement rather than geomorphic relief allocation.

---

## Report-only diagnostics caveat (both axes)

* **Catalogue hide-and-recover (PROXY):** Constant at `0.0384` across R0 and all
  three SPACING arms (`n = 18,296` withheld positives, 95 % Wilson CI `[0.0357, 0.0413]`),
  because every newly placed dot satisfies `d_cat >= 3.0 px` by construction and
  SPACING locks `d_cat < 3.0` dots.
* **Off-catalogue SGMC control (PROXY):** USGS SGMC bedrock fault recall within
  3 px (`n = 63,121` off-collar px; https://doi.org/10.3133/ds1052) is `0.2015`
  on R0, `0.2004` (`strike`), `0.2014` (`poisson`), `0.2003` (`lattice`), vs
  `0.1764` on random null (surrogate DTI ~1.29× random null). Reported, never
  used as a gate or score.
