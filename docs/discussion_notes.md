# Discussion notes

Working material for Chapter 5. Each section states what the data supports, then how far
the argument can be pushed before it stops being defensible.

## 1. The loss is selective, not general

The headline finding is not that Mimi degrades speech. It is that Mimi degrades one kind of
information far faster than another.

Expressed as the share of WavLM's own margin that survives, which normalises for stance
being three-way and arousal binary.

| Rung | stance | arousal |
|---|---|---|
| WavLM, continuous teacher | 100% | 100% |
| Mimi pre-quantisation | 54% | 77% |
| Mimi post-quantisation | 42% | 53% |
| Mimi unigram histogram | 29% | 74% |

Mimi's pipeline retains roughly three quarters of the arousal signal and under a third of
the stance signal. Same clips, same probe, same representations, one variable changed.

The interpretation is a design consequence rather than a defect. A codec is optimised so
that audio can be reconstructed and still sound right. Energy and activation are directly
reconstructive, so they must be preserved. Whether a smile is warm or contemptuous is not
required to reconstruct a plausible waveform, so it need not be. The encoder is doing its
job, and its job never included the interpersonal layer.

The readout is selective in the same way. The histogram costs stance a further 13 points
while leaving arousal essentially untouched, so counts are an adequate summary of a physical
property and a poor summary of an abstract one.

**Caveat to state.** Raw margins across the two tasks are on different scales and must not
be compared directly. Only the proportional retention is comparable, because each task is
normalised against its own ceiling.

## 2. The bottleneck is upstream of the tokens

Decomposing the gap into controlled steps, with each margin taken over that configuration's own
permutation null. All figures below come from a single run so they are internally consistent.

| Representation | margin | encoder costs | quantisation costs |
|---|---|---|---|
| WavLM, continuous | +0.244 | | |
| DAC, purely acoustic | +0.087 | 0.182 | -0.025 |
| Mimi, WavLM-distilled | +0.099 | 0.112 | +0.034 |

Quantisation, the step this study set out to indict, is the smallest contributor in both codecs
and in DAC it is slightly negative. Most of the loss happens inside the codec encoder, before
anything is discretised, and that pattern replicates across two independent architectures.

The quantisation figure is also not a stable quantity. Measured under three readouts it ranges
from +0.056 to -0.036, enough to change sign, while the encoder cost holds at 0.116 against 0.121
across the same readouts. So the encoder loss is a property of the representation and the
quantisation loss is a property of the representation and the measurement together. Sun et al.
(2026) report the same signature from a different direction, noting that continuous features are
stable across configurations while discrete ones fluctuate, and treating that instability as
evidence of information loss in its own right.

This is the point of contact with the literature. ProsodyLM (Qian et al., 2025) proposes
explicit word-level prosody tokens and Segmentation-Variant Codebooks (Sanders et al., 2025)
proposes quantising at multiple segmental units. Both are codebook-level remedies for a
prosody problem. If most of the loss occurs before quantisation, a redesigned codebook
cannot recover information the encoder already declined to represent. That is a specific,
falsifiable disagreement with two recent proposals, and it comes from measurement rather
than argument.

It also changes the engineering implication. More codebooks or finer quantisation would
address 18 percent of the problem.

## 3. The preservation is incidental, and therefore unprotected

Distillation is the one component that measurably helps, and it was not added for this.

The Moshi report states the purpose plainly. Mimi "uses distillation to transfer non-causal,
high-level semantic information into the tokens produced by a causal model, allowing for streaming
encoding and decoding of semantic-acoustic tokens", and the reason for folding it into a single
tokeniser rather than running two was cost, since "generating acoustic and semantic tokens with
separate encoders represents a non-negligible computational burden". Prosody, emotion, stance and
the interpersonal layer appear nowhere in the motivation.

So the mechanism is accidental twice over. The stated target was semantic content, meaning lexical
meaning, and Shi et al. (2026) show that what distillation from WavLM actually transfers is
phonetic knowledge rather than semantic. The designers missed their own target. And the data here
shows the distilled stream is the only part of Mimi carrying appreciable pragmatic stance, a target
nobody was aiming at. It arrives because a student trained to match a teacher's representations
inherits whatever that teacher happens to encode, and WavLM encodes stance.

Two lines of evidence support the attribution, and they are not equally strong. Across codecs,
distilled Mimi retains roughly twice the stance that undistilled DAC does, which is suggestive but
confounded by frame rate, codebook geometry, architecture and training data. Within Mimi, codebook
0 is the best single codebook at 0.402 while five of the seven acoustic codebooks are
indistinguishable from chance, and here architecture, frame rate, training data and audio are all
held constant, so the only systematic difference is the distillation objective. The internal
comparison is the one to lean on.

