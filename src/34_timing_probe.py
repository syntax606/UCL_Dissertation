#!/usr/bin/env python3
"""
Does pragmatic stance survive a readout that respects time?

Everything measured so far went through a readout that discards frame order, so
the reported codec loss is really a loss measured through a flattening lens. This
script holds the representation fixed, varies only the readout, and asks what
comes back.

THE CONTROL. A time-aware readout has more dimensions than mean-and-std, so any
gain could be the extra parameters rather than the timing. The control is to
shuffle the frames within each clip and apply the identical readout. Shuffling
destroys order while preserving dimensionality, the marginal distribution of every
feature dimension, and the clip's length. So

    real - shuffled  =  what temporal order contributes
    shuffled         =  what the readout gets for free from dimensionality

This is the frame-shuffling control that src/20 correctly called vacuous against
mean-and-std, since shuffling cannot change an order-free summary at all. Against
an order-aware readout it becomes the sharpest test available, and it costs one
extra fit per cell.

Discrete streams take different readouts, since a temporal basis over code indices
is meaningless. See src/33.

Probe, folds and metric are src/18's exactly, so numbers are comparable to the
existing figures. Evaluation is out-of-fold under GroupKFold by episode.

Runs on CPU. The frames are large and live wherever PC_FRAMES_DIR points, so this
is meant to run beside them and bring home only the scores.

Usage:
  python3 src/34_timing_probe.py --reps core
  python3 src/34_timing_probe.py --reps layers --readouts meanstd basis4
  python3 src/34_timing_probe.py --reps core --perm 100
"""
import argparse, csv, importlib.util, sys, time, warnings
from collections import Counter
from pathlib import Path

import numpy as np
from joblib import Parallel, delayed
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold
from sklearn.metrics import f1_score

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
SHEET = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
OUT = ROOT / "results" / "timing_probe.txt"
CSV = ROOT / "results" / "timing_probe.csv"
CLASSES = ("affiliative", "neutral", "adversarial")
CLIP_SECONDS = 10.0
SEED = 0

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import FRAMES_DIR                                    # noqa: E402
_ro = importlib.util.spec_from_file_location("ro", Path(__file__).parent / "33_readouts.py")
RO = importlib.util.module_from_spec(_ro); _ro.loader.exec_module(RO)

# The continuous rungs of the ladder, plus the two variable-rate models. Layer
# choice is deliberately not made here, see --reps layers for the full sweep.
CORE = ["wavlm_L20", "hubert_L23", "whisper_L9",
        "mimi_pre", "mimi_post", "dac_pre", "dac_post",
        "sylber", "dycast_pre", "dycast_post"]
DISCRETE_REPS = {"mimi_codes": 2048, "dycast_toks": None}
VARIABLE = {"sylber": "bounds", "dycast_pre": "durs", "dycast_post": "durs",
            "dycast_toks": "durs"}


def probe():
    """src/18 make_probe, unchanged."""
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=3000, C=1.0, class_weight="balanced"))


def manifest():
    return {r["candidate_id"]: r for r in csv.DictReader(open(SHEET, newline=""))
            if r.get("stance", "").strip() in CLASSES}


def load(rep):
    stem = FRAMES_DIR / rep / "W2_segment"
    return (np.load(f"{stem}.X.npy", mmap_mode="r"),
            np.load(f"{stem}.lengths.npy"),
            np.load(f"{stem}.ids.npy", allow_pickle=True))


def build(rep, readout, shuffle=False, rng=None):
    """Apply one readout to every clip. Returns (X, ids)."""
    X, L, ids = load(rep)
    aux = None
    if rep in VARIABLE and readout == "timing":
        kind = VARIABLE[rep]
        side = "sylber_bounds" if kind == "bounds" else "dycast_durs"
        aux = load(side)[0]

    # Alphabet size once, not per clip. Reading it inside the loop would pull the
    # whole memmap into memory 873 times.
    n_codes = None
    if rep in DISCRETE_REPS and readout == "hist":
        n_codes = DISCRETE_REPS[rep] or int(np.asarray(X).max()) + 1

    rows = []
    for i in range(len(ids)):
        n = int(L[i])
        if n <= 0:
            rows.append(None); continue
        # Shuffle the raw slice, before any branch, so the control reaches the
        # discrete readouts too. Permuting a float copy would leave the code
        # sequence untouched and every run-length statistic identical.
        sl = X[i, :n]
        if shuffle:
            sl = sl[rng.permutation(n)]
        if readout == "timing":
            a = np.asarray(aux[i, :n], dtype=np.float64) if aux is not None else None
            rows.append(RO.r_timing(n, CLIP_SECONDS,
                                    bounds=a if VARIABLE.get(rep) == "bounds" else None,
                                    durs=a if VARIABLE.get(rep) == "durs" else None))
        elif rep in DISCRETE_REPS:
            rows.append(RO.r_hist(np.asarray(sl).astype(np.int64), n_codes)
                        if readout == "hist"
                        else RO.DISCRETE[readout](np.asarray(sl).astype(np.int64)))
        else:
            rows.append(RO.CONTINUOUS[readout](np.asarray(sl, dtype=np.float64)))

    D = next(len(r) for r in rows if r is not None)
    Xo = np.stack([r if r is not None else np.zeros(D) for r in rows])
    return np.nan_to_num(Xo, nan=0.0, posinf=0.0, neginf=0.0), ids


