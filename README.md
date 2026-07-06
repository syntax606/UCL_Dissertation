# Transcript-Equivalent Pragmatic Contrast in Speech Representations

A diagnostic probing study: when the *same* short phrase carries *different* pragmatic
force ("yeah" as sincere agreement vs. sarcastic "yeah"), do modern speech
representations preserve the contrast, and does it survive discrete tokenization?

The design's core move is **lexical control**: by holding the word constant and varying
only the delivery, it separates *loss of meaning* from *loss of sound*, which turns the
uncontroversial fact that tokenization is lossy into the sharper, deployment-relevant
claim that the tokens real speech-to-speech systems consume can collapse
transcript-equivalent but meaning-different utterances.

Representations compared: **WavLM**, **HuBERT**, **Whisper encoder**, **Mimi** (the
discrete tokenizer used by deployed S2S systems), and a **transcript-only** text
baseline.

---

## Project status

| Phase | State |
|---|---|
| 0. Corpus indexing | done |
| 1. Candidate search → clip extraction → **annotation** (label store) | **done** (~873 labelled clips) |
| 2. Feature extraction (WavLM / HuBERT / Whisper / Mimi / text) | in progress |
| 3. Probing + analysis (stance decodability, CPS, layer-wise, context-window) | planned |

This README fully documents Phases 0–1, which are complete and reproducible. The
Phase 2–3 scripts are being added; sections marked *(forthcoming)* will be filled in as
they land.

---

## What's in this repo (and what isn't)

Audio and verbatim transcripts are **not** included (public podcast audio, used under an
analysis-not-redistribution ethics approval). See **[DATA_AVAILABILITY.md](DATA_AVAILABILITY.md)**.
Included: all code, the annotation codebook, the label store (`annotations.db`), a
sanitized labels table (`labels/labels.csv`), and derived features under `features/`
once extracted.

```
src/                     pipeline scripts (00–13), run in order
  codebook.json          the annotation scheme (functions -> stance, arousal, etc.)
labels/labels.csv        one row per clip: ids, timing, stance, arousal (no transcript text)
annotations.db           persistent label store (SQLite); source of truth for labels
features/                pooled embeddings per clip (added in Phase 2)
DATA_AVAILABILITY.md      what can/can't be shared and why
requirements.txt
```

---

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Audio extraction also needs ffmpeg + ffprobe on PATH:
#   macOS: brew install ffmpeg
```

**Configuration.** Machine-specific paths are not hardcoded. Point the pipeline at your
audio and transcripts by copying the template and editing it:

```bash
cp configs/paths.example.yaml configs/paths.yaml   # git-ignored; set audio_dir + transcripts_dir
# or override per-run with env vars: PC_AUDIO_DIR=... PC_TRANSCRIPTS_DIR=...
```

`src/config.py` reads these; everything else derives from the repo location.

---

## The corpus you need to supply

Because the audio can't be shared, the pipeline assumes you point it at your own corpus,
indexed in DuckDB (`corpus.duckdb`) as a `segments` table with word-level timestamps:

| column | meaning |
|---|---|
| `episode_id`, `show_name` | episode + show identifiers |
| `segment_id`, `seg_start`, `seg_end` | segment index and timing |
| `text`, `prev_text`, `next_text` | segment transcript + neighbours |
| `avg_logprob`, `no_speech_prob` | Whisper quality signals (used for filtering) |

Per-episode transcript JSONs (with `segments[].words[].{word,start,end}`) are needed for
word-level centering during clip extraction (e.g. WhisperX output).

---

## Pipeline (Phases 0–1)

Run from the project root.

```bash
python3 src/00_health_check.py          # sanity-check corpus.duckdb
python3 src/01_ingest.py                # build the segments index
python3 src/02_search_candidates.py     # regex-match target phrases -> candidate_targets.csv
python3 src/03_filter_candidates.py     # ASR-quality + duration filter -> *_filtered.csv
python3 src/04_build_annotation_sheet.py# stratified sample -> data/annotations/annotation_sheet.csv
python3 src/05_extract_audio.py         # cut W1/W2/W3 clips (±3/5/8s) centered on the target word, 16 kHz, loudnorm
```

### Targeted candidate pulls (used to balance thin stance cells)
The bulk random pull over-samples one sense/stance, so specific cells were topped up with
sense- and construction-targeted pulls:

```bash
python3 src/09_build_topup.py                     # blocklist sense-filter top-up
python3 src/10_build_oh_topup.py                  # "oh X" constructions, pause-isolated
python3 src/11_build_yeahright.py                 # the "yeah right" sarcasm collocation
python3 src/12_build_targeted.py --label right --idprefix ohr2 \
    --anchor "right" --pause 0 --target 50 --patterns "\boh,?\s+right\b"   # generic pattern pull
```
`src/12` is the generic engine: `--patterns` (segment must match), `--anchor` (word span
to center the clip on), `--pause` (require silence before/after for standalone tokens),
`--shows` (restrict to given shows), `--target`, `--label`, `--idprefix`.

### Annotation

The annotation scheme is two-tier (see `src/codebook.json`): the annotator picks a fine
**pragmatic-function** tag, which maps to two orthogonal analysis axes, **stance**
(affiliative / neutral / adversarial) and **arousal** (low / high, judged independently),
plus a **confidence** flag. Arousal is kept separate on purpose: the headline test is
stance separability *at matched arousal*, so a positive result can't be dismissed as the
model merely encoding loudness.

Labelling uses a **fully self-contained offline HTML tool** (works on an iPad with no
server): audio is inlined, progress autosaves to local storage, and you export JSON.

```bash
python3 src/07_build_offline_annotator.py --sheet data/annotations/<sheet>.csv --prefix annotator
#   open the generated offline_annotator/annotator_*.html, label, tap Export
```

### Label store (source of truth)

Exports are ingested into a persistent SQLite store, keyed by clip id, newest-wins,
idempotent. This is authoritative: it survives regardless of which folder the JSON
exports live in.

```bash
python3 src/13_ingest_annotations.py "path/to/exports/*.json"
#   -> updates annotations.db and re-derives data/annotations/annotation_sheet_labeled.csv
```

---

## Dataset summary

~873 labelled clips across 8 target phrases (yeah, okay, right, sure, great, fine, really,
come_on), 753 distinct episodes, 32 shows. Each phrase carries a well-powered binary
stance contrast with arousal represented on both sides. Overall stance is balanced
(affiliative ≈ neutral-plus ≈ adversarial); neutral is concentrated in the agreement
particles, which is a linguistic property of the words, not a sampling gap.

The premise check (a counterbalanced subset judged transcript-only vs. audio) validates
that the contrast is speech-borne before any modelling; it is the go/no-go gate for
Phase 2.

---

## Feature extraction (Phase 2, forthcoming)

Per clip, per representation, per context window: continuous hidden states
(WavLM/HuBERT/Whisper, mean+std pooled, saved per layer), Mimi discrete tokens
(codebook-level), and text-embedding baselines (target-only + discourse-context).
Scripts and shipped `features/` to follow.

## Probing and analysis (Phase 3, planned)

Logistic-regression probes with GroupKFold by episode; a training-free
contrast-preservation score with a speaker-identity control; layer-wise and
context-window analyses; episode-level (cluster) bootstrap CIs and permutation tests.
See the analysis plan in the dissertation write-up.

---

## License

Code: MIT (see `LICENSE`). Data/labels: analysis use per `DATA_AVAILABILITY.md`.
