# SLOT PLAN — GEMSDOE89 (integrated CONCENTRATION sessions, 2026-10-23)

- **Timeline:** 2026-10-23 → **2026-12-03** (`UNVERIFIED`) ≈ 41 days ≈ **18 rolling slots** (one entity × 3/week) + one blind final. Slots used: `__ / 3` (human supplies).
- **Baseline:** R0 `h33-h33-2-b2`, byte-exact (`c55bafc4…`; `baeae3219…`), **0.2778 = CLAIM**. Best receipt: none. `TOP_PUBLIC`: `____` (human + date).
- **Rule:** `|Δ| < 0.01` is **no evidence**. PROXY/MODEL/canary/SGMC never gate and are never called scores.

## Candidate families added (all hashes/axis-value triples are distinct)

| family | values | central MODELs | queue role |
|---|---|---|---|
| 5 km catalogue-prior + shared potential-field `q` | `cat10` / `cat20` / `cat10away` | +0.009 / +0.019 / −0.009 | primary / conditional dose / conditional sign control |
| 2 km catalogue-prior + H19 exact sequential marginals | `m3765` / `m5648` / `m7531` | +0.0024 / −0.0028 / −0.0126 | held separate mechanism; larger doses need lower-dose receipts |

The 2 km family is **not a clean scale ablation**: its placement differs from
the 5 km `q` rule. Its H19 coverage and crowding counter-indicators are recorded
in `IRREGULARITIES.md` item 12; full cards are in
`ledger/MECHANISM_CARDS_CONCENTRATION.md`.

## Next 3 slots, in order

| # | File | Predicted live change | What the result changes |
|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-CONC5kmcat10-20261023-2dc19377.tif` | **+0.009** MODEL (−0.010…+0.038) | ≥ 0.2878 → `cat20`; ≤ 0.2678 → prior may be inverted, run `cat10away`; otherwise no 5 km evidence, do not infer a 2 km scale effect. |
| **2** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` | **+0.028** MODEL (−0.028…+0.084) | ≥ 0.2878 → SNAP is live and earns the conditional dose if slot 1 does not take it; ≤ 0.2678 → retire SNAP/EM-crest placement. |
| **3** | priority: `cat20` if slot 1 ≥ 0.2878; `cat10away` if ≤ 0.2678; else `snap1p4px-g0p00` if slot 2 ≥ 0.2878; else `MASSm10uniq` **or HOLD** | +0.019 / −0.009 / +0.028 / +0.002 MODEL | Confirms allocation dose/sign first, then SNAP dose; otherwise changes question to drop-only MASS or preserves the slot. |

Never spend two slots on the same dose question in one week. A null 5 km receipt
does not make the 2 km files a clean scale read; any later 2 km upload must be
justified as the separate H19-placement mechanism in its card.

## Weeks to the deadline

| week | dates | plan |
|---|---|---|
| 1 | 10-23 → 10-29 | slots 1 + 2; keep one spare for late receipts |
| 2 | 10-30 → 11-05 | conditional slot 3; record every receipt and exact file hash |
| 3-4 | 11-06 → 11-19 | combine only axes with receipts ≥ +0.010, one factor at a time |
| 5 | 11-20 → 11-26 | confirm winner against its parent; freeze final + fallback |
| 6 | 11-27 → 12-03 | re-validate both final candidates; one blind final submission |

## Proposed better axes — mechanism · confounder · falsifier (not built)

| Axis | Mechanism | Confounder / mimic | Falsifier |
|---|---|---|---|
| **FRONTIER** | target zero-catalogue blocks with high structural-edge density | edges also mark contacts/basin fill | fails to beat `cat10away` by ≥0.005 |
| **COVERAGE-NEUTRAL CONC** | shift block mass while constraining H19 ΔT ≈ 0 | joint optimization also changes spacing | cannot beat the matched CONC parent by ≥0.005 |
| **DEDUPE** | remove least exact-unique-credit dots, no refill | de-clustering is also spacing | fails to beat count-matched MASS by ≥0.005 |
| **RELAY-BRIDGE** | connect compatible en-echelon H19 tips on unmapped relays | channels/dike swarms bridge tips too | receipt ≤ R0 or PROXY loses to random tip pairs |
| **REPEAT-CALIBRATION** | exact R0 resubmission converts CLAIM to RECEIPT | costs a slot; zero expected raster gain | receipt differs from 0.2778 by >0.005 |
