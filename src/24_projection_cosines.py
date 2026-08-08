#!/usr/bin/env python3
"""
Capture the projection-space diagnostics the ladder argument depends on.

src/19 and src/21 compute these and print them, but never write them anywhere, so
the figures quoted in [3.5] and [4.6] had no committed artefact. This script
recomputes them on their own and writes results/projection_cosines.txt.

What is being checked. A residual quantiser does not operate on the encoder latent
directly. It applies an input projection, quantises in that projected space, sums the
selected codebook vectors, and only then applies an output projection. The input and
output projections do not map to a common space, so the obvious comparison, encoder
latent against the quantiser's reconstructed output, compares vectors that are not
commensurate and would make the measured "cost of quantisation" meaningless.

Three numbers are reported per codec:

  naive     cos(encoder latent, quantizer.decode(codes))    NOT comparable, near zero
  correct   cos(input_proj(latent), sum of codebook vectors) the ladder's actual pair
  norms     mean L2 of each side of the naive pair, which shows the scale mismatch

A high `correct` cosine is what licenses treating PRE and POST as the same vector
before and after rounding, which is the whole basis of the quantisation estimate.

Usage:  python3 src/24_projection_cosines.py [--n 100]
"""
import argparse, csv
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parent.parent
SHEET = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
CLIPS = ROOT / "data" / "clips" / "W2_segment"
OUT = ROOT / "results" / "projection_cosines.txt"
CLASSES = ("affiliative", "neutral", "adversarial")
N_CODEBOOKS = 8


def read_wav(path, target_sr):
    import soundfile as sf, librosa
    wav, sr = sf.read(path, dtype="float32")
    if wav.ndim > 1:
        wav = wav.mean(axis=1)
    if sr != target_sr:
        wav = librosa.resample(wav, orig_sr=sr, target_sr=target_sr)
    return wav


def cos(a, b):
    return float(torch.nn.functional.cosine_similarity(a, b, dim=1).mean())


def mimi_pair(model, wav, device):
    x = torch.tensor(wav)[None, None].to(device)
    with torch.no_grad():
        enc = model.encoder(x)
        enc = model.encoder_transformer(enc.transpose(1, 2)).last_hidden_state
        d = model.downsample(enc.transpose(1, 2))
        codes = model.quantizer.encode(d, num_quantizers=N_CODEBOOKS).transpose(0, 1)
        q = model.quantizer
        n_sem = q.num_semantic_quantizers
        pres, posts = [], []
        for rvq, cb in ((q.semantic_residual_vector_quantizer, codes[:, :n_sem]),
                        (q.acoustic_residual_vector_quantizer, codes[:, n_sem:])):
            pre = rvq.input_proj(d) if rvq.input_proj is not None else d
            post = torch.zeros_like(pre)
            for i, idx in enumerate(cb.transpose(0, 1)):
                post = post + rvq.layers[i].decode(idx)
            pres.append(pre); posts.append(post)
        pre_c, post_c = torch.cat(pres, 1), torch.cat(posts, 1)
        naive = model.quantizer.decode(codes.transpose(0, 1))
    return (cos(pre_c, post_c), cos(d, naive),
            float(d.norm(dim=1).mean()), float(naive.norm(dim=1).mean()))


def dac_pair(model, wav, device):
    x = torch.tensor(wav)[None, None].to(device)
    with torch.no_grad():
        e = model.encoder(x)
        out = model.quantizer(e, n_quantizers=N_CODEBOOKS)
        q = out[0] if isinstance(out, (tuple, list)) else out.quantized_representation
    return cos(e, q), float(e.norm(dim=1).mean()), float(q.norm(dim=1).mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100, help="clips to average over")
    args = ap.parse_args()

    rows = [r for r in csv.DictReader(open(SHEET, newline=""))
            if r.get("stance", "").strip() in CLASSES][:args.n]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    lines = []

    def emit(s=""):
        print(s, flush=True)
        lines.append(s)

    emit("PROJECTION-SPACE DIAGNOSTICS for the quantisation ladder")
    emit("The residual quantiser works in a projected space. The encoder latent and the")
    emit("quantiser's reconstructed output are therefore NOT commensurate. The ladder")
    emit("compares input_proj(latent) against the summed codebook vectors, before the")
    emit("output projection. These numbers are what licenses that choice.")
    emit(f"clips averaged: {len(rows)}   codebooks: {N_CODEBOOKS}   device: {device}")
    emit("=" * 78)

    from transformers import MimiModel
    m = MimiModel.from_pretrained("kyutai/mimi").to(device).eval()
    c_ok, c_naive, n_lat, n_dec = [], [], [], []
    for r in rows:
        w = read_wav(CLIPS / (r["candidate_id"] + ".wav"), 24000)
        a, b, c, d = mimi_pair(m, w, device)
        c_ok.append(a); c_naive.append(b); n_lat.append(c); n_dec.append(d)
    emit(f"Mimi  correct pair  cos = {np.mean(c_ok):.3f}   min {np.min(c_ok):.3f}")
    emit(f"Mimi  naive pair    cos = {np.mean(c_naive):.3f}   "
         f"norms {np.mean(n_lat):.1f} against {np.mean(n_dec):.1f}")
    del m

    from transformers import DacModel
    d_model = DacModel.from_pretrained("descript/dac_24khz").to(device).eval()
    d_ok = []
    for r in rows:
        w = read_wav(CLIPS / (r["candidate_id"] + ".wav"), 24000)
        d_ok.append(dac_pair(d_model, w, device)[0])
    emit(f"DAC   correct pair  cos = {np.mean(d_ok):.3f}   min {np.min(d_ok):.3f}")

    emit()
    emit("Read: the correct pairs share a space, so PRE and POST differ only by rounding.")
    emit("The naive Mimi pair does not, which is why it is never used.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
