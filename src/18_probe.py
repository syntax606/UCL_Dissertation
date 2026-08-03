#!/usr/bin/env python3
"""
Phase 3 probing: how decodable is pragmatic STANCE from each representation?

Linear logistic-regression probes on frozen features, with all evaluation done
out-of-fold under GroupKFold BY EPISODE (no episode's clips ever span train and
test, so nothing leaks through shared episode topic or recording session).
Reported with:
  - macro-F1 (3-way stance) out-of-fold
  - 95% CI from an EPISODE-CLUSTER bootstrap (resample whole episodes)
  - a permutation p-value, and the mean of that same permutation null, which is
    the chance level these scores should be judged against (near 0.33 here, NOT
    the 0.196 a majority-class predictor scores; see permutation_null)

Layer selection for the audio encoders is NESTED by default: the layer is chosen
inside each outer fold's training data, so the reported score never sees the
layer choice. `--layer-selection best` restores the older non-nested behaviour,
which is optimistically biased and is kept only to reproduce earlier runs.

Label permutation preserves EPISODE CLUSTERING (whole episodes' label blocks are
exchanged, rather than labels being shuffled freely), matching the bootstrap.

Nine views:
  A. Pooled 3-way stance decodability per representation, on the primary window
     W2_segment. Audio models use nested layer selection.
  A2. The same, on a subsample where stance is balanced WITHIN each phrase, so word
     identity cannot predict stance from base rates. Removes the lexical confound
     from the pooled figure.
  B. Context-window sweep (W1/W2/W3).
  C. Per-phrase WITHIN-WORD binary contrast: the lexical control. Same word,
     two stances -> can the probe still separate them? Averaged over phrases,
     and optionally split by lexical variant (bare vs "oh X" vs "yeah right").
  D. Matched-arousal test: stance decoded within each arousal level.
  E. Show-identity control: fold-grouping by show vs by episode. Note this controls
     SHOW, not speaker: shows have multiple participants and guests recur across shows.
  F. Training-free contrast-preservation score, within show x word. Its baseline is the
     within-cell majority rate, NOT 0.50 -- see cps().
  G. Layer-wise curve: where in the stack the contrast is carried (diagnostic only;
     the headline score no longer comes from the argmax of this curve).
  H. Mimi codebook-level probe: where inside the tokenizer anything survives.

Usage:
  python3 src/18_probe.py                       # all models, full analysis
  python3 src/18_probe.py --models wavlm text
  python3 src/18_probe.py --perm 0              # skip all permutation tests
  python3 src/18_probe.py --layer-selection best --perm 200   # reproduce the older run
  python3 src/18_probe.py --no-balanced         # skip view A2 (roughly halves runtime)

Cost note: nested selection costs roughly (outer folds x layers x inner folds)
model fits per audio model, ~500 for a 25-layer model. The headline permutation
test at `--perm P` costs a further P x 5 fits by default, because it permutes at
a fixed layer. `--perm-nested` makes that test exact by redoing the whole nested
selection under permutation, which multiplies its cost by ~100 -- correct, but
expect hours per model. See docs/limitations.md.
"""
import argparse, csv, hashlib, warnings
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
STANCES = ("affiliative", "neutral", "adversarial")
SEED = 42


def rng_for(tag):
    """A generator seeded from a stable tag.

    Each analysis draws from its own stream, so results do not depend on how many
    models were requested or in what order -- a single shared generator made
    `--models wavlm` and `--models wavlm text` disagree about wavlm.

    Uses md5 rather than hash(): Python randomises string hashing per process
    unless PYTHONHASHSEED is fixed, which would make this irreproducible across
    runs -- the exact failure this function exists to prevent.
    """
    digest = hashlib.md5(str(tag).encode("utf-8")).digest()[:4]
    return np.random.default_rng(
        np.random.SeedSequence([SEED, int.from_bytes(digest, "big")]))


def load_manifest():
    m = {}
    src = MANIFEST
    if not src.exists():  # fall back to the labeled sheet
        src = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
    if not src.exists():
        raise SystemExit(
            f"no label source found. Looked for {MANIFEST} and {src}.\n"
            f"Copy the shipped labels: cp labels/labels.csv manifest.csv")
    for r in csv.DictReader(open(src, newline="")):
        if r.get("stance", "").strip() in STANCES:
            m[r["candidate_id"]] = r
    return m


