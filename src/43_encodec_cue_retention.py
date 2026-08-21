#!/usr/bin/env python3
"""Cue retention for EnCodec, using the method and cue groups of src/30.

src/30 predates EnCodec's addition to the study, so Table 4.4 carries Mimi and DAC
but not the codec that makes the architectural comparison in [4.5] possible. This
fills that row using identical groups, identical folds and the same ridge setup, so
the figures are comparable to the existing ones rather than merely similar.
"""
import csv, warnings
from pathlib import Path
import numpy as np
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.metrics import r2_score

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
FEAT, FR = ROOT / "features", ROOT / "features_frames"
CLASSES = ("affiliative", "neutral", "adversarial")
ALPHAS = (1.0, 10.0, 100.0, 1000.0, 10000.0)
GROUPS = {"contour": [1,5,6,7,8,9,11,15,16,17,18,19],
          "level": [0,2,3,4,10,12,13,14,87],
          "voice quality": list(range(30,40)),
          "temporal": list(range(81,87)),
          "spectral": list(range(20,30))+list(range(40,81))}


def man():
    return {r["candidate_id"]: r for r in
            csv.DictReader(open(ROOT/"data/annotations/annotation_sheet_labeled.csv", newline=""))
            if r.get("stance", "").strip() in CLASSES}


def pooled_from_frames(name, order):
    st = FR / name / "W2_segment"
    X = np.load(f"{st}.X.npy", mmap_mode="r"); L = np.load(f"{st}.lengths.npy")
    ids = [str(c) for c in np.load(f"{st}.ids.npy", allow_pickle=True)]
    idx = {c: i for i, c in enumerate(ids)}
    out = []
    for c in order:
        i = idx[c]; F = np.asarray(X[i, :max(int(L[i]), 1)], dtype=np.float64)
        out.append(np.concatenate([F.mean(0), F.std(0)]))
    return np.stack(out)


def pooled_npz(name, order, layer=None):
    z = np.load(FEAT/name/"W2_segment.npz", allow_pickle=True)
    ids = [str(c) for c in z["ids"]]; X = z["X"]
    if layer is not None: X = X[:, layer, :]
    X = X.reshape(len(ids), -1); idx = {c: i for i, c in enumerate(ids)}
    return X[[idx[c] for c in order]]


def group_r2(X, Y, g, cols):
    pipe = make_pipeline(StandardScaler(), RidgeCV(alphas=ALPHAS))
    s = []
    for c in cols:
        y = Y[:, c]
        if np.std(y) < 1e-9: continue
        s.append(r2_score(y, cross_val_predict(pipe, X, y, groups=g, cv=GroupKFold(n_splits=5))))
    return float(np.mean(s)) if s else float("nan")


def main():
    m = man()
    eg = np.load(FEAT/"egemaps"/"W2_segment.npz", allow_pickle=True)
    ids = [str(c) for c in eg["ids"]]
    order = [c for c in ids if c in m]
    pos = {c: i for i, c in enumerate(ids)}
    Y = eg["X"][[pos[c] for c in order]]
    g = np.array([m[c]["episode_id"] for c in order])

    ceil = {gn: group_r2(pooled_npz("wavlm", order, 20), Y, g, cols)
            for gn, cols in GROUPS.items()}
    print(f"{'representation':30}" + "".join(f"{k:>16}" for k in GROUPS))
    print(f"{'WavLM, ceiling, absolute R2':30}" + "".join(f"{ceil[k]:>16.3f}" for k in GROUPS))
    for label, name in (("EnCodec, before quantisation", "encodec_pre"),
                        ("EnCodec, after quantisation", "encodec_post")):
        X = pooled_from_frames(name, order)
        row = {gn: group_r2(X, Y, g, cols) for gn, cols in GROUPS.items()}
        print(f"{label:30}" + "".join(f"{row[k]/ceil[k]:>15.0%} " for k in GROUPS))


if __name__ == "__main__":
    main()
