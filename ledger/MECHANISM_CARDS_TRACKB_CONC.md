# Mechanism cards — TRACKB (Phase 2 trace inventory + controlled structural
# concentration), session `arena/7fd24ce1-gemsdoe89` (2026-10-24)

Parent for every card: **R0 = `h33-h33-2-b2`** (`GEMSDOE32` lineage; 37,654 unit-mass
dots; zero on catalogue, 1,611 inherited dots in the `2 < d_cat < 3 px` collar).
Rebuilt bit-for-bit this session (`tools/rebuild_r0.py`: `c55bafc4…` zeros /
`baeae321…` NaN). Owner-reported live **0.2778 = CLAIM** — no receipt stored here.

**Evidence discipline.** Every local number below is **MODEL** or **PROXY**, never a live
score. `|Δlive| < 0.01` is *no evidence*. Organizer page (format/metric):
https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ ;
GeoDAWN ~kernel-radius lineament uncertainty:
https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7 ; "new fault"
includes newly mapped geometry of existing systems:
https://community.drivendata.org/t/where-do-you-draw-the-line/11536 .

## Why TRACKB, and why it is deliberately NOT a weekly-slot candidate

The scored axes (`MASS`, `CONCENTRATION`, `SNAP`, `PRUNE`, `RELIEF`, `SPACING`) are
already saturated in `ledger/submissions.csv` and **21 GEMSDOE89 pairs sit `BUILT
(unscored)`** waiting on receipts — the binding constraint is live feedback, not more
files. TRACKB is the one unbuilt axis and it targets **Phase 2 ($250k)**, where experts
rescore against labels they expand *after reviewing submitted faults*. Its primary
product is a geologist-reviewable trace inventory; the three rasters are a controlled,
count-preserving **Phase-1 probe of the same structural prior**, offered so the human
*can* test it but explicitly held out of the weekly slot queue.

### The Phase-2 inventory (`releases/h33-h33-2-b2-TRACKB-traces-20261024.geojson`)

R0 dots are linked across **≤ 4 px (400 m) step-overs** — one GeoDAWN Area-2 flight-line
spacing — into chains; a chain is kept as a "trace" when its geodesic arc ≥ **1 km** and
sinuosity (arc / endpoint chord) ≤ **1.6** (strike-consistent). **1,520 traces** result
(median 1.8 km, p90 4.3 km, max 27.9 km), ranked by structural significance
`length × mean(unique_credit)` — i.e. literally built from R0's **top-ranked dots**,
where `unique_credit` is the metric-derived flat-prior ranking (`gemsdoe.mass`).
Each trace carries **one evidence paragraph** (length, strike, TMI-horizontal-gradient /
isostatic-gravity-slope / detrended-DEM-scarp strengths, distance to nearest mapped fault,
and a review prompt). A 48-trace human-readable atlas is
`evidence/TRACKB_trace_atlas_20261024.md`. **23 % of traces lie within 300 m of a mapped
fault** — candidate newly-mapped geometry of existing systems; **77 % are frontier
lineaments** an expert could add to the label set.

### The three rasters (nested, count-preserving)

A single seeded off-trace permutation (the inherited collar is **frozen**, so this is not a
PRUNE edit) and a single ranked, separation-feasible corridor placement list are truncated
at **10 / 20 / 30 % of R0**. Off-trace dots move into a **±300 m (3 px) cross-strike
corridor** around the traces at mutual separation ≥ 2.8 px and `d_cat ≥ 3 px`. Total dot
count is held fixed at **37,654** — the DTI change isolates the *structural prior* from any
MASS effect. **1,611 collar dots frozen; min added-dot separation 2.83 px; added `d_cat ≥ 3 px`.**

## The confounder that sets the prediction: the H19 surrogate can only price the COST

Jitter MODEL (`registry/build_reports_trackb_conc.json`): hold out a seeded 16.5 % of eligible
H19-5 strands as surrogate truth, shift each laterally by σ px (GeoDAWN mislocation), and
score DTI(variant) − DTI(R0). Because **R0 is itself derived from H19-5**, this surrogate is
near-optimal for R0 and prices the **on-ridge coverage cost** of moving dots off short
fragments; it structurally *cannot* value the Phase-2 benefit of pointing experts at
mappable structures or of new-fault truth on long traces. Read it as a **floor**, not a
point forecast. Catalogue hide-and-recover PROXY and surrogate DTI are **invariant** at
`0.03842` / `0.00671` (every edit is at `d_cat ≥ 3 px`, IRREGULARITIES item 4) — confirming
no catalogue leakage.

