#!/usr/bin/env python3
"""
Linear against non-linear probe, on identical features and identical folds.

A linear probe reports whether information is linearly ACCESSIBLE, not whether it
is PRESENT. A low score is therefore ambiguous between a representation having lost
a distinction and a representation encoding it in a form a linear probe cannot
reach. That ambiguity bears hardest on the continuous-against-discrete comparison,
because quantised vectors occupy a finite set of fixed positions and there is no
guarantee they are as linearly separable as a continuous manifold carrying the same
information.

This script tests it rather than arguing around it. If discreteness were penalising
the linear probe, Mimi should gain MOST from the extra flexibility.

The MLP is kept deliberately small and strongly regularised. A sufficiently powerful
probe can learn a task from almost any representation and thereby report on its own
capacity instead of on the encoding, so a large network would make the comparison
meaningless. Single hidden layer, 64 units, strong weight decay, early stopping.

A single configuration turned out to be a weak basis for the conclusion, because the
per-representation gains move by up to 0.06 across reasonable settings and two of them
change sign. --sweep therefore reports the gain under six configurations, and the claim
made in the write-up is the one that survives all of them, namely a bound on the size of
any non-linear gain rather than a statement about which representation gains most.

Folds, scaling, scoring and the permutation-null procedure are taken unchanged from
src/18_probe.py so the linear column here reproduces the headline figures exactly.

Usage:
  python3 src/22_nonlinear_probe.py
  python3 src/22_nonlinear_probe.py --sweep
  python3 src/22_nonlinear_probe.py --perm 30 --out results/linear_vs_nonlinear_probe.txt
"""
import argparse, csv, sys, warnings
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.metrics import f1_score

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
FEAT = ROOT / "features"
CLASSES = ("affiliative", "neutral", "adversarial")
WINDOW = "W2_segment"
RNG = np.random.default_rng(42)

# Best layer per continuous encoder, as established by the layer sweep in src/18.
BEST_LAYER = {"wavlm": 20, "hubert": 23, "whisper": 9}

# (display name, feature dir, window/key, layer or None)
VIEWS = [
    ("WavLM",            "wavlm",            WINDOW,    BEST_LAYER["wavlm"]),
    ("Whisper encoder",  "whisper",          WINDOW,    BEST_LAYER["whisper"]),
    ("HuBERT",           "hubert",           WINDOW,    BEST_LAYER["hubert"]),
    ("Mimi pre-quant",   "mimi_pre_meanstd", WINDOW,    None),
    ("Mimi post-quant",  "mimi_post",        WINDOW,    None),
    ("Mimi histogram",   "mimi",             WINDOW,    None),
    ("DAC post-quant",   "dac_post",         WINDOW,    None),
    ("Text, context",    "text",             "context", None),
]
# Representations carried through the MLP permutation null. One continuous and one
# discrete is enough to show the MLP is training rather than emitting noise.
NULL_VIEWS = ("WavLM", "Mimi post-quant")


def load_manifest():
    src = ROOT / "manifest.csv"
    if not src.exists():
        src = ROOT / "data" / "annotations" / "manifest.csv"
    if not src.exists():
        src = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
    return {r["candidate_id"]: r for r in csv.DictReader(open(src, newline=""))
            if r.get("stance", "").strip() in CLASSES}


def load_view(feat_dir, key, layer, man):
    p = FEAT / feat_dir / f"{key}.npz"
    if not p.exists():
        return None
    d = np.load(p, allow_pickle=True)
    ids, X = list(d["ids"]), d["X"]
    if layer is not None:
        if X.ndim != 3:
            sys.exit(f"{p} is {X.ndim}-D; a layer index needs (n, layers, dim)")
        X = X[:, layer, :]
    X = X.reshape(len(ids), -1)
    keep = [i for i, cid in enumerate(ids) if cid in man]
    y = np.array([man[ids[i]]["stance"] for i in keep])
    groups = np.array([man[ids[i]]["episode_id"] for i in keep])
    return X[keep], y, groups


def linear_pipe():
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=3000, C=1.0, class_weight="balanced"),
    )


def mlp_pipe(hidden=64, alpha=1.0, early=True):
    """Deliberately small and strongly regularised. See the module docstring."""
    return make_pipeline(
        StandardScaler(),
        MLPClassifier(hidden_layer_sizes=(hidden,), alpha=alpha, max_iter=2000,
                      early_stopping=early, n_iter_no_change=20,
                      validation_fraction=0.15, random_state=42),
    )


