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
chosen over acted emotion corpora for two reasons. The central claim concerns how representations
behave on the spontaneous delivery deployed systems actually encounter. And acted and spontaneous
renditions of the same category are not interchangeable stimuli, a methodological problem set out
for vocal emotion research generally by Scherer (2003) and demonstrated for sarcasm specifically by
Rockwell (2000), who found listeners able to discriminate posed sarcasm from non-sarcasm but not
spontaneous sarcasm. Naturalistic podcast-derived corpora were constructed in response to exactly
this problem (Lotfian and Busso, 2019; Busso et al., 2025), and this corpus follows that precedent
at a finer grain, since the unit of analysis is a single phrase rather than a speaking turn. Audio was
transcribed with word-level timestamps and indexed so that individual token occurrences could
be located and cut precisely.

The study targets eight short, high-frequency phrases whose pragmatic force varies by delivery
while their lexical content is fixed, namely *yeah, okay, right, sure, great, fine, really,* and
*come on*. These fall into three functional families. The agreement particles (*yeah, okay, right,
sure*) are response tokens in the conversation-analytic sense, a class Gardner (2001) characterises
as carrying no dictionary meaning but conveying the listener's stance through phonetic form,
prosodic shape and placement, which is precisely the property this design requires. Individual
members are well described. Schegloff (1982) establishes their continuer function, Beach (1993)
shows *okay* pivoting between receipting prior talk and shifting to next matters, and Gardner (2007)
distinguishes three uses of *right*. Gravano et al. (2012) add that these functions are separated in
spontaneous dialogue by prosodic realisation rather than by wording, and frame that ambiguity as a
problem for spoken dialogue systems. Their account predicts the distribution reported in [B.5],
where neutral stance concentrates almost entirely in these four words, since backchannelling is a
function of this class specifically. The evaluative terms (*great, fine*) and challenge markers
(*really, come on*) are grouped here on functional grounds for this study rather than following an
established classification.

Candidates were first drawn by a stratified pull balanced across shows, then supplemented with
targeted, construction- and sense-specific pulls to fill thin stance cells (for example, the
"yeah right" sarcasm collocation and pause-isolated standalone tokens), because a purely random
pull over-samples the dominant sense of each word. After annotation (below), the usable set is
**873 clips across 32 shows and 753 distinct episodes**. Stance is close to balanced overall
(364 affiliative, 147 neutral, 362 adversarial), and arousal is represented on both sides (345
high, 528 low). Every phrase carries a well-powered binary stance contrast.

For each retained occurrence, three context windows were cut, all centred on the midpoint of
the target word as located from the word-level timestamps. These are a **local** window of 6 s
(plus or minus 3 s), a **segment** window of 10 s, and a **discourse** window of 16 s. The durations
are set against the transcript segments they sit in, which have a median length of 5.4 s, so the
three windows correspond approximately to the target segment alone, the target segment with one
neighbour either side, and the target with roughly a full conversational turn either side. Windows
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

At **Tier 2**, each Tier-1 tag maps to two independently judged analysis axes. **Stance** takes three
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

Clips that could not be judged were discarded against a fixed reason list rather than
force-labelled, and a confidence flag records the rest, of which only nine of the 873 keepers are
marked borderline. Discard reasons, the optional secondary-function field and the annotation
instrument are described in Appendix [A].

## 3.4 Premise check

Before any modelling, the premise that the contrast is speech-borne was validated at the human
level, because if annotators can recover the pragmatic label from the transcript alone, the
probing exercise has no target. A 60-clip subset, balanced across stance, was judged by two
auxiliary annotators in two conditions, counterbalanced so that each annotator saw one half of
the clips as transcript only and the other half with audio, against a hidden reference. The decision rule was
fixed before scoring and is given in Appendix [D]. The outcome, reported in [4.1], is that audio
carries pragmatic information beyond the words while discourse context alone is a strong baseline,
which motivates splitting the text baseline into two roles (3.5) and treating audio's contribution
as the increment over context.

