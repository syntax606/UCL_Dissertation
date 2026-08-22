<!-- GENERATED from the Word draft by src/45_export_draft.py.
     The .docx is authoritative. Edits made here will be overwritten. -->

# Chapter 6: Conclusion, Limitations and Future Work

## 6.1 Conclusions

This study asked whether pragmatic contrast survives the representations that speech-to-speech systems consume, and if not, where it is lost and why. The four research questions in [1.3] are answered as follows.

RQ1. Stance is linearly decodable under lexical control. WavLM reaches 0.557 macro-F1 against its own null of 0.331, and the ordering survives the within-word contrast, matched arousal, held-out shows and six probe capacities [4.2, 4.6]. This is decodability relative to other representations rather than to a listener, since the best model condition reaches 0.533 where annotators reach 0.730 [4.1].

RQ2. The representation deployed systems consume retains little of it. Mimi’s token histogram reaches 0.371, a margin of 0.059 over its null against WavLM’s 0.225, and sits below 88 hand-crafted acoustic functionals at 0.420 [4.2]. Whatever the deployed stream carries, a standard feature set carries more.

RQ3. The loss is not where this study expected to find it. Quantisation, the only step capable of making two distinct inputs literally identical, is the smaller contributor in all three codecs, by 3.3 to 1 in Mimi and 6.7 to 1 in DAC [4.3]. The falsification of H4 is what redirected the study toward the encoder.

RQ4, and the remainder of RQ3. What the encoder fails to preserve is temporal organisation rather than acoustic detail. The codecs recover hand-crafted cues more faithfully than the model Mimi distils from, including the contour features stance is built from, while reading stance off them far worse [4.4]. Temporal is the one cue group they lose, and independently the gain from frame order declines across the encoder rungs. Matching DAC and EnCodec at 75 Hz isolates the reason [4.5].

A fifth result bears on the literature rather than on codecs. Fold assignment alone contributes a standard deviation of 0.010 with a range up to 0.06, the magnitude of several differences reported in this area [3.7], so differences under roughly 0.03 are not read as orderings here.

Of the five hypotheses formed before the analyses, H1, H2, H3 and H5 are supported and H4 is not. Of the four formed after the falsification of H4 redirected the study, H9 is supported and H6 to H8 are not. As [1.3] states, H9 was formed after an anomalous result and then tested on a codec not previously included, which is not the same kind of claim as one registered in advance.

## 6.2 Limitations

The full treatment of each constraint below is in Appendix [D].

Three hypotheses were stated before testing and are not supported, and reporting them is part of the result. Variable-frame-rate tokenisation does not recover the loss. Timing features alone sit at chance. Run-length and change-rate summaries of the discrete streams lose to counting [4.6, 5.3]. A training-free contrast-preservation measure was also attempted and does not discriminate, and its failure is structural rather than a matter of power [E.5].

Four constraints bound the positive findings, and a fifth concerns the identity control.

The architectural account cannot be separated from training history. Frozen public checkpoints cannot distinguish what an architecture can represent from what a particular training run taught it to represent, and an apparent architectural limit in DAC has already been shown to resolve into a training misconfiguration (Gichamba and Busogi, 2026).

The encoder figure is an upper bound while the quantisation figure is not, since WavLM contributes twice the pooled dimensionality of a codec latent while the quantiser step compares a representation against itself at equal width. That matters because the ratio between the two is the claim [D].

The attribution to distillation is associational. Mimi's codebook 0 carries the stance signal and codebook 0 is the distilled one, but the decisive experiment trains one codec with and without the objective.

Linear probing measures accessibility rather than presence (Belinkov, 2022), though across six probe capacities no configuration recovers more than +0.025 against a gap of 0.139 [E.3], so accessibility bounds rather than explains the result. The identity control is held-out shows rather than unseen speakers, since the corpus carries show labels only.

## 6.3 A programme for repair

Because the loss is caused by design choices rather than by rounding, and design choices are chosen, it is a tractable problem. Four steps follow, ordered so that each supplies what the next needs.

Give the encoder a mechanism for representing time. This is the most direct implication and the one the measurements support most strongly. The comparison at matched frame rate says that raising sampling density does not help, which matters because the active response to prosody loss in codec design has been to make the frame rate dynamic. Those proposals diagnose the problem correctly and choose a mechanism these results suggest is insufficient, since an adaptive grid does not by itself produce a representation from which interpersonal meaning is readable. The prediction is stated so it can fail. A codec with attention should retain more order information than one with recurrence, which should retain more than one with neither, and the next codec added can falsify it.

Establish causality for the distillation observation. Train one codec with and without a distillation term, and across teachers differing in how much stance they encode. Every other step assumes its outcome.

Test the organisation account directly. Which cues a codec loses is now measured, and the answer is one group of five. The other four survive better in a codec than in the model it distils from, so the open question is why acoustics that survive are not usable. The sharpest test holds a representation fixed in acoustic content and varies only how that content is arranged, for instance by reorganising a codec latent under a contrastive objective with no access to new signal. Same-word opposite-stance pairs make delivery the only separating signal, and the 873 clips assembled here are already in that form.

Build the diagnostic that would notice. The retention that exists is optimised for by no loss term, and reconstruction quality, word error rate and perceptual scores would be unchanged if it vanished, so a successor system could drop the objective and every reported number would improve. The minimal-pair ABX task is the natural template, since it fixes the comparison as a triplet and estimates no centroid, so it degrades gracefully at small samples (Schatz et al., 2013) and is used this way inside evaluation suites for spoken language modelling (Dunbar et al., 2021). A pragmatic-contrast analogue would present two clips of one word carrying opposing stance and a third matched to one of them. Preservation that appears on a scorecard is preservation that can be defended.

## 6.4 Closing

The finding this study set out to make was that discretisation destroys interpersonal meaning. What it reports is that discretisation is the smaller part, that the encoder is the larger part, and that what the encoder loses is not the acoustics but their arrangement in time. Whether that arrangement survives tracks whether the encoder has anything with which to represent it.

That is a less tidy result and a more actionable one. Rounding is irreducible. Architectures are chosen.
