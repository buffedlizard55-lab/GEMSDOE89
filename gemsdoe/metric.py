"""DTI algebra for the GEMS Prize (DrivenData #306).

Derived form (see brief sec.2), not copied from organizer code:

    DTI = T / ( 0.2*T + 0.2*(S - M) + 0.8*|G| )

    G  : binary ground-truth fault mask
    p  : prediction raster, values in [0, 1]
    T  : kernel credit claimed by truth  = sum_{g in G} max_i p_i * k(i, g)
    S  : total predicted mass           = sum_i p_i
    M  : mass already explained         = sum_i p_i * max_{g in G} k(i, g)
    k  : triangular kernel, radius R pixels, k(d) = max(0, 1 - d/R)

Consequences that this module makes testable (tests/test_metric.py):

  * perfect prediction (p == 1 on G, else 0)  ->  DTI = 1 exactly
  * empty prediction                          ->  DTI = 0
  * marginal gain of ONE added dot of credit k, holding the rest fixed:
        Delta DTI = (T + k)/(D + 0.2) - T/D, with D the old denominator
    which is positive exactly when  k > 0.2 * DTI.
    At DTI = 0.2778 that threshold is 0.0556 -- the brief's "about 0.056".
  * the same threshold, with the sign reversed, ranks dots for removal:
    a dot whose credit is below 0.2*DTI costs more mass than it earns.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi

KERNEL_RADIUS_PX = 3.0  # 300 m at 100 m pixels


def kernel_weight(distance_px, radius=KERNEL_RADIUS_PX):
    """Triangular kernel, continuous in distance (pixels)."""
    d = np.asarray(distance_px, dtype=np.float64)
    return np.clip(1.0 - d / radius, 0.0, 1.0)


def _truth_credit(truth, pred, radius):
    """T = sum over truth pixels of max over prediction pixels of p*k."""
    truth = np.asarray(truth) > 0
    if truth.sum() == 0:
        return 0.0
    # distance from every pixel to the nearest positive prediction pixel
    d = ndi.distance_transform_edt(pred <= 0)
    w = kernel_weight(d[truth], radius)
    return float(np.sum(w))


def _explained_mass(truth, pred, radius):
    """M = sum over prediction pixels of p * max over truth pixels of k."""
    truth = np.asarray(truth) > 0
    pos = pred > 0
    if not pos.any() or truth.sum() == 0:
        return 0.0
    d = ndi.distance_transform_edt(~truth)
    return float(np.sum(pred[pos] * kernel_weight(d[pos], radius)))


def dti(truth, pred, radius=KERNEL_RADIUS_PX):
    """Dispatch Type Index. truth/pred: 2-D arrays on the same grid."""
    truth = np.asarray(truth) > 0
    pred = np.asarray(pred, dtype=np.float64)
    g = float(truth.sum())
    s = float(pred.sum())
    t = _truth_credit(truth, pred, radius)
    m = _explained_mass(truth, pred, radius)
    denom = 0.2 * t + 0.2 * (s - m) + 0.8 * g
    if denom == 0:
        return 0.0
    return float(t / denom)


def marginal_gain_add(truth, pred, i, j, radius=KERNEL_RADIUS_PX):
    """Exact DTI change from adding one unit dot at (i, j). Negative = harmful.

    Computed from the metric definition, not from the 0.2*DTI shortcut; the
    shortcut is separately tested against this function.
    """
    base = dti(truth, pred, radius)
    trial = pred.copy()
    trial[i, j] = 1.0
    return dti(truth, trial, radius) - base


def marginal_gain_remove(truth, pred, i, j, radius=KERNEL_RADIUS_PX):
    """Exact DTI change from removing the dot at (i, j)."""
    if pred[i, j] <= 0:
        return 0.0
    base = dti(truth, pred, radius)
    trial = pred.copy()
    trial[i, j] = 0.0
    return dti(truth, trial, radius) - base


def pays_threshold(dti_value):
    """Minimum kernel credit a new dot must earn to raise DTI."""
    return 0.2 * dti_value
