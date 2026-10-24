# CURRENT STATE

# CURRENT STATE

- **Parent (recipe-rebuilt, byte-verified 2026-10-24):** `h33-h33-2-b2` — 37,654 unit dots;
  `tools/rebuild_r0.py` matches `c55bafc470054e82…` (zeros) and `baeae3219bba6a19…` (NaN).
  All 10 fetchable manifest pins pass; the SGMC control pin stays UNVERIFIED and report-only.
  Live **0.2778 = CLAIM**; **best receipt: none**.
- **Built, unscored:** **34 pairs / 68 GeoTIFFs + 4 GeoJSON dossiers**, all `BUILT` and format/data-gated
  (`SNAP` 9 here + 3 upstream, `CONCENTRATION` 9 across 3 families, `SPACING` 3, `RELIEF` 3, drop-`MASS` 3,
  `PRUNE` 3 collar-ablation arms, `TRACKB` 4 Phase-2 pairs). No `(parent, axis, value)` repeat anywhere in the ledger (149 rows total).
- **PRUNE collar ablation axis (`ledger/MECHANISM_CARDS.md` Part X, this session):**
  - **`c3p0` (`7b101829`):** 3.0 px collar (300 m full kernel clearance),
    `+0.003 MODEL` (band `−0.005…+0.012`), 2,171 dots relocated (5.77%),
    refilled on `h19_5` outside 300 m ($d_{cat} > 3.0$ px, separation $\ge 2.0$ px).
  - **`c1p0` (`85cf176a`):** 1.0 px collar (100 m proximal splay probe),
    `−0.004 MODEL` (band `−0.015…+0.008`), 2,545 dots swapped in from `d28`.
  - **`c4p0` (`d681292b`):** 4.0 px collar (400 m flight-line smear purge),
    `−0.001 MODEL` (band `−0.018…+0.015`), 3,825 dots relocated (10.16%).
- **Dual-Phase `TRACKB` 150-trace R0-consolidating arms**
  (`ledger/MECHANISM_CARDS.md` Part IX, `docs/TRACKB_EVIDENCE.md`; Phase 2 $250k — **not** weekly-slot candidates unless the human decides):
  - `TRACKBt150add` (`5a09404f`, `+1,415/-0` px = `3.76%`, `39,069` px, `150` unbroken `≥ 1.00 km` traces / `225.7 km` chord + RFC 7946 `.geojson`; `P1 +0.000` / `P2 +0.012 MODEL`),
  - `TRACKBt150swap` (`8cfcbe4c`, `+1,415/-1,415` px = `3.76%`, `37,654` px, 1-for-1 speckle-funded control; `P1 −0.002` / `P2 +0.011 MODEL`),
  - `TRACKBt150link` (`eded7713`, `+1,586/-1,586` px = `4.21%`, `37,654` px, `249.1 km` chord with `100` `≤ 620 m` wash/step-over gaps bridged; `P1 −0.003` / `P2 +0.009 MODEL`),
  plus earlier review-only `TRACKBtop12` (`fb156257`, `145` dots, `12` traces).
- **`SNAP` directional corner** (`ledger/MECHANISM_CARDS.md`
  Part VIII): `dirfw2p0` (`dc578b2f`, 20,853 dots moved footwall-only, mean 1.738 px),
  its exact mirror `dirhw2p0` (`5cccfc1d`, 21,399 moved hanging-wall-only, mean 1.737 px),
  and the dose `dirfw1p0` (`373c8fd6`, 16,632 moved, mean 1.000 px). Count fixed at 37,654,
  targets `d_cat ≥ 3 px`, zero catalogue mass, no RNG. Undirected crest arm `snap2p0px-g0p00`
  moves **15,585 dots up-slope and 15,670 down-slope** (direction-neutral).
- **`SNAP` state:** the 3-window × 3-gate factorial is **complete** (`1p0px-g0p00`
  `1add5aa6`, `1p0px-g0p01` `2916ec2d`, `1p0px-g0p02` `384435e6`, `1p4px-g0p00`
  `e1474851`, `1p4px-g0p01` `afc60a25`, plus upstream `1p4px-g0p02` `0b6a2ab2`,
  `2p0px-g0p00` `69db3aae`, `2p0px-g0p01` `7bdaa58b`, `2p0px-g0p02` `b2019f55`), and the
  three directional arms sit outside it.
- **Other axes, no receipts:** `CONCENTRATION` `12p8km-int10` (`bcade136`, +0.008,
  −0.006…+0.018), `CONC5kmcat10` (`2dc19377`, +0.009) and their away/dose arms;
  `RELIEF` `r10`/`r15`/`r15s`; `MASS` `m10uniq`/`m10rand`/`m20uniq`;
  `SPACING` `alongstrike`/`poisson`/`lattice`.
- **Report only, never gates:** catalogue hide-and-recover CIs overlap R0 for every arm;
  leakage canary `max AUC = 0.665 < 0.90`; SGMC skipped (UNVERIFIED pin).
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
| 3 | conditional: `dirfw1p0` (`373c8fd6`) if `fw − hw ≥ +0.010`; else `conc-12p8km-int10` (`bcade136`, +0.008) or `prune-c3p0` (`7b101829`, +0.003); else **hold** | +0.015 / +0.008 / +0.003 | dose vs direction; or independent block-prior test; or 300 m kernel clearance |

**Alternative week (equally cheap, same two slots):** the gate pair `1p4px-g0p01`
(`afc60a25`) against its matched gateless control `1p4px-g0p00` (`e1474851`) — reads
selectivity-vs-dose, not direction. Do **not** run both pairs in one week (4 files > quota).

**Human must supply:** `TOP_PUBLIC` + date; slots used/available; every uploaded file's
`receipt_score` + `date`; deadline confirmation; public-mirror review (`IRREGULARITIES.md`
item 2); optional official-USGS SGMC restoration (item 8); and all upload/final-file choices.

**Alternative week (equally cheap, same two slots):** the gate pair `1p4px-g0p01`
(`afc60a25`) against its matched gateless control `1p4px-g0p00` (`e1474851`) — reads
selectivity-vs-dose, not direction. Do **not** run both pairs in one week (4 files > quota).

**Human must supply:** `TOP_PUBLIC` + date; slots used/available; every uploaded file's
`receipt_score` + `date`; deadline confirmation; public-mirror review (`IRREGULARITIES.md`
item 2); optional official-USGS SGMC restoration (item 8); and all upload/final-file choices.
