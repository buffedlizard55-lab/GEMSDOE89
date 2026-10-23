# SLOT PLAN — one page, session GEMSDOE89 (2026-10-23)

Deadline **2026-12-03** (`UNVERIFIED` — confirm on the competition page; ≈6 weeks, 41 days).
Quota: **ONE entity = 3 scored submissions per rolling week + ONE final blind submission**
(https://docs.nlr.gov/docs/fy26osti/96647.pdf). Slots left this week / total: **`__ / __`**
(human fills before spending a slot). Live deltas `|Δ| < 0.01` count as no evidence.

## Next 3 slots in order (orthogonal axes first; never burn two slots on collinear arms)

| # | File | Axis / value | Predicted change (MODEL) | What the live result changes |
|---|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-spacing-alongstrike-20261023-3b263c7a.tif` | `SPACING alongstrike` | **+0.002** (−0.003…+0.006) | Zero cross-strike downside; tests 1-D geodesic + exact kernel 1-swap vs northern-BFS thinning (`0.2778` CLAIM). `>= +0.010` → adopt geodesic emitter permanently; inside `±0.010` → on-ridge spacing is saturated (98.7 %). |
| **2** | `releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif` | `RELIEF r10` | **+0.003** (−0.012…+0.018) | Orthogonal macro-allocation probe (10 % range-front → structured piedmont). `>= +0.010` → run `RELIEF r15` (`6aa774ce`) in Slot 3 for 1.5× dose-response; inside `±0.010` → close `RELIEF`. |
| **3** | `releases/h33-h33-2-b2-spacing-poisson-20261023-ff167173.tif` *(or `RELIEF r15` if Slot 2 ≥ +0.010; else hold)* | `SPACING poisson` | **−0.010** (−0.032…+0.004) | Definitive test of GeoDAWN 400 m line-spacing lateral offset (`±150 m` 2-D corridor). `<= −0.010` → proves test faults hug `h19_5` within `<=150 m` (retires `poisson` and `lattice` `454c9098`); `>= +0.010` → proves `>=250 m` scarp step-out and opens `lattice`. |

Do **not** upload `poisson` (`ff167173`) and `lattice` (`454c9098`) in the same week: both spread mass laterally across the fault corridor and share the same centerline-loss risk.

## Weeks to the deadline (one entity, 3 slots/week)

| Week | Dates | Plan |
|---|---|---|
| **1** | 10-23 → 10-29 | Slot 1 (`SPACING alongstrike`) + Slot 2 (`RELIEF r10`); Slot 3 = `RELIEF r15` if `r10 >= +0.010`, else `SPACING poisson` (or unscored upstream `SNAP 2p0px-g0p02` / `MASS -10pct`). |
| **2** | 10-30 → 11-05 | Score remaining orthogonal single-axis arms (`SNAP`, `MASS`, `CONCENTRATION` from ledger if still unscored); build top proposed axis (`DEDUPE`) below. |
| **3–4** | 11-06 → 11-19 | Combine the two best confirmed axes one factor at a time (e.g., best emitter/snap + best redundancy prune), holding parent-diff gates strict. |
| **5** | 11-20 → 11-26 | Confirm the composite candidate directly against its immediate parent; freeze **one primary final file** and **one conservative fallback**. |
| **6** | 11-27 → 12-03 | Re-validate CRS, transform, footprint NaN mask, `[0,1]` range, and SHA-256 of **both** final files from disk; submit one blind before the deadline. |

## Proposed better axes (mechanism · confounder · falsifier) — not built this session

1. **`DEDUPE` (exact marginal-credit redundancy prune; highest expected value).**
   *Mechanism:* Under `DTI = T / (0.2T + 0.2(S−M) + 0.8|G|)`, R0's 11,415 dots at `d = 2.828 px` and Y-junction triplets share overlapping `R = 3.0 px` kernels; ranking dots by exact removal gain `gemsdoe.metric.marginal_gain_remove` against the multi-layer ridge prior and dropping the most redundant 12–18 % *without* refill cuts `0.2(S−M)` while preserving `T`.
   *Confounder:* Alters both total dot count (`MASS`) and local pair density (`SPACING`), so it must be benchmarked directly against `MASS -10pct` (`2cde51f3`) and `SPACING alongstrike` (`3b263c7a`).
   *Falsifier:* Failure to beat `MASS -10pct` by `>= +0.005` on live chunks falsifies kernel-overlap redundancy as the primary denominator drag.

2. **`RELAY-BRIDGE` (strike-collinear step-over & gap bridging `<= 600 m`).**
   *Mechanism:* `h19_5` has 26,645 disconnected 8-connected components because alluvial fans bury short (`300–600 m`) segments between collinear scarps; bridging co-striking (`Δθ <= 15°`) strand tips separated by `4–7 px` (swapping out isolated 1-px noise fragments to hold `S = 37,654` fixed) targets structurally continuous fault systems (Faulds interaction prior on fault tips/relays).
   *Confounder:* Bridges across stream breaches of erosional hogbacks look geometrically identical to breached relay ramps.
   *Falsifier:* Live delta `< +0.010` vs R0 proves unmapped test faults do not preferentially occupy short collinear gaps between `h19_5` fragments.

3. **`REPEAT-CALIBRATION` (single deliberate twin upload only if slack permits).**
   *Mechanism:* Upstream history burned `>= 8` slots on accidental byte-identical repeats that returned identical public scores; verifying deterministic public-chunk scoring vs Phase-1 private variance requires zero slots if historical receipts already confirm exact determinism—check receipts first before ever spending a slot.
   *Confounder:* Public determinism says nothing about public-to-private chunk variance.
   *Falsifier:* Any two receipts for the same `sha8` differing by `> 0.0001` would indicate stochastic evaluation.
