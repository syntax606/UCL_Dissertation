# Chapter 1: Introduction

*(Draft, rewritten in the dense method-paper register. The
previous spare version is preserved at commit 826bd0b. Hypotheses are stated as formed before the
analyses, and H4 is reported as falsified, which is deliberate. Cross-references marked [Ch.x].)*

## 1.1 Motivation

Full-duplex speech-to-speech systems route speech through a discrete token interface. Moshi
(Défossez et al., 2024) passes the waveform through a neural codec, which encodes it and then
quantises the result, before anything reaches the language model. The codec therefore stands between
the speaker and every component downstream, and it does so in two distinct stages, which matters
because they turn out not to cost the same. The choice is architecturally determined rather than
universal, since systems that generate speech need a discrete target to predict while systems built
only to understand it more often keep continuous features (Arora et al., 2025). The codes, not the audio, are what the system reasons over.
Whatever the tokeniser declines to represent is unavailable thereafter, irrespective of how capable
the downstream model becomes. Under this paradigm the central question is not what a model can learn
but what its input representation carries, and that question is answerable by measurement rather than
by benchmark performance.

The interpersonal layer of speech is a demanding case for any such interface. The same lexical item
performs opposite speech acts depending on delivery. A single *yeah* can accept
a proposal, concede it grudgingly, or reject it by mocking it, and the transcript is identical across
all three. Human listeners recover the distinction from audio well above chance though not
reliably, at 0.73 against a three-way chance of 0.33 in the premise check reported here [4.1].
Whether a codec preserves it is a
question about representational content, and it is separable from whether any particular system
happens to use it.

There is converging evidence that deployed systems handle this layer poorly. A benchmark of
paralinguistic-aware interaction finds leading end-to-end models scoring 3.37 against 3.18 for a
cascaded pipeline that transcribes the query and discards delivery entirely, with two systems falling
below the pipeline (Yang et al., 2026). Audio language models follow lexical content over acoustic
evidence when the two conflict (Pang et al., 2026), and the training data that would teach otherwise
rarely pairs discourse context with paralinguistic cues (Wang et al., 2025a). Safety behaviour is
exposed through the same channel, with attacks that hold transcript content fixed and vary only
delivery succeeding roughly nine times more often than neutral delivery on Qwen2-Audio (Qian and Li,
2026). Failures of this kind are documented in settings with little tolerance for them, including
human-robot interaction (Cao et al., 2025).

These are behavioural observations, and behavioural observations underdetermine the diagnosis. A
system can fail because the information never reached it, or because the information reached it and
was ignored. The two are indistinguishable from the outside and they admit different remedies. Better
modelling can recover information that is present and unused. Nothing downstream recovers information
that was never encoded.

## 1.2 Two extremes and a shared limitation

Existing work approaches this question from two directions, and each resolves one half of it while
leaving the other open.

**Probing without lexical control.** One line establishes that speech representations carry
pragmatic and affective content that text discards, probing self-supervised encoders on
prosody-related tasks including sarcasm (Lin et al., 2022) and characterising where in a layer stack
such content lives (Pasad et al., 2021; Zhang et al., 2024b; Chiu et al., 2025). These studies compare
utterances whose words differ, typically on acted corpora such as MUStARD (Castro et al., 2019). A
probe succeeding under those conditions may be reading word choice rather than delivery, so the
result supports the general claim that speech beats text without isolating the delivery-borne
component that motivates it.

**Attribution without stage isolation.** A second line establishes that discretisation is lossy and
that prosodic and paralinguistic content suffers disproportionately (Mousavi et al., 2026; Guo et
al., 2025), with affect specifically degrading when speech is passed through neural
codecs (Ren et al., 2024; Sun et al., 2026). The standard comparison places a continuous encoder
against a token stream and assigns the difference to quantisation. Those two conditions differ
simultaneously in architecture, training objective, frame rate and feature construction, so the
attribution is an inference from an uncontrolled contrast rather than a measurement of the
discretisation step. Several proposals nonetheless intervene at the codebook on the strength of it,
introducing word-level prosody tokens (Qian et al., 2025) or quantising at multiple segmental units
(Sanders et al., 2025).

Despite their differences, the two lines share a limitation. Neither isolates the variable it needs.
The first varies delivery and lexical content together and cannot separate their contributions. The
second varies quantisation and four other things together and cannot localise the loss. In both cases
the confound is a property of the comparison rather than of the representations, which means it is
removable by design.

