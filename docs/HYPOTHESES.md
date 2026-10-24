# Candidate geological hypotheses — ranked (2026-10-24)

Requirement: each names layer(s), physical signature/transform, why it
should catch a fault missing from the USGS/INGENIOUS catalogue, how it
differs from anything already implemented in this repo, expected DTI
leverage and implementation cost. Fleet cross-check against
`ledger/submissions.csv` (144 rows) done per item. Validation for all:
`gemsdoe/holdout.py` segment holdout + leakage canary + uniqueness
audits before any slot (protocol). Rank 1 was implemented and tested
this session; ranks 2–5 are unbuilt.

| # | Hypothesis (layers → transform) | Why catalogue-missing faults | Difference vs repo/fleet | Expected leverage | Cost |
|---|---|---|---|---|---|
| 1 | **BSTP** — b15 `depth_to_base_surf` + b17 `cond_surf` + b03/b18 HG → sober gradient magnitudes, geometric-mean corroboration, greedy 2.8 px dotted refill at fixed R0 mass | Buried basin normal faults step basement and host conductive alteration/fluids without any scarp to map | No prior row uses b15/b17 gradients as an emission surface; all 28 prior GEMSDOE89 files only move/prune R0 dots | HIGH if basin truth is enriched (break-even: new dot within 283 m of truth) | LOW (stack only) — **BUILT: HOLDOUT-DTI −0.0254 [−0.0296,−0.0210], verdict negative** |
| 2 | **Signed DEM scarp polarity** — b12 `det_elev` + b19 slope → signed cross-strike Laplacian, keep down-to-basin polarity only, dotted refill like BSTP | Low piedmont scarps get buried/planed and skipped by mappers, but keep a one-sided topographic step at 100 m | SNAP uses *unsigned* potential-field HG; polarity has never been an emission filter in this repo (proposed unbuilt in `SLOT_PLAN.md`) | MEDIUM (catalogue-habitat-adjacent, so holdout can actually validate it) | LOW |
| 3 | **Relay-bridge tip linking** — R0 strand geometry + BSTP surface → bridge co-linear/en-échelon strand tips ≤12 px, strike diff ≤20°, only where the bridge corridor is surface-corroborated | Breaching/relay faults between mapped segments are young, low-displacement and routinely unmapped | TRACKB extracted traces but never emitted bridge dots; fleet `tip-stepover` rows (0.2632 CLAIM) used a different parent/recipe, not fixed-mass R0 refill | MEDIUM | MEDIUM |
| 4 | **Geodetic strain localisation at full mass** — b04 2nd invariant + b07 shear rate + b08 dilatation → ridge of strain-rate magnitude, triple-corroborated with EDGE, dotted refill | Actively straining blind faults localise interseismic deformation before they break the surface | Fleet strain attempt scored 0.0000 with 440 dots (mass-starved); never tried at 37,654 fixed mass with corroboration | LOW–MEDIUM (smooth fields, poor centreline precision) | LOW |
| 5 | **1 m LiDAR micro-scarps fused at fixed mass** — USGS 3DEP 1 m DEMs (free official source: USGS National Map / 3DEP, https://www.usgs.gov/3d-elevation-program) → sub-2 m scarp detection (profile curvature), refill only where the 100 m stack is blind | Scarps <2 m high are invisible in the 100 m stack and under-mapped in alluviated piedmonts | Fleet LiDAR-only files scored 0.038–0.146 as standalone masses; never fused as a >3 px-off-parent fixed-mass refill. **Obtainability: free/official but NOT downloadable from this sandbox (host allowlist) — requires human supply, so it is not viable as an autonomous next step** | HIGH potential | HIGH |

**Ranking logic:** expected DTI improvement × probability the segment
holdout can certify it ÷ cost. Rank 1 was chosen because it is the only
candidate that is simultaneously new-support (protocol uniqueness),
stack-only (autonomous), and mechanistically aimed at the scored
population. Its holdout-negative result (see
`ledger/MECHANISM_CARDS_BSTP.md`) moves rank 2 — the only remaining
candidate whose truth population the holdout can actually see — to the
top of the *validatable* queue.
