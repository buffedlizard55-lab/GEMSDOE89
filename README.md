# CURRENT STATE

- **Parent (recipe-rebuilt, byte-verified 2026-10-24):** `h33-h33-2-b2` — 37,654 unit dots;
  `tools/rebuild_r0.py` matches `c55bafc470054e82…` (zeros) and `baeae3219bba6a19…` (NaN).
  All 10 fetchable manifest pins pass; the SGMC control pin stays UNVERIFIED and report-only.
  Live **0.2778 = CLAIM**; **best receipt: none**.
- **Built, unscored:** **31 pairs / 62 GeoTIFFs**, all `BUILT` and format/data-gated
  (`SNAP` 9 factorial + 3 directional, `CONCENTRATION` 9, `SPACING` 3, `RELIEF` 3,
  drop-`MASS` 3, `TRACKB` 1 top12 Phase-2 pair + 3 concentration pairs). No
  `(parent, axis, value)` repeat anywhere in the ledger.
- **This session (2026-10-24) — `TRACKB` structural concentration** (`branch
  arena/7fd24ce1-gemsdoe89`; `ledger/MECHANISM_CARDS_TRACKB_CONC.md`): a Phase-2 trace
  inventory `releases/h33-h33-2-b2-TRACKB-traces-20261024.geojson` (**1,520** strike-consistent
  ≥1 km chains, one evidence paragraph each; atlas `evidence/TRACKB_trace_atlas_20261024.md`),
  plus 3 nested, count-preserving rasters `TR10`/`TR20`/`TR30` (`32211f1f` / `5da46626` /
  `c8a264b5`) moving 10/20/30 % of off-trace dots into the ±300 m trace corridor at
  `d_cat ≥ 3 px`, `r_sep ≥ 2.8 px`, collar frozen. Phase-1 jitter MODEL is a coverage-cost
  **floor** (central −0.002 / −0.012 / −0.021); **not a weekly-slot candidate unless the human
  decides**. Distinct from the merged `top12` 145-dot trace overlay (PR #15).
- **`SNAP` directional corner (merged 2026-10-24, `ledger/MECHANISM_CARDS.md` Part VIII):**
  `dirfw2p0` (`dc578b2f`) / mirror `dirhw2p0` (`5cccfc1d`) / dose `dirfw1p0` (`373c8fd6`);
  count fixed 37,654, `d_cat ≥ 3 px`, read as `fw − hw`, never alone. The undirected crest arm
  moves ~15.6k dots each up- and down-slope, so R0 is crest-direction-neutral.
- **`SNAP` factorial complete:** 3 windows × 3 gates (`1p0px`/`1p4px`/`2p0px` ×
  `g0p00`/`g0p01`/`g0p02`); the three directional arms sit outside it.
- **Other axes, no receipts:** `CONCENTRATION` `12p8km-int10` (`bcade136`, +0.008),
  `CONC5kmcat10` (`2dc19377`, +0.009) + away/dose arms, `2 km` H19 family; `RELIEF`
  `r10`/`r15`/`r15s`; `MASS` `m10uniq`/`m10rand`/`m20uniq`; `SPACING`
  `alongstrike`/`poisson`/`lattice`; upstream `PRUNE` refills at 1–4 px.
- **Phase-2 `TRACKB` top12 (merged PR #15, not a weekly-slot candidate):** `fb156257`
  GeoJSON + 145-dot raster, 12 strike-consistent traces ≥1 km (41.3 km total), per-trace
  evidence in `ledger/TRACKB_TRACES.md`.
- **Report only, never gates:** catalogue hide-and-recover CIs overlap R0 for every arm;
  leakage canaries all `< 0.90` (19-band + TRACKB composite footprint-masked max `0.569`,
  composite `0.543`; SNAP-response canary `0.665`); SGMC skipped (UNVERIFIED pin).
- **TOP_PUBLIC:** `____` — human must supply from the leaderboard with a date; no other
  target number is valid. **Slots this week:** `__ / 3` — human supplies used/available
  (3 per rolling week per entity + 1 blind final).
- **Deadline:** `2026-12-03` (≈6 weeks, ~17 rolling slots) is **UNVERIFIED**; automated
  competition-page access is barred, so the human confirms it.

## Next 3 slots (details in `SLOT_PLAN.md` and `docs/SUBMIT.md`)

| # | file | predicted (`MODEL`) | decision triggered by a receipt |
|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-snapdirfw2p0-20261024-dc578b2f.tif` | −0.019…+0.056 (sign prior weak by design) | half of a matched pair — unreadable alone |
| 2 | `releases/h33-h33-2-b2-snapdirhw2p0-20261024-5cccfc1d.tif` | −0.019…+0.057 | mirror: `fw − hw ≥ +0.010` ⇒ truth is footwall-side of the crest; reverse ⇒ hanging-wall side; both ≤ R0−0.010 ⇒ the crest is right and SNAP position work stops |
| 3 | conditional: `dirfw1p0` (`373c8fd6`) if `fw − hw ≥ +0.010`; else the gate pair head `1p4px-g0p01` (`afc60a25`, +0.0120) or the block fork `conc-12p8km-int10` (`bcade136`, +0.008); else **hold** | +0.015 / +0.012 / +0.008 | dose vs direction; or selectivity; or the first independent block-prior test |

**Alternative week (equally cheap, same two slots):** the gate pair `1p4px-g0p01`
(`afc60a25`) against its matched gateless control `1p4px-g0p00` (`e1474851`) — reads
selectivity-vs-dose, not direction. Do **not** run both pairs in one week (4 files > quota).

**Human must supply:** `TOP_PUBLIC` + date; slots used/available; every uploaded file's
`receipt_score` + `date`; deadline confirmation; public-mirror review (`IRREGULARITIES.md`
item 2); optional official-USGS SGMC restoration (item 8); and all upload/final-file choices.

`TRACKB` rasters (top12 and TR10/TR20/TR30) are **held out** of this weekly queue (Phase-2 evidence play; see `SLOT_PLAN.md`). A strong alternative for any Slot 1 is a **REPEAT-CALIBRATION** upload of byte-exact R0 to convert `0.2778` from `CLAIM` → `RECEIPT` before trusting any MODEL delta.
