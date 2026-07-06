#!/usr/bin/env python3
"""
Dedicated pull of the canonical sarcasm collocation "yeah right".

Finds segments containing the bigram "yeah right", centers a clip on the
"yeah right" span, and prefers tokens that are pause-isolated (a silence gap
before "yeah" and after "right", i.e. a standalone intonation unit). Falls back
to embedded "yeah right" only if standalone tokens run short of --target.

target_phrase = 'yeah_right' (fold into a base category at merge time, like the
oh-clips). notes records 'standalone' or 'embedded'.

Usage:  python3 src/11_build_yeahright.py [--pause 0.20] [--target 50]
"""
import argparse, csv, random, re, subprocess, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from importlib import import_module
oh = import_module("10_build_oh_topup")  # reuse find_audio, clean, load_segs, extract

ROOT = Path.home() / "Desktop" / "pragmatic_contrast"
POOL = ROOT / "candidate_targets_filtered.csv"
MASTER = ROOT / "data" / "annotations" / "annotation_sheet.csv"
OUT_SHEET = ROOT / "data" / "annotations" / "annotation_sheet_yeahright.csv"
CLIPS_DIR = ROOT / "data" / "clips"
W_HALF = {"W1_local": 3.0, "W2_segment": 5.0, "W3_discourse": 8.0}
BIG = 9.9
SEED = 42
PAT = re.compile(r"\byeah,?\s+right\b")


def locate_yr(segs, seg_start, pause_min):
    idx = next((i for i, s in enumerate(segs) if abs(s["start"] - seg_start) < 0.1), None)
    if idx is None or "words" not in segs[idx]:
        return None, None
    words = segs[idx]["words"]
    for i in range(len(words) - 1):
        if oh.clean(words[i]["word"]) == "yeah" and oh.clean(words[i + 1]["word"]) == "right":
            y, r = words[i], words[i + 1]
            center = (y["start"] + r["end"]) / 2.0
            gap_b = (segs[idx]["start"] - segs[idx - 1]["end"]) if i == 0 and idx > 0 else (BIG if i == 0 else y["start"] - words[i - 1]["end"])
            li = i + 1
            gap_a = (segs[idx + 1]["start"] - segs[idx]["end"]) if li == len(words) - 1 and idx + 1 < len(segs) else (BIG if li == len(words) - 1 else words[li + 1]["start"] - r["end"])
            return center, (gap_b >= pause_min and gap_a >= pause_min)
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pause", type=float, default=0.20)
    ap.add_argument("--target", type=int, default=50)
    args = ap.parse_args()
    random.seed(SEED)

    seen = {r["candidate_id"] for r in csv.DictReader(open(MASTER, newline=""))}
    # one row per segment containing "yeah right"
    by_seg = {}
    with open(POOL, newline="") as f:
        for r in csv.DictReader(f):
            if r["target_phrase"] not in ("yeah", "right"):
                continue
            if not PAT.search((r["segment_text"] or "").lower()):
                continue
            key = (r["episode_id"], r["seg_start"])
            if key not in by_seg and ("yr_" + r["candidate_id"]) not in seen:
                by_seg[key] = r
    cands = list(by_seg.values())
    # show-balanced order
    bys = defaultdict(list)
    for r in cands:
        bys[r["show_name"]].append(r)
    for s in bys:
        random.shuffle(bys[s])
    order = list(bys); random.shuffle(order)
    queue, i = [], 0
    while any(i < len(bys[s]) for s in order):
        for s in order:
            if i < len(bys[s]):
                queue.append(bys[s][i])
        i += 1
    print(f'"yeah right" candidate segments: {len(queue)}')

    cols = ["candidate_id", "target_phrase", "episode_id", "show_name", "seg_start", "seg_end",
            "duration", "segment_text", "prev_text", "next_text", "audio_path", "status", "label", "confidence", "notes"]

    def do_extract(r, standalone, center):
        cid = "yr_" + r["candidate_id"]
        paths = {wd: CLIPS_DIR / wd / (cid + ".wav") for wd in W_HALF}
        if not all(oh.extract(ap_, center, W_HALF[wd], paths[wd]) for ap_ in [oh.find_audio(r["show_name"], r["episode_id"])] for wd in W_HALF):
            return None
        return {"candidate_id": cid, "target_phrase": "yeah_right", "episode_id": r["episode_id"],
                "show_name": r["show_name"], "seg_start": r["seg_start"], "seg_end": r["seg_end"],
                "duration": r.get("duration", ""), "segment_text": r["segment_text"],
                "prev_text": r["prev_text"], "next_text": r["next_text"],
                "audio_path": str(paths["W1_local"]), "status": "unreviewed",
                "label": "", "confidence": "", "notes": "standalone" if standalone else "embedded"}

    out_rows, embedded_hold = [], []
    for r in queue:
        if len(out_rows) >= args.target:
            break
        ap_ = oh.find_audio(r["show_name"], r["episode_id"])
        segs = oh.load_segs(r["show_name"], r["episode_id"]) if ap_ else None
        if not segs:
            continue
        center, standalone = locate_yr(segs, float(r["seg_start"]), args.pause)
        if center is None:
            continue
        if standalone:
            row = do_extract(r, True, center)
            if row:
                out_rows.append(row)
        else:
            embedded_hold.append((r, center))
    # top up with embedded if standalone ran short
    short = args.target - len(out_rows)
    n_standalone = len(out_rows)
    for r, center in embedded_hold:
        if len(out_rows) >= args.target:
            break
        row = do_extract(r, False, center)
        if row:
            out_rows.append(row)
    print(f"extracted {len(out_rows)}  (standalone {n_standalone}, embedded {len(out_rows)-n_standalone})")

    with open(OUT_SHEET, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out_rows)
    with open(MASTER, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writerows(out_rows)
    print(f"wrote {OUT_SHEET} ({len(out_rows)} rows) and appended to master")


if __name__ == "__main__":
    main()
