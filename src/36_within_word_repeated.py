#!/usr/bin/env python3
"""
The lexical control, recomputed under repeated episode-to-fold partitions.

This is the enabling move of the study. Holding the word constant and varying only
delivery is what separates loss of meaning from loss of sound, so the figures it
produces carry more weight than any other table. They were also, until now, the
least robustly measured ones in the paper.

Each phrase is probed separately on its two commonest stances, so the cells hold
68 to 127 clips rather than 873. src/32 and src/34 established that fold
assignment alone contributes sd 0.010 at full sample size, and that noise grows as
cells shrink. src/18 reports these on a single partition through GroupKFold, whose
assignment is scikit-learn version dependent.

This repeats the same analysis over 25 partitions defined in src/34 and reports a
mean with an sd, both per phrase and averaged over phrases. The averaged figure
should be the more stable of the two, since averaging eight independent estimates
suppresses partition noise, and the per-phrase figures should carry visibly wider
intervals. Reporting both makes that visible rather than implied.

Contrast selection follows src/18 per_phrase_binary exactly: the two commonest
stances within the phrase, requiring at least 8 in the minority class.

Usage:  python3 src/36_within_word_repeated.py
"""
import csv, importlib.util, sys, warnings
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
FEAT = ROOT / "features"
SHEET = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
OUT = ROOT / "results" / "within_word_repeated.txt"
CLASSES = ("affiliative", "neutral", "adversarial")
N_REP = 25
MIN_MINORITY = 8

sys.path.insert(0, str(Path(__file__).resolve().parent))
_tp = importlib.util.spec_from_file_location("tp", Path(__file__).parent / "34_timing_probe.py")
TP = importlib.util.module_from_spec(_tp); _tp.loader.exec_module(TP)

# (display name, features dir, key, layer)
REPS = [
    ("Whisper encoder L9",        "whisper",   "W2_segment",  9),
    ("WavLM L20",                 "wavlm",     "W2_segment", 20),
    ("Mimi, before quantisation", "mimi_pre",  "W2_segment", None),
    ("Mimi, after quantisation",  "mimi_post", "W2_segment", None),
    ("eGeMAPS, 88 functionals",   "egemaps",   "W2_segment", None),
    ("Text, discourse context",   "text",      "context",    None),
    ("Mimi, deployed histogram",  "mimi",      "W2_segment", None),
]


def manifest():
    return {r["candidate_id"]: r for r in csv.DictReader(open(SHEET, newline=""))
            if r.get("stance", "").strip() in CLASSES}


def load(d, key, layer):
    z = np.load(FEAT / d / f"{key}.npz", allow_pickle=True)
    X = z["X"]
    if layer is not None:
        X = X[:, layer, :]
    return X.reshape(len(z["ids"]), -1), [str(c) for c in z["ids"]]


def phrase_of(row):
    """candidate_id encodes the phrase after the final underscore-separated index."""
    return row.get("target_phrase") or row["candidate_id"].rsplit("_", 1)[-1]


def main():
    man = manifest()
    lines = []
    def emit(s=""):
        print(s, flush=True); lines.append(s)

    emit("LEXICAL CONTROL, REPEATED PARTITIONS")
    emit(f"Within each phrase, binary contrast between its two commonest stances,")
    emit(f"exactly as src/18 per_phrase_binary. Mean over {N_REP} partitions with sd.")
    emit("Cells hold 68 to 127 clips against 873 for the pooled tables, so partition")
    emit("noise is expected to be larger here than the sd 0.010 measured at full size.")
    emit("=" * 86)

    summary = []
    for label, d, key, layer in REPS:
        try:
            X, ids = load(d, key, layer)
        except Exception as e:
            emit(f"\n{label}: unavailable ({type(e).__name__})"); continue
        idx = {c: i for i, c in enumerate(ids)}
        rows = [(c, r) for c, r in man.items() if c in idx]
        ph = np.array([phrase_of(r) for _, r in rows])
        y_all = np.array([r["stance"] for _, r in rows])
        g_all = np.array([r["episode_id"] for _, r in rows])
        Xk = X[[idx[c] for c, _ in rows]]

        emit(f"\n{label}")
        emit(f"  {'phrase':10}{'contrast':14}{'n':>5}{'F1':>8}{'sd':>7}{'min':>7}{'max':>7}")
        per_phrase = []
        for phrase in sorted(set(ph)):
            sel = ph == phrase
            yy = y_all[sel]
            top2 = [c for c, _ in Counter(yy).most_common(2)]
            if len(top2) < 2:
                continue
            keep = np.isin(yy, top2)
            Xp, yp, gp = Xk[sel][keep], yy[keep], g_all[sel][keep]
            if min(Counter(yp).values()) < MIN_MINORITY:
                continue
            R = TP.repeated_f1(np.nan_to_num(Xp.astype(np.float32)), yp, gp, N_REP)
            R = R[~np.isnan(R)]
            if len(R) == 0:
                continue
            per_phrase.append(R)
            tag = "/".join(c[:3] for c in top2)
            emit(f"  {phrase:10}{tag:14}{len(yp):>5}{R.mean():>8.3f}{R.std():>7.3f}"
                 f"{R.min():>7.3f}{R.max():>7.3f}")
        if per_phrase:
            # mean over phrases, computed per partition so the sd is the sd of the
            # reported quantity rather than a pooled sd of the individual cells
            M = np.mean(np.stack(per_phrase), axis=0)
            summary.append((label, M.mean(), M.std(),
                            float(np.mean([r.std() for r in per_phrase]))))
            emit(f"  {'MEAN':10}{'':14}{'':>5}{M.mean():>8.3f}{M.std():>7.3f}"
                 f"{M.min():>7.3f}{M.max():>7.3f}")

    emit()
    emit("=" * 86)
    emit("SUMMARY, mean over phrases")
    emit(f"{'representation':30}{'F1':>8}{'sd':>8}{'mean per-phrase sd':>22}")
    for label, m, s, ps in sorted(summary, key=lambda r: -r[1]):
        emit(f"{label:30}{m:>8.3f}{s:>8.3f}{ps:>22.3f}")
    emit()
    emit("Read: the third column is how much an individual phrase cell moves with the")
    emit("partition, and the second is how much the averaged figure moves. If the third")
    emit("is much larger than the second, individual phrase figures should not be read")
    emit("as orderings and only the mean should carry weight.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
