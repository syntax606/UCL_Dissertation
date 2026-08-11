#!/usr/bin/env python3
"""
Which acoustic cues does the codec actually lose?

src/27 established where the two annotated axes live in measured acoustics.
Stance is carried by F0 and loudness dynamics, arousal by voice quality. That
locates the contrasts but says nothing about what compression does to them, so it
cannot on its own explain why Mimi retains roughly three quarters of arousal and
under a third of stance.

This script asks the question that can. For each rung of the pipeline, and for
each cue group, how well can the cue be recovered from the representation? Ridge
regression from the representation to the eGeMAPS features, cross-validated by
episode, R-squared averaged within each group.

Retention is then expressed against WavLM, which is the continuous ceiling and
Mimi's distillation teacher. If the mechanism holds, voice quality should be
retained along the ladder and dynamics should not, since voice quality is what
arousal is made of and dynamics are what stance is made of.

This replaces an interpretation with a measurement. It is the second step of the
[Ch.6] programme, run rather than proposed.

Usage:  python3 src/30_cue_retention.py
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
FEAT = ROOT / "features"
OUT = ROOT / "results" / "cue_retention.txt"
CLASSES = ("affiliative", "neutral", "adversarial")
ALPHAS = (1.0, 10.0, 100.0, 1000.0, 10000.0)

GROUPS = {
    "contour (dynamics)":   [1, 5, 6, 7, 8, 9, 11, 15, 16, 17, 18, 19],
    "level (means)":        [0, 2, 3, 4, 10, 12, 13, 14, 87],
    "voice quality":        list(range(30, 40)),
    "temporal (rate)":      list(range(81, 87)),
    "spectral and formant": list(range(20, 30)) + list(range(40, 81)),
}
CARRIES = {"contour (dynamics)": "stance", "voice quality": "arousal",
           "level (means)": "both weakly", "temporal (rate)": "neither",
           "spectral and formant": "both, not size-comparable"}

RUNGS = [
    ("WavLM (teacher, ceiling)", "wavlm",            "W2_segment", 20),
    ("Mimi, pre-quantisation",   "mimi_pre_meanstd", "W2_segment", None),
    ("Mimi, post-quantisation",  "mimi_post",        "W2_segment", None),
    ("Mimi, deployed histogram", "mimi",             "W2_segment", None),
    ("DAC, pre-quantisation",    "dac_pre",          "W2_segment", None),
    ("DAC, post-quantisation",   "dac_post",         "W2_segment", None),
]


def manifest():
    src = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
    return {r["candidate_id"]: r for r in csv.DictReader(open(src, newline=""))
            if r.get("stance", "").strip() in CLASSES}


def load(feat_dir, key, layer, order):
    p = FEAT / feat_dir / f"{key}.npz"
    if not p.exists():
        return None
    d = np.load(p, allow_pickle=True)
    ids, X = list(d["ids"]), d["X"]
    if layer is not None:
        X = X[:, layer, :]
    X = X.reshape(len(ids), -1)
    idx = {c: i for i, c in enumerate(ids)}
    if any(c not in idx for c in order):
        return None
    return X[[idx[c] for c in order]]


def group_r2(Xrep, Y, g, cols):
    """Mean cross-validated R-squared over the features in one cue group."""
    scores = []
    pipe = make_pipeline(StandardScaler(), RidgeCV(alphas=ALPHAS))
    for c in cols:
        y = Y[:, c]
        if np.std(y) < 1e-9:
            continue
        pred = cross_val_predict(pipe, Xrep, y, groups=g, cv=GroupKFold(n_splits=5))
        scores.append(r2_score(y, pred))
    return float(np.mean(scores)) if scores else float("nan")


def main():
    man = manifest()
    eg = np.load(FEAT / "egemaps" / "W2_segment.npz", allow_pickle=True)
    order = [c for c in list(eg["ids"]) if c in man]
    pos = {c: i for i, c in enumerate(list(eg["ids"]))}
    Y = eg["X"][[pos[c] for c in order]]
    g = np.array([man[c]["episode_id"] for c in order])

    lines = []
    def emit(s=""):
        print(s, flush=True); lines.append(s)

    emit("WHICH CUES DOES THE CODEC LOSE?")
    emit("Ridge from each representation to each eGeMAPS feature, cross-validated by")
    emit("episode, R-squared averaged within cue group. Retention is the fraction of")
    emit("WavLM's R-squared, WavLM being the continuous ceiling and Mimi's teacher.")
    emit(f"{len(order)} clips.")
    emit("=" * 96)

    table = {}
    for name, d, k, layer in RUNGS:
        X = load(d, k, layer, order)
        if X is None:
            emit(f"{name}: features missing or misaligned")
            continue
        table[name] = {gn: group_r2(X, Y, g, cols) for gn, cols in GROUPS.items()}
        emit(f"  computed {name}")

    ceil = table.get("WavLM (teacher, ceiling)")
    emit()
    emit("ABSOLUTE, mean cross-validated R-squared")
    emit(f"{'representation':28}" + "".join(f"{gn.split(' (')[0]:>19}" for gn in GROUPS))
    for name in table:
        emit(f"{name:28}" + "".join(f"{table[name][gn]:>19.3f}" for gn in GROUPS))

    if ceil:
        emit()
        emit("RETENTION, as a fraction of WavLM")
        emit(f"{'representation':28}" + "".join(f"{gn.split(' (')[0]:>19}" for gn in GROUPS))
        for name in table:
            if name == "WavLM (teacher, ceiling)":
                continue
            row = f"{name:28}"
            for gn in GROUPS:
                c, v = ceil[gn], table[name][gn]
                row += f"{(v / c if c > 0 else float('nan')):>18.0%} "
            emit(row)

    emit()
    emit(f"{'cue group':28}{'carries':>28}")
    for gn, what in CARRIES.items():
        emit(f"{gn:28}{what:>28}")
    emit()
    emit("Read: the mechanism in [5.4] requires the group carrying arousal to be")
    emit("retained along the ladder and the group carrying stance to be lost. If both")
    emit("are retained equally, the asymmetry in what the codec keeps is not explained")
    emit("by which cues it keeps, and some other account is needed.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
