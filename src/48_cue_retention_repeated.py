#!/usr/bin/env python3
"""Cue retention recomputed under the partitioning scheme in [3.7].

Why this exists. src/30 and src/43 produced the cue-retention table in [4.4] using
GroupKFold on a single partition. [3.7] says every reported figure is the mean over 25
partitions constructed in the analysis code rather than delegated to a library, and gives
the reason: GroupKFold's assignment changed between sklearn 1.7 and 1.9 and moved WavLM
L20 by 0.020 on byte-identical inputs. The cue-retention figures were the one table not
built that way, and [4.5] leans on them as the second, independent measurement behind the
architectural claim. A corroborating measurement should not rest on the procedure the
methods chapter rejects.

Two things change and nothing else does. The partition comes from _partition in src/34
with 25 seeds, and retention is formed per partition before averaging, so the ratio itself
carries a spread rather than being a ratio of two averages. Cue groups, eGeMAPS targets,
ridge alphas and the standardise-then-ridge pipeline are unchanged from src/30, so the
numbers stay comparable to the ones they replace.

The comparison that matters is EnCodec against DAC on the temporal group. [4.5] reads
72 per cent against 68 as the same ordering the order effect gives, and four points on a
single partition with no spread is not something to rest a claim on. That contrast is
tested paired across partitions here.

Usage:  python3 src/48_cue_retention_repeated.py
        python3 src/48_cue_retention_repeated.py --reps 5      (quick check)
"""
import argparse
import csv
import warnings
from pathlib import Path

import numpy as np
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
FEAT, FR = ROOT / "features", ROOT / "features_frames"
OUT = ROOT / "results" / "cue_retention_repeated.txt"
CLASSES = ("affiliative", "neutral", "adversarial")
ALPHAS = (1.0, 10.0, 100.0, 1000.0, 10000.0)
N_FOLDS = 5

GROUPS = {
    "contour":       [1, 5, 6, 7, 8, 9, 11, 15, 16, 17, 18, 19],
    "level":         [0, 2, 3, 4, 10, 12, 13, 14, 87],
    "voice quality": list(range(30, 40)),
    "temporal":      list(range(81, 87)),
    "spectral":      list(range(20, 30)) + list(range(40, 81)),
}

# (label, loader spec) — npz(dir, layer) or frames(dir), matching src/30 and src/43
RUNGS = [
    ("WavLM, ceiling",               ("npz", "wavlm", 20)),
    ("Mimi, before quantisation",    ("npz", "mimi_pre_meanstd", None)),
    ("Mimi, after quantisation",     ("npz", "mimi_post", None)),
    ("Mimi, deployed histogram",     ("npz", "mimi", None)),
    ("EnCodec, before quantisation", ("frames", "encodec_pre", None)),
    ("EnCodec, after quantisation",  ("frames", "encodec_post", None)),
    ("DAC, before quantisation",     ("npz", "dac_pre", None)),
    ("DAC, after quantisation",      ("npz", "dac_post", None)),
]

CEIL = "WavLM, ceiling"


def _partition(g, seed, n_folds=N_FOLDS):
    """Whole episodes to folds from an explicit seed. Copied from src/34 so the two
    analyses partition identically rather than merely similarly."""
    uq = sorted(set(g))
    perm = np.random.default_rng(seed).permutation(len(uq))
    g2f = {uq[perm[i]]: i % n_folds for i in range(len(uq))}
    return np.array([g2f[gi] for gi in g])


def manifest():
    src = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
    return {r["candidate_id"]: r for r in csv.DictReader(open(src, newline=""))
            if r.get("stance", "").strip() in CLASSES}


def load_npz(name, order, layer=None):
    z = np.load(FEAT / name / "W2_segment.npz", allow_pickle=True)
    ids = [str(c) for c in z["ids"]]
    X = z["X"]
    if layer is not None:
        X = X[:, layer, :]
    X = X.reshape(len(ids), -1)
    idx = {c: i for i, c in enumerate(ids)}
    return X[[idx[c] for c in order]]


def load_frames(name, order):
    st = FR / name / "W2_segment"
    X = np.load(f"{st}.X.npy", mmap_mode="r")
    L = np.load(f"{st}.lengths.npy")
    ids = [str(c) for c in np.load(f"{st}.ids.npy", allow_pickle=True)]
    idx = {c: i for i, c in enumerate(ids)}
    out = []
    for c in order:
        i = idx[c]
        F = np.asarray(X[i, :max(int(L[i]), 1)], dtype=np.float64)
        out.append(np.concatenate([F.mean(0), F.std(0)]))
    return np.stack(out)


def load(spec, order):
    kind, name, layer = spec
    return load_npz(name, order, layer) if kind == "npz" else load_frames(name, order)


