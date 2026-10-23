# IRREGULARITIES — only items that change a decision

## IR-89-01 — R0 byte-exactness needs the parent's entropy coder (libdeflate), not just its recipe

**Found:** the recorded recipe reproduces all 12,279,160 cells of R0 and every intermediate stage
pixel-for-pixel, but the written file did **not** match the published SHA-256:

| writer | zeros size | zeros sha256 |
|---|---|---|
| rasterio 1.3.10 / GDAL 3.8.4 (zlib, raw deflate) | 204,802 B | `c6186b07…` |
| rasterio 1.4.3 / GDAL 3.9.3 (identical output) | 204,802 B | `c6186b07…` |
| published parent | 219,065 B | `c55bafc4…` |

**Cause (diagnosed, not guessed):** the parent's tile streams are **zlib-wrapped libdeflate**
(`78 da …`); the wheel builds emit raw zlib deflate. Recompressing the parent's own
predictor-encoded payloads with `imagecodecs.deflate_encode` (libdeflate) at **level 10** reproduces
195/195 tiles byte-for-byte; levels 1–9 and 11–12 reproduce 0–96 tiles. Google's summary of the
stream, not of the pixels.

**Decision:** `scripts/canonical_writer.py` lets GDAL lay out the container and apply Predictor=3,
then recompresses each tile with libdeflate level 10. Result: `c55bafc4…` and `baeae321…` both
reproduce exactly, so the parent gate passes **without approximating anything**.
**Carry-forward:** every receipt records `encoder: {container, deflate, level}`. Any future session
that claims a byte-exact rebuild must state its encoder, or its "exact" claim is untestable.

## IR-89-02 — the owner's public repos contain competition rasters (data-use unchecked)

`buffedlizard55-lab/GEMSDOE`, `/GEMSDOE24`, `/GEMSDOE32` and `/GEMSDOE88` publish mirrors of
login-walled DrivenData #306 files and derived submissions as tracked Git blobs (e.g.
`GEMSDOE/data/bridge/example_submission.tif`, 1,599,597 B). Redistribution terms are unchecked.
**Decision:** GEMSDOE89 reads those pins but tracks **no** raster (`data/`, `releases/*.tif`
gitignored); only hashes, receipts and scripts are committed. The pre-existing exposure is the
owner's to resolve before Phase 2 — this repository neither adds to it nor can remove it.

## IR-89-03 — Brief §4.4 ("keep ≥ 3 px") conflicts with §5 ("differ ONLY on your AXIS")

R0 itself carries **2,171 dots at 2 < d_cat ≤ 3 px`. A non-PRUNE variant that inherits R0 must
therefore either break the 3 px collar or break "differ only on the axis". The two rules cannot
both hold for any RELIEF variant.
**Decision:** the axis wins — inherited parent geometry is preserved untouched, and **every dot the
variant adds or moves is at `d_cat > 3.0`** (min 3.1623 px in all three arms). Each arm still
carries 2,095 inherited dots in the 2–3 px band. Under a literal reading these three files are not
collar-clean; the PRUNE lane (`…PRUNEp3px…`, `…PRUNEp4px…`) is the only collar-clean family in the
ledger, and a RELIEF-on-`PRUNEp3px` re-base is the clean follow-up if the human wants both.
**Why it matters:** if the human reads §4.4 as absolute, **slots 1–3 must not be uploaded** and
the RELIEF arm should be re-based on `PRUNEp3px` first.

## IR-89-04 — this session started from an empty repository; inputs and ledger were reconstructed

`buffedlizard55-lab/GEMSDOE89` at commit `9bf120b` contained one 11-byte README. There was no
`ledger/`, no `SLOT_PLAN.md`, no `raw_paste.txt`, no manifest, no parent raster.
**Decision:** rebuild the working set from the owner's own sibling repositories at frozen commit
refs (`GEMSDOE24 @07345ea0`, `GEMSDOE32 @078f3cea`, `GEMSDOE28 @d618b648`, `GEMSDOE @c0c06ac8`,
`GEMSDOE88` read-only for its ledger and recipes), each pinned by SHA-256 in
`registry/data_manifest.json`; inherit the 20 prior ledger rows with `provenance` recorded. No
competition page, leaderboard or submission service was read. All 10 pins verified byte-exactly.

## IR-89-05 — "AXIS is assigned by the human" vs "pick your own session"

Brief §1 says the human assigns the axis and §5 says to log the conflict; the same message says
"Do not prompt me over choosing an Axis for the session, pick your own session".
**Decision:** the instruction wins. `AXIS = RELIEF` — the only axis in the brief's week-1 list with
zero rows in the combined ledger (MASS 3, PRUNE 4, CONCENTRATION 4, SNAP 9, RELIEF 0).

## IR-89-06 — deadline and Phase split cannot be verified here

Brief §1 asks to confirm the 2026-12-03 deadline and the Phase-1/Phase-2 split on the competition
page; Brief §4.1 bans fetching `drivendata.org` (terms forbid automated access).
**Decision:** `2026-12-03` is carried as **UNVERIFIED** in `SLOT_PLAN.md` and `README.md`. The human
must confirm it. No scheduling decision in this repo depends on any other unverified date.
