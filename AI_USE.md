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

---

# Second session (2026-10-23, SPACING axis)

## What the AI wrote

- `gemsdoe/spacing.py` — the SPACING constructions: nearest-neighbour geometry,
  the greedy hard-disk independent set, the structure-tensor strike estimate
  (derived only from the parent raster), the vectorised relocation engine with
  its repair pass, the coverage-area statistic and the coverage→DTI model.
- `tools/build_spacing.py` — manifest/parent verification, the build, the
  twin write, the gates (including two new ones: new positions ≥ 3 px from the
  catalogue, and no dot pair tighter than the parent's own 2.828 px disk),
  the REPORT-ONLY instruments, the ledger rows and the build reports.
- `tests/test_spacing.py` — 7 tests on synthetic ribbon fields (no competition
  data): independent-set separation, count preservation, determinism,
  clearance, footprint containment, coverage monotonicity, prediction algebra.
- `ledger/MECHANISM_CARDS.md` (SPACING section), `SLOT_PLAN.md`,
  `docs/SUBMIT.md`, the CURRENT STATE block of `README.md`, this section, and
  irregularity item 8.

## What the AI decided (and the human can reverse)

- **Axis = SPACING.** Chosen, not assigned, because it was the only axis with no
  `(axis, value)` pair anywhere in the recovered ledger (RELIEF was spent in the
  first session; MASS, PRUNE, SNAP and CONCENTRATION already had pairs on this
  parent). It also needs no external data: parent + template + catalogue only.
- **No lattice arm.** The brief suggests lattice vs Poisson-disk vs along-strike.
  Measuring R0 first showed a hard disk at 2.828 px, so a lattice or a
  fully-rebuilt Poisson field would change > 50 % of the dots and break the
  brief's own 1–50 % constraint. Dose + geometry arms were built instead; the
  reason is logged as IRREGULARITIES item 8.
- **A build defect was found and fixed before release.** The first pass let a
  dot whose relocation failed stay in place while later placements ignored it,
  producing 26 dot pairs at 1.0–2.24 px — tighter than the parent's own disk.
  A repair pass now reverts any placement that lands within the target radius of
  a stayer, and a MUST gate asserts the invariant. The defective files were
  deleted, their ledger rows removed, and every file here is from the fixed
  build (see `registry/build_report_spacing_*.json`, `n_reverted_by_repair`).
- **Predictions are MODEL.** Each is the coverage-area integral converted to DTI
  through dDTI = (1 − 0.2·DTI)·DTI·(dT/T) at the claimed parent DTI. The band's
  negative side is the stated alternative assumption (truth concentrated on the
  parent's own saturated ribbons). None of these is a score.

## What the human still decides

Which file to submit and when; `TOP_PUBLIC`; slots used/available; every
`receipt_score`; the deadline confirmation; the data-exposure decision.

## What no AI did here

No competition page was fetched, no leaderboard was read, no credentials were
handled, no test labels were used. The only labels touched are the pinned
pixel-masked USGS/INGENIOUS catalogue, used for exclusion and for REPORT-ONLY
instruments that cannot gate a file.
