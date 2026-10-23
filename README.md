# CURRENT STATE

- **Parent (verified + rebuild-matched):** `h33-h33-2-b2` — 37,654 unit dots,
  sha256 `c55bafc470054e82…`; every manifest input re-hashed this session, and
  `tools/rebuild_r0.py` now **reproduces R0's bytes from its mask** and matches
  that sha256 (the dot-*selection* recipe still does not exist — see
  `IRREGULARITIES.md` item 1). Live **0.2778 = CLAIM** (no receipt in this repo).
- **Best receipt (this repo):** none. No file built here has been scored.
- **TOP_PUBLIC:** `____` — **not supplied**; the human must fill it from the
  leaderboard with a date. It is the only valid target number.
- **Slots this week:** `__ / __` — **not supplied**; the brief's quota is
  3 scored submissions per rolling week per entity, plus one final blind choice.
- **Axis this session:** **SNAP (gateless corner)** — chosen because MASS ±10 %
  and PRUNE ≤1/≤2/≤3 px were already built upstream, RELIEF was completed on
  this branch's previous session, and the ledger showed no `g0p00` value:
  upstream built (1.42, .02), (2.0, .02), (2.0, .01); this session built
  **1p0px / 1p4px / 2p0px at gate 0.00**, which turn the cross-session
  comparison into a clean *gate ablation*.
- **Week:** 2026-10-23. Deadline **2026-12-03** (≈6 weeks) — *UNVERIFIED*:
  the competition page may not be fetched under its terms, so the human must
  confirm the date.

## Next 3 slots (detail in `SLOT_PLAN.md`)

| # | file | predicted (MODEL) | what the result would change |
|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif` | +0.003 (−0.012…+0.018) | allocation fork: ≥ +0.010 → run r15; ±0.010 → close RELIEF and CONCENTRATION |
| 2 | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` | +0.028 (−0.028…+0.084) | placement fork: ≥ +0.010 → snap real, run 1p4px window dose; ≤ −0.010 → retire SNAP |
| 3 | conditional: r15 if slot 1 ≥ 0.2878; else 1p4px-g0p00 if slot 2 ≥ 0.2878; else hold | +0.004 / +0.028 | dose-response for whichever axis woke up; hold keeps one slot spare |

**Files built this session:** 3 SNAP variants × 2 encodings (NaN-outside and
zeros-outside twins), all passing every MUST gate, appended to
`ledger/submissions.csv` (3 RELIEF variants from the previous session remain
queued). Exact moved-dose: 80.83 % / 82.95 % / 83.09 % of dots, mean
displacement 1.00 / 1.35 / 1.86 px.

**What only the human can supply:** TOP_PUBLIC + date; slots used/available;
a receipt score for each submitted file (`receipt_score`, `receipt_date` in the
ledger); confirmation of the 2026-12-03 deadline; a decision on the
data-exposure item in `IRREGULARITIES.md`; and whether to also retrieve the
upstream gated SNAP / MASS / PRUNE files from GEMSDOE84's releases (they are
not in this repo).
