#!/usr/bin/env python3
"""
Is Mimi's within-word figure a fact about Mimi, or about the readout?

The per-phrase analysis in view C of src/18_probe.py summarises Mimi as per-codebook
unigram histograms, 16,384 dimensions, while the continuous encoders get pooled
embeddings of 2,048 or fewer. Pooled over all 873 clips that asymmetry costs about
0.031 of margin. Within a phrase the cells hold 58 to 129 clips, so the same
asymmetry is far more punishing, and on three phrases the histogram probe
degenerates entirely, emitting a single class for every clip.

This script reruns the within-word analysis with Mimi represented three ways, so
the readout is the only thing that varies:

  histogram      per-codebook unigram counts, 16,384 dims, as reported in Table 4.2
  post-quant     summed codebook vectors, 1,024 dims, mean and std pooled
  pre-quant      projected encoder latent, 1,024 dims, mean and std pooled

The continuous encoders and the text baseline are included unchanged as reference
points. Degenerate cells are detected and counted rather than averaged in silently.

Usage:  python3 src/26_within_word_readout.py
"""
import csv, warnings
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.metrics import f1_score

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
FEAT = ROOT / "features"
OUT = ROOT / "results" / "within_word_readout.txt"
CLASSES = ("affiliative", "neutral", "adversarial")

VIEWS = [
    ("Whisper encoder",        "whisper",          "W2_segment", 9,    "embedding, 1,536"),
    ("WavLM",                  "wavlm",            "W2_segment", 20,   "embedding, 2,048"),
    ("HuBERT",                 "hubert",           "W2_segment", 23,   "embedding, 2,048"),
    ("Mimi, pre-quantisation", "mimi_pre_meanstd", "W2_segment", None, "embedding, 1,024"),
    ("Mimi, post-quantisation", "mimi_post",       "W2_segment", None, "embedding, 1,024"),
    ("Text, with discourse",   "text",             "context",    None, "embedding, 768"),
    ("Mimi, histogram",        "mimi",             "W2_segment", None, "histogram, 16,384"),
]


def manifest():
    src = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
    return {r["candidate_id"]: r for r in csv.DictReader(open(src, newline=""))
            if r.get("stance", "").strip() in CLASSES}


def load(feat_dir, key, layer, man):
    p = FEAT / feat_dir / f"{key}.npz"
    if not p.exists():
        return None
    d = np.load(p, allow_pickle=True)
    ids, X = list(d["ids"]), d["X"]
    if layer is not None:
        X = X[:, layer, :]
    X = X.reshape(len(ids), -1)
    keep = [i for i, c in enumerate(ids) if c in man]
    meta = [man[ids[i]] for i in keep]
    return (X[keep],
            np.array([m["stance"] for m in meta]),
            np.array([m["target_phrase"] for m in meta]),
            np.array([m["episode_id"] for m in meta]))


def within_word(X, y, ph, g):
    """Per-phrase dominant binary contrast. Returns {phrase: (f1, maj, degenerate)}."""
    out = {}
    for p in sorted(set(ph)):
        m = ph == p
        yp = y[m]
        keep = [c for c, _ in Counter(yp).most_common(2)]
        s = np.isin(yp, keep)
        ys, Xs, gs = yp[s], X[m][s], g[m][s]
        if len(set(ys)) < 2:
            continue
        ns = min(5, len(set(gs)), min(Counter(ys).values()))
        if ns < 2:
            continue
        pipe = make_pipeline(StandardScaler(),
                             LogisticRegression(max_iter=3000, C=1.0,
                                                class_weight="balanced"))
        pred = cross_val_predict(pipe, Xs, ys, groups=gs, cv=GroupKFold(n_splits=ns))
        maj = Counter(ys).most_common(1)[0][0]
        out[p] = (f1_score(ys, pred, average="macro"),
                  f1_score(ys, [maj] * len(ys), average="macro"),
                  len(set(pred)) < 2)
    return out


def main():
    man = manifest()
    lines = []

    def emit(s=""):
        print(s, flush=True)
        lines.append(s)

    emit("WITHIN-WORD DECODABILITY BY READOUT")
    emit("Per-phrase dominant binary contrast, W2, mean over the eight phrases.")
    emit("A degenerate cell is one where the probe emitted a single class, scoring")
    emit("exactly the within-phrase majority. Those are counted, not excluded, so the")
    emit("mean is directly comparable to Table 4.2 as currently reported.")
    emit("=" * 84)
    emit(f"{'representation':26}{'readout':22}{'mean F1':>10}{'degenerate':>12}")
    emit("-" * 84)

    results = {}
    for name, d, key, layer, readout in VIEWS:
        got = load(d, key, layer, man)
        if got is None:
            emit(f"{name:26}{'features missing':>34}")
            continue
        res = within_word(*got)
        results[name] = res
        f1 = np.mean([v[0] for v in res.values()])
        dg = sum(v[2] for v in res.values())
        emit(f"{name:26}{readout:22}{f1:>10.3f}{f'{dg}/{len(res)}':>12}")

    emit()
    emit("PER-PHRASE, MIMI ONLY, BY READOUT")
    emit("=" * 84)
    mimi = [n for n in results if n.startswith("Mimi")]
    emit(f"{'phrase':12}" + "".join(f"{n.split(', ')[1]:>22}" for n in mimi))
    for p in sorted(next(iter(results.values()))):
        row = f"{p:12}"
        for n in mimi:
            e = results[n].get(p)
            row += f"{('degenerate' if e[2] else f'{e[0]:.3f}'):>22}" if e else f"{'-':>22}"
        emit(row)

    emit()
    hist = np.mean([v[0] for v in results["Mimi, histogram"].values()])
    post = np.mean([v[0] for v in results["Mimi, post-quantisation"].values()])
    text = np.mean([v[0] for v in results["Text, with discourse"].values()])
    emit(f"Cost of the histogram readout within a phrase: {post - hist:.3f}")
    emit(f"For comparison, pooled over all 873 clips it costs 0.031 (results/quantisation_ladder.txt).")
    emit(f"Mimi against the discourse-text baseline of {text:.3f}: "
         f"{hist:.3f} under the histogram, {post:.3f} under the embedding.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
