# AI USE — session GEMSDOE89

Required by the competition rules (generative-AI disclosure in
https://docs.nlr.gov/docs/fy26osti/96647.pdf as cited in the brief).
This section is factual, not promotional: it separates what the agent produced
from what the human decided.

## What the AI wrote

**Earlier session (RELIEF, 2026-10-23, superseded but still in the repo)**

- `gemsdoe/metric.py` — the DTI algebra (kernel credit T, mass S, explained M),
  exact add/remove marginal-gain functions, `pays_threshold`.
- `gemsdoe/grid.py` — the submission grid contract and byte-deterministic writer;
  GeoTIFF tags copied programmatically from `sample_submission.tif`.
- `gemsdoe/relief.py`, `gemsdoe/proxy.py`, `gemsdoe/validate.py`,
  `tools/build_relief.py`, `tools/validate_raster.py`, `tools/check_ledger.py`,
  `tests/test_metric.py`, `tests/test_grid_validate.py`,
  `.github/workflows/ci.yml`, the RELIEF cards, `docs/SUBMIT.md`.

**This session (MASS, 2026-10-23)**

- `gemsdoe/mass.py` — the unique-credit ranking (`u_i` = credit a dot can claim
  when it is the strictly nearest dot under a flat truth prior), the drop
  selector, block-density CV, nearest-neighbour statistics, and the
  break-even band `dDTI = -n(k - 0.2*DTI)/D`.
- `tools/build_mass.py` — the gated build: manifest verification → parent
  identity proof from two ancestors → three drop-only arms → twins → re-read →
  every MUST gate → build reports.
- `tests/test_mass.py` — 9 unit tests for the ranking and the drop-only
  invariants (24 tests total in the suite).
- `ledger/MECHANISM_CARDS_MASS.md`, the rewritten `SLOT_PLAN.md`,
  `README.md` CURRENT STATE, `docs/SUBMIT.md`, `IRREGULARITIES.md` items 1, 6,
  7 and 8-11, and this file.
- The fleet and ancestor fetches, the geometry analyses (catalogue-distance
  profile, block-scale prior vs parent density, per-dot credit attribution, the
  fleet score↔geometry correlations), and the calibration of the ranking on the
  one measured mass step.

## What the AI decided (and the human can reverse)

- **Axis = MASS.** The brief forbade asking which axis to use. Reasoning: MASS
  is the only family whose mechanism touches the *count*, and the count is the
  one operator with a measured live dose-response inside this lineage
  (a 121k-px field → 44,090 → 40,199 → 37,654 dots scored 0.1922 → 0.2600 →
  0.2708 → 0.2778). CONCENTRATION, SNAP, PRUNE, RELIEF and SPACING all hold
  count fixed; SPACING is already taken by GEMSDOE91 session 3; and the fleet's
  six existing MASS rows have no recorded ranking basis.
- **Ranking = unique kernel credit** rather than distance to the catalogue,
  because the second is a covert PRUNE and because the metric's own max operator
  is what makes duplicated mass worthless. The consequence was measured: only
  1.54 % of the dropped dots are inside the 3 px collar (base rate 4.28 %), so
  this is not another collar arm.
- **A random control arm** (`m10rand`) was built instead of a third dose. It
  costs one build and is the only way to tell whether the ranking or the count
  carried the result.
- **Predictions are bands**, not point estimates, because the ranking failed its
  only calibration (see `IRREGULARITIES.md` item 9). The arithmetic ceiling of
  each arm is stated explicitly (+0.0105 / +0.021).
- **The parent's identity was proved at the dot-set level** from two pinned
  ancestors; the file *bytes* are not re-encodable and that is recorded.

## What the human decided / must decide

- Which files to submit, and when — the human submits from their own registered
  account. The agent never submits, logs in, or scrapes the leaderboard.
- `TOP_PUBLIC`, the leaderboard date, slots used/available, and every
  `receipt_score`.
- The data-exposure decision in `IRREGULARITIES.md` item 4.
- Whether to accept the derived ranking (item 8) or retire these files if the
  original ranking artefact is ever found.

## What no AI did here

- No competition page was fetched (banned by the site terms as cited in the
  brief), no leaderboard was read, and no credentials were handled, stored, or
  transmitted.
- No model was trained on test truth; the only labels touched are the pinned,
  pixel-masked USGS/INGENIOUS catalogue, used for exclusion, for the fleet
  distance statistics, and for REPORT-ONLY proxies.
- No file was built to probe where public-test faults are: all three arms are
  drop-only edits of the incumbent, and no region-isolated or patterned raster
  was produced.
