#!/usr/bin/env python3
"""
Extract and KEEP the frame sequence, instead of pooling it away at extraction time.

Every feature set in features/ is already pooled. src/17 saves mean and standard
deviation per layer, src/20 computes frames and then discards them at the pooling
step, src/21 pools DAC the same way. A contour cannot be recovered from a mean and
a standard deviation, so every question about timing is unanswerable against the
stored features no matter how the probe is written.

This script saves the frames themselves. Readouts then become post-processing over
a saved array, computed in seconds and iterated without touching a model again,
which is the property the current pipeline lacks.

Storage is float16, which halves the footprint and is well inside the precision a
linear probe resolves. Sequences are right-padded to the longest clip in the set
and a lengths vector is saved alongside, so no readout ever pools over padding.

  representation   what is saved                             frame rate
  wavlm            hidden_states[20]                         50 Hz
  hubert           hidden_states[23]                         50 Hz
  whisper          encoder hidden_states[9], valid frames    50 Hz
  mimi_pre         input_proj(latent), quantiser space       12.5 Hz
  mimi_post        summed codebook vectors, same space       12.5 Hz
  mimi_codes       raw code indices, int16                   12.5 Hz
  dac_pre          encoder output                            75 Hz
  dac_post         quantised output                          75 Hz
  sylber           per-syllable features + [start, end]      ~4 Hz, variable
  dycast           plats, pcodes, toks, durs                 ~6-24 Hz, variable

mimi_codes is saved because the discrete stream cannot take a temporal basis.
Code indices are categorical, so index 5 is not between 4 and 6 and a trend
coefficient over them is meaningless. Its order-aware summary has to be transition
statistics over consecutive codes, which needs the sequence, not a histogram.

Usage:
  python3 src/31_extract_frames.py --models dycast --limit 8
  python3 src/31_extract_frames.py --models wavlm hubert whisper
  python3 src/31_extract_frames.py --models all
"""
import argparse, csv, pickle, sys, time, warnings
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
BEST_LAYER = {"wavlm": 20, "hubert": 23, "whisper": 9}
# src/32 showed the argmax layer choice is not stable across folds, and that the
# reported figures were inflated by choosing the winner on the same data
# (wavlm +0.003, whisper +0.015, hubert +0.029). So a band is saved rather than
# one layer, and the choice is made honestly downstream instead of baked in here.
BAND = {"wavlm": [19, 20, 21], "hubert": [19, 21, 23], "whisper": [8, 9, 11]}
N_CODEBOOKS = 8
ALL = ["wavlm", "hubert", "whisper", "mimi", "dac", "sylber", "dycast"]


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


def save(name, window, ids, seqs, extra=None, dtype=np.float16):
    """Right-pad to the longest sequence and record true lengths.

    A clip can legitimately come back with nothing in it. Sylber finds no
    syllables in silence or in a stretch of laughter, and numpy gives that back
    as shape (0,) rather than (0, D), so taking the width from seqs[0] or calling
    lens.max() on an all-empty set would fail. Width is taken from the first clip
    that has one and empties are normalised, so a blank clip becomes length 0 and
    is skipped by any readout that respects lengths.
    """
    D = next((s.shape[1] for s in seqs if s.ndim == 2 and s.shape[0] > 0), None)
    if D is None:
        print(f"  SKIPPED {name}: every clip came back empty")
        return
    seqs = [s if (s.ndim == 2 and s.shape[1] == D) else np.zeros((0, D), dtype)
            for s in seqs]
    n_empty = sum(1 for s in seqs if len(s) == 0)
    if n_empty:
        print(f"  note: {n_empty}/{len(seqs)} clips empty for {name}, saved as length 0")
    lens = np.array([len(s) for s in seqs], dtype=np.int32)
    T = max(int(lens.max()), 1)
    X = np.zeros((len(seqs), T, D), dtype=dtype)
    for i, s in enumerate(seqs):
        X[i, :len(s)] = s.astype(dtype)
    p = OUT / name / f"{window}.npz"
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {"ids": np.array(ids), "X": X, "lengths": lens}
    if extra:
        payload.update(extra)
    np.savez_compressed(p, **payload)
    mb = p.stat().st_size / 1e6
    # p is only under ROOT when PC_FRAMES_DIR is unset, so relative_to would raise
    # as soon as frames are redirected to an external disk.
    try:
        shown = p.relative_to(ROOT)
    except ValueError:
        shown = p
    print(f"  saved {name:12} {X.shape} {X.dtype}  lens {lens.min()}-{lens.max()}"
          f"  {mb:.0f} MB -> {shown}")


