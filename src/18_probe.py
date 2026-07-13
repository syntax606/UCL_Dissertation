#!/usr/bin/env python3
"""
Phase 3 probing: how decodable is pragmatic STANCE from each representation?

Linear logistic-regression probes on frozen features, with all evaluation done
out-of-fold under GroupKFold BY EPISODE (no episode's clips ever span train and
test, so nothing leaks through shared speaker/topic). Reported with:
  - macro-F1 (3-way stance) out-of-fold
  - 95% CI from an EPISODE-CLUSTER bootstrap (resample whole episodes)
  - a permutation p-value (shuffle stance labels, re-fit)
  - a majority-class baseline for reference

Three views:
  A. Pooled 3-way stance decodability per representation (best layer for the
     audio models), on the primary window W2_segment.
  B. Context-window sweep (W1/W2/W3) at each model's best layer.
  C. Per-phrase WITHIN-WORD binary contrast: the lexical control. Same word,
     two stances -> can the probe still separate them? Averaged over phrases.

Usage:
  python3 src/17_probe.py                     # all models, full analysis
  python3 src/17_probe.py --models wavlm text
  python3 src/17_probe.py --perm 0            # skip permutation (faster)
"""
import argparse, csv, sys, warnings
from collections import Counter, defaultdict
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
MANIFEST = ROOT / "manifest.csv"
if not MANIFEST.exists():
    MANIFEST = ROOT / "data" / "annotations" / "manifest.csv"
PRIMARY = "W2_segment"
WINDOWS = ["W1_local", "W2_segment", "W3_discourse"]
AUDIO = ["wavlm", "hubert", "whisper"]
RNG = np.random.default_rng(42)


def load_manifest():
    m = {}
    src = MANIFEST
    if not src.exists():  # fall back to the labeled sheet
        src = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
    for r in csv.DictReader(open(src, newline="")):
        if r.get("stance", "").strip() in ("affiliative", "neutral", "adversarial"):
            m[r["candidate_id"]] = r
    return m


def build_pipe(dim):
    # lbfgs handles our dims (2048 audio-layer, 14336 mimi, 768 text) fine
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=3000, C=1.0, class_weight="balanced"),
    )


def oof_predict(X, y, groups, n_splits=5):
    ns = min(n_splits, len(set(groups)), min(Counter(y).values()))
    if ns < 2:
        return None
    cv = GroupKFold(n_splits=ns)
    return cross_val_predict(build_pipe(X.shape[1]), X, y, groups=groups, cv=cv)


def cluster_bootstrap_ci(y, pred, groups, B=1000):
    groups = np.asarray(groups)
    y = np.asarray(y); pred = np.asarray(pred)
    uniq = np.unique(groups)
    idx_by_g = {g: np.where(groups == g)[0] for g in uniq}
    scores = []
    for _ in range(B):
        pick = RNG.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([idx_by_g[g] for g in pick])
        scores.append(f1_score(y[idx], pred[idx], average="macro"))
    return float(np.percentile(scores, 2.5)), float(np.percentile(scores, 97.5))


def permutation_p(X, y, groups, observed, P=200):
    y = np.asarray(y); groups = np.asarray(groups)
    ge = 0
    for _ in range(P):
        yp = RNG.permutation(y)
        pred = oof_predict(X, yp, groups)
        if pred is None:
            continue
        if f1_score(yp, pred, average="macro") >= observed:
            ge += 1
    return (ge + 1) / (P + 1)


def majority_f1(y):
    y = np.asarray(y)
    maj = Counter(y).most_common(1)[0][0]
    return f1_score(y, [maj] * len(y), average="macro")


def load_feat(model, window):
    if model == "text":
        p = FEAT / "text" / f"{window}.npz"   # window in {targetonly, context}
    else:
        p = FEAT / model / f"{window}.npz"
    if not p.exists():
        return None
    d = np.load(p, allow_pickle=True)
    return list(d["ids"]), d["X"]


def align(ids, man):
    keep = [i for i, cid in enumerate(ids) if cid in man]
    y = np.array([man[ids[i]]["stance"] for i in keep])
    arous = np.array([man[ids[i]].get("arousal", "") for i in keep])
    phrase = np.array([man[ids[i]]["target_phrase"] for i in keep])
    groups = np.array([man[ids[i]]["episode_id"] for i in keep])
    return np.array(keep), y, arous, phrase, groups


def eval_2d(X, y, groups, perm):
    pred = oof_predict(X, y, groups)
    if pred is None:
        return None
    f1 = f1_score(y, pred, average="macro")
    lo, hi = cluster_bootstrap_ci(y, pred, groups)
    p = permutation_p(X, y, groups, f1, P=perm) if perm else float("nan")
    return dict(f1=f1, lo=lo, hi=hi, p=p, maj=majority_f1(y), n=len(y))


