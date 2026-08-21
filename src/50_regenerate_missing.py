#!/usr/bin/env python3
"""Regenerate the Chapter 4 figures that were printed but never saved.

A numerical audit traced every cell of the eight Chapter 4 tables back to the results
file that produced it. Two groups had no file behind them. Ten of the fifteen
permutation nulls in Table 4.2 came from src/41 and src/42, which print to the terminal
and write nothing, and EnCodec's two order effects in Table 4.6 came from an ad hoc run
because encodec_pre and encodec_post are not in src/34's CORE list. The figures were
reproducible in principle, since the scripts exist, but nothing on disk recorded them.

This recomputes both groups with the machinery they were originally produced by, imported
from src/34 rather than reimplemented, and writes the result to results/. Where a figure
differs from what the draft prints, the difference is reported rather than silently
adopted, because a regeneration that quietly changes the paper is worse than no
regeneration at all.

Usage:  python3 src/50_regenerate_missing.py
        python3 src/50_regenerate_missing.py --perm 10      (quick check)
"""
import argparse
import csv
import importlib.util
import sys
import warnings
from pathlib import Path

import numpy as np
from joblib import Parallel, delayed

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

_spec = importlib.util.spec_from_file_location("tp", ROOT / "src" / "34_timing_probe.py")
TP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TP)

OUT = ROOT / "results" / "regenerated_nulls_and_encodec.txt"
CLASSES = ("affiliative", "neutral", "adversarial")

# What the draft currently prints, so any drift is visible rather than assumed away.
DRAFT_NULL = {
    "WavLM L20": (0.557, 0.330), "Whisper encoder L9": (0.548, 0.333),
    "Mimi, before quantisation": (0.468, 0.329), "Mimi, deployed histogram": (0.371, 0.311),
    "eGeMAPS, 88 functionals": (0.420, 0.324),
    "Text, target word only": (0.493, 0.313), "Mimi, after quantisation": (0.441, 0.337),
    "DAC, before quantisation": (0.404, 0.336), "DAC, after quantisation": (0.381, 0.331),
    "EnCodec, before quantisation": (0.396, 0.326), "EnCodec, after quantisation": (0.400, 0.328),
    "Text, with discourse context": (0.394, 0.333), "Sylber": (0.446, 0.328),
    "DyCAST, before quantisation": (0.401, 0.320), "DyCAST, after quantisation": (0.403, 0.317),
}
DRAFT_ORDER = {"EnCodec, before quantisation": (0.033, 0.017, 9.8),
               "EnCodec, after quantisation": (0.063, 0.021, 15.0)}


def manifest():
    src = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
    return {r["candidate_id"]: r for r in csv.DictReader(open(src, newline=""))
            if r.get("stance", "").strip() in CLASSES}


def pooled(d, key="W2_segment", layer=None):
    z = np.load(ROOT / "features" / d / f"{key}.npz", allow_pickle=True)
    X = z["X"]
    if layer is not None:
        X = X[:, layer, :]
    return X.reshape(len(z["ids"]), -1), [str(c) for c in z["ids"]]


def frames_pooled(d):
    st = ROOT / "features_frames" / d / "W2_segment"
    X = np.load(f"{st}.X.npy", mmap_mode="r")
    L = np.load(f"{st}.lengths.npy")
    ids = [str(c) for c in np.load(f"{st}.ids.npy", allow_pickle=True)]
    rows = []
    for i in range(len(ids)):
        F = np.asarray(X[i, :max(int(L[i]), 1)], dtype=np.float64)
        rows.append(np.concatenate([F.mean(0), F.std(0)]))
    return np.stack(rows), ids


# All fifteen rows of Table 4.2, so the table has one provenance rather than three.
# The five from controls_repeated.txt are recomputed too, since mixing a 50-shuffle
# estimate with a 200-shuffle one in the same column would be worse than either.
JOBS = [
    ("WavLM L20", lambda: pooled("wavlm", "W2_segment", 20)),
    ("Whisper encoder L9", lambda: pooled("whisper", "W2_segment", 9)),
    ("Mimi, before quantisation", lambda: pooled("mimi_pre_meanstd")),
    ("Mimi, deployed histogram", lambda: pooled("mimi")),
    ("eGeMAPS, 88 functionals", lambda: pooled("egemaps")),
    ("Text, target word only", lambda: pooled("text", "targetonly")),
    ("Mimi, after quantisation", lambda: pooled("mimi_post")),
    ("Sylber", lambda: frames_pooled("sylber")),
    ("DyCAST, before quantisation", lambda: frames_pooled("dycast_pre")),
    ("DyCAST, after quantisation", lambda: frames_pooled("dycast_post")),
    ("EnCodec, before quantisation", lambda: frames_pooled("encodec_pre")),
    ("EnCodec, after quantisation", lambda: frames_pooled("encodec_post")),
    ("DAC, before quantisation", lambda: pooled("dac_pre")),
    ("DAC, after quantisation", lambda: pooled("dac_post")),
    ("Text, with discourse context", lambda: pooled("text", "context")),
]


