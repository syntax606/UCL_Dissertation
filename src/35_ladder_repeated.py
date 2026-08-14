#!/usr/bin/env python3
"""
The quantisation ladder, recomputed under repeated episode-to-fold partitions.

Move 1 of the argument, that the loss sits at the encoder rather than the
quantiser, currently rests on src/19 and src/21. Both score a single partition
through GroupKFold, whose assignment changed between scikit-learn 1.7 and 1.9 and
which src/32 and src/34 showed contributes sd 0.010 with range up to 0.06 on its
own. The claim is not in danger, since the two costs differ by roughly 0.08, but
the paper should not report its spine on a weaker measurement than its later
sections use.

This recomputes the ladder the way src/34 does everything else: partitions defined
here rather than delegated, 25 of them, mean and sd reported. It runs off the
POOLED features in features/, which are mean-and-std already and are exactly what
the ladder needs, so no GPU and no frame extraction.

EnCodec is included because src/31 now extracts it and it completes the
architectural comparison: DAC has no temporal mechanism, EnCodec has an LSTM,
Mimi has self-attention.

Usage:  python3 src/35_ladder_repeated.py
"""
import csv, importlib.util, sys, warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
FEAT = ROOT / "features"
SHEET = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
OUT = ROOT / "results" / "ladder_repeated.txt"
CLASSES = ("affiliative", "neutral", "adversarial")
N_REP = 25

sys.path.insert(0, str(Path(__file__).resolve().parent))
_tp = importlib.util.spec_from_file_location("tp", Path(__file__).parent / "34_timing_probe.py")
TP = importlib.util.module_from_spec(_tp); _tp.loader.exec_module(TP)

# (label, source, how to get a meanstd vector). Frame sources are pooled here so
# every rung is measured the same way.
RUNGS = [
    ("WavLM L20, continuous teacher", "pooled", ("wavlm", 20)),
    ("Mimi, pre-quantisation",        "pooled", ("mimi_pre", None)),
    ("Mimi, post-quantisation",       "pooled", ("mimi_post", None)),
    ("Mimi, deployed histogram",      "pooled", ("mimi", None)),
    ("DAC, pre-quantisation",         "pooled", ("dac_pre", None)),
    ("DAC, post-quantisation",        "pooled", ("dac_post", None)),
    ("EnCodec, pre-quantisation",     "frames", ("encodec_pre", None)),
    ("EnCodec, post-quantisation",    "frames", ("encodec_post", None)),
]


def manifest():
    return {r["candidate_id"]: r for r in csv.DictReader(open(SHEET, newline=""))
            if r.get("stance", "").strip() in CLASSES}


def load_pooled(name, layer):
    z = np.load(FEAT / name / "W2_segment.npz", allow_pickle=True)
    X = z["X"]
    if layer is not None:
        X = X[:, layer, :]
    return X.reshape(len(z["ids"]), -1), [str(c) for c in z["ids"]]


def load_frames_pooled(name):
    """meanstd over the real frames, so it is the same summary as features/."""
    d = TP.load(name)
    X, L, ids = d if isinstance(d, tuple) else (d["X"], d["lengths"], d["ids"])
    rows = []
    for i in range(len(ids)):
        F = np.asarray(X[i, :int(L[i])], dtype=np.float64)
        rows.append(np.concatenate([F.mean(0), F.std(0)]))
    return np.stack(rows), [str(c) for c in ids]


def main():
    man = manifest()
    lines = []
    def emit(s=""):
        print(s, flush=True); lines.append(s)

    emit("QUANTISATION LADDER, REPEATED PARTITIONS")
    emit(f"Mean over {N_REP} independent episode-to-fold partitions, with sd. Partitions")
    emit("are defined in src/34 rather than by GroupKFold, whose assignment changed")
    emit("between scikit-learn 1.7 and 1.9. Compare against src/19 and src/21, which")
    emit("report a single partition each.")
    emit("=" * 78)
    emit(f"{'rung':34}{'macroF1':>9}{'sd':>7}{'min':>8}{'max':>8}")

    got = {}
    for label, kind, (name, layer) in RUNGS:
        try:
            X, ids = (load_pooled(name, layer) if kind == "pooled"
                      else load_frames_pooled(name))
        except Exception as e:
            emit(f"{label:34}  unavailable ({type(e).__name__})"); continue
        keep = [i for i, c in enumerate(ids) if c in man]
        X = np.nan_to_num(X[keep].astype(np.float32))
        y = np.array([man[ids[i]]["stance"] for i in keep])
        g = np.array([man[ids[i]]["episode_id"] for i in keep])
        R = TP.repeated_f1(X, y, g, N_REP)
        got[label] = R
        emit(f"{label:34}{R.mean():>9.3f}{R.std():>7.3f}{R.min():>8.3f}{R.max():>8.3f}")

    emit()
    emit("STEP COSTS, paired on partitions so partition noise cancels")
    emit(f"{'step':46}{'cost':>8}{'sd':>7}{'t':>7}")
    steps = [("encoder, WavLM to Mimi pre", "WavLM L20, continuous teacher", "Mimi, pre-quantisation"),
             ("quantiser, Mimi pre to post", "Mimi, pre-quantisation", "Mimi, post-quantisation"),
             ("readout, Mimi post to histogram", "Mimi, post-quantisation", "Mimi, deployed histogram"),
             ("encoder, WavLM to DAC pre", "WavLM L20, continuous teacher", "DAC, pre-quantisation"),
             ("quantiser, DAC pre to post", "DAC, pre-quantisation", "DAC, post-quantisation"),
             ("encoder, WavLM to EnCodec pre", "WavLM L20, continuous teacher", "EnCodec, pre-quantisation"),
             ("quantiser, EnCodec pre to post", "EnCodec, pre-quantisation", "EnCodec, post-quantisation")]
    for label, a, b in steps:
        if a not in got or b not in got:
            continue
        d = got[a] - got[b]
        sd = d.std(ddof=1)
        t = d.mean() / (sd / np.sqrt(len(d))) if sd > 0 else float("nan")
        emit(f"{label:46}{d.mean():>+8.3f}{sd:>7.3f}{t:>7.1f}")

    emit()
    emit("Read: a positive cost means the step loses stance. The claim in [Ch.4] is")
    emit("that the encoder step is the larger one and that this replicates across")
    emit("codecs of independent design. Costs here are paired across partitions, so")
    emit("their sd is the scale to judge them against, not the sd of either rung.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