# ----------------------------------------------------- frame extractors
# wavlm / whisper / mimi are src/20's functions unchanged. hubert shares the
# wavlm path. dac follows src/21.
def frames_hidden(model, fe, wav, device, band):
    """One forward pass, several layers out. band is a list of layer indices."""
    import torch
    iv = fe(wav, sampling_rate=16000, return_tensors="pt").input_values.to(device)
    with torch.no_grad():
        hs = model(iv, output_hidden_states=True).hidden_states
    return [hs[L][0].float().cpu().numpy() for L in band]


def frames_whisper(enc, fe, wav, device, band):
    """Whisper pads every input to 30 s, so only the real frames are kept."""
    import torch
    valid = min(1500, int(round(len(wav) / 16000 * 50)))
    feats = fe(wav, sampling_rate=16000, return_tensors="pt").input_features.to(device)
    with torch.no_grad():
        hs = enc(feats, output_hidden_states=True).hidden_states
    return [hs[L][0, :valid].float().cpu().numpy() for L in band]


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
    """Walk the clips for one model, checkpointing so a crash is not a restart.

    per_clip(path) returns {output_name: (T, D) array}. Progress is written to a
    pickle every `every` clips and removed once the real files land, so a run that
    dies at clip 800 on a rented box resumes there rather than from zero. Finished
    models are skipped outright unless --force.
    """
    finals = {n: OUT / n / f"{window}.npz" for n in dtypes}
    if all(p.exists() for p in finals.values()) and not force:
        print(f"  already done, skipping ({', '.join(dtypes)}). --force to redo")
        return
    ckpt = OUT / f".partial_{key}_{window}.pkl"
    acc, start = {n: [] for n in dtypes}, 0
    if ckpt.exists() and not force:
        try:
            with open(ckpt, "rb") as f:
                d = pickle.load(f)
            if d["ids"] == ids[:d["done"]]:
                acc, start = d["acc"], d["done"]
                print(f"  resuming from clip {start}/{len(paths)}")
            else:
                print("  checkpoint does not match this clip list, starting over")
        except Exception as e:
            print(f"  checkpoint unreadable ({e}), starting over")

    t0 = time.time()
    for i in range(start, len(paths)):
        for n, v in per_clip(paths[i]).items():
            acc[n].append(v)
        done = i + 1
        if done % every == 0:
            OUT.mkdir(parents=True, exist_ok=True)
            tmp = ckpt.with_suffix(".pkl.tmp")
            with open(tmp, "wb") as f:
                pickle.dump({"ids": ids[:done], "done": done, "acc": acc}, f, 4)
            tmp.replace(ckpt)                      # atomic, never a torn file
            print(f"  {done}/{len(paths)}  {time.time()-t0:.0f}s", flush=True)

    for n, dt in dtypes.items():
        save(n, window, ids, acc[n], dtype=dt)
    ckpt.unlink(missing_ok=True)


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=["dycast"])
    ap.add_argument("--window", default="W2_segment")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--force", action="store_true",
                    help="redo models whose outputs already exist, ignore checkpoints")
    args = ap.parse_args()
    models = ALL if args.models == ["all"] else args.models

    import torch
    device = ("cuda" if torch.cuda.is_available()
              else "mps" if torch.backends.mps.is_available() else "cpu")
    rows = load_keepers(args.limit)
    ids = [r["candidate_id"] for r in rows]
    paths = [CLIPS / args.window / (i + ".wav") for i in ids]
    print(f"device={device} | clips={len(rows)} | window={args.window} | models={models}")

    for key in models:
        t0 = time.time()
        print(f"\n[{key}]")

        if key in ("wavlm", "hubert"):
            from transformers import AutoFeatureExtractor, AutoModel
            fe = AutoFeatureExtractor.from_pretrained(CKPT[key])
            m = AutoModel.from_pretrained(CKPT[key]).to(device).eval()
            band = BAND[key]
            def per_clip(p, m=m, fe=fe, band=band, key=key):
                F = frames_hidden(m, fe, read_wav(p, 16000), device, band)
                return {f"{key}_L{L}": F[j] for j, L in enumerate(band)}
            run(key, args.window, ids, paths, per_clip,
                {f"{key}_L{L}": np.float16 for L in band}, args.force)

        elif key == "whisper":
            from transformers import WhisperFeatureExtractor, WhisperModel
            fe = WhisperFeatureExtractor.from_pretrained(CKPT["whisper"])
            enc = WhisperModel.from_pretrained(CKPT["whisper"]).to(device).eval().get_encoder()
            band = BAND["whisper"]
            def per_clip(p, enc=enc, fe=fe, band=band):
                F = frames_whisper(enc, fe, read_wav(p, 16000), device, band)
                return {f"whisper_L{L}": F[j] for j, L in enumerate(band)}
            run("whisper", args.window, ids, paths, per_clip,
                {f"whisper_L{L}": np.float16 for L in band}, args.force)

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
                return {"sylber": np.asarray(o["segment_features"], dtype=np.float32),
                        "sylber_bounds": np.asarray(o["segments"], dtype=np.float32)}
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
