# CURRENT STATE

- **Parent (recipe-rebuilt, byte-verified):** `h33-h33-2-b2` — 37,654 unit dots.
  `tools/rebuild_r0.py` rebuilds it from `scored_h19_5.tif` (`dot_thin(r=2.8)` +
  `d_cat > 2.0` flank prune) and matches **both** pins byte-for-byte:
  `sha256_zeros` `c55bafc470054e82…`, `sha256_nan` `baeae3219bba6a19…`. Live
  **0.2778 = CLAIM** (no receipt in this repo).
- **Best receipt (this repo):** none. All **15** `GEMSDOE89` pairs (**30 `.tif`
  files**: 3 `CONCENTRATION` + 3 `SNAP` + 3 `SPACING` + 3 `RELIEF` + 3 `MASS`)
  are `BUILT (unscored)` and pass every format + data gate.
- **TOP_PUBLIC:** `____` — **not supplied**; the human must fill it from the
  leaderboard with a date. It is the only valid target number.
- **Slots this week:** `__ / 3` — **not supplied**; quota is 3 scored
  submissions per rolling week per entity, plus one final blind choice.
- **Axes built on this branch (one session each):** `RELIEF` (`r10`/`r15`/`r15s`),
  `MASS` (`m10uniq`/`m10rand`/`m20uniq`), `SPACING` (`alongstrike`/`poisson`/
  `lattice`), `SNAP` gateless (`1p0px`/`1p4px`/`2p0px` at `g0p00`), and
  **`CONCENTRATION` (`12p8km-int10` / `12p8km-int20` / `12p8km-geod15`)** —
  12.8 km (`128 px`) structural-domain reallocation testing Faulds fault-interaction
  vs catalogue-free GPS strain/seismicity priors (upstream `GEMSDOE84` built 5 km
  blocks only).
- **Week:** 2026-10-23. Deadline **2026-12-03** (≈6 weeks, ~18 slots) —
  *UNVERIFIED*: automated competition-page access is barred by its terms, so the
  human must confirm the date.

## Next 3 slots (detail in `SLOT_PLAN.md`)

| # | file | predicted (`MODEL`) | what the result would change |
|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136.tif` | +0.008 (−0.006…+0.018) | 12.8 km concentration fork (`CV_12.8km` held at `0.5533` inside `0.51–0.59`): `≥ +0.010` → run `12p8km-int20`; `≤ −0.010` → run catalogue-free `12p8km-geod15`; `±0.010` → hold `int20` |
| 2 | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` | +0.028 (−0.028…+0.084) | orthogonal local-placement fork (`1.86 px` EM-crest snap): `≥ +0.010` → run `1p4px-g0p00`; `≤ −0.010` → retire SNAP (low-variance alt: `relief-r10`, `+0.003`) |
| 3 | conditional: `conc-12p8km-int20` (`357b4ac4`) if Slot 1 `≥ 0.2878`; else `conc-12p8km-geod15` (`259ea040`) if Slot 1 `≤ 0.2678`; else `snap1p4px-g0p00` (`e1474851`) if Slot 2 `≥ 0.2878`; else `relief-r10` (`366c87ca`) / `MASSm10uniq` (`beed130f`) or **hold** | +0.009 / +0.003 / +0.028 / +0.003 / +0.002 | tests `CV_12.8km > 0.59` saturation (`int20`), active-strain discriminator (`geod15`), or SNAP window dose (`1p4px`); hold keeps quota for late receipts |

Queue behind these (all gated, all in `releases/`): `RELIEF r10/r15/r15s`,
`MASS m10uniq/m20uniq/m10rand`, `SPACING alongstrike`, `SNAP 1p0px-g0p00`, and
held negative-`MODEL` arms `SPACING poisson/lattice`.

**What only the human can supply:** `TOP_PUBLIC` + date; slots used/available; a
receipt for each submitted file (`receipt_score`, `date` in `ledger/submissions.csv`);
confirmation of the 2026-12-03 deadline; the public-mirror governance review
(`IRREGULARITIES.md` item 2); and an official USGS DS-1052 raster if SGMC
report-only numbers are desired (item 8).
