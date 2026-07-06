"""Central paths. Real values live in configs/paths.yaml (git-ignored) or env vars,
so no machine-specific path is committed. Stdlib only (no pyyaml dependency)."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_yaml_flat(path):
    d = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.split("#", 1)[0].rstrip()
            if ":" in line:
                k, v = line.split(":", 1)
                d[k.strip()] = v.strip()
    return d


_cfg = _load_yaml_flat(PROJECT_ROOT / "configs" / "paths.yaml")

# Source audio + word-level transcripts (supply your own; see configs/paths.example.yaml)
AUDIO_DIR = Path(os.environ.get("PC_AUDIO_DIR", _cfg.get("audio_dir", "/path/to/podcast-audio")))
TRANSCRIPTS_DIR = Path(os.environ.get("PC_TRANSCRIPTS_DIR", _cfg.get("transcripts_dir", "/path/to/podcast-transcripts")))
