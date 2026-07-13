#!/usr/bin/env python3
"""
Build the premise-check subset + two counterbalanced auxiliary-annotator packages.

Samples ~60 kept clips, stance-balanced and phrase-spread across distinct episodes,
splits them into Set X / Set Y, and emits two self-contained HTML files:

  Aux 1:  Set X = TRANSCRIPT ONLY,   Set Y = AUDIO + TRANSCRIPT
  Aux 2:  Set X = AUDIO + TRANSCRIPT, Set Y = TRANSCRIPT ONLY

So every clip receives one transcript-only judgment and one audio judgment, from
different people, and neither condition is tied to a single annotator. Annotators
make a 3-way stance call (+ unsure). Your stance labels are the hidden reference,
written to data/annotations/premise_key.csv (NOT given to annotators).

Usage:  python3 src/14_build_premise_check.py [--n 60] [--bitrate 32k]
"""
import argparse, base64, csv, json, os, random, subprocess, sys, tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABELED = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
CLIPS_DIR = ROOT / "data" / "clips"
OUT = ROOT / "offline_annotator"
KEY = ROOT / "data" / "annotations" / "premise_key.csv"
STANCES = ["affiliative", "neutral", "adversarial"]
SEED = 42


def wav_b64(cid):
    """Embed the already-extracted W2 wav directly (no ffmpeg needed)."""
    wav = CLIPS_DIR / "W2_segment" / (cid + ".wav")
    if not wav.exists():
        return None
    return base64.b64encode(wav.read_bytes()).decode("ascii")


def sample(rows, n):
    random.seed(SEED)
    kept = [r for r in rows if r.get("status") == "reviewed" and r.get("stance") in STANCES]
    per_stance = n // len(STANCES)
    chosen, used_eps = [], set()
    for st in STANCES:
        pool = [r for r in kept if r["stance"] == st]
        # prefer clear confidence, then spread across phrases, distinct episodes
        pool.sort(key=lambda r: (r.get("confidence") != "clear", random.random()))
        by_phrase = defaultdict(list)
        for r in pool:
            by_phrase[r["target_phrase"]].append(r)
        phrases = list(by_phrase); random.shuffle(phrases)
        picked, i = [], 0
        while len(picked) < per_stance and any(i < len(by_phrase[p]) for p in phrases):
            for p in phrases:
                if len(picked) >= per_stance:
                    break
                if i < len(by_phrase[p]):
                    r = by_phrase[p][i]
                    if r["episode_id"] not in used_eps:
                        picked.append(r); used_eps.add(r["episode_id"])
            i += 1
        chosen.extend(picked)
    random.shuffle(chosen)
    return chosen[:n]


def split_xy(clips):
    # balance stance across X and Y by alternating within each stance group
    by_st = defaultdict(list)
    for c in clips:
        by_st[c["stance"]].append(c)
    X, Y = [], []
    for st, group in by_st.items():
        for j, c in enumerate(group):
            (X if j % 2 == 0 else Y).append(c)
    return X, Y


