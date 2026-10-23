# CURRENT STATE

- **Parent (recipe-rebuilt, byte-verified):** `h33-h33-2-b2` — 37,654 unit dots.
  `tools/rebuild_r0.py` matches `c55bafc470054e82…` (zeros) and
  `baeae3219bba6a19…` (NaN); all 10 fetchable manifest pins pass. Live
  **0.2778 = CLAIM**; no receipt is stored here.
- **Best receipt:** none. All **18** `GEMSDOE89` pairs (**36 `.tif` files**) are
  `BUILT (unscored)`: 3 each SNAP / SPACING / RELIEF / MASS, plus **6
  CONCENTRATION** arms from two non-duplicate sessions.
- **TOP_PUBLIC:** `____` — human must supply it from the leaderboard with a
  date; no other target number is valid. **Slots this week:** `__ / __` —
  human supplies used/available (3 per rolling week per entity + one final).
- **CONCENTRATION families:** 5 km `cat10` / `cat20` / `cat10away` uses an
  independent catalogue prior and shared potential-field placement; 2 km
  `2km-b50-t33-m3765` / `m5648` / `m7531` keeps additions on H19-5 and uses
  exact sequential DTI marginals. They are different mechanisms, **not**
  scale-only ablations. Cards: `ledger/MECHANISM_CARDS.md` Parts IV–V and
  `ledger/MECHANISM_CARDS_CONCENTRATION.md`.
- **Other axes:** `RELIEF` (`r10`/`r15`/`r15s`), `MASS`
  (`m10uniq`/`m10rand`/`m20uniq`), `SPACING` (`alongstrike`/`poisson`/`lattice`),
  and gateless `SNAP` (`1p0px`/`1p4px`/`2p0px`).
- **Deadline:** 2026-12-03 (≈6 weeks, ~18 rolling slots) is **UNVERIFIED**;
  automated competition-page access is barred, so the human confirms it.

## Next 3 slots (details in `SLOT_PLAN.md` and `docs/SUBMIT.md`)

| # | file | predicted (MODEL) | decision triggered by a receipt |
|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-CONC5kmcat10-20261023-2dc19377.tif` | +0.009 (−0.010…+0.038) | ≥ 0.2878 → `cat20`; ≤ 0.2678 → `cat10away`; otherwise no 5 km evidence |
| 2 | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` | +0.028 (−0.028…+0.084) | ≥ 0.2878 → snap mechanism is live; ≤ 0.2678 → retire SNAP |
| 3 | priority: `cat20` if slot 1 ≥ 0.2878; `cat10away` if ≤ 0.2678; else `snap1p4px` if slot 2 ≥ 0.2878; else `MASSm10uniq` or **hold** | +0.019 / −0.009 / +0.028 / +0.002 | dose/sign confirmation first, then SNAP dose, then an orthogonal MASS probe |

The 2 km CONCENTRATION family remains **held** behind these: its 10% central
MODEL is +0.0024, but the 15%/20% central values are negative and its placement
rule differs from the 5 km family. `SPACING poisson/lattice` also remain held.

**Human must supply:** TOP_PUBLIC + date; slots used/available; every uploaded
file's `receipt_score` + `date`; deadline confirmation; the data-exposure
decision (`IRREGULARITIES.md` item 2); optional official-USGS SGMC restoration
(item 8); and all upload/final-file decisions.
