# How to submit a file from this repository

The agent never touches the submission portal, never reads credentials, and
never contacts `drivendata.org`. Upload is performed manually by the human
competitor.

## 1. Before you upload anything

1. Read the current top public leaderboard score and write it down with today's
   date (`TOP_PUBLIC = ____ on YYYY-MM-DD`). Check how many of your 3 weekly
   scored slots remain (`https://docs.nlr.gov/docs/fy26osti/96647.pdf`).
2. Verify the local release files match the hashes in `ledger/submissions.csv`:
   ```bash
   python tools/validate_raster.py
   python tools/check_ledger.py
   ```
   Every gate must print `PASS` (`all gates pass: True`) and `ledger consistent`.

## 2. Which file to upload (`SPACING` axis — primary session)

Upload the **NaN-outside** file first (matches `sample_submission.tif` pixel-for-pixel
in its outside-footprint mask). Only use `-zeros.tif` if the portal's pre-scorer
rejects NaN outside the footprint — and record which twin was uploaded.

### Slot 1 — Primary (`SPACING = strike`)

* **Primary file (NaN outside):** `releases/h33-h33-2-b2-spacing-strike-20261023-37910355.tif`
  * `sha256`: `37910355789dc5a0489aaadf739260d0e0fe057170084ef978d34236ae3c768f`
  * Dots: `37,654` (`5,444` moved = `14.46 %` of R0; symmetric diff `28.92 %`)
* **Fallback twin (zeros outside):** `releases/h33-h33-2-b2-spacing-strike-20261023-37910355-zeros.tif`
  * `sha256`: `943199db7410b6c8f45d154f6380257f2dc86f1e5641f5bf26fbd0812b46a1cb`
* **Paste-ready form note (115 chars, ≤140 limit):**
  ```text
  h33-h33-2-b2; SPACING strike (5444/37654=14.46% along-strike on H19 crest, dcat>=3px); pred +0.006 (-0.004..+0.011)
  ```

### Slot 2A — Conditional anisotropy control (`SPACING = poisson`, ONLY if Slot 1 ≥ +0.010 vs R0)

* **Primary file (NaN outside):** `releases/h33-h33-2-b2-spacing-poisson-20261023-95c51e18.tif`
  * `sha256`: `95c51e182563dba79eec1e8b306fa9b673955c6615a687cdc0f8f35af4cd3b15`
  * Dots: `37,654` (`4,800` moved = `12.75 %` of R0; symmetric diff `25.50 %`)
* **Fallback twin (zeros outside):** `releases/h33-h33-2-b2-spacing-poisson-20261023-95c51e18-zeros.tif`
  * `sha256`: `dc82177c1fa9c962464e78c5efa2a416a91c998a7a2e54feef168efefa77ca6e`
* **Paste-ready form note (113 chars, ≤140 limit):**
  ```text
  h33-h33-2-b2; SPACING poisson (4800/37654=12.75% Voronoi/Poisson on H19, dcat>=3px); pred +0.001 (-0.002..+0.004)
  ```

### Hold control (`SPACING = lattice` — do not spend a weekly slot unless both `strike` and `poisson` move ≥ +0.010)

* **Primary file (NaN outside):** `releases/h33-h33-2-b2-spacing-lattice-20261023-dd652665.tif`
  * `sha256`: `dd65266597fc85480445a2bcbea3dd1a3cc6ba00c7d14b3333b0501657eacb93`
* **Fallback twin (zeros outside):** `releases/h33-h33-2-b2-spacing-lattice-20261023-dd652665-zeros.tif`
  * `sha256`: `5fe27a0e479d4c92eb7e6e85e33f31729635a00bed6999488dde226717df2025`
* **Paste-ready form note (116 chars, ≤140 limit):**
  ```text
  h33-h33-2-b2; SPACING lattice (5195/37654=13.80% hex-lattice a=3.2px on H19, dcat>=3px); pred 0.000 (-0.003..+0.003)
  ```

*(Also retained in `releases/` and `ledger/submissions.csv`: `MASSm10uniq` `beed130f` — Slot 2B if Slot 1 is inside ±0.010 — plus `MASSm20uniq` `87ec6213`, `MASSm10rand` `7a4c49b6`, and `RELIEF` `r10` `366c87ca`, `r15` `6aa774ce`, `r15s` `5f0ae851`.)*

## 3. After the portal scores the file

1. Save a screenshot or copy of the submission confirmation showing the timestamp
   and the 4-decimal score.
2. Open `ledger/submissions.csv`, find the row by `sha8`, and fill in:
   * `score`: the 4-decimal portal number
   * `evidence_class`: `RECEIPT`
   * `status`: `SCORED`
   * `receipt`: `Y`
   * `receipt_score`: same 4-decimal number
   * `receipt_date`: UTC date (`YYYY-MM-DD`) from the portal receipt
3. Re-run `python tools/check_ledger.py` and commit the updated ledger row.
4. Apply the decision rule in `SLOT_PLAN.md`:
   * Any delta inside `[-0.010, +0.010]` relative to R0 (`0.2778` CLAIM) is **no
     evidence** on a 4-decimal public subset — do **not** adopt the child as a
     new parent and do **not** run its higher-dose/control follow-up.
   * Only if Slot 1 (`spacing-strike`) reaches `≥ 0.2878` (`+0.010` over R0) run
     Slot 2A (`spacing-poisson`). If Slot 1 lands inside `±0.010`, pivot Slot 2
     to `MASSm10uniq` (`beed130f`).
