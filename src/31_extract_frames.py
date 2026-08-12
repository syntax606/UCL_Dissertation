#!/usr/bin/env python3
"""
Extract and KEEP the frame sequence, instead of pooling it away at extraction time.

Every feature set in features/ is already pooled. src/17 saves mean and standard
deviation per layer, src/20 computes frames and then discards them at the pooling
step, src/21 pools DAC the same way. A contour cannot be recovered from a mean and
a standard deviation, so every question about timing is unanswerable against the
stored features no matter how the probe is written.

This script saves the frames themselves, for EVERY layer. A transformer forward
pass computes all hidden states whether or not they are collected, so keeping all
25 costs no extra GPU time, only disk. Selecting a layer here would mean choosing
under the pooled readout, which is the instrument this rebuild exists to replace,
and src/32 showed that choice is neither stable across folds nor honest about its
own performance. So nothing is chosen here. Layer, readout and codebook decisions
all move downstream, where they can be made against the evidence.

Storage is one directory per representation holding three files:

    <window>.X.npy         (clips, frames, dim), float16 or int16, memory-mappable
    <window>.lengths.npy   (clips,) true frame count, padding starts after it
    <window>.ids.npy       (clips,) candidate_id, aligned with X

.npy rather than .npz so downstream readouts can mmap one representation without
loading tens of GB, and so this script can stream to disk clip by clip instead of
holding the whole run in memory.

  representation   what is saved                             frame rate
  wavlm_L0..L24    every hidden state                        50 Hz
  hubert_L0..L24   every hidden state                        50 Hz
  whisper_L0..L12  encoder hidden states, valid frames only   50 Hz
  mimi_pre         input_proj(latent), quantiser space       12.5 Hz
  mimi_post        summed codebook vectors, same space       12.5 Hz
  mimi_codes       raw code indices, int16                   12.5 Hz
  dac_pre          encoder output                            75 Hz
  dac_post         quantised output                          75 Hz
  sylber           per-syllable features, plus boundaries    ~4 Hz, variable
  dycast           plats, pcodes, toks, durs                 ~6-24 Hz, variable

mimi_codes is saved because the discrete stream cannot take a temporal basis. Code
indices are categorical, so index 5 is not between 4 and 6 and a trend coefficient
over them is meaningless. Its order-aware summary has to be transition statistics
over consecutive codes, which needs the sequence, not a histogram.

N_CODEBOOKS = 8 is the deployed Mimi configuration, 1 semantic plus 7 acoustic of
32 available. For DAC it is a deliberate truncation of 32 down to Mimi's budget,
matching src/21, so DAC figures here characterise DAC-held-to-Mimi and not DAC.

Usage:
  python3 src/31_extract_frames.py --models dycast --limit 8
  python3 src/31_extract_frames.py --models all
  python3 src/31_extract_frames.py --models wavlm --force
"""
import argparse, csv, json, sys, time, warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
SHEET = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
CLIPS = ROOT / "data" / "clips"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import FRAMES_DIR as OUT   # PC_FRAMES_DIR redirects this to any disk
CLASSES = ("affiliative", "neutral", "adversarial")

CKPT = {"wavlm": "microsoft/wavlm-large", "hubert": "facebook/hubert-large-ll60k",
        "whisper": "openai/whisper-small", "mimi": "kyutai/mimi",
        "dac": "descript/dac_24khz", "dycast": "lucadellalib/dycast"}
N_CODEBOOKS = 8
ALL = ["wavlm", "hubert", "whisper", "mimi", "dac", "sylber", "dycast"]

# Fixed-rate models give the same frame count for every clip of the same duration,
# so the array is allocated exactly. Sylber and DyCAST decide their own boundaries,
# so their length varies per clip and the allocation needs headroom over whatever
# the probe clip happened to produce.
HEADROOM = {"sylber": 4.0, "dycast": 3.0}


# --------------------------------------------------------------------- io
def load_keepers(limit=None):
    rows = [r for r in csv.DictReader(open(SHEET, newline=""))
            if r.get("stance", "").strip() in CLASSES]
    return rows[:limit] if limit else rows


def read_wav(path, target_sr):
    """Identical to src/20 read_wav, so the forward pass matches the old numbers."""
    import soundfile as sf, librosa
    wav, sr = sf.read(str(path), dtype="float32")
    if wav.ndim > 1:
        wav = wav.mean(axis=1)
    if sr != target_sr:
        wav = librosa.resample(wav, orig_sr=sr, target_sr=target_sr)
    return wav


