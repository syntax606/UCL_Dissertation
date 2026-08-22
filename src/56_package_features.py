#!/usr/bin/env python3
"""Package the derived features as release assets, with a manifest a grader can verify.

The features are what makes the probing analysis re-runnable without audio. They are
pooled embeddings and frame sequences rather than recordings, so they carry no
redistributable speech, which is what allows them to be published at all.

Both directories ship whole, and the reason is worth recording. features/ stores WavLM
and HuBERT as (873, 25, 2048) and Whisper as (873, 13, 1536), all layers, and the
analysis selects a layer by indexing that axis. Slicing to the three layers the paper
reports would cut 1.17 GB to 59 MB, but every script would then need its indexing
changed, and editing the code a grader is meant to re-run in order to make it fit is a
bad trade. The layer sweep in src/32 needs the full stacks in any case.

Two assets rather than one, split where the analyses split.

  features.tar.gz         pooled embeddings, the ladder and everything read from it
  features_frames.tar.gz  frame sequences, which is where EnCodec, Sylber and DyCAST
                          live, and what the timing and cue-retention work reads

Neither exceeds the 2 GB per-asset limit on a GitHub release, which is why they are not
combined.

Writing the archives needs roughly as much free space again as the sources occupy, so
the default run computes the manifest and writes nothing. Pass --write to build them.

Usage:  python3 src/56_package_features.py
        python3 src/56_package_features.py --write DIR
"""
import argparse
import hashlib
import json
import shutil
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "reference"

ASSETS = {
    "features": ("features.tar.gz",
                 "Pooled embeddings, one row per clip. WavLM, HuBERT and Whisper carry "
                 "every layer, so this also serves the layer sweep in src/32."),
    "features_frames": ("features_frames.tar.gz",
                        "Frame sequences, variable length. EnCodec, Sylber and DyCAST are "
                        "here rather than in features/, and so is everything the timing "
                        "and cue-retention analyses read."),
}

HEADROOM_GB = 1.0


def sha(p, buf=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(buf):
            h.update(chunk)
    return h.hexdigest()


def survey(d):
    files = sorted(p for p in d.rglob("*") if p.is_file() and not p.name.startswith("."))
    return files, sum(p.stat().st_size for p in files)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", metavar="DIR", help="build the archives into DIR")
    args = ap.parse_args()

    print(f"Feature assets\n{'-' * 78}")
    manifest, total = {}, 0
    for name, (arc, why) in ASSETS.items():
        d = ROOT / name
        if not d.exists():
            print(f"  FAIL  {name}/ is not here, nothing to package")
            return 1
        files, size = survey(d)
        total += size
        manifest[arc] = {
            "source": f"{name}/",
            "what": why,
            "files": len(files),
            "bytes": size,
            "contents": {str(p.relative_to(d)): {"bytes": p.stat().st_size} for p in files},
        }
        print(f"  {name:16} {len(files):4} files   {size / 1e9:5.2f} GB   -> {arc}")

    free = shutil.disk_usage(ROOT).free
    print(f"{'-' * 78}")
    print(f"  sources {total / 1e9:.2f} GB, free {free / 1e9:.2f} GB")

    if not args.write:
        (REF / "FEATURE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"  ok    wrote reference/FEATURE_MANIFEST.json, no archives built")
        print(f"  note  pass --write DIR to build them, which needs about "
              f"{total / 1e9:.1f} GB free")
        return 0

    if free - total < HEADROOM_GB * 1e9:
        print(f"  FAIL  building would leave under {HEADROOM_GB:.0f} GB free, refusing")
        print(f"        free space first, or pass a --write path on another volume")
        return 1

    dest = Path(args.write).expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)
    for name, (arc, _) in ASSETS.items():
        out = dest / arc
        with tarfile.open(out, "w:gz") as tf:
            tf.add(ROOT / name, arcname=name)
        digest = sha(out)
        manifest[arc]["archive_bytes"] = out.stat().st_size
        manifest[arc]["archive_sha256"] = digest
        print(f"  ok    {arc:26} {out.stat().st_size / 1e9:5.2f} GB   {digest[:16]}")

    (REF / "FEATURE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"{'-' * 78}\n  attach both to the release, and keep the manifest in the repo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
