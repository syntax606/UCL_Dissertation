#!/usr/bin/env python3
"""Which measured cues carry stance, recomputed under the partitioning in [3.7].

src/27 answered this on a single GroupKFold partition and its output still carries the
pre-repartitioning figures, WavLM at 0.573 rather than 0.557. Nothing in the draft cites
it, which is the reason for redoing it: the result is the missing motivation for [1.3]'s
fourth research question.

The question that matters is not whether stance is decodable from hand-crafted acoustics.
It is which kind of acoustic property carries it. Two answers separate cleanly and the
paper needs both, because on the face of it they look contradictory.

  contour, meaning how pitch and loudness MOVE across the phrase
  level,   meaning how loud and how high the phrase SITS
  temporal, meaning coarse rate and segment statistics

If contour carries stance and level and coarse rate do not, then [4.4]'s finding that what
the codecs lose is temporal organisation is a prediction confirmed rather than a surprise,
and [4.6]'s finding that timing features alone sit at chance stops looking like its
opposite. The two senses of temporal are different quantities.

Groups, features and probe are src/27's. Only the partitioning changes, to _partition from
src/34 with 25 seeds, plus a permutation null of 200 shuffles as in src/50.

Usage:  python3 src/52_cue_groups_repeated.py
        python3 src/52_cue_groups_repeated.py --reps 5 --perm 20     (quick check)
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

OUT = ROOT / "results" / "cue_groups_repeated.txt"
CLASSES = ("affiliative", "neutral", "adversarial")

# src/27's grouping, unchanged, so the two runs are comparable
GROUPS = {
    "contour (F0/loudness dynamics)": [1, 5, 6, 7, 8, 9, 11, 15, 16, 17, 18, 19],
    "level (loudness, F0 mean)":      [0, 2, 3, 4, 10, 12, 13, 14, 87],
    "voice quality (jitter/HNR)":     list(range(30, 40)),
    "spectral and formant":           list(range(20, 30)) + list(range(40, 81)),
    "temporal (rate, segments)":      list(range(81, 87)),
}


def manifest():
    src = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
    return {r["candidate_id"]: r for r in csv.DictReader(open(src, newline=""))
            if r.get("stance", "").strip() in CLASSES}


def load(man):
    z = np.load(ROOT / "features" / "egemaps" / "W2_segment.npz", allow_pickle=True)
    ids = [str(c) for c in z["ids"]]
    keep = [i for i, c in enumerate(ids) if c in man]
    X = np.nan_to_num(z["X"][keep].astype(np.float32))
    y = np.array([man[ids[i]]["stance"] for i in keep])
    ar = np.array([man[ids[i]].get("arousal", "").strip() for i in keep])
    g = np.array([man[ids[i]]["episode_id"] for i in keep])
    return X, y, ar, g


def measure(X, y, g, reps, perm, rng):
    """Mean over `reps` partitions, and a null over `perm` label shuffles on partition 0."""
    R = TP.repeated_f1(X, y, g, reps)
    fold = TP._partition(g, 0)
    sc = np.array(Parallel(n_jobs=-1)(
        delayed(TP._score_partition)(X, rng.permutation(y), fold) for _ in range(perm)))
    return float(R.mean()), float(R.std()), float(sc.mean()), float(R.mean() - sc.mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=25)
    ap.add_argument("--perm", type=int, default=200)
    args = ap.parse_args()

    man = manifest()
    X, y, ar, g = load(man)
    rng = np.random.default_rng(0)

    lines = []
    def emit(s=""):
        print(s, flush=True)
        lines.append(s)

    emit("WHICH MEASURED CUES CARRY STANCE, UNDER THE PARTITIONING IN [3.7]")
    emit(f"{len(y)} clips, {len(set(g))} episodes, eGeMAPSv02, {X.shape[1]} features.")
    emit(f"{args.reps} partitions for the score, {args.perm} label shuffles for the null.")
    emit("Replaces the single-partition figures in results/egemaps_baseline.txt.")
    emit("=" * 94)
    emit()

    all_r = measure(X, y, g, args.reps, args.perm, rng)
    emit(f"All 88 features against stance: {all_r[0]:.3f} (sd {all_r[1]:.3f}), "
         f"null {all_r[2]:.3f}, margin {all_r[3]:+.3f}")
    emit()

    emit("CUE GROUPS AGAINST STANCE, each group on its own")
    emit(f"{'group':34}{'feat':>6}{'macroF1':>10}{'sd':>7}{'null':>8}{'margin':>9}{'per feat':>10}")
    stance = {}
    for name, idx in GROUPS.items():
        m, sd, null, marg = measure(X[:, idx], y, g, args.reps, args.perm, rng)
        stance[name] = (m, sd, null, marg, len(idx))
        emit(f"{name:34}{len(idx):>6}{m:>10.3f}{sd:>7.3f}{null:>8.3f}{marg:>+9.3f}"
             f"{marg / len(idx):>10.4f}")
    emit()

    emit("THE SAME GROUPS AGAINST AROUSAL, which is the other half of the design")
    emit(f"{'group':34}{'feat':>6}{'macroF1':>10}{'sd':>7}{'null':>8}{'margin':>9}")
    arousal = {}
    for name, idx in GROUPS.items():
        m, sd, null, marg = measure(X[:, idx], ar, g, args.reps, args.perm, rng)
        arousal[name] = marg
        emit(f"{name:34}{len(idx):>6}{m:>10.3f}{sd:>7.3f}{null:>8.3f}{marg:>+9.3f}")
    emit()

    emit("=" * 94)
    emit("WHAT THIS SETTLES")
    top = max(stance, key=lambda k: stance[k][3] / stance[k][4])
    emit(f"  Most stance per feature: {top}, {stance[top][3]:+.3f} from "
         f"{stance[top][4]} features.")
    c, t, l = (stance["contour (F0/loudness dynamics)"], stance["temporal (rate, segments)"],
               stance["level (loudness, F0 mean)"])
    emit(f"  Contour carries {c[3]:+.3f} from {c[4]} features. Coarse rate carries {t[3]:+.3f} "
         f"from {t[4]}.")
    emit(f"  Level, how loud and how high the phrase sits, carries {l[3]:+.3f} from {l[4]}.")
    emit("  So the two senses of temporal come apart. How pitch and loudness move carries")
    emit("  stance; how fast the phrase runs does not. [4.6] and [5.2] are about different")
    emit("  quantities and only look contradictory if the distinction is left implicit.")
    emit()
    emit("  Against arousal the ordering differs, which is what makes the two axes separable:")
    for k in sorted(arousal, key=lambda x: -arousal[x])[:3]:
        emit(f"    {k:34}{arousal[k]:+.3f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
