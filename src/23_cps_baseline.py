#!/usr/bin/env python3
"""
What is the correct no-skill baseline for the contrast-preservation score?

CPS (view F of src/18_probe.py) does leave-one-out nearest-centroid classification
within each (show, phrase) cell that holds at least `min_each` exemplars of the
minority stance. It was originally reported against a stated chance level of 0.50 on
the grounds that the within-cell contrast is binary. That is wrong, because
eligibility requires only three minority exemplars, so eligible cells are
class-imbalanced and a constant predictor already beats 0.50.

There are two defensible replacements and they disagree, which is the point of this
script. The baseline depends only on labels and cell membership, never on features,
so it is computed exactly rather than estimated.

  whole-cell majority   predict each cell's most frequent class.
                        Contaminated: the held-out item's own label is counted when
                        determining which class is the majority, which is precisely
                        the leakage leave-one-out exists to prevent. Optimistic.

  leave-one-out majority  predict the most frequent class among the OTHER n-1.
                        Consistent with what the classifier under test sees, but
                        pathological on near-balanced cells, where removing an item
                        flips the majority against it and the baseline is
                        anti-correlated with the truth. Pessimistic.

Neither is clean, so the honest reading is the interval between them. If the CPS
scores fall inside that interval, the measure does not discriminate and should be
reported as uninformative rather than as either corroboration or a failure.

Usage:  python3 src/23_cps_baseline.py
"""
import csv
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SHEET = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
CLASSES = ("affiliative", "neutral", "adversarial")
MIN_EACH = 3

# CPS as reported in results/probe_results.txt, view F.
CPS = {"WavLM": 0.618, "Whisper": 0.618, "HuBERT": 0.613,
       "Text, context": 0.592, "Mimi": 0.560}


def cells(y, show, phrase, min_each=MIN_EACH):
    """Yield the label vector of each cell eligible under the CPS rule."""
    for sh in sorted(set(show)):
        for ph in sorted(set(phrase)):
            cell = (show == sh) & (phrase == ph)
            top2 = [c for c, _ in Counter(y[cell]).most_common(2)]
            if len(top2) < 2:
                continue
            yc = y[cell & np.isin(y, top2)]
            if min(Counter(yc).values()) < min_each:
                continue
            yield yc


def main():
    rows = [r for r in csv.DictReader(open(SHEET, newline=""))
            if r.get("stance", "").strip() in CLASSES]
    y = np.array([r["stance"] for r in rows])
    show = np.array([r["show_name"] for r in rows])
    phrase = np.array([r["target_phrase"] for r in rows])

    n_cells = n_dec = whole = loo = 0
    for yc in cells(y, show, phrase):
        n_cells += 1
        n_dec += len(yc)
        cnt = Counter(yc)
        whole += cnt[cnt.most_common(1)[0][0]]
        for i in range(len(yc)):
            rest = Counter(np.delete(yc, i))
            loo += rest.most_common(1)[0][0] == yc[i]

    near = sum(1 for yc in cells(y, show, phrase, min_each=2)
               if min(Counter(yc).values()) == 2)

    lo, hi = loo / n_dec, whole / n_dec
    print(f"eligible cells: {n_cells}   leave-one-out decisions: {n_dec}")
    print(f"cells exactly one exemplar short of eligibility: {near}")
    print()
    print(f"leave-one-out majority baseline : {lo:.4f}   (pessimistic)")
    print(f"whole-cell majority baseline    : {hi:.4f}   (optimistic)")
    print(f"defensible interval             : [{lo:.3f}, {hi:.3f}]")
    print()
    print(f"{'representation':16}{'CPS':>8}   verdict")
    for name, v in sorted(CPS.items(), key=lambda kv: -kv[1]):
        verdict = ("inside the interval, does not discriminate" if lo <= v <= hi
                   else "above both baselines" if v > hi else "below both baselines")
        print(f"{name:16}{v:8.3f}   {verdict}")
    print()
    inside = all(lo <= v <= hi for v in CPS.values())
    print("All representations fall inside the interval."
          if inside else "At least one representation falls outside the interval.")
    print("The measure is therefore uninformative rather than a clean null."
          if inside else "")


if __name__ == "__main__":
    main()
