#!/usr/bin/env python3
"""
Does temporal order carry pragmatic stance, or is an order-free summary enough?

Every feature set in this study so far is permutation-invariant. Mean and standard
deviation pooling and unigram histograms both discard the order of frames, so the
frame-shuffling control used by Hsu et al. (2026, arXiv 2606.09366) is vacuous
against them by construction. That paper reports a bag-of-supports probe reaching
16.8 percent pooled against 77.7 percent with order preserved, which if it
transfers would mean the numbers in this study are floors rather than estimates.

This script re-pools the SAME forward pass three ways, so the representation is
held fixed and only the readout changes.

  meanstd    mean and std over all frames            order-free, current baseline
  seg<N>     split into N equal segments, pool each  coarse trajectory
  delta      meanstd plus meanstd of frame diffs     local dynamics

If stance decoding rises with the order-aware readouts, order matters and the
existing figures understate what these representations hold. If it does not,
stance is not trajectory-dependent in the way their emotion task was, which
defends the pooling choice and is a finding in its own right.

Models: wavlm and whisper run on CPU here but are slow; mimi is fast. Use --models
to pick. Outputs land in features/<model>_<readout>/<window>.npz.

Usage:
  python3 src/20_order_aware_features.py --models mimi --limit 5
  python3 src/20_order_aware_features.py --models mimi
  python3 src/20_order_aware_features.py --models wavlm
"""
import argparse, csv, time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SHEET = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
CLIPS = ROOT / "data" / "clips"
OUT = ROOT / "features"
CLASSES = ("affiliative", "neutral", "adversarial")
CKPT = {"wavlm": "microsoft/wavlm-large", "whisper": "openai/whisper-small",
        "mimi": "kyutai/mimi"}
BEST_LAYER = {"wavlm": 20, "whisper": 9}


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


def readouts(F, n_seg=4):
    """F: (T, D) numpy. Return dict of readout name -> 1-D feature vector.

    meanstd is exactly what src/17 computes, so the baseline here is directly
    comparable to the existing figures.
    """
    def ms(x):
        return np.concatenate([x.mean(0), x.std(0)]) if len(x) > 1 else \
               np.concatenate([x.mean(0), np.zeros(x.shape[1])])
    out = {"meanstd": ms(F)}
    idx = np.array_split(np.arange(len(F)), n_seg)
    out[f"seg{n_seg}"] = np.concatenate([ms(F[i]) if len(i) else np.zeros(2 * F.shape[1])
                                         for i in idx])
    d = np.diff(F, axis=0) if len(F) > 1 else np.zeros((1, F.shape[1]))
    out["delta"] = np.concatenate([ms(F), ms(d)])
    return out


def frames_wavlm(model, fe, wav, device, layer):
    import torch
    iv = fe(wav, sampling_rate=16000, return_tensors="pt").input_values.to(device)
    with torch.no_grad():
        hs = model(iv, output_hidden_states=True).hidden_states
    return hs[layer][0].float().cpu().numpy()


def frames_whisper(enc, fe, wav, device, layer):
    import torch
    valid = min(1500, int(round(len(wav) / 16000 * 50)))
    feats = fe(wav, sampling_rate=16000, return_tensors="pt").input_features.to(device)
    with torch.no_grad():
        hs = enc(feats, output_hidden_states=True).hidden_states
    return hs[layer][0, :valid].float().cpu().numpy()


def frames_mimi(model, wav, device, stage="post"):
    """Latent in the quantiser's projected space, per frame.

    stage="post" returns the summed codebook vectors, stage="pre" returns
    input_proj(encoder latent), the same vector before quantisation. Both live in
    the same space, so a readout comparison between them isolates quantisation."""
    import torch
    x = torch.tensor(wav)[None, None].to(device)
    with torch.no_grad():
        enc = model.encoder(x)
        enc = model.encoder_transformer(enc.transpose(1, 2)).last_hidden_state
        d = model.downsample(enc.transpose(1, 2))
        codes = model.quantizer.encode(d, num_quantizers=8).transpose(0, 1)
        q = model.quantizer
        parts = []
        for rvq, cb in ((q.semantic_residual_vector_quantizer, codes[:, :q.num_semantic_quantizers]),
                        (q.acoustic_residual_vector_quantizer, codes[:, q.num_semantic_quantizers:])):
            pre = rvq.input_proj(d) if rvq.input_proj is not None else d
            post = torch.zeros_like(pre)
            for i, idx in enumerate(cb.transpose(0, 1)):
                post = post + rvq.layers[i].decode(idx)
            parts.append(pre if stage == "pre" else post)
        f = torch.cat(parts, dim=1)          # (1, D, T)
    return f[0].transpose(0, 1).float().cpu().numpy()   # (T, D)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=["mimi"])
    ap.add_argument("--window", default="W2_segment")
    ap.add_argument("--segments", type=int, default=4)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--stage", default="post", choices=["pre", "post"],
                    help="mimi only: quantiser-space latent before or after quantisation")
    args = ap.parse_args()

    import torch
    device = ("cuda" if torch.cuda.is_available()
              else "mps" if torch.backends.mps.is_available() else "cpu")
    rows = load_keepers(args.limit)
    print(f"device={device} | clips={len(rows)} | window={args.window} | "
          f"models={args.models} | segments={args.segments}")

    for model_key in args.models:
        t0 = time.time()
        if model_key == "mimi":
            from transformers import MimiModel
            model = MimiModel.from_pretrained(CKPT["mimi"]).to(device).eval()
            get, sr = (lambda w: frames_mimi(model, w, device, args.stage)), 24000
        elif model_key == "wavlm":
            from transformers import AutoFeatureExtractor, AutoModel
            fe = AutoFeatureExtractor.from_pretrained(CKPT["wavlm"])
            model = AutoModel.from_pretrained(CKPT["wavlm"]).to(device).eval()
            get, sr = (lambda w: frames_wavlm(model, fe, w, device, BEST_LAYER["wavlm"])), 16000
        elif model_key == "whisper":
            from transformers import WhisperFeatureExtractor, WhisperModel
            fe = WhisperFeatureExtractor.from_pretrained(CKPT["whisper"])
            enc = WhisperModel.from_pretrained(CKPT["whisper"]).to(device).eval().get_encoder()
            get, sr = (lambda w: frames_whisper(enc, fe, w, device, BEST_LAYER["whisper"])), 16000
        else:
            print(f"  unknown model {model_key}"); continue

        ids, acc, nframes = [], {}, []
        for i, r in enumerate(rows):
            F = get(read_wav(CLIPS / args.window / (r["candidate_id"] + ".wav"), sr))
            nframes.append(len(F))
            for k, v in readouts(F, args.segments).items():
                acc.setdefault(k, []).append(v)
            ids.append(r["candidate_id"])
            if (i + 1) % 100 == 0:
                print(f"  [{model_key}] {i+1}/{len(rows)}  {time.time()-t0:.0f}s", flush=True)

        for k, X in acc.items():
            X = np.asarray(X, dtype=np.float32)
            suffix = f"_{args.stage}" if model_key == "mimi" and args.stage == "pre" else ""
            p = OUT / f"{model_key}{suffix}_{k}" / f"{args.window}.npz"
            p.parent.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(p, ids=np.array(ids), X=X,
                                meta=np.array([f"readout={k}", f"segments={args.segments}"]))
            print(f"  saved {X.shape} -> {p.relative_to(ROOT)}")
        print(f"  [{model_key}] frames per clip, median {int(np.median(nframes))}, "
              f"done in {time.time()-t0:.0f}s\n")


if __name__ == "__main__":
    main()
