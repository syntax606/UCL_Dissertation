#!/usr/bin/env python3
"""
Build a clean, sense-filtered top-up of candidates for under-quota phrases.

1. Streams the big filtered pool, applies per-phrase blocklist rules to the
   FIRST occurrence of the target word (the occurrence the extractor centres on),
   and drops candidates already seen in the master sheet.
2. Samples a show-balanced top-up per phrase, sized to close the gap to TARGET
   keepers given an assumed keep-rate.
3. Extracts W1/W2/W3 audio for the top-up (same centring + loudnorm as 05).
4. Appends the new rows to the master annotation_sheet.csv (so 08 can merge them)
   and writes annotation_sheet_topup.csv (so 07 can build batches for them).

Usage:  python3 src/09_build_topup.py
"""
import csv, json, math, random, re, subprocess, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path.home() / "Desktop" / "pragmatic_contrast"
POOL = ROOT / "candidate_targets_filtered.csv"
MASTER = ROOT / "data" / "annotations" / "annotation_sheet.csv"
LABELED = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
TOPUP = ROOT / "data" / "annotations" / "annotation_sheet_topup.csv"
CLIPS_DIR = ROOT / "data" / "clips"
AUDIO_DIR = Path("/Volumes/Caro Drive/podcast-dissertation-audio/audio copy")
TRANSCRIPTS_DIR = Path("/Volumes/Caro Drive/podcast-dissertation-audio/podcast_transcripts")

TARGET = 40            # keepers wanted per phrase
KEEP_RATE = 0.55       # assumed survival of filtered candidates through labelling
BUFFER = 1.15          # extra margin
SEED = 42
RESERVOIR = 4000       # cap collected per phrase while streaming
W_HALF = {"W1_local": 3.0, "W2_segment": 5.0, "W3_discourse": 8.0}
PHRASE_WORD = {"come_on": "come"}

# Blocklist: an occurrence is the WRONG sense if its local window matches any pattern.
BLOCK = {
  "right": [r"\bright (now|here|there|away|back|wing|winger|wingers|in|into|on|onto|after|before|up|down|out|outside|next|side|hand|behind|across|past|over|where|when|about|around)\b",
            r"\b(the|a|far|alt|center|centre|hard|religious|political|christian|radical|extreme) right\b"],
  "sure": [r"\bmak(e|es|ing) sure\b", r"\bmade sure\b", r"\bbe sure\b",
           r"\b(i'm|im|i am|we're|we are|you're|you are|are you|not|n't) sure\b",
           r"\bsure (that|if|whether|about|of|i|you|we|he|she|it|they|the|did|do|does|is|was|were|will|would|can|could|enough|thing|footed)\b",
           r"\bfor sure\b"],
  "really": [r"\breally (a|an|the|good|bad|great|nice|important|hard|easy|big|small|want|wanted|like|liked|need|needed|think|thought|believe|feel|felt|love|hate|don't|do|does|did|is|was|are|were|have|has|had|been|going|gonna|just|very|quite|so|much|more|well|interesting|cool|amazing|incredible|serious|sad|happy|angry|funny|weird|strange|smart|stupid)\b"],
  "great": [r"\bgreat (deal|job|news|idea|ideas|country|nation|again|thing|things|way|point|work|question|guy|guys|man|woman|people|leader|president|power|powers|depression|war|number|amount|majority|success|story|stuff|moment|day|time|honor|honour|opportunity|example|friend|friends|company|economy|achievement|loss|grandfather|grandmother|deal)\b",
            r"\b(the|a|how|so|such a|really|very|truly|pretty|that) great\b",
            r"\bgreatest\b", r"\bgreater\b", r"\bgreatly\b", r"\bgreatness\b"],
  "fine": [r"\bfine (with|by|print|line|lines|tune|tuning|tuned|art|arts|wine|dining|grained|detail|details|job|jobs|young|man|people|day)\b",
           r"\b(completely|perfectly|just|totally|absolutely|doing|feel|feeling|felt|am|is|are|was|were|be|been|being|seems|seem|looks|look|a|the|pay|paid|hefty|heavy|small|large) fine\b"],
  "yeah": [], "okay": [], "come_on": [
           r"\bcome on (the|a|an|our|my|your|his|her|their|its|to|at|in|on|onto|over|up|down|out|board|stage|air|set|tv|television|radio|line|lines|phone|phones|screen|screens|camera|cameras|show|shows|here|today|tonight|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b"],
}


def first_occ_ok(text, phrase):
    t = (text or "").lower()
    w = PHRASE_WORD.get(phrase, phrase).replace("_", " ") if phrase == "come_on" else phrase.replace("_", " ")
    m = re.search(r"\b" + re.escape(w) + r"\b", t)
    if not m:
        return False
    win = t[max(0, m.start() - 25): m.end() + 25]
    return not any(re.search(b, win) for b in BLOCK.get(phrase, []))


def find_audio(show, ep):
    p = AUDIO_DIR / show / (ep + ".mp3")
    return str(p) if p.exists() else None


