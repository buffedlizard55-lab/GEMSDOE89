# MECHANISM CARD — BSTP lane (GEMSDOE89, 2026-10-24)

Machine record: `registry/run_card_bstp40.json` (protocol item 5). Code:
`gemsdoe/bstep.py`, `gemsdoe/holdout.py`, `tools/build_bstep.py`,
`tests/test_bstep.py`. Reports: `registry/build_report_bstp40*.json`,
`registry/holdout_bstp40*.json`.

## The one method (lane)

At fixed mass `n = 37,654` from parent R0 `h33-h33-2-b2`: retain the top
60% of R0 dots by the label-free unique-credit ranking
(`mass.unique_credit`), drop the rest, and refill with greedy
surface-ranked dots (2.8 px suppression, the lineage spacing) on

```
S = ( robust|grad b15 depth_to_base_surf|
    * robust|grad b17 cond_surf|
    * max(b03 tmi_hg, b18 iso_grav_anom_hg) )^(1/3)
```

with new dots constrained to footprint, `d_cat >= 3 px`, and
`d_parent > 3 px` (no new dot inside the 300 m scoring kernel of any
parent dot). All normalisation reuses `snap.py`; the parent rebuild
reuses `parent.py`; writing/gating reuse `grid.py`/`validate.py`.
No RNG anywhere; a re-run reproduced the NaN-twin sha256
`2e7e8a8f…` byte-identically.

## Why it should catch catalogue-missing faults

The scored truth is faults *absent* from the USGS/INGENIOUS catalogue
(known faults are masked pixel-exactly). A surface-mapped catalogue
systematically misses buried basin faults with no scarp. Those faults
still (1) step the depth-to-basement surface, (2) juxtapose basement
lithologies (magnetic/gravity HG edge), and (3) host conductive damage-
zone alteration and fluids — the geothermal conduit signature. Requiring
all three (geometric mean) targets that conjunction.

**Named mimics:** non-fault basement lithologic contacts, paleochannel /
playa-margin conductivity edges, volcanic flow margins.

## Three experiments (budget 3/3) — all HOLDOUT-DTI negative

Evaluator `segment-holdout-v1`: 911 whole catalogue segments (≥20 px,
39,310 px) withheld across 5 folds with a 10 px buffer; parent and
candidate rebuilt per fold from the visible catalogue only; visible
faults masked pixel-exactly; pooled DTI (α 0.2, β 0.8, R = 3 px);
segment-bootstrap 95% CI on the difference.

| exp | variant | HOLDOUT-DTI diff vs R0-fold [95% CI] |
|---|---|---|
| 1 | `bstp40` (`2e7e8a8f`, kept) | **−0.0254 [−0.0296, −0.0210]** (parent 0.0914, cand 0.0660) |
| 2 | `bstp40corr` (`e3b6d3d2`, corridor ≤15 px; TIFs withdrawn/deleted) | −0.0220 [−0.0262, −0.0178] |
| 3 | `bstp40corrE` (`598993b2`, edge-ranked retention; TIFs withdrawn/deleted) | −0.0269 [−0.0337, −0.0204] |

Leakage canary PASS (max single-feature AUC 0.5209 < 0.90). Uniqueness
PASS (surface ρ 0.29 vs edge-only; ≤3 px dot overlap 60.0% vs R0, worst
prior registry raster 62.4% — both inside protocol limits 0.90 / 70%).

## Read-out (falsifier, stated after the fact but binding)

The lane's pre-registered hope — that triple-corroborated basin
lineaments also trace withheld *mapped* segments well enough to break
even at 40% replacement — is falsified three times with CIs excluding
zero. The result does **not** falsify the live hypothesis (blind faults
are absent from holdout truth by construction; see
`IRREGULARITIES.md` item 17), but under the parallel-run protocol an
idea that has not beaten the holdout best does not get a weekly slot.

**Verdict: negative. Not promoted.** The format-validated zeros twin
exists for a deliberate human risk decision only; the evidence-based
queue stays in `SLOT_PLAN.md`.
