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
- **Derived features** (pooled embeddings), added under `features/` once extracted.
  Because features are derived, not audio, they can be shared and let anyone reproduce
  the probing results exactly without the audio.

## Reproducing the results

- **Probing results only:** use the shipped `features/` + `labels/labels.csv`. No audio
  needed.
- **Full pipeline from audio:** point the pipeline at **your own** audio + word-level
  transcripts (see the corpus schema in the README), then run `src/02` onward. The
  labels here are keyed by `candidate_id`, which encodes `episode_id` + segment; they
  will only line up with the identical source episodes.

## Labels refer to pragmatic function, not inner states

Annotations describe the **pragmatic force in context** (affiliative / neutral /
adversarial stance; low / high arousal), not claims about a speaker's private mental
state. No speaker identification beyond available metadata is performed.
