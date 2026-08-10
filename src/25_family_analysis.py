#!/usr/bin/env python3
"""
Is the phrase-family effect real, or is it the neutral class in disguise?

Grouping the eight target phrases by functional family (agreement particles,
evaluative terms, challenge markers) shows challenge markers carrying the stance
contrast most strongly in every representation, and Mimi retaining almost nothing
on the agreement particles. That would be a striking result, because the agreement
particles are the phrases with the least lexical content of their own, so they are
the ones where delivery does all the work.

But the families are confounded with contrast type. In view C of src/18_probe.py
each phrase is probed on its own DOMINANT binary contrast, and three of the four
agreement particles (yeah, okay, right) have a dominant contrast involving the
NEUTRAL class, while no evaluative or challenge phrase does. Neutral is the
smallest and fuzziest category, so part of any family effect could be a neutral
effect.

This script separates them by running every phrase on the SAME contrast,
adversarial against affiliative, so contrast type is held constant and family is
the only thing varying. Phrases are attempted only where both classes clear
MIN_PER_CLASS.

  dominant   each phrase's dominant contrast, reproducing view C
  advaff     adversarial against affiliative for every phrase

If the family ordering survives under advaff, it is a family effect. If it
collapses, it was the neutral class.

Usage:  python3 src/25_family_analysis.py
"""
import csv, sys, warnings
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
FEAT = ROOT / "features"
OUT = ROOT / "results" / "phrase_family_analysis.txt"
CLASSES = ("affiliative", "neutral", "adversarial")
WINDOW = "W2_segment"
MIN_PER_CLASS = 10

FAMILY = {"yeah": "agreement", "okay": "agreement", "right": "agreement",
          "sure": "agreement", "great": "evaluative", "fine": "evaluative",
          "really": "challenge", "come_on": "challenge"}
ORDER = ("agreement", "evaluative", "challenge")

VIEWS = [("WavLM", "wavlm", WINDOW, 20), ("Whisper", "whisper", WINDOW, 9),
         ("HuBERT", "hubert", WINDOW, 23), ("Mimi", "mimi", WINDOW, None),
         ("Text, context", "text", "context", None)]


def manifest():
    src = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
    return {r["candidate_id"]: r for r in csv.DictReader(open(src, newline=""))
            if r.get("stance", "").strip() in CLASSES}


def load(feat_dir, key, layer, man):
    p = FEAT / feat_dir / f"{key}.npz"
    if not p.exists():
        return None
    d = np.load(p, allow_pickle=True)
    ids, X = list(d["ids"]), d["X"]
    if layer is not None:
        X = X[:, layer, :]
    X = X.reshape(len(ids), -1)
    keep = [i for i, c in enumerate(ids) if c in man]
    meta = [man[ids[i]] for i in keep]
    return (X[keep],
            np.array([m["stance"] for m in meta]),
            np.array([m["target_phrase"] for m in meta]),
            np.array([m["episode_id"] for m in meta]))


def probe(X, y, g):
    """Binary macro-F1 out-of-fold, plus whether the probe degenerated.

    A probe that emits a single class for every clip scores exactly the majority
    baseline, so its margin is exactly 0.000. That is not a measured near-zero
    effect, it is a failure to separate at all, and the two must not be averaged
    together. Degenerate cells are flagged and excluded from family means."""
    ns = min(5, len(set(g)), min(Counter(y).values()))
    if ns < 2:
        return None, None
    pipe = make_pipeline(StandardScaler(),
                         LogisticRegression(max_iter=3000, C=1.0,
                                            class_weight="balanced"))
    pred = cross_val_predict(pipe, X, y, groups=g, cv=GroupKFold(n_splits=ns))
    return f1_score(y, pred, average="macro"), len(set(pred)) < 2


def majority(y):
    c = Counter(y)
    return f1_score(y, [c.most_common(1)[0][0]] * len(y), average="macro")


