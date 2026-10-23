"""Distance-Weighted Tversky Index (DTI) primitives for DrivenData #306.

Independent implementation of the scoring algebra stated in the competition
problem description (https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
as transcribed in Agent Brief v2 section 2 and cross-checked against the
lineage's shared template (`GEMSDOE32/src/gems32/metric.py`, read-only).  The
brief requires the algebra to be unit-tested; `tests/test_metric.py` checks
every function here against a literal O(|G|*|P|) transcription.

Official equations
------------------
Triangular kernel, R = 300 m = 3 px on the 100 m grid::

    k(d) = max(1 - d/R, 0)

For prediction values p(x) in [0, 1] and binary truth g:

    TP_w = sum_{g in G} max_{x: d(x,g) <= R} p(x) * k(d(x,g))      "T"
    FP_w = sum_{x: p(x) > 0} p(x) * (1 - max_{g in G} k(d(x,g)))  "n_emit - M"
    FN_w = |G| - TP_w
    DTI  = TP_w / (TP_w + alpha*FP_w + beta*FN_w),  alpha = 0.2, beta = 0.8

Binary-dot algebra
------------------
With unit mass on every dot, S = number of dots, M = sum over dots of
max_g k(d(x,g)), so::

    denom = alpha*T + alpha*(S - M) + beta*|G| = T + alpha*(S - M) + beta*|G| - (1-alpha)*T

which is exactly the brief's `DTI = T / (0.2T + 0.2(S-M) + 0.8|G|)`.  T is a sum
over *truth* pixels (saturating at 1 per truth pixel) and M is a sum over *dots*
(saturating at 1 per dot); they are not interchangeable.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt

ALPHA: float = 0.2
BETA: float = 0.8
RADIUS_PX: float = 3.0
PIXEL_M: float = 100.0
RADIUS_M: float = RADIUS_PX * PIXEL_M
EPS: float = 1e-12


def kernel(d, radius: float = RADIUS_PX) -> np.ndarray:
    """Triangular kernel max(1 - d/R, 0) for distances in pixels."""
    return np.maximum(1.0 - np.asarray(d, dtype=np.float64) / radius, 0.0)


def offsets(radius: float = RADIUS_PX):
    """Lattice offsets with non-zero kernel weight, and their weights."""
    r = int(np.ceil(radius))
    dy, dx, kw = [], [], []
    for j in range(-r, r + 1):
        for i in range(-r, r + 1):
            k = float(kernel(np.hypot(j, i), radius))
            if k > 0.0:
                dy.append(j)
                dx.append(i)
                kw.append(k)
    return np.array(dy, np.int64), np.array(dx, np.int64), np.array(kw, np.float64)


OFF_DY, OFF_DX, OFF_K = offsets()


def max_cover(pred: np.ndarray, truth: np.ndarray):
    """Kernel credit per truth pixel, and per-prediction self-credit."""
    p = np.asarray(pred, np.float64)
    g = np.asarray(truth, bool)
    if p.shape != g.shape:
        raise ValueError("grid shape mismatch")
    if not np.all(np.isfinite(p)):
        raise ValueError("prediction contains non-finite values")
    if (p < 0).any() or (p > 1).any():
        raise ValueError("prediction must lie in [0, 1]")
    h, w = p.shape
    yy, xx = np.nonzero(g)
    credit = np.zeros(yy.size, np.float64)
    for j, i, k in zip(OFF_DY, OFF_DX, OFF_K):
        ny, nx = yy + j, xx + i
        ok = (ny >= 0) & (ny < h) & (nx >= 0) & (nx < w)
        credit[ok] = np.maximum(credit[ok], p[ny[ok], nx[ok]] * k)
    dg = distance_transform_edt(~g) if yy.size else np.full(p.shape, np.inf)
    return credit, kernel(dg), dg


def dti_components(pred: np.ndarray, truth: np.ndarray, *, alpha: float = ALPHA,
                   beta: float = BETA) -> dict:
    """Exact (T, S, M, G, denom, dti) for a prediction on a scored domain.

    `truth` is expected to be already restricted to the scored domain (the
    caller removes known-catalogue pixels and outside-footprint cells).
    """
    p = np.asarray(pred, np.float64)
    g = np.asarray(truth, bool)
    if p.shape != g.shape:
        raise ValueError("grid shape mismatch")
    n_truth = int(g.sum())
    s = float(p.sum())
    if n_truth == 0 or s == 0.0:
        denom = alpha * s + beta * n_truth + EPS
        return dict(T=0.0, S=s, M=0.0, G=float(n_truth), denom=denom, dti=0.0)
    credit, self_credit, _ = max_cover(p, g)
    t = float(credit.sum())
    m = float((p * self_credit).sum())
    denom = alpha * t + alpha * (s - m) + beta * n_truth + EPS
    return dict(T=t, S=s, M=m, G=float(n_truth), denom=denom, dti=t / denom)


def dti_binary(pred: np.ndarray, truth: np.ndarray, *, alpha: float = ALPHA,
               beta: float = BETA) -> dict:
    """DTI for a binary dot field, computed from Euclidean distance transforms."""
    p = np.asarray(pred, bool)
    g = np.asarray(truth, bool)
    if p.shape != g.shape:
        raise ValueError("grid shape mismatch")
    n_truth, n_emit = int(g.sum()), int(p.sum())
    if n_truth == 0 or n_emit == 0:
        return dict(tp=0.0, fp=float(n_emit), fn=float(n_truth), n_truth=n_truth,
                    n_emitted=n_emit, dti=0.0, coverage=0.0)
    tp = float(kernel(distance_transform_edt(~p)[g]).sum())
    kmax = kernel(distance_transform_edt(~g)[p])
    fp = float((1.0 - kmax).sum())
    fn = float(n_truth) - tp
    return dict(tp=tp, fp=fp, fn=fn, n_truth=n_truth, n_emitted=n_emit,
                dti=float(tp / (tp + alpha * fp + beta * fn + EPS)),
                coverage=tp / n_truth)


def dti_bruteforce(pred: np.ndarray, truth: np.ndarray, *, alpha: float = ALPHA,
                   beta: float = BETA, radius: float = RADIUS_PX) -> dict:
    """Literal O(|G|*|P|) transcription of the published equations (test oracle)."""
    p = np.asarray(pred, float)
    g = np.asarray(truth, bool)
    gs = np.argwhere(g)
    xs = np.argwhere(p > 0)
    tp = fn = 0.0
    for gpt in gs:
        best = 0.0
        if xs.size:
            d = np.hypot(*(xs - gpt).T)
            near = d <= radius
            if near.any():
                best = float(np.max(p[tuple(xs[near].T)] * np.maximum(1.0 - d[near] / radius, 0.0)))
        tp += best
        fn += 1.0 - best
    fp = 0.0
    for xpt in xs:
        kmax = 0.0
        if gs.size:
            d = np.hypot(*(gs - xpt).T)
            kmax = float(np.max(np.maximum(1.0 - d / radius, 0.0)))
        fp += p[tuple(xpt)] * (1.0 - kmax)
    return dict(tp=tp, fp=fp, fn=fn,
                dti=float(tp / (tp + alpha * fp + beta * fn + EPS)))


def unique_credit(dots: np.ndarray) -> np.ndarray:
    """Per-dot unique kernel credit: sum of kernel cells where this dot is the sole provider.

    A dot that sits on top of a neighbour (distance < 1 px is impossible on a
    lattice, but 1 px neighbours share most of their 28-cell footprint) supplies
    little credit no truthful field could lose; a dot on a bare ridge supplies
    its full footprint.  This is a property of the dot field only.
    """
    dots = np.asarray(dots, bool)
    h, w = dots.shape
    yy, xx = np.nonzero(dots)
    n = yy.size
    if n == 0:
        return np.zeros(0)
    # provider count per cell over the kernel support
    cover = np.zeros(dots.shape, np.uint8)
    for j, i, _k in zip(OFF_DY, OFF_DX, OFF_K):
        ny, nx = yy + j, xx + i
        ok = (ny >= 0) & (ny < h) & (nx >= 0) & (nx < w)
        cover[ny[ok], nx[ok]] += 1
    loss = np.zeros(n, np.float64)
    for j, i, k in zip(OFF_DY, OFF_DX, OFF_K):
        ny, nx = yy + j, xx + i
        ok = (ny >= 0) & (ny < h) & (nx >= 0) & (nx < w)
        sole = np.zeros(n, bool)
        sole[ok] = cover[ny[ok], nx[ok]] == 1.0
        loss += np.where(sole, k, 0.0)
    return loss
