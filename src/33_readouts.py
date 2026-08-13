#!/usr/bin/env python3
"""
Readouts over frame sequences. The library, not the experiment.

Every readout in the study so far is permutation-invariant over frames. Mean and
standard deviation are order-free by construction and a unigram histogram counts
codes without regard to when they occurred, so shuffling the frames leaves the
probe input identical. A rising "yeah?" and a falling "yeah." have the same mean.
That makes the measured codec loss unattributable between the codec and the
readout, which is what src/31 was rebuilt to fix.

This module turns a (T, D) frame sequence into a vector, several ways, so the
representation is held fixed and only the readout changes.

  meanstd        mean and std over frames              order-free, the baseline
  basisK         Legendre coefficients over time       level, trend, curvature, ...
  segK           K equal segments, pooled              coarse trajectory
  delta          meanstd, plus meanstd of differences  local dynamics

basisK is the principled one. Time is normalised to [-1, 1] over each clip's own
real length and the sequence projected onto orthonormal Legendre polynomials, so
coefficient 0 is the mean, 1 is linear trend, 2 is curvature. Two properties earn
it its place. It is nested, since basis1 IS the mean, so any gain over meanstd is
attributable to the added terms and nothing else. And it handles variable length
natively, evaluating the basis at whatever T a clip actually produced, which segK
only fakes by chopping into equal pieces.

Discrete streams get different treatment, because a temporal basis over code
indices is meaningless. Index 5 is not between 4 and 6, so a trend coefficient
over indices has no interpretation. Their order-aware summaries are instead:

  hist           per-codebook unigram counts           the deployed baseline
  runs           run-length statistics per codebook    how long codes persist
  changes        change rate per codebook              how often codes switch

Variable-rate models carry timing that no fixed-grid model emits at all, so they
get one more:

  timing         token count, rate, duration moments   the segmentation itself

Nothing here pools over padding. Every function takes the clip's true length and
reads only that far.

Imported by src/34. Not run directly.
"""
import numpy as np

# --------------------------------------------------------------- continuous


def _ms(F):
    """Mean and std, the pooling src/17 and src/20 use, so results are comparable."""
    if len(F) < 2:
        return np.concatenate([F.mean(0), np.zeros(F.shape[1])]) if len(F) else None
    return np.concatenate([F.mean(0), F.std(0)])


def legendre_basis(T, K):
    """(T, K) orthonormal Legendre polynomials on time normalised to [-1, 1].

    Column 0 is constant, so projecting onto it recovers the mean up to scale.
    Higher columns are linear, quadratic and so on, which is what gives the
    coefficients their reading as level, trend and curvature.
    """
    if T == 1:
        return np.ones((1, K), dtype=np.float64) / np.sqrt(K)
    t = np.linspace(-1.0, 1.0, T)
    B = np.empty((T, K), dtype=np.float64)
    for k in range(K):
        c = np.zeros(k + 1); c[k] = 1.0
        B[:, k] = np.polynomial.legendre.legval(t, c)
    B /= np.linalg.norm(B, axis=0, keepdims=True) + 1e-12   # orthonormal columns
    return B


def r_basis(F, K=4):
    """Project the sequence onto the first K Legendre polynomials. -> (K*D,)"""
    B = legendre_basis(len(F), K)
    return (B.T @ F).ravel()


def r_meanstd(F):
    return _ms(F)


def r_seg(F, K=4):
    """K equal segments, each pooled. -> (2*K*D,)"""
    idx = np.array_split(np.arange(len(F)), K)
    D = F.shape[1]
    return np.concatenate([_ms(F[i]) if len(i) > 1 else np.zeros(2 * D) for i in idx])


def r_delta(F):
    """meanstd of the sequence and of its first differences. -> (4D,)"""
    d = np.diff(F, axis=0) if len(F) > 1 else np.zeros((1, F.shape[1]))
    return np.concatenate([_ms(F), _ms(d)])


CONTINUOUS = {
    "meanstd":  r_meanstd,
    "basis2":   lambda F: r_basis(F, 2),
    "basis4":   lambda F: r_basis(F, 4),
    "basis8":   lambda F: r_basis(F, 8),
    "seg4":     lambda F: r_seg(F, 4),
    "delta":    r_delta,
}

# ----------------------------------------------------------------- discrete


def r_hist(C, n_codes):
    """Per-codebook unigram counts, normalised. This is the deployed baseline in
    src/17, and it is order-free. -> (n_books * n_codes,)"""
    out = [np.bincount(C[:, b], minlength=n_codes) for b in range(C.shape[1])]
    return np.concatenate(out).astype(np.float64) / max(len(C), 1)


def r_runs(C):
    """Run-length statistics per codebook: mean, std, max, and the fraction of
    frames that begin a new run. How long a code persists is a temporal property
    that no histogram can see, and unlike a basis it is meaningful on categorical
    values. -> (4 * n_books,)"""
    out = []
    for b in range(C.shape[1]):
        v = C[:, b]
        if len(v) < 2:
            out += [float(len(v)), 0.0, float(len(v)), 1.0]; continue
        starts = np.flatnonzero(np.diff(v) != 0) + 1
        runs = np.diff(np.concatenate([[0], starts, [len(v)]])).astype(np.float64)
        out += [runs.mean(), runs.std(), runs.max(), len(runs) / len(v)]
    return np.asarray(out)


def r_changes(C):
    """Fraction of adjacent frames where the code differs, per codebook.
    -> (n_books,)"""
    if len(C) < 2:
        return np.zeros(C.shape[1])
    return (np.diff(C, axis=0) != 0).mean(0).astype(np.float64)


DISCRETE = {
    "hist":     None,        # needs n_codes, wired up in src/34
    "runs":     r_runs,
    "changes":  r_changes,
}

# ------------------------------------------------------------------- timing


def r_timing(T, clip_seconds, bounds=None, durs=None):
    """The segmentation itself, for models that choose their own units.

    Every W2 clip is exactly 10 seconds, so token count is not contaminated by
    duration and reflects delivery alone. No fixed-grid model can produce this
    feature at all, because its token count is a property of the clock.

    bounds: (n, 2) start and end per unit, Sylber.
    durs:   (n, 1) frame counts per unit, DyCAST.
    """
    out = [float(T), T / clip_seconds]
    if bounds is not None and len(bounds) > 1:
        span = bounds[:, 1] - bounds[:, 0]
        gap = bounds[1:, 0] - bounds[:-1, 1]
        out += [span.mean(), span.std(), span.min(), span.max(),
                gap.mean(), gap.std(), float(span.sum() / clip_seconds)]
    elif durs is not None and len(durs) > 1:
        d = durs.ravel().astype(np.float64)
        out += [d.mean(), d.std(), d.min(), d.max(),
                float(np.median(d)), float((d == 1).mean()), float(d.sum())]
    else:
        out += [0.0] * 7
    return np.asarray(out, dtype=np.float64)
