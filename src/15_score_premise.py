#!/usr/bin/env python3
"""
Score the premise check once both auxiliary annotators return their JSON.

Compares each clip's transcript-only judgment and audio+transcript judgment
(pooled across the two counterbalanced annotators) against your hidden reference
stance in premise_key.csv.

Reports, per condition: accuracy vs reference, Cohen's kappa, and unsure rate.
Go/no-go read:
  audio agrees well AND transcript-only near chance  -> contrast is speech-borne, PROCEED
  transcript-only also agrees well                   -> meaning is text-recoverable, revise framing
  audio does NOT agree well                          -> labels/contrast weak, investigate before compute

Usage:  python3 src/15_score_premise.py premise_aux1.json premise_aux2.json
"""
import csv, json, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY = ROOT / "data" / "annotations" / "premise_key.csv"
CLASSES = ["affiliative", "neutral", "adversarial"]


def kappa(pairs):
    pairs = [(a, b) for a, b in pairs if a in CLASSES and b in CLASSES]
    n = len(pairs)
    if n == 0:
        return float("nan")
    po = sum(a == b for a, b in pairs) / n
    ca = Counter(a for a, _ in pairs); cb = Counter(b for _, b in pairs)
    pe = sum((ca[c] / n) * (cb[c] / n) for c in CLASSES)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def main(argv):
    if len(argv) < 2:
        sys.exit("pass the two exported JSONs: premise_aux1.json premise_aux2.json")
    ref = {r["candidate_id"]: r["reference_stance"] for r in csv.DictReader(open(KEY, newline=""))}
    # gather judgments by condition
    text_j, audio_j = {}, {}   # cid -> stance
    for p in argv:
        obj = json.load(open(p))
        for cid, v in obj.get("answers", obj).items():
            (audio_j if v.get("condition") == "audio" else text_j)[cid] = v.get("stance")

    def report(name, judged):
        pairs = [(ref[c], judged[c]) for c in judged if c in ref]
        unsure = sum(1 for _, j in pairs if j == "unsure")
        scored = [(a, b) for a, b in pairs if b != "unsure"]
        acc = sum(a == b for a, b in scored) / len(scored) if scored else float("nan")
        print(f"  {name:16s} n={len(pairs):>3}  unsure={unsure:>2}  "
              f"accuracy={acc:.2f}  kappa={kappa(pairs):.2f}")
        return acc

    print(f"reference clips: {len(ref)} | transcript-only judged: {len(text_j)} | audio judged: {len(audio_j)}\n")
    print("condition          n  unsure  acc   kappa")
    t_acc = report("transcript-only", text_j)
    a_acc = report("audio+transcript", audio_j)
    print(f"\n  (3-way chance accuracy ~= 0.33)\n")

    if a_acc >= 0.65 and t_acc <= 0.50:
        print("VERDICT: contrast is speech-borne (audio recovers it, transcript near chance). PROCEED.")
    elif t_acc >= 0.65:
        print("VERDICT: meaning is text-recoverable (transcript agrees well). Revise framing before compute.")
    elif a_acc < 0.55:
        print("VERDICT: audio agreement is weak. Investigate labels/contrast before spending compute.")
    else:
        print("VERDICT: ambiguous. Consider enlarging the subset before deciding.")

    # per-phrase peek (audio condition)
    key_phrase = {r["candidate_id"]: r["target_phrase"] for r in csv.DictReader(open(KEY, newline=""))}
    byp = defaultdict(lambda: [0, 0])
    for c, j in audio_j.items():
        if c in ref and j in CLASSES:
            byp[key_phrase[c]][0] += (ref[c] == j); byp[key_phrase[c]][1] += 1
    print("\n  audio accuracy by phrase:")
    for ph, (ok, tot) in sorted(byp.items()):
        print(f"    {ph:9s} {ok}/{tot}")


if __name__ == "__main__":
    main(sys.argv[1:])
