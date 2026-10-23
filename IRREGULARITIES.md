# Decision-changing irregularities

## 2026-10-23 — STOP: exact-parent prerequisites absent

Inspected tracked files and the workspace at base commit
`9bf120b9cc25bdab5078dfdd66c36c605ef6bf84`. The only project file was
`README.md` (`# GEMSDOE89`). Missing:

- `registry/data_manifest.json` or an equivalent pinned-input registry;
- R0 (`h33-h33-2-b2`, GEMSDOE32), its full expected SHA-256, reproducible recipe,
  ranking, and source inputs;
- `sample_submission.tif`, footprint definition, and catalogue mask;
- `ledger/submissions.csv` and `ledger/raw_paste.txt`;
- `SLOT_PLAN.md` and a README CURRENT STATE block.

Decision: input hashes cannot be verified, R0 cannot be rebuilt or matched,
and prior (parent, axis, value) experiments cannot be checked. Stop before
candidate construction. No parent approximation, raster, validation result,
ledger row, score receipt, or submission has been created. R0's reported
0.2778 remains CLAIM from the human brief, not RECEIPT.

The repository is public (GitHub metadata checked 2026-10-23):
https://github.com/buffedlizard55-lab/GEMSDOE89 . No competition rasters were
found in this checkout or its tracked HEAD. Supply inputs through private
workspace storage, not this public repository or a release; data-use terms
are unchecked. This inspection does not establish what other repositories
or historical objects contain.

The deadline 2026-12-03 is human-provided and UNVERIFIED here. Automated
DrivenData access is prohibited by the brief; the human must confirm it on
https://www.drivendata.org/competitions/306/competition-doe-gems/ .
TOP_PUBLIC, receipt evidence, weekly usage, and total remaining slots are
unknown. Do not allocate a scored submission until the human supplies them.

README was left unchanged: it has no CURRENT STATE block, and the brief
permits editing only that block. There is no configured CI workflow in this
checkout. Leave the documentation PR open unless CI is green; absence of
checks is not a green result.
