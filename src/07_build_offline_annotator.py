#!/usr/bin/env python3
"""
Build fully self-contained, offline HTML annotation batches for the iPad.

Each output .html embeds:
  - the codebook (codebook.json)
  - the clip metadata (transcript, context, phrase)
  - the audio itself, transcoded to AAC and base64-inlined (no server, no network)

Annotations are saved to the browser's localStorage as you work, and exported
as JSON (download + copy-to-clipboard). Merge them back with 08_merge_offline_annotations.py.

Usage:
  # small test batch: 2 clips per phrase, one file
  python3 src/07_build_offline_annotator.py --sample 2

  # full run: all candidates, phrase-balanced batches of 150
  python3 src/07_build_offline_annotator.py --batch-size 150
"""
import argparse, base64, csv, json, os, subprocess, sys, tempfile
from collections import defaultdict, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEET = os.path.join(ROOT, "data", "annotations", "annotation_sheet.csv")
CODEBOOK = os.path.join(ROOT, "src", "codebook.json")
CLIPS_DIR = os.path.join(ROOT, "data", "clips")
OUT_DIR = os.path.join(ROOT, "offline_annotator")

WINDOW_DIRS = {"w1": "W1_local", "w2": "W2_segment", "w3": "W3_discourse"}
WINDOW_LABEL = {"w1": "Word (±2s)", "w2": "Utterance", "w3": "Discourse"}


def transcode_b64(wav_path, bitrate):
    """Transcode a wav to mono 16k AAC (.m4a) and return base64 string, or None."""
    if not os.path.exists(wav_path):
        return None
    with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as tf:
        tmp = tf.name
    try:
        r = subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path,
             "-c:a", "aac", "-b:a", bitrate, "-ar", "16000", "-ac", "1", tmp],
            capture_output=True)
        if r.returncode != 0 or os.path.getsize(tmp) == 0:
            return None
        with open(tmp, "rb") as fh:
            return base64.b64encode(fh.read()).decode("ascii")
    finally:
        try: os.remove(tmp)
        except OSError: pass


def window_path(audio_path_w1, window):
    """Derive a window's wav path from the sheet's W1_local audio_path."""
    fname = os.path.basename(audio_path_w1)
    return os.path.join(CLIPS_DIR, WINDOW_DIRS[window], fname)


