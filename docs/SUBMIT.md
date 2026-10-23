# SUBMIT — session GEMSDOE89 (integrated queue, 2026-10-23)

The human submits from their own registered account. Nothing here logs in,
scrapes, or uploads. One file per slot; upload the NaN-outside twin (the
`-zeros.tif` twin is the fallback and scores identically per ledger history).

## Slot 1 (allocation fork)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-relief-r10-20261023-366c87ca.tif` |
| **name** | `h33-h33-2-b2-relief-r10-20261023-366c87ca` |
| **sha256** | `366c87ca620402158cfbbf4911ed8abc8ba2da34f198694c9df7c5ea640ab335` |
| **form note** (122 chars) | `R0 h33-h33-2-b2 + RELIEF r10: 3765/37654 dots (10%) range->piedmont class, count fixed, dcat>=3px, structured; pred +0.003` |
| **predicted** | +0.003 MODEL (−0.012 … +0.018) |

## Slot 2 (placement fork — SNAP session build)

| field | value |
|---|---|
| **file** | `releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif` |
| **name** | `h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae` |
| **sha256** | `69db3aae7da2311d43a621d0c4d2ab423a3cd39acfea9cf13f666def10fd5c54` |
| **fallback** | `releases/…-69db3aae-zeros.tif` (`0fe545f9de5723e2…`) |
| **form note** (105 chars) | `R0 h33-h33-2-b2 + SNAP 2p0px-g0p00: 31,287/37654 dots moved, mean 1.86 px, targets dcat>=3px; pred +0.028` |
| **predicted** | +0.028 MODEL (−0.028 … +0.084) — widest band in the repo; the negative side prices non-fault EM crests (cards: `ledger/MECHANISM_CARDS.md` Part III) |

## Slot 3 (conditional — pick at most one, or hold)

| condition | file (name = file minus `.tif`) | predicted |
|---|---|---|
| slot 1 ≥ **0.2878** | `…-relief-r15-20261023-6aa774ce.tif` (`6aa774ce21fe10b3…`) | +0.004 (−0.017…+0.027) |
| else slot 2 ≥ **0.2878** | `…-snap1p4px-g0p00-20261023-e1474851.tif` (`e14748519b3fb35c…`) | +0.028 (−0.028…+0.083) |
| else | `…-spacing-alongstrike-20261023-3b263c7a.tif` (`3b263c7a…`) or **hold** | +0.002 (−0.003…+0.006) |

## The rest of the gated queue (names in `ledger/submissions.csv`, status BUILT)

| axis | value (sha8) | predicted | trigger |
|---|---|---|---|
| SNAP | `1p0px-g0p00` (1add5aa6) | +0.027 (−0.027…+0.081) | only if two gate-0 receipts both fire and a 3rd window point is wanted (it saturates — prefer hold) |
| RELIEF | `r15s` (5f0ae851) | +0.001 (−0.007…+0.011) | alternate definition if r10 null and the axis still needs closing |
| MASS | `m10uniq` (beed130f) | +0.002 (−0.010…+0.010) | orthogonal axis when a fork is null |
| MASS | `m20uniq` (87ec6213) | +0.004 (−0.020…+0.021) | after m10uniq ≥ +0.010 (dose) |
| MASS | `m10rand` (7a4c49b6) | −0.002 (−0.016…+0.010) | null control for m10uniq |
| SPACING | `poisson` (ff167173) / `lattice` (454c9098) | −0.010 / −0.007 | held; only if `alongstrike` ≥ +0.010 |
| upstream | gated SNAP `2p0px-g0p01` (GEMSDOE84, `b2019f55`… class) | +0.018…+0.044 | conservative first SNAP probe if the human prefers a tighter band; file is **not in this repo** |

## Format receipt (re-read from disk after writing; data gates live-verified at build)

| gate | result |
|---|---|
| grid contract vs `sample_submission.tif` (3730×3292, 100 m, EPSG:32611, float32, 1 band) | pass ×24 files |
| values in [0,1]; dots exactly 1.0; no NaN inside footprint; NaN/zeros outside per twin | pass |
| dot count 37,654 per file; twins carry identical masks | pass |
| zero catalogue mass; moved-target clearance ≥ 3.00 px (inherited 2.236-px parent collar unchanged-or-shrinking) | pass |
| sha256 not already in the ledger; no duplicate (parent, axis, value) triples | pass (127 rows) |
| R0 parent rebuild (recipe + mask paths) byte-exact vs both pins | pass (`python tools/rebuild_r0.py`) |

## Before you upload (2 minutes)

```
export GEMSDOE_DATA=/path/to/verified/inputs      # 10 pinned files + optional SGMC
python tools/fetch_pinned_data.py                 # or verify hashes yourself
python -m pytest tests -q
python tools/validate_raster.py                   # every release, every gate
python tools/check_ledger.py                      # ledger <-> disk, no dup triples
python tools/rebuild_r0.py                        # must print "[ok] R0 rebuilt byte-identical"
sha256sum releases/h33-h33-2-b2-snap2p0px-g0p00-20261023-69db3aae.tif   # must start 69db3aae
```

Then fill `receipt_score` and `receipt_date` in `ledger/submissions.csv` from the
submission-page receipt. Until that exists the file's score is **CLAIM only** —
this repo currently holds no receipt for any file, including the parent's 0.2778.
