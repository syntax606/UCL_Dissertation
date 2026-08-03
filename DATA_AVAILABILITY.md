# Data availability and ethics

## What this repository does and does not contain

This project analyses short excerpts of **public political podcast audio**. Consistent
with the project's ethics approval, the corpus is used for computational analysis, not
redistribution. Therefore:

**Not included (by design):**
- Raw or clipped **audio** (the ~5,000 extracted WAV clips).
- **Verbatim transcripts** (`segment_text` and surrounding context), which are
  copyrighted speech. The candidate CSVs and the full annotation sheet, which contain
  this text, are git-ignored.
- The 7.9 GB `corpus.duckdb` index.

**Included:**
- All pipeline **code** (`src/`) and the annotation **codebook** (`src/codebook.json`).
- The **label store** (`annotations.db`) and a sanitized **labels table**
  (`labels/labels.csv`): one row per clip with `candidate_id`, `target_phrase`,
  `show_name`, `episode_id`, timing, and the analysis labels (`stance`, `arousal`,
  `literal`, `confidence`). No transcript text.
**Shareable, but not currently in the repository:**
- **Derived features** (pooled embeddings) under `features/`. Because features are derived
  rather than audio, they *can* be shared without an ethics problem — but they are not
  committed here: the WavLM/HuBERT matrices are ~156 MB per window, above GitHub's 100 MB
  file limit, and `features/` is listed in `.gitignore`. Distributing them requires git-lfs
  or a release attachment. Until that is done, the probing results cannot be reproduced from
  this repository alone.

## Reproducing the results

- **Probing results only:** requires `features/`, which is **not currently shipped** (see
  above). With a copy of `features/` in place no audio is needed: copy the shipped
  `labels/labels.csv` to `manifest.csv` at the repository root, then run `src/18_probe.py`.
  `labels.csv` carries every column the probe needs (`candidate_id`, `stance`, `arousal`,
  `target_phrase`, `episode_id`, `show_name`); the copy is necessary because `src/18` looks
  for `manifest.csv` and otherwise falls back to the git-ignored labeled annotation sheet.
- **Re-extracting features:** requires the clips, and therefore the audio. Note additionally
  that the *text* baseline in `src/17` reads `prev_text` / `segment_text` / `next_text`, which
  are verbatim transcript and are excluded from `labels.csv` for the copyright reasons above,
  so the text features cannot be regenerated from the shipped labels alone.
- **Per-phrase cells:** reproducing the published per-phrase results (view C) also requires
  re-applying the phrase fold described under "Dataset summary" in the README, which no
  script in this repository performs.
- **Full pipeline from audio:** point the pipeline at **your own** audio + word-level
  transcripts (see the corpus schema in the README), then run `src/02` onward. The
  labels here are keyed by `candidate_id`, which encodes `episode_id` + segment; they
  will only line up with the identical source episodes.

## Labels refer to pragmatic function, not inner states

Annotations describe the **pragmatic force in context** (affiliative / neutral /
adversarial stance; low / high arousal), not claims about a speaker's private mental
state. No speaker identification beyond available metadata is performed.
