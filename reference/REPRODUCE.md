# Reproducing

Three levels, differing in what they require rather than in what they show. Level 1 needs
nothing beyond this package and settles whether the dissertation reports what its code
produced. Level 2 re-runs the analysis. Level 3 rebuilds from audio and is included for
completeness rather than because it is expected of a reader.

---

## Level 1, verify the reported numbers

Every three-decimal figure in the dissertation appears in a file under `results/`.
`PROVENANCE.md` gives the producing script and a checksum for each file.

```bash
grep -rn "0.821" results/
```

The dissertation's own consistency checker runs against the manuscript and is included as
`src/53_check_draft.py`. It verifies fifteen invariants, among them that table margins
agree with subtracting their own columns, that every table figure appears in a results
file, that table and figure numbering is sequential, and that no embedded figure has drifted
from the file that generated it.

One limitation of that checker is worth stating plainly, because it caused a real defect
during writing. It verifies that a cross-reference resolves to a section that exists, not
that the section is the right one. Renumbering an appendix once left four references
pointing one section short while the checker still reported fifteen of fifteen passing.

## Level 2, re-run the probing analysis

This needs the derived feature arrays. They are pooled embeddings and frame sequences
rather than audio, so they carry no redistributable speech, but they total 2.1 GB and are
therefore attached to the tagged release rather than tracked in git. Both are needed for
the full analysis and they divide where the analyses divide.

| Asset | Size | What it carries |
|---|---|---|
| `features.tar.gz` | 1.29 GB | pooled embeddings, one row per clip, every layer of WavLM, HuBERT and Whisper |
| `features_frames.tar.gz` | 0.79 GB | frame sequences, where EnCodec, Sylber and DyCAST live |

Unpack both into the repository root, so that `features/` and `features_frames/` sit
beside `src/`. `FEATURE_MANIFEST.json` lists every file with its size and gives a sha256
for each archive, so a download can be checked before it is trusted.

The split matters for what you can run. The ladder, the within-word analysis, the controls
and the eGeMAPS work read `features/` alone. Cue retention, the timing and order-effect
work, and every row involving EnCodec, Sylber or DyCAST read `features_frames/`.

The layer stacks are shipped whole rather than sliced to the three layers the paper
reports. Slicing would cut 1.17 GB to 59 MB, but the analysis selects a layer by indexing
that axis directly, so every script would need its indexing changed. Editing the code a
reader is meant to re-run, in order to make the download smaller, is a bad trade. It also
keeps the layer sweep in `src/32_layer_selection.py` runnable, which a sliced package would
not.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock.txt
```

The lock file pins scikit-learn deliberately. `GroupKFold`'s assignment changed between
releases 1.7 and 1.9 and moved one representation's score by 0.020, which is larger than
several differences the study reports. The analysis therefore defines its own fold
assignment, and the pin exists so that the scripts predating that change still reproduce.

With features in place, the analyses that carry the argument are these.

```bash
python3 src/35_ladder_repeated.py       # the ladder, 25 partitions
python3 src/48_cue_retention_repeated.py # which cue groups each codec keeps
python3 src/52_cue_groups_repeated.py    # which cue groups carry stance
python3 src/34_timing_probe.py           # order effect against a shuffled control
python3 src/51_build_figures.py          # the three figures in the text
```

Expect the figures to regenerate byte-identically. Expect the analyses to reproduce to the
third decimal, since partitions are seeded. The permutation nulls carry a Monte Carlo
standard error near 0.001 at 200 shuffles, so a null may move in the last place.

One analysis will not reproduce from this package, and it is marked where it is used in the
dissertation. The premise check was scored from annotator packages that carry clip audio
and the hidden reference labels, so those packages are withheld and the figures drawn from
them, including the per-phrase human accuracies, cannot be regenerated here.

## Level 3, rebuild from audio

You supply the audio and word-level transcripts. The labels here are keyed by
`candidate_id`, which encodes the episode and the segment, so they align only with the
identical source episodes. Against different material the pipeline runs and the labels do
not apply, which makes this a rebuild of the method rather than of the result.

```bash
cp configs/paths.example.yaml configs/paths.yaml   # point at your own audio
python3 src/01_ingest.py
python3 src/02_search_candidates.py
python3 src/03_filter_candidates.py
python3 src/17_extract_features.py
```

Audio extraction additionally needs `ffmpeg` and `ffprobe` on the path, installed at system
level rather than through pip.

---

## Regenerating this package

```bash
python3 src/55_build_reference.py
```

`PROVENANCE.md` and `requirements.lock.txt` are generated. `README.md` and this file are
authored, and the generator checks them, so a figure quoted here that no longer appears in
any results file fails the build rather than sitting stale. That check exists because the
working repository's README drifted for months without anyone noticing.
