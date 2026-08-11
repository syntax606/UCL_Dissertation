#!/usr/bin/env python3
"""
Put the models and the human annotators on the same 60 clips.

[4.1] reports human accuracy of 0.65 from transcript with discourse context and
0.73 from audio with transcript, on a 60-clip subset judged against a hidden
reference. [4.2] reports model macro-F1 of 0.573 for WavLM over all 873 clips.
Those two numbers are routinely read against each other and should not be. They
differ in sample, in metric, and in what the judge had access to.

This script removes all three differences. Models are trained on the 813 clips the
annotators never saw, with every episode appearing in the test set excluded from
training, and evaluated on exactly the 60 they did. Accuracy is reported alongside
macro-F1, since accuracy is what the human figures are.

The information asymmetry is handled by including a condition that concatenates
audio and text features, which is what the human audio condition actually had.

Usage:  python3 src/29_premise_ceiling.py
"""
import csv, warnings
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import f1_score, accuracy_score

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
FEAT = ROOT / "features"
KEY = ROOT / "data" / "annotations" / "premise_key.csv"
OUT = ROOT / "results" / "premise_ceiling.txt"
CLASSES = ("affiliative", "neutral", "adversarial")

# name, feature dir, key, layer, modality
VIEWS = [
    ("WavLM",             "wavlm",    "W2_segment", 20,   "audio"),
    ("Whisper encoder",   "whisper",  "W2_segment", 9,    "audio"),
    ("HuBERT",            "hubert",   "W2_segment", 23,   "audio"),
    ("eGeMAPS",           "egemaps",  "W2_segment", None, "audio"),
    ("Mimi, deployed",    "mimi",     "W2_segment", None, "audio"),
    ("Text, discourse",   "text",     "context",    None, "text"),
]


def manifest():
    src = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
    return {r["candidate_id"]: r for r in csv.DictReader(open(src, newline=""))
            if r.get("stance", "").strip() in CLASSES}


def load(feat_dir, key, layer):
    p = FEAT / feat_dir / f"{key}.npz"
    if not p.exists():
        return None
    d = np.load(p, allow_pickle=True)
    ids, X = list(d["ids"]), d["X"]
    if layer is not None:
        X = X[:, layer, :]
    return {c: X[i].reshape(-1) for i, c in enumerate(ids)}


def evaluate(feats, man, test_ids, test_eps):
    """Train on clips from episodes absent from the test set, score on the 60."""
    tr = [c for c in feats
          if c in man and c not in test_ids and man[c]["episode_id"] not in test_eps]
    te = [c for c in test_ids if c in feats]
    if len(te) < 10:
        return None
    Xtr = np.array([feats[c] for c in tr]); ytr = np.array([man[c]["stance"] for c in tr])
    Xte = np.array([feats[c] for c in te]); yte = np.array([man[c]["stance"] for c in te])
    pipe = make_pipeline(StandardScaler(),
                         LogisticRegression(max_iter=3000, C=1.0,
                                            class_weight="balanced"))
    pipe.fit(Xtr, ytr)
    pred = pipe.predict(Xte)
    return (accuracy_score(yte, pred), f1_score(yte, pred, average="macro"),
            len(tr), len(te))


def main():
    man = manifest()
    key = list(csv.DictReader(open(KEY, newline="")))
    test_ids = [r["candidate_id"] for r in key if r["candidate_id"] in man]
    test_eps = {man[c]["episode_id"] for c in test_ids}
    yte = [man[c]["stance"] for c in test_ids]

    lines = []
    def emit(s=""):
        print(s, flush=True); lines.append(s)

    emit("MODELS AND HUMANS ON THE SAME 60 CLIPS")
    emit("Trained on clips from episodes absent from the test set, scored on the")
    emit("premise-check subset. Accuracy is the comparable metric, since that is what")
    emit("the human figures in [4.1] are. Macro-F1 given alongside.")
    emit("=" * 78)
    emit(f"test clips: {len(test_ids)}   held-out episodes: {len(test_eps)}")
    emit(f"test stance mix: {dict(Counter(yte))}")
    maj = Counter(yte).most_common(1)[0]
    emit(f"majority-class accuracy on these 60: {maj[1]/len(yte):.3f} ({maj[0]})")
    emit(f"three-way chance: 0.333")
    emit()

    emit(f"{'condition':28}{'modality':10}{'accuracy':>10}{'macro-F1':>10}{'train n':>9}")
    emit("-" * 78)
    emit(f"{'HUMAN, transcript + context':28}{'text':10}{0.65:>10.3f}{'':>10}{'':>9}")
    emit(f"{'HUMAN, audio + transcript':28}{'both':10}{0.73:>10.3f}{'':>10}{'':>9}")
    emit("-" * 78)

    loaded = {}
    for name, d, k, layer, modality in VIEWS:
        f = load(d, k, layer)
        if f is None:
            emit(f"{name:28}{'features missing':>40}")
            continue
        loaded[name] = f
        r = evaluate(f, man, test_ids, test_eps)
        if r:
            emit(f"{name:28}{modality:10}{r[0]:>10.3f}{r[1]:>10.3f}{r[2]:>9}")

    # the condition that matches what the human audio judges actually had
    if "WavLM" in loaded and "Text, discourse" in loaded:
        a, tx = loaded["WavLM"], loaded["Text, discourse"]
        both = {c: np.concatenate([a[c], tx[c]]) for c in a if c in tx}
        r = evaluate(both, man, test_ids, test_eps)
        if r:
            emit(f"{'WavLM + text, concatenated':28}{'both':10}{r[0]:>10.3f}"
                 f"{r[1]:>10.3f}{r[2]:>9}")

    emit()
    emit("The last row is the only model condition with the same information the human")
    emit("audio judges had. The rows above it are audio-only or text-only and are not")
    emit("directly comparable to the 0.73, though they are comparable to each other.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
