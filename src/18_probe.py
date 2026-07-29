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


def permutation_null(X, y, groups, P=200):
    """Empirical null distribution of macro-F1: refit the probe on shuffled labels.

    This, not the majority-class score, is the reference a probe should be judged
    against. A constant (majority) predictor scores 0 on every class it never emits,
    so macro-F1 punishes it far harder than it punishes a genuinely no-skill probe;
    with balanced class weights our probe spreads predictions over all three classes
    and its true chance level sits near 0.33, not near 0.196.
    """
    y = np.asarray(y); groups = np.asarray(groups)
    null = []
    for _ in range(P):
        yp = RNG.permutation(y)
        pred = oof_predict(X, yp, groups)
        if pred is not None:
            null.append(f1_score(yp, pred, average="macro"))
    return np.asarray(null)


def majority_f1(y):
    """Macro-F1 of always predicting the most frequent class. Reported for
    completeness only; see permutation_null for the reference actually used."""
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
    if perm:
        null = permutation_null(X, y, groups, P=perm)
        p = (int((null >= f1).sum()) + 1) / (len(null) + 1)
        chance, chance95 = float(null.mean()), float(np.percentile(null, 95))
    else:
        p = chance = chance95 = float("nan")
    return dict(f1=f1, lo=lo, hi=hi, p=p, chance=chance, chance95=chance95,
                maj=majority_f1(y), n=len(y))


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


def _arrays(model, window, man, layer):
    """Return (X, y_stance, arousal, phrase, episode, show) aligned by id."""
    f = load_feat(model, window)
    if not f:
        return None
    ids, X = f
    keep, y, ar, ph, g = align(ids, man)
    show = np.array([man[ids[i]]["show_name"] for i in keep])
    Xk = X[keep, layer] if (model in AUDIO and layer is not None) else X[keep]
    return Xk, y, ar, ph, g, show


def _config(model_tag, best_layers):
    """Map a display tag to (feature_model, window, layer)."""
    if model_tag == "text":
        return "text", "context", None
    if model_tag == "mimi":
        return "mimi", PRIMARY, None
    return model_tag, PRIMARY, best_layers.get(model_tag)


def matched_arousal(model_tag, man, best_layers):
    """D. Stance decodable WITHIN each arousal level? (defends the arousal confound)."""
    m, w, lay = _config(model_tag, best_layers)
    a = _arrays(m, w, man, lay)
    if a is None:
        return {}
    Xk, y, ar, ph, g, show = a
    out = {}
    for lvl in ("low", "high"):
        sel = ar == lvl
        if sel.sum() < 30:
            continue
        pred = oof_predict(Xk[sel], y[sel], g[sel])
        if pred is None:
            continue
        out[lvl] = dict(f1=f1_score(y[sel], pred, average="macro"),
                        n=int(sel.sum()), maj=majority_f1(y[sel]))
    return out


def speaker_control(model_tag, man, best_layers):
    """E. Re-score grouping folds by SHOW (speaker). If F1 holds, the probe is not
    riding speaker identity (train/test never share a show)."""
    m, w, lay = _config(model_tag, best_layers)
    a = _arrays(m, w, man, lay)
    if a is None:
        return None
    Xk, y, ar, ph, g, show = a
    pe = oof_predict(Xk, y, g)          # by episode (main setting)
    ps = oof_predict(Xk, y, show)       # by show (stricter)
    return dict(episode=f1_score(y, pe, average="macro") if pe is not None else float("nan"),
                show=f1_score(y, ps, average="macro") if ps is not None else float("nan"),
                maj=majority_f1(y), n_shows=len(set(show)))