def oof_f1(X, y, g, n_splits=5):
    ns = min(n_splits, len(set(g)), min(Counter(y).values()))
    if ns < 2:
        return float("nan")
    pred = np.empty(len(y), dtype=object)
    for tr, te in GroupKFold(n_splits=ns).split(X, y, g):
        pred[te] = probe().fit(X[tr], y[tr]).predict(X[te])
    return f1_score(y, list(pred), average="macro")


def perm_null(X, y, g, n=50, seed=SEED):
    rng = np.random.default_rng(seed)
    return float(np.mean(Parallel(n_jobs=-1)(
        delayed(oof_f1)(X, rng.permutation(y), g) for _ in range(n))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", nargs="+", default=["core"])
    ap.add_argument("--readouts", nargs="+", default=None)
    ap.add_argument("--perm", type=int, default=0,
                    help="permutations for the empirical null (slow, 0 to skip)")
    ap.add_argument("--no-shuffle", action="store_true",
                    help="skip the frame-shuffling control")
    args = ap.parse_args()

    man = manifest()
    reps = []
    for r in args.reps:
        if r == "core":
            reps += CORE + list(DISCRETE_REPS)
        elif r == "layers":
            reps += [f"{m}_L{i}" for m, n in (("wavlm", 25), ("hubert", 25),
                                              ("whisper", 13)) for i in range(n)]
        else:
            reps.append(r)
    reps = [r for r in reps if (FRAMES_DIR / r / "W2_segment.X.npy").exists()]

    lines, rowsout = [], []
    def emit(s=""):
        print(s, flush=True); lines.append(s)

    emit("DOES STANCE SURVIVE A READOUT THAT RESPECTS TIME?")
    emit("Representation held fixed, readout varied. 'shuffled' applies the same")
    emit("readout to frame-shuffled clips, so it matches on dimensionality and on")
    emit("every feature's marginal distribution but destroys order. The gap between")
    emit("them is what temporal order contributes.")
    emit("=" * 92)
    emit(f"{'representation':16}{'readout':10}{'dims':>7}{'macroF1':>9}"
         f"{'shuffled':>10}{'order':>8}{'chance':>8}")

    for rep in reps:
        avail = (list(RO.DISCRETE) if rep in DISCRETE_REPS else list(RO.CONTINUOUS))
        if rep in VARIABLE:
            avail = avail + ["timing"]
        todo = [r for r in (args.readouts or avail) if r in avail]
        for readout in todo:
            t0 = time.time()
            try:
                X, ids = build(rep, readout)
            except Exception as e:
                emit(f"{rep:16}{readout:10}  FAILED {type(e).__name__}: {e}"); continue
            keep = [i for i, c in enumerate(ids) if str(c) in man]
            X = X[keep]
            y = np.array([man[str(ids[i])]["stance"] for i in keep])
            g = np.array([man[str(ids[i])]["episode_id"] for i in keep])

            f1 = oof_f1(X, y, g)
            sh = np.nan
            if not args.no_shuffle and readout not in ("meanstd", "hist", "timing"):
                Xs, _ = build(rep, readout, shuffle=True,
                              rng=np.random.default_rng(SEED))
                sh = oof_f1(Xs[keep], y, g)
            ch = perm_null(X, y, g, args.perm) if args.perm else np.nan
            order = f1 - sh if sh == sh else np.nan

            emit(f"{rep:16}{readout:10}{X.shape[1]:>7}{f1:>9.3f}"
                 f"{sh:>10.3f}{order:>+8.3f}{ch:>8.3f}"
                 if sh == sh else
                 f"{rep:16}{readout:10}{X.shape[1]:>7}{f1:>9.3f}"
                 f"{'—':>10}{'—':>8}{ch:>8.3f}")
            rowsout.append(dict(rep=rep, readout=readout, dims=X.shape[1],
                                f1=round(f1, 4),
                                shuffled=None if sh != sh else round(sh, 4),
                                order=None if order != order else round(order, 4),
                                chance=None if ch != ch else round(ch, 4),
                                secs=round(time.time() - t0, 1)))

    emit()
    emit("Read: 'order' is the readout's gain over its own shuffled control, so it")
    emit("is the part attributable to timing rather than to having more dimensions.")
    emit("If it is near zero everywhere, stance is not carried temporally and the")
    emit("pooled figures were not understating anything. If it is large for the")
    emit("codecs and small for the continuous encoders, the loss reported in [Ch.4]")
    emit("is partly an artefact of the readout rather than a property of the codec.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    if rowsout:
        with open(CSV, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rowsout[0])); w.writeheader()
            w.writerows(rowsout)
    print(f"\nwrote {OUT}\nwrote {CSV}")


if __name__ == "__main__":
    main()
