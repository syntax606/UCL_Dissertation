#!/usr/bin/env python3
"""
Merge exported offline-annotator JSON back into the annotation sheet.

Reads one or more annotations_batch_*.json files and writes
data/annotations/annotation_sheet_labeled.csv with the new columns:
  fine_tag, stance, arousal, literal, confidence, secondary, discarded,
  discard_reason, notes, status
The original annotation_sheet.csv is left untouched.

Usage:
  python3 src/08_merge_offline_annotations.py ~/Downloads/annotations_batch_*.json
"""
import csv, glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEET = os.path.join(ROOT, "data", "annotations", "annotation_sheet.csv")
OUT = os.path.join(ROOT, "data", "annotations", "annotation_sheet_labeled.csv")

NEW_COLS = ["fine_tag", "stance", "arousal", "literal", "confidence",
            "secondary", "discarded", "discard_reason", "notes"]


def main(argv):
    paths = []
    for a in argv:
        paths.extend(glob.glob(os.path.expanduser(a)))
    if not paths:
        sys.exit("no JSON files matched")

    merged = {}  # candidate_id -> record (last writer wins, by ts)
    for p in paths:
        obj = json.load(open(p))
        anns = obj.get("annotations", obj)
        for cid, r in anns.items():
            prev = merged.get(cid)
            if prev is None or r.get("ts", 0) >= prev.get("ts", 0):
                merged[cid] = r
    print(f"loaded {len(merged)} annotations from {len(paths)} file(s)")

    rows = list(csv.DictReader(open(SHEET, newline="")))
    base_cols = rows[0].keys() if rows else []
    out_cols = list(dict.fromkeys(list(base_cols) + NEW_COLS))

    n_lab = n_disc = 0
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out_cols)
        w.writeheader()
        for row in rows:
            r = merged.get(row["candidate_id"])
            if r:
                if r.get("discarded"):
                    row["discarded"] = "1"; row["discard_reason"] = r.get("discard_reason", ""); row["status"] = "discarded"; n_disc += 1
                elif r.get("fine_tag"):
                    row["fine_tag"] = r.get("fine_tag", "")
                    row["stance"] = r.get("stance", "")
                    row["arousal"] = r.get("arousal", "")
                    row["literal"] = "1" if r.get("literal") else ("0" if "literal" in r else "")
                    row["confidence"] = r.get("confidence", "")
                    row["secondary"] = r.get("secondary", "")
                    row["notes"] = r.get("notes", "")
                    # keep legacy 'label' column populated with the derived binary
                    row["label"] = "literal_affiliative" if r.get("literal") else "nonliteral"
                    row["status"] = "reviewed"; n_lab += 1
            w.writerow(row)
    print(f"wrote {OUT}\n  {n_lab} labeled, {n_disc} discarded")


if __name__ == "__main__":
    main(sys.argv[1:])