def balanced_manifest(man, tag="A2"):
    """Restrict to a subsample where stance is 50/50 WITHIN each phrase.

    The pooled view A is confounded by lexis: per-phrase stance base rates are
    strongly non-uniform (come_on is 72% adversarial, okay 60% neutral), so a probe
    scores above chance from word identity alone. Equalising the two commonest
    stances within each phrase removes that signal, at the cost of some clips.

    NOTE this does not reduce a word-identity probe to chance. Knowing the phrase
    still narrows the candidate stances from three to two, even when those two are
    equiprobable -- come_on is never neutral. So `text:targetonly` on this subsample
    is the empirical baseline to beat, not a guaranteed floor. It is reported in the
    same table for exactly that reason.
    """
    rng = rng_for(tag)
    by_phrase = defaultdict(lambda: defaultdict(list))
    for cid, r in man.items():
        by_phrase[r["target_phrase"]][r["stance"]].append(cid)
    keep = []
    for phrase in sorted(by_phrase):
        by_st = by_phrase[phrase]
        top2 = sorted(by_st.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:2]
        if len(top2) < 2:
            continue
        k = min(len(v) for _, v in top2)
        for _, cids in top2:
            ordered = sorted(cids)                      # deterministic before shuffling
            pick = rng.permutation(len(ordered))[:k]
            keep.extend(ordered[i] for i in pick)
    return {cid: man[cid] for cid in keep}


def variant_of(cid, row):
    """Lexical variant a clip carries, for the view-C robustness split.

    src/13b records the pull-time phrase in `target_phrase_raw`; where that column
    is absent (e.g. the shipped labels.csv) the variant is recoverable from the
    candidate_id prefix, since src/10 prefixes `oh_` and src/11 prefixes `yr_`.
    """
    raw = (row.get("target_phrase_raw") or "").strip()
    if raw.startswith("oh_"):
        return "oh"
    if raw in ("yeah_right", "yeah_sure"):
        return raw
    if cid.startswith("oh_"):
        return "oh"
    if cid.startswith("yr_"):
        return "yeah_right"
    return "bare"


def build_pipe():
    # lbfgs handles our dims (2048 audio-layer, 16384 mimi, 768 text) fine
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=3000, C=1.0, class_weight="balanced"),
    )


def _n_splits(y, groups, n_splits):
    return min(n_splits, len(set(groups)), min(Counter(y).values()))


def oof_predict(X, y, groups, n_splits=5):
    ns = _n_splits(y, groups, n_splits)
    if ns < 2:
        return None
    cv = GroupKFold(n_splits=ns)
    return cross_val_predict(build_pipe(), X, y, groups=groups, cv=cv)


def oof_predict_layered(X3, y, groups, n_splits=5, inner_splits=4):
    """Out-of-fold predictions with the LAYER CHOSEN INSIDE EACH TRAINING FOLD.

    X3 is (N, L, D). For each outer fold the layer is selected by inner GroupKFold
    on the training portion only, so the layer choice never sees the test clips.
    This is the fix for the selection bias in the older `argmax over layers, then
    report that layer's score` procedure.

    Returns (predictions, layers_chosen_per_fold).
    """
    y = np.asarray(y); groups = np.asarray(groups)
    ns = _n_splits(y, groups, n_splits)
    if ns < 2:
        return None, []
    cv = GroupKFold(n_splits=ns)
    pred = np.empty(len(y), dtype=y.dtype)
    chosen = []
    L = X3.shape[1]
    for tr, te in cv.split(X3[:, 0], y, groups):
        ytr, gtr = y[tr], groups[tr]
        ins = _n_splits(ytr, gtr, inner_splits)
        best_l, best_s = 0, -1.0
        if ins >= 2:
            icv = GroupKFold(n_splits=ins)
            for l in range(L):
                ip = cross_val_predict(build_pipe(), X3[tr][:, l], ytr,
                                       groups=gtr, cv=icv)
                s = f1_score(ytr, ip, average="macro")
                if s > best_s:
                    best_s, best_l = s, l
        model = build_pipe().fit(X3[tr][:, best_l], ytr)
        pred[te] = model.predict(X3[te][:, best_l])
        chosen.append(int(best_l))
    return pred, chosen


def permute_grouped(y, groups, rng):
    """Permute labels while PRESERVING episode clustering.

    Whole episodes' label blocks are exchanged between episodes of the same size,
    rather than labels being shuffled freely across clips. A free shuffle destroys
    the within-episode label correlation that the real data has, which makes the
    null too narrow and the p-value anticonservative. On this dataset most episodes
    contribute a single clip, so the two differ little -- but the bootstrap is
    episode-clustered and the null should match it.
    """
    y = np.asarray(y); groups = np.asarray(groups)
    idx_by_g = defaultdict(list)
    for i, g in enumerate(groups):
        idx_by_g[g].append(i)
    by_size = defaultdict(list)
    for idx in idx_by_g.values():
        by_size[len(idx)].append(idx)
    out = np.empty_like(y)
    for blocks in by_size.values():
        labels = [y[b] for b in blocks]
        order = rng.permutation(len(blocks))
        for b, j in zip(blocks, order):
            out[b] = labels[j]
    return out


