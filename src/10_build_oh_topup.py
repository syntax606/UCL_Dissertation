#!/usr/bin/env python3
"""
Build an 'oh'-prefaced, pause-isolated candidate set.

For each base phrase, find segments containing "oh <phrase>", then use the
word-level transcript timestamps to keep only STANDALONE tokens: the "oh X"
span must be flanked by a silence gap of >= PAUSE_MIN on both sides (or sit at
a Whisper segment boundary, which implies a pause). Clips are centered on the
"oh X" span. Output target_phrase is 'oh_<base>'.

Non-destructive: writes annotation_sheet_oh.csv and appends to the master sheet.

Usage:  python3 src/10_build_oh_topup.py [--pause 0.20] [--per 50]
"""
import argparse, csv, json, random, re, subprocess, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path.home() / "Desktop" / "pragmatic_contrast"
POOL = ROOT / "candidate_targets_filtered.csv"
MASTER = ROOT / "data" / "annotations" / "annotation_sheet.csv"
OH_SHEET = ROOT / "data" / "annotations" / "annotation_sheet_oh.csv"
CLIPS_DIR = ROOT / "data" / "clips"
import sys; sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import AUDIO_DIR, TRANSCRIPTS_DIR

BASES = ["yeah", "okay", "right", "sure", "great", "really", "come_on"]  # 'fine' excluded: only 12 'oh fine'
BASE_TOKENS = {b: (["come", "on"] if b == "come_on" else [b]) for b in BASES}
W_HALF = {"W1_local": 3.0, "W2_segment": 5.0, "W3_discourse": 8.0}
BIG = 9.9
SEED = 42
RESERVOIR = 3000


def find_audio(show, ep):
    p = AUDIO_DIR / show / (ep + ".mp3")
    return str(p) if p.exists() else None


def clean(w):
    return re.sub(r"[^a-z]", "", w.lower())


def load_segs(show, ep):
    try:
        return json.load(open(TRANSCRIPTS_DIR / show / (ep + ".json")))["segments"]
    except Exception:
        return None


def locate_oh_span(segs, seg_start, base, pause_min):
    """Return (center_time, is_standalone) for an 'oh <base>' span, or (None, None)."""
    idx = next((i for i, s in enumerate(segs) if abs(s["start"] - seg_start) < 0.1), None)
    if idx is None or "words" not in segs[idx]:
        return None, None
    words = segs[idx]["words"]
    toks = BASE_TOKENS[base]
    n = len(toks)
    for i in range(len(words) - n):
        if clean(words[i]["word"]) != "oh":
            continue
        if [clean(words[i + 1 + k]["word"]) for k in range(n)] != toks:
            continue
        oh_w = words[i]
        last_w = words[i + n]
        center = (oh_w["start"] + last_w["end"]) / 2.0
        # pause before "oh"
        if i == 0:
            gap_b = (segs[idx]["start"] - segs[idx - 1]["end"]) if idx > 0 else BIG
        else:
            gap_b = oh_w["start"] - words[i - 1]["end"]
        # pause after the phrase
        li = i + n
        if li == len(words) - 1:
            gap_a = (segs[idx + 1]["start"] - segs[idx]["end"]) if idx + 1 < len(segs) else BIG
        else:
            gap_a = words[li + 1]["start"] - last_w["end"]
        return center, (gap_b >= pause_min and gap_a >= pause_min)
    return None, None


def extract(audio, center, half, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", str(max(0.0, center - half)),
           "-i", audio, "-t", str(half * 2), "-ac", "1", "-ar", "16000", "-af", "loudnorm", str(out)]
    return subprocess.run(cmd, capture_output=True).returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pause", type=float, default=0.20, help="min silence (s) before and after the span")
    ap.add_argument("--per", type=int, default=50, help="standalone keepers wanted per phrase")
    args = ap.parse_args()
    random.seed(SEED)

    seen = {r["candidate_id"] for r in csv.DictReader(open(MASTER, newline=""))}
    pat = {b: re.compile(r"\boh,?\s+" + b.replace("_", " ") + r"\b") for b in BASES}

    # collect oh-prefaced, unseen candidates per base (reservoir-capped)
    res = defaultdict(list); cnt = defaultdict(int)
    with open(POOL, newline="") as f:
        for r in csv.DictReader(f):
            b = r["target_phrase"]
            if b not in pat or r["candidate_id"] in seen:
                continue
            if not pat[b].search((r["segment_text"] or "").lower()):
                continue
            cnt[b] += 1
            if len(res[b]) < RESERVOIR:
                res[b].append(r)
            else:
                j = random.randint(0, cnt[b] - 1)
                if j < RESERVOIR:
                    res[b][j] = r
    print("oh-prefaced unseen collected:", {b: cnt[b] for b in BASES})

    cols = ["candidate_id", "target_phrase", "episode_id", "show_name", "seg_start", "seg_end",
            "duration", "segment_text", "prev_text", "next_text", "audio_path", "status", "label", "confidence", "notes"]
    out_rows = []
    for b in BASES:
        rows = res[b]
        # show-balanced order
        by_show = defaultdict(list)
        for r in rows:
            by_show[r["show_name"]].append(r)
        for s in by_show:
            random.shuffle(by_show[s])
        order = list(by_show); random.shuffle(order)
        queue, i = [], 0
        while any(i < len(by_show[s]) for s in order):
            for s in order:
                if i < len(by_show[s]):
                    queue.append(by_show[s][i])
            i += 1
        # walk queue, keep pause-isolated standalone until --per
        kept = tried = nonstand = noaudio = 0
        for r in queue:
            if kept >= args.per:
                break
            tried += 1
            ap_ = find_audio(r["show_name"], r["episode_id"])
            if not ap_:
                noaudio += 1; continue
            segs = load_segs(r["show_name"], r["episode_id"])
            if not segs:
                noaudio += 1; continue
            center, standalone = locate_oh_span(segs, float(r["seg_start"]), b, args.pause)
            if center is None or not standalone:
                nonstand += 1; continue
            cid = "oh_" + r["candidate_id"]
            paths = {wd: CLIPS_DIR / wd / (cid + ".wav") for wd in W_HALF}
            if not all(extract(ap_, center, W_HALF[wd], paths[wd]) for wd in W_HALF):
                continue
            kept += 1
            out_rows.append({
                "candidate_id": cid, "target_phrase": "oh_" + b, "episode_id": r["episode_id"],
                "show_name": r["show_name"], "seg_start": r["seg_start"], "seg_end": r["seg_end"],
                "duration": r.get("duration", ""), "segment_text": r["segment_text"],
                "prev_text": r["prev_text"], "next_text": r["next_text"],
                "audio_path": str(paths["W1_local"]), "status": "unreviewed",
                "label": "", "confidence": "", "notes": "",
            })
        print(f"  oh_{b:8s} kept {kept:>3} standalone  (tried {tried}, non-standalone {nonstand}, no-audio {noaudio})")

    with open(OH_SHEET, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out_rows)
    with open(MASTER, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writerows(out_rows)
    print(f"\nwrote {OH_SHEET} ({len(out_rows)} rows) and appended to master")


if __name__ == "__main__":
    main()
