# Mechanism card — TRACKB axis, session GEMSDOE89 (2026-10-24)

Parent: **R0 = h33-h33-2-b2** (37,654 unit-mass dots). Live 0.2778 = **CLAIM**;
this repo holds no receipt. Axis chosen by the agent (brief §1, human
directed no prompt): **TRACKB**, because a full-ledger scan showed every
weekly axis already built at this parent — MASS, CONCENTRATION (3 families),
SNAP, RELIEF, SPACING in GEMSDOE89, and PRUNE at 1 / 1.5 / 2.5 / 3 / 4 px in
upstream GEMSDOE84 (IRREGULARITIES item 14). TRACKB had zero rows anywhere.

## Card — `top12` — `h33-h33-2-b2-TRACKBtop12-20261024-fb156257`

- **Hypothesis.** The subset of R0 dots that (a) claim the most triangular-
  kernel credit on the corroborated h19_5 ridge (strand credit) and (b) form
  long, strike-consistent chains are the dots most likely to sit on real,
  mappable fault strands — and are therefore the right objects to hand a
  structural geologist for Phase-2 expert label expansion.
- **Mechanism.** Faults are line-like: a real strand produces a chain of
  ridge dots with a stable strike over kilometres, whereas noise, contacts
  and cultural linears break, bend or scatter. The build ranks dots by
  strand credit (kernel credit claimed on h19_5 pixels as nearest dot;
  flat-prior unique credit was measured to fragment strands — largest
  linked component 9 dots vs 170 — and was rejected), links the top two-
  thirds at 4.5 px, orders components by graph-geodesic arc length, and
  keeps traces with length ≥ 1 km, ≥ 8 dots, segment-azimuth consistency
  R ≥ 0.85 and straightness ≥ 0.60. 19 traces qualified; the top 12 by
  total member strand credit (41.3 km, 145 member dots) are delivered as
  GeoJSON (EPSG:32611) + member-dot raster, one evidence paragraph each in
  `ledger/TRACKB_TRACES.md`.
- **Non-fault mimic.** A lithologic contact, dike, road, fence or GeoDAWN
  survey-line artefact can produce a straight potential-field ridge with
  stable strike and no surface rupture. Straightness alone cannot exclude
  it; that is exactly what the per-trace falsifier hands to the reviewer.
- **Predicted sign and size.** No live-score prediction: this is a Phase-2
  review product, not a weekly-slot candidate. The companion raster keeps
  only 145 of 37,654 dots and would score far below R0 if submitted as-is
  (MODEL, by construction — do not submit it). The Phase-2 value is
  conditional: if experts confirm even a few traces as new faults, those
  strands enter the expanded label set on ground the parent already
  covers only as scattered dots.
- **Falsifier.** Expert review or field evidence placing any delivered
  trace on a non-fault mimic, or showing a mapped fault departing from the
  stated strike by > ~25° along its corridor, removes that trace; if the
  majority of the 12 fall this way, the strand-credit + straightness
  selection rule itself is falsified and TRACKB should not be extended
  (e.g. to the remaining 7 qualifying traces) in later sessions.

## Proposed follow-on (not built this session)

**TRACKB-EXTEND**: deliver the remaining 7 qualifying traces plus traces
from the next credit tier only if expert feedback on the top 12 is
positive. Confounder: reviewer attention is scarce, so trace ordering by
credit sum (which favours long traces) may bury short but real strands.
Falsifier: confirmation rate of traces 13–19 no better than a length-
matched random set of R0 strands.
