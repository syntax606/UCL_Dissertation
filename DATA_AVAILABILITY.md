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
- The returned **premise-check annotator packages**, which embed clip audio alongside the
  hidden reference labels. Figures scored from them, including the per-phrase human
  accuracies, therefore cannot be regenerated from this repository. The dissertation
  marks each one at the point of use.

**Included:**
- All pipeline **code** (`src/`) and the annotation **codebook** (`src/codebook.json`).
- The **label store** (`annotations.db`) and a sanitized **labels table**
  (`labels/labels.csv`): one row per clip with `candidate_id`, `target_phrase`,
  `show_name`, `episode_id`, timing, and the analysis labels (`stance`, `arousal`,
  `literal`, `confidence`). No transcript text.
- The **saved output** of every analysis the dissertation reports (`results/`), with
  `reference/PROVENANCE.md` naming the script that produced each file.

**Included, but attached to the release rather than tracked in git:**
- **Derived features**, 2.1 GB across two archives, listed with per-file sizes in
  `reference/FEATURE_MANIFEST.json`. They are pooled embeddings (`features.tar.gz`) and
  frame sequences (`features_frames.tar.gz`), derived rather than raw, so they carry no
  redistributable speech and let anyone reproduce the probing results without the audio.
  They are too large to track in git, which is why they are release assets and not
  repository contents.

## Reproducing the results

- **Verify the reported numbers:** every figure in the dissertation appears in a file
  under `results/`. Needs nothing else.
- **Re-run the probing analysis:** download both feature archives from the release,
  unpack them beside `src/`, and use them with `labels/labels.csv`. No audio needed.
  `reference/REPRODUCE.md` says which archive each analysis reads.
- **Full pipeline from audio:** point the pipeline at **your own** audio + word-level
  transcripts (see the corpus schema in the README), then run `src/02` onward. The
  labels here are keyed by `candidate_id`, which encodes `episode_id` + segment; they
  will only line up with the identical source episodes.

## Labels refer to pragmatic function, not inner states

Annotations describe the **pragmatic force in context** (affiliative / neutral /
adversarial stance; low / high arousal), not claims about a speaker's private mental
state. No speaker identification beyond available metadata is performed.
