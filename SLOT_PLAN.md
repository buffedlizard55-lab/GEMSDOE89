# SLOT PLAN — one page, session GEMSDOE89 (2026-10-23)

Deadline **2026-12-03** (UNVERIFIED — confirm on the competition page; ≈6 weeks,
41 days). Quota: 3 scored submissions per rolling week per entity + one final
blind submission (https://docs.nlr.gov/docs/fy26osti/96647.pdf). Slots
used/available: **`__ / __`** (human fills before spending any). Treat any public
delta within ±0.010 of R0 (0.2778 = **CLAIM**) as no evidence.

## Next 3 slots, in order

| # | File | Predicted live change | Submit only if | What the result changes |
|---|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-spacing-strike-20261023-37910355.tif` | **+0.006** MODEL (−0.004…+0.011) | gates green (verified) | Primary test of 1-D fault-crest along-strike spacing on `scored_h19_5` (+1,119 crest kernel units, 0 regional drift). ≥ +0.010 → run `spacing-poisson` in Slot 2 to isolate anisotropy vs 2-D relaxation. Inside ±0.010 → close SPACING; pivot Slot 2 to `MASSm10uniq`. ≤ −0.010 → dipping-fault traces sit off-crest; build DIP-DOUBLET below. |
| **2A** *(if #1 ≥ +0.010)* | `releases/h33-h33-2-b2-spacing-poisson-20261023-95c51e18.tif` | **+0.001** MODEL (−0.002…+0.004) | Slot 1 scored ≥ 0.2878 | Disambiguates Slot 1: `strike − poisson ≥ +0.005` confirms 1-D strike anisotropy; `poisson ≈ strike` shows isotropic Voronoi de-clustering suffices. |
| **2B** *(if #1 in ±0.010)* | `releases/h33-h33-2-b2-MASSm10uniq-20261023-beed130f.tif` | **+0.002** MODEL (−0.010…+0.010) | Slot 1 inside ±0.010 | Orthogonal denominator test (drop 3,765 lowest-unique-credit R0 dots → 33,889). ≥ +0.010 → run `MASSm20uniq` in Slot 3; ≤ −0.010 → test-set `G` is heavier than modelled, retiring drop-only pruning. |
| **3** | *hold*, or `…-MASSm20uniq-…-87ec6213.tif` | **+0.004** MODEL (−0.020…+0.021) | Slot 2B ≥ +0.010 (else hold for wk 2) | 20 % dose-linearity check on MASS; otherwise hold the 3rd weekly slot for `relief-r10` (`366c87ca`, +0.003 MODEL) or wk 2. Hold `spacing-lattice` (`dd652665`, pred 0.000) and `MASSm10rand` (`7a4c49b6`, pred −0.002) as controls. |

## Weeks to the deadline (default 1-entity schedule, ≤18 weekly slots left)

| Week | Dates | Plan |
|---|---|---|
| 1 | 10-23 → 10-29 | Slot 1 (`spacing-strike`), then conditional Slot 2A (`spacing-poisson`) or Slot 2B (`MASSm10uniq`); hold Slot 3 unless 2B ≥ +0.010 |
| 2 | 10-30 → 11-05 | Score `relief-r10` (`366c87ca`) and upstream `SNAP 2p0px-g0p02` (`b2019f55`); build DIP-DOUBLET or CREST-DEDUPE |
| 3–4 | 11-06 → 11-19 | Combine the two best orthogonal axes (e.g., `spacing-strike` + `MASSm10uniq` if both positive), one factor per step |
| 5 | 11-20 → 11-26 | Confirm the composite candidate directly against its immediate parent; freeze primary final file + fallback |
| 6 | 11-27 → 12-03 | Re-validate grid/format/hashes of **both** frozen files from disk; submit one final blind choice |

## Proposed better axes (mechanism · confounder · falsifier) — not built this session

1. **CREST-DEDUPE (1-D NMS crest marginal-loss pruning without refill).** Rank R0's
   37,654 dots by exact marginal kernel loss on the 1-px NMS fault crest
   (`gemsdoe.metric.marginal_gain_remove` against `crest` rather than self-disc
   area) and drop the 4,000–5,500 flank twins without refilling. *Mechanism:*
   combines `MASSm10uniq`'s denominator reduction with `spacing-strike`'s crest
   selectivity, sacrificing <0.3 % of 1-D crest credit `T`. *Confounder:* couples
   count reduction with flank pruning — controlled directly against `MASSm10uniq`
   and `spacing-strike`. *Falsifier:* fails to beat both single-axis parents by
   ≥ 0.005 live.
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
