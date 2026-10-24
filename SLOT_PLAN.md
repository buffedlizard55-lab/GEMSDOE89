# SLOT PLAN — GEMSDOE89 (SNAP directional corner, 2026-10-24)

- **Timeline:** 2026-10-24 → **2026-12-03** (deadline `UNVERIFIED`, human confirms) ≈ 40 days ≈ **17 rolling slots** (`3/week`) + **1 blind final**. Slots used this week: `__ / 3` (human supplies).
- **Incumbent:** Parent R0 `h33-h33-2-b2`, rebuilt byte-exactly today (`c55bafc4…` zeros / `baeae321…` NaN, 37,654 unit dots, 10/10 fetchable pins verified). Live **0.2778 = CLAIM** (no receipt). **TOP_PUBLIC** `____` (date `____`).
- **Evidence rule:** `|Δ| < 0.01` on public chunks is **no evidence**. `PROXY` / canary / surrogate / SGMC are report-only instruments, never gates, never scores.
- **Why the queue changed:** all six weekly axes already hold ≥3 built values (MASS 6, CONCENTRATION 12, PRUNE 7, SNAP 6, RELIEF 3, SPACING 3) and **none has a live receipt**, so a 22nd unrelated build buys little. The SNAP factorial was `{window} x {gate}` only; the measured fact that the undirected 2 px arm moves **15,585 dots up-slope and 15,670 down-slope** (50/50) shows the crest-side question was never tested and costs exactly one predicate to test (`ledger/MECHANISM_CARDS.md` Part VII).

## Next 3 slots, in order

| # | File | Predicted (`MODEL`) | What the receipt changes |
|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-snapdirfw2p0-20261024-dc578b2f.tif` | band −0.019…+0.057 (sign prior weak **by design**) | Half of a matched pair. Alone it is unreadable; with Slot 2 it returns the **sign of R0's crest-side bias** — a transferable fact about the parent, not just a file. |
| **2** | `releases/h33-h33-2-b2-snapdirhw2p0-20261024-5cccfc1d.tif` | band −0.019…+0.057 | The **exact mirror**. `fw − hw ≥ +0.010` ⇒ truth is on the footwall side of the HG maximum (re-aim every placement rule up-slope). `hw − fw ≥ +0.010` ⇒ hanging-wall side (dip-offset story confirmed with the opposite sign). Both `≤ R0 − 0.010` ⇒ **the crest is right**; retreat to R0 and stop spending slots on position. Both inside `±0.010` ⇒ SNAP is saturated at 1–2 px. |
| **3** | conditional: `releases/h33-h33-2-b2-snapdirfw1p0-20261024-373c8fd6.tif` if `fw2p0 − hw2p0 ≥ +0.010`; else the block fork `releases/h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136.tif` (+0.008, band −0.006…+0.018) **or** `…-CONC5kmcat10-…-2dc19377.tif` (+0.009, wider band); else **HOLD** the slot | +0.015 / +0.008 / +0.009 | Dose (`1 px` vs `2 px`) if the direction effect is real; otherwise the first independent test of block-level priors. If both Slot 1–2 land `≤ R0 − 0.010`, no position arm gets another slot this cycle. |

**Override the human may prefer:** upload the crest anchor `…-snap2p0px-g0p00-20261023-69db3aae.tif` in place of one arm and read the pair as `dirfw2p0` vs `dirhw2p0` **vs crest** — three-way, but the crest arm alone still cannot separate "direction" from "dose".

## Weeks to the deadline

| Week | Dates | Plan |
|---|---|---|
| 1 | 10-24 → 10-30 | Slots 1 + 2 as a pair (never one without the other); keep the 3rd slot spare for a receipt or for the block fork. |
| 2 | 10-31 → 11-06 | Slot 3 from Week 1's reading; record every `receipt_score` + `date` in `ledger/submissions.csv` (all 24 `GEMSDOE89` rows are currently `BUILT`/unscored). |
| 3–4 | 11-07 → 11-20 | Combine **only** axes with live receipts `≥ +0.010`, one factor at a time, each child diffed against its direct parent. |
| 5 | 11-21 → 11-27 | Confirm the composite against its parent; freeze primary + `-zeros.tif` fallback. |
| 6 | 11-28 → 12-03 | Re-validate format + hashes of both twins; submit **1 blind final**. Fallback if nothing beats R0: R0 itself (`baeae321…`). |

## Proposed better axes (mechanism · confounder · falsifier) — **not** built this session

| Axis | Structural mechanism | Non-fault confounder / mimic | Falsifier |
|---|---|---|---|
| **RELIEF basin residual (`0→1`, `2→0`)** — untested direction | The catalogue records *surface-mapped* faults, which cluster at range fronts (R0's lift vs catalogue: range **1.30**, piedmont 1.03, basin **0.67**); new-fault truth is the residual inventory, so it should be enriched where mapping exposure is worst — basin fill | Basinal gravity/magnetic anomalies are closed bodies, basement-top steps and alluvial-thickness changes: pure mass with no surface trace | Receipt `≤ R0 − 0.010`, or the matched `2→0` arm beating `0→1` |
| **Redundancy prune (geometric MASS)** | With a 3 px kernel, two dots 2.8 px apart cannot both be the argmax: the loser is pure mass. Rank dots by *union coverage lost* if removed, a label-free criterion | Redundant dots sit on the thickest, most reliable ridges — pruning them removes the best-located mass | Fails to beat `MASSm10uniq` (`beed130f`) by `≥ 0.005`, or loses to its random null `m10rand` |
| **Anisotropic SPACING (stretch along-strike, tighten across-strike)** at fixed count | The positional error budget is anisotropic: 400 m flight lines smear *across* strike, so along-strike stations can be wider while across-strike needs density. Kernel is isotropic; the error is not | Strike estimates from R0's own strands are noisy and circular (the ridge field is what defines strike) | Loses to isotropic `poisson` (`ff167173`) or `lattice` (`454c9098`) at matched count |
| **4 px directional dose** (this session's own follow-up) | If `fw − hw ≥ +0.010`, the correction scale may be 1.7–4.2 px, not 2 px | Wider windows reach unrelated parallel gradients (the `2p0px` arm's own warning: PROXY 0.0384 → 0.0152) | Dose response non-monotone between 1 / 2 / 4 px |
| **TRACKB (Phase 2, still zero builds)** | Strike-consistent traces `≥ 1 km` from R0's top-ranked dots, as GeoJSON + raster with one evidence paragraph per trace | Trace building is exactly where a human's prior should dominate; a raster is not the deliverable | Not a weekly-slot candidate unless the human decides; needs a geologist's read of the paragraphs |
