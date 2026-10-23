# Submission Sheet — one file per slot (DrivenData #306, one entity, 3 slots/week)

> The human uploads from their own registered account. This agent never logs in, never reads the
> leaderboard and never scores anything. Every `sha256` below was re-read from disk after writing.

**Parent:** `R0 = h33-h33-2-b2` — 37,654 unit-mass dots, 0 within 2 px of the catalogue, CLAIM 0.2778
(no receipt exists). **Rebuild status: byte-exact.** Both published encodings reproduce:
`zeros c55bafc4…` (219,065 B) and `nan baeae321…` (355,443 B), from the recorded
H19-5 → D1.5 → D2.8 → SOLO-D2.8 → R0 recipe (`scripts/rebuild_r0.py`, `registry/r0_verification.json`).
Byte-exactness required the parent's *libdeflate* encoder; see IRREGULARITIES.md IR-89-01.

**Session axis:** `RELIEF`. Three arms, all draining the **piedmont** tercile of `det_elev`
(training_features Band 12) and re-inserting 10.00 % of the dots into one receiving tercile.
Count fixed at 37,654. Every arm changes 19.9979 % of the dots (7,530 of 37,654).
Tercile edges: **−143.06 m** and **+38.59 m** (detrended elevation, footprint terciles).
Insertion rule (identical in all three arms): `det_elev_slope` (Band 19) ≥ its footprint
80th percentile (14.10), `d(catalogue) > 3.0 px`, nearest-neighbour ≥ 2.8284 px, ranked by
distance to the nearest retained dot.

---

## SLOT 1 — `h33-h33-2-b2-RELIEFbasin10-20261023-d1a3b00d`

- **File (NaN outside, competition format):** `releases/h33-h33-2-b2-RELIEFbasin10-20261023-d1a3b00d.tif`
  · `sha256 d1a3b00d06607c366827d2f7dbb4be7dfa892237dd352e635a48514230662421` · 355,560 B
- **Fallback (0.0 outside, identical inside):** `…-zeros.tif`
  · `sha256 6507187903ea51b473126e86c2153c0ec09621090eee69fab4f565b6042709bc` · 219,359 B
- **Submission name:** `h33-h33-2-b2-RELIEFbasin10-20261023-d1a3b00d`
- **Form note (94/140):** `h33-2-b2; RELIEF pied->basin 10% onto p80 sharp ground; 20.0% chg, 0 on cat; pred +0.008 MODEL`
- **Diff:** −3,765 dots from the piedmont tercile, +3,765 in the basin tercile; allocation
  basin 7,696 → 11,461 · piedmont 15,744 → 11,979 · range-front 14,214 (unchanged).
  Added dots: min `d_cat` 3.162 px, min NN 4.12 px, mean NN 9.46 px.
- **PROXY (off-catalogue SGMC, never a score):** DTI 0.0961… → Δ **+0.00850**; decomposed as
  removal −0.00551 + insertion +0.01401. Catalogue control Δ −0.00024 (known faults preserved).
- **MODEL:** +0.008, credible range [−0.004, +0.016]. Tercile contrast vs the control arm: **+0.00029**.

## SLOT 2 — `h33-h33-2-b2-RELIEFpied10-20261023-b0285b17` (reshuffle CONTROL)

- **File (NaN outside):** `releases/h33-h33-2-b2-RELIEFpied10-20261023-b0285b17.tif`
  · `sha256 b0285b1798db9ccb0588b3ecfe382a068d50d609abae938849dbdb7c42282a3a` · 356,922 B
- **Fallback:** `…-zeros.tif` · `sha256 22da4a5c544a5b81d74f155021d894fd46171e46d1eaeefed355f96c614e4401` · 220,459 B
- **Submission name:** `h33-h33-2-b2-RELIEFpied10-20261023-b0285b17`
- **Form note (105/140):** `h33-2-b2; RELIEF pied->pied reshuffle control (terciles unchanged) 20.0% chg, 0 on cat; pred +0.008 MODEL`
- **Diff:** −3,765 piedmont dots, +3,765 piedmont dots; allocation **unchanged**
  (7,696 / 15,744 / 14,214). Added dots: min `d_cat` 3.162 px, min NN 13.93 px, mean NN 19.14 px.