def cluster_bootstrap_ci(y, pred, groups, rng, B=1000):
    groups = np.asarray(groups)
    y = np.asarray(y); pred = np.asarray(pred)
    uniq = np.unique(groups)
    idx_by_g = {g: np.where(groups == g)[0] for g in uniq}
    scores = []
    for _ in range(B):
        pick = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([idx_by_g[g] for g in pick])
        scores.append(f1_score(y[idx], pred[idx], average="macro"))
    return float(np.percentile(scores, 2.5)), float(np.percentile(scores, 97.5))


def permutation_null(X, y, groups, rng, P=200):
    """Empirical null distribution of macro-F1: refit the probe on permuted labels.

    This, not the majority-class score, is the reference a probe should be judged
    against. A constant (majority) predictor scores 0 on every class it never emits,
    so macro-F1 punishes it far harder than it punishes a genuinely no-skill probe;
    with balanced class weights our probe spreads predictions over all three classes
    and its true chance level sits near 0.33, not near 0.196.
    """
    null = []
    for _ in range(P):
        yp = permute_grouped(y, groups, rng)
        pred = oof_predict(X, yp, groups)
        if pred is not None:
            null.append(f1_score(yp, pred, average="macro"))
    return np.asarray(null)


def permutation_null_layered(X3, y, groups, rng, P=200, layer=0, nested=False):
    """Null for a layer-selected probe.

    With `nested=True` the whole nested selection is redone under each permutation,
    which is the exact null for the reported procedure but costs ~100x more. The
    default permutes at a FIXED layer, which is an approximation: it does not let
    the null benefit from layer selection, so it sits slightly low and the p-value
    is correspondingly slightly optimistic.
    """
    null = []
    for _ in range(P):
        yp = permute_grouped(y, groups, rng)
        if nested:
            pred, _ = oof_predict_layered(X3, yp, groups)
        else:
            pred = oof_predict(X3[:, layer], yp, groups)
        if pred is not None:
            null.append(f1_score(yp, pred, average="macro"))
    return np.asarray(null)


def majority_f1(y):
    """Macro-F1 of always predicting the most frequent class. Reported for
    completeness only; see permutation_null for the reference actually used."""
    y = np.asarray(y)
    maj = Counter(y).most_common(1)[0][0]
    return f1_score(y, [maj] * len(y), average="macro")


def _pval(null, f1):
    if null is None or not len(null):
        return float("nan"), float("nan")
    return (int((null >= f1).sum()) + 1) / (len(null) + 1), float(null.mean())


def load_feat(model, window, with_meta=False):
    p = FEAT / model / f"{window}.npz"
    if not p.exists():
        return None
    d = np.load(p, allow_pickle=True)
    if not with_meta:
        return list(d["ids"]), d["X"]
    meta = {}
    if "meta" in d.files:
        for item in d["meta"]:
            s = str(item)
            if "=" in s:
                k, v = s.split("=", 1)
                meta[k.strip()] = v.strip()
    return list(d["ids"]), d["X"], meta


def align(ids, man):
    keep = [i for i, cid in enumerate(ids) if cid in man]
    y = np.array([man[ids[i]]["stance"] for i in keep])
    arous = np.array([man[ids[i]].get("arousal", "") for i in keep])
    phrase = np.array([man[ids[i]]["target_phrase"] for i in keep])
    groups = np.array([man[ids[i]]["episode_id"] for i in keep])
    return np.array(keep), y, arous, phrase, groups


def eval_flat(X, y, groups, perm, rng):
    """Score a 2-D feature matrix out-of-fold, with CI and permutation null."""
    pred = oof_predict(X, y, groups)
    if pred is None:
        return None
    f1 = f1_score(y, pred, average="macro")
    lo, hi = cluster_bootstrap_ci(y, pred, groups, rng)
    null = permutation_null(X, y, groups, rng, P=perm) if perm else None
    p, chance = _pval(null, f1)
    return dict(f1=f1, lo=lo, hi=hi, p=p, chance=chance,
                maj=majority_f1(y), n=len(y), layers=None)


def eval_layered(X3, y, groups, perm, rng, nested=True, perm_nested=False):
    """Score a 3-D (N, L, D) feature stack with nested (or fixed-best) layer choice."""
    if nested:
        pred, chosen = oof_predict_layered(X3, y, groups)
        if pred is None:
            return None, None
        layer_for_null = Counter(chosen).most_common(1)[0][0]
    else:
        per_layer = layer_curve(X3, y, groups)
        layer_for_null = int(np.argmax(per_layer))
        pred = oof_predict(X3[:, layer_for_null], y, groups)
        if pred is None:
            return None, None
        chosen = [layer_for_null]
    f1 = f1_score(y, pred, average="macro")
    lo, hi = cluster_bootstrap_ci(y, pred, groups, rng)
    null = (permutation_null_layered(X3, y, groups, rng, P=perm,
                                     layer=layer_for_null, nested=perm_nested)
            if perm else None)
    p, chance = _pval(null, f1)
    return dict(f1=f1, lo=lo, hi=hi, p=p, chance=chance,
                maj=majority_f1(y), n=len(y), layers=chosen,
                exact_null=bool(perm and perm_nested)), chosen


