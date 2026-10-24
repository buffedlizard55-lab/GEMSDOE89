# SLOT PLAN — GEMSDOE89 / directional SNAP pair + completed SNAP factorial (2026-10-24)

- **Entity/quota:** one entity, 3 scored submissions per rolling week + 1 blind final. Slots used/left this week: `__ / 3` (human supplies). **TOP_PUBLIC:** `____` (date `____`).
- **Parent:** R0 `h33-h33-2-b2`, 37,654 dots, rebuilt byte-exactly again today (`c55bafc4…` / `baeae321…`); live `0.2778` = **CLAIM**, no receipt. Deadline `2026-12-03` remains **UNVERIFIED**.
- **Decision rule:** only live `|Δ| ≥ 0.010` is evidence. Central values are **MODEL**, not scores; gated and gateless arms use different MODEL assumptions (`IRREGULARITIES.md` item 15), so compare matched receipts, never central-model subtraction. PROXY/canary/SGMC never gate.
- **Queue state:** every weekly axis holds ≥ 3 built values at this parent (`SNAP` 12, `CONCENTRATION` 9, `SPACING` 3, `RELIEF` 3, `MASS` 3, upstream `PRUNE` 1–4 px) plus **4 Phase-2 `TRACKB` builds** (`t150add` `5a09404f`, `t150swap` `8cfcbe4c`, `t150link` `eded7713` dual-phase R0-consolidating 150-trace arms + `top12` `fb156257` review extract) and **none has a live receipt**, so the scarce good is *readable pairs*.
- **Why this week's pair changed:** the SNAP factorial (`{window} × {gate}`) is complete, and a measurement made this session shows the undirected crest arm `2p0px-g0p00` moves **15,585 dots up-slope / 15,670 down-slope** (`share_upslope = 0.498`): R0 is direction-neutral w.r.t. the HG maximum, so no existing arm could detect a crest-side preference, and the proposed global dip-offset translation has no bias to correct (`IRREGULARITIES.md` item 16).

## Next 3 slots, in order (primary week)

