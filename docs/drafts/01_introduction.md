# Chapter 1: Introduction

*(Draft, rewritten in the dense method-paper register. The
previous spare version is preserved at commit 826bd0b. Hypotheses are stated as formed before the
analyses, and H4 is reported as falsified, which is deliberate. Cross-references marked [Ch.x].)*

## 1.1 Motivation

Spoken interaction with machines is moving from turn-taking exchange to full-duplex conversation.
The Moshi report states the limitation it was built to remove directly, that prior systems "rely on
a segmentation into speaker turns, which does not take into account overlapping speech,
interruptions and interjections", and notes that overlapping speech accounts for ten to twenty per
cent of spoken time (Défossez et al., 2024). The target is not a better question-answering system.
It is a system that can be interrupted, that can listen while speaking, and that can produce the
small acknowledgements by which people signal they are still there.

That capability rests on a specific class of linguistic object. Response tokens such as *yeah*,
*okay*, *right* and *mm-hm* are the machinery of spontaneous conversation, marking continued
attention, alignment and the passing of a turn (Schegloff, 1982; Gardner, 2001). Their defining
property is that they carry no dictionary meaning. What they convey is the speaker's stance toward
what they are hearing, and it is conveyed through phonetic form, prosodic shape and placement in the
flow of talk (Gardner, 2001), functions distinguished in spontaneous dialogue by delivery rather
than by wording (Gravano et al., 2012). A warm *yeah*, a grudging *yeah* and a mocking *yeah* are
the same transcript and three different conversational moves. Human listeners recover the
distinction from audio well above chance though not reliably, at 0.73 against a three-way chance of
0.33 in the premise check reported here [4.1].

These systems are deliberately trained on that machinery. Moshi's instruction dialogues are
generated with prompts requiring the transcript to "use some backchanneling", without assigning it
to either speaker, and its multi-stream training samples one conversational side at random as the
system's own, so backchannels appear in both streams as things to hear and things to say. Both
streams are encoded by the same neural codec, which passes the waveform through an encoder and then
quantises the result before anything reaches the language model. The codec therefore stands between
the speaker and every component downstream, in both directions and in two distinct stages, which
matters because the stages turn out not to cost the same. The choice is architecturally determined
rather than universal, since systems that generate speech need a discrete target to predict while
systems built only to understand it more often keep continuous features (Arora et al., 2025). What
the codec declines to represent is unavailable thereafter, however capable the model behind it.

So the move toward spontaneous conversation depends on a channel that the architecture enabling it
was never designed to preserve. There is converging evidence that the resulting systems handle that
channel poorly. A benchmark of paralinguistic-aware interaction finds leading end-to-end models
scoring 3.37 against 3.18 for a cascaded pipeline that transcribes the query and discards delivery
entirely, with two systems falling below the pipeline (Yang et al., 2026). Audio language models
follow lexical content over acoustic evidence when the two conflict (Pang et al., 2026), and the
training data that would teach otherwise rarely pairs discourse context with paralinguistic cues
(Wang et al., 2025a). Safety behaviour is exposed through the same channel, with attacks that hold
transcript content fixed and vary only delivery succeeding roughly nine times more often than
neutral delivery on Qwen2-Audio (Qian and Li, 2026). Failures of this kind are documented in
settings with little tolerance for them, including human-robot interaction (Cao et al., 2025).

These are behavioural observations, and behavioural observations underdetermine the diagnosis. A
system can fail because the information never reached it, or because the information reached it and
was ignored. The two are indistinguishable from the outside and they admit different remedies.
Better modelling can recover information that is present and unused. Nothing downstream recovers
information that was never encoded.

This dissertation pursues the first possibility through three nested questions. Whether the contrast
is present in speech representations at all once the words are held constant. How much of it the
representation deployed systems consume retains. And at which stage of the pipeline the remainder is
lost. Each is worth asking only if the previous one is answered affirmatively, and it is the third
where this study departs from the existing literature.

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
phrases whose pragmatic force varies while their wording does not. Four of the eight are the response
tokens of [1.1], so the corpus is built from the class whose meaning the full-duplex setting depends
on and whose meaning delivery alone supplies. Each clip carries a fine-grained
pragmatic function tag, from which interpersonal stance is derived, and separately and without
conditioning on that tag, a judgement of arousal. Because the word is
fixed within every contrast, a probe that separates the classes cannot be reading lexical content,
and because arousal is labelled independently the design tests directly whether stance reduces to
vocal energy.

**A stage decomposition.** Rather than comparing a continuous encoder against a token stream, each
codec is probed immediately before and immediately after quantisation, on identical forward passes
with identical pooling, so the rounding step is the only difference between conditions. This requires
establishing which vectors are commensurate inside a residual quantiser, since its input and output
projections do not map to a common space and the obvious pairing compares vectors that are neither
aligned nor of comparable scale [3.5]. The decomposition is run on both codecs, one distilled from a
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

## 1.4 Findings

Three results follow, and Chapters 4 and 5 report them in full. Pragmatic stance is linearly
decodable from continuous representations under the lexical control, and survives every control
applied to it, including matched arousal, held-out shows, three context windows, three readouts and
six non-linear probe capacities. The representation deployed systems consume retains a fraction of
it, and under the summarisation deployed systems imply it falls below a discourse-text baseline once
word identity is removed. And the loss is not
where this study expected. The codec encoder costs roughly three times what quantisation does, the
same ordering holds on a second codec of independent design where quantisation is marginally
beneficial, and what reaches Mimi's token stream is carried mainly by the codebook distilled from
WavLM, a component introduced for semantic transfer and computational economy rather than for
anything paralinguistic.

## 1.5 Research questions and hypotheses

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

## 1.6 Contributions

**A lexically controlled diagnostic corpus**, 873 clips of naturalistic spontaneous speech across
eight target phrases, annotated on two independently judged axes.

**A stage-resolved measurement of codec loss**, replicated on two codecs of independent design,
showing the encoder to be the dominant contributor by roughly threefold and quantisation to be
marginally beneficial in one of the two.

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

## 1.7 Structure

Chapter 2 situates the study in the literatures on discrete speech tokens, probing of speech
representations, and the pragmatics of same-word contrasts, and traces the codec design lineage the
decomposition later measures. Chapter 3 describes the corpus, the two-tier annotation scheme, the
premise check, the six representations and the probing protocol, including the pre-committed choices
of readout and chance level. Chapter 4 reports seven analyses. Chapter 5 interprets them with
attention to what they cannot support. Chapter 6 states the limitations and sets out a programme of
repair that follows from where the loss was found.