| σ (px) | TR10 | TR20 | TR30 |
|---|---|---|---|
| 0.0 (ridge-locked truth) | −0.043 | −0.091 | −0.137 |
| 1.8 | −0.011 | −0.029 | −0.046 |
| **2.5 (central)** | **−0.002** | **−0.012** | **−0.021** |
| 3.0 (kernel-radius uncertainty) | +0.001 | −0.005 | −0.013 |

The loss **shrinks toward break-even as uncertainty grows** — the corridor dots hedge
cross-strike mislocation. At the brief's stated ~kernel-radius (3 px) uncertainty, the
low dose is break-even; higher doses pay more coverage cost.

---

## Card TB1 — `tr10` (`…TRACKB-TR10-20261024-32211f1f`) — lowest-cost Phase-1 probe
- **Hypothesis:** New-fault truth is laterally continuous and strike-consistent at ≥1 km; relocating the 10 % least-structural off-trace dots into the trace corridors adds kernel coverage where experts will expand labels, at near-zero Phase-1 cost at realistic GeoDAWN uncertainty.
- **Mechanism:** 3,765 off-trace dots (10 %) → ±300 m of ≥1 km traces, count fixed, `d_cat ≥ 3 px`, `r_sep ≥ 2.8 px`; H19 on-ridge coverage 0.730 → 0.672.
- **Non-fault mimic:** Cross-strike corridor dots may land on parallel volcanic/dike/shoreline edges; if test truth hugs short H19 fragments, moving off them loses T with no offset gain.
- **Predicted sign/size (`MODEL`):** central **−0.002**, band **−0.043 … +0.001** (σ = 0 … 3 px). Central is *no evidence*; the negative tail is the measurable on-ridge cost. Phase-2 upside is unpriced.
- **Falsifier:** A Phase-1 receipt `≤ −0.010`, or a Phase-2 rescore that does not expand labels along the submitted traces, retires the corridor-concentration mechanism (keep the inventory, drop the raster move).

## Card TB2 — `tr20` (`…TRACKB-TR20-20261024-5da46626`) — dose
- **Hypothesis / mechanism:** Same rule at 20 % (7,531 dots); H19 coverage 0.730 → 0.610. Tests linear dose-response of the coverage cost.
- **Non-fault mimic:** As TB1, amplified; secondary ridges in the corridor recruit non-tectonic scarps.
- **Predicted sign/size (`MODEL`):** central **−0.012**, band **−0.091 … −0.005**. Held unless `tr10` surprises `≥ +0.010`.
- **Falsifier:** Failing to beat `tr10` confirms the cost scales with dose; do not advance.

## Card TB3 — `tr30` (`…TRACKB-TR30-20261024-c8a264b5`) — high dose / held
- **Hypothesis / mechanism:** 30 % (11,296 dots); H19 coverage 0.730 → 0.545. The upper bound on corridor reallocation capacity.
- **Non-fault mimic:** Dominant — at 30 % most moved dots sit ~2.8 px off the ridge, so on-ridge truth is systematically under-covered.
- **Predicted sign/size (`MODEL`):** central **−0.021**, band **−0.137 … −0.013**. Strongest predicted Phase-1 loss; held strictly.
- **Falsifier:** A `≥ +0.010` receipt would overturn the H19-surrogate floor and validate strong structural concentration — otherwise retire.

---

### Shared caveats
- All three encode **NaN-outside** (primary) and **zeros-outside** (`-zeros.tif`, fallback) twins; the human uploads at most one per slot. **None should consume a weekly slot by default.**
- The corroboration composite that ranks legal corridor pixels has footprint-masked catalogue AUC 0.543 (raw 0.813 is a data-availability artifact — IRREGULARITIES item 14); known faults are masked in scoring and the operator only re-ranks legal `d_cat ≥ 3 px` pixels, never selecting regions.
- Phase-2 benefit depends on undisclosed expert review behaviour; the inventory is a set of *hypotheses for a structural geologist*, not confirmed faults.
