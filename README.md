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

**Temporal cues are the single exception.** Retention against WavLM runs 106 per cent for
Mimi pre-quantisation, 78 per cent for the deployed histogram, and 63 to 68 per cent for
DAC. Every other cue family is retained at or above 97 per cent. DAC runs at 75 Hz against
Mimi's 12.5 and is *worse* on temporal, so this is not a matter of sampling density.

Probing frame sequences directly rather than pooled summaries gives that a second,
independent line of support. How much the probe gains from frame **order**, measured
against a shuffled control at matched dimensionality, declines monotonically along the same
ladder: +0.113 for WavLM, +0.080 for Mimi before quantisation, +0.048 after, and nothing
at all for DAC. So the organisation that is lost is at least partly temporal, and it is
lost progressively rather than at any single step.

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
`argmax` figures still printed by `src/18`. All six carry a caveat about precision, below.

Quantisation ladder, from the matched two-codec run in `src/21`. Mimi loses 0.112 at the
encoder against 0.034 at the quantiser. DAC loses 0.182 at the encoder and *gains* 0.025
at the quantiser. The Mimi-only ladder in `src/19` is a separate run with its own
permutation null and puts the same split at 0.109 against 0.030. Inside Mimi, codebook 0
alone reaches +0.069 against +0.071 for all eight together, and codebook 0 is the one
distilled from WavLM.

Human ceiling on the 60-clip premise subset. Annotators reach 0.730 with audio and
transcript, 0.650 on transcript alone. The best model condition reaches 0.533. Decoding
above chance is not decoding at a useful level.

### How much precision these numbers can carry

Less than three decimal places, and this was found the hard way.

`GroupKFold` assigns folds differently in scikit-learn 1.7 and 1.9. On byte-identical
inputs that moves WavLM L20 from 0.553 to 0.573. Holding everything else constant and
varying only which episodes land in which fold, macro-F1 moves by **sd 0.010, range up to
0.06**:

| representation | mean | sd | min | max |
|---|---:|---:|---:|---:|
| wavlm_L20 | 0.5573 | 0.0094 | 0.5305 | 0.5706 |
| hubert_L23 | 0.5052 | 0.0125 | 0.4776 | 0.5300 |
| mimi_pre | 0.4680 | 0.0145 | 0.4401 | 0.5005 |
| mimi_codes | 0.3699 | 0.0088 | 0.3488 | 0.3857 |

Three consequences. The figures above are tied to a library version on a machine that no
longer exists. They sit at the top of their own range, WavLM's 0.573 being above the
maximum of 25 random partitions. And **differences under roughly 0.03 are not robust** to
a choice nobody thinks of as a choice.

`src/34` therefore defines its own partitions rather than delegating to `GroupKFold`, and
reports the mean over 25 of them with an sd. Anything new should do the same.

### The timing result

Whether stance survives a readout that respects frame order, `src/34`. Each readout is
compared against **its own frame-shuffled control**, which matches on dimensionality and on
every feature's marginal distribution while destroying order, paired on identical
partitions so partition noise cancels.

Temporal order carries stance, and the amount declines monotonically along the processing
ladder:

| representation | order effect | ± | t |
|---|---:|---:|---:|
| WavLM L20 | **+0.113** | 0.013 | 44.6 |
| HuBERT L23 | +0.086 | 0.020 | 21.3 |
| Mimi pre-quantisation | +0.080 | 0.018 | 21.9 |
| Whisper L9 | +0.070 | 0.015 | 23.6 |
| Mimi post-quantisation | +0.048 | 0.019 | 13.0 |
| Sylber | +0.042 | 0.016 | 13.1 |
| DyCAST pre | +0.025 | 0.014 | 8.7 |
| DyCAST post | +0.022 | 0.017 | 6.6 |
| DAC pre | −0.007 | 0.019 | −1.9 |
| DAC post | −0.018 | 0.018 | −4.9 |

That decline tracks the stance-decoding decline, which makes it a candidate mechanism
rather than a correlation. The codec does not merely carry less stance, it carries less of
the temporal structure stance is expressed through.

**Three hypotheses were tested and are not supported.** They were stated before the run.

The loss is **not** an artefact of the readout. Time-aware readouts gain at most +0.031,
which is at the edge of partition noise, and the ranking in [Ch.4] is unchanged. WavLM and
Whisper both peak under `seg4`, at 0.588 and 0.577 against 0.557 and 0.548 for
mean-and-std.

Variable-frame-rate tokenisers do **not** preserve more. Sylber reaches 0.446 and DyCAST
0.40, both below Mimi pre-quantisation at 0.468. Syllable-aligned tokenisation at roughly
4 Hz does not recover prosodic content.

Timing features alone sit **at chance**. Token count, rate and duration moments reach 0.316
for Sylber and 0.338 for DyCAST against a null near 0.33. Order-aware summaries of the
discrete streams, run-length and change-rate, also score below the unigram histogram they
were meant to improve on.

### What was rebuilt, and why