The consequence is what makes this worth reporting rather than a footnote. An accidental benefit is
an unprotected one. No loss term optimises for it, no ablation in the Moshi report evaluates it,
and no standard codec metric is sensitive to it. Reconstruction quality, word error rate and
perceptual scores would all be unaffected if it disappeared. A successor system could swap the
teacher, drop distillation for something cheaper, or tune it toward transcription accuracy, and the
pragmatic retention would go with it while every published number improved.

A formulation for the write-up.

> Mimi's distillation objective was introduced to transfer high-level semantic information into a
> causal tokeniser at acceptable computational cost. It was not motivated by paralinguistic
> preservation, and the Moshi report does not evaluate it in those terms. Nevertheless it is the
> only component of the tokeniser that measurably retains pragmatic stance. The preservation is
> therefore incidental rather than designed, and because no standard codec metric is sensitive to
> it, it could be removed or degraded in a successor system without appearing as a regression on
> any reported benchmark.

## 4. The security argument, stated at the strength the data allows

**What was hypothesised.** That systems built on these representations may encode activation
and treat it as though it were intent, so that loudness stands in for emotional stance. If
true, safety behaviour gated on inferred affect could be driven by delivery rather than by
what a speaker actually means.

**What the test showed.** Not supported in that form. Holding arousal constant does not
remove the stance signal in any representation, Mimi included. The two axes are partly
entangled, with margins falling by a quarter to a third, but stance is not reducible to
arousal. This should be reported, not omitted.

**What remains defensible.** An asymmetry of availability rather than a confusion. Mimi
carries rich information about activation and impoverished information about stance. Any
downstream component inferring speaker state from that representation is working with a loud
signal and a faint one, and will be dominated by the loud one in proportion to how much
signal each carries.

That asymmetry is a plausible mechanism for a documented vulnerability. Qian and Li (2026,
arXiv 2607.26541) held transcript content fixed and varied delivery, which is the same
control used here, and found jailbreak success on Qwen2-Audio of 38 of 95 for panic, 35 of
95 for anger and 32 of 95 for fast delivery, against 4 of 95 for neutral. Emotional delivery
in audio alone reached 44 of 95 against 11 of 95 for emotional text. Every effective preset
is a high-arousal one. StyleBreak (AAAI 2026) reports attack success improvements of 7.1 to
22.3 percent from paralinguistic style transformation.

**Where the argument stops.** This study measures representational availability. It does not
show that any deployed system uses arousal for safety decisions, and it runs no attack. The
chain from asymmetry to vulnerability is a hypothesis consistent with the jailbreak
literature, not a demonstration. State it as such.

## 5. The ceiling argument, which is how the motivation stays rigorous

The study cannot speak to conversational competence, since it measures whether information
is linearly decodable from a frozen representation and not whether a system uses it well,
and it touches comprehension only, never generation.

The defensible bridge is a necessary-condition claim. A system cannot act on what its input
representation does not carry, so these probes establish a ceiling on what any downstream
model built on these tokens could do with stance, however good the modelling.

Two supports for the premise that these systems already mishandle this information.
VoxParadox (Pang, Chaubey and Soleymani, 2026, arXiv 2605.27772) finds audio LLMs following
language-implied answers over acoustic ground truth, with paralinguistic cues degrading in
deeper encoder layers and at the encoder to LLM interface, and being ignored even when
present. Wang et al. (2025, arXiv 2508.07273) argue speech LMs lack empathetic reasoning
because training data does not combine context with paralinguistic cues.

VoxParadox is worth positioning against directly. It documents information that is present
and unused. This study documents information that is absent. A better language model can fix
the former. Nothing downstream can fix the latter.

## 6. Where the contrast lives

WavLM peaks at layer 20 of 24 and falls away above it, consistent with upper layers
abstracting toward linguistic content and shedding paralinguistics. Whisper plateaus across
its top third instead.

The Whisper result deserves more attention than it has had. A supervised transcription
objective costs almost nothing here, 0.564 against WavLM's 0.573. The expectation from the
literature was that training to transcribe would strip paralinguistic information from the
encoder. It largely does not, and that is a small negative result worth reporting.

Inside Mimi, what little survives sits in codebook 0, the WavLM-distilled stream, at 0.402.
Five of the seven acoustic refinement codebooks are not significant. Chapter 2 predicted the
opposite on the grounds that codebook 0 is phonetic rather than semantic, and section 2.3.3
now reports that as a corrected expectation, diagnosing the error as a category mistake,
since the semantic versus phonetic axis concerns which words were said and pragmatic force
is orthogonal to it.
