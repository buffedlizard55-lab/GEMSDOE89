# SLOT PLAN — GEMSDOE89 / SNAP factorial completion (2026-10-24)

- **Entity/quota:** one entity, 3 scored submissions per rolling week + 1 blind final. Slots used/left this week: `__ / 3` (human supplies). **TOP_PUBLIC:** `____` (date `____`).
- **Parent:** R0 `h33-h33-2-b2`, 37,654 dots, byte-verified; live `0.2778` = **CLAIM**, no receipt. Deadline `2026-12-03` remains **UNVERIFIED**; human confirms.
- **Decision rule:** only live `|Δ| >= 0.010` is evidence. Central values below are **MODEL**, not scores; gated/gateless MODEL assumptions differ (`IRREGULARITIES.md` item 14), so use matched receipts, not central-model subtraction.

## Next 3 slots, in order

| # | File | Predicted change | What the result changes |
|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-snap1p4px-g0p01-20261024-afc60a25.tif` | **+0.0120** (`−0.0060…+0.0301`) | Intermediate-gate, diagonal-window probe. `>=0.2878` supports SNAP; `<=0.2678` rejects this gated correction; between them is no evidence. |
| **2** | `releases/h33-h33-2-b2-snap1p4px-g0p00-20261023-e1474851.tif` | **+0.0278** (`−0.0278…+0.0834`) | Exact matched gateless control: same parent, response and 1.42 px window; only gate changes. Compare receipts directly with Slot 1. |
| **3** | **Conditional:** `…-snap1p0px-g0p01-20261024-2916ec2d.tif` if Slot 1 beats Slot 2 by `>=0.010`; otherwise `…-snap2p0px-g0p00-20261023-69db3aae.tif` if either SNAP arm is `>=0.2878`; otherwise `…-CONC5kmcat20-20261023-4d229938.tif` **or HOLD** | `+0.0076` / `+0.0278` / `+0.019` | Gated win → fixed-gate 1 px window control. Any SNAP signal without a gated win → 2 px gateless dose. Two null SNAP receipts → stop spending on SNAP and take one orthogonal large-effect concentration probe (or preserve quota). |

**Held:** `1p0px-g0p02` (`384435e6`, central `+0.0022`) is a minimum-dose boundary/control, not a default slot. Do not submit both twins; `-zeros.tif` is fallback only. Record every upload's receipt and date.

## Weeks to deadline (assuming human confirms 2026-12-03)

| Window | Action |
|---|---|
| 10-24 → 10-30 | Slots 1–2; reserve Slot 3 until both receipts are recorded. |
| 10-31 → 11-06 | Conditional Slot 3; update parent/axis decisions only on `>=0.010` changes. |
| 11-07 → 11-20 | Combine only the two best axes with live `>=+0.010` evidence; change one factor from a named parent at a time. |
| 11-21 → 11-27 | Confirm the composite against its direct parent; freeze primary and fallback. |
| 11-28 → 12-03 | Re-validate both final twins' hashes/format; human chooses one final file blind. |

## Proposed better axes — not built this session

| Axis | Mechanism | Confounder / mimic | Falsifier |
|---|---|---|---|
| **SIGNED-SCARP SNAP** | Basin-facing signed elevation scarps reject unsigned TMI/gravity contacts that look sharp but lack normal-fault topography. | Fan channels and shoreline terraces share the sign; detrended-DEM resolution smooths low scarps. | Does not beat matched unsigned SNAP by `>=0.010`, or loses a catalogue strand-holdout to an unsigned control. |
| **RELAY-BRIDGE** | Connect en-echelon tips `<=12 px` with strike difference `<=20°` where breaching faults form (https://www.osti.gov/servlets/purl/1249065). | Streams/dikes bridge the same tips; added mass may earn no truth credit. | Live `<R0+0.010`, or strand-holdout loses to random tip pairs. |
| **COVERAGE-NEUTRAL CONC** | Reallocate km-scale mass while constraining H19 `ΔT≈0`, separating block prior from centerline retention. | Joint optimization silently changes spacing and local edge alignment. | Fails to beat matched CONC by `>=0.005` under the same live evidence rule. |
