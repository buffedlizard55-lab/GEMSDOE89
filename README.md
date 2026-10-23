# CURRENT STATE

- **Parent (rebuilt & verified):** `h33-h33-2-b2` — 37,654 unit-mass dots, rebuilt
  byte-identically from its recorded recipe (`tools/rebuild_r0.py`) to sha256
  `c55bafc470054e82…` (`-zeros`) and `baeae3219bba6a19…` (`-nan`), with
  37,654/37,654 dots on `scored_h19_5`. Live **0.2778 = CLAIM** (no submission
  receipt in `ledger/`).
- **Best receipt (this repo):** none. No file built here has a logged receipt.
- **TOP_PUBLIC:** `____` — **not supplied**; the human must fill it from the
  leaderboard with a date. It is the only valid target number.
- **Slots left (this week / total):** `__ / __` — **not supplied**; quota is
  3 scored submissions per rolling week per entity + 1 final blind submission
  (https://docs.nlr.gov/docs/fy26osti/96647.pdf).
- **Axis this session:** **SPACING** (`strike`, `poisson`, `lattice` — zero
  `SPACING` pairs existed in `ledger/submissions.csv`; prior `RELIEF` files are
  retained on disk and in the ledger).
- **Date:** 2026-10-23. Deadline **2026-12-03** (≈6 weeks, 41 days) — *UNVERIFIED*:
  automated access to drivendata.org is prohibited by site terms, so the human
  must confirm the date on the competition page.

## Next 3 slots (detail in `SLOT_PLAN.md`)

| # | file | predicted (MODEL) | what the result would change |
|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-spacing-strike-20261023-37910355.tif` | +0.006 (−0.004…+0.011) | ≥ +0.010 → run `spacing-poisson` next; inside ±0.010 → close SPACING, pivot to `relief-r10`; ≤ −0.010 → dipping-fault offset dominates |
| 2 | `…-spacing-poisson-…-95c51e18.tif` *(if #1 ≥ +0.010)* or `…-relief-r10-…-366c87ca.tif` *(if #1 null)* | +0.001 / +0.003 | isolates 1-D strike anisotropy vs 2-D Voronoi relaxation, or tests range→piedmont class allocation |
| 3 | hold, or `releases/h33-h33-2-b2-relief-r15-20261023-6aa774ce.tif` *(if r10 ≥ +0.010)* | +0.004 (−0.017…+0.027) | dose-response check on RELIEF; otherwise save slot for wk 2 (`MASS -10pct` / `DEDUPE`) |

**Files built this session:** 3 `SPACING` variants × 2 encodings (NaN-outside
primary + zeros-outside fallback), all passing every MUST gate (plus the 3 prior
`RELIEF` × 2 twins retained); see `ledger/submissions.csv` and `docs/SUBMIT.md`.

**What only the human can supply:** `TOP_PUBLIC` + date; weekly/total slots
remaining; `receipt_score` and `receipt_date` in `ledger/submissions.csv` after
any upload; confirmation of the 2026-12-03 deadline; and a decision on the
upstream public-mirror exposure flagged in `IRREGULARITIES.md`.
