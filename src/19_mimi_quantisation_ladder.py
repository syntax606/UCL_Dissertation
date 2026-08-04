#!/usr/bin/env python3
"""
Isolate what QUANTISATION alone costs, holding everything else fixed.

The pooled Mimi figure in src/17 summarises the code stream as per-codebook
unigram histograms. That is a sparse, order-free tally (about 125 tokens spread
over 2048 bins), whereas WavLM is summarised as mean+std over ~500 dense frames.
So "WavLM vs Mimi" confounds quantisation with feature construction, frame rate,
training objective and architecture. This script removes every one of those.

Mimi's residual quantiser works in a PROJECTED space. MimiResidualVectorQuantizer
.encode applies `input_proj` and then quantises the result; .decode sums the
codebook vectors and only then applies `output_proj`. The two projections map to
different spaces, so the encoder latent and `quantizer.decode(...)` are NOT
comparable (empirically cosine ~0.008, norms 1.5 against 62). The comparable pair
is:

    PRE  = input_proj(encoder latent)          continuous, pre-quantisation
    POST = sum of selected codebook vectors    the same vector, quantised

Both are pooled mean+std exactly as WavLM is, so the ONLY difference between them
is quantisation. That gives the three-point ladder:

    WavLM            teacher, continuous            features/wavlm/
    mimi_pre         distilled, still continuous    features/mimi_pre/
    mimi_post        the same, quantised            features/mimi_post/

WavLM -> mimi_pre measures what distillation and the codec encoder cost.
mimi_pre -> mimi_post measures what quantisation costs, which is the number the
deployment argument actually needs.

Semantic (codebook 0, WavLM-distilled) and acoustic (codebooks 1..7) have separate
projections, so each is handled in its own space and the two are concatenated.
`--semantic-only` restricts to codebook 0 for the cleanest teacher-to-student
comparison against WavLM.

CPU is fine, roughly 10 to 15 minutes for 873 clips at W2.

Usage:
  python3 src/19_mimi_quantisation_ladder.py --limit 5     # smoke test
  python3 src/19_mimi_quantisation_ladder.py
"""
import argparse, csv, time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SHEET = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
CLIPS = ROOT / "data" / "clips"
OUT = ROOT / "features"
CLASSES = ("affiliative", "neutral", "adversarial")
CKPT = "kyutai/mimi"
N_CODEBOOKS = 8


def load_keepers(limit=None):
    rows = [r for r in csv.DictReader(open(SHEET, newline=""))
            if r.get("stance", "").strip() in CLASSES]
    return rows[:limit] if limit else rows


def read_wav(path, target_sr=24000):
    import soundfile as sf, librosa
    wav, sr = sf.read(path, dtype="float32")
    if wav.ndim > 1:
        wav = wav.mean(axis=1)
    if sr != target_sr:
        wav = librosa.resample(wav, orig_sr=sr, target_sr=target_sr)
    return wav


def pool(x):
    """x: (1, D, T) -> (2D,) mean and std over time, matching src/17's pooling."""
    import torch
    v = x[0].transpose(0, 1)                      # (T, D)
    return torch.cat([v.mean(0), v.std(0)]).float().cpu().numpy()


def latents(model, x):
    """Return (pre, post) in the quantiser's projected space, both (1, D, T)."""
    import torch
    enc = model.encoder(x)
    enc = model.encoder_transformer(enc.transpose(1, 2)).last_hidden_state
    d = model.downsample(enc.transpose(1, 2))                 # encoder latent
    codes = model.quantizer.encode(d, num_quantizers=N_CODEBOOKS).transpose(0, 1)

    q = model.quantizer
    n_sem = q.num_semantic_quantizers
    out = {}
    for name, rvq, cb in (("sem", q.semantic_residual_vector_quantizer, codes[:, :n_sem]),
                          ("aco", q.acoustic_residual_vector_quantizer, codes[:, n_sem:])):
        pre = rvq.input_proj(d) if rvq.input_proj is not None else d
        post = torch.zeros_like(pre)
        for i, idx in enumerate(cb.transpose(0, 1)):          # (K, B, T)
            post = post + rvq.layers[i].decode(idx)           # BEFORE output_proj
        out[name] = (pre, post)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", default="W2_segment")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--semantic-only", action="store_true")
    args = ap.parse_args()

    import torch
    from transformers import MimiModel
    device = ("cuda" if torch.cuda.is_available()
              else "mps" if torch.backends.mps.is_available() else "cpu")
    model = MimiModel.from_pretrained(CKPT).to(device).eval()
    rows = load_keepers(args.limit)
    print(f"device={device} | clips={len(rows)} | window={args.window} | "
          f"{'semantic only' if args.semantic_only else 'semantic + acoustic'}")

    ids, PRE, POST, diag = [], [], [], []
    t0 = time.time()
    for i, r in enumerate(rows):
        wav = read_wav(CLIPS / args.window / (r["candidate_id"] + ".wav"))
        x = torch.tensor(wav)[None, None].to(device)
        with torch.no_grad():
            L = latents(model, x)
        parts = [L["sem"]] if args.semantic_only else [L["sem"], L["aco"]]
        PRE.append(np.concatenate([pool(p) for p, _ in parts]))
        POST.append(np.concatenate([pool(q) for _, q in parts]))
        # sanity: quantisation should approximately preserve the vector
        p, q = L["sem"]
        diag.append(float(torch.nn.functional.cosine_similarity(p, q, dim=1).mean()))
        ids.append(r["candidate_id"])
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(rows)}  {time.time()-t0:.0f}s  "
                  f"cos(pre,post) running mean {np.mean(diag):.3f}")

    tag = "_sem" if args.semantic_only else ""
    for name, X in (("mimi_pre" + tag, PRE), ("mimi_post" + tag, POST)):
        X = np.asarray(X, dtype=np.float32)
        p = OUT / name / f"{args.window}.npz"
        p.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(p, ids=np.array(ids), X=X,
                            meta=np.array([f"codebooks={N_CODEBOOKS}",
                                           "space=quantiser projected",
                                           "pooling=mean+std"]))
        print(f"  saved {X.shape} -> {p.relative_to(ROOT)}")
    print(f"\nsemantic cos(pre, post) mean {np.mean(diag):.3f}  min {np.min(diag):.3f}")
    print("A high cosine confirms pre and post live in the same space, so the probe")
    print("difference between them is attributable to quantisation.")
    print(f"done in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
