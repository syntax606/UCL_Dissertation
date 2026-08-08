# Chapter 6: Conclusion, Limitations and Future Work

*(Draft. Target budget ~800 words. Limitations condensed from `docs/limitations.md`, which holds the
full treatment and is the appendix source. Cross-references marked [Ch.x].)*

## 6.1 Conclusions

This study asked whether pragmatic contrast survives the representations that speech-to-speech
systems actually consume, and if not, where it is lost. Three answers follow from the measurements.

Pragmatic stance is linearly decodable from continuous speech representations when the lexical item
is held constant, and it survives every control applied to it. It holds at matched arousal, on
held-out shows, across three context windows, under three readouts and against a probe with more
capacity than the one used to report it [Ch.4].

The representation deployed systems consume retains a fraction of that. Mimi clears its own
permutation null by 0.070 against WavLM's 0.241, and falls below discourse text once the word is
held constant.

The loss is not where this study expected to find it. Quantisation costs 0.034 and the codec encoder
costs 0.112, a ratio of roughly one to three, and the same ordering appears in DAC, an independently
designed acoustic codec where quantisation is marginally beneficial. What survives inside Mimi sits
almost entirely in the codebook distilled from WavLM, a component introduced for semantic transfer
and computational economy rather than for anything paralinguistic [Ch.5].

## 6.2 Limitations

Three hypotheses were tested and not supported, and reporting them is part of the result. The
contrast-preservation score falls inside the interval between its two defensible baselines, 0.545 and
0.670, in every representation, so it does not discriminate and is not corroboration. The proposal
that these representations
encode activation and are read downstream as intent does not hold, because stance survives at fixed
arousal everywhere tested. And an apparent dissociation between the two axes reversed once the
readout was varied, so it was a property of the summary rather than of the representation.

Four constraints bound the positive findings. The 0.112 attributed to the codec encoder is an upper
bound, because WavLM contributes twice Mimi's pooled dimensionality, while the 0.034 for
quantisation is clean, since both sides share dimensionality, pooling and source. The attribution to
distillation is associational rather than causal, supported once across codecs and once within Mimi,
and the decisive experiment would train the same codec with and without the objective. Linear
probing measures accessibility rather than presence, and across six probe capacities no
configuration recovers more than +0.025, against a gap of roughly 0.14, so accessibility bounds
rather than explains the result, though a small regularised probe rules out modest non-linear
encoding rather than any conceivable encoding. And the corpus carries show labels rather than
speaker labels, so the identity control is properly described as held-out shows.

## 6.3 Why the loss is worth repairing

Three lines of evidence make this an applied problem rather than a representational curiosity.

Deployed systems already handle this information poorly. ParaS2S reports spoken language models
scoring 3.37 against 3.18 for a baseline that discards delivery entirely (Yang et al., 2026), and
VoxParadox finds audio language models following language-implied answers over acoustic evidence
(Pang et al., 2026). Safety behaviour is exposed to the same channel, with delivery-only jailbreaks
succeeding roughly nine times more often than neutral delivery on identical transcript content (Qian
and Li, 2026). And the applications that most need interpersonal reading are the ones with the least
tolerance for error, including the human-robot interaction failures catalogued by Cao et al. (2025).

The findings here add a specific constraint on how any of that can be addressed. A downstream model
cannot act on what its input representation does not carry, so better modelling addresses
information that is present and ignored and cannot address information that was never encoded. The
distinction matters because the two failure modes look identical from the outside.

The structural risk compounds it. Because the retention that does exist is incidental, no loss term
optimises for it and the metrics routinely reported for codecs are not sensitive to it.
Reconstruction quality, word error rate and perceptual scores would be unchanged if it vanished, so a
successor system could substitute the teacher or drop the objective and every reported number would
improve. Affect under codecs has been evaluated in its own right (Ren et al., 2024), but through
categorical emotion on resynthesised audio, and [Ch.5] gives the reason that measure would be an
imperfect guard for this particular quantity.

## 6.4 A programme for repair

Because the loss is caused by a training objective rather than by rounding, and objectives are
chosen, it is a design problem. Four steps follow directly from the measurements above.

**Establish causality.** Train one codec with and without a distillation term, and across teachers
that differ in how much stance they encode, converting the associational claim of [Ch.5] into a
controlled one.

**Choose the teacher layer by measurement.** WavLM carries 0.573 at layer 20 and 0.490 at layer 24,
so the choice of distillation target is consequential for this contrast. Semantic distillation
conventionally takes a mid-stack layer or an average across layers, selected for alignment with
linguistic content (Zhang et al., 2024; Jo et al., 2025). Selecting it against a paralinguistic probe
curve instead is an intervention that requires no architectural change, and the decomposition here
supplies the curve.

**Supervise the encoder on the right quantity.** Making affect a codec training objective is already
an active line, pursued through pre-quantisation latent modulation (Shi et al., 2026b) and through
structured projections inside the quantiser (Meng et al., 2026), and both act at or before the stage
this study identifies as dominant. The contribution available is therefore in the supervision rather
than the mechanism. Those objectives are supervised on categorical emotion, which is substantially
arousal-loaded, and the results here separate stance from arousal and find the surviving axis is the
arousal one [Ch.5]. An auxiliary objective over lexically matched pairs, same word and opposite
stance, supplies a signal that categorical emotion labels do not, and the 873 clips assembled here
are already in that form. The prediction is specific, namely that emotion-supervised objectives
improve retention of the axis that was least damaged, and that a lexically controlled contrastive
term is what reaches the other one.

**Build the diagnostic that would notice.** Affect under codecs has been evaluated (Ren et al.,
2024), though through resynthesis and downstream recognition rather than on the representation, and
not as a figure reported during development. The null in [Ch.4] is a specification for what a
representation-level version needs. A preservation measure defined on continuous within-cell
distances rather than hard classification, estimated over a depth-first sample of densely populated
speaker-by-word cells with the distance metric fixed in advance, would degrade gracefully at small
samples and could be computed cheaply enough to sit beside reconstruction quality during training.
Preservation that appears on a scorecard is preservation that can be defended.