# Capacity settings for --sweep. The primary configuration is (64, 1.0, True).
SWEEP = [(32, 1.0, True), (64, 0.1, True), (64, 1.0, True),
         (64, 10.0, True), (64, 1.0, False), (128, 1.0, True)]


def cfg_label(h, a, e):
    return f"h{h}/a{a}" + ("" if e else "/noES")


def oof(pipe_fn, X, y, groups, n_splits=5):
    ns = min(n_splits, len(set(groups)), min(Counter(y).values()))
    if ns < 2:
        return None
    return cross_val_predict(pipe_fn(), X, y, groups=groups, cv=GroupKFold(n_splits=ns))


def score(pipe_fn, X, y, groups):
    pred = oof(pipe_fn, X, y, groups)
    return None if pred is None else f1_score(y, pred, average="macro")


def permutation_null(pipe_fn, X, y, groups, P):
    """Empirical null: refit on shuffled labels. Same procedure as src/18_probe.py."""
    out = []
    for _ in range(P):
        yp = RNG.permutation(np.asarray(y))
        pred = oof(pipe_fn, X, yp, groups)
        if pred is not None:
            out.append(f1_score(yp, pred, average="macro"))
    return np.asarray(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perm", type=int, default=30,
                    help="permutations for the MLP null (30 in the reported run)")
    ap.add_argument("--sweep", action="store_true",
                    help="also report the gain under six capacity settings")
    ap.add_argument("--out", default="results/linear_vs_nonlinear_probe.txt")
    args = ap.parse_args()

    man = load_manifest()
    lines = []

    def emit(s=""):
        print(s, flush=True)
        lines.append(s)

    emit("LINEAR vs NON-LINEAR PROBE, 3-way stance, W2, identical features and folds")
    emit("A large non-linear gain would mean the information was present but not linearly")
    emit("accessible, and that the linear figures understate that representation.")
    emit("=" * 86)
    emit(f"{'representation':22}{'linear':>10}{'MLP':>10}{'gain':>10}")

    loaded = {}
    for name, d, key, layer in VIEWS:
        got = load_view(d, key, layer, man)
        if got is None:
            emit(f"{name:22}{'(features missing)':>30}")
            continue
        X, y, g = got
        loaded[name] = got
        lin, mlp = score(linear_pipe, X, y, g), score(mlp_pipe, X, y, g)
        if lin is None or mlp is None:
            emit(f"{name:22}{'(too few folds)':>30}")
            continue
        emit(f"{name:22}{lin:10.3f}{mlp:10.3f}{mlp - lin:+10.3f}")

    if args.sweep:
        emit()
        emit("CAPACITY SWEEP. Gain over the linear probe under six settings.")
        emit("A single configuration is a weak basis for this conclusion: individual gains move")
        emit("by up to 0.06 across these settings and some change sign. What is stable is the")
        emit("BOUND, so that is what the write-up claims.")
        emit("=" * 86)
        emit(f"{'representation':18}{'linear':>8}" +
             "".join(f"{cfg_label(*c):>14}" for c in SWEEP))
        best = {}
        for name, _, _, _ in VIEWS:
            if name not in loaded:
                continue
            X, y, g = loaded[name]
            lin = score(linear_pipe, X, y, g)
            gains = [score(lambda h=h, a=a, e=e: mlp_pipe(h, a, e), X, y, g) - lin
                     for h, a, e in SWEEP]
            best[name] = max(gains)
            emit(f"{name:18}{lin:8.3f}" + "".join(f"{v:+14.3f}" for v in gains))
        emit()
        emit(f"Largest gain observed anywhere in the sweep: "
             f"{max(best.values()):+.3f} ({max(best, key=best.get)})")

    emit()
    emit(f"MLP permutation null, {args.perm} permutations, to confirm the MLP is not "
         f"simply overfitting")
    emit("=" * 86)
    for name in NULL_VIEWS:
        if name not in loaded:
            continue
        X, y, g = loaded[name]
        mlp = score(mlp_pipe, X, y, g)
        null = permutation_null(mlp_pipe, X, y, g, args.perm)
        p = (int((null >= mlp).sum()) + 1) / (len(null) + 1)
        emit(f"{name:20} MLP {mlp:.3f}   null mean {null.mean():.3f}   "
             f"margin {mlp - null.mean():+.3f}   p {p:.3f}")

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