def run(X, y, ph, g, mode):
    """Return {phrase: (f1, maj, n, contrast)} under the given contrast rule."""
    out = {}
    for p in sorted(set(ph)):
        m = ph == p
        yp, Xp, gp = y[m], X[m], g[m]
        if mode == "dominant":
            keep = [c for c, _ in Counter(yp).most_common(2)]
        else:
            keep = ["adversarial", "affiliative"]
        sel = np.isin(yp, keep)
        ys, Xs, gs = yp[sel], Xp[sel], gp[sel]
        cnt = Counter(ys)
        if len(cnt) < 2 or min(cnt.values()) < MIN_PER_CLASS:
            continue
        f1, degenerate = probe(Xs, ys, gs)
        if f1 is None:
            continue
        imbalance = max(cnt.values()) / min(cnt.values())
        out[p] = (f1, majority(ys), len(ys),
                  "/".join(sorted(k[:3] for k in cnt)), degenerate, imbalance)
    return out


def main():
    man = manifest()
    lines = []

    def emit(s=""):
        print(s, flush=True)
        lines.append(s)

    emit("IS THE PHRASE-FAMILY EFFECT REAL, OR THE NEUTRAL CLASS IN DISGUISE?")
    emit("Every phrase probed twice: on its dominant contrast, and on adversarial")
    emit("against affiliative for all phrases, which holds contrast type constant.")
    emit(f"Margins are macro-F1 minus that phrase's own majority baseline. "
         f"Minimum {MIN_PER_CLASS} per class.")
    emit("Cells where the probe emitted a single class are marked degen and excluded")
    emit("from family means, since their margin is exactly zero by construction.")
    emit("=" * 92)

    results = {}
    for name, d, key, layer in VIEWS:
        got = load(d, key, layer, man)
        if got is None:
            emit(f"{name}: features missing")
            continue
        X, y, ph, g = got
        results[name] = {m: run(X, y, ph, g, m) for m in ("dominant", "advaff")}

    # which phrases are eligible under advaff, and which involve neutral
    any_model = next(iter(results.values()))
    emit()
    emit("PHRASE COVERAGE")
    emit(f"{'phrase':10}{'family':12}{'dominant':>14}{'adv/aff n':>12}{'imbalance':>12}")
    for p in sorted(FAMILY):
        dom = any_model["dominant"].get(p)
        aa = any_model["advaff"].get(p)
        emit(f"{p:10}{FAMILY[p]:12}{(dom[3] if dom else '-'):>14}"
             f"{(aa[2] if aa else 0):>12}"
             f"{(f'{aa[5]:.1f}:1' if aa else '-'):>12}")

    for mode, label in (("dominant", "DOMINANT CONTRAST (reproduces view C)"),
                        ("advaff", "ADVERSARIAL vs AFFILIATIVE, contrast held constant")):
        emit()
        emit(label)
        emit("=" * 92)
        emit(f"{'model':16}" + "".join(f"{f:>18}" for f in ORDER))
        for name, bymode in results.items():
            d = bymode[mode]
            row = f"{name:16}"
            for f in ORDER:
                ph = [p for p in d if FAMILY[p] == f]
                if not ph:
                    row += f"{'n/a':>18}"
                    continue
                live = [p for p in ph if not d[p][4]]
                if not live:
                    row += f"{'all degen':>18}"
                    continue
                mg = sum(d[p][0] - d[p][1] for p in live) / len(live)
                row += f"{mg:>+13.3f}({len(live)}/{len(ph)})"
            emit(row)

    emit()
    emit("PER-PHRASE UNDER THE HELD-CONSTANT CONTRAST")
    emit("=" * 92)
    emit(f"{'phrase':10}{'family':12}" + "".join(f"{n:>16}" for n in results))
    for p in sorted(FAMILY, key=lambda q: FAMILY[q]):
        if p not in results[list(results)[0]]["advaff"]:
            continue
        row = f"{p:10}{FAMILY[p]:12}"
        for name in results:
            e = results[name]["advaff"].get(p)
            if not e:
                row += f"{'-':>16}"
            elif e[4]:
                row += f"{'degen':>16}"
            else:
                row += f"{(e[0]-e[1]):>+16.3f}"
        emit(row)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