class Writer:
    """Streams one representation to a memory-mapped .npy, one clip at a time.

    Nothing accumulates in RAM. At 25 layers the list-of-arrays approach this
    replaces would have held tens of GB before writing anything, and the periodic
    checkpoint would have tried to pickle all of it.
    """

    def __init__(self, name, window, n, T, D, dtype, resume=False):
        self.dir = OUT / name
        self.dir.mkdir(parents=True, exist_ok=True)
        self.stem = self.dir / window
        self.xp = Path(f"{self.stem}.X.npy")
        self.T, self.name = T, name
        lp = Path(f"{self.stem}.lengths.npy")
        # "w+" truncates and zeroes. On resume that would silently wipe every clip
        # already written and refill it with zeros, so the file must be reopened
        # in place instead.
        if resume and self.xp.exists():
            self.X = np.lib.format.open_memmap(self.xp, mode="r+")
            if self.X.shape != (n, T, D):
                raise ValueError(
                    f"{name}: existing array is {self.X.shape}, this run wants "
                    f"{(n, T, D)}. Rerun with --force.")
            self.lengths = np.load(lp) if lp.exists() else np.zeros(n, dtype=np.int32)
        else:
            self.X = np.lib.format.open_memmap(
                self.xp, mode="w+", dtype=dtype, shape=(n, T, D))
            self.lengths = np.zeros(n, dtype=np.int32)
        self.n_empty = 0

    def write(self, i, arr):
        # A clip can legitimately come back with nothing in it. Sylber finds no
        # syllables in silence or laughter, and numpy returns that as shape (0,)
        # rather than (0, D). Length 0 is recorded and every readout that respects
        # lengths will skip it.
        if arr.ndim != 2 or arr.shape[0] == 0:
            self.lengths[i] = 0
            self.n_empty += 1
            return
        t = arr.shape[0]
        if t > self.T:
            raise ValueError(
                f"{self.name}: clip {i} produced {t} frames, allocated {self.T}. "
                f"Raise HEADROOM for this model and rerun with --force.")
        self.X[i, :t] = arr.astype(self.X.dtype)
        self.lengths[i] = t

    def flush(self, ids, done):
        self.X.flush()
        np.save(f"{self.stem}.lengths.npy", self.lengths)
        np.save(f"{self.stem}.ids.npy", np.array(ids))
        (self.dir / f".{Path(self.stem).name}.progress").write_text(str(done))

    def close(self, ids):
        self.flush(ids, len(ids))
        (self.dir / f".{Path(self.stem).name}.progress").unlink(missing_ok=True)
        mb = self.xp.stat().st_size / 1e6
        lo, hi = int(self.lengths.min()), int(self.lengths.max())
        empt = f"  {self.n_empty} empty" if self.n_empty else ""
        try:
            shown = self.xp.relative_to(ROOT)
        except ValueError:
            shown = self.xp
        print(f"  saved {self.name:14} {self.X.shape} {self.X.dtype}  "
              f"lens {lo}-{hi}{empt}  {mb:.0f} MB -> {shown}")


def load_frames(name, window="W2_segment"):
    """Read back what this script wrote, without pulling X into memory.

    Downstream readouts should use this. X stays memory-mapped, so a single layer
    can be scanned without loading the rest.
    """
    stem = OUT / name / window
    return {"X": np.load(f"{stem}.X.npy", mmap_mode="r"),
            "lengths": np.load(f"{stem}.lengths.npy"),
            "ids": np.load(f"{stem}.ids.npy", allow_pickle=True)}


# ----------------------------------------------------- frame extractors
# wavlm / whisper / mimi follow src/20's functions. hubert shares the wavlm path.
# dac follows src/21. All now return every layer rather than a selected one.
def frames_hidden(model, fe, wav, device):
    import torch
    iv = fe(wav, sampling_rate=16000, return_tensors="pt").input_values.to(device)
    with torch.no_grad():
        hs = model(iv, output_hidden_states=True).hidden_states
    return [h[0].float().cpu().numpy() for h in hs]


def frames_whisper(enc, fe, wav, device):
    """Whisper pads every input to 30 s, so only the real frames are kept."""
    import torch
    valid = min(1500, int(round(len(wav) / 16000 * 50)))
    feats = fe(wav, sampling_rate=16000, return_tensors="pt").input_features.to(device)
    with torch.no_grad():
        hs = enc(feats, output_hidden_states=True).hidden_states
    return [h[0, :valid].float().cpu().numpy() for h in hs]