## 1.3 Approach

This dissertation removes both confounds jointly, and the two moves are not independent.

**A lexical control.** A corpus of 873 clips was assembled from approximately 7,310 hours of
political podcast audio, spanning 32 shows and 753 episodes, each clip containing one of eight short
phrases whose pragmatic force varies while their wording does not. Each clip carries a fine-grained
pragmatic function tag, from which interpersonal stance is derived, and separately and without
conditioning on that tag, a judgement of arousal. Because the word is
fixed within every contrast, a probe that separates the classes cannot be reading lexical content,
and because arousal is labelled independently the design tests directly whether stance reduces to
vocal energy.

**A stage decomposition.** Rather than comparing a continuous encoder against a token stream, each
codec is probed immediately before and immediately after quantisation, on identical forward passes
with identical pooling, so the rounding step is the only difference between conditions. This requires
establishing which vectors are commensurate inside a residual quantiser, since the input and output
projections do not map to a common space. Measured over all 873 clips, the naive pairing of encoder
latent against reconstructed output reaches a cosine of 0.004 with a 27-fold norm mismatch, while the
correct pairing of projected latent against summed codebook vectors reaches 0.821 for Mimi and 0.773
for the Descript codec [3.5]. The decomposition is then run on both codecs, one distilled from a
self-supervised teacher and one purely acoustic (Kumar et al., 2023).

The dependence between the two is what licenses the result. A stage decomposition on an uncontrolled
task localises the loss of *something*, and for a codec the likely something is phonetic or lexical
detail, which such a system is built to preserve and which says nothing about the interpersonal
layer. Holding the word fixed makes the margins the decomposition assigns to each stage margins on
delivery specifically.

The joint design resolves the trade-off along three axes. **(i) Removing the lexical route.** Within
a phrase, word identity is constant, so no separation can be attributed to vocabulary. **(ii)
Bounding the arousal route.** Stance is decoded within each arousal level, so any separation that
survives is not attributable to loudness alone. **(iii) Localising rather than attributing.** Each stage is measured against
its own empirical permutation null, so the pipeline is decomposed rather than compared end to end.

## 1.4 Results

Under a setting of 873 lexically controlled clips, six frozen representations and a linear diagnostic
probe with fold grouping by episode, the following obtains.

Pragmatic stance is linearly decodable from continuous representations. WavLM clears its own
permutation null by 0.241 and the Whisper encoder by 0.232, against 0.070 for the deployed Mimi token
stream and 0.045 for a discourse-context text embedding. Under the lexical control the ordering
changes, with Whisper at 0.672 ahead of WavLM at 0.659 mean within-word macro-F1 against 0.534 for
discourse text and 0.466 for Mimi, which falls below the text baseline once word identity is removed
[4.3].

The loss is not where it has been attributed. Between WavLM at +0.244 and Mimi's quantised output at
+0.099, the codec encoder accounts for 0.112 and quantisation for 0.034, so the encoder costs
roughly three times what quantisation does. The pattern replicates on the Descript codec, which loses 0.182 at its encoder and *gains*
0.025 at quantisation, so in that system discretisation is marginally beneficial [4.6]. Two codecs of
different objective, frame rate and codebook geometry agree that the encoder is where the information
goes.

What survives is traceable to a component introduced for unrelated reasons. Probing each of Mimi's
eight codebooks separately, the WavLM-distilled codebook 0 is the strongest at 0.402, two acoustic
codebooks are weakly significant and the remaining five are indistinguishable from chance. The
acoustic stack adds nothing to the distilled one, since all eight together reach 0.381 against 0.402
for codebook 0 alone, and codebooks 1 to 7 without it reach only 0.352 [4.5]. The Moshi report motivates distillation by semantic transfer and computational cost and
does not evaluate it in paralinguistic terms, so the preservation is incidental and consequently
unprotected by any routinely reported codec metric [5.4].

## 1.5 Interventions

Six interventions test whether the decodable signal is what it is claimed to be.

**Holding energy constant.** Stance is decoded within each arousal level separately. It survives in
every representation including the discrete ones, with margins reduced by 6 to 37 per cent in seven of
eight model-by-level cells, so stance is entangled with arousal but not reducible to it.

