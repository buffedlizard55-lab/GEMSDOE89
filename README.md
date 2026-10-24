# CURRENT STATE

- **Parent (recipe-rebuilt, byte-verified):** `h33-h33-2-b2` — 37,654 unit dots.
  `tools/rebuild_r0.py` matches `c55bafc470054e82…` (zeros) and
  `baeae3219bba6a19…` (NaN) again this session, after all 10 fetchable manifest
  pins passed; the `parent_r0_nan` twin re-verified as well. Live **0.2778 =
  CLAIM**; no receipt is stored here.
- **Best receipt:** none. All **24** `GEMSDOE89` pairs (**48 `.tif` files**) are
  `BUILT (unscored)` and pass every format + data gate: 6 `SNAP` (3 gateless
  window cells + **3 directional** this session), 3 `SPACING`, 3 `RELIEF`,
  3 drop-only `MASS`, 9 `CONCENTRATION` across three mechanisms, 3 `PRUNE`-family
  refills.
- **This session (2026-10-24) — `SNAP` directional corner:** `dirfw2p0`
  (`dc578b2f`, 20,853 dots moved footwall-only, mean 1.738 px), its exact mirror
  `dirhw2p0` (`5cccfc1d`, 21,399 moved hanging-wall-only, mean 1.737 px), and the
  dose `dirfw1p0` (`373c8fd6`, 16,632 moved, mean 1.000 px). Count fixed at
  37,654, targets `d_cat ≥ 3 px`, zero catalogue mass, no RNG, parity with
  `snap.snap_dots` proven by test. **The finding that re-ordered the queue:** the
  undirected crest arm `snap2p0px-g0p00` moves **15,585 dots up-slope and 15,670
  down-slope** — R0 is direction-neutral w.r.t. the HG maximum, so the crest-side
  question was never tested. Bands `−0.019…+0.057` (`MODEL`, sign prior weak by
  design): the pair is read as `fw − hw`, never alone.
- **TOP_PUBLIC:** `____` — human must supply from the leaderboard with a date;
  no other target number is valid. **Slots this week:** `__ / 3` — human supplies
  used/available (3 per rolling week per entity + 1 blind final).
- **Other axes already built (no receipts):** `CONCENTRATION` `12p8km-int10`
  (`bcade136`, +0.008, −0.006…+0.018), `CONC5kmcat10` (`2dc19377`, +0.009) and
  their away/dose arms; `RELIEF` `r10`/`r15`/`r15s`; `MASS` `m10uniq`/`m10rand`/
  `m20uniq`; `SPACING` `alongstrike`/`poisson`/`lattice`; `PRUNE` refills at
  1.5/2.5/3/4 px.
- **Deadline:** 2026-12-03 (≈6 weeks, ~17 rolling slots) is **UNVERIFIED**;
  automated competition-page access is barred, so the human confirms it.

## Next 3 slots (details in `SLOT_PLAN.md` and `docs/SUBMIT.md`)

| # | file | predicted (`MODEL`) | decision triggered by a receipt |
|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-snapdirfw2p0-20261024-dc578b2f.tif` | −0.019…+0.057 (sign prior weak by design) | half of a matched pair — unreadable alone |
| 2 | `releases/h33-h33-2-b2-snapdirhw2p0-20261024-5cccfc1d.tif` | −0.019…+0.057 | mirror: `fw − hw ≥ +0.010` ⇒ truth is footwall-side of the crest; reverse ⇒ hanging-wall side; both ≤ R0−0.010 ⇒ the crest is right and SNAP position work stops |
| 3 | conditional: `dirfw1p0` (`373c8fd6`) if `fw − hw ≥ +0.010`; else `conc-12p8km-int10` (`bcade136`) or `CONC5kmcat10` (`2dc19377`); else **hold** | +0.015 / +0.008 / +0.009 | dose vs direction, or the first independent block-prior test |

**Human must supply:** `TOP_PUBLIC` + date; slots used/available; every uploaded
file's `receipt_score` + `date`; deadline confirmation; public-mirror review
(`IRREGULARITIES.md` item 2); optional official-USGS SGMC restoration (item 8);
and all upload/final-file choices.
