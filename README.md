# Transcript-Equivalent Pragmatic Contrast in Speech Representations

A diagnostic probing study. When the *same* short phrase carries *different* pragmatic
force (`yeah` as sincere agreement against sarcastic `yeah`), do speech representations
preserve the contrast, and where in the pipeline is it lost?

The design's core move is **lexical control**. Holding the word constant and varying only
the delivery separates *loss of meaning* from *loss of sound*, which turns the
uncontroversial fact that tokenisation is lossy into a sharper, deployment-relevant
question about the tokens that speech-to-speech systems actually consume.

---

## Where the study stands

This section is the live state. Read it first. Everything below it is procedure.

### The argument, in one paragraph

Continuous encoders carry pragmatic stance. The deployed codec carries a fraction of it.
The loss sits at the **encoder**, not the quantiser, by roughly three to one, and that
splits the same way on a second codec of independent design. But the codec has not
discarded the prosody. It recovers hand-crafted acoustic cues *better* than WavLM, 153 per
cent on the contour features that stance is built from and 158 per cent on voice quality.
So what is lost is not acoustic detail, it is organisation. Which is consistent with the
only part of Mimi that carries stance being the codebook distilled from a model trained on
a linguistic objective.

**Temporal cues are the single exception**, and they are the reason the timing rebuild
matters. Retention against WavLM runs 106 per cent for Mimi pre-quantisation, 78 per cent
for the deployed histogram, and 63 to 68 per cent for DAC. Every other cue family is
retained at or above 97 per cent. DAC runs at 75 Hz against Mimi's 12.5 and is *worse* on
temporal, so this is not a matter of sampling density.

### Headline numbers

Three-way stance, macro-F1, primary window `W2_segment`, out-of-fold by episode, against
an empirical permutation null of roughly 0.33.

| representation | macro-F1 | margin over null |
|---|---:|---:|
| WavLM-large L20 | 0.569 | +0.237 |
| Whisper-small enc L9 | 0.549 | +0.217 |
| HuBERT-large L23 | 0.491 | +0.157 |
| eGeMAPS, 88 functionals | — | +0.104 |
| Mimi, deployed tokens | 0.381 | +0.070 |
| text, discourse context | 0.378 | +0.045 |

The three neural encoder figures are the **nested** estimates from `src/32`, not the
`argmax` figures still printed by `src/18`. See "corrections in flight" below.

Quantisation ladder, from the matched two-codec run in `src/21`. Mimi loses 0.112 at the
encoder against 0.034 at the quantiser. DAC loses 0.182 at the encoder and *gains* 0.025
at the quantiser. The Mimi-only ladder in `src/19` is a separate run with its own
permutation null and puts the same split at 0.109 against 0.030. Inside Mimi, codebook 0
alone reaches +0.069 against +0.071 for all eight together, and codebook 0 is the one
distilled from WavLM.

Human ceiling on the 60-clip premise subset. Annotators reach 0.730 with audio and
transcript, 0.650 on transcript alone. The best model condition reaches 0.533. Decoding
above chance is not decoding at a useful level.

### What is being rebuilt, and why

Every array in `features/` is **pooled**. Mean and standard deviation over frames, or a
unigram histogram over codes. All of them are permutation-invariant, so shuffling the
frames leaves the input identical.

That is a problem, because pragmatic force lives partly in *change over time*. A rising
`yeah?` and a falling `yeah.` have the same mean by construction. So the measured loss
cannot currently be attributed between the codec and the readout.

The frames were discarded at extraction time and the GPU instance that produced them no
longer exists, so this cannot be recovered by re-analysis. `src/31` re-extracts and keeps
the frame sequence, after which every readout becomes cheap post-processing.

### Corrections in flight

| issue | status |
|---|---|
| `src/18` picks the layer by `argmax` on the same data it reports from, inflating WavLM by 0.003, Whisper by 0.015 and **HuBERT by 0.029** | measured in `src/32`, drafts not yet updated |
| HuBERT's layer is genuinely unstable across folds, picks ranged over L10 to L23 | `src/31` now saves a band rather than one layer |
| every stored feature is order-free, so the timing question is unanswerable against them | `src/31` written and tested, not yet run at full scale |
| this README previously described Mimi as `(n, 14336)` from codebooks 1 to 7 | wrong on both counts, the array is `(873, 16384)` and codebook 0 is the carrier |

### Open questions

- Whether the loss survives a readout that respects time. This is the live experiment.
- Whether variable-frame-rate tokenisers behave differently. Sylber and DyCAST are
  installed and verified to run on this corpus, with no results yet.
- Whether EnCodec, X-Codec and SpeechTokenizer still earn a place once the timing result
  is known. All three are fixed-rate, so they extend the ladder without testing timing.

