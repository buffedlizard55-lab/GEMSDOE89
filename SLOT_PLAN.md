# SLOT PLAN — GEMSDOE89 (`SPACING` Session, 2026-10-23)

- **Timeline:** 2026-10-23 -> **2026-12-03** (`UNVERIFIED` deadline) = **41 days (~5.9 weeks)** -> **~18 rolling weekly slots** (1 entity @ 3 slots/wk) + **1 blind final submission**.
- **Baseline:** Parent R0 `h33-h33-2-b2` (`c55bafc4...`), rebuilt bit-for-bit, **0.2778 = CLAIM** (no `RECEIPT` in this repo). `TOP_PUBLIC`: `____` (human must supply). Weekly slots used: `__ / 3` (human must supply).
- **Rule:** Live changes `< 0.01` (`|Delta| < 0.010`) are treated as **no evidence** (indistinguishable from test-mask variance without a repeat-submission `RECEIPT`).

## Next 3 Slots (Ordered) & Decision Tree

1. **Slot 1 — `h33-h33-2-b2-spacing-alongstrike-20261023-3b263c7a.tif`** (`SPACING=alongstrike`, `5,222/37,654 = 13.87%` moved, `n=37,654`, `MODEL` `+0.002`, band `-0.003..+0.006`).
   - *Why first:* Purest single-variable test of along-strike spacing on R0's 834 multi-dot `h19_5` fault strands (`>=6` dots): 100% ridge retention, zero count change, zero 5 km CV drift (`0.8991 -> 0.8991`), smallest downside (`-0.003`).
2. **Slot 2 — Conditional on Slot 1 `RECEIPT` `S1` (relative to R0 `0.2778` `CLAIM`):**
   - **If `S1 >= 0.2878` (`Delta >= +0.010`):** Submit **`h33-h33-2-b2-spacing-poisson-20261023-ff167173.tif`** (`20.29%` moved, `MODEL` `-0.010`, band `-0.032..+0.004`) to test whether 2D lateral corridor spacing (`+-150 m`) adds gain beyond 1D strand equalization.
   - **If `0.2678 < S1 < 0.2878` (`|Delta| < 0.010`, expected):** **Close `SPACING`** (along-strike packing is within noise; do **not** spend slots on `poisson` or `lattice`). Pivot Slot 2 to an orthogonal unscored axis already built: **`MASS m10uniq`** (`releases/h33-h33-2-b2-MASSm10uniq-20261023-beed130f.tif`, `MODEL` `+0.002`, ceiling `+0.0105`), **`RELIEF r10`** (`releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif`, `MODEL` `+0.003`), or upstream **`SNAP 2p0px-g0p02`** (`GEMSDOE84`, `b2019f55`, `MODEL` `+0.007..+0.018`).
   - **If `S1 <= 0.2678` (`Delta <= -0.010`):** Greedy `r=2.8 px` strand endpoints carry live signal; freeze strand positions and never re-space along `h19_5`.
3. **Slot 3 — Conditional on Slot 2 `RECEIPT` `S2`:**
   - **If `poisson` ran and `S2 >= S1 + 0.010`:** Submit **`h33-h33-2-b2-spacing-lattice-20261023-454c9098.tif`** (`19.40%` moved, `MODEL` `-0.007`) to test hexagonal crystal packing (`nn<3 px` `-32.8%`).
   - **Otherwise:** **HOLD Slot 3** (or spend on R0 baseline `RECEIPT` verification if `h33-h33-2-b2` still lacks a verified screenshot/receipt) to conserve weekly quota for the higher-upside axes below.

## Proposed Better Axes (Not Built This Session)

None of the pure rearrangements of R0's existing 37,654 binary ridge dots (`SPACING`, `RELIEF`, `CONCENTRATION`, drop-only `MASS`) has `MODEL` central expectation `>= +0.010`. Reaching `+0.01..+0.03+` requires new fault geometry or continuous gradient calibration:

| Proposed Axis | Mechanism | Confounder / Non-Fault Mimic | Falsifier |
|---|---|---|---|
| **`RELAY-BRIDGE`** (en-echelon stepover linking) | Basin-and-Range normal faults segment across 0.3–1.5 km relay ramps (`h19_5` breaks at transfer zones where single-method gradients dip); bridging co-linear strand tips (`<=12 px`, strike diff `<=20 deg`) puts mass on unmapped relay faults outside the 3 px catalogue collar. | Bridging across alluvial channel scarps or volcanic dike swarms linking unrelated ridges, inflating `P` without hitting `G`. | Live `RECEIPT` `<= R0` or `PROXY` on withheld multi-segment catalogue relays fails to beat random tip pairs of equal length. |
| **`TRACKB-DIP-OFFSET`** (dip-slip potential-field shift) | Range-bounding normal faults dip 45–60 deg basinward, shifting gravity/magnetic horizontal-gradient maxima 200–500 m (`2–5 px`) hanging-wall-ward of the surface trace; shifting `h19_5` dots up-slope toward `det_elev_slope` footwall breaks aligns `P` with surface traces. | Sub-vertical strike-slip faults and volcanic contacts have near-zero dip offset; shifting them moves dots off the trace. | Live `RECEIPT` drops by `>= 0.005` vs R0, or footwall-shifted dots lose SGMC off-catalogue `PROXY` coverage. |
| **`REPEAT-CALIBRATION`** (R0 baseline `RECEIPT` anchor) | Score exact parent `h33-h33-2-b2` (`baeae321...`) once under current receipted governance to convert `0.2778` from `CLAIM` to `RECEIPT` and bound single-slot noise. | Consumes 1 of ~18 remaining weekly slots with zero expected score gain. | Live `RECEIPT` differs from `0.2778` by `> 0.005` (invalidating `CLAIM`-anchored deltas across the ledger). |
