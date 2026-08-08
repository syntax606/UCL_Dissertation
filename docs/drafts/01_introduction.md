# Chapter 1: Introduction

*(Draft. Target budget ~1,200 words. Hypotheses are stated as they were formed before the analyses,
and Chapter 4 reports that not all of them were supported, which is deliberate. Cross-references
marked [Ch.x] and [n.n].)*

## 1.1 Motivation

A speaker says "yeah". Depending on how it is delivered, that single syllable can accept a proposal,
concede a point grudgingly, or reject the proposal outright by mocking it. The transcript is
identical in all three cases. Everything that distinguishes them sits in timing, pitch movement,
voice quality and emphasis, and human listeners resolve the distinction without apparent effort.

This is ordinary in conversation and it is a live engineering problem, because a growing class of
systems no longer receives speech as speech. Contemporary speech-to-speech models convert audio into
sequences of discrete tokens before any modelling occurs, so a tokeniser stands between the speaker
and everything downstream. Whatever that tokeniser discards is unavailable to every component that
follows, however capable those components become. If the interpersonal layer of an utterance is
absent from the tokens, no amount of downstream modelling can restore it.

There is evidence that these systems handle this layer poorly. Benchmarking of spoken language
models finds leading end-to-end systems scoring 3.37 on paralinguistic-aware interaction against
3.18 for a cascaded pipeline that transcribes the query and discards delivery entirely, with two
systems scoring below the pipeline (Yang et al., 2026). Audio language models have been shown to
follow the words over the voice when the two conflict (Pang et al., 2026). And safety behaviour is
exposed through the same channel, with attacks that hold transcript content fixed and vary only
delivery succeeding roughly nine times more often than neutral delivery (Qian and Li, 2026). The
applications with the least tolerance for misreading interpersonal signals, including assistive and
human-robot settings, are the ones where this matters most (Cao et al., 2025).

Those are behavioural observations. They establish that something is wrong without establishing
where. A system can fail at this because the information never reached it, or because the
information reached it and was ignored. The two look identical from outside and they call for
different remedies. Nothing downstream can recover what was never encoded, whereas better modelling
can attend to what was encoded and overlooked.

This dissertation takes the first possibility and pursues it through three nested questions. Whether
the contrast is present in speech representations at all once the words are held constant. How much
of it the representation deployed systems consume retains. And at which stage of that pipeline the
remainder is lost. Each question is worth asking only if the previous one is answered
affirmatively, and it is the third where this study departs from the current literature.

## 1.2 The gap

Two literatures approach these questions, and each settles one of them without reaching the third.

Probing work has established that speech representations carry pragmatic and affective information
that text discards, and the closest precedent probes self-supervised models on prosody-related tasks
including sarcasm (Lin et al., 2022). That work compares utterances whose words differ, so a probe
succeeding on it may be exploiting word choice rather than delivery. The general claim that speech
beats text is well supported. The specific claim that speech carries meaning the words cannot convey
requires holding the words constant, which is a stricter test.

Work on discrete tokenisation has established that quantisation is lossy and that prosodic and
paralinguistic content suffers most (Mousavi et al., 2026; Guo et al., 2025), and affect
specifically has been shown to degrade when speech is passed through neural codecs (Ren et al.,
2024). That literature generally compares a continuous representation against a token stream and
attributes the difference to discretisation. But those two conditions differ in several respects at
once, including architecture, training objective, frame rate and how features are summarised. The
attribution to quantisation is therefore an inference from an uncontrolled comparison rather than a
measurement of the quantisation step itself. Several recent proposals aim to preserve prosody by
redesigning codebooks (Qian et al., 2025; Sanders et al., 2025), which presumes the attribution is
correct.

## 1.3 Contribution

This dissertation makes four contributions.

The first is a lexically controlled probing design. A corpus of 873 clips was assembled from
approximately 7,310 hours of political podcast audio, each clip containing one of eight short phrases
whose pragmatic force varies while their wording does not. Each clip was annotated for interpersonal
stance and, independently, for arousal. Because the word is fixed within each contrast, a probe that
separates the classes cannot be reading lexical content, and because arousal is labelled separately
the design can test whether stance reduces to vocal energy.

The second is a decomposition of the pipeline into stages. Rather than comparing a continuous
encoder against a token stream, this study probes each codec immediately before and immediately after
quantisation, on identical forward passes with identical pooling, so that the rounding step is the
only difference between the two conditions. This requires establishing which vectors are commensurate
inside a residual quantiser [3.5]. The decomposition is run on two codecs of different design.

These first two contributions are not independent, and the dependence is what licenses the result. A
stage decomposition run on an uncontrolled task would show where sensitivity to something is lost,
and for a codec the most likely something is phonetic or lexical detail, which such a system is built
to preserve and which would say nothing about the interpersonal layer. Because the word is fixed
across every contrast, the margins the decomposition assigns to each stage are margins on delivery.
The lexical control is therefore what makes the decomposition a measurement of pragmatics rather than
of audio fidelity in general, and neither contribution would support the conclusion without the
other.

The third follows from what that decomposition shows. The loss is concentrated in the codec encoder
rather than at quantisation, and what survives is traceable to a component introduced for unrelated
reasons, which reframes the problem from a limit imposed by rounding to a consequence of a chosen
training objective.

The fourth is the reporting of three hypotheses that were tested and not supported, alongside the
findings that were. A training-free corroborating measure returned a null against its correct
baseline, a proposed mechanism linking these representations to safety failures did not hold, and an
apparent asymmetry between the two annotated axes proved to be a property of the summary rather than
of the representation [Ch.4, Ch.6].

## 1.4 Research questions and hypotheses

Three questions organise the study.

**RQ1.** Is interpersonal pragmatic force recoverable from speech representations when lexical
content is held constant?

**RQ2.** How much of it is retained by the representation that deployed speech-to-speech systems
consume?

**RQ3.** Which stage of the pipeline is responsible for whatever is lost?

Five hypotheses were formed in advance.

**H1.** Human listeners recover more stance from audio than from the transcript, which is a premise
check rather than a finding, and a negative result here would end the study.

**H2.** Stance is linearly decodable from continuous speech representations under lexical control.

**H3.** The deployed discrete representation retains substantially less of it than the continuous
representations do.

**H4.** The loss is principally attributable to quantisation, on the grounds that discretisation is
the only step in the pipeline capable of rendering two distinct inputs identical.

**H5.** Stance decodability is not reducible to arousal, and survives when energy is held constant.

H1, H2, H3 and H5 are supported. **H4 is not**, and its failure is the most consequential result
reported here, because the remedies currently proposed in the literature are addressed to the stage
it names.

## 1.5 Structure

Chapter 2 situates the study in the literatures on discrete speech tokens, probing of speech
representations, and the pragmatics of same-word contrasts, and traces the codec design lineage that
the stage decomposition later measures. Chapter 3 describes the corpus, the two-tier annotation
scheme, the premise check, the six representations and the probing protocol, including the
pre-committed choices of readout and chance level. Chapter 4 reports seven analyses. Chapter 5
interprets them, with attention to what the results cannot support. Chapter 6 states the limitations
and sets out a programme of repair that follows from where the loss was found.