def frames_mimi(model, wav, device):
    """Returns (pre, post, codes). Pre and post live in the quantiser's projected
    space, which is the only pairing where the two are comparable, see src/24."""
    import torch
    x = torch.tensor(wav)[None, None].to(device)
    with torch.no_grad():
        enc = model.encoder(x)
        enc = model.encoder_transformer(enc.transpose(1, 2)).last_hidden_state
        d = model.downsample(enc.transpose(1, 2))
        codes = model.quantizer.encode(d, num_quantizers=N_CODEBOOKS).transpose(0, 1)
        q = model.quantizer
        pre_parts, post_parts = [], []
        for rvq, cb in ((q.semantic_residual_vector_quantizer,
                         codes[:, :q.num_semantic_quantizers]),
                        (q.acoustic_residual_vector_quantizer,
                         codes[:, q.num_semantic_quantizers:])):
            pre = rvq.input_proj(d) if rvq.input_proj is not None else d
            post = torch.zeros_like(pre)
            for i, idx in enumerate(cb.transpose(0, 1)):
                post = post + rvq.layers[i].decode(idx)
            pre_parts.append(pre); post_parts.append(post)
        pre = torch.cat(pre_parts, dim=1)[0].transpose(0, 1)
        post = torch.cat(post_parts, dim=1)[0].transpose(0, 1)
    return (pre.float().cpu().numpy(), post.float().cpu().numpy(),
            codes[0].transpose(0, 1).cpu().numpy().astype(np.int16))


def frames_dac(model, wav, device):
    import torch
    x = torch.tensor(wav)[None, None].to(device)
    with torch.no_grad():
        e = model.encoder(x)
        q = model.quantizer(e, n_quantizers=N_CODEBOOKS)[0]
    return (e[0].transpose(0, 1).float().cpu().numpy(),
            q[0].transpose(0, 1).float().cpu().numpy())


