# GEMSDOE89 — executive summary and submission status

> **DOWNLOAD STATUS: ALL SESSION CANDIDATES DO NOT SUBMIT.** This session ran three holdout experiments
> (ANNULUS, PF-PEAKS, TC-UNION) against the spatially blocked segment holdout. Every candidate scored far
> below the visible-only R0 baseline (HOLDOUT-DTI 0.161230 [0.142648, 0.180061]); none is cleared for a
> competition slot. All GeoTIFFs below are format-validated research artifacts with verdict `negative` —
> **do not upload them to DrivenData**. No organizer submission receipt exists for any file in this repo,
> and no live score (including the fleet's 0.2778) is organizer-confirmed here.
>
> | candidate (stem) | sha256 (first 16) | holdout DTI (95% CI) vs R0 baseline 0.161230 [0.142648, 0.180061] | verdict | download |
> |---|---|---|---|---|
> | `h89-annulus-splay-20261024-e9b2bec1-candidate` | `e9b2bec11c2c60cd` | 0.001202 [0.000455, 0.002061]; delta −0.160028 [−0.180591, −0.139843] | **negative — DO NOT SUBMIT** | [releases/h89-annulus-splay-20261024-e9b2bec1-candidate.tif](releases/h89-annulus-splay-20261024-e9b2bec1-candidate.tif) |
> | `h89-pfpeaks-20261024-18f0316a-candidate` | `18f0316a457fb3af` | 0.068825 [0.042551, 0.095776]; delta −0.092405 [−0.136201, −0.049139] | **negative — DO NOT SUBMIT** | [releases/h89-pfpeaks-20261024-18f0316a-candidate.tif](releases/h89-pfpeaks-20261024-18f0316a-candidate.tif) |
> | `h89-tcunion-20261024-…` | — | 0.070181 [0.043417, 0.097668]; delta −0.091049 [−0.135214, −0.047593] | **negative — blocked as duplicate** (100% of dots within 3 px of the PF-PEAKS raster; no TIF emitted) | none |
> | `h89-condedge-s2-4-20261024-829cc418-candidate` | `829cc41856540a93` | 0.049875 [0.036830, 0.061751]; delta −0.111355 [−0.133218, −0.087864] | **negative — DO NOT SUBMIT** (prior session, same holdout) | [releases/h89-condedge-s2-4-20261024-829cc418-candidate.tif](releases/h89-condedge-s2-4-20261024-829cc418-candidate.tif) |
>
> Run cards: `registry/run_card_annulus_20261024.json`, `registry/run_card_pfpeaks_20261024.json`,
> `registry/run_card_tcunion_20261024.json`, `registry/run_card_condedge_20261024.json`.
> Format gates: PASS for all emitted TIFs (one float32 band, EPSG:32611, 3730×3292, template transform,
> finite values in [0,1], NaN only outside the footprint, exact known-fault mask, unique SHA-256 vs ledger,
> rank correlation < 0.90 and < 70% of dots within 3 px of every local registry raster).
> [Holdout and uniqueness gates](docs/HYPOTHESIS_REGISTER.md) · [How contest submissions work](docs/SUBMIT.md)

- **Incumbent (parent R0, recipe byte-verified):** `h33-h33-2-b2` — 37,654 unit-mass dots; live **0.2778 = CLAIM** (no organizer receipt in this repo). Its spatial holdout on this data is 0.161230 [0.142648, 0.180061], the best local comparator this session could beat — no candidate did.

## Read first on every session

The static site is [`index.html`](index.html) with the dedicated [`submit.html`](submit.html) submission guide. `docs/index.html` and `docs/submit.html` are generated publishing mirrors (run `python tools/build_pages_site.py`) for GitHub Pages configured to publish the `docs/` folder. Read [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md) and the upstream [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md) / [`PROMPT.md`](PROMPT.md) before research or coding, then inspect `README.md`, `IRREGULARITIES.md`, `SLOT_PLAN.md`, `docs/SUBMIT.md`, and the full local ledger. The brief carries the original mission, Arena values (**Maximize P(Win)** and **Own the Outcome**), experiment budget, holdout rules, evidence labels, uniqueness thresholds, submission gates, and trusted source links.

## Why the `0.2778` result is not yet an established target

The local evidence verifies R0's geometry and file identity, not the cause of its live result. R0 is reproduced as a 2.8-pixel-thinned `h19_5` ridge set pruned using the known-fault catalogue, yielding 37,654 unit-mass dots; its reported **0.2778 is CLAIM, not ORGANIZER-CONFIRMED** because no submission-page receipt is stored in this repository. Plausible contributors include multi-layer geophysical ridge continuity, sparse placement, and the recorded catalogue prune, but a single result cannot establish which mechanism caused the score. The request also gives `0.3195` and `0.4413` as different leaderboard snapshots without dates or receipts; neither is independently confirmed here. See the hash-verified recipe in [`gemsdoe/parent.py`](gemsdoe/parent.py), [`registry/parent_verification.json`](registry/parent_verification.json), and official metric rules in the [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).

## This session — three experiments, all negative (budget: 3 experiments / 2 hours)

Lanes tested, in order, each reusing the shared stacked holdout (`gemsdoe/holdout.py`) and writer
(`tools/submission_writer.py`) on the pinned, SHA-256-verified inputs:

1. **COND-EDGE** (prior session, on this checkout): band-17 `cond_surf` multi-scale conductivity edges.
   Holdout **0.049875 [0.036830, 0.061751]** vs R0 **0.161230 [0.142648, 0.180061]** — negative.
2. **ANNULUS** (this session): potential-field ridge peaks (bands 3 `tmi_hg` + 18 `iso_grav_anom_hg`,
   max multi-scale Gaussian gradient, sigma 2/4 px) restricted to the 200–800 m annulus around visible
   faults — splay/stepover targeting. Holdout **0.001202 [0.000455, 0.002061]** — negative. Diagnostics
   showed held-out truth sits 8–12 km from visible faults, so local annulus gating placed dots too far
   from held-out segments.
3. **PF-PEAKS** (this session): same ridge surface, fixed-mass spaced peaks across the whole visible-eligible
   image with R0's > 2 px visible-fault prune — strength-weighted ridge targeting. Holdout
   **0.068825 [0.042551, 0.095776]** — negative. All single-feature leakage canaries ≤ 0.5365 (< 0.90).
4. **TC-UNION** (this session): max gradient over bands 3 `tmi_hg`, 6 `tc` (tilt/total curvature) and
   18 `iso_grav_anom_hg`, same placement constraints. Holdout **0.070181 [0.043417, 0.097668]** —
   negative; additionally blocked by the registry duplicate guard (100% of dots within 3 px of the
   PF-PEAKS raster) so no TIF was emitted.

**Answer to the opening question:** the fleet's `h33-h33-2-b2-zeros` result of **0.2778 is CLAIM, not
ORGANIZER-CONFIRMED** — no submission-page receipt is stored in this repository, and the public snapshots
0.4413 / 0.3195 are conflicting, undated, and unverified. Plausible contributors to R0's result are its
potential-field ridge skeleton (TMI + gravity horizontal gradient), sparse fixed-mass placement
(37,654 dots), and the catalogue prune (dots > 2 px from known faults); no single result can establish
the causal mechanism. **We cannot generate a verified submission that beats 0.2778 in this session:** all
three holdout lanes lost to R0 decisively (paired-delta CIs exclude 0), and the parallel-run protocol
forbids spending a weekly slot on anything that has not beaten the incumbent on holdout. Negative
results are the deliverable: no file below is cleared to submit, and no slot was used.

Reproduce (after dependencies and pinned data are available):

```bash
python tools/fetch_pinned_data.py
python tools/rebuild_r0.py
python tools/evaluate_holdout.py        # COND-EDGE lane
python tools/evaluate_annulus.py        # ANNULUS lane
python tools/evaluate_pfpeaks.py        # PF-PEAKS lane
python tools/evaluate_tcunion.py        # TC-UNION lane
```

Each evaluator rechecks input hashes, tests each feature alone on spatially held-out fault segments
(leakage canary), audits the pre-placement surface and final raster against locally available registry
rasters (duplicate guard: |Spearman| > 0.90 or > 70% of dots within 3 px), and calls the shared
[`tools/submission_writer.py`](tools/submission_writer.py). None accesses DrivenData or uploads a file.
A valid GeoTIFF is **not** automatically a good submission.

## Existing validated fleet at the previous merge

- **Parent (recipe-rebuilt, byte-verified 2026-10-24):** `h33-h33-2-b2` — 37,654 unit dots;
  `tools/rebuild_r0.py` matches `c55bafc470054e82…` (zeros) and `baeae3219bba6a19…` (NaN).
  All 10 fetchable manifest pins pass; the SGMC control pin stays UNVERIFIED and report-only.
  Live **0.2778 = CLAIM**; **best receipt: none**.
- **Built, unscored:** **28 pairs / 56 GeoTIFFs**, all `BUILT` and format/data-gated
  (`SNAP` 9 here + 3 upstream, `CONCENTRATION` 9, `SPACING` 3, `RELIEF` 3, drop-`MASS` 3,
  `TRACKB` 1 Phase-2 pair). No `(parent, axis, value)` repeat anywhere in the ledger.
- **This session (2026-10-24) — `SNAP` directional corner** (`ledger/MECHANISM_CARDS.md`
  Part VIII): `dirfw2p0` (`dc578b2f`, 20,853 dots moved footwall-only, mean 1.738 px),
  its exact mirror `dirhw2p0` (`5cccfc1d`, 21,399 moved hanging-wall-only, mean 1.737 px),
  and the dose `dirfw1p0` (`373c8fd6`, 16,632 moved, mean 1.000 px). Count fixed at 37,654,
  targets `d_cat ≥ 3 px`, zero catalogue mass, no RNG, and a test proving the rule reduces
  to `snap.snap_dots` when the direction filter is off. **The measurement that re-ordered
  the queue:** the undirected crest arm `snap2p0px-g0p00` moves **15,585 dots up-slope and
  15,670 down-slope** — R0 is direction-neutral w.r.t. the HG maximum, so the crest-side
  question had never been tested. Bands `−0.019…+0.057` (`MODEL`, sign prior weak by
  design): the pair is read as `fw − hw`, never alone.
- **`SNAP` state:** the 3-window × 3-gate factorial is **complete** (`1p0px-g0p00`
  `1add5aa6`, `1p0px-g0p01` `2916ec2d`, `1p0px-g0p02` `384435e6`, `1p4px-g0p00`
  `e1474851`, `1p4px-g0p01` `afc60a25`, plus upstream `1p4px-g0p02` `0b6a2ab2`,
  `2p0px-g0p00` `69db3aae`, `2p0px-g0p01` `7bdaa58b`, `2p0px-g0p02` `b2019f55`), and the
  three directional arms sit outside it.
- **Other axes, no receipts:** `CONCENTRATION` `12p8km-int10` (`bcade136`, +0.008,
  −0.006…+0.018), `CONC5kmcat10` (`2dc19377`, +0.009) and their away/dose arms;
  `RELIEF` `r10`/`r15`/`r15s`; `MASS` `m10uniq`/`m10rand`/`m20uniq`;
  `SPACING` `alongstrike`/`poisson`/`lattice`; upstream `PRUNE` refills at 1–4 px.
- **Phase-2 `TRACKB` (not a weekly-slot candidate):** `fb156257` GeoJSON + 145-dot raster,
  12 strike-consistent traces ≥ 1 km (41.3 km total), per-trace evidence in
  `ledger/TRACKB_TRACES.md`.
- **Report only, never gates:** catalogue hide-and-recover CIs overlap R0 for every arm;
  leakage canary `max AUC = 0.665 < 0.90`; SGMC skipped (UNVERIFIED pin).
- **TOP_PUBLIC:** `____` — human must supply from the leaderboard with a date; no other
  target number is valid. **Slots this week:** `__ / 3` — human supplies used/available
  (3 per rolling week per entity + 1 blind final).
- **Deadline:** `2026-12-03` (≈6 weeks, ~17 rolling slots) is **UNVERIFIED**; automated
  competition-page access is barred, so the human confirms it.

## Other merged research records (separate lanes; not promoted)

The merged `main` also contains a separately documented BSTP experiment and historical TRACKB/SNAP products (`registry/run_card_bstp40.json`, `docs/index.html`, and `docs/REVIEW_AND_HYPOTHESES_20261024.md`). BSTP's stored verdict is negative; its artifacts and evaluation are distinct from this COND-EDGE run. This README's current download status remains **DO NOT SUBMIT**. See the ledger for the full inventory; do not infer that any listed file is cleared for a slot.

## Previous slot plan (historical, not current selection)

The following plan was inherited from the prior SNAP session. It is not updated to clear any submission; see the current `DO NOT SUBMIT` status above and the separate selector requirement.

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
