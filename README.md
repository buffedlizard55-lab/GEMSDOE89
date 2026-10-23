# CURRENT STATE

- **Parent (recipe-rebuilt, byte-verified):** `h33-h33-2-b2` — 37,654 unit dots.
  `tools/rebuild_r0.py` matches both pins: `c55bafc470054e82…` (zeros) and
  `baeae3219bba6a19…` (NaN). Live **0.2778 = CLAIM**; no receipt is stored here.
- **Best receipt (this repo):** none. All **15** `GEMSDOE89` pairs (**30 `.tif`
  files**: 3 each `SNAP`, `SPACING`, `RELIEF`, `MASS`, `CONCENTRATION`) are
  `BUILT (unscored)`.
- **TOP_PUBLIC:** `____` — **not supplied**; the human must fill it from the
  leaderboard with a date. It is the only valid target number.
- **Slots this week:** `__ / __` — **not supplied**; quota is 3 scored
  submissions per rolling week per entity, plus one final blind choice.
- **New axis:** `CONCENTRATION` at 2 km, bottom-half → top-third catalogue
  prior, nested 10% / 15% / 20% transfers (`m3765` / `m5648` / `m7531`).
  Additions stay on H19-5 and use exact sequential DTI marginals. Only m3765
  has a positive central MODEL; m5648/m7531 are held because H19 coverage and
  crowding worsen. Cards: `ledger/MECHANISM_CARDS_CONCENTRATION.md`.
- **Other axes built:** `RELIEF` (`r10`/`r15`/`r15s`), `MASS`
  (`m10uniq`/`m10rand`/`m20uniq`), `SPACING` (`alongstrike`/`poisson`/`lattice`),
  and gateless `SNAP` (`1p0px`/`1p4px`/`2p0px` at `g0p00`).
- **Week:** 2026-10-23. Deadline **2026-12-03** (≈6 weeks, ~18 slots) —
  *UNVERIFIED*: automated competition-page access is barred; human confirms.

## Next 3 slots (detail in `SLOT_PLAN.md`)

| # | file | predicted (MODEL) | what the result would change |
|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-conc2km-b50-t33-m3765-20261023-da3a4886.tif` | +0.0024 (−0.0127…+0.0174) | ≥ +0.010 → test m5648; ±0.010 → no evidence/hold doses; ≤ −0.010 → close this recipe |
| 2 | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` | +0.028 (−0.028…+0.084) | ≥ +0.010 → snap mechanism is live, test 1p4px; ≤ −0.010 → retire SNAP |
| 3 | conditional: m5648 if slot 1 ≥ 0.2878; else 1p4px-g0p00 if slot 2 ≥ 0.2878; else `relief-r10` or **hold** | −0.0028 / +0.028 / +0.003 | dose only after a live ≥ +0.010 result; otherwise independent RELIEF probe or spare slot |

Queue behind these: `RELIEF r15/r15s`, `MASS m10uniq` (+0.002),
`SPACING alongstrike` (+0.002), then dose arms only on their triggers.
`CONCENTRATION m7531` (−0.0126 central) and negative-Model SPACING
`poisson/lattice` remain held. Full gated queue: `docs/SUBMIT.md`.

**What only the human can supply:** TOP_PUBLIC + date; slots used/available; a
receipt for each submitted file (`receipt_score`, `date` in the ledger);
confirmation of the 2026-12-03 deadline; the data-exposure decision
(`IRREGULARITIES.md` item 2); SGMC restoration from official USGS for optional
report-only numbers (item 8); and all upload/final-file decisions.