## 3.5 Representations and feature extraction

Seven representations are compared, with the text baseline supplying two conditions rather than one
[below]. With one exception, noted below, the selection is determined by the research question rather
than by availability.

**Why these models.** Mimi is the object of study because it is the tokeniser a deployed full-duplex
system actually consumes rather than a research codec [2.2], and it distils its first codebook from
WavLM-Large, which produces 1024-dimensional embeddings at 50 Hz (Défossez et al., 2024). Measuring
what that distillation transfers therefore requires probing WavLM at that size, so WavLM is not a
free choice.
HuBERT-large is its matched control, sharing architecture, depth and width and differing chiefly in
WavLM's noise and overlapped-speech augmentation, so the pair isolates that augmentation rather than
scale. The Whisper encoder is included to test whether a transcription objective strips paralinguistic
content, so the objective rather than the scale is the variable under test. The small variant, at 13
layers of 768 units against 25 of 1,024, is the one genuinely constrained choice here, and the
constraint bears asymmetrically on the conclusion. A null result would have been uninterpretable,
since a failure to recover stance could not be separated from insufficient capacity. The positive
result reported in [4.3] is not, since capacity can only have worked against it. The Descript codec is used as the undistilled contrast
because it sits on the reconstruction-only branch of the lineage in [2.1]. SpeechTokenizer would not
serve, since it also distils from a self-supervised teacher and so does not contrast on the variable
of interest, and DAC is preferred to EnCodec as the more recent reconstruction-only codec and one
already benchmarked against Mimi elsewhere (Mousavi et al., 2026). MPNet is used for the text
baseline because the argument requires a strong text competitor rather than a strawman, since the
premise check shows discourse context recovers a substantial part of the contrast [4.1]. The seventh
representation is not a model at all. eGeMAPS supplies a hand-crafted acoustic baseline, without
which the study could report that a learned representation separates stance without establishing
that this is more than pitch and energy would give. It also serves a second purpose, since its
features are individually interpretable and can therefore be grouped by what they measure, which is
what the cue analysis in [4.7] requires.

Feature extraction was run once on a single A100 GPU and the resulting features frozen. No representation is fine-tuned,
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
Keeping the full stack matters because a model built on Mimi consumes every codebook, and because it
allows the codebook-level analysis in [Ch.4] to probe each stream separately rather than assuming in
advance where pragmatic information sits. The histogram is one summarisation among several and is
adopted as the deployed condition because it preserves token identity, which no pooled readout does.
Its cost relative to an embedding readout is measured rather than assumed, and turns out to be
substantial [4.3, G.2].

Codebook-level analysis is ordinarily confounded, and the lexical control is what removes the
confound. Shi et al. (2026) show that phonetic content in a Mimi code stream is not confined to the
distilled first codebook, finding that "even without the first layer, as the acoustic codebook
layers go deeper, the speech features from these layers also accumulate a substantial" amount of
phonetic information. Because the target word is held constant, phonetic content is constant across
every contrast, so no discriminative signal a probe recovers at codebook level can be phonetic in
origin.

**Undistilled discrete codec.** The Descript Audio Codec at 24 kHz (Kumar et al., 2023) is run as a
contrast to Mimi. It is a purely acoustic codec trained on reconstruction and adversarial objectives
with no distillation term, so it sits on the reconstruction-only branch of the lineage described in
[2.1]. It differs from Mimi in frame rate, at 75 Hz against 12.5, and in codebook size, at 1,024
entries against 2,048, so it is not a controlled ablation of the distillation objective and is not
presented as one. Its frame rate follows from an encoder stride of 320 at 24 kHz. The checkpoint
provides 32 residual codebooks against Mimi's 8, so the first eight are used, matching Mimi's
deployed depth and making the two ladders comparable at equal quantiser count rather than at equal
bitrate.

**Isolating quantisation.** Comparing a continuous encoder against a token stream confounds
quantisation with feature construction, frame rate, architecture and training objective. To separate
them, both codecs are additionally probed immediately before and immediately after quantisation, on
identical forward passes and with identical pooling, so the only difference between the two
conditions is the rounding step.

