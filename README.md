# CURRENT STATE

- **Parent (verified):** `h33-h33-2-b2` — 37,654 unit dots, sha256
  `c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9`.
  The pinned artifact was re-read and matched exactly on 2026-10-23; live
  **0.2778 = CLAIM** (no submission receipt in this repo). The original R0
  generation recipe is still unavailable; no approximate parent was used.
- **Best receipt (this repo):** none. All RELIEF and SPACING variants are
  **BUILT / unscored**.
- **TOP_PUBLIC:** `____` — **not supplied**; the human must fill it from the
  leaderboard with a date. It is the only valid target number.
- **Slots this week:** `__ / __` — **not supplied**. Quota is 3 scored
  submissions per rolling week per entity, plus one final blind choice.
- **Axis this continuation:** **SPACING**, the only unused weekly axis in the
  recovered R0 ledger (MASS, CONCENTRATION, SNAP, PRUNE and RELIEF pairs already
  exist). Three new arms share one removal set and matched gap anchors; each
  changes 3,765 dots (9.9989%) and preserves 5 km block counts exactly.
- **Week:** 2026-10-23. Deadline **2026-12-03** — **UNVERIFIED**; the human must
  confirm it on the competition page.

## Next 3 slots (conditional; detail in `SLOT_PLAN.md`)

| # | file | predicted (MODEL) | what the result would change |
|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-spacing-poisson10-20261023-986e9365.tif` | +0.002 (−0.008…+0.012) | ≥ +0.010 supports generic de-overlap; inside ±0.010 is no evidence; ≤ −0.010 stops the remaining SPACING arms |
| 2 | `releases/h33-h33-2-b2-spacing-strike10-20261023-442188a4.tif` | +0.003 (−0.010…+0.016) | strike−Poisson ≥ +0.010 supports line continuity; within ±0.010 means no orientation evidence |
| 3 | `releases/h33-h33-2-b2-spacing-lattice10-20261023-9d7dc126.tif` | +0.001 (−0.008…+0.010) | run only after a ≥ +0.010 result above; otherwise hold the slot for DEDUPE |

**Built in this continuation:** 3 SPACING variants × 2 encodings (NaN outside
and zeros-outside fallback), all passing every MUST gate after re-reading from
disk; see `ledger/submissions.csv` and `docs/SUBMIT.md`. The three earlier
RELIEF variants remain available and unscored.

**What only the human can supply:** TOP_PUBLIC + date; slots used/available;
receipt scores/dates for submitted files; confirmation of the 2026-12-03
deadline; the data-exposure decision in `IRREGULARITIES.md`; and, if a reviewer
requires parent-level reproducibility, the original R0 recipe.