**Holding the show constant.** Regrouping folds by show moves WavLM from 0.573 to 0.530 and Mimi from
0.381 to 0.362, so the probe is not principally recovering speaker identity.

**Varying the context window.** For the continuous encoders performance is flat across local,
segment and discourse windows and does not rise with more surrounding speech, indicating they read
delivery rather than discourse. Mimi is the exception and does rise slightly with context, to 0.411
at the discourse window.

**Varying the readout.** Three summarisations on identical forward passes leave WavLM's margin within
0.009 while moving Mimi's by 0.056, which identifies readout sensitivity as a signature of thin
signal rather than a nuisance (Sun et al., 2026).

**Varying probe capacity.** A non-linear probe under six capacity settings recovers at most +0.025
anywhere, against a continuous-to-discrete gap of roughly 0.14, and the gains that occur track
remaining headroom rather than representation type, with the largest falling on the continuous text
embedding. Linear accessibility therefore bounds rather than explains the result [4.4].

**Replacing the codec.** Repeating the decomposition on an architecturally independent acoustic codec
reproduces the encoder-dominant ordering, which distinguishes a property of codec design from a
property of one system.

Together these characterise the decodable signal as delivery-borne rather than lexical, robust to
held-out shows, and not dependent on surrounding discourse. The interventions also locate where it is
lost, since the codec encoder rather than quantisation accounts for most of the reduction, and what
reaches the token stream arrives largely through the distilled codebook.

## 1.6 Research questions and hypotheses

**RQ1.** Is interpersonal pragmatic force recoverable from speech representations when lexical
content is held constant?

**RQ2.** How much of it is retained by the representation deployed speech-to-speech systems consume?

**RQ3.** Which stage of the pipeline is responsible for what is lost?

Five hypotheses were formed in advance.

**H1.** Human listeners recover more stance from audio than from the transcript. A premise check
rather than a finding, and a negative result ends the study.

**H2.** Stance is linearly decodable from continuous representations under lexical control.

**H3.** The deployed discrete representation retains substantially less of it.

**H4.** The loss is principally attributable to quantisation, on the grounds that discretisation is
the only step capable of rendering two distinct inputs identical.

**H5.** Stance decodability is not reducible to arousal and survives when energy is held constant.

H1, H2, H3 and H5 are supported. **H4 is not**, and its falsification is the most consequential result
reported here, because the interventions currently proposed in the literature are addressed to the
stage it names.

## 1.7 Contributions

**A lexically controlled diagnostic corpus.** 873 clips of naturalistic spontaneous speech across
eight target phrases, annotated on two independently judged axes, in which delivery varies while
wording does not.

**A stage-resolved measurement of codec loss.** A decomposition that separates the codec encoder from
quantisation on commensurate vectors, replicated on two codecs of independent design, showing the
encoder to be the dominant contributor by roughly threefold and quantisation to be marginally
beneficial in one of the two.

**A mechanistic account of what survives.** Identification of the WavLM-distilled codebook as the
strongest single carrier of stance inside Mimi, ahead of two weakly significant acoustic codebooks
and five that are indistinguishable from chance, together with the argument that this preservation is
incidental to its stated objective and invisible to every routinely reported codec metric, and is
therefore removable in a successor system without registering as a regression.

**A falsifiable disagreement with current remedies.** Because most of the loss precedes quantisation,
codebook-level interventions operate on information the encoder has already declined to represent.
The prediction is an ordering between design families rather than a verdict on any system, and it is
testable on a common corpus.

**Reporting of three unsupported hypotheses.** A training-free preservation measure that falls inside
the interval between its two defensible baselines and therefore does not discriminate, a proposed
arousal-confusion mechanism that does not hold, and an apparent asymmetry between the annotated axes
that proved to be a property of the readout rather than of the representation [Ch.6].

## 1.8 Structure

Chapter 2 situates the study in the literatures on discrete speech tokens, probing of speech
representations, and the pragmatics of same-word contrasts, and traces the codec design lineage the
decomposition later measures. Chapter 3 describes the corpus, the two-tier annotation scheme, the
premise check, the six representations and the probing protocol, including the pre-committed choices
of readout and chance level. Chapter 4 reports seven analyses. Chapter 5 interprets them with
attention to what they cannot support. Chapter 6 states the limitations and sets out a programme of
repair that follows from where the loss was found.
