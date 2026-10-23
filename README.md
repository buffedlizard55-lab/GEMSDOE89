# CURRENT STATE

- **Parent (verified):** `h33-h33-2-b2` — 37,654 unit dots, sha256 `c55bafc470054e82…`.
  Its **dot set is now reproduced cell-for-cell** from two independent pinned
  ancestors (`solo-d2.8` 40,199 and `d2.8` 44,090, each minus every dot within
  2.0 px of the catalogue → 0 differing cells). The parent's *file bytes* cannot
  be re-encoded here (original writer settings lost), so it is referenced by
  hash. Live **0.2778 = CLAIM** (no receipt in this repo).
- **Best receipt (this repo):** none. No file built here has been scored.
- **TOP_PUBLIC:** `____` — **not supplied**; the human must fill it from the
  leaderboard with a date. It is the only valid target number.
- **Slots this week:** `__ / __` — **not supplied**; the brief's quota is
  3 scored submissions per rolling week per entity, plus one final blind choice.
- **Axis this session:** **MASS** (the only family whose mechanism
  touches the dot count, the one operator with a measured live dose-response in
  this lineage: a 121k-px field → 44,090 → 40,199 → 37,654 dots scored 0.1922 →
  0.2600 → 0.2708 → 0.2778). Values `m10uniq`, `m10rand`, `m20uniq` were unused.
  Every earlier MASS row (six across the two fleet ledgers, some repeats) has no
  ranking recipe in the repo, and `GEMSDOE88` records its own basis as a
  distance+uniform field because **the parent's own ranking does not exist** —
  its ancestor `h19-5` is binary (`{0,1}`, 121,131 cells).
- **Week:** 2026-10-23. Deadline **2026-12-03** (≈6 weeks, 41 days) — *UNVERIFIED*:
  the competition page may not be fetched under its terms.

## Next 3 slots (detail in `SLOT_PLAN.md`)

| # | file | predicted (MODEL) | what the result would change |
|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-MASSm10uniq-20261023-beed130f.tif` | +0.002 (−0.010…+0.010) | ≥ +0.005 → mass outside the collar is waste, run the dose; \|Δ\| < 0.005 → count is not a lever, close MASS; ≤ −0.005 → only collar mass may be removed |
| 2 | `releases/h33-h33-2-b2-MASSm20uniq-20261023-87ec6213.tif` | +0.004 (−0.020…+0.021) | additive → push the dose below 30k; super-linear loss → optimum is between 33.9k and 37.6k |
| 3 | `releases/h33-h33-2-b2-MASSm10rand-20261023-7a4c49b6.tif` — or hold | −0.002 (−0.016…+0.010) | the count-matched null: tells whether the *ranking* or the *count* carried the result |

**Ceiling, stated up front:** at the `D` pinned by the one measured mass step,
a 10 % drop can gain at most **+0.0105** and a 20 % drop at most **+0.021** even
if every removed dot carries zero credit. This family cannot reach +0.03.

**Files built this session:** 3 arms × 2 encodings (NaN-outside and zeros-outside
twins), all passing every MUST gate on a re-read from disk; see
`ledger/submissions.csv` and `ledger/MECHANISM_CARDS_MASS.md`.

**What only the human can supply:** TOP_PUBLIC + date; slots used/available; a
receipt score for each submitted file (`receipt_score`, `receipt_date`); and
confirmation of the 2026-12-03 deadline. Also outstanding: the data-exposure
decision in `IRREGULARITIES.md` item 4.
