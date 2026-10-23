# SLOT PLAN — one page, session GEMSDOE89 (2026-10-23)

Deadline **2026-12-03** (UNVERIFIED — confirm on the competition page; ≈6 weeks,
41 days). Quota: 3 scored submissions per rolling week per entity + one final
blind submission (https://docs.nlr.gov/docs/fy26osti/96647.pdf). Slots
used/available: **`__ / __`** (human fills before spending any). Treat any public
delta within ±0.010 of R0 (0.2778 = **CLAIM**) as no evidence.

## Next 3 slots, in order

| # | File | Predicted live change | Submit only if | What the result changes |
|---|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-spacing-strike-20261023-37910355.tif` | **+0.006** MODEL (−0.004…+0.011) | gates green (verified) | Primary test of 1-D fault-crest along-strike spacing on `scored_h19_5` (+1,119 crest kernel units, 0 regional drift). ≥ +0.010 → run `spacing-poisson` in Slot 2 to isolate anisotropy vs 2-D relaxation. Inside ±0.010 → close SPACING; pivot Slot 2 to `relief-r10`. ≤ −0.010 → dipping-fault traces sit off-crest; build DIP-DOUBLET below. |
| **2A** *(if #1 ≥ +0.010)* | `releases/h33-h33-2-b2-spacing-poisson-20261023-95c51e18.tif` | **+0.001** MODEL (−0.002…+0.004) | Slot 1 scored ≥ 0.2878 | Disambiguates Slot 1: `strike − poisson ≥ +0.005` confirms 1-D strike anisotropy; `poisson ≈ strike` shows isotropic Voronoi de-clustering suffices. |
| **2B** *(if #1 in ±0.010)* | `releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif` | **+0.003** MODEL (−0.012…+0.018) | Slot 1 inside ±0.010 | Orthogonal macro-allocation test (10 % range-front → piedmont). ≥ +0.010 → run `relief-r15` in Slot 3; ≤ −0.010 → leaving `scored_h19_5` support loses precision, retiring off-manifold moves. |
| **3** | *hold*, or `…-relief-r15-…-6aa774ce.tif` | **+0.004** MODEL (−0.017…+0.027) | Slot 2B ≥ +0.010 (else hold for wk 2) | Dose-linearity check on RELIEF (`r15 ≈ 1.5 × r10`). Otherwise preserve the 3rd weekly slot for DEDUPE or an unscored upstream MASS/SNAP arm. Hold `spacing-lattice` (`dd652665`, pred 0.000) as a crystallographic control. |

## Weeks to the deadline (default 1-entity schedule, ≤18 weekly slots left)

| Week | Dates | Plan |
|---|---|---|
| 1 | 10-23 → 10-29 | Slot 1 (`spacing-strike`), then conditional Slot 2A (`spacing-poisson`) or Slot 2B (`relief-r10`); hold Slot 3 unless 2B ≥ +0.010 |
| 2 | 10-30 → 11-05 | Score best unscored upstream single-axis arm (`MASS -10pct` `2cde51f3` or `SNAP 2p0px-g0p02` `b2019f55`); build DEDUPE / DIP-DOUBLET |
| 3–4 | 11-06 → 11-19 | Combine the two best orthogonal axes (e.g., winning SPACING/SNAP + winning MASS/DEDUPE), one factor per step |
| 5 | 11-20 → 11-26 | Confirm the composite candidate directly against its immediate parent; freeze primary final file + fallback |
| 6 | 11-27 → 12-03 | Re-validate grid/format/hashes of **both** frozen files from disk; submit one final blind choice |

## Proposed better axes (mechanism · confounder · falsifier) — not built this session

1. **DEDUPE (exact submodular redundant-dot pruning without refill).** Rank R0's
   37,654 dots on `scored_h19_5` by exact marginal crest-kernel loss
   (`gemsdoe.metric.marginal_gain_remove` on the 1-px NMS crest) and drop the
   4,000–5,500 most redundant across-strike flank twins *without* refilling.
   *Mechanism:* removes ~12 % of `0.2(S − M)` denominator mass while sacrificing
   <0.3 % of 1-D crest credit `T`. *Confounder:* couples `MASS` reduction with
   `SPACING` flank removal — controlled directly by comparing against upstream
   `MASS -10pct` and this session's fixed-count `spacing-strike`. *Falsifier:*
   fails to beat `MASS -10pct` by ≥ 0.005 live.
2. **DIP-DOUBLET (updip scarp vs downdip potential-field offset).** Where DEM
   scarp ridges (`det_elev_slope`) and potential-field horizontal gradients
   (`iso_grav_anom_hg`, `tmi_hg`) run parallel 200–400 m apart, shift corridor
   dots toward the updip topographic edge rather than the medial axis.
   *Mechanism:* on 45°–60°-dipping Basin-and-Range normal faults, the hanging-wall
   basement step sits downdip of the surface fault trace. *Confounder:* antithetic
   faults dip toward the range. *Falsifier:* fails to beat `spacing-strike` by
   ≥ 0.010 when `spacing-strike` underperforms R0.
3. **TIP-BRIDGE (collinear relay / step-over linking).** Place 1,500–2,500 dots
   exclusively across collinear 300–800 m gaps between aligned `scored_h19_5`
   terminations (using Faulds step-over geometry strictly as a fault-interaction
   prior, brief sec.2). *Confounder:* echelon dikes or incised fan channels.
   *Falsifier:* live delta < −0.005 vs R0.
