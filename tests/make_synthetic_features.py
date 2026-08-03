#!/usr/bin/env python3
"""
Build FAKE features so `src/18_probe.py` can be smoke-tested without a GPU.

WHY: `features/` is not committed (>100 MB per file) and re-extracting it needs the
audio. That makes it easy to discover a crash in `src/18` only after renting a GPU.
This writes a synthetic `features/` with the same contract `src/17` produces -- same
paths, same `ids`/`X` keys, same 3-D layout for the audio models, same `meta` entry
for Mimi -- so the whole analysis can be exercised end to end in a few minutes.

THE NUMBERS IT PRODUCES ARE MEANINGLESS. Signal is injected deliberately so the
probes have something to find; the scores reflect the injection, not any model.
Never cite output produced from these features.

Usage:
    python3 tests/make_synthetic_features.py
    cp labels/labels.csv manifest.csv
    python3 src/18_probe.py --perm 20 --perm-secondary 10     # a few minutes
    rm -rf features manifest.csv                              # clean up

Dimensionality is reduced (64 instead of 2048) to keep the run fast; the layer
counts (25/25/13) and Mimi's codebook structure are kept faithful, because those
are what the analysis code actually branches on.
"""
import csv
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
LABELS = ROOT / "labels" / "labels.csv"
FEAT = ROOT / "features"
STANCES = ("affiliative", "neutral", "adversarial")
DIM = 64          # stand-in for 2048 / 1536
K, NCB = 32, 8    # stand-in for Mimi's 2048 x 8

rows = [r for r in csv.DictReader(open(LABELS, newline=""))
        if r["stance"] in STANCES]
ids = [r["candidate_id"] for r in rows]
y = np.array([r["stance"] for r in rows])
ph = np.array([r["target_phrase"] for r in rows])
n = len(ids)
rng = np.random.default_rng(0)
S_IDX = {s: i for i, s in enumerate(STANCES)}
P_IDX = {p: i for i, p in enumerate(sorted(set(ph)))}


def _inject(X, stance_gain, phrase_gain):
    """Put stance signal in the first dims and word identity in later dims.

    Encoding word identity matters: it reproduces the real confound where a probe
    can score above chance from lexis alone, so views C and C2 get exercised.
    """
    for s, i in S_IDX.items():
        X[y == s, i * 3:(i + 1) * 3] += stance_gain
    for p, i in P_IDX.items():
        X[ph == p, 40 + i] += phrase_gain
    return X


def stack(n_layers, dim, stance_gain, phrase_gain=0.4):
    X = rng.normal(size=(n, n_layers, dim)).astype(np.float32)
    for l in range(n_layers):
        _inject(X[:, l], stance_gain * (l + 1) / n_layers, phrase_gain)
    return X


def flat(dim, stance_gain, phrase_gain=0.4):
    return _inject(rng.normal(size=(n, dim)).astype(np.float32),
                   stance_gain, phrase_gain)


def save(path, X, meta=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    kw = dict(ids=np.array(ids), X=X)
    if meta is not None:
        kw["meta"] = meta
    np.savez_compressed(path, **kw)


for model, L in (("wavlm", 25), ("hubert", 25), ("whisper", 13)):
    for w in ("W1_local", "W2_segment", "W3_discourse"):
        save(FEAT / model / f"{w}.npz", stack(L, DIM, 0.9))

for w in ("W1_local", "W2_segment", "W3_discourse"):
    save(FEAT / "mimi" / f"{w}.npz", flat(K * NCB, 0.35),
         meta=np.array([f"codebooks={list(range(NCB))}", f"K={K}"]))

# target-only encodes ONLY word identity, mirroring the real baseline
save(FEAT / "text" / "targetonly.npz", flat(DIM, 0.0, 1.2))
save(FEAT / "text" / "context.npz", flat(DIM, 0.5))

print(f"wrote synthetic features for {n} clips under {FEAT}")
print("NOTE: scores from these features are meaningless. Delete when done:")
print("  rm -rf features manifest.csv")
