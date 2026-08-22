# Pragmatic Contrast Preservation in Speech Representations

Companion package for the MA dissertation *Track A, Pragmatic Contrast Preservation*.
C. Swartz, MA Computational Linguistics, UCL.

This package exists so that every number in the dissertation can be followed to the code
that produced it. It is not the working repository. The working repository carries eight
months of exploration, abandoned branches and a running lab notebook, none of which a
reader needs. What is here is the finished pipeline, the saved output of every analysis
the dissertation reports, and the record connecting the two.

Start with [`PROVENANCE.md`](PROVENANCE.md). It maps all thirty files in `results/` to the
script that wrote each one, so any claim in the text can be traced in two steps.

---

## The question

Speech-to-speech systems do not consume audio. They consume discrete tokens produced by a
neural codec, and every downstream model sees only those tokens. Codecs are trained to
reconstruct the waveform, which is a different objective from preserving what a speaker
meant.

So the question is whether pragmatic force survives tokenisation. A sincere `yeah` and a
sarcastic `yeah` are the same word. If the transcript is identical and only the delivery
differs, then anything a model can still tell apart has to have come from the delivery.

## The design

Two choices carry the study.

**Lexical control.** The word is held fixed and only the delivery varies. This separates
loss of meaning from loss of sound. Without it, a probe that distinguishes two clips might
simply be reading the words, and the result would say nothing about prosody.

**Stage decomposition.** The probe is applied immediately before and immediately after
quantisation on the same forward pass, so the encoder and the quantiser can be charged
separately. Comparing an encoder latent against a reconstructed waveform instead would
compare vectors that do not live in the same space. Getting this right required projecting
the latent through the quantiser's own input projection before comparison, which raises the
cosine between the two representations from near zero to a value reported in
`results/projection_cosines.txt`.

Evaluation uses repeated episode-to-fold partitions over 25 seeds rather than a single
split, and the fold assignment is defined in the analysis code rather than delegated to
`GroupKFold`. That is deliberate. `GroupKFold`'s assignment changed between two scikit-learn
releases and moved one representation's score by 0.020, which is larger than several of the
differences the study reports. Every margin is quoted against a permutation null computed
for that configuration.

## What was found

**The loss is at the encoder, not the quantiser.** Across three codecs of independent
design, the encoder accounts for most of the drop and the quantiser for much less. In one
codec the quantiser costs nothing measurable at all. This is the opposite of where the
intuitive account would put it.

**What is lost is temporal organisation, not acoustic detail.** The codecs recover
hand-crafted acoustic cue groups better than the continuous encoder does, on half the
feature dimensions. Temporal cues are the exception, and they are the only group that falls
below the continuous baseline. A second continuous encoder included as a control recovers
every group at or above the baseline, so the shortfall belongs to codecs rather than to
representations in general.

**The mechanism is architectural.** Temporal retention orders the codecs by what their
encoder contains, attention against recurrence against neither, rather than by frame rate,
receptive field or latent width, each of which is excluded by a codec that shares it with a
differently-behaved neighbour. An independent measurement of how much a probe gains from
frame order ranks the same systems the same way.

Two variable-frame-rate tokenisers were added to give the competing account, that the loss
follows from imposing a fixed clock on speech, its best chance. Neither recovers the
organisation, so abandoning the clock does not by itself preserve what the clock was
carrying.

---

## What is in this package

| Path | What it is |
|---|---|
| `PROVENANCE.md` | every results file, the script that wrote it, and its checksum |
| `REPRODUCE.md` | the three levels at which this study can be reproduced |
| `CHECKPOINTS.md` | the exact model revisions the figures were produced from |
| `requirements.lock.txt` | the exact environment that produced the reported figures |
| `src/` | the pipeline, from corpus search through annotation to probing |
| `results/` | saved output of every analysis the dissertation reports |
| `figures/` | the three figures in the text, with the script that generates them |
| `labels/labels.csv` | one row per clip, with the analysis labels and no transcript text |
| `annotations.db` | the label store the analysis reads |
| `DATA_AVAILABILITY.md` | what is absent, why, and what it would take to rebuild it |

## What is not in this package

Audio, transcripts and the corpus index are absent by design rather than by oversight, and
the reasons are set out in `DATA_AVAILABILITY.md`. In short, the study analyses public
political podcast audio under an ethics approval that covers computational analysis and not
redistribution. The clips, the verbatim transcript text and the 7.9 GB corpus index are all
withheld on that basis.

One further omission is worth naming here rather than leaving to be discovered. The premise
check was scored from annotator packages that carry both clip audio and the hidden reference
labels, so those packages are not distributed and the figures drawn from them cannot be
regenerated from this package. The dissertation marks every such figure at the point of use.

## Reproducing

See [`REPRODUCE.md`](REPRODUCE.md). Three levels are available, and they differ in what they
require rather than in what they show.

1. **Verify the reported numbers.** Needs nothing but this package. Every figure in the text
   appears in a file in `results/`, and `PROVENANCE.md` says which.
2. **Re-run the probing analysis.** Needs the derived feature arrays, 2.1 GB across two
   release assets. They are derived rather than raw, so they carry no redistributable
   speech and can be published. Both are attached, including the full per-layer stacks, so
   the layer sweep runs as well as the headline analyses.
3. **Rebuild from audio.** Needs your own audio and word-level transcripts. The labels here
   are keyed to specific source episodes and will only align with the identical material.

## Licence

Code is released under the licence in `LICENSE`. The labels are the author's own work. The
underlying audio and transcripts are the property of their respective publishers and are not
redistributed here.
