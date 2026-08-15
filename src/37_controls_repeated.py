#!/usr/bin/env python3
"""
The controls in [4.6], and the permutation nulls, under repeated partitions.

Two things were left inconsistent by the move to the partition scheme in [3.7].

The speaker and arousal controls in Chapter 4 were carried over from src/18 and
report baselines of 0.573, 0.564 and 0.381, which are the single-partition figures.
Table 4.1 now reports 0.557, 0.548 and 0.371, so a reader comparing the two finds
three mismatches in one sentence. Both sides of a control have to be measured the
same way or the comparison means nothing.

And the empirical permutation null was never recomputed under the new partitioning.
Chapter 4 asserts it sits "near 0.33 in every configuration tested", which is
carried from src/18. That matters because the codebook analysis reports margins
against a null of roughly 0.31 for the Mimi histogram, and a margin of +0.071 against
a pooled figure of 0.371 only reconciles if the null for that configuration really is
lower. This measures it rather than assuming it.

Usage:  python3 src/37_controls_repeated.py
        python3 src/37_controls_repeated.py --perm 50
"""
import argparse, csv, importlib.util, sys, warnings
from pathlib import Path

import numpy as np
from joblib import Parallel, delayed
from sklearn.metrics import f1_score

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
FEAT = ROOT / "features"
SHEET = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
OUT = ROOT / "results" / "controls_repeated.txt"
CLASSES = ("affiliative", "neutral", "adversarial")
N_REP = 25

sys.path.insert(0, str(Path(__file__).resolve().parent))
_tp = importlib.util.spec_from_file_location("tp", Path(__file__).parent / "34_timing_probe.py")
TP = importlib.util.module_from_spec(_tp); _tp.loader.exec_module(TP)

REPS = [("WavLM L20", "wavlm", 20), ("Whisper enc L9", "whisper", 9),
        ("Mimi, deployed tokens", "mimi", None), ("Mimi, pre-quantisation", "mimi_pre", None),
        ("eGeMAPS", "egemaps", None)]


def rows():
    return [r for r in csv.DictReader(open(SHEET, newline=""))
            if r.get("stance", "").strip() in CLASSES]


def load(d, layer):
    z = np.load(FEAT / d / "W2_segment.npz", allow_pickle=True)
    X = z["X"]
    if layer is not None:
        X = X[:, layer, :]
    return X.reshape(len(z["ids"]), -1), [str(c) for c in z["ids"]]


def aligned(d, layer, man):
    X, ids = load(d, layer)
    keep = [i for i, c in enumerate(ids) if c in man]
    return (np.nan_to_num(X[keep].astype(np.float32)),
            np.array([man[ids[i]]["stance"] for i in keep]),
            np.array([man[ids[i]]["episode_id"] for i in keep]),
            np.array([man[ids[i]]["show_name"] for i in keep]),
            np.array([man[ids[i]]["arousal"] for i in keep]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perm", type=int, default=50)
    args = ap.parse_args()
    man = {r["candidate_id"]: r for r in rows()}

    lines = []
    def emit(s=""):
        print(s, flush=True); lines.append(s)

    emit("CONTROLS AND NULLS UNDER REPEATED PARTITIONS")
    emit(f"Mean over {N_REP} partitions with sd, as [3.7]. Replaces the single-partition")
    emit("figures carried into [4.6] from src/18.")
    emit("=" * 88)

    emit("\nA. SPEAKER CONTROL, folds grouped by show rather than by episode")
    emit(f"{'representation':24}{'by episode':>12}{'sd':>7}{'by show':>10}{'sd':>7}{'change':>9}")
    for label, d, layer in REPS:
        X, y, g, show, ar = aligned(d, layer, man)
        Re = TP.repeated_f1(X, y, g, N_REP)
        Rs = TP.repeated_f1(X, y, show, N_REP)
        emit(f"{label:24}{Re.mean():>12.3f}{Re.std():>7.3f}{Rs.mean():>10.3f}"
             f"{Rs.std():>7.3f}{Rs.mean()-Re.mean():>+9.3f}")

    emit("\nB. AROUSAL CONTROL, stance decoded within each arousal level")
    emit(f"{'representation':24}{'pooled':>9}{'low':>9}{'sd':>7}{'high':>9}{'sd':>7}")
    for label, d, layer in REPS:
        X, y, g, show, ar = aligned(d, layer, man)
        Rp = TP.repeated_f1(X, y, g, N_REP)
        out = [Rp.mean()]
        for lv in ("low", "high"):
            s = ar == lv
            R = TP.repeated_f1(X[s], y[s], g[s], N_REP)
            R = R[~np.isnan(R)]
            out += [R.mean(), R.std()]
        emit(f"{label:24}{out[0]:>9.3f}{out[1]:>9.3f}{out[2]:>7.3f}{out[3]:>9.3f}{out[4]:>7.3f}")

    if args.perm:
        emit(f"\nC. EMPIRICAL PERMUTATION NULL, {args.perm} label shuffles per configuration,")
        emit("   each scored on one partition, so the null is measured the same way the")
        emit("   score is. Chapter 4 asserts 'near 0.33 in every configuration'.")
        emit(f"{'representation':24}{'dims':>7}{'score':>9}{'null':>8}{'margin':>9}")
        rng = np.random.default_rng(0)
        for label, d, layer in REPS:
            X, y, g, show, ar = aligned(d, layer, man)
            R = TP.repeated_f1(X, y, g, N_REP)
            fold = TP._partition(g, 0)
            null = np.mean(Parallel(n_jobs=-1)(
                delayed(TP._score_partition)(X, rng.permutation(y), fold)
                for _ in range(args.perm)))
            emit(f"{label:24}{X.shape[1]:>7}{R.mean():>9.3f}{null:>8.3f}"
                 f"{R.mean()-null:>+9.3f}")
        emit("\n   Read: if the null varies materially by configuration, the claim that it")
        emit("   sits near 0.33 everywhere is too strong, and margins reported against a")
        emit("   single assumed null do not reconcile with margins reported per config.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
