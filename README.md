# CURRENT STATE

- **Parent (recipe-rebuilt, byte-verified 2026-10-24):** `h33-h33-2-b2` — 37,654 unit dots; `c55bafc470054e82…` (zeros) and `baeae3219bba6a19…` (NaN). All 10 fetchable manifest pins pass. Live **0.2778 = CLAIM**; **best receipt: none**.
- **Built, unscored:** **24 pairs / 48 GeoTIFFs**, all `BUILT` and format/data-gated. The 2026-10-24 session added exactly the three missing **SNAP** cells, completing the 3-window × 3-gate factorial with prior local/upstream cells; no `(SNAP, value)` repeat.
- **New SNAP arms (`ledger/MECHANISM_CARDS.md` Part VII):**
  - `1p4px-g0p01` (`afc60a25`): 6,767 moved (17.972%), mean 1.370 px; **+0.0120 MODEL** (`−0.0060…+0.0301`) — primary new arm.
  - `1p0px-g0p01` (`2916ec2d`): 4,265 moved (11.327%), mean 1.000 px; **+0.0076 MODEL** (`−0.0038…+0.0190`) — conditional fixed-gate window control.
  - `1p0px-g0p02` (`384435e6`): 1,245 moved (3.306%), mean 1.000 px; **+0.0022 MODEL** (`−0.0011…+0.0055`) — held high-gate boundary.
- **Report only:** catalogue hide-and-recover CIs overlap R0; SNAP-response leakage canary `max AUC=0.66538 < 0.90`; SGMC remains skipped/UNVERIFIED. None gates a release or is a live score.
- **TOP_PUBLIC:** `____` — human must supply from the leaderboard with a date; no other target number is valid. **Slots this week:** `__ / 3` — human supplies used/available.
- **Deadline:** `2026-12-03` is **UNVERIFIED** because automated competition-page access is barred; human confirms.

## Next 3 slots (details in `SLOT_PLAN.md` and `docs/SUBMIT.md`)

| # | file | predicted (`MODEL`) | decision triggered by receipts |
|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-snap1p4px-g0p01-20261024-afc60a25.tif` | +0.0120 (`−0.0060…+0.0301`) | `>=0.2878` supports SNAP; `<=0.2678` rejects this gated correction; otherwise no evidence. |
| 2 | `releases/h33-h33-2-b2-snap1p4px-g0p00-20261023-e1474851.tif` | +0.0278 (`−0.0278…+0.0834`) | Matched gateless control. Slot 1 beating it by `>=0.010` supports selectivity; the reverse supports dose. |
| 3 | conditional: `1p0px-g0p01` (`2916ec2d`) after a gated win; else `2p0px-g0p00` (`69db3aae`) after any SNAP signal; else `CONC5kmcat20` (`4d229938`) or **HOLD** | +0.0076 / +0.0278 / +0.019 | Tests fixed-gate window, gateless window dose, or pivots after two null SNAP receipts. |

**Human must supply:** `TOP_PUBLIC` + date; slots used/available; every uploaded file's `receipt_score` + `date`; deadline confirmation; public-mirror review (`IRREGULARITIES.md` item 2); and all upload/final-file choices. Upload only one twin per slot; the human submits manually.