def build_html(aux_name, clips_with_cond, audio_cids, bitrate):
    """clips_with_cond: list of (row, condition) where condition in {'text','audio'}."""
    audio = {cid: wav_b64(cid) for cid in audio_cids}
    payload = {"aux": aux_name, "clips": [{
        "id": r["candidate_id"], "phrase": r["target_phrase"].replace("_", " "),
        "prev": r["prev_text"], "text": r["segment_text"], "next": r["next_text"],
        "condition": cond, "audio": audio.get(r["candidate_id"]) if cond == "audio" else None,
    } for r, cond in clips_with_cond]}
    html = TEMPLATE.replace("__AUX__", aux_name).replace("__N__", str(len(clips_with_cond))).replace("__PAYLOAD__", json.dumps(payload))
    p = OUT / f"premise_{aux_name}.html"
    p.write_text(html)
    return p, sum(1 for _, c in clips_with_cond if c == "audio")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--bitrate", default="32k")
    args = ap.parse_args()
    rows = list(csv.DictReader(open(LABELED, newline="")))
    clips = sample(rows, args.n)
    X, Y = split_xy(clips)
    setmap = {c["candidate_id"]: "X" for c in X}
    setmap.update({c["candidate_id"]: "Y" for c in Y})

    # Aux1: X text, Y audio ; Aux2: X audio, Y text
    aux1 = [(c, "text") for c in X] + [(c, "audio") for c in Y]
    aux2 = [(c, "audio") for c in X] + [(c, "text") for c in Y]
    random.seed(SEED); random.shuffle(aux1); random.shuffle(aux2)

    p1, na1 = build_html("aux1", aux1, [c["candidate_id"] for c in Y], args.bitrate)
    p2, na2 = build_html("aux2", aux2, [c["candidate_id"] for c in X], args.bitrate)

    # hidden reference key (never shown to annotators)
    with open(KEY, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["candidate_id", "set", "target_phrase", "reference_stance", "reference_arousal", "confidence", "episode_id", "show_name"])
        w.writeheader()
        for c in clips:
            w.writerow({"candidate_id": c["candidate_id"], "set": setmap[c["candidate_id"]],
                        "target_phrase": c["target_phrase"], "reference_stance": c["stance"],
                        "reference_arousal": c["arousal"], "confidence": c.get("confidence", ""),
                        "episode_id": c["episode_id"], "show_name": c["show_name"]})

    from collections import Counter
    print(f"sampled {len(clips)} clips | stance {dict(Counter(c['stance'] for c in clips))} | "
          f"phrases {dict(Counter(c['target_phrase'] for c in clips))} | episodes {len(set(c['episode_id'] for c in clips))}")
    print(f"Set X {len(X)} / Set Y {len(Y)}")
    print(f"wrote {p1.name} ({na1} audio clips), {p2.name} ({na2} audio clips), and {KEY.name} (hidden reference)")


