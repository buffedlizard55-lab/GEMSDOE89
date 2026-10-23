# CURRENT STATE

- **Parent (recipe-rebuilt, byte-verified):** `h33-h33-2-b2` — 37,654 unit dots.
  `tools/rebuild_r0.py` rebuilds it from `scored_h19_5.tif` (`dot_thin(r=2.8)` +
  `d_cat > 2.0` flank prune) and matches **both** pins byte-for-byte:
  `sha256_zeros` `c55bafc470054e82…`, `sha256_nan` `baeae3219bba6a19…`; the SNAP
  session independently reproduced the same bytes from the mask alone and
  corrected three broken manifest pins + flagged one UNVERIFIED
  (`IRREGULARITIES.md` items 1, 8). Live **0.2778 = CLAIM** (no receipt in this repo).
- **Best receipt (this repo):** none. All **12** `GEMSDOE89` pairs (**24 `.tif`
  files**: 3 `SNAP` + 3 `SPACING` + 3 `RELIEF` + 3 `MASS`) are `BUILT (unscored)`.
- **TOP_PUBLIC:** `____` — **not supplied**; the human must fill it from the
  leaderboard with a date. It is the only valid target number.
- **Slots this week:** `__ / __` — **not supplied**; quota is 3 scored
  submissions per rolling week per entity, plus one final blind choice.
- **Axes built on this branch (one session each):** `RELIEF` (`r10`/`r15`/`r15s`),
  `MASS` (`m10uniq`/`m10rand`/`m20uniq`), `SPACING` (`alongstrike`/`poisson`/
  `lattice`), **`SNAP` gateless (`1p0px`/`1p4px`/`2p0px` at `g0p00`)** — the
  SNAP session's values are the only ones no prior session built (upstream has
  gated arms 1.42/.02, 2.0/.02, 2.0/.01 only), so receipts become a clean
  **gate ablation**.
- **Week:** 2026-10-23. Deadline **2026-12-03** (≈6 weeks, ~18 slots) —
  *UNVERIFIED*: automated competition-page access is barred by its terms, so the
  human must confirm the date.

## Next 3 slots (detail in `SLOT_PLAN.md`)

| # | file | predicted (MODEL) | what the result would change |
|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif` | +0.003 (−0.012…+0.018) | allocation fork: ≥ +0.010 → run r15; ±0.010 → close RELIEF *and* CONCENTRATION |
| 2 | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` | +0.028 (−0.028…+0.084) | placement fork, independent of slot 1: ≥ +0.010 → snap real, run 1p4px; ≤ −0.010 → retire SNAP |
| 3 | conditional: r15 if slot 1 ≥ 0.2878; else 1p4px-g0p00 if slot 2 ≥ 0.2878; else `spacing-alongstrike` (narrow band −0.003…+0.006) or **hold** | +0.004 / +0.028 / +0.002 | dose-response for whichever axis woke up; hold keeps a slot for late receipts |

Queue behind these (all gated, all in `releases/`): `MASS m10uniq` (+0.002),
`SPACING alongstrike` (+0.002), `RELIEF r15/r15s`, `MASS m20uniq` (+0.004),
`SPACING poisson/lattice` (negative MODEL — held per their cards), upstream
gated SNAP arms (GEMSDOE84 releases, not in this repo).

**What only the human can supply:** TOP_PUBLIC + date; slots used/available; a
receipt for each submitted file (`receipt_score`, `receipt_date` in the ledger);
confirmation of the 2026-12-03 deadline; the data-exposure decision
(`IRREGULARITIES.md` item 2); SGMC restore-from-USGS for report-only numbers
(item 8); and whether to queue upstream gated-`SNAP` files from GEMSDOE84.