This requires care about which vectors are comparable. In both codecs the residual quantiser
operates in a projected space rather than on the encoder output directly, applying an input
projection before quantising and an output projection after summing the selected codebook vectors.
Those two projections do not map to a common space, so comparing the encoder latent against the
quantiser's reconstructed output would compare vectors that are not commensurate. Measured over all
873 clips their cosine is 0.004, and their mean norms differ by a factor of roughly 27, at 1.5
against 39.9. The comparable pair is the projected latent against the summed codebook vectors taken
before the output projection. Measured cosine between that pair is 0.821 for Mimi and 0.773 for the
Descript codec, with per-clip minima of 0.766 and 0.717, confirming a shared space. These
diagnostics are produced by `src/24_projection_cosines.py`. Both sides are then pooled by mean
and standard deviation, so the embedding readout is held constant and the histogram readout used for
the deployed condition plays no part in this comparison.

**Hand-crafted acoustic baseline.** The eGeMAPSv02 functionals are extracted with openSMILE, giving
88 features per clip covering F0 statistics, loudness, spectral slope and balance, formants, voice
quality through jitter, shimmer and harmonics-to-noise ratio, and rate proxies from voiced and
unvoiced segment lengths. This is the standard minimal set for affective computing and is used here
unmodified. For the cue analysis the 88 features are partitioned by what they measure into level,
contour, voice quality, temporal and spectral groups, a partition fixed by the feature definitions
rather than by inspecting results.

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

**Probe capacity.** A linear probe measures whether information is linearly accessible, which is not
the same as whether it is present, a distinction developed at length by Belinkov (2022). The
companion concern, that a probe may succeed by memorising rather than by reading structure, is
addressed by Hewitt and Liang (2019) through control tasks with randomised labels, and the empirical
permutation null used throughout is an instance of that idea. Accessibility is tested rather than
argued around, by a small strongly regularised non-linear probe run on identical features and folds
under six capacity settings, since the gain over a linear probe depends on the capacity chosen. The
quantity carried forward is the bound across that sweep rather than the ordering at any one setting
[G.3].

**Uncertainty and significance.** Two procedures accompany every headline score. A 95%
confidence interval is obtained by an **episode-cluster bootstrap** that resamples whole episodes
rather than individual clips, respecting the non-independence of clips nested in episodes. A
**permutation test** shuffles the stance labels and refits the probe many times. The p-value is
the fraction of permutations reaching the observed macro-F1, establishing that decodability
exceeds chance.

**The analyses.** Chapter 4 reports six, each named by the section that carries it. Pooled three-way
decodability at each model's best layer [4.2]. The per-phrase within-word contrast, which is the
lexical control at the heart of the design and under which word identity carries no information
[4.3]. Three controls, namely matched arousal, fold grouping by show and a context-window sweep
[4.4]. A layer sweep and a codebook-level probe [4.5]. The quantisation ladder, comparing the
continuous teacher against each codec's projected encoder latent and post-quantisation vectors under
a shared embedding readout, on two codecs of different design [4.6]. And a cue-retention analysis
[4.7], which asks not whether stance is decodable but whether the acoustic properties it is built
from are recoverable, by ridge regression from each representation to each eGeMAPS feature,
cross-validated on the same folds and reported as R-squared averaged within cue group. That last
analysis is what separates a codec discarding acoustic detail from a codec retaining it in an
unusable arrangement, and the two are otherwise indistinguishable from decoding scores alone.

Four further checks bear on how these figures should be read rather than on what they say, and are
reported in Appendix [G]. They are the model-against-human comparison on the premise subset, the
readout decomposition, a probe-capacity sweep, and a training-free contrast-preservation measure.

Hyperparameters, exact dimensionalities, and the full per-phrase counts are given in Appendix
[B]. All code and the analysis scripts are released so that, given a corpus and the label store,
every number in [Ch.4] can be reproduced.
