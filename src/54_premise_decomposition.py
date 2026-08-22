#!/usr/bin/env python3
"""The decomposition E.1 argues from, which was never saved.

E.1 names results/premise_ceiling.txt as its source. That file carries the table, but the
paragraph after it quotes five figures the file does not contain: WavLM's per-class scores
on the sixty-clip subset, and its accuracy under three different evaluations. That
paragraph is the defensive one, the one explaining why the model column sits where it does,
so it is the part of E.1 most likely to be challenged and the part with nothing behind it.

Three evaluations of the same representation, which is the point E.1 makes.

  all 873 out-of-fold      the ordinary condition, every clip scored when held out
  these 60 out-of-fold     the same procedure restricted to the sixty the annotators saw
  held-out-episode split   train on episodes absent from the sixty, as src/29 does

The first two share a training regime and differ only in which clips are scored, so the
gap between them is the subset being harder. The second and third differ only in how much
training data the model gets, so that gap is the cost of the stricter split.

Usage:  python3 src/54_premise_decomposition.py
"""
import csv
import warnings
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
FEAT = ROOT / "features"
KEY = ROOT / "data" / "annotations" / "premise_key.csv"
OUT = ROOT / "results" / "premise_decomposition.txt"
CLASSES = ("affiliative", "neutral", "adversarial")


def manifest():
    src = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
    return {r["candidate_id"]: r for r in csv.DictReader(open(src, newline=""))
            if r.get("stance", "").strip() in CLASSES}


def load(feat_dir, key, layer):
    z = np.load(FEAT / feat_dir / f"{key}.npz", allow_pickle=True)
    ids, X = [str(c) for c in z["ids"]], z["X"]
    if layer is not None:
        X = X[:, layer, :]
    return {c: X[i].reshape(-1) for i, c in enumerate(ids)}


def probe():
    return make_pipeline(StandardScaler(),
                         LogisticRegression(max_iter=3000, C=1.0, class_weight="balanced"))


def main():
    man = manifest()
    feats = load("wavlm", "W2_segment", 20)
    test_ids = [r["candidate_id"] for r in csv.DictReader(open(KEY, newline=""))
                if r["candidate_id"] in man]
    test_eps = {man[c]["episode_id"] for c in test_ids}

    ids = [c for c in feats if c in man]
    X = np.array([feats[c] for c in ids])
    y = np.array([man[c]["stance"] for c in ids])
    g = np.array([man[c]["episode_id"] for c in ids])

    lines = []
    def emit(s=""):
        print(s, flush=True)
        lines.append(s)

    emit("WHY THE MODEL COLUMN IN E.1 SITS WHERE IT DOES")
    emit("WavLM L20, the same features and probe as everywhere else. Supplies the figures")
    emit("E.1 quotes, which results/premise_ceiling.txt does not carry.")
    emit("=" * 84)
    emit()

    # the subset's composition, which is half of E.1's explanation
    sub_mix = Counter(man[c]["stance"] for c in test_ids)
    all_mix = Counter(y)
    emit("SUBSET COMPOSITION")
    emit(f"  the sixty      {dict(sub_mix)}   neutral "
         f"{sub_mix['neutral'] / len(test_ids):.0%}")
    emit(f"  all {len(ids)} clips  {dict(all_mix)}   neutral "
         f"{all_mix['neutral'] / len(ids):.0%}")
    emit()

    # ordinary out-of-fold over everything, and the same predictions read on the sixty
    pred = np.empty(len(y), dtype=object)
    for tr, te in GroupKFold(n_splits=5).split(X, y, g):
        pred[te] = probe().fit(X[tr], y[tr]).predict(X[te])
    pos = {c: i for i, c in enumerate(ids)}
    sub = [pos[c] for c in test_ids if c in pos]
    a_all = accuracy_score(y, list(pred))
    a_sub = accuracy_score(y[sub], list(pred[sub]))

    # the stricter split src/29 uses, which withholds every episode the sixty come from
    tr = [c for c in ids if c not in test_ids and man[c]["episode_id"] not in test_eps]
    Xtr = np.array([feats[c] for c in tr]); ytr = np.array([man[c]["stance"] for c in tr])
    Xte = np.array([feats[c] for c in test_ids if c in feats])
    yte = np.array([man[c]["stance"] for c in test_ids if c in feats])
    p_strict = probe().fit(Xtr, ytr).predict(Xte)
    a_strict = accuracy_score(yte, p_strict)

    emit("THE SAME REPRESENTATION UNDER THREE EVALUATIONS, accuracy")
    emit(f"  all {len(ids)} clips out-of-fold            {a_all:.3f}")
    emit(f"  these {len(sub)} out-of-fold                  {a_sub:.3f}   "
         f"the subset is harder by {a_all - a_sub:+.3f}")
    emit(f"  held-out-episode split, as src/29       {a_strict:.3f}   "
         f"the stricter split costs a further {a_sub - a_strict:+.3f}")
    emit(f"  training clips, out-of-fold {len(X) - len(X) // 5} against "
         f"held-out-episode {len(tr)}")
    emit()

    emit("PER CLASS OVER ALL 873, out-of-fold, F1, which is what E.1 quotes")
    pc = f1_score(y, list(pred), average=None, labels=list(CLASSES))
    for c, v in zip(CLASSES, pc):
        emit(f"  {c:14}{v:.3f}")
    emit(f"  neutral is the weakest by {min(pc[0], pc[2]) - pc[1]:.3f}")
    emit()
    emit("PER CLASS ON THE SIXTY, out-of-fold, F1, where each cell holds twenty clips")
    per = f1_score(y[sub], list(pred[sub]), average=None, labels=list(CLASSES))
    for c, v in zip(CLASSES, per):
        emit(f"  {c:14}{v:.3f}")
    emit(f"  neutral is the weakest by {min(per[0], per[2]) - per[1]:.3f} against the nearer of the "
         f"other two")
    emit()

    # E.1 reads the gap to the human audio figure as a number of standard errors
    HUMAN = 0.730
    n = len(sub)
    gap = HUMAN - a_sub
    se = float(np.sqrt(a_sub * (1 - a_sub) / n))
    emit("THE GAP E.1 QUOTES")
    emit(f"  human audio {HUMAN:.3f} against the most generous model reading {a_sub:.3f}")
    emit(f"  gap {gap:.3f}, and one standard error at {n} items is {se:.3f}, so {gap / se:.1f} of them")
    emit()
    emit("Read: the subset is a third neutral against a sixth overall, and neutral is the")
    emit("class every representation reads worst, so the sixty are harder than the corpus")
    emit("before any model is chosen. That is most of the distance between this table and")
    emit("the headline figures, and it is why [4.1] reads the comparison as a ceiling.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