def clean(w):
    return re.sub(r"[^a-z]", "", w.lower())


def find_midpoint(show, ep, seg_start, phrase):
    jp = TRANSCRIPTS_DIR / show / (ep + ".json")
    target = PHRASE_WORD.get(phrase, phrase)
    try:
        segs = json.load(open(jp))["segments"]
    except Exception:
        return None
    seg = next((s for s in segs if abs(s["start"] - seg_start) < 0.1), None)
    if not seg or "words" not in seg:
        return None
    for w in seg["words"]:
        if clean(w["word"]) == target:
            return (w["start"] + w["end"]) / 2.0
    return None


def extract(audio, center, half, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", str(max(0.0, center - half)),
           "-i", audio, "-t", str(half * 2), "-ac", "1", "-ar", "16000", "-af", "loudnorm", str(out)]
    return subprocess.run(cmd, capture_output=True).returncode == 0


def main():
    random.seed(SEED)
    seen = {r["candidate_id"] for r in csv.DictReader(open(MASTER, newline=""))}

    # current keepers per phrase -> per-phrase pull target
    kept = defaultdict(int)
    for r in csv.DictReader(open(LABELED, newline="")):
        if r.get("status") == "reviewed":
            kept[r["target_phrase"]] += 1
    pull = {}
    for ph in BLOCK:
        gap = max(0, TARGET - kept.get(ph, 0))
        pull[ph] = math.ceil(gap / KEEP_RATE * BUFFER) if gap else 0
    print("pull targets:", {k: v for k, v in pull.items() if v})

    # stream pool, reservoir-collect filtered+unseen per phrase
    res = defaultdict(list)
    cnt = defaultdict(int)
    with open(POOL, newline="") as f:
        for r in csv.DictReader(f):
            ph = r["target_phrase"]
            if pull.get(ph, 0) == 0:
                continue
            if r["candidate_id"] in seen:
                continue
            if not first_occ_ok(r["segment_text"], ph):
                continue
            cnt[ph] += 1
            if len(res[ph]) < RESERVOIR:
                res[ph].append(r)
            else:
                j = random.randint(0, cnt[ph] - 1)
                if j < RESERVOIR:
                    res[ph][j] = r
    print("clean unseen collected:", {k: cnt[k] for k in cnt})

    # show-balanced selection per phrase
    chosen = []
    for ph, n in pull.items():
        if n == 0:
            continue
        rows = res[ph]
        by_show = defaultdict(list)
        for r in rows:
            by_show[r["show_name"]].append(r)
        for s in by_show:
            random.shuffle(by_show[s])
        order = list(by_show)
        random.shuffle(order)
        picked, i = [], 0
        while len(picked) < min(n, len(rows)):
            progressed = False
            for s in order:
                if i < len(by_show[s]):
                    picked.append(by_show[s][i]); progressed = True
                    if len(picked) >= n:
                        break
            if not progressed:
                break
            i += 1
        chosen.extend(picked)
        print(f"  {ph:9s} selected {len(picked)} (from {len(rows)} clean, {len(by_show)} shows)")

    # extract audio for chosen
    cols = ["candidate_id", "target_phrase", "episode_id", "show_name", "seg_start", "seg_end",
            "duration", "segment_text", "prev_text", "next_text", "audio_path", "status", "label", "confidence", "notes"]
    out_rows = []
    ok = miss = 0
    for r in chosen:
        ap = find_audio(r["show_name"], r["episode_id"])
        center = find_midpoint(r["show_name"], r["episode_id"], float(r["seg_start"]), r["target_phrase"]) if ap else None
        if not ap or center is None:
            miss += 1; continue
        cid = r["candidate_id"]
        paths = {wd: CLIPS_DIR / wd / (cid + ".wav") for wd in W_HALF}
        if all(extract(ap, center, W_HALF[wd], paths[wd]) for wd in W_HALF):
            ok += 1
            out_rows.append({
                "candidate_id": cid, "target_phrase": r["target_phrase"], "episode_id": r["episode_id"],
                "show_name": r["show_name"], "seg_start": r["seg_start"], "seg_end": r["seg_end"],
                "duration": r.get("duration", ""), "segment_text": r["segment_text"],
                "prev_text": r["prev_text"], "next_text": r["next_text"],
                "audio_path": str(paths["W1_local"]), "status": "unreviewed",
                "label": "", "confidence": "", "notes": "",
            })
        else:
            miss += 1
        if (ok + miss) % 25 == 0:
            print(f"   extracted {ok}/{ok+miss}", file=sys.stderr)
    print(f"extracted ok {ok} | skipped (no audio/word/fail) {miss}")

    # write topup sheet
    with open(TOPUP, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out_rows)
    # append to master
    with open(MASTER, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writerows(out_rows)
    print(f"wrote {TOPUP} ({len(out_rows)} rows) and appended to master sheet")


if __name__ == "__main__":
    main()
