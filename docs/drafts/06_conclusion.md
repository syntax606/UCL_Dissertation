# Chapter 6: Conclusion, Limitations and Future Work

*(Draft. Target budget ~800 words, currently over. Limitations condensed from `docs/limitations.md`,
which holds the full treatment and is the appendix source. Cross-references marked [Ch.x].)*

## 6.1 Conclusions

This study asked whether pragmatic contrast survives the representations that speech-to-speech
systems actually consume, and if not, where it is lost. Three answers follow from the measurements.

Pragmatic stance is linearly decodable from continuous speech representations when the lexical item
is held constant, and it survives every control applied to it [Ch.4]. The representation deployed
systems consume retains a fraction of that, and under its deployed summarisation falls below a
discourse-text baseline once the word is held constant. And the loss is not where this study expected to find it. The codec encoder costs
roughly three times what quantisation does, the same ordering appears on an independently designed
acoustic codec where quantisation is marginally beneficial, and what survives inside Mimi is carried
mainly by the codebook distilled from WavLM, a component introduced for semantic transfer and
computational economy rather than for anything paralinguistic [Ch.5].

## 6.2 Limitations

Three hypotheses were tested and not supported, and reporting them is part of the result. The
contrast-preservation score falls inside the interval between its two defensible baselines, 0.545 and
0.670, in every representation, so it does not discriminate and is not corroboration. The proposal
that these representations encode activation and are read downstream as intent does not hold, because
stance survives at fixed arousal everywhere tested. And an apparent dissociation between the two axes
reversed once the readout was varied, so it was a property of the summary rather than of the
representation.

Five constraints bound the positive findings, and the reasoning behind each is in Appendix [F]. The
0.112 attributed to the codec encoder is an upper bound, because WavLM contributes twice Mimi's
pooled dimensionality, while the 0.034 for quantisation is clean. The attribution to distillation is
associational rather than causal, and the decisive experiment would train one codec with and without
the objective. Linear probing measures accessibility rather than presence, though across six probe
capacities no configuration recovers more than +0.025 against a gap of roughly 0.14, so accessibility
bounds rather than explains the result. The identity control is held-out shows rather than unseen
speakers, since the corpus carries show labels only.

The fifth concerns the interpretation offered in [Ch.5]. A mechanism was proposed there for why
arousal survives compression and stance does not, resting on level cues being reconstructive and
contour cues not. Probing the cue groups directly supports half of it and refutes the other half
[4.5, 5.4]. Stance is carried by dynamics rather than levels, as proposed, but voice quality rather
than level is the strongest arousal carrier, which the proposal had the wrong way round. The
asymmetry stands as a measurement and its explanation does not, and closing that gap requires probing
the codec representations for individual cues rather than probing cues and codecs separately.

## 6.3 Why the loss is worth repairing

That deployed systems handle this information poorly is established in [1.1], across behavioural
benchmarking, conflict resolution between words and voice, delivery-driven safety failures and
human-robot interaction. This section states what the present findings add to it.

The headroom is measurable rather than assumed. On the sixty clips human annotators judged, the best
model condition reaches 0.533 accuracy against their 0.730 [4.1], so these representations carry
something closer to half of what a listener recovers from the same audio. A repair programme is worth
proposing only if there is something to recover, and that is the quantity.

The findings add a specific constraint on how any of that can be addressed. A downstream model
cannot act on what its input representation does not carry, so better modelling addresses information
that is present and ignored and cannot address information that was never encoded. The distinction
matters because the two failure modes look identical from the outside.

The structural risk compounds it. Because the retention that does exist is incidental, no loss term
optimises for it and the metrics routinely reported for codecs are not sensitive to it. Reconstruction
quality, word error rate and perceptual scores would be unchanged if it vanished, so a successor
system could substitute the teacher or drop the objective and every reported number would improve.
Affect under codecs has been evaluated in its own right (Ren et al., 2024), but through categorical
emotion on resynthesised audio, and [Ch.5] gives the reason that measure would be an imperfect guard
for this particular quantity.

## 6.4 A programme for repair

