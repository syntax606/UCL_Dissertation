#!/usr/bin/env python3
"""Linear against non-linear probe, recomputed over 25 partitions.

src/22 produced Appendix B.3 on a single GroupKFold partition, which is the scheme [3.7]
rejects. Its linear column drifted up to 0.036 from Table 4.1 as a result, most of that on
DAC after quantisation. The gains were defensible even so, since each is a difference taken
within one run on identical folds, but they were the last load-bearing figures in the
document not built the way the methods chapter describes. [4.6] and [6.2] both quote the
bound across the capacity sweep, so that bound should rest on the same footing as everything
else.

Everything about the probes is src/22's. The linear probe is the same L2 logistic
regression with balanced class weights, the MLP is the same deliberately small and strongly
regularised network, and the six capacity settings are unchanged. Only the partitioning
changes, to _partition from src/34 seeded 25 times, and the gain is formed inside each
partition before averaging so it carries a spread rather than being a difference of two
averages.

Usage:  python3 src/49_nonlinear_repeated.py
        python3 src/49_nonlinear_repeated.py --reps 5 --jobs 4
"""
import argparse
import csv
import warnings
from pathlib import Path

import numpy as np
from joblib import Parallel, delayed
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
FEAT = ROOT / "features"
OUT = ROOT / "results" / "nonlinear_repeated.txt"
CLASSES = ("affiliative", "neutral", "adversarial")
WINDOW = "W2_segment"
N_FOLDS = 5

BEST_LAYER = {"wavlm": 20, "hubert": 23, "whisper": 9}
VIEWS = [
    ("WavLM",           "wavlm",            WINDOW,   BEST_LAYER["wavlm"]),
    ("Whisper encoder", "whisper",          WINDOW,   BEST_LAYER["whisper"]),
    ("HuBERT",          "hubert",           WINDOW,   BEST_LAYER["hubert"]),
    ("Mimi pre-quant",  "mimi_pre_meanstd", WINDOW,   None),
    ("Mimi post-quant", "mimi_post",        WINDOW,   None),
    ("Mimi histogram",  "mimi",             WINDOW,   None),
    ("DAC post-quant",  "dac_post",         WINDOW,   None),
    ("Text, context",   "text",             "context", None),
]
SWEEP = [(32, 1.0, True), (64, 0.1, True), (64, 1.0, True),
         (64, 10.0, True), (64, 1.0, False), (128, 1.0, True)]


def cfg_label(h, a, e):
    return f"h{h}/a{a}" + ("" if e else "/noES")


def _partition(g, seed, n_folds=N_FOLDS):
    """Whole episodes to folds from an explicit seed. Copied from src/34."""
    uq = sorted(set(g))
    perm = np.random.default_rng(seed).permutation(len(uq))
    g2f = {uq[perm[i]]: i % n_folds for i in range(len(uq))}
    return np.array([g2f[gi] for gi in g])


def linear_pipe():
    return make_pipeline(StandardScaler(),
                         LogisticRegression(max_iter=3000, C=1.0, class_weight="balanced"))


def mlp_pipe(hidden=64, alpha=1.0, early=True):
    return make_pipeline(
        StandardScaler(),
        MLPClassifier(hidden_layer_sizes=(hidden,), alpha=alpha, max_iter=2000,
                      early_stopping=early, n_iter_no_change=20,
                      validation_fraction=0.15, random_state=42))


def manifest():
    src = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
    return {r["candidate_id"]: r for r in csv.DictReader(open(src, newline=""))
            if r.get("stance", "").strip() in CLASSES}


def load_view(d, key, layer, man):
    p = FEAT / d / f"{key}.npz"
    if not p.exists():
        return None
    z = np.load(p, allow_pickle=True)
    ids = [str(c) for c in z["ids"]]
    keep = [i for i, c in enumerate(ids) if c in man]
    X = z["X"][keep]
    if layer is not None:
        X = X[:, layer, :]
    X = X.reshape(len(keep), -1)
    y = np.array([man[ids[i]]["stance"] for i in keep])
    g = np.array([man[ids[i]]["episode_id"] for i in keep])
    return X, y, g


