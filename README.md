# CURRENT STATE

- **Parent (verified & rebuilt from recipe):** `h33-h33-2-b2` — 37,654 unit-mass dots,
  rebuilt bit-for-bit from `scored_h19_5.tif` via `tools/rebuild_r0.py`, matching
  upstream `sha256_zeros = c55bafc470054e82…` and `sha256_nan = baeae3219bba6a19…`.
  Live **0.2778 = CLAIM** (no submission receipt in this repo).
- **Best receipt (this repo):** none. Every historical score in `ledger/submissions.csv`
  is `CLAIM` until `receipt_score` and `date` are filled from a submission receipt.
- **TOP_PUBLIC:** `____` — **not supplied**; the human must fill it from the
  leaderboard with a date (the `2026-10-03` snapshot `0.3195` in upstream notes is
  20 days old and is not used as a target).
- **Slots left (this week / total):** `__ / __` — **not supplied**; quota is ONE entity =
  3 scored submissions per rolling week + 1 blind final submission. Deadline
  **2026-12-03** (`UNVERIFIED` — human must confirm on the competition page).
- **Axis this session:** **SPACING** (`alongstrike`, `poisson`, `lattice` at matched
  count 37,654 — selected because `MASS`, `CONCENTRATION`, `SNAP`, `PRUNE`, and
  `RELIEF` already had built `(AXIS, value)` pairs in `ledger/submissions.csv`, while
  `SPACING` had zero).

## Next 3 slots (detail in `SLOT_PLAN.md`)

| # | file | predicted (MODEL) | what the result would change |
|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-spacing-alongstrike-20261023-3b263c7a.tif` | +0.002 (−0.003…+0.006) | `>= +0.010` → adopt 1-D geodesic/kernel-optimal emitter; inside `±0.010` → on-ridge spacing saturated |
| 2 | `releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif` | +0.003 (−0.012…+0.018) | `>= +0.010` → relief class transfer works, run `r15` (`6aa774ce`); inside `±0.010` → close `RELIEF` |
| 3 | `releases/h33-h33-2-b2-spacing-poisson-20261023-ff167173.tif` *(or `r15` / hold)* | −0.010 (−0.032…+0.004) | `<= −0.010` → test truth hugs `h19_5` within `<=150 m` (retires `poisson` + `lattice`); `>= +0.010` → proves `>=250 m` offset |

**Files on disk (`releases/`):** 3 `SPACING` variants + 3 prior `RELIEF` variants (each
with NaN-outside primary `.tif` and `-zeros.tif` fallback = 12 files), all passing every
MUST gate; see `ledger/submissions.csv` and `docs/SUBMIT.md`.