Every array in `features/` is **pooled**, mean and standard deviation over frames or a
unigram histogram over codes, so all of them are invariant to frame order. A rising
`yeah?` and a falling `yeah.` have the same mean by construction, which left the measured
loss unattributable between the codec and the readout.

The frames had been discarded at extraction time and the GPU instance that produced them
no longer existed, so this was a rebuild rather than a re-analysis. `src/31` re-extracts
and keeps the frame sequence for **every layer**, since a forward pass computes them all
regardless and selecting one would mean selecting under the readout being replaced.

Verified: mean-pooling the rebuilt frames reproduces the original A100 features at
**cosine 1.000000**, so the new pipeline agrees with the one the existing figures came
from.

### Corrections in flight

| issue | status |
|---|---|
| `src/18` picks the layer by `argmax` on the same data it reports from, inflating WavLM by 0.003, Whisper by 0.015 and **HuBERT by 0.029** | measured in `src/32`, drafts not yet updated |
| HuBERT's layer is unstable across folds, picks ranged over L10 to L23 | `src/31` saves every layer, so the choice moves downstream |
| single-partition macro-F1 carries sd 0.010 from fold assignment alone, and depends on the scikit-learn version | fixed in `src/34`, drafts not yet updated |
| this README previously described Mimi as `(n, 14336)` from codebooks 1 to 7 | wrong on both counts, the array is `(873, 16384)` and codebook 0 is the carrier |

### Open questions

- Whether the order effect peaks at a different layer than stance decoding does. The full
  63-layer sweep addresses this.
- Whether EnCodec, X-Codec and SpeechTokenizer earn a place. All three are fixed-rate, so
  they extend the ladder without testing timing, and the timing result above lowers the
  value of adding them.
- The absolute permutation null has not been recomputed under the new partitioning.

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

`features/` and `features_frames/` are both gitignored. `features_frames/` holds every
layer of every model and runs to **56.7 GB** (52.8 GiB), which does not fit on a laptop.
`PC_FRAMES_DIR` relocates the tree to any disk without editing code, so it can sit on an
external drive or on cloud storage beside the GPU.

Regenerating it costs about 35 minutes and under a dollar, given the clips and
`requirements-gpu.txt`, so it is cheaper to rebuild than to store indefinitely. Each
representation is a separate memory-mapped `.npy`, so a readout reads one 892 MB layer at a
time rather than the whole tree, which makes even a USB drive workable.

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

**GPU environment.** `requirements-gpu.txt` is a `pip freeze` of the environment that
produced `features_frames/`, committed so the rebuild is reproducible. Recreate it with

```bash
python3 -m venv venv && venv/bin/pip install \
    torch==2.7.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu128
venv/bin/pip install -r requirements-gpu.txt
```

Two traps, both hit on the way here. `librosa` pulls numpy 2.x, which breaks array interop
with a torch built against 1.x, so numpy must be held below 2. And building on top of
Ubuntu's system `python3` packages produces a stale `networkx` that calls the removed
`np.int`, plus a Pillow too old for `transformers`. Build a clean venv rather than one with
`--system-site-packages`.

The instance that produced the older `features/` left no manifest, which is why those
figures cannot be regenerated exactly.

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

`src/31` is the current one, and it selects nothing. A transformer forward pass computes
every hidden state whether or not they are collected, so keeping all 25 layers costs no
extra GPU time, only disk. Choosing a layer at extraction would mean choosing under the
pooled readout, which is the instrument being replaced. Layer, readout and codebook
decisions all move downstream.

Output is one directory per representation holding `<window>.X.npy`,
`<window>.lengths.npy` and `<window>.ids.npy`. Plain `.npy` rather than `.npz` so a
readout can memory-map a single layer without loading the rest, and so extraction streams
to disk clip by clip. Memory stays flat regardless of layer count. Use `load_frames()`
from the same module to read it back lazily.

Progress is an integer on disk rather than a copy of the data, so a crash on a rented box
resumes where it stopped. Resume has been checked against a clean run and is bit-identical.

```bash
python3 src/31_extract_frames.py --models dycast --limit 8   # smoke test first
python3 src/31_extract_frames.py --models all                # roughly 56 GB out
```

### Phase 3, probing and analysis

All evaluation is out-of-fold under **GroupKFold by episode**, so no episode's clips ever
span train and test. Scores carry a 95 per cent CI from an **episode-cluster bootstrap**,
resampling whole episodes rather than clips, and headline configs carry a **permutation
p-value**.

```bash
python3 src/18_probe.py                  # the main battery, six views
python3 src/32_layer_selection.py        # is the layer choice honest and stable
python3 src/34_timing_probe.py --reps core --reps-n 25    # needs features_frames/
```

`src/34` is the one to reach for on anything new. It defines its own episode-to-fold
partitions and averages 25 of them, so its figures do not shift with the scikit-learn
version, and it pairs every order-aware readout against its own frame-shuffled control.

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
| `33_readouts.py` | the readout library, imported not run |
| `34_timing_probe.py` | does stance survive a readout that respects time |

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
