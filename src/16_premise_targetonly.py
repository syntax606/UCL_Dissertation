#!/usr/bin/env python3
"""
Target-only manipulation check: the same 60 premise clips, shown as the bare
target word with NO context and NO audio. If humans sit near chance / mostly
unsure, the word alone carries no stance, which validates the lexical control
and anchors the clean end of the baseline story (target-only << discourse-text
<< audio).

Build (no args):   python3 src/16_premise_targetonly.py
Score (give jsons): python3 src/16_premise_targetonly.py to_aux1.json to_aux2.json
"""
import base64, csv, json, random, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY = ROOT / "data" / "annotations" / "premise_key.csv"
OUT = ROOT / "offline_annotator"
CLASSES = ["affiliative", "neutral", "adversarial"]
SEED = 42


def kappa(pairs):
    pairs = [(a, b) for a, b in pairs if a in CLASSES and b in CLASSES]
    n = len(pairs)
    if not n:
        return float("nan")
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum((ca[c] / n) * (cb[c] / n) for c in CLASSES)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def build():
    rows = list(csv.DictReader(open(KEY, newline="")))
    random.seed(SEED)
    for aux in ("aux1", "aux2"):
        clips = [{"id": r["candidate_id"], "word": r["target_phrase"].replace("_", " ")} for r in rows]
        random.shuffle(clips)
        html = TEMPLATE.replace("__AUX__", aux).replace("__PAYLOAD__", json.dumps({"aux": aux, "clips": clips}))
        (OUT / f"premise_targetonly_{aux}.html").write_text(html)
    print(f"built premise_targetonly_aux1.html and _aux2.html ({len(rows)} clips each, word-only, no audio)")


def score(paths):
    ref = {r["candidate_id"]: r["reference_stance"] for r in csv.DictReader(open(KEY, newline=""))}
    phrase = {r["candidate_id"]: r["target_phrase"] for r in csv.DictReader(open(KEY, newline=""))}
    per_file = {}
    for p in paths:
        ans = json.load(open(p)).get("answers", {})
        per_file[Path(p).name] = {c: v.get("stance") for c, v in ans.items()}
    print("target-only (word alone, no context, no audio):")
    print("file                 n  unsure  acc   kappa")
    pooled = []
    for name, judged in per_file.items():
        pairs = [(ref[c], judged[c]) for c in judged if c in ref]
        pooled += pairs
        unsure = sum(1 for _, j in pairs if j == "unsure")
        scored = [(a, b) for a, b in pairs if b != "unsure"]
        acc = sum(a == b for a, b in scored) / len(scored) if scored else float("nan")
        print(f"  {name:18s} {len(pairs):>3}  {unsure:>5}  {acc:.2f}  {kappa(pairs):.2f}")
    unsure = sum(1 for _, j in pooled if j == "unsure")
    scored = [(a, b) for a, b in pooled if b != "unsure"]
    acc = sum(a == b for a, b in scored) / len(scored) if scored else float("nan")
    print(f"  {'POOLED':18s} {len(pooled):>3}  {unsure:>5}  {acc:.2f}")
    print(f"\n  chance ~= 0.33   |   for comparison: discourse-text 0.65, audio 0.73")
    print("  Expectation: near chance / high unsure -> word alone carries no stance (control holds).")


# runner defined at end of file (after TEMPLATE)


