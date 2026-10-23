# AI USE — session GEMSDOE89

Required by the competition rules (generative-AI disclosure in
https://docs.nlr.gov/docs/fy26osti/96647.pdf as cited in the brief).
This section is factual, not promotional: it separates what the agent produced
from what the human decided.

## What the AI wrote (this session, 2026-10-23)

- `gemsdoe/metric.py` — the DTI algebra (kernel credit T, mass S, explained M),
  the exact add/remove marginal-gain functions, and the `pays_threshold`
  helper. Derived from the formula in the brief; no organizer code was read.
- `gemsdoe/grid.py` — the submission grid contract and the byte-deterministic
  writer. GeoTIFF tags were copied programmatically from
  `sample_submission.tif`; no tag value was typed from memory.
- `gemsdoe/relief.py` — the RELIEF construction: equal-area terciles, class
  statistics, source/target choice, redundancy-ranked removal, structure-gated
  gap-filling placement.
- `gemsdoe/proxy.py` — the REPORT-ONLY instruments (catalogue hide-and-recover,
  Wilson interval, random null, rank AUC / leakage canary, surrogate DTI).
- `gemsdoe/validate.py` — the MUST gates.
- `tools/build_relief.py`, `tools/build_ledger.py`, `tools/validate_raster.py`,
  `tests/`, `.github/workflows/ci.yml`.
- `ledger/MECHANISM_CARDS.md`, `SLOT_PLAN.md`, `IRREGULARITIES.md`, this file,
  `docs/SUBMIT.md`, and the CURRENT STATE block of `README.md`.

## What the AI decided (and the human can reverse)

- **Axis = RELIEF.** The brief told the agent not to ask which axis to use. The
  choice was made from the recovered ledger: MASS (3), PRUNE (7), SNAP (3) and
  CONCENTRATION (3) already had `(axis, value)` pairs on this parent; RELIEF had
  none.
- **Source/target classes** were chosen from the pinned catalogue's density, not
  from any test label.
- **Destination rule** (structure-gated gap filling) was chosen after a first
  build placed the added dots on flat ground (mean |∇det_elev| 0.66 vs the
  parent's 13.6), which would have tested placement quality rather than relief.
  That first build was discarded and is not in the ledger.
- The **predicted changes and their bands** are the agent's MODEL, built from
  the marginal-gain algebra with an explicit, stated assumption range. They are
  not scores.

## What the human decided / must decide

- Which files to submit, and when — the human submits from their own registered
  account. The agent never submits, logs in, or scrapes the leaderboard.
- `TOP_PUBLIC`, the leaderboard date, slots used/available, and every
  `receipt_score`.
- The data-exposure decision in `IRREGULARITIES.md` item 4.

## What no AI did here

- No competition page was fetched (banned by the site terms as cited in the
  brief), no leaderboard was read, and no credentials were handled, stored, or
  transmitted.
- No model was trained on test truth; the only labels touched are the pinned,
  pixel-masked USGS/INGENIOUS catalogue, used for exclusion, for a global class
  prior, and for a REPORT-ONLY proxy.
