# Why `h33-h33-2-b2` scored 0.2778 — and what beating it requires

Evidence labels used everywhere in this repo: `ORGANIZER-CONFIRMED`
(registration-page receipt, none exist in this ledger), `CLAIM`
(owner-recorded live score, e.g. 0.2778), `HOLDOUT-DTI` (local segment
holdout with evaluator version + withheld n + CI), `MODEL` (scenario
arithmetic, never a score). Fleet scores below are `CLAIM` from
`ledger/submissions.csv` / the owner's site list; the prompt's two
leaderboard figures (0.4413 and 0.3195) conflict and are both treated as
**UNVERIFIED** until a human reads them off the leaderboard with a date
(`IRREGULARITIES.md` item 17).

## The lineage is the explanation (all steps byte-verified in this repo)

| step | file | mass | CLAIM |
|---|---|---|---|
| corroborated multi-layer ridge (continuous) | `h19-5` | 121,131 px | 0.1922 |
| dot-thin, r = 2.8 px suppression | `d28` | 44,090 dots | 0.2600 |
| prune dots within 2.0 px of catalogue | **`h33-h33-2-b2` (R0)** | **37,654 dots** | **0.2778** |

`tools/rebuild_r0.py` reproduces both R0 twins bit-for-bit
(zeros `c55bafc4…`, NaN `baeae321…`), so this decomposition is measured,
not folklore. Three effects, in order of the jumps:

1. **Centreline habitat (0 → 0.19).** The h19-5 ridge requires several
   independent geophysical/topographic layers to agree, which traces
   real fault-related basement structure far better than any single
   channel — the best single-source fleet entries (LiDAR scarps alone
   0.038–0.146, Euler alone 0.036–0.098, ML on catalogue labels
   0.02–0.16) confirm that corroboration, not any one transform, carries
   the recall.
2. **Dotted emission matched to the metric (0.19 → 0.26).** The DTI
   metric (`gemsdoe/metric.py`: `T / (0.2T + 0.2(S−M) + 0.8|G|)`, 300 m
   triangular kernel, `max` credit) pays once per truth pixel no matter
   how many prediction pixels cover it, but charges 0.2 per unit mass.
   A continuous 3-px-wide ridge spends ~3× the mass of a 2.8-px-spaced
   dot chain for the same `T`. Thinning to r ≈ kernel radius tiles the
   same centrelines at minimum mass. This is also why graded
   probability surfaces and heavy ML ensembles underperform: fractional
   mass spread over area is charged by the pixel and credited by the
   `max`.
3. **Catalogue-collar prune (0.26 → 0.2778).** Known faults are masked
   pixel-exactly in scoring, so a dot on or beside the catalogue earns
   (almost) nothing and still costs mass. Deleting the 6,436 dots
   within 2 px of the catalogue — 15% of the mass for ~0 credit — is a
   free denominator reduction. The per-dot break-even makes this
   precise: a unit dot raises DTI iff its kernel credit exceeds
   `0.2 × DTI ≈ 0.056` at R0's level, i.e. iff some true fault pixel
   lies within ≈2.83 px (283 m).

Why catalogue-trained ML fails here (fleet: 0.02–0.16) is the same story
with the sign flipped: the training labels *are* the masked catalogue,
so supervised models learn to redraw known, surface-mapped faults —
exactly the pixels that earn nothing — and to avoid the buried-basin
habitat where the scored (unmapped) faults live.

## Can a submission beat 0.2778?

Yes in principle — the verified gap to the (UNVERIFIED) public top
implies somebody's centrelines recover substantially more blind-fault
length at comparable mass. At R0's operating point the only ways up are
(i) more true centreline within 283 m of a dot (better/new physical
channels, better centreline accuracy), or (ii) less wasted mass
(redundancy removal, collar hygiene) — (ii) is nearly exhausted by R0's
own construction, which is why this repo's 28 built single-axis
perturbations all predict only `MODEL` deltas of ±0.01–0.03.

The honest constraint is *validation*: the only local truth available
is the catalogue itself, and a whole-segment holdout on it
(`gemsdoe/holdout.py`, this session) measures recovery of *mapped*
faults — the population R0 already matches. This session's BSTP lane
(new basin lineaments; `ledger/MECHANISM_CARDS_BSTP.md`) lost that
holdout three times (−0.022…−0.027, CIs excluding 0), which falsifies
"basin dots also trace mapped faults" but cannot falsify "basin dots
trace *blind* faults". Under the parallel-run protocol that is a
**negative verdict: no slot**. Beating 0.2778 with evidence, rather
than hope, requires either a lane that wins the segment holdout
(catalogue-habitat improvements: centreline accuracy, spacing,
redundancy) or a deliberate human decision to spend a slot as the
experiment itself, read against a matched control (the `SLOT_PLAN.md`
pair discipline). No file in this repo — including this session's —
carries a guarantee, and any site that implies one is hallucinating.
