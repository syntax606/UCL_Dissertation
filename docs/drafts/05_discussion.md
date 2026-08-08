# Chapter 5: Discussion

*(Draft. Target budget ~1,200 words. Figures are the settled single-run values reported in
[Ch.4]. Cross-references marked [Ch.x].)*

## 5.1 What the results establish

Three findings carry this chapter. Pragmatic stance is linearly decodable from continuous speech
representations when the lexical item is held constant, and it survives every control applied to
it. The representation that deployed speech-to-speech systems consume retains substantially less
of it. And the loss occurs earlier in the pipeline than the field's attention has been directed,
which changes what would count as a remedy.

## 5.2 The loss is upstream of the tokens

The study was designed on the assumption that discretisation was the culprit. Decomposing the
pipeline into controlled steps does not support that assumption.

Between WavLM at +0.244 and Mimi's quantised output at +0.099, two things happen. The codec
encoder and its distillation account for 0.112 of the loss. Quantisation itself accounts for
0.034. The step that converts continuous values into a finite set of symbols, and which is the
only step in the pipeline capable of making two distinct inputs literally identical, turns out to
be the smaller contributor by a factor of roughly three.

That pattern replicates on an independent architecture. DAC, a purely acoustic codec, loses 0.182
at its encoder and gains 0.025 at quantisation, so in that system the discretisation step is
marginally beneficial. Two codecs with different objectives, frame rates and codebook geometries
agree that the encoder is where the information goes.

This bears directly on two recent proposals. ProsodyLM (Qian et al., 2025) introduces explicit
word-level prosody tokens and Segmentation-Variant Codebooks (Sanders et al., 2025) quantises at
multiple segmental units. Both are codebook-level interventions aimed at a prosody problem. If the
majority of the loss precedes quantisation, then a redesigned codebook operates on information the
encoder has already declined to represent, and the ceiling on what it can recover is set upstream
of the change. The disagreement is specific and falsifiable, and it follows from measurement
rather than from argument.

A second design family is better placed by the same reasoning, which is worth saying because it
converts the point from a criticism into a prediction. X-Codec (Ye et al., 2024) injects teacher
features before quantisation rather than only supervising after it, and one of the two
emotion-preserving codecs published in 2026 modulates the latent before quantisation as well (Shi et
al., 2026b). Those interventions act at the stage the present decomposition identifies as dominant.
The measurements here therefore predict an ordering between the two families rather than a verdict
on any single system, and that ordering is testable on a common corpus.

## 5.3 What is stable and what is not

The encoder loss is a property of the representation. Measured under three readouts it holds at
0.116 and 0.121, a difference inside run-to-run variation from permutation sampling.

The quantisation loss is not. Across the same readouts it ranges from +0.056 to -0.036, a swing
large enough to change its sign. Its apparent magnitude is therefore a joint property of the
representation and the way that representation is summarised, and any single reported figure is
contingent on a choice that is rarely stated.

This instability is itself informative rather than merely inconvenient. Sun et al. (2026) observe
the same signature from a different direction, finding that continuous features perform stably
across layer configurations while discrete ones fluctuate, and treating that fluctuation as
evidence of information loss in its own right. The present results reproduce that contrast across
readouts rather than layers. WavLM moves by 0.009 across the three, Mimi by 0.056. A representation
whose measured content depends heavily on how it is read is one in which the signal is thin, and
that observation is available without committing to any particular readout being correct.

## 5.4 The preservation that does exist is incidental

Distillation is the one component that measurably improves retention, and it was introduced for
something else.

The Moshi report states that Mimi "uses distillation to transfer non-causal, high-level semantic
information into the tokens produced by a causal model", and explains the decision to fold this
into a single tokeniser on the grounds that "generating acoustic and semantic tokens with separate
encoders represents a non-negligible computational burden". The motivation is semantic content and
computational cost. Prosody, affect and interpersonal meaning are absent from it.

The outcome diverges from the intention in both directions. Shi et al. (2026) show that what
distillation from WavLM transfers is phonetic rather than semantic knowledge, so the stated target
was not reached. And the results here show that the distilled codebook is the only part of Mimi
carrying appreciable pragmatic stance, at 0.402 against five of the seven acoustic codebooks that
are statistically indistinguishable from chance, so a target nobody was aiming at was reached
instead. A student trained to match a teacher's representations inherits what that teacher happens
to encode, and WavLM encodes stance.

The consequence is what makes this worth stating. An unintended benefit is an unprotected one. No
loss term optimises for it, the Moshi ablations do not evaluate it, and the metrics routinely
reported for codecs are not sensitive to it. Reconstruction quality, word error rate and perceptual
scores would be unchanged if it disappeared. A successor system could substitute the teacher, tune
distillation toward transcription accuracy, or remove it for a cheaper alternative, and pragmatic
retention would fall without registering as a regression on any reported benchmark.

That claim needs one qualification, and the qualification turns out to sharpen it. Affect under
codecs has been measured. EMO-Codec (Ren et al., 2024) resynthesises speech through legacy and
neural codecs and finds emotion recognition degraded afterwards. But it is an evaluation study
rather than a metric reported during development, it works through resynthesis and downstream
recognition rather than on the representation, and it measures categorical emotion on acted corpora.
The results here bear on that last point directly. Stance and arousal are separable in this data, and
Mimi retains roughly three quarters of the arousal signal against under a third of the stance signal
[Ch.4]. A measure supervised on categorical emotion labels, which are substantially arousal-loaded,
would therefore register the axis that survives more readily than the axis that does not. The same
concern applies to the emotion-preserving objectives now being proposed. Making affect a training
target is the right move, and which affective quantity supervises it determines whether the
interpersonal layer is among what improves.

It also reframes the problem usefully. Were the loss caused by discretisation it would be close to
irreducible, since rounding is rounding. Because it is caused by a training objective, and
objectives are chosen, the finding is a design observation rather than a limit.

## 5.5 What these results cannot say

Three hypotheses were tested and not supported, and reporting them constrains the claims above.

The contrast-preservation score is a null. Against the correct within-cell majority baseline of
0.670 every representation falls below, so the measure does not corroborate the probing results and
is reported as a failure rather than as weak agreement [Ch.4].

The proposal that these representations encode activation and are read downstream as intent was
tested directly by holding arousal constant. Stance survives at fixed arousal in every
representation, so the two axes are related but not interchangeable, and the stronger claim that
such systems mistake loudness for stance is not made here. What the data supports is an asymmetry
of availability rather than a confusion, which offers a candidate mechanism for the delivery-driven
vulnerabilities documented by Qian and Li (2026) without demonstrating that any deployed system
exhibits it.

More broadly, this study measures whether information is linearly decodable from a frozen
representation. It does not measure whether a system uses that information, and it addresses
comprehension rather than generation. The defensible bridge to deployment is a necessary condition.
A system cannot act on what its input representation does not carry, so these probes bound what any
downstream model built on these tokens could achieve, however capable that model is. That bound is
worth knowing alongside VoxParadox (Pang et al., 2026), which documents audio language models
failing to use paralinguistic information that is present. The two failure modes are distinct and
the remedies differ. Better modelling can address information that is available and ignored.
Nothing downstream can address information that was never encoded.
