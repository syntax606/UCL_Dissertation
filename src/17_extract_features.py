#!/usr/bin/env python3
"""
Phase 2 feature extraction for the pragmatic-contrast probing study.

For each keeper clip (one WAV per context window W1/W2/W3) this produces, per
representation, a fixed-length vector suitable for a linear probe:

  wavlm / hubert / whisper : mean+std pooled hidden states, saved PER LAYER
                             -> X shape (n_clips, n_layers, 2*hidden)
  mimi                     : per-codebook unigram histograms, ALL codebooks 0..7
                             (block j of 2048 dims == codebook j; the probe slices
                              these, e.g. all-8 for the deployed condition)
                             -> X shape (n_clips, 8*codebook_size)
  text                     : sentence-embedding of (a) the target phrase alone
                             and (b) the discourse context (prev+seg+next)
                             -> X shape (n_clips, dim)   [window-independent]

Keepers are read straight from data/annotations/annotation_sheet_labeled.csv
(rows whose stance is affiliative/neutral/adversarial). Clips are expected at
data/clips/<window>/<candidate_id>.wav (produced by src/05_extract_audio.py).
Outputs land in  features/<model>/<window>.npz  with an aligned `ids` array.

Audio models run one clip at a time (batch=1) so there is no padding to pool
over. Whisper is padded to 30s internally, so we pool only the valid frames.

This is a GPU job. On a fresh CUDA box (e.g. Lambda Cloud, A100) install:
    pip install torch transformers soundfile librosa sentence-transformers "numpy<2"
(Lambda Stack ships torch/CUDA; "numpy<2" avoids an ABI clash, and you may need
 `pip install -U Pillow` for a recent transformers.)

Usage:
  python3 src/17_extract_features.py                       # everything
  python3 src/17_extract_features.py --limit 5             # smoke test
  python3 src/17_extract_features.py --models wavlm text   # subset
  python3 src/17_extract_features.py --windows W2_segment  # subset
"""
import argparse, csv, time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SHEET = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
CLIPS = ROOT / "data" / "clips"
OUT = ROOT / "features"
WINDOWS = ["W1_local", "W2_segment", "W3_discourse"]
CLASSES = ("affiliative", "neutral", "adversarial")

CKPT = {
    "wavlm":   "microsoft/wavlm-large",
    "hubert":  "facebook/hubert-large-ll60k",
    "whisper": "openai/whisper-small",
    "mimi":    "kyutai/mimi",
    "text":    "sentence-transformers/all-mpnet-base-v2",
}
AUDIO_MODELS = ["wavlm", "hubert", "whisper"]


def load_keepers(limit=None):
    rows = [r for r in csv.DictReader(open(SHEET, newline=""))
            if r.get("stance", "").strip() in CLASSES]
    return rows[:limit] if limit else rows


def read_wav(path, target_sr):
    import soundfile as sf, librosa
    wav, sr = sf.read(path, dtype="float32")
    if wav.ndim > 1:
        wav = wav.mean(axis=1)
    if sr != target_sr:
        wav = librosa.resample(wav, orig_sr=sr, target_sr=target_sr)
    return wav


def pool_mean_std(hidden):
    """hidden: (T, H) tensor -> (2H,) numpy: [mean over T ; std over T]."""
    import torch
    return torch.cat([hidden.mean(dim=0), hidden.std(dim=0)]).float().cpu().numpy()


def run_ssl(model_key, rows, windows, device, args):
    import torch
    from transformers import AutoFeatureExtractor, AutoModel
    fe = AutoFeatureExtractor.from_pretrained(CKPT[model_key])
    model = AutoModel.from_pretrained(CKPT[model_key]).to(device).eval()
    for w in windows:
        out = OUT / model_key / f"{w}.npz"
        if out.exists() and not args.overwrite:
            print(f"  [{model_key}/{w}] exists, skip"); continue
        ids, X, t0 = [], [], time.time()
        for i, r in enumerate(rows):
            wav = read_wav(CLIPS / w / (r["candidate_id"] + ".wav"), 16000)
            iv = fe(wav, sampling_rate=16000, return_tensors="pt").input_values.to(device)
            with torch.no_grad():
                hs = model(iv, output_hidden_states=True).hidden_states
            X.append(np.stack([pool_mean_std(h[0]) for h in hs]))
            ids.append(r["candidate_id"])
            if (i + 1) % 100 == 0:
                print(f"  [{model_key}/{w}] {i+1}/{len(rows)}  {time.time()-t0:.0f}s")
        _save(out, ids, X, model_key, w, t0)


