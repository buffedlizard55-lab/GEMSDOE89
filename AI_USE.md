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

## What the AI wrote (SNAP session, 2026-10-23, branch `arena/7efbb7cc-gemsdoe89`)

- `gemsdoe/snap.py` — the gateless SNAP construction: response recipe
  (median fill → gaussian σ=1 → robust_unit p99.5 → max fusion of bands
  3/18), deterministic snap algorithm, displacement/CV statistics.
- `tools/rebuild_r0.py` — the start gate: rebuilds R0 from its mask with the
  parent writer profile and requires a byte-exact match to `c55bafc47005…`
  (it matches).
- `tools/build_snap_gateless.py` — verifies every manifest hash, rebuilds R0,
  builds the three variants, writes both encodings, re-reads from disk, runs
  the MUST gates, appends the ledger rows, writes
  `registry/build_report_snap_<value>.json`.
- `tests/test_snap.py` — window/gate invariants, allowed-mask enforcement,
  count preservation, determinism.
- SNAP mechanism cards appended to `ledger/MECHANISM_CARDS.md`; updated
  `SLOT_PLAN.md`, README CURRENT STATE, `docs/SUBMIT.md`, this file, and the
  reproducibility note in `IRREGULARITIES.md` item 1.

## What the AI decided (and the human can reverse)

- **Axis = SNAP, values = 1p0px/1p4px/2p0px at gate 0.00.** Brief v2 says not
  to ask. Chosen from the ledger: MASS ±10 % and PRUNE ≤1/≤2/≤3 px were already
  built upstream, RELIEF was completed on this branch's previous session, and
  no `g0p00` value existed anywhere — the gateless corner is the brief's
  literal SNAP definition and turns receipts into a clean gate ablation
  against upstream's three gated arms.
- **Response recipe replicated exactly** from the upstream recorded recipe
  (bands 3 + 18, fill/σ/robust-unit/fusion) so the gate is the only
  cross-session difference; band identities come from the manifest's
  `band_identity_source`, not from memory.
- **Collar handling inherited** from IRREGULARITIES item 2: targets ≥ 3 px
  enforced; the parent's 1,611 diagonal-collar dots may stay (they never move
  closer; collar shrank to 575/666/938). Reversal would be a second
  simultaneous change (PRUNE), already built upstream.
- **Prediction bands** use the upstream live-anchor inversion
  (D = 18,734.44) with an explicit −0.05/+0.05/+0.15 scenario on moved dots —
  the negative side is this session's addition (upstream bands had none).
  Evidence class MODEL; never a score.
- The three report-only instruments (hide-and-recover PROXY, catalogue
  surrogate, leakage canary) were computed and reported; none gated a file,
  and none set a predicted sign.

## What only the human can supply (unchanged + new)

- All submission decisions and every `receipt_score`; `TOP_PUBLIC` + date;
  slots used/available; the 2026-12-03 deadline confirmation; the
  data-exposure decision (IRREGULARITIES item 4).
- **New:** whether to also queue the upstream gated SNAP / MASS / PRUNE files
  held in GEMSDOE84's releases (not present in this repo; not fetched here).