---

## Representations

| representation | checkpoint | what is measured | rate |
|---|---|---|---|
| WavLM | `microsoft/wavlm-large` | hidden states, per layer | 50 Hz |
| HuBERT | `facebook/hubert-large-ll60k` | hidden states, per layer | 50 Hz |
| Whisper encoder | `openai/whisper-small` | encoder hidden states, valid frames only | 50 Hz |
| Mimi | `kyutai/mimi` | pre-quantisation latent, summed codebook vectors, code indices | 12.5 Hz |
| DAC | `descript/dac_24khz` | encoder output and quantised output | 75 Hz |
| eGeMAPS | openSMILE v02 | 88 functionals, grouped into five cue families | clip-level |
| Text | `sentence-transformers/all-mpnet-base-v2` | target-only and discourse-context embeddings | none |
| Sylber | `cheoljun95/sylber` | per-syllable embeddings plus boundaries | ~4 Hz, variable |
| DyCAST | `lucadellalib/dycast` | pooled latents, pooled codes, tokens, **durations** | 6 to 24 Hz, variable |

Mimi's pre-quantisation and post-quantisation vectors are only comparable in the
quantiser's **projected** space, `input_proj(latent)` against the summed codebook vectors
before `output_proj`. The naive pairing gives a cosine of 0.004 with a 27-fold norm
mismatch. See `src/24`.

Sylber and DyCAST are the only two representations here whose segmentation is derived
from the signal rather than a clock, so token count and boundary placement are data in
their own right. On this corpus Sylber runs at 4.06 syllables per second against the 4.27
it reports on read speech, so it does not degrade on spontaneous material.

---

## What's in this repo, and what isn't

Audio and verbatim transcripts are **not** included. Public podcast audio, used under an
analysis-not-redistribution ethics approval. See
**[DATA_AVAILABILITY.md](DATA_AVAILABILITY.md)**.

Included: all code, the annotation codebook, the label store (`annotations.db`), and a
sanitised labels table (`labels/labels.csv`) with no transcript text.

```
src/                      pipeline scripts 00 to 32, numbered in dependency order
  codebook.json           the annotation scheme
  config.py               machine-specific paths, via env var or gitignored YAML
labels/labels.csv         one row per clip: ids, timing, stance, arousal
annotations.db            persistent label store (SQLite), source of truth
results/                  committed text output of every analysis script
features/                 pooled features, gitignored, regenerate with src/17
features_frames/          frame sequences, gitignored, regenerate with src/31
docs/drafts/              dissertation chapters
DATA_AVAILABILITY.md      what can and cannot be shared, and why
```

`features/` and `features_frames/` are both gitignored. `features_frames/` runs to several
GB and can be relocated to another disk with `PC_FRAMES_DIR` without editing any code.

---

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# audio extraction also needs ffmpeg and ffprobe on PATH
```

Machine-specific paths are not hardcoded.

```bash
cp configs/paths.example.yaml configs/paths.yaml   # gitignored
# or per-run: PC_AUDIO_DIR=... PC_TRANSCRIPTS_DIR=... PC_FRAMES_DIR=...
```

**Record the environment.** The instance that produced the current `features/` is gone and
left no dependency manifest behind, which is why those numbers cannot be regenerated
exactly. Run `pip freeze > requirements-gpu.txt` on any GPU box and commit it.

---

## The corpus you need to supply

Indexed in DuckDB (`corpus.duckdb`) as a `segments` table with word-level timestamps.

| column | meaning |
|---|---|
| `episode_id`, `show_name` | episode and show identifiers |
| `segment_id`, `seg_start`, `seg_end` | segment index and timing |
| `text`, `prev_text`, `next_text` | segment transcript and neighbours |
| `avg_logprob`, `no_speech_prob` | Whisper quality signals, used for filtering |

Per-episode transcript JSONs with `segments[].words[].{word,start,end}` are needed for
word-level centering during clip extraction, for example WhisperX output.

---

## Pipeline

### Phase 0 to 1, corpus to labels

```bash
python3 src/00_health_check.py           # sanity-check corpus.duckdb
python3 src/01_ingest.py                 # build the segments index
python3 src/02_search_candidates.py      # regex-match target phrases
python3 src/03_filter_candidates.py      # ASR-quality and duration filter
python3 src/04_build_annotation_sheet.py # stratified sample
python3 src/05_extract_audio.py          # cut W1/W2/W3 clips, 16 kHz, loudnorm
```

Targeted pulls used to balance thin stance cells, since the bulk random pull
over-samples one sense.

```bash
python3 src/09_build_topup.py            # blocklist sense-filter top-up
python3 src/10_build_oh_topup.py         # "oh X" constructions, pause-isolated
python3 src/11_build_yeahright.py        # the "yeah right" sarcasm collocation
python3 src/12_build_targeted.py --label right --idprefix ohr2 \
    --anchor "right" --pause 0 --target 50 --patterns "\boh,?\s+right\b"
