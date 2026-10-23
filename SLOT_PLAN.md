# SLOT PLAN — session GEMSDOE89 (2026-10-23), axis MASS

Deadline **2026-12-03** (UNVERIFIED — confirm on the competition page; ≈6 weeks,
41 days). Quota: 3 scored submissions per rolling week per entity, plus one
final blind submission. Slots used/available: **not supplied**. No file in this
repo has a receipt; the parent's 0.2778 is still a **CLAIM**.

## What changed this session

R0's **dot set is now reproducible**: `solo-d2.8` (40,199) and `d2.8` (44,090),
each minus every dot within 2.0 px of the catalogue, both reproduce the parent
**cell-for-cell** (0 differing cells, two independent ancestors). The parent's
*file bytes* still cannot be re-encoded (the original writer settings are lost),
so the parent is referenced by sha256 `c55bafc4…`.

The MASS family's ceiling is arithmetic, not opinion: at `D ≈ 1.5–2×10^4`
(a value pinned by the one measured mass step), dropping 10 % of the dots can
gain at most **+0.0105**, and 20 % at most **+0.021**, even if every dropped dot
carries zero credit. Nothing in this family can plausibly reach +0.03.

## The three slots, in order

| # | file | predicted (MODEL) | submit only if | what the result changes |
|---|---|---|---|---|
| **1** | `releases/h33-h33-2-b2-MASSm10uniq-20261023-beed130f.tif` | **+0.002** (band −0.010…+0.010; ceiling +0.0105) | gates green (verified) | The primary read. ≥ +0.005 → mass outside the collar is waste, spend slot 2 on the dose. \|Δ\| < 0.005 → the count is not a lever; close MASS and do **not** build DEDUPE/FLOOR. ≤ −0.005 → the far field is credit-bearing; from now on only collar mass may be removed. |
| **2** | `releases/h33-h33-2-b2-MASSm20uniq-20261023-87ec6213.tif` | **+0.004** (band −0.020…+0.021; ceiling +0.021) | slot 1 scored and ≥ +0.005 | Dose-response. `m20 − m10 ≈ m10` → count is the lever, push the dose below 30k next. Super-linear loss → the optimum is between 33.9k and 37.6k and the next rung is 5 %, not 30 %. |
| **3** | `releases/h33-h33-2-b2-MASSm10rand-20261023-7a4c49b6.tif` — **or hold** | **−0.002** (band −0.016…+0.010) | slot 1 is within ±0.005 of zero and the human wants to know whether the *ranking* or the *count* carried whatever happened | The control. `m10rand ≈ m10uniq` retires the unique-credit ranking for good; `m10rand > m10uniq` inverts it. If slot 1 is clearly positive, **hold this slot** — it buys a decision here, not a score. |

Report-only, never a gate: the catalogue hide-and-recover proxy gives 0.0370 /
0.0340 / 0.0346 against the parent's 0.0384 (random null 0.0000); the
catalogue-surrogate DTI moves by −0.0002 / −0.0006 / −0.0004. Neither may be
used to overrule the live read.

## Alternates already built (unchanged by this session)

The three RELIEF arms (`…-relief-r10/r15/r15s-…`, see `docs/SUBMIT.md`) remain
built and unscored. They are the fallback if the human would rather test class
allocation than mass. Do not spend two slots in one week on the same question.

## Weeks to the deadline

| week | dates | plan |
|---|---|---|
| 1 | 10-23 → 10-29 | slot 1. Spend slot 2 only if slot 1 lands ≥ +0.005. |
| 2 | 10-30 → 11-05 | the dose (slot 2) or the control (slot 3) — not both — plus one receipt-backed re-read. |
| 3-4 | 11-06 → 11-19 | combine the only two operators with *measured* support: the collar (prune ≤2 px, +0.007 live) and whichever of mass/relief reads positive. One factor at a time, from a receipt-backed parent. |
| 5 | 11-20 → 11-26 | confirm the winner against its own parent; freeze the final file and a fallback. |
| 6 | 11-27 → 12-03 | re-validate both final files from disk, then submit one blind. |

## Proposed better axes (mechanism · confounder · falsifier) — not built

**1. FLOOR-BY-MASS (highest expected value; needs a new pair).** The flat-slope
tercile holds 33 % of the footprint and 20 % of the catalogue but 0.1 dots per
1000 px of R0's mass. Adding ~2,000 dots there at catalogued-fault spacing tests
whether the parent's coverage gap is a modelling failure or a correct
abstention. *Confounder:* flat ground has no DEM edge response, so any dot there
is a bet on a non-DEM signal. *Falsifier:* a 2,000-dot arm scoring below R0
− 0.005 says the gap is correctly empty, and retires every coverage-gap idea.
Note it is the **complement** of this session's arms: they remove mass, this adds
it, and the two together bound where mass should sit.

**2. DIP_ASYMMETRY (PRUNE, new pair).** Offset the catalogue collar one-sided by
local dip direction instead of symmetrically: if new traces are hanging-wall
scarps, the collar is wasted on the footwall. *Confounder:* antithetic faults and
the catalogue's own mapping bias. *Falsifier:* no improvement over the symmetric
`dcat≥3px-refill` arm, which is already built.

**3. DOSE (cheap sanity, any week).** Re-submit a byte-identical twin of a scored
file once. Upstream shows ≥8 slots went to exact repeats *by accident*; a
deliberate repeat is the only way to measure the score's run-to-run noise, which
is the real bar for "under 0.01 is no evidence".