TEMPLATE = r"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Manipulation check - __AUX__</title><style>
:root{--bg:#11151c;--panel:#1b212b;--ink:#e8edf4;--mut:#8b97a8;--line:#2c3543;--acc:#3b6ea5;}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}html,body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.45 -apple-system,system-ui,sans-serif}
.wrap{max-width:640px;margin:0 auto;padding:12px 12px 120px}
header{position:sticky;top:0;background:var(--bg);padding:8px 0;border-bottom:1px solid var(--line);z-index:5}
.prog{height:8px;background:var(--panel);border-radius:6px;overflow:hidden}.prog>i{display:block;height:100%;background:var(--acc);width:0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:26px 14px;margin:10px 0;text-align:center}
.word{font-size:44px;font-weight:800;letter-spacing:.5px}
.opts{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:16px}
.btn{background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:10px;padding:14px;font-size:15px;cursor:pointer}
.opt small{display:block;color:var(--mut);font-size:11px;margin-top:2px}.opt.sel{outline:2px solid var(--acc);border-color:var(--acc)}
.nav{position:fixed;left:0;right:0;bottom:0;background:var(--panel);border-top:1px solid var(--line);display:flex;gap:8px;padding:10px 12px;padding-bottom:calc(10px + env(safe-area-inset-bottom))}
.nav .btn{flex:1;font-weight:600}.nav .prim{background:var(--acc);border-color:var(--acc)}
.save{font-size:12px;color:var(--mut);text-align:center;margin-top:6px}details{margin:8px 0}summary{color:var(--mut);font-size:13px}
</style></head><body><div class="wrap">
<header><div class="prog"><i id="pb"></i></div>
<div style="display:flex;gap:8px;margin-top:6px;align-items:center"><span class="save" id="pos"></span>
<button class="btn" style="margin-left:auto;padding:6px 10px;font-size:13px" onclick="nextUn()">Next unanswered</button>
<button class="btn prim" style="padding:6px 10px;font-size:13px" onclick="exp()">Export</button></div></header>
<details><summary>Instructions (tap)</summary><div class="save" style="text-align:left">
You will see ONLY a single word, with no surrounding context and no audio. Based on the word by
itself, what stance does it carry? <b>Affiliative</b> (warm/approving), <b>Neutral</b> (just
acknowledging), <b>Adversarial</b> (dismissive/sarcastic/hostile), or <b>Unsure</b>. It is expected
that you will often be unsure, that is fine and is what we want to measure. Answer every card, do not
skip. Export at the end and send the file back.</div></details>
<div id="clip"></div></div>
<div class="nav"><button class="btn" onclick="go(-1)">Prev</button><button class="btn prim" onclick="go(1)">Next</button></div>
<script>
const DATA=__PAYLOAD__; const KEY="premise_to_"+DATA.aux; let i=0, ans={};
try{ans=JSON.parse(localStorage.getItem(KEY)||"{}")}catch(e){ans={}}
function cur(){return DATA.clips[i]}
function save(){try{localStorage.setItem(KEY,JSON.stringify(ans))}catch(e){}}
function answered(){return DATA.clips.filter(c=>ans[c.id]).length}
function pick(s){ans[cur().id]={stance:s,condition:"targetonly"};save();render()}
function render(){const c=cur(),r=ans[c.id]||{};
document.getElementById("pos").textContent=(i+1)+" / "+DATA.clips.length+"   ("+answered()+" answered)";
document.getElementById("pb").style.width=(100*answered()/DATA.clips.length)+"%";
let h="<div class='card'><div class='word'>"+c.word+"</div><div class='opts'>";
const opts=[["affiliative","warm / approving"],["neutral","just acknowledging"],["adversarial","dismissive / hostile"],["unsure","can't tell"]];
for(const[v,g]of opts){h+="<button class='btn opt"+(r.stance===v?" sel":"")+"' onclick=\"pick('"+v+"')\">"+v[0].toUpperCase()+v.slice(1)+"<small>"+g+"</small></button>"}
h+="</div></div>";document.getElementById("clip").innerHTML=h;save()}
function go(d){i=Math.max(0,Math.min(DATA.clips.length-1,i+d));scrollTo(0,0);render()}
function nextUn(){for(let k=1;k<=DATA.clips.length;k++){const j=(i+k)%DATA.clips.length;if(!ans[DATA.clips[j].id]){i=j;scrollTo(0,0);render();return}}alert("All answered.")}
function exp(){const out=JSON.stringify({aux:DATA.aux,exported:new Date().toISOString(),answers:ans},null,2);
const b=new Blob([out],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="premise_targetonly_"+DATA.aux+".json";document.body.appendChild(a);a.click();a.remove();
if(navigator.clipboard)navigator.clipboard.writeText(out).then(()=>alert("Exported + copied."),()=>alert("Exported."));else alert("Exported.")}
render();
</script></body></html>
"""


if __name__ == "__main__":
    args = list(sys.argv[1:])
    score(args) if args else build()
