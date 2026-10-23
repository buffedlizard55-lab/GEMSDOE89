# CURRENT STATE

- **Parent (verified):** `h33-h33-2-b2` — 37,654 unit dots, sha256 `c55bafc470054e82…`,
  restored byte-identical from the owner's mirror and matching the `sha256_zeros`
  recorded for R0 in the upstream ledger. Live **0.2778 = CLAIM** (no receipt).
- **Best receipt (this repo):** none. No file built here has been scored.
- **TOP_PUBLIC:** `____` — **not supplied**; the human must fill it from the
  leaderboard with a date. It is the only valid target number.
- **Slots this week:** `__ / __` — **not supplied**; quota is 3 scored
  submissions per rolling week per entity, plus one final blind choice.
- **Axes built:** RELIEF (r10, r15, r15s) and **SPACING** (hd3p0, hd4p0,
  hd3p0-along — this session). SPACING had no `(axis, value)` pair anywhere in
  the recovered ledger. The parent is a saturated hard disk: minimum dot-to-dot
  distance 2.828 px, 30.3 % of dots at exactly that distance, median 3.0 px.
- **Week:** 2026-10-23. Deadline **2026-12-03** (≈6 weeks) — *UNVERIFIED*: the
  competition page may not be fetched under its terms.

## Next 3 slots (detail in `SLOT_PLAN.md`)

| # | file | predicted (MODEL) | what the result would change |
|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-spacing-hd4p0-20261023-0cf9025b.tif` | +0.025 (−0.012…+0.061) | ≥ +0.010 → coverage area converts to score, run the dose arm; ≤ −0.012 → close SPACING and CONCENTRATION |
| 2 | `releases/h33-h33-2-b2-spacing-hd3p0-20261023-08f80fd3.tif` | +0.006 (−0.003…+0.015) | linear dose-response → the mechanism holds; super-linear → positional drift |
| 3 | `releases/h33-h33-2-b2-spacing-hd3p0-along-20261023-f3d99d91.tif` | +0.008 (−0.004…+0.021) | along > isotropic at matched dose → TRACKB becomes the next axis |

**Files built this session:** 3 SPACING variants × 2 encodings (NaN-outside and
zeros-outside twins), all passing every MUST gate; see `ledger/submissions.csv`
and `registry/build_report_spacing_*.json`.

**What only the human can supply:** TOP_PUBLIC + date; slots used/available; a
receipt score for each submitted file (`receipt_score`, `receipt_date` in the
ledger); confirmation of the 2026-12-03 deadline; and a decision on the
data-exposure item in `IRREGULARITIES.md`.
