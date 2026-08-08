# Chapter 3: Data and Methods

*(Draft. Target budget ~2,600 words. Placeholders for cross-references are marked [Ch.x].)*

## 3.1 Overview

This chapter describes the corpus, the annotation scheme, the human validation step, the
feature-extraction pipeline, and the probing protocol. The design follows directly from the
commitments the literature forces onto the study [Ch.2]. The pragmatic contrast must be shown
to be speech-borne before any modelling. The transcript baseline must be split into a
manipulation check and a substantive baseline. The speaker confound must be controlled at both
the classifier and the distance-measure level, and the arousal confound must be addressed by
labelling arousal independently of stance. Each of these is realised concretely below.

## 3.2 Corpus and target phrases

The material is naturalistic speech drawn from political podcasts and broadcast programmes,
chosen over acted emotion corpora because the central claim concerns how representations behave
on the spontaneous, in-the-wild delivery that deployed systems actually encounter. Audio was
transcribed with word-level timestamps and indexed so that individual token occurrences could
be located and cut precisely.

The study targets eight short, high-frequency phrases whose pragmatic force varies by delivery
while their lexical content is fixed, namely *yeah, okay, right, sure, great, fine, really,* and
*come on*. These fall into three functional families, agreement particles (*yeah, okay, right,
sure*), evaluative terms (*great, fine*), and challenge markers (*really, come on*). Each can
perform several speech acts. "Right" can signal agreement, correction, sarcasm, or challenge.
"Sure" can signal consent, reluctance, or disbelief. "Great" can signal approval, sarcasm, or
resignation. In every case the word is constant and the meaning is carried by prosody, timing,
and discourse position.

Candidates were first drawn by a stratified pull balanced across shows, then supplemented with
targeted, construction- and sense-specific pulls to fill thin stance cells (for example, the
"yeah right" sarcasm collocation and pause-isolated standalone tokens), because a purely random
pull over-samples the dominant sense of each word. After annotation (below), the usable set is
**873 clips across 32 shows and 753 distinct episodes**. Stance is close to balanced overall
(364 affiliative, 147 neutral, 362 adversarial), and arousal is represented on both sides (345
high, 528 low). Every phrase carries a well-powered binary stance contrast. Neutral labels
concentrate in the agreement particles, which is a linguistic property of those words rather
than a sampling gap, and is reported as such.

For each retained occurrence, three context windows were cut, all centred on the midpoint of
the target word as located from the word-level timestamps. These are a **local** window of 6 s
(plus or minus 3 s), a **segment** window of 10 s, and a **discourse** window of 16 s. Windows
are symmetric fixed durations rather than segment-boundary-aligned spans, which keeps the amount
of acoustic context strictly comparable across clips. All clips are 16 kHz mono with EBU R128
loudness normalisation, so that overall level cannot act as a trivial cue. Holding three nested
windows allows the later context-window analysis to separate representations that recover a
contrast from local delivery alone from those that require surrounding discourse [3.6, Ch.4].

## 3.3 Annotation scheme

Labelling uses a two-tier scheme (full codebook in Appendix [A]). At **Tier 1** the annotator
assigns one of fourteen fine pragmatic-function tags, such as sincere agreement, emphatic
agreement, neutral backchannel, topic closure, reluctant or concessive, skeptical, sarcastic,
dismissive, genuine approval, resigned, genuine surprise, confrontational, or encouraging. These
tags are the natural categories an annotator can hear, and they keep the judgement close to the
data rather than forcing an abstract choice at label time.

At **Tier 2**, each Tier-1 tag maps to two orthogonal analysis axes. **Stance** takes three
values, affiliative, neutral, and adversarial, and is derived from the function tag but
overridable. **Arousal** takes two values, low and high, and is judged independently of stance.
Keeping arousal separate is a deliberate defence against a known confound. The binary
literal-versus-nonliteral distinction collapses sarcasm, disbelief, dismissal, and reluctance
into one class, and these differ substantially in arousal, so a probe that appears to separate
stance might only be re-deriving that these encoders represent loudness or excitation. Because
arousal is labelled separately, the headline test can be posed as stance separability *at
matched arousal*, since an enthusiastic "great!" and a contemptuous "great" carry the same energy and
opposite stance, and only a representation reading pragmatic force, not arousal, will separate
them [3.6, Ch.4].

Each clip also carries a **confidence** flag (clear or borderline), so that ambiguous items are
recorded as data rather than silently dropped, and a slot for an optional secondary function.
Clips that were mistranscribed or inaudible, dominated by music, advertising, or overlapping
speech, not the target use of the word, or too ambiguous to judge were discarded rather than
force-labelled. The 873 keepers are the confidently stance-labelled remainder. Annotation was
carried out on a purpose-built, fully self-contained offline tool that embeds the audio and
autosaves, and all labels are held in a persistent store that is the single source of truth for
the analysis.

## 3.4 Premise check