def layer_curve(X3, y, groups):
    """Diagnostic per-layer macro-F1 (view G). NOT used to pick the reported layer."""
    out = []
    for l in range(X3.shape[1]):
        pred = oof_predict(X3[:, l], y, groups)
        out.append(f1_score(y, pred, average="macro") if pred is not None else 0.0)
    return out


def analyze_model(model, man, args):
    """Return (primary_result, layers_chosen, per_window, layer_curve)."""
    rng = rng_for(("A", model))
    if model == "text":
        out = {}
        for variant in ("targetonly", "context"):
            f = load_feat("text", variant)
            if not f:
                continue
            ids, X = f
            k, y, ar, ph, g = align(ids, man)
            out[variant] = eval_flat(X[k], y, g, args.perm, rng_for(("A", "text", variant)))
        return out, None, None, None

    f = load_feat(model, PRIMARY)
    if not f:
        return None, None, None, None
    ids, X = f
    k, y, ar, ph, g = align(ids, man)

    if model in AUDIO:
        Xk = X[k]
        primary, chosen = eval_layered(Xk, y, g, args.perm, rng,
                                       nested=(args.layer_selection == "nested"),
                                       perm_nested=args.perm_nested)
        if primary is None:
            return None, None, None, None
        curve = layer_curve(Xk, y, g)
        # window sweep at the modal chosen layer
        lay = Counter(chosen).most_common(1)[0][0]
        byw = {}
        for w in WINDOWS:
            fw = load_feat(model, w)
            if not fw:
                continue
            idw, Xw = fw
            kw, yw, _, _, gw = align(idw, man)
            r = eval_flat(Xw[kw, lay], yw, gw, 0, rng_for(("B", model, w)))
            byw[w] = r["f1"] if r else None
        return primary, chosen, byw, curve

    primary = eval_flat(X[k], y, g, args.perm, rng)          # mimi
    byw = {}
    for w in WINDOWS:
        fw = load_feat(model, w)
        if not fw:
            continue
        idw, Xw = fw
        kw, yw, _, _, gw = align(idw, man)
        r = eval_flat(Xw[kw], yw, gw, 0, rng_for(("B", model, w)))
        byw[w] = r["f1"] if r else None
    return primary, None, byw, None


def _config(model_tag, layers):
    """Map a display tag to (feature_model, window, layer)."""
    if model_tag == "text":
        return "text", "context", None
    if model_tag == "mimi":
        return "mimi", PRIMARY, None
    ch = layers.get(model_tag)
    return model_tag, PRIMARY, (Counter(ch).most_common(1)[0][0] if ch else None)


def _arrays(model, window, man, layer, ids_wanted=None):
    """Return (X, y_stance, arousal, phrase, episode, show, ids) aligned by id."""
    f = load_feat(model, window)
    if not f:
        return None
    ids, X = f
    keep, y, ar, ph, g = align(ids, man)
    show = np.array([man[ids[i]]["show_name"] for i in keep])
    cids = np.array([ids[i] for i in keep])
    Xk = X[keep, layer] if (model in AUDIO and layer is not None) else X[keep]
    return Xk, y, ar, ph, g, show, cids


def per_phrase_binary(model_tag, man, layers, perm, min_each=8, exclude_variants=()):
    """C. Within each phrase, binary contrast between its two commonest stances."""
    m, w, lay = _config(model_tag, layers)
    a = _arrays(m, w, man, lay)
    if a is None:
        return {}
    Xk, y, ar, ph, g, show, cids = a
    if exclude_variants:
        var = np.array([variant_of(c, man[c]) for c in cids])
        sel = ~np.isin(var, list(exclude_variants))
        Xk, y, ph, g, cids = Xk[sel], y[sel], ph[sel], g[sel], cids[sel]
    res = {}
    for phrase in sorted(set(ph)):
        sel = ph == phrase
        yy = y[sel]
        top2 = [c for c, _ in Counter(yy).most_common(2)]
        if len(top2) < 2:
            continue
        keep = np.isin(yy, top2)
        Xp, yp, gp = Xk[sel][keep], yy[keep], g[sel][keep]
        if min(Counter(yp).values()) < min_each:
            continue
        pred = oof_predict(Xp, yp, gp)
        if pred is None:
            continue
        f1 = f1_score(yp, pred, average="macro")
        rng = rng_for(("C", model_tag, phrase, exclude_variants))
        null = permutation_null(Xp, yp, gp, rng, P=perm) if perm else None
        p, chance = _pval(null, f1)
        res[phrase] = dict(f1=f1, classes=top2, n=len(yp),
                           maj=majority_f1(yp), p=p, chance=chance)
    return res


