# CURRENT STATE

- **Parent (rebuilt & byte-verified):** `h33-h33-2-b2` (`GEMSDOE32`, 37,654 unit-mass dots) — rebuilt bit-for-bit from `scored_h19_5.tif` via `dot_thin(r=2.8 px) & (d_cat > 2.0 px)` using `sample_submission.tif` as template (`tools/rebuild_r0.py`): `sha256_zeros` `c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9` (matches parent pin), `sha256_nan` `baeae321d33f676473d31a158da4e4eb15ca55897d2d9c9af3a38de0cb48fc04`. Live **0.2778 = CLAIM** (no receipt in this repo).
- **Best receipt (this repo):** none. All 9 `GEMSDOE89` release pairs (`3 SPACING + 3 RELIEF + 3 MASS`, 18 `.tif` files in `releases/`) are `BUILT (unscored)`.
- **TOP_PUBLIC:** `____` — **not supplied**; the human must fill it from the leaderboard with a date (`UNVERIFIED` here; automated `drivendata.org` access is barred by ToS).
- **Slots this week:** `__ / 3` — **not supplied** (one entity at 3 scored slots/rolling week + 1 blind final choice).
- **Axis this session:** **`SPACING`** — unused across all ledger rows (`alongstrike`, `poisson`, `lattice`), changing 13.87%–20.29% of R0 dots at fixed count (`n=37,654`), 5 km density CV (`0.8991 -> 0.8984..0.9001`), and relief terciles (`<=0.9%` drift). Earlier `GEMSDOE89` sessions built `RELIEF` (`r10`, `r15`, `r15s`) and `MASS` (`m10uniq`, `m10rand`, `m20uniq`).
- **Week:** 2026-10-23. Deadline **2026-12-03** (`~5.9` weeks / 41 days; ~18 scored slots + 1 final blind choice) — `UNVERIFIED` pending human confirmation.

## Next 3 slots (detail in `SLOT_PLAN.md`)

| # | file | predicted (`MODEL`) | decision trigger (`<0.01` = no evidence) |
|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-spacing-alongstrike-20261023-3b263c7a.tif` | `+0.002` (`-0.003..+0.006`) | `>= 0.2878` (`+0.010`): test `poisson` in Slot 2; `0.2678..0.2878`: close `SPACING`, pivot to `SNAP` / `MASS m10uniq` / `RELIEF r10`; `<= 0.2678`: freeze greedy-`r=2.8` strands |
| 2 | Conditional: `releases/h33-h33-2-b2-spacing-poisson-20261023-ff167173.tif` (only if Slot 1 `>= 0.2878`), else `releases/h33-h33-2-b2-MASSm10uniq-20261023-beed130f.tif` or `RELIEF r10` (`366c87ca`) | `-0.010` (`-0.032..+0.004`) for `poisson`; `+0.002` for `m10uniq`; `+0.003` for `r10` | Separates 1D along-strike equalization from 2D lateral corridor spread (or tests orthogonal `MASS` / `RELIEF` axis) |
| 3 | **HOLD** (`releases/h33-h33-2-b2-spacing-lattice-20261023-454c9098.tif` held unless Slot 2 `poisson >= Slot 1 + 0.010`) | `-0.007` (`-0.025..+0.003`) | Preserves weekly slot budget for `SNAP` (`GEMSDOE84` `2p0px-g0p02`) or proposed `RELAY-BRIDGE` / `REPEAT-CALIBRATION` |

**Files built this session:** 3 `SPACING` arms x 2 encodings (`releases/h33-h33-2-b2-spacing-*.tif` + `-zeros.tif`; repo total 18 `.tif` files across `SPACING`, `RELIEF`, `MASS`), all passing every MUST gate on disk re-read; see `ledger/submissions.csv` and `ledger/MECHANISM_CARDS.md`.

**What only the human can supply:** `TOP_PUBLIC` + date; weekly slots used/remaining; DrivenData submission + live `RECEIPT` (`receipt_score`, `receipt_date`) for each submitted file; confirmation of the `2026-12-03` deadline; and governance sign-off on `IRREGULARITIES.md`.