Because the loss is caused by a training objective rather than by rounding, and objectives are
chosen, it is a design problem. Five steps follow from the measurements above, ordered so that each
supplies what the next needs.

**Establish causality.** Train one codec with and without a distillation term, and across teachers
that differ in how much stance they encode, converting the associational claim of [Ch.5] into a
controlled one. This is the experiment the compute available here did not permit, and every other
step assumes its outcome.

**Identify which cues are lost.** Half of this is now done. Extracting eGeMAPS from the same clips
and probing its cue groups shows stance carried by F0 and loudness dynamics and arousal by voice
quality [4.5], which refutes the mechanism [Ch.5] originally proposed. What remains is the other
half, namely which of those cues a codec actually loses. That requires predicting each cue group from
the codec representations at each rung of the ladder, rather than probing cues and codecs separately
as here, and it would say directly which properties an objective must protect. It needs no training
and reuses the corpus and features already extracted.

**Choose the teacher layer by measurement.** WavLM carries 0.573 at layer 20 and 0.490 at layer 24,
so the choice of distillation target is consequential for this contrast. Semantic distillation
conventionally takes a mid-stack layer or an average across layers, selected for alignment with
linguistic content (Zhang et al., 2024a; Jo et al., 2025). The Moshi report does not state which
WavLM layer Mimi distils from, which is itself informative, since a choice worth 0.083 on this
contrast is not one the report treats as a variable. Where the optimum sits for prosodic
properties is not settled either, since de la Fuente and Jurafsky (2024) locate suprasegmental
categories in the middle third of a twelve-layer model while the peak observed here is at layer 20 of
24. That disagreement is the reason to select a target from a probe curve on the property of interest
rather than by convention, and it is an intervention requiring no architectural change.

**Supervise the encoder on the right quantity.** Making expressivity a training target is already an
active line, pursued at the codec level through pre-quantisation latent modulation (Shi et al.,
2026b) and structured projections inside the quantiser (Meng et al., 2026), and at the system level
by Spirit-LM (Nguyen et al., 2024), which adds explicit pitch and style tokens to an interleaved
speech-text model for this purpose. The available contribution is therefore in the supervision rather
than in the mechanism, and the mechanisms that exist already act at or before the stage this study
identifies as dominant. Those objectives are supervised on categorical emotion or on style, both
substantially arousal-loaded, and the results here separate stance from arousal and find the
surviving axis is the arousal one [Ch.5]. An auxiliary objective over lexically matched pairs, same
word and opposite stance, supplies a signal that categorical labels do not, and the 873 clips
assembled here are already in that form. The prediction is specific, namely that emotion-supervised
and style-supervised objectives improve retention of the axis that was least damaged, and that a
lexically controlled contrastive term is what reaches the other one.

**Build the diagnostic that would notice.** The uninformative result in [Ch.4] is a specification for
its replacement, and the specification is now more precise than a call for more power, because the
failure was structural rather than incidental. Estimating a class centroid inside a speaker-by-word
cell makes the measure depend on cell size, which is why only 15 cells qualified and why the two
defensible baselines diverge. The minimal-pair ABX task avoids this by fixing the comparison as a
triplet, so no centroid is estimated and no cell need be large (Schatz et al., 2013). A
pragmatic-contrast analogue would present two clips of one word carrying opposing stance and a third
matched to one of them, then score whether the representation places the third nearer its own class.
That is training-free, degrades gracefully at small samples, and is cheap enough to report during
development, which is how ABX functions inside multi-level evaluation suites (Dunbar et al., 2021).
The wider precedent is a small body of prosodic benchmarks built for speech-to-speech systems
specifically, covering emphasis transfer (de Seyssel et al., 2023) and expressive resynthesis (Nguyen
et al., 2023), and that is where such a measure would belong. Preservation that appears on a
scorecard is preservation that can be defended.

## 6.5 Closing

The finding this study set out to make was that discretisation destroys interpersonal meaning. The
finding it reports is that discretisation is the smaller part of the problem, that the codec encoder
is the larger part, and that what survives does so because a component added for unrelated reasons
happened to inherit it from a teacher that encodes stance. That is a less tidy result and a more
actionable one. Rounding is irreducible and training objectives are chosen.
