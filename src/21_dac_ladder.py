#!/usr/bin/env python3
"""
Add a purely acoustic codec to the discrete arm, so it is a trend not a point.

The field's taxonomy splits codecs into acoustic, semantic and hybrid. Mimi is
hybrid, reconstruction plus WavLM distillation. DAC is purely acoustic, trained
for reconstruction with no semantic objective at all. Comparing them tests whether
the semantic distillation objective is what discards pragmatic stance, which is
the mechanism the decomposition in src/19 implicates.

Both are extracted the same way. Pre-quantisation is the encoder output, post is
the summed quantised reconstruction, both pooled mean+std exactly as WavLM is, and
both restricted to 8 codebooks so the comparison is at matched depth.

Caveats to state in the write-up. DAC 24 kHz runs at 75 Hz against Mimi's 12.5 Hz,
and their codebooks differ (1024 entries of dim 8 against 2048). Frame rate and
codebook geometry are therefore confounded with the semantic objective. The
comparison is informative about the deployed configurations, not a clean ablation
of distillation alone.

Literature predictions to test against. CodecBench reports Mimi 0.621 against DAC
0.413 on emotion, and Sun et al. (2026) put DAC lowest of all codecs at 0.1187.
Both predict DAC below Mimi despite DAC preserving more acoustic detail.

Usage:
  python3 src/21_dac_ladder.py --limit 5
  python3 src/21_dac_ladder.py
"""
import argparse, csv, time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SHEET = ROOT / "data" / "annotations" / "annotation_sheet_labeled.csv"
CLIPS = ROOT / "data" / "clips"
OUT = ROOT / "features"
CLASSES = ("affiliative", "neutral", "adversarial")
CKPT = "descript/dac_24khz"
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
    """x: (1, D, T) -> (2D,) mean and std over time, matching src/17 and src/19."""
    import torch
    v = x[0].transpose(0, 1)
    return torch.cat([v.mean(0), v.std(0)]).float().cpu().numpy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", default="W2_segment")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    import torch
    from transformers import DacModel
    device = ("cuda" if torch.cuda.is_available()
              else "mps" if torch.backends.mps.is_available() else "cpu")
    model = DacModel.from_pretrained(CKPT).to(device).eval()
    rows = load_keepers(args.limit)
    print(f"device={device} | clips={len(rows)} | window={args.window} | "
          f"codebooks={N_CODEBOOKS} of {len(model.quantizer.quantizers)}")

    ids, PRE, POST, cos, nframes = [], [], [], [], []
    t0 = time.time()
    for i, r in enumerate(rows):
        wav = read_wav(CLIPS / args.window / (r["candidate_id"] + ".wav"))
        x = torch.tensor(wav)[None, None].to(device)
        with torch.no_grad():
            e = model.encoder(x)
            q = model.quantizer(e, n_quantizers=N_CODEBOOKS)[0]
        PRE.append(pool(e)); POST.append(pool(q))
        cos.append(float(torch.nn.functional.cosine_similarity(e, q, dim=1).mean()))
        nframes.append(e.shape[-1]); ids.append(r["candidate_id"])
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(rows)}  {time.time()-t0:.0f}s", flush=True)

    for name, X in (("dac_pre", PRE), ("dac_post", POST)):
        X = np.asarray(X, dtype=np.float32)
        p = OUT / name / f"{args.window}.npz"
        p.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(p, ids=np.array(ids), X=X,
                            meta=np.array([f"codebooks={N_CODEBOOKS}", "pooling=mean+std",
                                           "space=encoder output"]))
        print(f"  saved {X.shape} -> {p.relative_to(ROOT)}")
    print(f"\nframes per clip, median {int(np.median(nframes))} at 75 Hz")
    print(f"cos(pre, post) mean {np.mean(cos):.3f}   min {np.min(cos):.3f}")
    print(f"done in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
