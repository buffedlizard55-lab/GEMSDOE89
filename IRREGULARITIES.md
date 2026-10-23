# IRREGULARITIES — items that change a decision or carry legal/disqualification risk

Routine engineering checks live in `registry/*.json` (`parent_verification.json`,
`leakage_canary.json`, `report_only_status.json`, `format_receipts.json`). Only
findings that change a human decision or carry competition-rule risk are listed
here.

## 1. Competition data is hosted in public GitHub repositories under this account (ACTION REQUIRED)

During input verification (`registry/data_manifest.json`), the competition
feature stack (`gems-geodawn-numerical-features.tif`, 418.9 MB across five split
parts), `sample_submission.tif`, and `existing_faults.tif` (byte-identical to
`labels.tif`) were found committed inside **public** GitHub repositories under
`buffedlizard55-lab` (`GEMSDOE`, `GEMSDOE24`, `GEMSDOE28`, `GEMSDOE32`,
`GEMSDOE84`, `GEMSDOE86`, `GEMSDOE92`).

* **Why this matters:** Competition data terms normally prohibit public
  redistribution of organizer-supplied datasets during an active prize. Under
  the official GEMS Phase 1 rules (`https://docs.nlr.gov/docs/fy26osti/96647.pdf`),
  breaching competition data terms can carry disqualification risk.
* **What this repo (`GEMSDOE89`) did:** Zero competition data files are
  committed to `GEMSDOE89`. `.gitignore` blocks `data/`, and all verified inputs
  live outside Git (`./data/`).
* **Decision for the human:** Check the DrivenData #306 data redistribution
  rules immediately and make those upstream mirror repositories private (or
  remove the split competition rasters from their public history).

## 2. Parent R0 (`0.2778`) and all 115 upstream scores are `CLAIM`s, not `RECEIPT`s — though R0's raster bytes are now recipe-verified

`tools/rebuild_r0.py` verified **100 % byte-exact reconstruction** of R0
(`h33-h33-2-b2`, 37,654 dots) from its recorded upstream recipe
(`GEMSDOE28` `h27-4-r1-solo-d2-8` pruned by `distance_transform_edt(~catalogue) > 2`),
matching both `c55bafc4…` (`-zeros`) and `baeae321…` (`-nan`), and confirming
that 100 % of R0's dots sit on `scored_h19_5`.

However, **none** of the upstream scores (`0.2778` for R0, `0.2708` for
`h27-4-r1-solo-d2-8`, `0.2335` for `h19_5`, etc.) carries a verifiable portal
screenshot or submission receipt in this repository. Every upstream number is
labelled `CLAIM` in `ledger/submissions.csv`.

* **Decision impact:** Before interpreting Slot 1's live score against `0.2778`,
  the human should verify in their DrivenData account history that
  `h33-h33-2-b2` (`baeae321` / `c55bafc4`) actually scored `0.2778` under the
  same single competitor account.

## 3. Multi-site upstream history (`GEMSDOE` … `GEMSDOE88`) vs single-entity rule

The upstream ledger aggregates runs across dozens of numbered repositories. Under
the official GEMS Phase 1 rules (`https://docs.nlr.gov/docs/fy26osti/96647.pdf`),
one competitor/team is a **single entity** limited to **3 scored submissions per
rolling 7-day window** and **1 final submission**. Using multiple DrivenData
accounts to multiply weekly slots is disqualifying.

* **Decision impact:** All planning in `SLOT_PLAN.md` assumes strictly **one**
  competitor account and ≤3 scored uploads per rolling week.

## 4. `TOP_PUBLIC` and confirmation of the `2026-12-03` deadline are missing

Automated access to `drivendata.org` is prohibited by site terms and by the
session brief, so neither `TOP_PUBLIC` nor live confirmation of the `2026-12-03`
deadline could be fetched here. Both remain `UNVERIFIED` placeholders in
`README.md` and `SLOT_PLAN.md` until the human supplies them.