Before any modelling, the premise that the contrast is speech-borne was validated at the human
level, because if annotators can recover the pragmatic label from the transcript alone, the
probing exercise has no target. A 60-clip subset, balanced across stance, was judged by two
auxiliary annotators in two conditions, counterbalanced so that each annotator saw one half of
the clips as transcript only and the other half with audio, against a hidden reference. Accuracy
was 0.65 for transcript-with-discourse-context and 0.73 for audio-plus-transcript, against a
three-way chance level of 0.33. The gap confirms that audio carries pragmatic information beyond
the words while also showing that discourse context alone is a strong, honest baseline. This
directly motivates splitting the text baseline into two roles (3.5) and treating audio's
contribution as the increment over context. The agreement particles were hardest even from
audio, which anticipates the per-phrase results in [Ch.4].

## 3.5 Representations and feature extraction

Six representations are compared, spanning self-supervised continuous encoders, a supervised
continuous encoder, a deployed discrete tokenizer, a second discrete codec used as a contrast, and
a text baseline. Feature extraction was
run once on a single A100 GPU and the resulting features frozen. No representation is fine-tuned,
which is the defining property of a diagnostic probing study. Each clip is processed
individually (batch size one), so there is no padding to pool over.

**Self-supervised continuous encoders.** WavLM-large and HuBERT-large are run with all hidden
states exposed. For each transformer layer, the sequence of frame vectors is summarised by
concatenating its per-dimension mean and standard deviation over time, giving a fixed
2,048-dimensional vector per layer and a (layers x 2*hidden) matrix per clip. Retaining every
layer rather than assuming a mid-layer optimum is a direct response to the finding that the
strongest paralinguistic performance does not always sit in the final layers [Ch.2]. The
layer-wise analysis in [Ch.4] uses this.

**Supervised continuous encoder.** The Whisper-small encoder is treated the same way, with one
correction. Whisper pads every input to 30 s internally, so pooling over the full output would
average in silence. Only the valid frames corresponding to the actual clip duration are pooled,
computed from the clip length at the encoder's frame rate.

**Deployed discrete tokenizer.** Mimi, the tokenizer used by deployed speech-to-speech systems,
is run at 24 kHz (clips are resampled in memory). Mimi emits residual code streams. Codebook 0
is a WavLM-distilled stream and codebooks 1 to 7 carry acoustic refinement. All eight are
retained. Each codebook's token sequence is summarised as a normalised unigram histogram over
its codebook, and the eight histograms are concatenated into a single fixed vector per clip.
Keeping the full stack matters for two reasons. It represents Mimi at the granularity a language
model built on it would actually consume, and it allows the codebook-level analysis in [Ch.4] to
probe each stream separately rather than assuming in advance where pragmatic information sits.

Codebook-level analysis is ordinarily confounded, and it is worth stating why this design escapes
that. Shi et al. (2026) show that the phonetic content of a Mimi code stream is not confined to
the distilled first codebook, finding that "even without the first layer, as the acoustic codebook
layers go deeper, the speech features from these layers also accumulate a substantial" amount of
phonetic information. For an uncontrolled study that is a serious problem, because a probe
separating classes at codebook level cannot be shown to be reading paralinguistic rather than
phonetic structure. Here it is not a problem. Because the target word is held constant across the
contrast, phonetic content is constant across it too, so any discriminative signal a probe
recovers cannot be phonetic in origin. The lexical control neutralises the confound that pervades
codebook-level analysis, which is a second reason for the design beyond isolating delivery from
lexical choice.

**Undistilled discrete codec.** The Descript Audio Codec at 24 kHz (Kumar et al., 2023) is run as a
contrast to Mimi. It is a purely acoustic codec trained on reconstruction and adversarial objectives
with no distillation term, so it sits on the reconstruction-only branch of the lineage described in
[2.2]. It differs from Mimi in frame rate, at 75 Hz against 12.5, and in codebook size, at 1,024
entries against 2,048, so it is not a controlled ablation of the distillation objective and is not
presented as one. Its eight codebooks are used, matching Mimi's deployed depth.

**Isolating quantisation.** Comparing a continuous encoder against a token stream confounds
quantisation with feature construction, frame rate, architecture and training objective. To separate
them, both codecs are additionally probed immediately before and immediately after quantisation, on
identical forward passes and with identical pooling, so the only difference between the two
conditions is the rounding step.

This requires care about which vectors are comparable. In both codecs the residual quantiser
operates in a projected space rather than on the encoder output directly, applying an input
projection before quantising and an output projection after summing the selected codebook vectors.
Those two projections do not map to a common space, so comparing the encoder latent against the
quantiser's reconstructed output would compare vectors that are not commensurate, and the measured
cosine between them is 0.008. The comparable pair is the projected latent against the summed
codebook vectors taken before the output projection. Measured cosine between that pair is 0.808 for
Mimi and 0.773 for the Descript codec, confirming a shared space. Both sides are then pooled by mean
and standard deviation, so the embedding readout is held constant and the histogram readout used for
the deployed condition plays no part in this comparison.

