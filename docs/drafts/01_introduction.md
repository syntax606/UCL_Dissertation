# Chapter 1: Introduction

## 1.1 The same word, three different moves

A warm *yeah*, a grudging *yeah* and a mocking *yeah* are the same transcript and three
different conversational moves. That observation is the instrument this dissertation is
built around, because it separates two things that are otherwise inseparable.

Compression discards signal. That is uncontroversial and uninformative. The question
worth asking is whether a representation loses *meaning* while keeping the sound it is
carried in, and no comparison between utterances with different words can answer it,
because a probe that separates them may be reading vocabulary. Holding the lexical item
constant and varying only delivery removes that route. Any separation that survives is
delivery-borne by construction, and any loss localised to a pipeline stage is a loss of
pragmatic rather than phonetic sensitivity.

The class of words that makes this possible is also the class that matters most for the
systems under study. Response tokens such as *yeah*, *okay* and *right* carry no
dictionary meaning, functioning as continuers that signal a turn is passing rather than
being taken (Schegloff, 1982), and conveying the speaker's stance through phonetic form,
prosodic shape and placement in the flow of talk (Gardner, 2001), functions distinguished in spontaneous
dialogue by delivery rather than by wording (Gravano et al., 2012). Human listeners
recover the distinction from audio well above chance though not reliably, at 0.73 against
a three-way chance of 0.33 in the premise check reported here [4.1].

Spoken interaction with machines is meanwhile moving from turn-taking exchange to
full-duplex conversation. The Moshi report states the limitation it was built to remove,
that prior systems "rely on a segmentation into speaker turns, which does not take into
account overlapping speech, interruptions and interjections" (Défossez et al., 2024), and
its training explicitly includes backchannelling in both streams. Both streams are
encoded by the same neural codec, which passes the waveform through an encoder and then
quantises the result before anything reaches the language model. The codec therefore
stands between the speaker and every component downstream, in two distinct stages, and
those stages turn out not to cost the same. What the codec declines to represent is
unavailable thereafter, however capable the model behind it.

There is converging evidence that such systems handle this channel poorly, including
end-to-end models scoring below a cascaded pipeline that discards delivery entirely (Yang
et al., 2026), models following lexical content over acoustic evidence when the two
conflict (Pang et al., 2026), and safety behaviour exposed through delivery alone (Qian
and Li, 2026). Behavioural observations of this kind underdetermine the diagnosis. A
system can fail because the information never reached it or because it reached it and was
ignored, the two are indistinguishable from outside, and they admit different remedies.
Better modelling recovers information that is present and unused. Nothing downstream
recovers information that was never encoded.

## 1.2 What existing work cannot separate

Two lines of work bear on this and each leaves the other half open.

One establishes that speech representations carry pragmatic and affective content that
text discards, probing self-supervised encoders on prosody-related tasks and
characterising where in a layer stack such content sits (Pasad et al., 2021). These
studies typically compare utterances whose words differ, often on acted corpora, so a
probe succeeding under those conditions may be reading word choice rather than delivery.

The other establishes that discretisation is lossy and that paralinguistic content
suffers disproportionately (Mousavi et al., 2026). The standard comparison places a
continuous encoder against a token stream and assigns the difference to quantisation.
Those two conditions differ simultaneously in architecture, training objective, frame
rate and feature construction, so the attribution rests on an uncontrolled contrast
rather than on a measurement of the discretisation step. Several proposals nonetheless
intervene at the codebook on the strength of it.

Neither line isolates the variable it needs. The first varies delivery and wording
together. The second varies quantisation and four other things together. In both cases
the confound is a property of the comparison rather than of the representations, which
means it is removable by design.

## 1.3 Approach

Both confounds are removed jointly, and the two moves are not independent.

