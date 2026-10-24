# GEMSDOE89 — executive summary and submission status

## Latest safety review — 2026-10-24

**OK to download for research; NOT OK to submit.** The existing COND-EDGE experiment was reproduced from hash-pinned features. This is not a new scientific submission. Its negative HOLDOUT-DTI and file hash reproduced; its NaN-outside encoding also fails the new all-finite upload check. No weekly slot was used.

- [Automated readiness report](registry/submission_readiness.json) — fails closed on missing evidence, negative holdout, incomplete registry coverage, stale hash, or unsafe upload values.
- [Three-pass review, source audit, ranked follow-ups and limitations](docs/AUDIT_20261024.md).
- Shared writer now defaults to finite zeros outside the footprint; the historical research evaluator explicitly retains NaN encoding. Renaming/re-encoding an existing artifact never establishes novelty.
- Existing mirror data are obtainable here; “data placement is the only blocker” is no longer accurate. The blocker is evidence of a distinct, better-performing model plus complete uniqueness/provenance checks.

Run the automatic decision (exit **2** = blocked, **0** = eligible for a separate selector, never automatic upload):

```bash
python tools/submission_readiness.py registry/run_card_condedge_20261024.json --output registry/submission_readiness.json
```

### Standing user instructions (operative summary, not a verbatim transcript)

Read this README and `PROMPT.md` every session. Prioritize a genuinely unique GeoTIFF and an unmistakable download/submission status at the beginning of the site. Use one assigned method lane, the shared cached feature stack/evaluator/writer, whole-segment buffered hide-and-recover, visible-only catalogue features and exact visible-fault masking, pooled triangular-kernel DTI, feature-by-feature leakage canaries, and surface plus final-dot registry checks. Stop on duplicates. Register and rank three to five geological hypotheses before implementing; test the top candidate against the locked current holdout best. Do not equate projections with scores. Use official sources and label inaccessible or unverified evidence honestly. Stop within three experiments or two hours; no slot selection in research. Finish with a JSON run card, including negative results. Perform implementation, adversarial review, and requirement reconciliation passes; open a PR and merge only after checks. Keep **Maximize P(Win)** and **Own the Outcome** central. The supplied prompt omitted its promised single-method paragraph; do not silently invent a lane. The full verbatim request remains in the conversation; the repo preserves this maintained operational summary and the existing score ledger.

---

> **DOWNLOAD STATUS: DO NOT SUBMIT.** This session generated and format-validated a locally unique candidate GeoTIFF, but its spatial holdout was decisively worse than the visible-only R0 baseline. It is preserved as a negative research result, not a recommended competition entry.
>
> [Download the research TIF](releases/h89-condedge-s2-4-20261024-829cc418-candidate.tif) · [Run card](registry/run_card_condedge_20261024.json) · [Holdout and uniqueness gates](docs/HYPOTHESIS_REGISTER.md) · [How contest submissions work](docs/SUBMIT.md)

- **Candidate:** `h89-condedge-s2-4-20261024-829cc418-candidate.tif` — SHA-256 `829cc41856540a9361aeaffcba5af9010168b513a332c10a7e92da21c99daa4d`.
- **HOLDOUT-DTI** (`GEMSDOE89-spatial-segment-holdout-v1`; 59,168 withheld positive pixels; 95% spatial-tile bootstrap CI): COND-EDGE **0.049875** `[0.036830, 0.061751]`; visible-only R0 comparator **0.161230** `[0.142648, 0.180061]`; paired delta **−0.111355** `[−0.133218, −0.087864]`. This is a local holdout, not a leaderboard score.
- **Leakage canary:** 20 single-feature tests; maximum AUC strength `0.5698`, below the `0.90` investigation threshold.
- **Local registry check (rerun after merging upstream main):** pre-placement score-surface maximum absolute Spearman `0.0387`; disk-reread final-raster maximum absolute Spearman `0.0128`; maximum final-dot overlap within 3 px `19.50%`; exact SHA-256 unique against 229 other ledger hash values. No duplicate-stop. Geometry comparison covers 36 locally available registry masks / 69 paths, **not every remote GeoTIFF in every public GEMSDOE site**.
- **Historical research-format validator:** PASS (all-finite upload gate FAIL) — one float32 band, EPSG:32611, shape 3730×3292, exact sample-template transform, no NaN inside the footprint, finite values 0–1, NaN only outside, zero dots on exact known-fault pixels.
- **Decision:** verdict `negative`; no upload, no slot selection. The separate slot selector remains responsible for any future promotion.

## Read first on every session

The static site is [`index.html`](index.html) with the dedicated [`submit.html`](submit.html) submission guide. `docs/index.html` and `docs/submit.html` are generated publishing mirrors (run `python tools/build_pages_site.py`) for GitHub Pages configured to publish the `docs/` folder. Read [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md) and the upstream [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md) / [`PROMPT.md`](PROMPT.md) before research or coding, then inspect `README.md`, `IRREGULARITIES.md`, `SLOT_PLAN.md`, `docs/SUBMIT.md`, and the full local ledger. The brief carries the original mission, Arena values (**Maximize P(Win)** and **Own the Outcome**), experiment budget, holdout rules, evidence labels, uniqueness thresholds, submission gates, and trusted source links.

## Why the `0.2778` result is not yet an established target

The local evidence verifies R0's geometry and file identity, not the cause of its live result. R0 is reproduced as a 2.8-pixel-thinned `h19_5` ridge set pruned using the known-fault catalogue, yielding 37,654 unit-mass dots; its reported **0.2778 is CLAIM, not ORGANIZER-CONFIRMED** because no submission-page receipt is stored in this repository. Plausible contributors include multi-layer geophysical ridge continuity, sparse placement, and the recorded catalogue prune, but a single result cannot establish which mechanism caused the score. The request also gives `0.3195` and `0.4413` as different leaderboard snapshots without dates or receipts; neither is independently confirmed here. See the hash-verified recipe in [`gemsdoe/parent.py`](gemsdoe/parent.py), [`registry/parent_verification.json`](registry/parent_verification.json), and official metric rules in the [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).

## This session — one COND-EDGE experiment

The top-ranked new hypothesis was a multi-scale gradient of band 17 `cond_surf`. Its scientific rationale and three alternatives are registered in [`docs/HYPOTHESIS_REGISTER.md`](docs/HYPOTHESIS_REGISTER.md). It did **not** beat the visible-only R0 comparator under the new spatially blocked, whole-segment hide-and-recover evaluator; the negative TIF remains available for auditing and must not be uploaded. No external raster was needed. One experiment was run, below the three-experiment/two-hour cap.

Reproduce (after dependencies and pinned data are available):

```bash
python tools/fetch_pinned_data.py
python tools/rebuild_r0.py
python tools/evaluate_holdout.py
```

The evaluator rechecks input hashes, tests each feature alone on spatially held-out fault segments, audits the pre-placement signal and final raster against locally available registry rasters, and calls the shared [`tools/submission_writer.py`](tools/submission_writer.py). It does not access DrivenData or upload a file. A valid GeoTIFF is **not** automatically a good submission.

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