```

`src/12` is the generic engine. `--patterns` for the segment match, `--anchor` for the
word span to centre on, `--pause` to require silence either side, `--shows`, `--target`,
`--label`, `--idprefix`.

### Annotation

Two-tier scheme, see `src/codebook.json`. The annotator picks a fine
**pragmatic-function** tag, which maps to two orthogonal axes, **stance** (affiliative,
neutral, adversarial) and **arousal** (low, high, judged independently), plus a
**confidence** flag. Arousal is kept separate on purpose, because the headline test is
stance separability *at matched arousal*, so a positive result cannot be dismissed as the
model merely encoding loudness.

Labelling uses a self-contained offline HTML tool that works on an iPad with no server.
Audio is inlined, progress autosaves, and the annotator exports JSON.

```bash
python3 src/07_build_offline_annotator.py --sheet data/annotations/<sheet>.csv --prefix annotator
python3 src/13_ingest_annotations.py "path/to/exports/*.json"
```

Ingest is idempotent and newest-wins, keyed by clip id, into `annotations.db`.

### Premise check, the go or no-go gate

A counterbalanced 60-clip subset judged transcript-only against audio, to establish that
the contrast is speech-borne before any modelling.

```bash
python3 src/14_build_premise_check.py
python3 src/15_score_premise.py aux1.json aux2.json
python3 src/29_premise_ceiling.py          # models against humans on the same 60 clips
```

The hidden reference `data/annotations/premise_key.csv` stays local. Transcript with
context reaches roughly 0.65, audio with transcript roughly 0.73, three-way chance
roughly 0.33.

### Phase 2, features

```bash
python3 src/17_extract_features.py       # pooled, per layer, all windows
python3 src/27_egemaps.py                # 88 functionals plus cue groups
python3 src/31_extract_frames.py --models all   # frame sequences, the rebuild
```

`src/31` is the current one. It keeps the frame sequence instead of pooling at extraction
time, saves a band of layers rather than one, stores float16 with a `lengths` vector so no
readout ever pools over padding, and checkpoints every 100 clips so a crash on a rented
box resumes rather than restarts.

```bash
python3 src/31_extract_frames.py --models dycast --limit 8   # smoke test first
python3 src/31_extract_frames.py --models all                # roughly 6 GB out
```

### Phase 3, probing and analysis

All evaluation is out-of-fold under **GroupKFold by episode**, so no episode's clips ever
span train and test. Scores carry a 95 per cent CI from an **episode-cluster bootstrap**,
resampling whole episodes rather than clips, and headline configs carry a **permutation
p-value**.

```bash
python3 src/18_probe.py                  # the main battery, six views
python3 src/32_layer_selection.py        # is the layer choice honest and stable
```

| script | question |
|---|---|
| `18_probe.py` | pooled decodability, context window, within-word, matched arousal, speaker control, layer curve, codebooks |
| `19_mimi_quantisation_ladder.py` | encoder against quantiser, Mimi |
| `20_order_aware_features.py` | meanstd against seg4 against delta |
| `21_dac_ladder.py` | the same split on a second codec |
| `22_nonlinear_probe.py` | does probe capacity change the ordering |
| `23_cps_baseline.py` | the two defensible baselines for the contrast-preservation score |
| `24_projection_cosines.py` | which pre and post pairing is actually comparable |
| `25_family_analysis.py` | phrase-family effects, negative result |
| `26_within_word_readout.py` | Mimi under three readouts |
| `28_codebook_ladder.py` | cumulative codebooks, is codebook 0 doing the work |
| `30_cue_retention.py` | which acoustic cues does the codec actually lose |
| `32_layer_selection.py` | nested layer selection against argmax |

Every script writes a text file into `results/`, which is committed. Those files are the
record of what was actually run.

---

## Dataset

Roughly 873 labelled clips across 8 target phrases (`yeah`, `okay`, `right`, `sure`,
`great`, `fine`, `really`, `come_on`), 753 distinct episodes, 32 shows. Overall stance is
balanced. Neutral concentrates in the agreement particles, which is a property of those
words rather than a sampling gap. All `W2_segment` clips are exactly 10 seconds, so token
count under a variable-rate model reflects delivery and not duration.

---

## License

Code: MIT, see `LICENSE`. Data and labels: analysis use per `DATA_AVAILABILITY.md`.
