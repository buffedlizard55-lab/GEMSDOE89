# CURRENT STATE

- **Parent (verified):** `h33-h33-2-b2` — 37,654 unit dots, sha256 `c55bafc470054e82…`,
  byte-identical to the `sha256_zeros` recorded for R0 in the upstream ledger.
  Live **0.2778 = CLAIM** (no submission receipt in this repo).
- **Best receipt (this repo):** none. No file built here has been scored.
- **TOP_PUBLIC:** `____` — **not supplied**; the human must fill it from the
  leaderboard with a date. It is the only valid target number.
- **Slots this week:** `__ / __` — **not supplied**; the brief's quota is
  3 scored submissions per rolling week per entity, plus one final blind choice.
- **Axis this session:** **RELIEF** (chosen: the only axis with zero
  `(RELIEF, value)` pairs in the recovered ledger — MASS 3, PRUNE 7, SNAP 3,
  CONCENTRATION 3 upstream).
- **Week:** 2026-10-23. Deadline **2026-12-03** (≈6 weeks, 41 days) — *UNVERIFIED*:
  the competition page may not be fetched under its terms, so the human must
  confirm the date.

## Next 3 slots (detail in `SLOT_PLAN.md`)

| # | file | predicted (MODEL) | what the result would change |
|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif` | +0.003 (−0.012…+0.018) | ≥ +0.010 → relief allocation is real, run r15 for dose-response; inside ±0.010 → close the axis |
| 2 | `releases/h33-h33-2-b2-relief-r15-20261023-6aa774ce.tif` | +0.004 (−0.017…+0.027) | linear vs r10 → mechanism; super-linear loss → density over-stripped |
| 3 | hold, or `…relief-r15s…5f0ae851.tif` | +0.001 (−0.007…+0.011) | isolates slope-definition vs direction |

**Files built this session:** 3 variants × 2 encodings (NaN-outside and
zeros-outside twins), all passing every MUST gate; see `ledger/submissions.csv`.

**What only the human can supply:** TOP_PUBLIC + date; slots used/available; a
receipt score for each submitted file (`receipt_score`, `receipt_date` in the
ledger); confirmation of the 2026-12-03 deadline; and a decision on the
data-exposure item in `IRREGULARITIES.md`.