def align(X, ids, man):
    keep = [i for i, c in enumerate(ids) if c in man]
    X = np.nan_to_num(np.asarray(X)[keep].astype(np.float32))
    y = np.array([man[ids[i]]["stance"] for i in keep])
    g = np.array([man[ids[i]]["episode_id"] for i in keep])
    return X, y, g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perm", type=int, default=200)
    ap.add_argument("--reps", type=int, default=25)
    args = ap.parse_args()

    man = manifest()
    lines = []
    def emit(s=""):
        print(s, flush=True)
        lines.append(s)

    emit("REGENERATED FIGURES, previously printed but not saved")
    emit(f"{args.reps} partitions from src/34's _partition, {args.perm} label shuffles per null,")
    emit("all scoring imported from src/34 rather than reimplemented.")
    emit("=" * 92)
    emit()
    emit("A. PERMUTATION NULLS, the ten in Table 4.2 not in results/controls_repeated.txt")
    emit(f"{'representation':32}{'dims':>7}{'macroF1':>9}{'null':>8}{'margin':>9}   {'vs draft':>16}")

    drift, ses = [], []
    rng = np.random.default_rng(0)
    for label, fn in JOBS:
        X, ids = fn()
        X, y, g = align(X, ids, man)
        R = TP.repeated_f1(X, y, g, args.reps)
        fold = TP._partition(g, 0)
        sc = np.array(Parallel(n_jobs=-1)(
            delayed(TP._score_partition)(X, rng.permutation(y), fold) for _ in range(args.perm)))
        null = float(sc.mean())
        se = float(sc.std(ddof=1) / np.sqrt(len(sc)))
        ses.append(se)
        f1, margin = float(R.mean()), float(R.mean()) - null
        d_f1, d_null = DRAFT_NULL[label]
        note = "matches"
        if abs(f1 - d_f1) > 0.0005 or abs(null - d_null) > 0.0005:
            note = f"F1 {f1 - d_f1:+.3f} null {null - d_null:+.3f}"
            drift.append((label, "null", f1 - d_f1, null - d_null))
        emit(f"{label:32}{X.shape[1]:>7}{f1:>9.3f}{null:>8.3f}{margin:>+9.3f}   {note:>16}")

    emit()
    emit(f"   Monte Carlo standard error of the null, across the {args.perm} shuffles: "
         f"mean {np.mean(ses):.4f}, worst {max(ses):.4f}. Margins are meaningful to about "
         f"{2*max(ses):.3f}.")
    emit()
    emit("B. ORDER EFFECT for EnCodec, absent from src/34's CORE list")
    emit(f"{'representation':32}{'real':>8}{'shuffled':>10}{'order':>8}{'sd':>7}{'t':>7}   {'vs draft':>14}")
    for rep, label in (("encodec_pre", "EnCodec, before quantisation"),
                       ("encodec_post", "EnCodec, after quantisation")):
        Xr, ids = TP.build(rep, "basis8", shuffle=False)
        Xs, _ = TP.build(rep, "basis8", shuffle=True, rng=np.random.default_rng(TP.SEED))
        Xr, y, g = align(Xr, ids, man)
        Xs, _, _ = align(Xs, ids, man)
        Rr = TP.repeated_f1(Xr, y, g, args.reps)
        Rs = TP.repeated_f1(Xs, y, g, args.reps)
        dd = Rr - Rs
        t = dd.mean() / (dd.std(ddof=1) / np.sqrt(len(dd)))
        d_o, d_sd, d_t = DRAFT_ORDER[label]
        note = "matches"
        if abs(dd.mean() - d_o) > 0.0015:
            note = f"{dd.mean() - d_o:+.3f}"
            drift.append((label, "order", dd.mean() - d_o, 0.0))
        emit(f"{label:32}{Rr.mean():>8.3f}{Rs.mean():>10.3f}{dd.mean():>+8.3f}"
             f"{dd.std():>7.3f}{t:>7.1f}   {note:>14}")

    emit()
    emit("=" * 92)
    if drift:
        emit(f"{len(drift)} figure(s) differ from what the draft prints:")
        for label, kind, a, b in drift:
            emit(f"   {label}, {kind}: {a:+.3f} {b:+.3f}")
        emit("The draft has not been changed. Decide per figure.")
    else:
        emit("Every regenerated figure reproduces what the draft prints.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
