# CURRENT STATE

- **Parent (verified):** `h33-h33-2-b2` — 37,654 unit dots, sha256 `c55bafc470054e82…`,
  byte-identical to the `sha256_zeros` recorded for R0 in the upstream ledger.
  Live **0.2778 = CLAIM** (no submission receipt in this repo).
- **Best receipt (this repo):** none. No file built here has been scored.
- **TOP_PUBLIC:** `____` — **not supplied**; the human must fill it from the
  leaderboard with a date. It is the only valid target number.
- **Slots this week:** `__ / __` — **not supplied**; the brief's quota is
  3 scored submissions per rolling week per entity, plus one final blind choice.
- **Axis this session:** **SPACING** (chosen: after RELIEF (3 pairs, prior
  session), MASS (3), PRUNE (7), SNAP (3) and CONCENTRATION (3) all had ledger
  pairs, SPACING was the only named weekly-slot axis with none; TRACKB remains
  Phase 2-only). Three matched-count, local, seeded re-spacings of R0.
- **Week:** 2026-10-23. Deadline **2026-12-03** (≈6 weeks, 41 days) — *UNVERIFIED*:
  the competition page may not be fetched under its terms, so the human must
  confirm the date.

## Next 3 slots (detail in `SLOT_PLAN.md`)

| # | file | predicted (MODEL) | what the result would change |
|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-spacing-strike3-20261023-59029fa7.tif` | +0.004 (−0.013…+0.024) | ≥ +0.010 → strike geometry is live, run slot 2; inside ±0.010 → close SPACING |
| 2 | `releases/h33-h33-2-b2-spacing-pd3-20261023-6b481dc1.tif` | +0.003 (−0.016…+0.025) | both spacing arms ≥ +0.010 → build DEDUPE; only strike3 wins → pivot to TRACKB |
| 3 | hold, or `…spacing-lat3-t1p5…0dbab41e.tif` | −0.001 (−0.008…+0.012) | structure-free control; submit only to bracket a positive spacing result |

**Files built this session:** 3 SPACING variants × 2 encodings (NaN-outside and
zeros-outside twins), all passing every MUST gate; see `ledger/submissions.csv`
and `ledger/MECHANISM_CARDS_SPACING.md`. The 3 RELIEF variants from the prior
session remain on disk, unscored and unmodified.

**What only the human can supply:** TOP_PUBLIC + date; slots used/available; a
receipt score for each submitted file (`receipt_score`, `receipt_date` in the
ledger); confirmation of the 2026-12-03 deadline; and a decision on the
data-exposure item in `IRREGULARITIES.md`.
