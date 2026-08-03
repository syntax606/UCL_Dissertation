#!/usr/bin/env python3
"""
Fold the targeted-pull target_phrase values back into the eight base phrases.

WHY THIS EXISTS
---------------
`src/10`, `src/11` and `src/12` emit their own `target_phrase` values, and the
published per-phrase analysis (view C in `src/18_probe.py`) reports eight base
phrases. The step that reconciled the two was originally done by hand and was not
committed, which made the per-phrase cells irreproducible from this repository.
This script reconstructs it.

WHAT ACTUALLY NEEDS FOLDING
---------------------------
Less than it looks. `src/12` assigns `target_phrase = --label` at pull time, so
its clips already carry a base phrase and are untouched here. Only two rules fire:

  1. `oh_<base>`   -> `<base>`    (src/10, 143 clips in the published set)
  2. `yeah_right`  -> `right`     (src/11,  25 clips)

A third rule is included for the `--label yeah_sure` form shown in the `src/12`
docstring, which folds to `sure` if it was ever used.

The pre-fold value is preserved in a new `target_phrase_raw` column. That matters
for interpretation: after folding, a cell such as `come_on` contains both bare
"come on" and "oh come on", so view C holds the word *family* constant rather than
the exact string. Keeping the raw value lets that be measured instead of assumed.

USAGE
-----
  # fold in place (writes <sheet> and keeps a .prefold backup)
  python3 src/13b_fold_target_phrases.py

  # explicit paths
  python3 src/13b_fold_target_phrases.py --in <sheet>.csv --out <folded>.csv

  # verify the rules reproduce the shipped labels (no audio, no features needed)
  python3 src/13b_fold_target_phrases.py --verify labels/labels.csv

Run after `src/13_ingest_annotations.py` and before `src/17_extract_features.py`.
"""
import argparse, csv, shutil, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SHEET = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"

BASE_PHRASES = ("yeah", "okay", "right", "sure", "great", "fine", "really", "come_on")

# Compound labels emitted by src/11 and src/12 that are not base phrases.
# "yeah right" is the canonical sarcastic use of *right*, so it folds to right.
COMPOUND_FOLD = {
    "yeah_right": "right",
    "yeah_sure": "sure",
}


def fold_phrase(target_phrase):
    """Map a pull-time target_phrase to its base phrase. Identity if already base."""
    tp = (target_phrase or "").strip()
    if tp.startswith("oh_"):                 # src/10: oh_yeah -> yeah
        tp = tp[len("oh_"):]
    return COMPOUND_FOLD.get(tp, tp)


def _prefold_from_id(candidate_id, folded_phrase):
    """Reconstruct the pull-time target_phrase from a clip id, for verification.

    src/10 prefixes ids with `oh_` and labelled them `oh_<base>`; src/11 prefixes
    with `yr_` and labelled them `yeah_right`. Everything else already carried a
    base phrase, so its pre-fold value equals its folded value.
    """
    if candidate_id.startswith("oh_"):
        return "oh_" + folded_phrase
    if candidate_id.startswith("yr_"):
        return "yeah_right"
    return folded_phrase


def verify(path):
    """Check that fold_phrase() reproduces the phrase column of a shipped labels file."""
    rows = list(csv.DictReader(open(path, newline="")))
    labelled = [r for r in rows
                if r.get("stance", "").strip() in ("affiliative", "neutral", "adversarial")]
    bad, folded_n = [], 0
    for r in labelled:
        final = r["target_phrase"]
        pre = _prefold_from_id(r["candidate_id"], final)
        got = fold_phrase(pre)
        if pre != final:
            folded_n += 1
        if got != final:
            bad.append((r["candidate_id"], pre, got, final))

    print(f"verifying against {path}")
    print(f"  labelled clips        : {len(labelled)}")
    print(f"  clips requiring a fold: {folded_n}")
    print(f"  mismatches            : {len(bad)}")
    for cid, pre, got, final in bad[:10]:
        print(f"    {cid}\n      pre-fold={pre!r} folded={got!r} expected={final!r}")

    off_base = Counter(r["target_phrase"] for r in labelled
                       if r["target_phrase"] not in BASE_PHRASES)
    if off_base:
        print(f"  WARNING non-base phrases remain: {dict(off_base)}")

    print(f"\n  phrase counts after fold: "
          f"{dict(sorted(Counter(r['target_phrase'] for r in labelled).items()))}")
    if bad or off_base:
        print("\nFAIL: the fold rules do not reproduce this labels file.")
        return 1
    print("\nOK: the fold rules reproduce this labels file exactly.")
    return 0


def apply_fold(in_path, out_path, backup):
    rows = list(csv.DictReader(open(in_path, newline="")))
    if not rows:
        sys.exit(f"no rows in {in_path}")
    cols = list(rows[0].keys())
    if "target_phrase_raw" not in cols:
        cols.insert(cols.index("target_phrase") + 1, "target_phrase_raw")

    changed = Counter()
    for r in rows:
        raw = r["target_phrase"]
        new = fold_phrase(raw)
        r["target_phrase_raw"] = r.get("target_phrase_raw") or raw
        r["target_phrase"] = new
        if new != raw:
            changed[f"{raw} -> {new}"] += 1

    if backup and in_path == out_path:
        bak = Path(str(in_path) + ".prefold")
        if not bak.exists():
            shutil.copy2(in_path, bak)
            print(f"backed up original to {bak.name}")

    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {out_path}  ({len(rows)} rows, {sum(changed.values())} folded)")
    for k, v in sorted(changed.items()):
        print(f"  {k:24s} {v}")
    leftover = Counter(r["target_phrase"] for r in rows
                       if r["target_phrase"] and r["target_phrase"] not in BASE_PHRASES)
    if leftover:
        print(f"  WARNING non-base phrases remain (add a COMPOUND_FOLD rule): {dict(leftover)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default=str(DEFAULT_SHEET))
    ap.add_argument("--out", dest="out", default=None, help="default: in place")
    ap.add_argument("--verify", metavar="LABELS_CSV",
                    help="check the rules against a labels file and exit")
    ap.add_argument("--no-backup", action="store_true")
    args = ap.parse_args()

    if args.verify:
        sys.exit(verify(args.verify))
    inp = Path(args.inp)
    if not inp.exists():
        sys.exit(f"not found: {inp}\n(run src/13_ingest_annotations.py first, "
                 f"or pass --verify labels/labels.csv to check the rules)")
    apply_fold(inp, Path(args.out) if args.out else inp, backup=not args.no_backup)


if __name__ == "__main__":
    main()