# -------------------------------------------------------------- runner
def run(key, window, ids, paths, per_clip, dtypes, force=False, every=100):
    """Walk the clips for one model, streaming each to disk as it is produced.

    per_clip(path) returns {output_name: (T, D) array}. Shapes are taken from the
    first clip and the arrays allocated once, so memory stays flat regardless of
    how many layers are saved. Progress is a small integer on disk rather than a
    copy of the data, so a run that dies at clip 800 on a rented box resumes there.
    """
    n = len(paths)
    done_file = OUT / f".{key}_{window}.done"
    if done_file.exists() and not force:
        print(f"  already done, skipping. --force to redo")
        return

    # Resume is decided BEFORE any writer is opened. Opening first and reopening
    # after would zero the file and lose everything already extracted.
    prog = OUT / f".{key}_{window}.progress"
    start = 0
    if prog.exists() and not force:
        try:
            saved = json.loads(prog.read_text())
            if saved["ids"] == ids[:saved["done"]]:
                start = saved["done"]
                print(f"  resuming from clip {start}/{n}")
            else:
                print("  progress file is for a different clip list, starting over")
        except Exception as e:
            print(f"  progress file unusable ({e}), starting over")

    # shapes from the first clip, plus headroom where the model picks its own units
    probe = per_clip(paths[0])
    head = HEADROOM.get(key, 1.0)
    writers = {}
    for name, arr in probe.items():
        T = max(int(np.ceil(arr.shape[0] * head)), 1)
        writers[name] = Writer(name, window, n, T, arr.shape[1], dtypes[name],
                               resume=start > 0)

    t0 = time.time()
    for i in range(start, n):
        out = probe if i == 0 else per_clip(paths[i])
        for name, arr in out.items():
            writers[name].write(i, arr)
        if (i + 1) % every == 0:
            for w in writers.values():
                w.X.flush()
                np.save(f"{w.stem}.lengths.npy", w.lengths)
            prog.write_text(json.dumps({"done": i + 1, "ids": ids[:i + 1]}))
            print(f"  {i+1}/{n}  {time.time()-t0:.0f}s", flush=True)

    for w in writers.values():
        w.close(ids)
    prog.unlink(missing_ok=True)
    done_file.write_text(json.dumps(sorted(writers)))


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=["dycast"])
    ap.add_argument("--window", default="W2_segment")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--force", action="store_true",
                    help="redo models already finished, ignore any progress file")
    args = ap.parse_args()
    models = ALL if args.models == ["all"] else args.models

    import torch
    device = ("cuda" if torch.cuda.is_available()
              else "mps" if torch.backends.mps.is_available() else "cpu")
    rows = load_keepers(args.limit)
    ids = [r["candidate_id"] for r in rows]
    paths = [CLIPS / args.window / (i + ".wav") for i in ids]
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"device={device} | clips={len(rows)} | window={args.window} | models={models}")

    for key in models:
        t0 = time.time()
        print(f"\n[{key}]")

        if key in ("wavlm", "hubert"):
            from transformers import AutoFeatureExtractor, AutoModel
            fe = AutoFeatureExtractor.from_pretrained(CKPT[key])
            m = AutoModel.from_pretrained(CKPT[key]).to(device).eval()
            nl = m.config.num_hidden_layers + 1
            def per_clip(p, m=m, fe=fe, key=key):
                return {f"{key}_L{j}": F for j, F in
                        enumerate(frames_hidden(m, fe, read_wav(p, 16000), device))}
            run(key, args.window, ids, paths, per_clip,
                {f"{key}_L{j}": np.float16 for j in range(nl)}, args.force)

        elif key == "whisper":
            from transformers import WhisperFeatureExtractor, WhisperModel
            fe = WhisperFeatureExtractor.from_pretrained(CKPT["whisper"])
            enc = WhisperModel.from_pretrained(CKPT["whisper"]).to(device).eval().get_encoder()
            nl = enc.config.encoder_layers + 1
            def per_clip(p, enc=enc, fe=fe):
                return {f"whisper_L{j}": F for j, F in
                        enumerate(frames_whisper(enc, fe, read_wav(p, 16000), device))}
            run("whisper", args.window, ids, paths, per_clip,
                {f"whisper_L{j}": np.float16 for j in range(nl)}, args.force)

        elif key == "mimi":
            from transformers import MimiModel
            m = MimiModel.from_pretrained(CKPT["mimi"]).to(device).eval()
            def per_clip(p, m=m):
                a, b, c = frames_mimi(m, read_wav(p, 24000), device)
                return {"mimi_pre": a, "mimi_post": b, "mimi_codes": c}
            run("mimi", args.window, ids, paths, per_clip,
                {"mimi_pre": np.float16, "mimi_post": np.float16,
                 "mimi_codes": np.int16}, args.force)

        elif key == "dac":
            from transformers import DacModel          # as src/21, not the descript package
            m = DacModel.from_pretrained(CKPT["dac"]).to(device).eval()
            def per_clip(p, m=m):
                a, b = frames_dac(m, read_wav(p, 24000), device)
                return {"dac_pre": a, "dac_post": b}
            run("dac", args.window, ids, paths, per_clip,
                {"dac_pre": np.float16, "dac_post": np.float16}, args.force)

        elif key == "sylber":
            import torchaudio, soundfile as sf, torch as _t
            def _sf_load(uri, *a, **k):            # torchaudio 2.11 needs torchcodec
                arr, sr = sf.read(str(uri), dtype="float32", always_2d=True)
                return _t.from_numpy(arr.T), sr
            torchaudio.load = _sf_load
            from sylber import Segmenter
            seg = Segmenter(model_ckpt="sylber", device=device if device != "mps" else "cpu")
            def per_clip(p, seg=seg):
                o = seg(str(p), in_second=True)
                f = np.asarray(o["segment_features"], dtype=np.float32)
                b = np.asarray(o["segments"], dtype=np.float32)
                return {"sylber": f,
                        "sylber_bounds": b if b.ndim == 2 else np.zeros((0, 2), np.float32)}
            run("sylber", args.window, ids, paths, per_clip,
                {"sylber": np.float16, "sylber_bounds": np.float32}, args.force)

        elif key == "dycast":
            import dycast as dc
            codec = dc.DyCAST.from_pretrained(CKPT["dycast"])
            codec.eval().requires_grad_(False)
            def per_clip(p, codec=codec):
                sig = torch.tensor(read_wav(p, codec.sample_rate_input))[None]
                with torch.no_grad():
                    f = codec.sig_to_feats(sig)
                    d = codec.feats_to_durs(f)
                    pl, _ = codec.lats_to_plats(codec.feats_to_lats(f), d)
                    pc = codec.plats_to_pcodes(pl)
                    tk = codec.plats_to_toks(pl)
                return {"dycast_pre": pl[0].float().numpy(),
                        "dycast_post": pc[0].float().numpy(),
                        "dycast_toks": tk[0].numpy().astype(np.int16),
                        "dycast_durs": d[0].numpy().astype(np.int16)[:, None]}
            run("dycast", args.window, ids, paths, per_clip,
                {"dycast_pre": np.float16, "dycast_post": np.float16,
                 "dycast_toks": np.int16, "dycast_durs": np.int16}, args.force)

        else:
            print(f"  unknown model {key}"); continue
        print(f"  [{key}] done in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
