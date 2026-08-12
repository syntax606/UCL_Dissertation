#!/usr/bin/env python3
"""
How much did picking the best layer by argmax flatter the reported numbers?

src/18 section G scores every layer and reports the winner, via
`best = int(np.argmax(curve))`. The winner is therefore selected on the same
cross-validated data its score is read from, which biases that score upward. The
size of the bias is unknown and BEST_LAYER = {wavlm: 20, hubert: 23, whisper: 9}
is hardcoded into src/20, src/22 and src/31 on the strength of it.

Two questions, both answerable from the pooled per-layer features that already
exist, with no re-extraction:

  1. HONESTY. Select the layer inside each training split only, then score on the
     held-out episodes. The gap between that and the reported figure is the
     optimism the argmax introduced.

  2. STABILITY. Record which layer each fold picks. If the winner moves around,
     the peak is noise, the hardcoded constant is arbitrary, and src/31 should
     save a band of layers rather than one.

Probe, folds and metric are src/18's exactly, so the numbers are comparable.

Usage:  python3 src/32_layer_selection.py
        python3 src/32_layer_selection.py --models wavlm
"""
import argparse, csv, time, warnings
from collections import Counter
from pathlib import Path

import numpy as np
from joblib import Parallel, delayed
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold
from sklearn.metrics import f1_score

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
FEAT = ROOT / "features"
SHEET = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
OUT = ROOT / "results" / "layer_selection.txt"
CLASSES = ("affiliative", "neutral", "adversarial")
REPORTED = {"wavlm": (20, 0.573), "hubert": (23, 0.520), "whisper": (9, 0.564)}
N_OUTER, N_INNER = 5, 5


def probe():
    """src/18 make_probe, unchanged."""
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=3000, C=1.0, class_weight="balanced"))


def manifest():
    return {r["candidate_id"]: r for r in csv.DictReader(open(SHEET, newline=""))
            if r.get("stance", "").strip() in CLASSES}


def load(model, man):
    z = np.load(FEAT / model / "W2_segment.npz", allow_pickle=True)
    ids = list(z["ids"])
    keep = [i for i, c in enumerate(ids) if c in man]
    X = z["X"][keep]                                   # (N, layers, dim)
    y = np.array([man[ids[i]]["stance"] for i in keep])
    g = np.array([man[ids[i]]["episode_id"] for i in keep])
    return X, y, g


def score_layer(X, y, g, layer, tr, te):
    """Fit on tr, score on te, for one layer."""
    p = probe().fit(X[tr, layer], y[tr])
    return f1_score(y[te], p.predict(X[te, layer]), average="macro")


def inner_pick(X, y, g, tr, n_layers):
    """Best layer judged only on the training episodes."""
    gi = g[tr]
    ns = min(N_INNER, len(set(gi)), min(Counter(y[tr]).values()))
    if ns < 2:
        return 0, np.zeros(n_layers)
    cv = list(GroupKFold(n_splits=ns).split(X[tr], y[tr], gi))
    def one(L):
        return float(np.mean([score_layer(X[tr], y[tr], gi, L, a, b) for a, b in cv]))
    curve = np.array(Parallel(n_jobs=-1)(delayed(one)(L) for L in range(n_layers)))
    return int(np.argmax(curve)), curve


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=["wavlm", "hubert", "whisper"])
    args = ap.parse_args()

    man = manifest()
    lines = []
    def emit(s=""):
        print(s, flush=True); lines.append(s)

    emit("DOES THE ARGMAX LAYER CHOICE HOLD UP?")
    emit("Nested selection: the layer is chosen inside each training split, then")
    emit("scored on held-out episodes. Probe, folds and metric as src/18.")
    emit("=" * 78)

    for model in args.models:
        t0 = time.time()
        X, y, g = load(model, man)
        n_layers = X.shape[1]
        emit(f"\n{model.upper()}  {X.shape[0]} clips, {n_layers} layers, "
             f"{len(set(g))} episodes")

        outer = list(GroupKFold(n_splits=N_OUTER).split(X, y, g))

        # 1. honest score for each FIXED layer, no selection at all
        def fixed(L):
            pred = np.empty(len(y), dtype=object)
            for tr, te in outer:
                p = probe().fit(X[tr, L], y[tr])
                pred[te] = p.predict(X[te, L])
            return f1_score(y, list(pred), average="macro")
        fixed_curve = np.array(Parallel(n_jobs=-1)(delayed(fixed)(L)
                                                   for L in range(n_layers)))

        # 2. nested: pick inside each training split, score on held-out
        picks, pred = [], np.empty(len(y), dtype=object)
        for tr, te in outer:
            L, _ = inner_pick(X, y, g, tr, n_layers)
            picks.append(L)
            p = probe().fit(X[tr, L], y[tr])
            pred[te] = p.predict(X[te, L])
        nested = f1_score(y, list(pred), average="macro")

        rep_L, rep_f1 = REPORTED[model]
        naive_L = int(np.argmax(fixed_curve))
        emit(f"  reported in src/18      L{rep_L:<3} {rep_f1:.3f}")
        emit(f"  best fixed layer here   L{naive_L:<3} {fixed_curve[naive_L]:.3f}"
             f"   (argmax over all data, same bias)")
        emit(f"  hardcoded layer, honest L{rep_L:<3} {fixed_curve[rep_L]:.3f}")
        emit(f"  NESTED selection            {nested:.3f}"
             f"   <- unbiased estimate")
        emit(f"  optimism from the argmax    {fixed_curve[naive_L] - nested:+.3f}")
        emit(f"  layer picked per fold   {picks}"
             f"  {'STABLE' if len(set(picks)) == 1 else 'UNSTABLE'}")
        spread = fixed_curve.max() - np.sort(fixed_curve)[-4]
        emit(f"  top-4 layers span       {spread:.3f}"
             f"   ({', '.join(f'L{i}' for i in np.argsort(fixed_curve)[-4:][::-1])})")
        emit(f"  {time.time()-t0:.0f}s")

    emit()
    emit("Read: if NESTED sits well below the reported figure, the reported figure")
    emit("was inflated by choosing the winner on the same data. If the per-fold picks")
    emit("disagree, the peak is noise and src/31 should save a band of layers rather")
    emit("than baking one constant into every downstream result.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
