# CURRENT STATE

- **Parent (recipe-rebuilt, byte-verified):** `h33-h33-2-b2` — 37,654 unit dots.
  `tools/rebuild_r0.py` matches `c55bafc470054e82…` (zeros) and
  `baeae3219bba6a19…` (NaN); all 10 fetchable manifest pins pass. Live
  **0.2778 = CLAIM**; no receipt is stored here.
- **Best receipt:** none. All **21** `GEMSDOE89` pairs (**42 `.tif` files**) are
  `BUILT (unscored)` and pass every format + data gate: 3 each `SNAP` /
  `SPACING` / `RELIEF` / `MASS`, plus **9 `CONCENTRATION`** arms across three
  non-duplicate mechanisms (`12.8 km` interaction + GPS strain, `5 km` raw
  catalogue + Sobel `q`, and `2 km` H19 sequential marginals).
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

**Human must supply:** `TOP_PUBLIC` + date; slots used/available; every uploaded
file's `receipt_score` + `date`; deadline confirmation; public-mirror review
(`IRREGULARITIES.md` item 2); optional official-USGS SGMC restoration (item 8);
and all upload/final-file choices.
