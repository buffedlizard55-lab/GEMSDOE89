# SLOT_PLAN — one entity, 3 slots/week, one blind final file by 2026-12-03

**Entity budget:** 1 (`buffedlizard55-lab`). Slots left this week: `__ / 3` (human fills).
**Deadline 2026-12-03: UNVERIFIED** — this agent may not read the competition page.
**TOP_PUBLIC:** `____` (human fills; the sibling session recorded 0.4413 on 2026-10-22, CLAIM).
**Parent:** `R0 = h33-h33-2-b2`, 37,654 dots, CLAIM 0.2778 (no receipt). Rebuild: **byte-exact**
(`c55bafc4…` / `baeae321…`).
**Session axis:** `RELIEF`. 3 arms built, 0 receipts.

## Next 3 slots, in order

| Slot | Release | Change vs R0 | PROXY Δ (SGMC) | Tercile contrast vs control | Predicted live Δ | What the result changes |
|---|---|---|---|---|---|---|
| 1 | `…RELIEFbasin10…d1a3b00d` | piedmont → basin, 10 % (19.9979 % of dots) | **+0.00850** | **+0.00029** | MODEL +0.008 [−0.004, +0.016] | ≥ +0.01: intrabasin/buried faults are the target → next axis is basin-interior lineaments. ≤ −0.01: basin ground is shorelines, close it. |
| 2 | `…RELIEFpied10…b0285b17` (CONTROL) | reshuffle inside piedmont, terciles unchanged | **+0.00821** | 0 by construction | MODEL +0.008 [−0.004, +0.016] | Calibrates every arm: `arm − control` is the only tercile evidence. ≥ +0.01: the *placement rule* is the winner, not the axis. |
| 3 | `…RELIEFrf10…7d62b548` | piedmont → range front, 10 % | **+0.00668** | **−0.00153** | MODEL +0.007 [−0.005, +0.015] | ≥ +0.01: range-front splays dominate; map those next. ≤ control − 0.01: range fronts are already mapped (and masked), as the mechanism card predicts. |

**Read the arms as a contrast, never as three independent scores.** All three share one removal set
(the 3,765 lowest-`unique_credit` piedmont dots) and one insertion rule, so:

- `basin10 − pied10` and `rf10 − pied10` are the tercile effects.
- The proxy puts both contrasts inside ±0.0016, i.e. **an order of magnitude under the 0.01
  "evidence" bar**. Honest expectation: this week resolves the *placement* effect, not the tercile.

Decision rule for the week:
1. If any arm ≥ R0 + 0.01 live → promote it to `R1`, re-base next week's axis on it.
2. If all three land within ±0.005 of R0 → RELIEF is dead at 10 %; spend week 2 on `REPLACE` below.
3. If the control beats both shifts by ≥ 0.01 → the gain is de-duplication plus sharp-ground
   placement; drop the tercile variable entirely.

## Weeks 2–6

- **Week 2 (slots 4–6) — `REPLACE` (proposed axis, not built this session).** Move the 10–20 % of
  dots with the lowest `unique_credit` onto the sharpest ground at matched spacing with **no tercile
  change**. Mechanism: a dot whose kernel footprint is shared with a neighbour supplies almost no
  credit a truthful field could lose; the same dot re-placed on uncovered sharp ground is free
  coverage. Confounder: sharp ground is shorelines, fan-head channels and roads. Falsifier: < +0.01
  live over the `pied10` control. *This is the axis the proxy says is worth real money (+0.0137 from
  insertion alone vs +0.0003 from the tercile).*
- **Week 3 (slots 7–9) — `BASIN_LINEAMENT` (proposed).** Second-derivative magnetic/gravity
  lineaments (Bands 4, 18) restricted to the basin tercile, inserted at the same spacing lock.
  Tests the buried-fault hypothesis directly. Confounder: cultural and processing artefacts along
  flight lines. Falsifier: < +0.01 over `REPLACE`.
- **Week 4 (slots 10–12) — combine the two best receipts** (a single edit each, logged as a new
  parent). Nothing combined before it has a receipt over its own parent.
- **Week 5 (slots 13–15) — confirm** the best composite on a second chunk set; build `TRACKB`
  (strike-consistent ≥ 1 km traces) only if a Phase-2 path is confirmed.
- **Week 6 (slots 16–18) — lock ONE blind final file + ONE `-zeros` fallback**, re-validate the
  format of both, freeze `docs/SUBMIT.md`.

## Standing constraints

- One change per parent per build; every new `(parent, axis, value)` is checked against
  `ledger/submissions.csv` (23 rows: MASS 3, PRUNE 4, CONCENTRATION 4, SNAP 9, RELIEF 3) first.
- Never infer a mass effect from file names; mass is confounded with field.
- Treat any live change < 0.01 as no evidence — public chunks only.
- `docs/SUBMIT.md` is authoritative for file, name, note and format receipt.
