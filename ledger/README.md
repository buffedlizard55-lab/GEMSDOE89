# Ledger

`submissions.csv` (17 fields, 23 rows) is the combined record across every session on this lineage.

- **Inherited (20 rows)** — `provenance = GEMSDOE88/ledger/submissions.csv`. MASS 3, PRUNE 4,
  CONCENTRATION 4, SNAP 9. Their `sha256` values are the owner's own recorded values; this session
  did **not** re-verify those rasters (most are not mirrored any more). Status `BUILT`, no receipts.
- **This session (3 rows, `axis = RELIEF`)** — `provenance = this repo: releases/<id>.json`.
  Rasters rebuilt here, gates re-run here, hashes re-read from disk here. See `docs/SUBMIT.md`.
- **`historical_climb.csv`** — the five claimed steps from H19-5 (0.1922) to R0 (0.2778). Every
  score in it is a CLAIM; none has a submission receipt.

## Rules used here

- Dedupe only on exact `sha256` and on repeated `(parent, axis, value)`. No rank-correlation or
  dot-overlap "uniqueness" threshold is applied — the ledger shows those proxies do not track live.
- `predicted_change` is always labelled `MODEL:` and is never a score. `PROXY` values live in the
  receipts (`proxy` block) and in `evidence/relief_axis_report.json`, never in this column.
- `receipt_score` and `receipt_date` are filled by the human from the submission-page receipt.

## RELIEF build facts

| arm | source → receiving tercile | dots moved | changed | PROXY Δ (SGMC) | tercile contrast |
|---|---|---|---|---|---|
| `…RELIEFbasin10…d1a3b00d` | piedmont → basin | 3,765 | 19.9979 % | +0.00850 | +0.00029 |
| `…RELIEFpied10…b0285b17` | piedmont → piedmont (control) | 3,765 | 19.9979 % | +0.00821 | 0 |
| `…RELIEFrf10…7d62b548` | piedmont → range front | 3,765 | 19.9979 % | +0.00668 | −0.00153 |

Terciles: `det_elev` (Band 12) split at −143.06 m and +38.59 m. Removal = the 3,765 lowest
`unique_credit` dots of the source tercile (truth-free). Insertion = `det_elev_slope` (Band 19)
≥ footprint p80, `d_cat > 3 px`, NN ≥ 2.8284 px, ranked by distance to the nearest retained dot.

**The number that matters:** on the proxy, insertion is worth +0.0122 to +0.0140 and the tercile is
worth ≤ 0.0016. Read the arms as a contrast, never as three independent scores.