def matched_arousal(model_tag, man, layers, perm):
    """D. Stance decodable WITHIN each arousal level? (defends the arousal confound)."""
    m, w, lay = _config(model_tag, layers)
    a = _arrays(m, w, man, lay)
    if a is None:
        return {}
    Xk, y, ar, ph, g, show, cids = a
    out = {}
    for lvl in ("low", "high"):
        sel = ar == lvl
        if sel.sum() < 30:
            continue
        pred = oof_predict(Xk[sel], y[sel], g[sel])
        if pred is None:
            continue
        f1 = f1_score(y[sel], pred, average="macro")
        rng = rng_for(("D", model_tag, lvl))
        null = permutation_null(Xk[sel], y[sel], g[sel], rng, P=perm) if perm else None
        p, chance = _pval(null, f1)
        out[lvl] = dict(f1=f1, n=int(sel.sum()), maj=majority_f1(y[sel]),
                        p=p, chance=chance)
    return out


def speaker_control(model_tag, man, layers, perm):
    """E. Re-score grouping folds by SHOW. If F1 holds, the probe is not riding
    show-level identity, since train/test never share a show.

    This is a show control, not a speaker control: a show has a host plus guests, and
    guests recur across shows, so train and test may still share a speaker.
    """
    m, w, lay = _config(model_tag, layers)
    a = _arrays(m, w, man, lay)
    if a is None:
        return None
    Xk, y, ar, ph, g, show, cids = a
    pe = oof_predict(Xk, y, g)          # by episode (main setting)
    ps = oof_predict(Xk, y, show)       # by show (stricter)
    f1s = f1_score(y, ps, average="macro") if ps is not None else float("nan")
    rng = rng_for(("E", model_tag))
    null = permutation_null(Xk, y, show, rng, P=perm) if perm else None
    p, chance = _pval(null, f1s)
    return dict(episode=f1_score(y, pe, average="macro") if pe is not None else float("nan"),
                show=f1s, maj=majority_f1(y), n_shows=len(set(show)),
                p=p, chance=chance)


def cps(model_tag, man, layers, min_each=3, perm=200):
    """F. Training-free Contrast-Preservation Score. Within each (show, word) cell -
    same show, same word - can leave-one-out nearest-centroid tell the two stances
    apart from distances alone? Lexis and show are both held fixed.

    NOT chance = 0.50. Cell eligibility only requires `min_each` exemplars of the
    minority stance, so the qualifying cells are class-imbalanced and a coin flip is the
    wrong reference. Two references are reported:
      maj    - the within-cell majority rate, i.e. always predicting each cell's
               dominant stance over exactly the same decisions. A CPS at or below
               this is a null result.
      chance - the mean of a permutation null that shuffles stance labels WITHIN
               each cell, which preserves every cell's class balance.
    """
    m, w, lay = _config(model_tag, layers)
    a = _arrays(m, w, man, lay)
    if a is None:
        return None
    Xk, y, ar, ph, g, show, cids = a
    Xs = StandardScaler().fit_transform(Xk)

    cells = []
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
            cells.append((yc, Xc, top2))
    if not cells:
        return None

    def score(labels_per_cell):
        correct = tot = 0
        for (_, Xc, top2), yc in zip(cells, labels_per_cell):
            for i in range(len(yc)):
                keep = np.ones(len(yc), bool); keep[i] = False
                cent = {c: Xc[keep][yc[keep] == c].mean(0) for c in top2
                        if (yc[keep] == c).any()}
                if len(cent) < 2:
                    continue
                pred = min(cent, key=lambda c: np.linalg.norm(Xc[i] - cent[c]))
                correct += (pred == yc[i]); tot += 1
        return correct, tot

    obs_labels = [yc for yc, _, _ in cells]
    correct, tot = score(obs_labels)
    maj_correct = sum(max(Counter(yc).values()) for yc, _, _ in cells)

    rng = rng_for(("F", model_tag))
    null = []
    for _ in range(perm or 0):
        permuted = [rng.permutation(yc) for yc, _, _ in cells]
        c2, t2 = score(permuted)
        if t2:
            null.append(c2 / t2)
    null = np.asarray(null)
    obs = correct / tot if tot else float("nan")
    p, chance = _pval(null if len(null) else None, obs)
    return dict(cps=obs, cells=len(cells), n=tot,
                maj=maj_correct / tot if tot else float("nan"),
                p=p, chance=chance)