- **PROXY:** Δ **+0.00821** = removal −0.00551 + insertion +0.01372. Catalogue control Δ −0.00024.
- **MODEL:** +0.008, [−0.004, +0.016]. This arm carries **no tercile signal by construction** — it
  measures the remove/insert rule itself. It is both the control and a legitimate contender.

## SLOT 3 — `h33-h33-2-b2-RELIEFrf10-20261023-7d62b548`

- **File (NaN outside):** `releases/h33-h33-2-b2-RELIEFrf10-20261023-7d62b548.tif`
  · `sha256 7d62b54885ec1f7405ab0683a615f1edca23a3ffbaefb74daf658b3917bbbb3c` · 353,175 B
- **Fallback:** `…-zeros.tif` · `sha256 d645fe705a033b6f214b8ea9d9c8309d5be37619920359234670271d59c2a255` · 216,836 B
- **Submission name:** `h33-h33-2-b2-RELIEFrf10-20261023-7d62b548`
- **Form note (99/140):** `h33-2-b2; RELIEF pied->rangefront 10% onto p80 sharp ground; 20.0% chg, 0 on cat; pred +0.007 MODEL`
- **Diff:** −3,765 piedmont dots, +3,765 range-front dots; allocation
  basin 7,696 · piedmont 15,744 → 11,979 · range-front 14,214 → 17,979.
  Added dots: min `d_cat` 3.162 px, min NN 30.48 px, mean NN 38.51 px.
- **PROXY:** Δ **+0.00668** = removal −0.00551 + insertion +0.01219. Catalogue control Δ −0.00024.
- **MODEL:** +0.007, [−0.005, +0.015]. Tercile contrast vs control: **−0.00153**.

---

## Format receipt (run on every arm, both encodings, re-read from disk)

| gate | value |
|---|---|
| CRS / shape / transform | `EPSG:32611` · 3730 × 3292 · `(100, 0, 243350, 0, -100, 4508550)` |
| dtype / band count | `float32` / 1 |
| values inside footprint | `[0, 1]`, 0 NaN inside |
| outside footprint | NaN (primary) / `0.0` (fallback) |
| dots | 37,654 in every arm |
| mass on catalogue | **0** |
| min `d_cat` of added dots | 3.1623 px (> 3.0) |
| inherited dots in the 2–3 px band | 2,095 in every arm (R0 geometry preserved — IR-89-03) |
| duplicate `sha256` | none, against all 23 ledger rows |
| validator | `python3 scripts/validate_release.py`, `pytest` (18 tests) |

Upload **one** file per slot: the NaN-outside file is the competition format; the `-zeros` twin is
byte-distinct with identical values inside the footprint and exists only so a portal that rejects
NaN outside still accepts an upload.

## Rebuild

```bash
python3 scripts/restore_inputs.py          # 10 pinned inputs, sha256-verified via api.github.com
python3 scripts/rebuild_r0.py              # must print ok:true and both byte-exact hashes
python3 scripts/relief_analysis.py         # tercile edges, pools, canary
python3 scripts/build_relief_variants.py   # writes releases/*.tif + receipts
python3 scripts/relief_report.py           # removal/addition decomposition
python3 scripts/validate_release.py        # fail-closed gate over every receipt
```

## What the human must supply

1. `receipt_score` + `receipt_date` in `ledger/submissions.csv` for each uploaded file.
2. `TOP_PUBLIC` (value + date) from the leaderboard — the only valid target number.
3. Slots used / left this rolling week.
4. Confirmation of the 2026-12-03 deadline and the Phase-1/Phase-2 split on the competition page
   (this agent cannot read it).
