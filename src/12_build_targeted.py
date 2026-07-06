#!/usr/bin/env python3
"""
Generic targeted pull: find segments matching given text patterns, center a clip
on an anchor span, optionally require pause-isolation, write a sheet + append master.

Examples:
  # "yeah sure" bigram, standalone-preferred, fold to 'sure' later
  python3 src/12_build_targeted.py --label yeah_sure --idprefix ys --anchor "yeah sure" \
      --pause 0.20 --target 40 --patterns "\byeah,?\s+sure\b"

  # encouraging come_on (runs on -> no pause requirement), joins 'come_on' directly
  python3 src/12_build_targeted.py --label come_on --idprefix coa --anchor "come on" \
      --pause 0 --target 40 --patterns "\bcome on,?\s+you can do it\b" "\bcome on,?\s+let[’']?s go\b"

  # sincere/accepting fine, joins 'fine' directly
  python3 src/12_build_targeted.py --label fine --idprefix fa --anchor "fine" \
      --pause 0 --target 40 --patterns "\bfine by me\b" "\bthat[’']?s fine\b" "\bfine with me\b"
"""
import argparse, csv, random, re, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from importlib import import_module
oh = import_module("10_build_oh_topup")

ROOT = Path.home() / "Desktop" / "pragmatic_contrast"
POOL = ROOT / "candidate_targets_filtered.csv"
MASTER = ROOT / "data" / "annotations" / "annotation_sheet.csv"
CLIPS_DIR = ROOT / "data" / "clips"
W_HALF = {"W1_local": 3.0, "W2_segment": 5.0, "W3_discourse": 8.0}
BIG = 9.9
SEED = 42

_seg_cache = {}
def cached_segs(show, ep):
    k = (show, ep)
    if k not in _seg_cache:
        _seg_cache[k] = oh.load_segs(show, ep)
    return _seg_cache[k]


def locate(segs, seg_start, anchor_tokens, pause_min):
    idx = next((i for i, s in enumerate(segs) if abs(s["start"] - seg_start) < 0.1), None)
    if idx is None or "words" not in segs[idx]:
        return None, None
    words = segs[idx]["words"]
    n = len(anchor_tokens)
    for i in range(len(words) - n + 1):
        if [oh.clean(words[i + k]["word"]) for k in range(n)] != anchor_tokens:
            continue
        first, last = words[i], words[i + n - 1]
        center = (first["start"] + last["end"]) / 2.0
        if pause_min <= 0:
            return center, True
        gap_b = (segs[idx]["start"] - segs[idx - 1]["end"]) if i == 0 and idx > 0 else (BIG if i == 0 else first["start"] - words[i - 1]["end"])
        li = i + n - 1
        gap_a = (segs[idx + 1]["start"] - segs[idx]["end"]) if li == len(words) - 1 and idx + 1 < len(segs) else (BIG if li == len(words) - 1 else words[li + 1]["start"] - last["end"])
        return center, (gap_b >= pause_min and gap_a >= pause_min)
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--patterns", nargs="+", required=True)
    ap.add_argument("--anchor", required=True, help="space-separated words to center on")
    ap.add_argument("--label", required=True, help="target_phrase to assign")
    ap.add_argument("--idprefix", required=True)
    ap.add_argument("--pause", type=float, default=0.0)
    ap.add_argument("--target", type=int, default=40)
    ap.add_argument("--shows", nargs="*", default=[], help="restrict to these exact show_name values")
    args = ap.parse_args()
    show_set = set(args.shows)
    random.seed(SEED)
    pats = [re.compile(p) for p in args.patterns]
    anchor = args.anchor.split()

    rows = list(csv.DictReader(open(MASTER, newline="")))
    seen_segs = {(r["episode_id"], r["seg_start"]) for r in rows}

    by_seg = {}
    with open(POOL, newline="") as f:
        for r in csv.DictReader(f):
            if show_set and r["show_name"] not in show_set:
                continue
            t = (r["segment_text"] or "").lower().replace("’", "'")
            if not any(p.search(t) for p in pats):
                continue
            key = (r["episode_id"], r["seg_start"])
            if key in seen_segs or key in by_seg:
                continue
            by_seg[key] = r
    cands = list(by_seg.values())
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
    print(f'[{args.label}] matched {len(queue)} unseen segments')

    cols = ["candidate_id", "target_phrase", "episode_id", "show_name", "seg_start", "seg_end",
            "duration", "segment_text", "prev_text", "next_text", "audio_path", "status", "label", "confidence", "notes"]

    def emit(r, center, standalone):
        ap_ = oh.find_audio(r["show_name"], r["episode_id"])
        if not ap_:
            return None
        cid = args.idprefix + "_" + r["candidate_id"]
        paths = {wd: CLIPS_DIR / wd / (cid + ".wav") for wd in W_HALF}
        if not all(oh.extract(ap_, center, W_HALF[wd], paths[wd]) for wd in W_HALF):
            return None
        return {"candidate_id": cid, "target_phrase": args.label, "episode_id": r["episode_id"],
                "show_name": r["show_name"], "seg_start": r["seg_start"], "seg_end": r["seg_end"],
                "duration": r.get("duration", ""), "segment_text": r["segment_text"],
                "prev_text": r["prev_text"], "next_text": r["next_text"],
                "audio_path": str(paths["W1_local"]), "status": "unreviewed",
                "label": "", "confidence": "", "notes": ("standalone" if standalone else "embedded") if args.pause > 0 else ""}

    out, hold = [], []
    for r in queue:
        if len(out) >= args.target:
            break
        segs = cached_segs(r["show_name"], r["episode_id"])
        if not segs:
            continue
        center, standalone = locate(segs, float(r["seg_start"]), anchor, args.pause)
        if center is None:
            continue
        if args.pause > 0 and not standalone:
            hold.append((r, center)); continue
        row = emit(r, center, standalone)
        if row:
            out.append(row)
    n_sa = len(out)
    for r, center in hold:  # top up with embedded only if pause-filtered and short
        if len(out) >= args.target:
            break
        row = emit(r, center, False)
        if row:
            out.append(row)
    extra = f" (standalone {n_sa}, embedded {len(out)-n_sa})" if args.pause > 0 else ""
    print(f"[{args.label}] extracted {len(out)}{extra}")

    sheet = ROOT / "data" / "annotations" / f"annotation_sheet_{args.idprefix}.csv"
    with open(sheet, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)
    with open(MASTER, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writerows(out)
    print(f"[{args.label}] wrote {sheet.name} ({len(out)}) and appended to master")


if __name__ == "__main__":
    main()