def mimi_codebooks(man, perm=100):
    """H. Where inside the tokenizer does anything survive? Probe each codebook alone.

    Codebook 0 is the WavLM-distilled stream, 1..7 are acoustic refinement. Chapter 2
    predicted pragmatics would more plausibly sit in 1..7, since the codec-probing
    literature shows codebook 0 is phonetic rather than semantic. The data says the
    reverse, so this view is reported as a correction to that expectation.

    The codebook size is read from the `meta` array written by src/17, rather than
    assumed to be 2048: a wrong K would silently slice the matrix into bogus blocks.
    """
    f = load_feat("mimi", PRIMARY, with_meta=True)
    if not f:
        return []
    ids, X, meta = f
    K = None
    if meta.get("K", "").isdigit():
        K = int(meta["K"])
    if not K or X.shape[1] % K:
        K = 2048
        if X.shape[1] % K:
            print(f"  (cannot determine Mimi codebook size from meta or shape "
                  f"{X.shape}; skipping view H)")
            return []
        print(f"  (no usable K in features meta; assuming K={K})")
    k, y, ar, ph, g = align(ids, man)
    Xk = X[k]
    n_cb = Xk.shape[1] // K
    out = []

    def one(tag, blk):
        pred = oof_predict(blk, y, g)
        if pred is None:
            return
        f1 = f1_score(y, pred, average="macro")
        rng = rng_for(("H", tag))
        null = permutation_null(blk, y, g, rng, P=perm) if perm else None
        p, chance = _pval(null, f1)
        out.append(dict(tag=tag, f1=f1, chance=chance, p=p))

    for j in range(n_cb):
        one(f"codebook {j}" + (" (WavLM-distilled)" if j == 0 else ""),
            Xk[:, j * K:(j + 1) * K])
    one(f"all {n_cb}, the deployed condition", Xk)
    if n_cb > 1:
        one(f"1 to {n_cb - 1}, acoustic refinement only", Xk[:, K:])
    return out