def cps(model_tag, man, best_layers, min_each=3):
    """F. Training-free Contrast-Preservation Score. Within each (show, word) cell -
    same speaker, same word - can leave-one-out nearest-centroid tell the two stances
    apart from distances alone? Pure delivery: lexis and speaker are both held fixed.
    Chance = 0.50."""
    m, w, lay = _config(model_tag, best_layers)
    a = _arrays(m, w, man, lay)
    if a is None:
        return None
    Xk, y, ar, ph, g, show = a
    Xs = StandardScaler().fit_transform(Xk)
    correct = tot = cells = 0
    for sh in set(show):
        for phrase in set(ph):
            cell = (show == sh) & (ph == phrase)
            top2 = [c for c, _ in Counter(y[cell]).most_common(2)]
            if len(top2) < 2:
                continue
            mm = cell & np.isin(y, top2)
            yc, Xc = y[mm], Xs[mm]
            if min(Counter(yc).values()) < min_each:
                continue
            cells += 1
            for i in range(len(yc)):
                keep = np.ones(len(yc), bool); keep[i] = False
                cent = {c: Xc[keep][yc[keep] == c].mean(0) for c in top2}
                pred = min(cent, key=lambda c: np.linalg.norm(Xc[i] - cent[c]))
                correct += (pred == yc[i]); tot += 1
    return dict(cps=correct / tot if tot else float("nan"), cells=cells, n=tot)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+",
                    default=["wavlm", "hubert", "whisper", "mimi", "text"])
    ap.add_argument("--perm", type=int, default=200)
    args = ap.parse_args()
    man = load_manifest()
    print(f"labelled clips in manifest: {len(man)}")
    print(f"stance dist: {dict(Counter(r['stance'] for r in man.values()))}\n")

    print("=" * 88)
    print("A. POOLED 3-WAY STANCE DECODABILITY  (primary window W2_segment)")
    print("   'chance' = mean of the empirical permutation null (probe refit on shuffled")
    print("   labels). This is the reference to judge macroF1 against. 'major' is the")
    print("   majority-class constant predictor, reported for completeness only: macro-F1")
    print("   punishes a constant predictor far harder than a no-skill probe, so it")
    print("   understates chance (0.196 here) and would flatter every model.")
    print("=" * 88)
    print(f"{'model':16s}{'layer':>6}{'macroF1':>9}{'95% CI':>16}{'chance':>8}{'perm p':>9}{'major':>8}")
    best_layers = {}
    windows_tbl = {}
    for model in args.models:
        pr, best, byw = analyze_model(model, man, args.perm)
        if model == "text":
            for variant, r in (pr or {}).items():
                if r:
                    print(f"{'text:'+variant:16s}{'-':>6}{r['f1']:>9.3f}"
                          f"{'['+format(r['lo'],'.2f')+','+format(r['hi'],'.2f')+']':>16}"
                          f"{r['chance']:>8.3f}{r['p']:>9.3f}{r['maj']:>8.3f}")
            continue
        if pr is None:
            print(f"{model:16s}  (no features found)"); continue
        best_layers[model] = best
        windows_tbl[model] = byw
        lay = str(best) if best is not None else "-"
        print(f"{model:16s}{lay:>6}{pr['f1']:>9.3f}"
              f"{'['+format(pr['lo'],'.2f')+','+format(pr['hi'],'.2f')+']':>16}"
              f"{pr['chance']:>8.3f}{pr['p']:>9.3f}{pr['maj']:>8.3f}")

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

    tags = args.models

    print("\n" + "=" * 74)
    print("D. MATCHED-AROUSAL TEST  (3-way stance decoded WITHIN each arousal level)")
    print("   stance still above majority at fixed arousal => not just loudness")
    print("=" * 74)
    print(f"{'model':16s}{'low F1':>9}{'low maj':>9}{'low n':>7}"
          f"{'high F1':>10}{'high maj':>10}{'high n':>8}")
    for t in tags:
        d = matched_arousal(t, man, best_layers)
        if not d:
            continue
        lo, hi = d.get("low", {}), d.get("high", {})
        print(f"{t:16s}{lo.get('f1',float('nan')):>9.3f}{lo.get('maj',float('nan')):>9.3f}"
              f"{lo.get('n',0):>7}{hi.get('f1',float('nan')):>10.3f}"
              f"{hi.get('maj',float('nan')):>10.3f}{hi.get('n',0):>8}")

    print("\n" + "=" * 74)
    print("E. SPEAKER-IDENTITY CONTROL  (fold-grouping by SHOW vs by episode)")
    print("   F1 holds under show-grouping => probe is not riding speaker identity")
    print("=" * 74)
    print(f"{'model':16s}{'by episode':>12}{'by show':>10}{'major':>8}{'#shows':>8}")
    for t in tags:
        r = speaker_control(t, man, best_layers)
        if not r:
            continue
        print(f"{t:16s}{r['episode']:>12.3f}{r['show']:>10.3f}{r['maj']:>8.3f}{r['n_shows']:>8}")

    print("\n" + "=" * 74)
    print("F. CONTRAST-PRESERVATION SCORE  (training-free, within speaker x word)")
    print("   leave-one-out nearest-centroid on distances alone; chance = 0.50")
    print("=" * 74)
    print(f"{'model':16s}{'CPS':>8}{'cells':>8}{'decisions':>11}")
    for t in tags:
        r = cps(t, man, best_layers)
        if not r:
            continue
        print(f"{t:16s}{r['cps']:>8.3f}{r['cells']:>8}{r['n']:>11}")


if __name__ == "__main__":
    main()