def run_whisper(rows, windows, device, args):
    import torch
    from transformers import WhisperFeatureExtractor, WhisperModel
    fe = WhisperFeatureExtractor.from_pretrained(CKPT["whisper"])
    enc = WhisperModel.from_pretrained(CKPT["whisper"]).to(device).eval().get_encoder()
    for w in windows:
        out = OUT / "whisper" / f"{w}.npz"
        if out.exists() and not args.overwrite:
            print(f"  [whisper/{w}] exists, skip"); continue
        ids, X, t0 = [], [], time.time()
        for i, r in enumerate(rows):
            wav = read_wav(CLIPS / w / (r["candidate_id"] + ".wav"), 16000)
            valid = min(1500, int(round(len(wav) / 16000 * 50)))  # 50 enc frames/s
            feats = fe(wav, sampling_rate=16000, return_tensors="pt").input_features.to(device)
            with torch.no_grad():
                hs = enc(feats, output_hidden_states=True).hidden_states
            X.append(np.stack([pool_mean_std(h[0, :valid]) for h in hs]))
            ids.append(r["candidate_id"])
            if (i + 1) % 100 == 0:
                print(f"  [whisper/{w}] {i+1}/{len(rows)}  {time.time()-t0:.0f}s")
        _save(out, ids, X, "whisper", w, t0)


def run_mimi(rows, windows, device, args, n_codebooks=8):
    """All 8 codebooks are kept, codebook 0 included.

    Codebook 0 is the WavLM-distilled stream; the codec-probing literature shows it
    carries phonetic rather than semantic content, which is why an earlier version of
    this script skipped it. That was the wrong call for two reasons. A model built on
    Mimi consumes the whole stack, so the deployment-relevant condition is all 8, and
    skipping codebook 0 leaves the one place pragmatic information might survive
    untested. The probe slices this matrix into per-codebook blocks.
    """
    import torch
    from transformers import AutoFeatureExtractor, MimiModel
    fe = AutoFeatureExtractor.from_pretrained(CKPT["mimi"])
    model = MimiModel.from_pretrained(CKPT["mimi"]).to(device).eval()
    K = model.config.codebook_size
    probe_books = list(range(n_codebooks))        # 0..7, block j == codebook j
    for w in windows:
        out = OUT / "mimi" / f"{w}.npz"
        if out.exists() and not args.overwrite:
            print(f"  [mimi/{w}] exists, skip"); continue
        ids, X, t0 = [], [], time.time()
        for i, r in enumerate(rows):
            wav = read_wav(CLIPS / w / (r["candidate_id"] + ".wav"), 24000)
            iv = fe(raw_audio=wav, sampling_rate=24000, return_tensors="pt").input_values.to(device)
            with torch.no_grad():
                codes = model.encode(iv, num_quantizers=n_codebooks).audio_codes[0].cpu().numpy()
            T = codes.shape[1]
            hist = np.stack([np.bincount(codes[cb], minlength=K).astype(np.float32) / max(T, 1)
                             for cb in probe_books])
            X.append(hist.reshape(-1)); ids.append(r["candidate_id"])
            if (i + 1) % 100 == 0:
                print(f"  [mimi/{w}] {i+1}/{len(rows)}  {time.time()-t0:.0f}s")
        _save(out, ids, X, "mimi", w, t0,
              meta=np.array([f"codebooks={probe_books}", f"K={K}"]))


def run_text(rows, device, args):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(CKPT["text"], device=device)
    ids = [r["candidate_id"] for r in rows]
    target = [r["target_phrase"].replace("_", " ") for r in rows]
    context = [" ".join([r.get("prev_text", ""), r.get("segment_text", ""),
                         r.get("next_text", "")]).strip() for r in rows]
    for name, texts in [("targetonly", target), ("context", context)]:
        out = OUT / "text" / f"{name}.npz"
        if out.exists() and not args.overwrite:
            print(f"  [text/{name}] exists, skip"); continue
        X = model.encode(texts, batch_size=64, convert_to_numpy=True,
                         show_progress_bar=False).astype(np.float32)
        out.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(out, ids=np.array(ids), X=X)
        print(f"  [text/{name}] saved {X.shape} -> {out.name}")


def _save(out, ids, X, model, w, t0, meta=None):
    X = np.asarray(X, dtype=np.float32)
    out.parent.mkdir(parents=True, exist_ok=True)
    kw = dict(ids=np.array(ids), X=X)
    if meta is not None:
        kw["meta"] = meta
    np.savez_compressed(out, **kw)
    print(f"  [{model}/{w}] saved {X.shape} -> {out.name}  ({time.time()-t0:.0f}s)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+",
                    default=["wavlm", "hubert", "whisper", "mimi", "text"])
    ap.add_argument("--windows", nargs="+", default=WINDOWS)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    import torch
    device = ("cuda" if torch.cuda.is_available()
              else "mps" if torch.backends.mps.is_available() else "cpu")
    rows = load_keepers(args.limit)
    print(f"device={device} | clips={len(rows)} | models={args.models} | windows={args.windows}")
    for m in args.models:
        print(f"== {m} ==")
        if m in ("wavlm", "hubert"):
            run_ssl(m, rows, args.windows, device, args)
        elif m == "whisper":
            run_whisper(rows, args.windows, device, args)
        elif m == "mimi":
            run_mimi(rows, args.windows, device, args)
        elif m == "text":
            run_text(rows, device, args)
        else:
            print(f"  unknown model {m}, skip")
    print("done.")


if __name__ == "__main__":
    main()
