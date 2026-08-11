#!/usr/bin/env python3
"""
A hand-crafted acoustic baseline, and a direct test of the [Ch.5] cue account.

Three questions this study cannot currently answer.

  1. Is WavLM's margin large? There is no hand-crafted comparison anywhere in the
     study, so a reader cannot tell whether +0.244 beats 88 classical features or
     merely matches them.
  2. Are the arousal labels grounded? Arousal is annotated by the same person in
     the same pass as the function tag, so "judged independently of stance" is a
     procedural claim. Predicting the label from measured acoustics tests it.
  3. Does the [5.4] cue account hold? That section argues codecs retain directly
     reconstructive cues (loudness, mean F0) and shed contour-shaped ones (F0
     range, voice quality, rate). eGeMAPS contains both kinds, so the groups can
     be probed separately instead of the account being asserted.

eGeMAPSv02 Functionals, 88 features, extracted once and cached in the same
(ids, X) layout as features/<model>/<window>.npz so it plugs into the existing
tooling.

Usage:
  python3 src/27_egemaps.py --extract     # cache the features
  python3 src/27_egemaps.py               # analyse (extracts first if needed)
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
CLIPS = ROOT / "data" / "clips" / "W2_segment"
FEAT = ROOT / "features" / "egemaps"
OUT = ROOT / "results" / "egemaps_baseline.txt"
CLASSES = ("affiliative", "neutral", "adversarial")
RNG = np.random.default_rng(42)

# Feature groups, by index into the 88 eGeMAPSv02 functionals. The split follows
# the argument in [5.4]: level and energy are directly reconstructive, so a codec
# optimised for reconstruction must keep them. Contour, quality and rate are not,
# and can be degraded at little reconstruction cost.
GROUPS = {
    "level (loudness, F0 mean)":      [0, 2, 3, 4, 10, 12, 13, 14, 87],
    "contour (F0/loudness dynamics)": [1, 5, 6, 7, 8, 9, 11, 15, 16, 17, 18, 19],
    "voice quality (jitter/HNR)":     list(range(30, 40)),
    "spectral and formant":           list(range(20, 30)) + list(range(40, 81)),
    "temporal (rate, segments)":      list(range(81, 87)),
}
RECONSTRUCTIVE = GROUPS["level (loudness, F0 mean)"]


def manifest():
    src = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
    return {r["candidate_id"]: r for r in csv.DictReader(open(src, newline=""))
            if r.get("stance", "").strip() in CLASSES}


def extract(man):
    import opensmile
    smile = opensmile.Smile(feature_set=opensmile.FeatureSet.eGeMAPSv02,
                            feature_level=opensmile.FeatureLevel.Functionals)
    ids, rows = [], []
    for i, cid in enumerate(sorted(man)):
        wav = CLIPS / f"{cid}.wav"
        if not wav.exists():
            continue
        rows.append(smile.process_file(str(wav)).values[0])
        ids.append(cid)
        if (i + 1) % 200 == 0:
            print(f"  {i+1}/{len(man)}", flush=True)
    FEAT.mkdir(parents=True, exist_ok=True)
    X = np.asarray(rows, dtype=np.float64)
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    np.savez(FEAT / "W2_segment.npz", ids=np.array(ids), X=X,
             names=np.array(smile.feature_names))
    print(f"wrote {FEAT/'W2_segment.npz'}  {X.shape}")
    return ids, X


def load(man):
    p = FEAT / "W2_segment.npz"
    if not p.exists():
        return extract(man)
    d = np.load(p, allow_pickle=True)
    return list(d["ids"]), d["X"]


def oof(X, y, g, splits=5):
    ns = min(splits, len(set(g)), min(Counter(y).values()))
    if ns < 2:
        return None
    pipe = make_pipeline(StandardScaler(),
                         LogisticRegression(max_iter=3000, C=1.0,
                                            class_weight="balanced"))
    return cross_val_predict(pipe, X, y, groups=g, cv=GroupKFold(n_splits=ns))


def score(X, y, g, perm=100):
    pred = oof(X, y, g)
    if pred is None:
        return None
    f1 = f1_score(y, pred, average="macro")
    null = []
    for _ in range(perm):
        yp = RNG.permutation(y)
        pr = oof(X, yp, g)
        if pr is not None:
            null.append(f1_score(yp, pr, average="macro"))
    null = np.asarray(null)
    p = (int((null >= f1).sum()) + 1) / (len(null) + 1)
    return f1, float(null.mean()), f1 - float(null.mean()), p, len(set(pred)) < 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--perm", type=int, default=100)
    args = ap.parse_args()

    man = manifest()
    if args.extract:
        extract(man); return

    ids, X = load(man)
    meta = [man[c] for c in ids]
    y = np.array([m["stance"] for m in meta])
    ar = np.array([m["arousal"] for m in meta])
    ph = np.array([m["target_phrase"] for m in meta])
    g = np.array([m["episode_id"] for m in meta])

    lines = []
    def emit(s=""):
        print(s, flush=True); lines.append(s)

    emit("eGeMAPS BASELINE AND CUE-GROUP ANALYSIS")
    emit(f"eGeMAPSv02 functionals, 88 features, {len(ids)} clips, W2, "
         f"same folds and probe as [3.6]. Permutations: {args.perm}.")
    emit("=" * 88)

    emit()
    emit("1. POOLED THREE-WAY STANCE, against the neural representations")
    emit("-" * 88)
    r = score(X, y, g, args.perm)
    emit(f"{'eGeMAPS, all 88':32}{r[0]:>9.3f}{r[1]:>9.3f}{r[2]:>+9.3f}{r[3]:>9.3f}")
    emit(f"{'  (WavLM, from [4.2])':32}{0.573:>9.3f}{0.332:>9.3f}{0.241:>+9.3f}")
    emit(f"{'  (Mimi histogram, from [4.2])':32}{0.381:>9.3f}{0.311:>9.3f}{0.070:>+9.3f}")
    emit(f"{'  (Text discourse, from [4.2])':32}{0.378:>9.3f}{0.333:>9.3f}{0.045:>+9.3f}")
    emit("columns: macro-F1, permutation chance, margin, p")

    emit()
    emit("2. WITHIN-WORD, comparable to Table 4.2")
    emit("-" * 88)
    f1s, dg = [], 0
    for p_ in sorted(set(ph)):
        m = ph == p_
        keep = [c for c, _ in Counter(y[m]).most_common(2)]
        s = np.isin(y[m], keep)
        pred = oof(X[m][s], y[m][s], g[m][s])
        if pred is None:
            continue
        f1s.append(f1_score(y[m][s], pred, average="macro"))
        dg += len(set(pred)) < 2
    emit(f"{'eGeMAPS mean within-word':32}{np.mean(f1s):>9.3f}   degenerate {dg}/{len(f1s)}")
    emit(f"{'  (WavLM 0.659, Mimi emb. 0.594, text 0.534, Mimi hist. 0.466)':32}")

    emit()
    emit("3. ARE THE AROUSAL LABELS GROUNDED IN MEASURED ACOUSTICS?")
    emit("-" * 88)
    ra = score(X, ar, g, args.perm)
    emit(f"{'arousal from eGeMAPS':32}{ra[0]:>9.3f}{ra[1]:>9.3f}{ra[2]:>+9.3f}{ra[3]:>9.3f}")
    emit("A high margin means the annotated arousal axis tracks measurable energy and")
    emit("pitch rather than resting on annotator judgement alone.")

    emit()
    emit("4. DOES STANCE SURVIVE WITHOUT THE RECONSTRUCTIVE CUES?")
    emit("-" * 88)
    keep_idx = [i for i in range(X.shape[1]) if i not in RECONSTRUCTIVE]
    rs = score(X[:, keep_idx], y, g, args.perm)
    emit(f"{'stance, all 88':32}{r[2]:>+9.3f}")
    emit(f"{'stance, level cues removed':32}{rs[2]:>+9.3f}   ({len(keep_idx)} features)")
    lo, hi = ar == "low", ar == "high"
    for name, m in (("low arousal", lo), ("high arousal", hi)):
        rr = score(X[m], y[m], g[m], args.perm)
        if rr:
            emit(f"{'stance within ' + name:32}{rr[2]:>+9.3f}{rr[3]:>9.3f}")

    emit()
    emit("5. CUE GROUPS, three-way stance, each group alone")
    emit("-" * 88)
    emit(f"{'group':34}{'n feat':>7}{'macroF1':>9}{'chance':>9}{'margin':>9}{'p':>8}")
    for name, idx in GROUPS.items():
        rg = score(X[:, idx], y, g, args.perm)
        if rg:
            emit(f"{name:34}{len(idx):>7}{rg[0]:>9.3f}{rg[1]:>9.3f}{rg[2]:>+9.3f}{rg[3]:>8.3f}")
    emit()
    emit("6. THE SAME GROUPS AGAINST AROUSAL, which is the other half of the test")
    emit("-" * 88)
    emit(f"{'group':34}{'n feat':>7}{'macroF1':>9}{'chance':>9}{'margin':>9}{'p':>8}")
    for name, idx in GROUPS.items():
        rg = score(X[:, idx], ar, g, args.perm)
        if rg:
            emit(f"{name:34}{len(idx):>7}{rg[0]:>9.3f}{rg[1]:>9.3f}{rg[2]:>+9.3f}{rg[3]:>8.3f}")
    emit()
    emit("[5.4] argues that level cues are directly reconstructive and carry arousal,")
    emit("while contour, quality and rate carry stance and cost a codec little to shed.")
    emit("Rankings WITHIN a task are the comparable quantity. Margins across the two")
    emit("tasks are not, since stance is three-way and arousal binary, so the two tables")
    emit("must not be divided into each other.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