**A lexical control.** A corpus of 873 clips of naturalistic political podcast audio,
across 32 shows and 753 episodes, each containing one of eight short phrases whose
pragmatic force varies while their wording does not. Each clip carries a fine-grained
pragmatic function tag, from which interpersonal stance is derived, and separately and
without conditioning on that tag, a judgement of arousal. Because the word is fixed within
every contrast a probe cannot be reading lexical content, and because arousal is labelled
independently the design tests directly whether stance reduces to vocal energy.

**A stage decomposition.** Rather than comparing a continuous encoder against a token
stream, each codec is probed immediately before and immediately after quantisation, on
identical forward passes with identical pooling, so the rounding step is the only
difference between conditions. This is run on three codecs of independent design, one
distilled from a self-supervised teacher and two purely acoustic, two of which share a
frame rate and differ in encoder architecture.

The dependence between the two moves is what licenses the result. A stage decomposition
on an uncontrolled task localises the loss of *something*, and for a codec the likely
something is phonetic detail, which such a system is built to preserve and which says
nothing about the interpersonal layer. Holding the word fixed makes the cost assigned to
each stage a cost in delivery specifically.

## 1.4 Research questions and hypotheses

**RQ1.** Is interpersonal pragmatic force recoverable from speech representations when
lexical content is held constant?

**RQ2.** How much of it is retained by the representation deployed systems consume?

**RQ3.** Which stage of the pipeline is responsible for what is lost, and why?

Five hypotheses were formed before the analyses.

**H1.** Human listeners recover more stance from audio than from the transcript. A
premise check rather than a finding, and a negative result ends the study.
**H2.** Stance is linearly decodable from continuous representations under lexical
control.
**H3.** The deployed discrete representation retains substantially less of it.
**H4.** The loss is principally attributable to quantisation, on the grounds that
discretisation is the only step capable of rendering two distinct inputs identical.
**H5.** Stance decodability is not reducible to arousal and survives when energy is held
constant.

H1, H2, H3 and H5 are supported. **H4 is not.** Its falsification redirected the study,
and four further hypotheses were formed and tested afterwards.

**H6.** The measured loss reflects the order-free readout rather than the representation.
**H7.** Variable-frame-rate tokenisers, which allocate tokens to linguistic units rather
than to a fixed clock, retain more.
**H8.** The segmentation itself carries stance, through token count, rate and duration.
**H9.** Order retention tracks whether the encoder has an architectural mechanism for
representing time, rather than tracking frame rate.

H6, H7 and H8 are not supported. H9 was formed after an anomalous result on one codec and
was then tested on a fourth codec not previously included, which is the strongest form of
support available without retraining anything.

## 1.5 Contributions

**A lexically controlled diagnostic corpus** of 873 clips of naturalistic spontaneous
speech across eight target phrases, annotated on two independently judged axes.

**A stage-resolved measurement of codec loss**, replicated on three codecs of independent
design, showing the encoder to be the dominant contributor in every case and quantisation
to cost little or nothing.

**An account of what is lost.** Not acoustic detail, since the codecs recover
hand-crafted acoustic cues more faithfully than the model one of them distils from, but
temporal organisation, shown by two measurements that share no machinery.

**A controlled test of why.** Two codecs matched at 75 Hz and differing in encoder
architecture differ in how much frame order contributes, which excludes sampling density
as the mechanism and yields a prediction that the next codec added can falsify.

**Reporting of four unsupported hypotheses.** H4 from the first round and H6 to H8 from the
second, which is why later chapters describing only the second round refer to three. And of
a measurement problem found in the study's own pipeline, namely that fold assignment alone moves scores by as much as several
of the differences reported in this literature [3.7].

## 1.6 Structure

Chapter 2 situates the study in the literatures on discrete speech tokens, probing of
speech representations, and the pragmatics of same-word contrasts. Chapter 3 describes the
corpus, the annotation scheme, the representations, the readouts and the probing protocol.
Chapter 4 reports five analyses. Chapter 5 makes three moves, locating the loss upstream
of the tokens, establishing that what is lost is organisation rather than fidelity, and
identifying the architectural property that predicts it. Chapter 6 states the limitations
and sets out a programme of repair.
