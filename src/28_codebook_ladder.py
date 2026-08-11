#!/usr/bin/env python3
"""
Does the acoustic stack add anything to the distilled codebook, or not?

View H of src/18_probe.py probes each of Mimi's eight codebooks alone, then all
eight together, then codebooks 1 to 7 without the distilled one. That gives point
estimates, and the claim in [4.5] that the acoustic stack adds nothing to codebook
0 currently rests on comparing two of them, 0.402 against 0.381.

A cumulative ladder is harder to argue with. Probing CB0, then CB0-1, CB0-2, and
so on to CB0-7, shows how margin accumulates as codebooks are added. If the curve
is flat from the first codebook, nothing the acoustic stack contributes is
recoverable by a probe. If it rises anywhere, that is worth knowing and the
current claim is too strong.

The reverse direction is also run, adding codebooks from the last one backwards,
which separates "codebook 0 is sufficient" from "any single codebook would do".

Features already exist. The Mimi histogram is 8 codebooks of 2,048 bins each,
concatenated, so the slices are exact.

Usage:  python3 src/28_codebook_ladder.py [--perm 200]
"""
import argparse, csv, warnings
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
OUT = ROOT / "results" / "codebook_cumulative.txt"
CLASSES = ("affiliative", "neutral", "adversarial")
K = 2048          # bins per codebook
N_CB = 8
RNG = np.random.default_rng(42)


def manifest():
    src = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
    return {r["candidate_id"]: r for r in csv.DictReader(open(src, newline=""))
            if r.get("stance", "").strip() in CLASSES}


def oof(X, y, g):
    ns = min(5, len(set(g)), min(Counter(y).values()))
    if ns < 2:
        return None
    pipe = make_pipeline(StandardScaler(),
                         LogisticRegression(max_iter=3000, C=1.0,
                                            class_weight="balanced"))
    return cross_val_predict(pipe, X, y, groups=g, cv=GroupKFold(n_splits=ns))


def score(X, y, g, perm):
    pred = oof(X, y, g)
    if pred is None:
        return None
    f1 = f1_score(y, pred, average="macro")
    null = [f1_score(yp, pr, average="macro")
            for yp, pr in ((p_, oof(X, p_, g)) for p_ in
                           (RNG.permutation(y) for _ in range(perm)))
            if pr is not None]
    null = np.asarray(null)
    return (f1, float(null.mean()), f1 - float(null.mean()),
            (int((null >= f1).sum()) + 1) / (len(null) + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perm", type=int, default=200)
    args = ap.parse_args()

    man = manifest()
    d = np.load(ROOT / "features" / "mimi" / "W2_segment.npz", allow_pickle=True)
    ids, X = list(d["ids"]), d["X"]
    keep = [i for i, c in enumerate(ids) if c in man]
    meta = [man[ids[i]] for i in keep]
    X = X[keep]
    y = np.array([m["stance"] for m in meta])
    g = np.array([m["episode_id"] for m in meta])
    assert X.shape[1] == K * N_CB, X.shape

    lines = []
    def emit(s=""):
        print(s, flush=True); lines.append(s)

    emit("CUMULATIVE CODEBOOK LADDER, Mimi, three-way stance, W2")
    emit(f"{N_CB} codebooks of {K} bins. Each block probed with its own permutation")
    emit(f"null, {args.perm} permutations. Codebook 0 is the WavLM-distilled stream.")
    emit("=" * 78)
    emit()
    emit("FORWARD, adding codebooks to the distilled one")
    emit(f"{'block':18}{'dims':>7}{'macroF1':>10}{'chance':>9}{'margin':>9}{'p':>8}{'delta':>9}")
    prev = None
    for n in range(1, N_CB + 1):
        r = score(X[:, :K * n], y, g, args.perm)
        tag = "CB0" if n == 1 else f"CB0-{n-1}"
        delta = "" if prev is None else f"{r[2]-prev:>+9.3f}"
        emit(f"{tag:18}{K*n:>7}{r[0]:>10.3f}{r[1]:>9.3f}{r[2]:>+9.3f}{r[3]:>8.3f}{delta}")
        prev = r[2]

    emit()
    emit("REVERSE, adding codebooks from the last one backwards")
    emit(f"{'block':18}{'dims':>7}{'macroF1':>10}{'chance':>9}{'margin':>9}{'p':>8}")
    for n in range(1, N_CB + 1):
        r = score(X[:, K * (N_CB - n):], y, g, args.perm)
        tag = f"CB{N_CB-n}" if n == 1 else f"CB{N_CB-n}-7"
        emit(f"{tag:18}{K*n:>7}{r[0]:>10.3f}{r[1]:>9.3f}{r[2]:>+9.3f}{r[3]:>8.3f}")

    emit()
    emit("Read: if the forward deltas are near zero from CB0-1 onward, the acoustic")
    emit("stack contributes nothing a probe can recover on top of the distilled")
    emit("codebook. The reverse direction separates that from the weaker claim that")
    emit("any single codebook would have served.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