def load_rows(path=SHEET):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def interleave_by_phrase(rows):
    """Round-robin across phrases so each batch is phrase-balanced."""
    buckets = OrderedDict()
    for row in rows:
        buckets.setdefault(row["target_phrase"], []).append(row)
    out, i = [], 0
    while any(i < len(b) for b in buckets.values()):
        for b in buckets.values():
            if i < len(b):
                out.append(b[i])
        i += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--windows", default="w2,w1", help="comma list of windows to embed, in play order")
    ap.add_argument("--bitrate", default="32k")
    ap.add_argument("--batch-size", type=int, default=150)
    ap.add_argument("--sample", type=int, default=0, help="if >0, only N clips per phrase, single batch named 'sample'")
    ap.add_argument("--limit", type=int, default=0, help="cap total clips (0 = all)")
    ap.add_argument("--sheet", default=SHEET, help="annotation sheet CSV to build from")
    ap.add_argument("--prefix", default="annotator", help="output filename prefix")
    args = ap.parse_args()

    windows = [w.strip() for w in args.windows.split(",") if w.strip()]
    for w in windows:
        if w not in WINDOW_DIRS:
            sys.exit(f"unknown window {w}; choose from {list(WINDOW_DIRS)}")

    codebook = json.load(open(CODEBOOK))
    rows = load_rows(args.sheet)

    if args.sample > 0:
        per = defaultdict(int)
        sel = []
        for row in interleave_by_phrase(rows):
            if per[row["target_phrase"]] < args.sample:
                sel.append(row); per[row["target_phrase"]] += 1
        rows = sel
    else:
        rows = interleave_by_phrase(rows)
        if args.limit:
            rows = rows[:args.limit]

    os.makedirs(OUT_DIR, exist_ok=True)
    template = HTML_TEMPLATE

    # transcode + assemble clip records
    clips = []
    total = len(rows)
    for idx, row in enumerate(rows, 1):
        audio = {}
        for w in windows:
            b64 = transcode_b64(window_path(row["audio_path"], w), args.bitrate)
            if b64:
                audio[w] = b64
        clips.append({
            "id": row["candidate_id"],
            "phrase": row["target_phrase"],
            "show": row["show_name"],
            "episode": row["episode_id"],
            "prev": row["prev_text"],
            "text": row["segment_text"],
            "next": row["next_text"],
            "audio": audio,
        })
        if idx % 25 == 0 or idx == total:
            print(f"  transcoded {idx}/{total}", file=sys.stderr)

    # chunk into batches
    if args.sample > 0:
        batches = [("sample", clips)]
    else:
        bs = args.batch_size
        batches = [(f"{i//bs+1:02d}", clips[i:i+bs]) for i in range(0, len(clips), bs)]

    win_meta = [{"key": w, "label": WINDOW_LABEL[w]} for w in windows]
    manifest = []
    for bid, bclips in batches:
        payload = {
            "batch_id": bid,
            "scheme_version": codebook["scheme_version"],
            "windows": win_meta,
            "codebook": codebook,
            "clips": bclips,
        }
        html = (template
                .replace("__BATCH_ID__", bid)
                .replace("__N__", str(len(bclips)))
                .replace("__PAYLOAD__", json.dumps(payload)))
        out = os.path.join(OUT_DIR, f"{args.prefix}_{bid}.html")
        with open(out, "w") as fh:
            fh.write(html)
        mb = os.path.getsize(out) / 1e6
        manifest.append((out, len(bclips), mb))
        print(f"wrote {out}  ({len(bclips)} clips, {mb:.1f} MB)")

    with open(os.path.join(OUT_DIR, "README.txt"), "w") as fh:
        fh.write(
            "OFFLINE ANNOTATOR\n"
            "=================\n\n"
            "1. AirDrop / copy the annotator_*.html files to the iPad (save to Files).\n"
            "2. Open one in Safari. Everything (audio + scheme) is inside the file; no network needed.\n"
            "3. Label clips. Progress autosaves to Safari's local storage as you go.\n"
            "4. Tap EXPORT often. It downloads a JSON and copies it to the clipboard;\n"
            "   AirDrop/email that JSON back to the Mac.\n"
            "5. On the Mac: python3 src/08_merge_offline_annotations.py <exported>.json [...]\n\n"
            "Tip: do not 'Clear History and Website Data' in Safari mid-trip, or unexported\n"
            "progress is lost. Exporting after each sitting is the safe habit.\n")
    print(f"\n{len(batches)} batch file(s) in {OUT_DIR}")


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Pragmatic Contrast Annotator - batch __BATCH_ID__</title>
<style>
  :root { --bg:#11151c; --panel:#1b212b; --ink:#e8edf4; --mut:#8b97a8; --line:#2c3543;
          --aff:#2e7d51; --neu:#5a6472; --adv:#9c3b3b; --acc:#3b6ea5; --warn:#a5763b; }
  * { box-sizing:border-box; -webkit-tap-highlight-color:transparent; }
  html,body { margin:0; background:var(--bg); color:var(--ink);
    font:16px/1.4 -apple-system,system-ui,sans-serif; }
  .wrap { max-width:760px; margin:0 auto; padding:12px 12px 120px; }
  header { position:sticky; top:0; z-index:5; background:var(--bg); padding:8px 0 6px;
    border-bottom:1px solid var(--line); }
  .bar { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
  .prog { flex:1; height:8px; background:var(--panel); border-radius:6px; overflow:hidden; }
  .prog > i { display:block; height:100%; background:var(--acc); width:0; }
  .counts { font-size:12px; color:var(--mut); }
  .chip { font-size:12px; padding:2px 8px; border:1px solid var(--line); border-radius:20px; color:var(--mut); }
  .phrase { font-size:30px; font-weight:700; letter-spacing:.5px; }
  .hl { background:#3b6ea5; color:#fff; padding:0 4px; border-radius:4px; }
  .ctx { color:var(--mut); font-size:14px; margin:2px 0; }
  .seg { margin:8px 0; font-size:17px; }
  .card { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:12px; margin:10px 0; }
  .btn { background:var(--panel); color:var(--ink); border:1px solid var(--line);
    border-radius:10px; padding:12px 14px; font-size:15px; cursor:pointer; }
  .btn:active { transform:scale(.98); }
  .audio { display:flex; gap:8px; }
  .audio .btn { flex:1; font-weight:600; }
  .grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
  .opt { text-align:left; }
  .opt.sel { outline:2px solid var(--acc); border-color:var(--acc); background:#223247; }
  .opt small { display:block; color:var(--mut); font-size:11px; margin-top:2px; }
  .lab { font-size:12px; text-transform:uppercase; letter-spacing:.8px; color:var(--mut); margin:0 0 6px; }
  .row { display:flex; gap:8px; flex-wrap:wrap; }
  .row .btn { flex:1; }
  .stance { display:inline-block; padding:3px 10px; border-radius:20px; font-size:13px; font-weight:600; }
  .stance.affiliative{ background:var(--aff); } .stance.neutral{ background:var(--neu); } .stance.adversarial{ background:var(--adv); }
  .pill { padding:8px 12px; border-radius:20px; }
  .pill.sel { outline:2px solid var(--acc); }
  textarea, select { width:100%; background:var(--bg); color:var(--ink); border:1px solid var(--line);
    border-radius:8px; padding:8px; font-size:15px; }
  .nav { position:fixed; left:0; right:0; bottom:0; background:var(--panel); border-top:1px solid var(--line);
    display:flex; gap:8px; padding:10px 12px; padding-bottom:calc(10px + env(safe-area-inset-bottom)); }
  .nav .btn { flex:1; font-weight:600; }
  .nav .prim { background:var(--acc); border-color:var(--acc); }
  .save { font-size:12px; color:var(--mut); text-align:center; }
  .danger { color:#e88; }
  details { margin-top:8px; } summary { cursor:pointer; color:var(--mut); font-size:13px; }
  .done { opacity:.55; }
  .discarded { outline:2px solid var(--warn); }
  dialog { background:var(--panel); color:var(--ink); border:1px solid var(--line); border-radius:12px; max-width:90%; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="bar">
      <button class="btn" onclick="go(-1)">&larr;</button>
      <div class="prog"><i id="progbar"></i></div>
      <button class="btn" onclick="go(1)">&rarr;</button>
    </div>
    <div class="bar" style="margin-top:6px;">
      <span class="chip" id="pos"></span>
      <span class="counts" id="counts"></span>
      <button class="btn" style="margin-left:auto;padding:6px 10px;font-size:13px;" onclick="nextUnlabeled()">Next unlabeled</button>
    </div>
  </header>

  <div id="clip"></div>

  <div class="card">
    <p class="lab">Function (Tier 1)</p>
    <div class="grid" id="functions"></div>
    <div style="margin-top:10px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
      <span class="lab" style="margin:0;">Stance</span>
      <span id="stanceview" class="stance neutral">--</span>
      <span class="chip" id="literalview">--</span>
      <button class="btn" style="padding:6px 10px;font-size:13px;" onclick="cycleStance()">override</button>
    </div>
  </div>

  <div class="card">
    <p class="lab">Arousal (independent)</p>
    <div class="row" id="arousal"></div>
    <p class="lab" style="margin-top:12px;">Confidence</p>
    <div class="row" id="confidence"></div>
    <details>
      <summary>Secondary function + notes (optional)</summary>
      <select id="secondary" style="margin-top:8px;" onchange="set('secondary', this.value)"></select>
      <textarea id="notes" rows="2" placeholder="notes" style="margin-top:8px;" oninput="set('notes', this.value)"></textarea>
    </details>
  </div>

  <div class="card">
    <div class="row">
      <button class="btn danger" onclick="openDiscard()">Discard clip</button>
      <button class="btn" onclick="clearOne()">Clear this label</button>
    </div>
    <p class="save" id="discardview"></p>
  </div>

  <div class="card">
    <div class="row">
      <button class="btn prim" onclick="exportJSON()">Export</button>
      <button class="btn" onclick="openImport()">Resume / import</button>
    </div>
    <p class="save" id="savestate">loading...</p>
  </div>
</div>

<div class="nav">
  <button class="btn" onclick="go(-1)">Prev</button>
  <button class="btn prim" onclick="go(1)">Save &amp; next</button>
</div>

<dialog id="discardDlg">
  <p class="lab">Discard reason</p>
  <div id="discardReasons"></div>
  <div class="row" style="margin-top:10px;"><button class="btn" onclick="discardDlg.close()">Cancel</button></div>
</dialog>
<dialog id="importDlg">
  <p class="lab">Paste exported JSON to merge progress</p>
  <textarea id="importText" rows="6"></textarea>
  <div class="row" style="margin-top:10px;">
    <button class="btn" onclick="importDlg.close()">Cancel</button>
    <button class="btn prim" onclick="doImport()">Import</button>
  </div>
</dialog>

<script>
const DATA = __PAYLOAD__;
const KEY = "pca_" + DATA.batch_id + "_v" + DATA.scheme_version;
const CB = DATA.codebook;
const FAM = CB.families;
let i = 0;
let ann = {};
try { ann = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch(e) { ann = {}; }

function cur() { return DATA.clips[i]; }
function rec() { const c = cur(); return ann[c.id] || (ann[c.id] = {}); }
function fnById(id) { return CB.functions.find(f => f.id === id); }

function save() {
  try { localStorage.setItem(KEY, JSON.stringify(ann)); document.getElementById("savestate").textContent = "saved ✓  " + labeledCount() + "/" + DATA.clips.length + " labeled"; }
  catch(e) { document.getElementById("savestate").innerHTML = "<span class='danger'>storage full – EXPORT now</span>"; }
}
function labeledCount() { return DATA.clips.filter(c => { const r = ann[c.id]; return r && (r.fine_tag || r.discarded); }).length; }

function set(field, val) { rec()[field] = val; rec().ts = Date.now(); save(); }

function setFunction(id) {
  const r = rec(); r.fine_tag = id; r.discarded = false; delete r.discard_reason;
  const f = fnById(id);
  if (!r.stance_overridden) r.stance = f.stance;
  r.literal = f.literal; r.ts = Date.now();
  save(); render();
}
function cycleStance() {
  const r = rec(); const order = CB.stances;
  const k = order.indexOf(r.stance); r.stance = order[(k + 1) % order.length];
  r.stance_overridden = true; save(); render();
}
function clearOne() { delete ann[cur().id]; save(); render(); }

function openDiscard() {
  const box = document.getElementById("discardReasons"); box.innerHTML = "";
  CB.discard_reasons.forEach(reason => {
    const b = document.createElement("button"); b.className = "btn"; b.style.width = "100%"; b.style.marginBottom = "6px";
    b.textContent = reason;
    b.onclick = () => { const r = rec(); r.discarded = true; r.discard_reason = reason; delete r.fine_tag; r.ts = Date.now(); save(); discardDlg.close(); render(); go(1); };
    box.appendChild(b);
  });
  discardDlg.showModal();
}
function openImport() { document.getElementById("importText").value = ""; importDlg.showModal(); }
function doImport() {
  try {
    const obj = JSON.parse(document.getElementById("importText").value);
    const incoming = obj.annotations || obj;
    Object.keys(incoming).forEach(k => { if (DATA.clips.find(c => c.id === k)) ann[k] = incoming[k]; });
    save(); importDlg.close(); render();
  } catch(e) { alert("Could not parse JSON"); }
}

function exportJSON() {
  const out = JSON.stringify({ batch_id: DATA.batch_id, scheme_version: DATA.scheme_version,
    exported: new Date().toISOString(), annotations: ann }, null, 2);
  // download
  const blob = new Blob([out], {type:"application/json"});
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
  a.download = "annotations_batch_" + DATA.batch_id + ".json"; document.body.appendChild(a); a.click(); a.remove();
  // clipboard fallback (robust on iPad)
  if (navigator.clipboard) navigator.clipboard.writeText(out).then(
    () => alert("Exported. JSON downloaded AND copied to clipboard – paste into Notes/email to be safe."),
    () => alert("Exported (download). Clipboard blocked; use the downloaded file.")
  ); else alert("Exported (download).");
}

function highlight(text, phrase) {
  if (!text) return "";
  const words = phrase.replace("_", " ");
  const re = new RegExp("\\b(" + words.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")\\b", "ig");
  const esc = text.replace(/[&<>]/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]));
  return esc.replace(re, "<span class='hl'>$1</span>");
}

function audioButtons() {
  const c = cur(); let h = "<div class='audio'>";
  DATA.windows.forEach(w => {
    if (c.audio[w.key]) h += "<button class='btn' onclick=\"play('" + w.key + "')\">▶ " + w.label + "</button>";
  });
  h += "</div>";
  DATA.windows.forEach(w => {
    if (c.audio[w.key]) h += "<audio id='au_" + w.key + "' src='data:audio/mp4;base64," + c.audio[w.key] + "' preload='none'></audio>";
  });
  return h;
}
function play(w) { const a = document.getElementById("au_" + w); if (a) { a.currentTime = 0; a.play(); } }

function render() {
  const c = cur(), r = ann[c.id] || {}, fam = FAM[c.phrase];
  document.getElementById("pos").textContent = (i + 1) + " / " + DATA.clips.length;
  document.getElementById("progbar").style.width = (100 * labeledCount() / DATA.clips.length) + "%";
  document.getElementById("counts").textContent = c.phrase + "  ·  " + c.show;

  document.getElementById("clip").innerHTML =
    "<div class='card " + (r.discarded ? "discarded" : (r.fine_tag ? "done" : "")) + "'>" +
      "<div class='phrase'>" + c.phrase.replace("_"," ") + "</div>" +
      audioButtons() +
      (c.prev ? "<p class='ctx'>… " + highlight(c.prev, c.phrase) + "</p>" : "") +
      "<p class='seg'>" + highlight(c.text, c.phrase) + "</p>" +
      (c.next ? "<p class='ctx'>" + highlight(c.next, c.phrase) + " …</p>" : "") +
    "</div>";

  // functions for this family
  const fbox = document.getElementById("functions"); fbox.innerHTML = "";
  CB.functions.filter(f => f.families.includes(fam)).forEach(f => {
    const b = document.createElement("button");
    b.className = "btn opt" + (r.fine_tag === f.id ? " sel" : "");
    b.innerHTML = f.label + "<small>" + f.stance + (f.literal ? " · literal" : " · non-literal") + "</small>";
    b.onclick = () => setFunction(f.id);
    fbox.appendChild(b);
  });

  // stance view
  const sv = document.getElementById("stanceview");
  sv.className = "stance " + (r.stance || "neutral"); sv.textContent = r.stance || "--";
  document.getElementById("literalview").textContent =
    r.fine_tag ? (r.literal ? "literal" : "non-literal") + (r.stance_overridden ? " (stance overridden)" : "") : "--";

  // arousal / confidence pills (re-render after tap so the selection highlights)
  pills("arousal", CB.arousal_levels, r.arousal, v => { set("arousal", v); render(); });
  pills("confidence", CB.confidence_levels, r.confidence, v => { set("confidence", v); render(); });

  // secondary select
  const sel = document.getElementById("secondary");
  sel.innerHTML = "<option value=''>(no secondary)</option>" +
    CB.functions.filter(f => f.families.includes(fam)).map(f =>
      "<option value='" + f.id + "'" + (r.secondary === f.id ? " selected" : "") + ">" + f.label + "</option>").join("");
  document.getElementById("notes").value = r.notes || "";
  document.getElementById("discardview").textContent = r.discarded ? ("DISCARDED: " + r.discard_reason) : "";
  save();
}

function pills(boxId, opts, val, cb) {
  const box = document.getElementById(boxId); box.innerHTML = "";
  opts.forEach(o => {
    const b = document.createElement("button");
    b.className = "btn pill" + (val === o ? " sel" : "");
    b.textContent = o; b.onclick = () => cb(o);
    box.appendChild(b);
  });
}

function go(d) { i = Math.max(0, Math.min(DATA.clips.length - 1, i + d)); window.scrollTo(0,0); render(); }
function nextUnlabeled() {
  for (let k = 1; k <= DATA.clips.length; k++) {
    const j = (i + k) % DATA.clips.length; const r = ann[DATA.clips[j].id];
    if (!r || (!r.fine_tag && !r.discarded)) { i = j; window.scrollTo(0,0); render(); return; }
  }
  alert("All clips in this batch are labeled or discarded.");
}
render();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