def oof_r2(X, Y, fold):
    """Out-of-fold R-squared for every eGeMAPS target at once.

    src/30 fit one ridge per target inside cross_val_predict. Fitting all 88 jointly with
    alpha_per_target gives each target its own alpha exactly as before, and turns 88 fits
    per fold into one.
    """
    pred = np.empty_like(Y, dtype=np.float64)
    for f in range(N_FOLDS):
        te = fold == f
        tr = ~te
        sc = StandardScaler().fit(X[tr])
        m = RidgeCV(alphas=ALPHAS, alpha_per_target=True).fit(sc.transform(X[tr]), Y[tr])
        pred[te] = m.predict(sc.transform(X[te]))
    ss_res = ((Y - pred) ** 2).sum(0)
    ss_tot = ((Y - Y.mean(0)) ** 2).sum(0)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(ss_tot > 0, 1.0 - ss_res / ss_tot, np.nan)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=25)
    args = ap.parse_args()

    man = manifest()
    eg = np.load(FEAT / "egemaps" / "W2_segment.npz", allow_pickle=True)
    ids = [str(c) for c in eg["ids"]]
    order = [c for c in ids if c in man]
    pos = {c: i for i, c in enumerate(ids)}
    Y = eg["X"][[pos[c] for c in order]].astype(np.float64)
    g = np.array([man[c]["episode_id"] for c in order])

    lines = []
    def emit(s=""):
        print(s, flush=True)
        lines.append(s)

    emit("CUE RETENTION, RECOMPUTED UNDER THE PARTITIONING IN [3.7]")
    emit(f"{len(order)} clips, {len(set(g))} episodes, {args.reps} partitions, "
         f"{N_FOLDS} folds, ridge to {Y.shape[1]} eGeMAPS features.")
    emit("Replaces the single-partition GroupKFold figures from src/30 and src/43.")
    emit("=" * 100)

    X = {}
    for label, spec in RUNGS:
        try:
            X[label] = load(spec, order).astype(np.float64)
            emit(f"  loaded {label:32} {X[label].shape[1]:>6} dims")
        except Exception as e:
            emit(f"  ** {label}: {e}")
    emit()

    # per-partition group R-squared for every rung
    absR = {lab: {gn: [] for gn in GROUPS} for lab in X}
    for s in range(args.reps):
        fold = _partition(g, seed=s)
        for lab in X:
            r2 = oof_r2(X[lab], Y, fold)
            for gn, cols in GROUPS.items():
                absR[lab][gn].append(float(np.nanmean(r2[cols])))
        emit(f"  partition {s + 1}/{args.reps} done")
    emit()

    A = {lab: {gn: np.array(v) for gn, v in d.items()} for lab, d in absR.items()}

    emit("ABSOLUTE R-SQUARED, mean over partitions (sd)")
    emit(f"{'representation':30}" + "".join(f"{gn:>20}" for gn in GROUPS))
    for lab in X:
        emit(f"{lab:30}" + "".join(f"{A[lab][gn].mean():>13.3f} ({A[lab][gn].std():.3f})"
                                  for gn in GROUPS))
    emit()

    emit("RETENTION vs WavLM, ratio formed within each partition then averaged (sd)")
    emit(f"{'representation':30}" + "".join(f"{gn:>20}" for gn in GROUPS))
    ret = {}
    for lab in X:
        if lab == CEIL:
            continue
        ret[lab] = {gn: A[lab][gn] / A[CEIL][gn] for gn in GROUPS}
        emit(f"{lab:30}" + "".join(f"{ret[lab][gn].mean():>13.0%} ({ret[lab][gn].std():.0%})"
                                  for gn in GROUPS))
    emit()

    emit("THE COMPARISON [4.5] RESTS ON, paired across partitions")
    emit("-" * 100)
    for gn in ("temporal",):
        for a, b in (("EnCodec, before quantisation", "DAC, before quantisation"),
                     ("EnCodec, after quantisation", "DAC, after quantisation"),
                     ("Mimi, before quantisation", "EnCodec, before quantisation")):
            if a not in ret or b not in ret:
                continue
            d = ret[a][gn] - ret[b][gn]
            t = d.mean() / (d.std(ddof=1) / np.sqrt(len(d))) if d.std(ddof=1) > 0 else float("nan")
            wins = int((d > 0).sum())
            emit(f"  {gn:>9}  {a.split(',')[0]:>8} - {b.split(',')[0]:<8} "
                 f"= {d.mean():+.1%} (sd {d.std():.1%})  t = {t:>6.1f}  "
                 f"higher in {wins}/{len(d)} partitions")
    emit()
    emit("Read: [4.5] claims cue retention and the order effect rank the three codecs")
    emit("identically. That holds only if EnCodec sits above DAC on the temporal group by")
    emit("more than partition noise. The paired figures above are what decides it.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
