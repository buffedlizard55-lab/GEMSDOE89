# SLOT PLAN — GEMSDOE89 SPACING continuation (2026-10-23)

One entity: 3 scored submissions per rolling week + one final blind file.
Slots used/available: **not supplied**. Deadline **2026-12-03** is **UNVERIFIED**.
R0 = 0.2778 **CLAIM**. A live change inside ±0.010 is no evidence; predictions
below are **MODEL**, not scores. SPACING is the lowest-priority axis, so do not
displace an already validated higher-priority arm queued for the same slot.

## Next three slots, in order

| # | File | Predicted Δ | Submit only if | Decision from receipt |
|---|---|---:|---|---|
| **1** | `releases/h33-h33-2-b2-spacing-poisson10-20261023-986e9365.tif` | **+0.002** (−0.008…+0.012) | A slot is available and no higher-priority validated arm is queued | ≥ +0.010: generic de-overlap earns credit; run slot 2. Inside ±0.010: no evidence, slot 2 may still test the distinct strike mechanism. ≤ −0.010: stop SPACING; hold slots 2–3. |
| **2** | `releases/h33-h33-2-b2-spacing-strike10-20261023-442188a4.tif` | **+0.003** (−0.010…+0.016) | Slot 1 did not fall by >0.010 | strike−Poisson ≥ +0.010: local line continuity adds value. Both similarly positive: generic spacing, not strike. strike ≤ Poisson −0.010: close the PCA-strike mechanism. |
| **3** | `releases/h33-h33-2-b2-spacing-lattice10-20261023-9d7dc126.tif` | **+0.001** (−0.008…+0.010) | Slot 1 or 2 improved by ≥0.010 | Positive too: regular geometry suffices. Null while another arm is positive: matched anchors/orientation matter. If no earlier arm improves, **hold this slot for DEDUPE**. |

Do not submit the NaN and zeros twins separately: they are one experiment.
Upload the NaN-outside file; the zeros twin is only a fallback.

## Weeks to the deadline

| week | dates | plan |
|---|---|---|
| 1 | 10-23 → 10-29 | slot 1 if its condition is met; obtain receipts for any already submitted RELIEF/upstream arms before interpreting deltas |
| 2 | 10-30 → 11-05 | conditional slots 2–3; otherwise preserve slots and build DEDUPE as a new registered axis |
| 3–4 | 11-06 → 11-19 | combine only the two axes with >=0.010 receipt evidence, one factor at a time; no combination from PROXY alone |
| 5 | 11-20 → 11-26 | confirm the winner against its named parent; freeze one final file and one fallback |
| 6 | 11-27 → 12-03 | re-validate both final files from disk; make the single blind final choice |

## Proposed better axes — not built this session

**DEDUPE (highest expected value).** Remove 15–25% of dots with the lowest
*unique* exact marginal credit; do not refill. **Mechanism:** a neighbour's
kernel already claims the truth credit, while the duplicate still costs mass.
**Confounder:** it also de-clusters, so compare against matched random/SPACING
removal. **Falsifier:** if it does not beat the existing `MASS −10%` arm by
>=0.005 on receipts, unique-credit ranking is not the right cost model.

**FLOOR (coverage arm).** Add about 2,000 structured dots to the flat-slope
tercile, which the merged RELIEF session found had only 177 R0 dots.
**Mechanism:** cover fault traces without DEM scarps instead of concentrating
entirely on relief. **Confounder:** flat-ground placement depends on a non-DEM
signal that R0 may already have rejected; this is also a MASS change unless
count-compensated. **Falsifier:** a receipt <= R0 −0.005 closes flat-ground
expansion from the supplied bands.
