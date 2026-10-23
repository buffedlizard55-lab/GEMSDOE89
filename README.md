# CURRENT STATE

- **Parent (recipe-rebuilt, byte-verified):** `h33-h33-2-b2` — 37,654 unit dots.
  `tools/rebuild_r0.py` rebuilds it from `scored_h19_5.tif` (`dot_thin(r=2.8)` +
  `d_cat > 2.0` flank prune) and matches **both** pins byte-for-byte:
  `sha256_zeros` `c55bafc470054e82…`, `sha256_nan` `baeae3219bba6a19…`. This
  session re-ran the start gate from a clean sandbox: 10/10 fetchable manifest
  pins hash-verified (`tools/fetch_pinned_data.py`, after fixing a duplicate-pin
  bug that produced two false FAILs, `IRREGULARITIES.md` item 11) and R0 rebuilt
  in 8.6 s. Live **0.2778 = CLAIM** (no receipt in this repo).
- **Best receipt (this repo):** none. All **15** `GEMSDOE89` pairs (**30 `.tif`
  files**: 3 `SNAP` + 3 `SPACING` + 3 `RELIEF` + 3 `MASS` + **3 `CONCENTRATION`**)
  are `BUILT (unscored)`.
- **TOP_PUBLIC:** `____` — **not supplied**; the human must fill it from the
  leaderboard with a date. It is the only valid target number.
- **Slots this week:** `__ / __` — **not supplied**; quota is 3 scored
  submissions per rolling week per entity, plus one final blind choice.
- **Axes built on this branch (one session each):** `RELIEF` (`r10`/`r15`/`r15s`),
  `MASS` (`m10uniq`/`m10rand`/`m20uniq`), `SPACING` (`alongstrike`/`poisson`/
  `lattice`), `SNAP` gateless (`1p0px`/`1p4px`/`2p0px` at `g0p00`), and now
  **`CONCENTRATION` 5 km with an independent prior** (`cat10`/`cat20`/`cat10away`).
  Upstream `GEMSDOE84` had already spent `5km-t25-move2400`, `5km-t50-move3765`
  and `spread5km-move2400` on this axis with the parent's *own* gain surface as
  the block prior; the three arms here use catalogued-fault density instead, so
  they are new `(parent, axis, value)` triples and a different question.
- **Why CONCENTRATION now:** measured on R0, 5 km block density is uncorrelated
  with catalogued-fault density (**r = 0.039**) and **37.9 %** of the dots sit in
  the 862 blocks with no catalogued fault at all. That is the largest documented
  free parameter in the fleet: the other four axes move dots *within* their own
  neighbourhood, this one moves 10-20 % of the mass *between* 5 km blocks.
- **Week:** 2026-10-23. Deadline **2026-12-03** (≈6 weeks, ~18 slots) —
  *UNVERIFIED*: the human must confirm it on the competition page.

## Next 3 slots (detail in `SLOT_PLAN.md`)

| # | file | predicted (MODEL) | what the result would change |
|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-CONC5kmcat10-20261023-2dc19377.tif` | +0.009 (−0.010…+0.038) | allocation fork: ≥ +0.010 → run `cat20`; ≤ −0.010 → prior inverted, run `cat10away`; inside ±0.010 → the block prior carries no signal at 5 km |
| 2 | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` | +0.028 (−0.028…+0.084) | placement fork, independent of slot 1: ≥ +0.010 → snap real, run `1p4px`; ≤ −0.010 → retire SNAP |
| 3 | conditional: `cat20` if slot 1 ≥ +0.010; `cat10away` if slot 1 ≤ −0.010; else `MASSm10uniq` (`beed130f`, +0.002, ceiling +0.0105) or **hold** | +0.019 / −0.009 / +0.002 | dose/sign confirmation of the only axis with block-scale headroom, or the cheapest positive-drift file in the repo |

Queue behind these (all gated, all in `releases/`): `RELIEF r10` (+0.003),
`SPACING alongstrike` (+0.002), `RELIEF r15/r15s`, `MASS m20uniq` (+0.004),
`SPACING poisson/lattice` (negative MODEL — held per their cards), upstream
gated `SNAP` arms (GEMSDOE84 releases, not in this repo).

**What only the human can supply:** TOP_PUBLIC + date; slots used/available; a
receipt for each submitted file (`receipt_score`, `receipt_date` in the ledger);
confirmation of the 2026-12-03 deadline; the data-exposure decision
(`IRREGULARITIES.md` item 2); SGMC restore-from-USGS for report-only numbers
(item 8); and whether to queue upstream gated-`SNAP` files from GEMSDOE84.