| # | File | Predicted (`MODEL`) | What the receipt changes |
|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-snapdirfw2p0-20261024-dc578b2f.tif` | −0.019…+0.056 (sign prior weak **by design**) | Half of a matched pair; alone it is unreadable. |
| **2** | `releases/h33-h33-2-b2-snapdirhw2p0-20261024-5cccfc1d.tif` | −0.019…+0.057 | The **exact mirror** (same response, window, gate 0.00, targets, count; only the ±60° half-window differs). `fw − hw ≥ +0.010` ⇒ truth sits **footwall-side** of the HG maximum; reverse ⇒ **hanging-wall side**; both `≤ R0 − 0.010` ⇒ **the crest is right** and no position arm gets another slot this cycle; both inside `±0.010` ⇒ SNAP is saturated at 1–2 px. |
| **3** | Conditional: `dirfw1p0` (`373c8fd6`, +0.015) if `fw − hw ≥ +0.010`; else the gate-pair head `1p4px-g0p01` (`afc60a25`, +0.0120); else `conc-12p8km-int10` (`bcade136`, +0.008) or `CONC5kmcat10` (`2dc19377`, +0.009); else **HOLD** | +0.015 / +0.012 / +0.008–0.009 | Dose vs direction; or selectivity-vs-dose; or the first independent block-prior test. |

**Alternative week (same two slots, different question):** the gate pair `1p4px-g0p01` (`afc60a25`, +0.0120) against its matched gateless control `1p4px-g0p00` (`e1474851`, +0.0278) — reads *selectivity vs dose*, not direction. Do **not** run both pairs in one week (4 files > quota). **Held:** `1p0px-g0p02` (`384435e6`, +0.0022) is a minimum-dose boundary control, not a default slot. Never submit both twins; `-zeros.tif` is fallback only.

## Weeks to the deadline

| Window | Action |
|---|---|
| 10-24 → 10-30 | Slots 1–2 as a pair; reserve Slot 3 until both receipts are recorded. |
| 10-31 → 11-06 | Conditional Slot 3 (or the alternative gate pair); record every `receipt_score` + `date`. |
| 11-07 → 11-20 | Combine **only** axes with live `≥ +0.010` receipts, one factor at a time from a named parent. |
| 11-21 → 11-27 | Confirm the composite against its direct parent; optionally spend 1 slot confirming `TRACKBt150add` (`5a09404f`, `P1 +0.000 / P2 +0.012 MODEL`; or `t150swap` if `MASSm10uniq ≥ +0.010`) costs `< 0.005` Phase 1 DTI. |
| 11-28 → 12-03 | Re-validate both final twins; human chooses **1 blind final** ($50k P1 + $250k P2). If nothing beats R0, submit R0 (`baeae321…`) or `TRACKBt150add` (`5a09404f`). |

## Proposed better axes (mechanism · confounder · falsifier) — **not** built this session

| Axis | Structural mechanism | Non-fault confounder / mimic | Falsifier |
|---|---|---|---|
| **SIGNED-SCARP resp (residual of the old proposal)** | Use a *DEM-signed* scarp response instead of an unsigned HG contact, so basin-facing scarps only | Fan channels, shorelines and roads share the sign; 2 px DEM smoothing hides low scarps | Does not beat the matched unsigned arm by `≥ 0.010` |
| **RELIEF basin residual (`0→1`, `2→0`)** | Catalogue records *surface-mapped* faults, which cluster at range fronts (R0 lift vs catalogue: range 1.30, piedmont 1.03, basin 0.67); new-fault truth is the residual, so it should be enriched where exposure is worst | Basinal gravity/magnetic anomalies are closed bodies and basement steps: pure mass | `≤ R0 − 0.010`, or the matched `2→0` arm beating `0→1` |
| **Redundancy prune (geometric MASS)** | Two dots 2.8 px apart cannot both be the argmax under a 3 px kernel: the loser is pure mass. Rank by union coverage lost if removed — label-free | Redundant dots sit on the thickest, best-located ridges | Fails to beat `MASSm10uniq` (`beed130f`) by `≥ 0.005`, or loses to `m10rand` |
| **Anisotropic SPACING** | Error budget is anisotropic: 400 m flight lines smear *across* strike, so along-strike stations can be wider at fixed count | Strike estimated from R0's own strands is circular | Loses to isotropic `poisson` / `lattice` at matched count |
| **RELAY-BRIDGE** | Bridge co-linear / en-echelon tips (`≤ 12 px`, strike diff `≤ 20°`) where breaching faults nucleate | Streams and dikes bridge the same tips with no truth credit | Live `< R0 + 0.010`, or strand-holdout loses to random tip pairs |
| **COVERAGE-NEUTRAL CONC** | Reallocate km-scale mass while holding H19 `ΔT ≈ 0`, separating block prior from centreline retention | Joint optimisation silently changes spacing and local alignment | Fails to beat the matched CONC arm by `≥ 0.005` |
| **TRACKB-EXTEND / REPEAT-CALIBRATION** | Deliver the remaining qualifying traces for expert review; or submit byte-exact R0 once to convert `0.2778` CLAIM → RECEIPT | Reviewer attention favours long traces; the calibration slot buys no climb | Traces 13–19 no better than length-matched random strands; receipt differs from `0.2778` by `> 0.005` |
| **COMPOSITE-WINNER+TRACKB** *(gate: ≥1 weekly `RECEIPT ≥ +0.010`)* | Layer `TRACKBt150add`'s zero-drop continuous `≥ 1 km` trace infill (`+1,415 px`, `k = 1.00`) directly onto the best live-confirmed weekly variant for the single blind final ($50k P1 + $250k P2) | Linear shoreline/volcanic mimics in target blocks could add `~9.4` `S − M` pixels per mimic trace | Confirmation-slot receipt `< parent_winner − 0.005` retires trace infill and freezes the pure weekly winner |
| **REPEAT-CALIBRATION (R0 receipt)** | Submit byte-exact R0 once to convert `0.2778` CLAIM → RECEIPT before freezing composites | Spends 1 of ~17 remaining public slots without advancing climb | Receipt differs from `0.2778` by `> 0.005` (invalidates upstream baseline anchor) |
## Addendum 2026-10-24 (BSTP session) — queue unchanged

`gems89-bstp40-20261024-2e7e8a8f` (axis `BSTP`, 147-row merged ledger) is **BUILT /
NEGATIVE**: format- and uniqueness-gated, but HOLDOUT-DTI −0.0254
[−0.0296, −0.0210] vs the per-fold parent (`segment-holdout-v1`), so it
takes **no slot** and does not displace the SNAP directional pair above.
Its two sibling variants were withdrawn (TIFs deleted). Full record:
`registry/run_card_bstp40.json`, `ledger/MECHANISM_CARDS_BSTP.md`.