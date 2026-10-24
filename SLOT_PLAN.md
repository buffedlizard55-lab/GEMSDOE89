# SLOT PLAN — GEMSDOE89 / Promoted `H89 BH-RTP-HABC` Discovery + Matched `R0` Perturbation Controls (2026-10-24)

- **Entity/quota:** one entity, 3 scored submissions per rolling week + 1 blind final (`ORGANIZER-CONFIRMED` rules page 966). Slots used/left this week: `__ / 3` (human supplies; agent does **not** upload live submissions).
- **Leaderboard anchors:** Fleet parent `R0 = h33-h33-2-b2` (`0.2778` `CLAIM` on `GEMSDOE32`); best fleet score `GEMSDOE83` `h83-gvcd-dink300-37654dots` (`0.3195` `CLAIM`); top public leaderboard `0.4413` (`CLAIM`). Pure pruning of the `121,131`-px `h19_5` skeleton has a strict algebraic ceiling of **`0.3107`** at zero false-positive removal — crossing `0.32 -> 0.44+` requires genuine off-`h19_5` concealed-basin and relay-bridge fault discovery (`docs/preregistration-h89.md`).
- **Evidence labelling discipline:** Every holdout figure below is explicitly labelled **`HOLDOUT-DTI`** (`evaluator_version = gems57-pooled-hide-v2`, `K = 11,321` withheld positive pixels across `NW/NE/SW/SE`, `1,000` paired spatial-block bootstrap draws). Neither **`HOLDOUT-DTI`** nor **`MODEL`** is a live leaderboard score; any live public-chunk change with `|Δ| < 0.010` counts as **no evidence**.
- **Format recommendation (`IR-89-18`):** Upload the **`-zeros.tif`** (`nodata = None`, zero `NaN` anywhere, strict `[0.0, 1.0]` `float32`, matching Lipor's official `drivendataorg/gems-prize-reference-solution` `generate_submission.py`) to guarantee zero `"Predicted values must be in range [0, 1]"` validator errors.

---

## Primary Promoted Candidate (Slot 1 Recommendation)

| Slot | Artifact & Submission Name | Evidence (`HOLDOUT-DTI`, `gems57-pooled-hide-v2`, `K=11,321`) | Gates & Uniqueness (`84` unique rasters) | Form Note (`<= 140` chars) |
|---|---|---|---|---|
| **1 (PROMOTE)** | `docs/downloads/gemsdoe89-bh-rtp-habc-20261024-d7e1507c-zeros.tif`<br>*(CI twin: `releases/gemsdoe89-bh-rtp-habc-20261024-d7e1507c-zeros.tif`)*<br>**Name:** `gemsdoe89-bh-rtp-habc-20261024-d7e1507c-zeros` | **`0.16027`** (`95% CI [0.14498, 0.17553]`) vs `R0` fold-fair `0.09609` (`[0.08334, 0.10934]`); **paired `Δ = +0.06418` (`[+0.04928, +0.08033]`, `+66.8%` lift)**; wins **4 / 4** quadrants (`NW +83%`, `NE +27%`, `SW +110%`, `SE +54%`). | **`15 / 15` PASS** (`[0, 1]`, `0` NaN, `EPSG:32611`, `3730x3292`, `37,654` dots, `min d_cat = 3.00 px`).<br>Canary: `max AUC = 0.7829 <= 0.90` (`0/42` flagged).<br>Uniqueness: `max |ρ| = 0.1118 <= 0.90`, `max 3-px overlap = 0.5866 <= 0.70`, **`26.99%` overlap vs `R0`** (`73.01%` new conduits). | `H89 BH-RTP-HABC dual-LOQO+CELF300m: 37654 dots, dcat>=3px; HOLDOUT-DTI 0.1603 (+0.0642 vs R0 fair)` *(98 chars)* |

### Secondary / Diagnostic R0-Perturbation Slots (Slots 2–3, Optional Within Quota)

If the selector chooses to spend remaining weekly slots reading local crest-offset physics on parent `R0` (`h33-h33-2-b2`) alongside Slot 1's genuine discovery jump:

| # | File | Predicted (`MODEL`) | What the live receipt tests |
|---|---|---|---|
| **2** | `releases/h33-h33-2-b2-snapdirfw2p0-20261024-dc578b2f-zeros.tif` | `−0.019…+0.056` (`MODEL`) | Footwall/up-slope (`cos >= +0.5`) 2 px HG-crest snap on `R0`. Half of a matched directional pair. |
| **3** | `releases/h33-h33-2-b2-snapdirhw2p0-20261024-5cccfc1d-zeros.tif` | `−0.019…+0.057` (`MODEL`) | Exact mirror hanging-wall/down-slope (`cos <= −0.5`) 2 px snap. `fw − hw >= +0.010` tests footwall trace offset vs crest fidelity. |

---

## 3-Experiment Discovery Summary Executed in `GEMSDOE89` (Strict `<= 3` Cap)

| Exp ID | Lane / Hypothesis | Pooled `HOLDOUT-DTI` (`95% CI`) | Quadrant Breakdown (`NW / NE / SW / SE`) | Decision |
|---|---|---|---|---|
| Control | `r0_fold_fair` (`h33-h33-2-b2` rebuilt on visible network) | `0.09609 [0.08334, 0.10934]` | `0.0883 / 0.1112 / 0.0829 / 0.1044` | Baseline |
| Control | `d28_static` (`44,090` dots ancestor) | `0.09189 [0.07961, 0.10453]` | `0.0818 / 0.1128 / 0.0821 / 0.0956` | Baseline |
| **E89-1** | `H89-B` Pure 30-feature zero-catalogue physics + CELF | `0.08580 [0.06963, 0.10132]` | `0.0883 / 0.0787 / 0.0693 / 0.1095` | Beats `R0` fair in `NW` & `SE` with **zero** fault-catalogue inputs |
| **E89-2** | **`H89-A+B+C` Self-Masked Dual-Expert LOQO + Analytical-Self-Credit Global CELF** | **`0.16027 [0.14498, 0.17553]`** | **`0.1617 / 0.1413 / 0.1740 / 0.1604`** | **PROMOTED (`+0.06418`, `+66.8%` over `R0` fair)** |
| **E89-3** | `H89-A+B+C` 3-Regime Cover-Stratified CELF (`Bedrock / Piedmont / Basin`) | `0.15120 [0.13700, 0.16603]` | `0.1613 / 0.1403 / 0.1520 / 0.1527` | Strong runner-up (`+57.4%` over `R0` fair); `E89-2` wins by `+0.00907` |

---

## Schedule to Competition Close

| Window | Action |
|---|---|
| **Week 1 (Current)** | Selector reviews `gemsdoe89-bh-rtp-habc-20261024-d7e1507c-zeros.tif` (`15/15` PASS) for Slot 1; records live public-chunk receipt + date in `ledger/submissions.csv`. |
| **Week 2** | Compare live receipt of `H89` (`BH-RTP-HABC`) against fleet `0.2778` (`GEMSDOE32`) and `0.3195` (`GEMSDOE83`); only retain axes clearing `Δ >= +0.010`. |
| **Final Selection** | Re-verify `sha256` (`715c8b86…`) and `15/15` validator checks; human selector designates 1 blind final submission within competition rules. |