def _fmt(v, w=9, d=3):
    return f"{'':>{w}}" if v is None or (isinstance(v, float) and np.isnan(v)) \
        else f"{v:>{w}.{d}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+",
                    default=["wavlm", "hubert", "whisper", "mimi", "text"])
    ap.add_argument("--perm", type=int, default=200,
                    help="permutations for the headline views (A, H); 0 disables ALL "
                         "permutation tests")
    ap.add_argument("--perm-secondary", type=int, default=100,
                    help="permutations for views C/D/E/F (cheaper; 0 to skip)")
    ap.add_argument("--perm-nested", action="store_true",
                    help="make view A's null exact by redoing nested layer selection "
                         "under each permutation (~100x slower)")
    ap.add_argument("--layer-selection", choices=["nested", "best"], default="nested",
                    help="nested (default, unbiased) or best (legacy, optimistic)")
    ap.add_argument("--no-balanced", action="store_true",
                    help="skip view A2, the phrase-balanced subsample (roughly halves runtime)")
    args = ap.parse_args()
    if args.perm == 0:
        args.perm_secondary = 0
    perm2 = args.perm_secondary

    man = load_manifest()
    print(f"labelled clips in manifest: {len(man)}")
    print(f"stance dist: {dict(Counter(r['stance'] for r in man.values()))}")
    print(f"layer selection: {args.layer_selection}"
          f"{' (LEGACY, optimistically biased)' if args.layer_selection == 'best' else ''}"
          f" | perm A/H={args.perm} C-F={perm2}"
          f"{' | exact nested null' if args.perm_nested else ''}\n")

    print("=" * 92)
    print("A. POOLED 3-WAY STANCE DECODABILITY  (primary window W2_segment)")
    print("   'chance' = mean of the empirical permutation null (probe refit on permuted")
    print("   labels, episode blocks preserved). This is the reference to judge macroF1")
    print("   against. 'major' is the majority-class constant predictor, reported for")
    print("   completeness only: macro-F1 punishes a constant predictor far harder than a")
    print("   no-skill probe, so it understates chance (0.196 here) and would flatter")
    print("   every model. 'layers' lists the layer chosen in each outer fold.")
    print("   CAVEAT: pooled stance is partly recoverable from word identity alone")
    print("   (text:targetonly scores well above chance). View C is the lexical control.")
    print("=" * 92)
    print(f"{'model':16s}{'macroF1':>9}{'95% CI':>16}{'chance':>8}{'perm p':>9}"
          f"{'major':>8}   layers")
    layers_by_model = {}
    windows_tbl = {}
    layer_curves = {}
    for model in args.models:
        pr, chosen, byw, curve = analyze_model(model, man, args)
        if model == "text":
            for variant, r in (pr or {}).items():
                if r:
                    print(f"{'text:'+variant:16s}{r['f1']:>9.3f}"
                          f"{'['+format(r['lo'],'.2f')+','+format(r['hi'],'.2f')+']':>16}"
                          f"{_fmt(r['chance'],8)}{_fmt(r['p'],9)}{r['maj']:>8.3f}")
            continue
        if pr is None:
            print(f"{model:16s}  (no features found)"); continue
        if chosen:
            layers_by_model[model] = chosen
        windows_tbl[model] = byw
        if curve:
            layer_curves[model] = curve
        lay = ",".join(str(c) for c in chosen) if chosen else "-"
        print(f"{model:16s}{pr['f1']:>9.3f}"
              f"{'['+format(pr['lo'],'.2f')+','+format(pr['hi'],'.2f')+']':>16}"
              f"{_fmt(pr['chance'],8)}{_fmt(pr['p'],9)}{pr['maj']:>8.3f}   {lay}")
    if args.perm and not args.perm_nested and layers_by_model:
        print("\n   NOTE: the audio p-values permute at a fixed layer, so the null does not")
        print("   itself benefit from layer selection and they are slightly optimistic.")
        print("   Use --perm-nested for the exact (much slower) test.")

    if not args.no_balanced:
        man_bal = balanced_manifest(man)
        print("\n" + "=" * 92)
        print("A2. POOLED 3-WAY ON A PHRASE-BALANCED SUBSAMPLE")
        print("   Same analysis as A, but stance is equalised WITHIN each phrase, so word")
        print("   identity no longer predicts stance from base rates. Any margin the audio")
        print("   models keep here is delivery, not lexis.")
        print("   Compare each model against text:targetonly on THIS subsample -- that row")
        print("   is the word-identity-only baseline. Balancing does not force it to chance:")
        print("   knowing the phrase still narrows three stances to two.")
        print("=" * 92)
        print(f"   n = {len(man_bal)} of {len(man)} clips | "
              f"stance {dict(Counter(r['stance'] for r in man_bal.values()))}")
        print(f"{'model':16s}{'macroF1':>9}{'95% CI':>16}{'chance':>8}{'perm p':>9}"
              f"{'major':>8}   layers")
        for model in args.models:
            pr, chosen, _, _ = analyze_model(model, man_bal, args)
            if model == "text":
                for variant, r in (pr or {}).items():
                    if r:
                        print(f"{'text:'+variant:16s}{r['f1']:>9.3f}"
                              f"{'['+format(r['lo'],'.2f')+','+format(r['hi'],'.2f')+']':>16}"
                              f"{_fmt(r['chance'],8)}{_fmt(r['p'],9)}{r['maj']:>8.3f}")
                continue
            if pr is None:
                continue
            lay = ",".join(str(c) for c in chosen) if chosen else "-"
            print(f"{model:16s}{pr['f1']:>9.3f}"
                  f"{'['+format(pr['lo'],'.2f')+','+format(pr['hi'],'.2f')+']':>16}"
                  f"{_fmt(pr['chance'],8)}{_fmt(pr['p'],9)}{pr['maj']:>8.3f}   {lay}")

    print("\n" + "=" * 74)
    print("B. CONTEXT-WINDOW SWEEP  (macro-F1; audio at the modal selected layer)")
    print("=" * 74)
    print(f"{'model':16s}{'W1_local':>12}{'W2_segment':>12}{'W3_discourse':>14}")
    for model, byw in windows_tbl.items():
        if not byw:
            continue
        print(f"{model:16s}"
              f"{_fmt(byw.get('W1_local'),12)}"
              f"{_fmt(byw.get('W2_segment'),12)}"
              f"{_fmt(byw.get('W3_discourse'),14)}")

    print("\n" + "=" * 82)
    print("C. PER-PHRASE WITHIN-WORD BINARY CONTRAST  (lexical control, W2)")
    print("   The result the design's claim rests on: word held constant, stance varied.")
    print("   'chance' is the permutation null; 'maj' the majority predictor.")
    print("=" * 82)
    for model in args.models:
        tag = "text" if model == "text" else model
        phres = per_phrase_binary(tag, man, layers_by_model, perm2)
        if not phres:
            continue
        avg = np.mean([v["f1"] for v in phres.values()])
        print(f"\n{tag}  (mean over phrases: {avg:.3f})")
        for ph, v in phres.items():
            print(f"    {ph:9s} {'/'.join(c[:3] for c in v['classes']):8s} "
                  f"n={v['n']:>3}  F1={v['f1']:.3f} "
                  f" chance={_fmt(v['chance'],5)} p={_fmt(v['p'],5)} (maj {v['maj']:.3f})")

    print("\n" + "=" * 82)
    print("C2. VIEW C EXCLUDING FOLDED LEXICAL VARIANTS")
    print("   Folding (src/13b) puts 'oh come on' in the same cell as 'come on', so view C")
    print("   holds the word FAMILY constant, not the exact string. Re-running on bare")
    print("   tokens only tests whether that folding carries the result.")
    print("=" * 82)
    print(f"{'model':16s}{'all':>9}{'bare only':>12}{'delta':>9}")
    for model in args.models:
        tag = "text" if model == "text" else model
        full = per_phrase_binary(tag, man, layers_by_model, 0)
        bare = per_phrase_binary(tag, man, layers_by_model, 0,
                                 exclude_variants=("oh", "yeah_right", "yeah_sure"))
        if not full or not bare:
            continue
        shared = sorted(set(full) & set(bare))
        if not shared:
            continue
        a = np.mean([full[p]["f1"] for p in shared])
        b = np.mean([bare[p]["f1"] for p in shared])
        print(f"{tag:16s}{a:>9.3f}{b:>12.3f}{b-a:>+9.3f}   ({len(shared)} phrases)")

    tags = args.models

    print("\n" + "=" * 80)
    print("D. MATCHED-AROUSAL TEST  (3-way stance decoded WITHIN each arousal level)")
    print("   stance still decodable at fixed arousal => not just loudness.")
    print("   Judge against 'chance' (permutation null), not 'maj' -- see A.")
    print("=" * 80)
    print(f"{'model':16s}{'low F1':>9}{'low chn':>9}{'low p':>8}{'low n':>7}"
          f"{'high F1':>9}{'high chn':>10}{'high p':>8}{'high n':>8}")
    for t in tags:
        d = matched_arousal(t, man, layers_by_model, perm2)
        if not d:
            continue
        lo, hi = d.get("low", {}), d.get("high", {})
        print(f"{t:16s}{_fmt(lo.get('f1'),9)}{_fmt(lo.get('chance'),9)}"
              f"{_fmt(lo.get('p'),8)}{lo.get('n',0):>7}"
              f"{_fmt(hi.get('f1'),9)}{_fmt(hi.get('chance'),10)}"
              f"{_fmt(hi.get('p'),8)}{hi.get('n',0):>8}")

    print("\n" + "=" * 80)
    print("E. SHOW-IDENTITY CONTROL  (fold-grouping by SHOW vs by episode)")
    print("   F1 holds under show-grouping => probe is not riding SHOW identity.")
    print("   Not a speaker control: guests recur across shows.")
    print("=" * 80)
    print(f"{'model':16s}{'by episode':>12}{'by show':>10}{'chance':>9}{'p':>8}"
          f"{'major':>8}{'#shows':>8}")
    for t in tags:
        r = speaker_control(t, man, layers_by_model, perm2)
        if not r:
            continue
        print(f"{t:16s}{_fmt(r['episode'],12)}{_fmt(r['show'],10)}"
              f"{_fmt(r['chance'],9)}{_fmt(r['p'],8)}{r['maj']:>8.3f}{r['n_shows']:>8}")

    print("\n" + "=" * 84)
    print("F. CONTRAST-PRESERVATION SCORE  (training-free, within show x word)")
    print("   leave-one-out nearest-centroid on distances alone.")
    print("   The reference is NOT 0.50: eligible cells are class-imbalanced, so the")
    print("   baseline is 'cell-maj', always predicting each cell's dominant stance over")
    print("   the same decisions. CPS at or below cell-maj is a NULL result.")
    print("   'chance' permutes stance within each cell, preserving cell class balance.")
    print("=" * 84)
    print(f"{'model':16s}{'CPS':>8}{'cell-maj':>10}{'margin':>9}{'chance':>9}{'p':>8}"
          f"{'cells':>7}{'decisions':>11}")
    for t in tags:
        r = cps(t, man, layers_by_model, perm=perm2)
        if not r:
            continue
        print(f"{t:16s}{r['cps']:>8.3f}{r['maj']:>10.3f}{r['cps']-r['maj']:>+9.3f}"
              f"{_fmt(r['chance'],9)}{_fmt(r['p'],8)}{r['cells']:>7}{r['n']:>11}")

    print("\n" + "=" * 74)
    print("G. LAYER-WISE CURVE  (3-way stance macro-F1 per layer, W2_segment)")
    print("   DIAGNOSTIC ONLY: with nested selection the reported score in A is not")
    print("   the argmax of this curve. Shown to locate where the contrast is carried.")
    print("=" * 74)
    for model, curve in layer_curves.items():
        best = int(np.argmax(curve))
        picked = sorted(set(layers_by_model.get(model, [])))
        print(f"\n{model}  (curve peak L{best} at {curve[best]:.3f}; "
              f"nested folds picked L{picked})")
        for l, v in enumerate(curve):
            bar = "#" * int(round(max(v - 0.15, 0) / 0.45 * 44))
            marks = []
            if l == best:
                marks.append("peak")
            if l in picked:
                marks.append("picked")
            print(f"   L{l:>2} {v:.3f} {bar}{('  <- ' + '/'.join(marks)) if marks else ''}")

    print("\n" + "=" * 74)
    print("H. MIMI CODEBOOK-LEVEL PROBE  (W2_segment)")
    print("   codebook 0 is the WavLM-distilled stream, the rest acoustic refinement")
    print("=" * 74)
    rows_h = mimi_codebooks(man, perm=args.perm) if "mimi" in args.models else []
    if rows_h:
        print(f"{'block':36s}{'macroF1':>9}{'chance':>9}{'margin':>9}{'perm p':>9}")
        for r in rows_h:
            margin = (r['f1'] - r['chance']) if not np.isnan(r['chance']) else float("nan")
            print(f"  {r['tag']:34s}{r['f1']:>9.3f}{_fmt(r['chance'],9)}"
                  f"{_fmt(margin,9)}{_fmt(r['p'],9)}")


if __name__ == "__main__":
    main()
