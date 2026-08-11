# Chapter 5: Discussion

*(Draft. Figures are the values reported in [Ch.4]. Cross-references marked [Ch.x].)*

## 5.1 The loss is upstream of the tokens

The study was designed on the assumption that discretisation was the culprit. Decomposing the
pipeline into controlled steps does not support that assumption. The step that converts continuous
values into a finite set of symbols, and the only step capable of making two distinct inputs
literally identical, is the smaller contributor by a factor of roughly three, and on a second codec
of independent design it is marginally beneficial [4.6]. Two codecs with different objectives, frame
rates and codebook geometries agree that the encoder is where the information goes.

That the two costs behave differently is itself informative. The encoder cost holds across readouts
while the quantisation cost ranges from +0.056 to −0.036, a swing large enough to change its sign
[G.2]. Sun et al. (2026) observe the same signature from a different direction, finding continuous
features stable across configurations while discrete ones fluctuate, and treating that instability as
evidence of information loss in its own right. A representation whose measured content depends
heavily on how it is read is one in which the signal is thin.

This bears directly on two recent proposals. ProsodyLM (Qian et al., 2025) introduces explicit
word-level prosody tokens and Segmentation-Variant Codebooks (Sanders et al., 2025) quantises at
multiple segmental units. Both are codebook-level interventions aimed at a prosody problem. If the
majority of the loss precedes quantisation, a redesigned codebook operates on information the encoder
has already declined to represent, and the ceiling on what it can recover is set upstream of the
change. A second design family is better placed by the same reasoning, since X-Codec (Ye et al.,
2024) injects teacher features before quantisation and one of the two emotion-preserving codecs
published in 2026 modulates the latent before quantisation as well (Shi et al., 2026b). The
measurements predict an ordering between the two families rather than a verdict on any single system,
and that ordering is testable on a common corpus.

## 5.2 What is lost is not the acoustics

The natural reading of a codec losing pragmatic content is that it discards the acoustic detail that
content is built from. That reading is wrong, and the measurement is unambiguous.

Recovering hand-crafted acoustic cues from each rung of the pipeline, the codecs do **better** than
WavLM on every group except one, reaching 153 per cent of WavLM on the contour features that stance
is built from and 158 per cent on voice quality, using half the feature dimensions [4.7]. Mimi has
not thrown the prosody away. It represents it more faithfully than the model that decodes stance best.

Two further results point the same way. A supervised transcription objective is the most linguistic
in the study and ought, on the account in [2.2], to strip paralinguistic content from its upper
layers. Whisper shows no such decline, plateaus across its top third, and leads the within-word table
at 0.672 [4.3, 4.5], which is consistent with prior findings that ASR encoders retain paralinguistic
content (Gong et al., 2023; Ma et al., 2026). And 88 hand-crafted acoustic functionals outperform the
deployed token stream, at +0.104 against +0.070 [4.2]. The representation with the most acoustic
detail is among the worst at stance, and the two trained on linguistic objectives are the best.

So the binding constraint is not fidelity. It is whether the acoustics have been organised into a
space in which an interpersonal category is linearly separable. That distinction is not a technicality,
because it changes what a remedy has to do. Storing prosody more faithfully is what a redesigned
codebook achieves, and the codec already stores it more faithfully than WavLM. The problem is not
that the cues are absent but that nothing has arranged them into a form from which stance can be read.

## 5.3 The organisation that does survive is incidental

If organisation is the constraint, the question becomes where any of it in Mimi came from. The answer
is a component added for something else.

The Moshi report states that Mimi "uses distillation to transfer non-causal, high-level semantic
information into the tokens produced by a causal model", and explains folding this into a single
tokeniser on the grounds that "generating acoustic and semantic tokens with separate encoders
represents a non-negligible computational burden". The motivation is semantic content and
computational cost. Prosody, affect and interpersonal meaning appear nowhere in it.

The outcome diverges from the intention in both directions. Shi et al. (2026) show that what
distillation from WavLM transfers is phonetic rather than semantic knowledge, so the stated target was
not reached. And the distilled codebook is the strongest carrier of pragmatic stance inside Mimi at
0.402, with the seven acoustic codebooks adding nothing to it and reaching only 0.352 alone [4.5], so
a target nobody was aiming at was reached instead. A student trained to match a teacher's
representations inherits how that teacher organises its inputs, and that is precisely the quantity
[5.2] identifies as scarce.

An unintended benefit is an unprotected one. No loss term optimises for it, the Moshi ablations do not
evaluate it, and the metrics routinely reported for codecs are not sensitive to it. Reconstruction
quality, word error rate and perceptual scores would be unchanged if it vanished, so a successor
system could substitute the teacher or drop the objective and every reported number would improve.

Affect under codecs has been measured, which qualifies that claim and then sharpens it. EMO-Codec
(Ren et al., 2024) resynthesises speech through legacy and neural codecs and finds emotion recognition
degraded afterwards. But it is an evaluation study rather than a figure reported during development,
it works through resynthesis and downstream recognition rather than on the representation, and it
measures categorical emotion on acted corpora. Stance and arousal are separable in this data, and Mimi
retains roughly three quarters of the arousal signal against under a third of the stance signal
[Ch.4], with arousal carried most by voice quality and stance by contour dynamics [4.7]. A measure
supervised on categorical emotion labels, which are substantially arousal-loaded, would therefore
register the axis that survives more readily than the axis that does not. The same concern applies to
the emotion-preserving objectives now being proposed. Making affect a training target is the right
move, and which affective quantity supervises it determines whether the interpersonal layer is among
what improves.

This also reframes the problem usefully. Were the loss caused by discretisation it would be close to
irreducible, since rounding is rounding. Because it is caused by a training objective, and objectives
are chosen, the finding is a design observation rather than a limit.

## 5.4 What these results cannot say

Three hypotheses were tested and not supported, and reporting them constrains the claims above.

A training-free contrast-preservation measure does not discriminate, since every representation falls
inside the interval between its two defensible baselines [G.5]. The proposal that these
representations encode activation and are read downstream as intent does not hold, because stance
survives at fixed arousal everywhere tested [4.4]. What the data supports is an asymmetry of
availability rather than a confusion, which offers a candidate mechanism for the delivery-driven
vulnerabilities documented by Qian and Li (2026) without demonstrating that any deployed system
exhibits it. And an earlier account of why arousal survives and stance does not, resting on level cues
being reconstructive, is refuted by [4.7], where the codec retains every cue group and the level cues
turn out not to be the arousal carrier.

Decodability above chance is also not decodability at a useful level. On the sixty clips human
annotators judged, the best model condition reaches 0.533 against their 0.730, and a human reading
only the transcript reaches 0.650, exceeding every model condition including the one given both
modalities [4.1]. The claims here concern what these representations carry relative to one another
and to chance, not what they carry relative to a listener.

More broadly, this study measures whether information is linearly decodable from a frozen
representation. It does not measure whether a system uses that information, and it addresses
comprehension rather than generation. The defensible bridge to deployment is a necessary condition. A
system cannot act on what its input representation does not carry, so these probes bound what any
downstream model built on these tokens could achieve, however capable that model is. That bound is
worth knowing alongside VoxParadox (Pang et al., 2026), which documents audio language models failing
to use paralinguistic information that is present. The two failure modes are distinct and the remedies
differ. Better modelling can address information that is available and ignored. Nothing downstream can
address information that was never organised into a usable form.