TEMPLATE = r"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Premise check - __AUX__</title><style>
:root{--bg:#11151c;--panel:#1b212b;--ink:#e8edf4;--mut:#8b97a8;--line:#2c3543;--aff:#2e7d51;--neu:#5a6472;--adv:#9c3b3b;--acc:#3b6ea5;}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}html,body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.45 -apple-system,system-ui,sans-serif}
.wrap{max-width:760px;margin:0 auto;padding:12px 12px 120px}
header{position:sticky;top:0;background:var(--bg);padding:8px 0;border-bottom:1px solid var(--line);z-index:5}
.prog{height:8px;background:var(--panel);border-radius:6px;overflow:hidden}.prog>i{display:block;height:100%;background:var(--acc);width:0}
.cond{display:inline-block;font-size:12px;font-weight:700;letter-spacing:.6px;padding:3px 10px;border-radius:20px;margin-bottom:8px}
.cond.audio{background:#223247;color:#cfe3ff}.cond.text{background:#2a2333;color:#e8d7ff}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px;margin:10px 0}
.phrase{font-size:26px;font-weight:700}.hl{background:var(--acc);color:#fff;padding:0 4px;border-radius:4px}
.ctx{color:var(--mut);font-size:14px;margin:2px 0}.seg{font-size:17px;margin:8px 0}
.btn{background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:10px;padding:12px 14px;font-size:15px;cursor:pointer}
.audio .btn{width:100%;font-weight:600;margin-bottom:6px}
.opts{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:6px}
.opt{text-align:left}.opt small{display:block;color:var(--mut);font-size:11px;margin-top:2px}
.opt.sel{outline:2px solid var(--acc);border-color:var(--acc)}
.opt.aff.sel{background:#1e3b2b}.opt.neu.sel{background:#2b3038}.opt.adv.sel{background:#3b2323}
.nav{position:fixed;left:0;right:0;bottom:0;background:var(--panel);border-top:1px solid var(--line);display:flex;gap:8px;padding:10px 12px;padding-bottom:calc(10px + env(safe-area-inset-bottom))}
.nav .btn{flex:1;font-weight:600}.nav .prim{background:var(--acc);border-color:var(--acc)}
.save{font-size:12px;color:var(--mut);text-align:center;margin-top:6px}details{margin:8px 0}summary{color:var(--mut);font-size:13px}
</style></head><body><div class="wrap">
<header><div class="prog"><i id="pb"></i></div>
<div style="display:flex;gap:8px;margin-top:6px;align-items:center"><span class="save" id="pos"></span>
<button class="btn" style="margin-left:auto;padding:6px 10px;font-size:13px" onclick="nextUn()">Next unanswered</button>
<button class="btn prim" style="padding:6px 10px;font-size:13px" onclick="exp()">Export</button></div></header>
<details><summary>Instructions (tap)</summary><div class="ctx">
You are judging the <b>stance</b> of the highlighted word in each clip. Some clips have an audio
player; some are text only. Answer every clip. Pick the option that best fits how the word is used:
<br>• <b>Affiliative</b>: warm, sincere agreement, approval, encouragement.
<br>• <b>Neutral</b>: just acknowledging or going along, no strong stance.
<br>• <b>Adversarial</b>: dismissive, sarcastic, skeptical, resistant, hostile.
<br>• <b>Unsure</b>: you genuinely cannot tell. Use it honestly; do not guess.
<br>Export often and send the file back.</div></details>
<div id="clip"></div></div>
<div class="nav"><button class="btn" onclick="go(-1)">Prev</button><button class="btn prim" onclick="go(1)">Next</button></div>
<script>
const DATA=__PAYLOAD__; const KEY="premise_"+DATA.aux; let i=0, ans={};
try{ans=JSON.parse(localStorage.getItem(KEY)||"{}")}catch(e){ans={}}
function cur(){return DATA.clips[i]}
function save(){try{localStorage.setItem(KEY,JSON.stringify(ans))}catch(e){}}
function answered(){return DATA.clips.filter(c=>ans[c.id]&&ans[c.id].stance).length}
function hl(t,p){if(!t)return "";const w=p.replace(/[.*+?^${}()|[\]\\]/g,"\\$&");const e=t.replace(/[&<>]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]));return e.replace(new RegExp("\\b("+w+")\\b","ig"),"<span class='hl'>$1</span>")}
function pick(s){ans[cur().id]={stance:s,condition:cur().condition};save();render()}
function render(){const c=cur(),r=ans[c.id]||{};
document.getElementById("pos").textContent=(i+1)+" / "+DATA.clips.length+"   ("+answered()+" answered)";
document.getElementById("pb").style.width=(100*answered()/DATA.clips.length)+"%";
let h="<div class='card "+(c.condition==='audio'?'audio':'')+"'>";
h+="<span class='cond "+c.condition+"'>"+(c.condition==='audio'?'AUDIO + TRANSCRIPT':'TRANSCRIPT ONLY')+"</span>";
h+="<div class='phrase'>"+c.phrase+"</div>";
if(c.condition==='audio'&&c.audio){h+="<button class='btn' onclick=\"play()\">▶ Play</button><audio id='au' src='data:audio/wav;base64,"+c.audio+"' preload='none'></audio>"}
if(c.prev)h+="<p class='ctx'>… "+hl(c.prev,c.phrase)+"</p>";
h+="<p class='seg'>"+hl(c.text,c.phrase)+"</p>";
if(c.next)h+="<p class='ctx'>"+hl(c.next,c.phrase)+" …</p>";
h+="<div class='opts'>";
const opts=[["affiliative","aff","warm / sincere / approving"],["neutral","neu","just acknowledging"],["adversarial","adv","dismissive / sarcastic / hostile"],["unsure","neu","can't tell"]];
for(const[v,cl,g]of opts){h+="<button class='btn opt "+cl+(r.stance===v?" sel":"")+"' onclick=\"pick('"+v+"')\">"+v[0].toUpperCase()+v.slice(1)+"<small>"+g+"</small></button>"}
h+="</div></div>";document.getElementById("clip").innerHTML=h;save()}
function play(){const a=document.getElementById("au");if(a){a.currentTime=0;a.play()}}
function go(d){i=Math.max(0,Math.min(DATA.clips.length-1,i+d));scrollTo(0,0);render()}
function nextUn(){for(let k=1;k<=DATA.clips.length;k++){const j=(i+k)%DATA.clips.length;if(!ans[DATA.clips[j].id]){i=j;scrollTo(0,0);render();return}}alert("All clips answered.")}
function exp(){const out=JSON.stringify({aux:DATA.aux,exported:new Date().toISOString(),answers:ans},null,2);
const b=new Blob([out],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="premise_"+DATA.aux+".json";document.body.appendChild(a);a.click();a.remove();
if(navigator.clipboard)navigator.clipboard.writeText(out).then(()=>alert("Exported + copied to clipboard."),()=>alert("Exported (download)."));else alert("Exported.")}
render();
</script></body></html>
"""

if __name__ == "__main__":
    main()
