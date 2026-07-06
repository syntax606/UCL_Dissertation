#!/usr/bin/env python3
"""
Persistent annotation store (the running tally). Stdlib only (sqlite3 + csv + json).

annotations.db holds ONE row per candidate_id, the latest label record
(newest ts wins). Each round you ingest whatever export JSONs exist; the store
accumulates and never loses prior labels regardless of which folder the JSONs
sit in. Ingest is idempotent: re-ingesting the same file changes nothing.

After ingest it re-derives data/annotations/annotation_sheet_labeled.csv by
joining the store onto the master candidate sheet, so the labeled sheet is a
projection of the store, not of whichever JSONs happen to be lying around.

Usage:
  python3 src/13_ingest_annotations.py "<folder>/*.json" ["<folder2>/*.json" ...]
  python3 src/13_ingest_annotations.py            # no args: report + re-derive only
"""
import csv, glob, json, os, sqlite3, sys
from pathlib import Path

ROOT = Path.home() / "Desktop" / "pragmatic_contrast"
STORE = str(ROOT / "annotations.db")
MASTER = ROOT / "data" / "annotations" / "annotation_sheet.csv"
LABELED = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
FIELDS = ["fine_tag", "stance", "arousal", "literal", "confidence", "secondary", "notes", "discarded", "discard_reason"]


def connect():
    con = sqlite3.connect(STORE)
    con.execute("""CREATE TABLE IF NOT EXISTS annotations (
        candidate_id TEXT PRIMARY KEY, fine_tag TEXT, stance TEXT, arousal TEXT,
        literal INTEGER, confidence TEXT, secondary TEXT, notes TEXT,
        discarded INTEGER, discard_reason TEXT, ts INTEGER, source TEXT)""")
    return con


def ingest(con, paths):
    cur = con.cursor()
    added = updated = skipped = 0
    for pat in paths:
        for p in glob.glob(os.path.expanduser(pat)):
            try:
                anns = json.load(open(p)).get("annotations", {})
            except Exception:
                continue
            src = os.path.basename(p)
            for cid, v in anns.items():
                ts = int(v.get("ts", 0) or 0)
                row = cur.execute("SELECT ts FROM annotations WHERE candidate_id=?", (cid,)).fetchone()
                if row is None:
                    added += 1
                elif ts >= row[0]:
                    updated += 1
                else:
                    skipped += 1
                    continue
                cur.execute("""INSERT OR REPLACE INTO annotations
                    (candidate_id, fine_tag, stance, arousal, literal, confidence, secondary, notes, discarded, discard_reason, ts, source)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (cid, v.get("fine_tag"), v.get("stance"), v.get("arousal"),
                     1 if v.get("literal") else (0 if "literal" in v else None),
                     v.get("confidence"), v.get("secondary"), v.get("notes"),
                     1 if v.get("discarded") else 0, v.get("discard_reason"), ts, src))
    con.commit()
    print(f"ingest: +{added} new, {updated} updated, {skipped} older-skipped")


def derive(con):
    cur = con.cursor()
    store = {r[0]: r for r in cur.execute("SELECT candidate_id, fine_tag, stance, arousal, literal, confidence, secondary, notes, discarded, discard_reason FROM annotations")}
    if not MASTER.exists():
        return
    rows = list(csv.DictReader(open(MASTER, newline="")))
    base = list(rows[0].keys())
    extra = [c for c in ["fine_tag", "stance", "arousal", "literal", "confidence", "secondary", "discarded", "discard_reason", "notes"] if c not in base]
    cols = base + extra
    with open(LABELED, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in rows:
            rec = {c: r.get(c, "") for c in cols}
            s = store.get(r["candidate_id"])
            if s:
                _, fine, stance, arousal, literal, conf, sec, notes, disc, reason = s
                if fine:
                    rec.update(status="reviewed", fine_tag=fine, stance=stance, arousal=arousal,
                               confidence=conf or "", secondary=sec or "", notes=notes or "",
                               literal="1" if literal else "0",
                               label="literal_affiliative" if literal else "nonliteral")
                elif disc:
                    rec.update(status="discarded", discard_reason=reason or "")
            w.writerow(rec)
    print(f"re-derived {LABELED.name} from store")


def main(argv):
    con = connect()
    if argv:
        ingest(con, argv)
    n = con.execute("SELECT COUNT(*) FROM annotations").fetchone()[0]
    lab = con.execute("SELECT COUNT(*) FROM annotations WHERE fine_tag IS NOT NULL AND fine_tag<>''").fetchone()[0]
    disc = con.execute("SELECT COUNT(*) FROM annotations WHERE discarded=1 AND (fine_tag IS NULL OR fine_tag='')").fetchone()[0]
    print(f"STORE: {n} clips | labeled {lab} | discarded {disc}")
    derive(con)
    con.close()


if __name__ == "__main__":
    main(sys.argv[1:])