def score(pipe_fn, X, y, fold):
    """Out-of-fold macro-F1 under one partition."""
    pred = np.empty(len(y), dtype=object)
    for f in range(N_FOLDS):
        te = fold == f
        tr = ~te
        m = pipe_fn().fit(X[tr], y[tr])
        pred[te] = m.predict(X[te])
    return f1_score(y, list(pred), average="macro", labels=list(CLASSES))


def one_partition(seed, views):
    """Linear and every sweep configuration for every representation, one partition."""
    out = {}
    for name, (X, y, g) in views.items():
        fold = _partition(g, seed)
        lin = score(linear_pipe, X, y, fold)
        row = {"linear": lin}
        for h, a, e in SWEEP:
            row[cfg_label(h, a, e)] = score(lambda: mlp_pipe(h, a, e), X, y, fold) - lin
        out[name] = row
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=25)
    ap.add_argument("--jobs", type=int, default=6)
    args = ap.parse_args()

    man = manifest()
    views = {}
    for name, d, key, layer in VIEWS:
        got = load_view(d, key, layer, man)
        if got is not None:
            views[name] = got

    lines = []
    def emit(s=""):
        print(s, flush=True)
        lines.append(s)

    emit("LINEAR AGAINST NON-LINEAR PROBE, RECOMPUTED UNDER [3.7]")
    emit(f"{args.reps} partitions, {N_FOLDS} folds, six capacity settings. Replaces the "
         f"single-partition figures from src/22.")
    emit("The gain is formed inside each partition and averaged afterwards.")
    emit("=" * 104)
    for name in views:
        emit(f"  {name:20} {views[name][0].shape[1]:>6} dims")
    emit()

    res = Parallel(n_jobs=args.jobs, verbose=5)(
        delayed(one_partition)(s, views) for s in range(args.reps))

    labels = [cfg_label(*c) for c in SWEEP]
    emit()
    emit("LINEAR PROBE, mean over partitions (sd)")
    emit(f"{'representation':22}{'macro-F1':>12}")
    lin = {}
    for name in views:
        v = np.array([r[name]["linear"] for r in res])
        lin[name] = v
        emit(f"{name:22}{v.mean():>8.3f} ({v.std():.3f})")
    emit()

    emit("GAIN FROM THE NON-LINEAR PROBE, mean over partitions")
    emit(f"{'representation':22}" + "".join(f"{l:>16}" for l in labels))
    gains = {}
    for name in views:
        row = []
        for l in labels:
            v = np.array([r[name][l] for r in res])
            gains[(name, l)] = v
            row.append(f"{v.mean():>+11.3f} ({v.std():.3f})")
        emit(f"{name:22}" + "".join(f"{c:>16}" for c in row))
    emit()

    best = max(gains.items(), key=lambda kv: kv[1].mean())
    emit("THE BOUND [4.6] AND [6.2] QUOTE")
    emit("-" * 104)
    emit(f"  largest mean gain anywhere in the sweep: {best[1].mean():+.3f} "
         f"(sd {best[1].std():.3f}) at {best[0][1]} on {best[0][0]}")
    hi = max(gains.items(), key=lambda kv: kv[1].mean() + kv[1].std())
    emit(f"  largest mean plus one sd:                "
         f"{hi[1].mean() + hi[1].std():+.3f} at {hi[0][1]} on {hi[0][0]}")
    cont = [n for n in views if n in ("WavLM", "Whisper encoder", "HuBERT")]
    disc = [n for n in views if "histogram" in n or "post-quant" in n]
    if cont and disc:
        gap = np.mean([lin[n].mean() for n in cont]) - np.mean([lin[n].mean() for n in disc])
        emit(f"  continuous-to-discrete gap in the linear column: {gap:.3f}")
    emit()
    emit("Read: the claim carried into the chapters is a bound on any non-linear gain, not")
    emit("an ordering. It holds if the largest gain anywhere stays well under the gap above.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