**Text baseline.** A sentence-transformer (MPNet) encodes two texts per clip, following the two
roles the premise check established. The **target-only** embedding encodes the bare target word.
Because the word is held constant within a phrase, this embedding is near-identical across that
phrase's clips and is at chance *within* phrase by construction. Pooled across the eight phrases
it is not at chance, because the phrases differ in their stance base rates, so a probe can score
above chance from word identity alone. It therefore functions as a manipulation check for the
within-word analyses rather than as a competitor, and the pooled figure must be read with that
base-rate artefact in mind [Ch.4].
The **discourse-context** embedding encodes the surrounding transcript and is the substantive
text baseline, since pragmatic cues can leak into neighbouring words.

All features are stored with an aligned clip-identifier index so that labels, groups, and
feature matrices can be joined unambiguously downstream.

## 3.6 Probing protocol and analyses

**Probe and evaluation.** Each probe is an L2-regularised logistic regression on standardised
features, with balanced class weights to offset the neutral minority. All reported scores are
**out-of-fold under GroupKFold by episode**, so no episode's clips ever appear in both training and
test, which prevents leakage through shared speaker, topic, or recording conditions. The primary
metric is macro-F1 over the three stance classes.

**Choice of readout.** Frame-level representations are summarised by concatenating the per-dimension
mean and standard deviation over time, which is the convention in the probing literature and is
applied identically to every representation. This readout is fixed as primary in advance of the
analyses reported in [Ch.4]. Because it is order-free, alternatives that retain temporal structure
are reported as a sensitivity analysis rather than as competing headline figures, and the choice of
primary readout is not revisited in light of those results.

**Choice of chance level.** Macro-F1 has no fixed chance value, so the reference matters. A
majority-class constant predictor scores only 0.196 here, because macro-F1 assigns zero to each
of the two classes such a predictor never emits. That is not the right comparison for this probe,
because balanced class weights mean it distributes predictions across all three classes, so its no-skill
counterpart is not degenerate. The reference used throughout is therefore the **empirical
permutation null**, obtained by refitting the entire pipeline on shuffled stance labels, which
places chance near 0.33 (uniform and prior-matched random guessing give 0.322 and 0.333
respectively, closely agreeing). The majority figure is reported alongside for completeness only.
Using the permutation null rather than the majority score materially changes interpretation of
the weaker representations, as Chapter 4 discusses.

**Probe capacity.** A linear probe measures whether information is linearly accessible, which is
not the same as whether it is present. To test that this constraint is not driving the results, a
small non-linear probe was run as a companion on identical features and identical folds, a
single-hidden-layer network of 64 units with strong weight decay and early stopping. It is kept
deliberately small, because a sufficiently powerful probe can learn a task from almost any
representation and thereby report on itself rather than on the encoding.

Because the gain over a linear probe depends on the capacity chosen, and moves by up to 0.06 across
reasonable settings, the comparison is run under six configurations varying hidden width, weight
decay and early stopping rather than under one. The quantity carried into [Ch.4] is accordingly the
largest gain observed anywhere in that sweep, which is a bound and is stable, rather than the
per-representation ordering at any single setting, which is not. Full settings are in Appendix [B]
and the procedure is in `src/22_nonlinear_probe.py`.

**Uncertainty and significance.** Two procedures accompany every headline score. A 95%
confidence interval is obtained by an **episode-cluster bootstrap** that resamples whole episodes
rather than individual clips, respecting the non-independence of clips nested in episodes. A
**permutation test** shuffles the stance labels and refits the probe many times. The p-value is
the fraction of permutations reaching the observed macro-F1, establishing that decodability
exceeds chance.

**Seven analyses.** The results chapter reports seven views. (A) **Pooled three-way stance
decodability** per representation, using the best layer for the audio encoders, on the segment
window. (B) A **context-window sweep** across the local, segment, and discourse windows at each
model's best layer, distinguishing delivery-borne from discourse-recoverable contrasts. (C) The
**per-phrase within-word contrast**, the lexical control at the heart of the design. Within each
phrase, the probe attempts the dominant binary stance contrast, averaged across the eight
phrases, so that any separation cannot be attributed to word identity. (D) The **matched-arousal
test**, decoding stance within each arousal level separately, so a positive result cannot be
dismissed as encoding loudness. (E) A **speaker-identity control**, re-scoring with folds grouped
by show so that training and test never share a speaker, alongside the by-episode setting.
(F) A training-free **contrast-preservation score**, a within-speaker, within-word,
leave-one-out nearest-centroid measure over the embedding space. Because it is geometric and
unprotected by grouped cross-validation, it is computed within speaker and reported with the
caveats developed in [Ch.5], as a corroborating rather than a headline result. (G) A
**quantisation ladder**, comparing the continuous teacher, each codec's projected encoder latent and
each codec's post-quantisation vectors under the shared readout just described, which attributes the
gap between continuous and discrete representations to the encoder and to quantisation separately
and repeats that attribution on two codecs of different design.

Hyperparameters, exact dimensionalities, and the full per-phrase counts are given in Appendix
[B]. All code and the analysis scripts are released so that, given a corpus and the label store,
every number in [Ch.4] can be reproduced.