def analyze_model(model, man, perm):
    """Return (primary_result, best_layer, per_window_at_best)."""
    if model == "text":
        out = {}
        for variant in ("targetonly", "context"):
            f = load_feat("text", variant)
            if not f: continue
            ids, X = f
            k, y, ar, ph, g = align(ids, man)
            out[variant] = eval_2d(X[k], y, g, perm)
        return out, None, None

    # audio or mimi
    f = load_feat(model, PRIMARY)
    if not f:
        return None, None, None
    ids, X = f
    k, y, ar, ph, g = align(ids, man)
    if model in AUDIO:              # X: (N, L, D) -> sweep layers
        L = X.shape[1]
        per_layer = []
        for l in range(L):
            pred = oof_predict(X[k, l], y, g)
            per_layer.append(f1_score(y, pred, average="macro") if pred is not None else 0)
        best = int(np.argmax(per_layer))
        primary = eval_2d(X[k, best], y, g, perm)
        primary["per_layer"] = per_layer
        # context-window sweep at best layer
        byw = {}
        for w in WINDOWS:
            fw = load_feat(model, w)
            if not fw: continue
            idw, Xw = fw
            kw, yw, _, _, gw = align(idw, man)
            r = eval_2d(Xw[kw, best], yw, gw, 0)
            byw[w] = r["f1"] if r else None
        return primary, best, byw
    else:                          # mimi: (N, D)
        primary = eval_2d(X[k], y, g, perm)
        byw = {}
        for w in WINDOWS:
            fw = load_feat(model, w)
            if not fw: continue
            idw, Xw = fw
            kw, yw, _, _, gw = align(idw, man)
            r = eval_2d(Xw[kw], yw, gw, 0)
            byw[w] = r["f1"] if r else None
        return primary, None, byw


def per_phrase_binary(model, man, layer):
    """Within each phrase, binary contrast between its two commonest stances."""
    win = "context" if model == "text_context" else PRIMARY
    m = "text" if model == "text_context" else model
    f = load_feat(m, "context" if m == "text" else PRIMARY)
    if not f:
        return {}
    ids, X = f
    k, y, ar, ph, g = align(ids, man)
    if m in AUDIO and layer is not None:
        Xk = X[k, layer]
    elif m in AUDIO:
        Xk = X[k, layer or 0]
    else:
        Xk = X[k]
    res = {}
    for phrase in sorted(set(ph)):
        sel = ph == phrase
        yy = y[sel]
        top2 = [c for c, _ in Counter(yy).most_common(2)]
        if len(top2) < 2:
            continue
        keep = np.isin(yy, top2)
        Xp, yp, gp = Xk[sel][keep], yy[keep], g[sel][keep]
        if min(Counter(yp).values()) < 8:
            continue
        pred = oof_predict(Xp, yp, gp, n_splits=5)
        if pred is None:
            continue
        res[phrase] = dict(f1=f1_score(yp, pred, average="macro"),
                           classes=top2, n=len(yp),
                           maj=majority_f1(yp))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+",
                    default=["wavlm", "hubert", "whisper", "mimi", "text"])
    ap.add_argument("--perm", type=int, default=200)
    args = ap.parse_args()
    man = load_manifest()
    print(f"labelled clips in manifest: {len(man)}")
    print(f"stance dist: {dict(Counter(r['stance'] for r in man.values()))}\n")

    print("=" * 74)
    print("A. POOLED 3-WAY STANCE DECODABILITY  (primary window W2_segment)")
    print("=" * 74)
    print(f"{'model':16s}{'layer':>6}{'macroF1':>9}{'95% CI':>16}{'perm p':>9}{'major':>8}")
    best_layers = {}
    windows_tbl = {}
    for model in args.models:
        pr, best, byw = analyze_model(model, man, args.perm)
        if model == "text":
            for variant, r in (pr or {}).items():
                if r:
                    print(f"{'text:'+variant:16s}{'-':>6}{r['f1']:>9.3f}"
                          f"{'['+format(r['lo'],'.2f')+','+format(r['hi'],'.2f')+']':>16}"
                          f"{r['p']:>9.3f}{r['maj']:>8.3f}")
            continue
        if pr is None:
            print(f"{model:16s}  (no features found)"); continue
        best_layers[model] = best
        windows_tbl[model] = byw
        lay = str(best) if best is not None else "-"
        print(f"{model:16s}{lay:>6}{pr['f1']:>9.3f}"
              f"{'['+format(pr['lo'],'.2f')+','+format(pr['hi'],'.2f')+']':>16}"
              f"{pr['p']:>9.3f}{pr['maj']:>8.3f}")

    print("\n" + "=" * 74)
    print("B. CONTEXT-WINDOW SWEEP  (macro-F1 at each model's best layer)")
    print("=" * 74)
    print(f"{'model':16s}{'W1_local':>12}{'W2_segment':>12}{'W3_discourse':>14}")
    for model, byw in windows_tbl.items():
        print(f"{model:16s}"
              f"{byw.get('W1_local',float('nan')):>12.3f}"
              f"{byw.get('W2_segment',float('nan')):>12.3f}"
              f"{byw.get('W3_discourse',float('nan')):>14.3f}")

    print("\n" + "=" * 74)
    print("C. PER-PHRASE WITHIN-WORD BINARY CONTRAST  (lexical control, W2)")
    print("=" * 74)
    for model in args.models:
        if model == "text":
            phres = per_phrase_binary("text_context", man, None)
            tag = "text:context"
        else:
            phres = per_phrase_binary(model, man, best_layers.get(model))
            tag = model
        if not phres:
            continue
        avg = np.mean([v["f1"] for v in phres.values()])
        print(f"\n{tag}  (mean over phrases: {avg:.3f})")
        for ph, v in phres.items():
            print(f"    {ph:9s} {'/'.join(c[:3] for c in v['classes']):8s} "
                  f"n={v['n']:>3}  F1={v['f1']:.3f}  (maj {v['maj']:.3f})")


if __name__ == "__main__":
    main()
