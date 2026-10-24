# CURRENT STATE

- **Parent (recipe-rebuilt, byte-verified):** `h33-h33-2-b2` — 37,654 unit dots.
  `tools/rebuild_r0.py` matches `c55bafc470054e82…` (zeros) and
  `baeae3219bba6a19…` (NaN); all 10 fetchable manifest pins pass. Live
  **0.2778 = CLAIM**; no receipt is stored here.
- **Best receipt:** none. All **24** `GEMSDOE89` pairs (**48 `.tif` files**) are
  `BUILT (unscored)` and pass every format + data gate: 3 each `SNAP` /
  `SPACING` / `RELIEF` / `MASS`, **9 `CONCENTRATION`** arms across three
  non-duplicate mechanisms, plus **3 `TRACKB`** rasters (Phase 2, held out of
  the weekly slot queue).
- **TRACKB session (2026-10-24, this branch):** built a Phase-2 trace inventory —
  `releases/h33-h33-2-b2-TRACKB-traces-20261024.geojson` (**1,520** strike-consistent
  ≥1 km chains, one evidence paragraph each; atlas `evidence/TRACKB_trace_atlas_20261024.md`)
  — and 3 nested, count-preserving structural-concentration rasters `TR10`/`TR20`/`TR30`
  (`32211f1f` / `5da46626` / `c8a264b5`), moving 10/20/30 % of off-trace dots into the
  ±300 m trace corridor at `d_cat ≥ 3 px`, `r_sep ≥ 2.8 px`, collar frozen. Phase-1 jitter
  MODEL is a coverage-cost **floor** (central −0.002 / −0.012 / −0.021); **not a weekly-slot
  candidate unless the human decides** (`ledger/MECHANISM_CARDS_TRACKB.md`).
- **TOP_PUBLIC:** `____` — human must supply from the leaderboard with a date;
  no other target number is valid. **Slots this week:** `__ / 3` — human
  supplies used/available (3 per rolling week per entity + 1 blind final).
- **`CONCENTRATION` families (`ledger/MECHANISM_CARDS.md` Parts IV–VI):**
  - **12.8 km (`128 px`, this session):** `12p8km-int10` (`bcade136`, `+0.008 MODEL`,
    band `−0.006…+0.018`, `CV_12.8km = 0.5533` inside `0.51–0.59`, 3-seed
    strand-holdout `+0.0040`), `12p8km-int20` (`357b4ac4`, `+0.009`), and
    **catalogue-free GPS strain/seismicity** `12p8km-geod15` (`259ea040`, `+0.003`).
  - **5 km (`50 px`):** `cat10` (`2dc19377`, `+0.009`), `cat20` (`4d229938`,
    `+0.019`), `cat10away` (`f7b8aa28`, `−0.009` sign control).
  - **2 km (`20 px`):** `m3765` / `m5648` / `m7531` (held separate H19 mechanism).
- **Other axes:** `RELIEF` (`r10`/`r15`/`r15s`), `MASS`
  (`m10uniq`/`m10rand`/`m20uniq`), `SPACING` (`alongstrike`/`poisson`/`lattice`),
  and gateless `SNAP` (`1p0px`/`1p4px`/`2p0px`).
- **Deadline:** 2026-12-03 (≈6 weeks, ~18 rolling slots) is **UNVERIFIED**;
  automated competition-page access is barred, so the human confirms it.

## Next 3 slots (details in `SLOT_PLAN.md` and `docs/SUBMIT.md`)

| # | file | predicted (`MODEL`) | decision triggered by a receipt |
|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-conc-12p8km-int10-20261023-bcade136.tif` *(or 5 km `…-CONC5kmcat10-…-2dc19377.tif`)* | +0.008 (−0.006…+0.018) *(alt +0.009, −0.010…+0.038)* | ≥ 0.2878 → matched 20% dose (`12p8km-int20` or `cat20`); ≤ 0.2678 → catalogue-free `12p8km-geod15` or `cat10away` |
| 2 | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` | +0.028 (−0.028…+0.084) | ≥ 0.2878 → snap live (`snap1p4px` dose); ≤ 0.2678 → retire SNAP |
| 3 | conditional: `12p8km-int20` (`357b4ac4`) / `cat20` if Slot 1 ≥ 0.2878; `12p8km-geod15` (`259ea040`) / `cat10away` if Slot 1 ≤ 0.2678; else `snap1p4px` if Slot 2 ≥ 0.2878; else `MASSm10uniq` / `relief-r10` or **hold** | +0.009 (+0.019) / +0.003 (−0.009) / +0.028 / +0.002 | confirms concentration dose or active-strain vs map bias first, then SNAP dose, else orthogonal `MASS`/`RELIEF` |

`TRACKB` rasters are **held out** of this weekly queue (Phase-2 evidence play; see
`SLOT_PLAN.md`). A strong alternative for Slot 1 is a **REPEAT-CALIBRATION** upload of
byte-exact R0 to convert `0.2778` from `CLAIM` → `RECEIPT` before trusting any MODEL delta.

**Human must supply:** `TOP_PUBLIC` + date; slots used/available; every uploaded
file's `receipt_score` + `date`; deadline confirmation; public-mirror review
(`IRREGULARITIES.md` item 2); optional official-USGS SGMC restoration (item 8);
and all upload/final-file choices.
