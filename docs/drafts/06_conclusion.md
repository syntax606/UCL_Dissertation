# Chapter 6: Conclusion, Limitations and Future Work

*(Draft. Cross-references marked [Ch.x]. Full limitations treatment in Appendix [F].)*

## 6.1 Conclusions

This study asked whether pragmatic contrast survives the representations that
speech-to-speech systems consume, and if not, where it is lost. Three answers follow.

Pragmatic stance is linearly decodable from continuous speech representations when the
lexical item is held constant, and it survives every control applied to it [4.2, 4.6].
The representation deployed systems consume retains a fraction of that.

The loss is not where this study expected to find it. Quantisation, the only step capable
of making two distinct inputs literally identical, is the smaller contributor in all
three codecs tested, by 3.3 to 1 in Mimi and 6.7 to 1 in DAC, with EnCodec's quantiser
costing nothing measurable [4.3]. Three designs differing in objective, frame rate and
quantiser agree that the encoder is where the information goes.

What the encoder fails to preserve is temporal organisation rather than acoustic
detail. The codecs recover hand-crafted acoustic cues more faithfully than the model
Mimi distils from, including the contour features stance is built from, while reading
stance off them far worse [4.4]. Temporal is the one cue group they lose, and
independently, the gain a probe takes from frame order declines along the same ladder
the stance decoding declines along, reaching nothing in DAC. Matching two codecs at 75 Hz
isolates the reason. DAC and EnCodec differ by 0.040 in that quantity while sharing a
frame rate and a comparable convolutional receptive field, and what separates them is
that EnCodec's encoder carries an LSTM where DAC's carries nothing [4.5]. Temporal
structure appears to survive to the degree the encoder has a mechanism for representing
it, and sampling density is not that mechanism.

## 6.2 Limitations

Three hypotheses were stated before testing and are not supported, and reporting them is
part of the result. Variable-frame-rate tokenisation does not recover the loss, with
Sylber and DyCAST both below Mimi before quantisation. Timing features alone sit at
chance. Order-aware summaries of the discrete streams score below the unigram histogram
they were intended to improve on [4.6].

Four constraints bound the positive findings.

The architectural account is the best supported explanation available and it is not the
only one. Gichamba and Busogi (2026) show an apparent architectural limit in DAC
resolving into a training misconfiguration once sequence length was matched. Frozen
public checkpoints cannot separate what an architecture can represent from what a
particular training run taught it to represent, and settling that needs codecs trained
under matched conditions differing only in the temporal mechanism.

The attribution to distillation is associational. Mimi's codebook 0 carries the stance
signal and codebook 0 is the distilled one, but the decisive experiment trains one codec
with and without the objective.

Linear probing measures accessibility rather than presence (Belinkov, 2022), though
across six probe capacities no configuration recovers more than +0.025 against a gap of
roughly 0.14 [G.3], so accessibility bounds rather than explains the result. The identity
control is held-out shows rather than unseen speakers, since the corpus carries show
labels only.

Finally, the precision these figures can carry is lower than three decimal places
suggests. Fold assignment alone contributes a standard deviation of 0.010 with a range up
to 0.06 [3.7], so differences under roughly 0.03 are not robust. Every figure reported
here is a mean over 25 partitions for that reason, and the practice is worth adopting
more widely than this study, since it costs minutes and changes which comparisons survive.

## 6.3 A programme for repair

Because the loss is caused by design choices rather than by rounding, and design choices
are chosen, it is a tractable problem. Four steps follow, ordered so that each supplies
what the next needs.

**Give the encoder a mechanism for representing time.** This is the most direct
implication and the one the measurements support most strongly. The comparison at matched
frame rate says that raising sampling density does not help, which matters because the
active response to prosody loss in codec design has been to make the frame rate dynamic.
Those proposals diagnose the problem correctly and the mechanism they choose is one these
results suggest is insufficient, since making the grid adaptive to linguistic units does
not by itself produce a representation from which interpersonal meaning is readable. The
prediction is stated so it can fail. A codec with attention should retain more order
information than one with recurrence, which should retain more than one with neither, and
the next codec added can falsify it.

**Establish causality for the distillation observation.** Train one codec with and
without a distillation term, and across teachers differing in how much stance they
encode. Every other step assumes its outcome.

**Test the organisation account directly.** Which cues a codec loses is now measured and
the answer is essentially none of them, so the open question is not which acoustic
properties survive but why surviving acoustics are not usable. The sharpest test holds a
representation fixed in acoustic content and varies only how that content is arranged,
for instance by reorganising a codec latent under a contrastive objective with no access
to new signal. If stance becomes readable, organisation is the constraint. If it does
not, something else is. A lexically controlled contrast supplies what categorical emotion
labels do not, since same-word opposite-stance pairs make delivery the only separating
signal, and the 873 clips assembled here are already in that form.

**Build the diagnostic that would notice.** The retention that exists is not optimised
for by any loss term, and the metrics routinely reported for codecs are not sensitive to
it, so reconstruction quality, word error rate and perceptual scores would be unchanged
if it vanished. A successor system could drop the objective and every reported number
would improve. What is needed is a measure cheap enough to report during development. The
minimal-pair ABX task is the natural template, since it fixes the comparison as a triplet
and estimates no centroid, so it degrades gracefully at small samples (Schatz et al.,
2013). A pragmatic-contrast analogue would present two clips of one word carrying
opposing stance and a third matched to one of them, then score whether the representation
places the third nearer its own class. Preservation that appears on a scorecard is
preservation that can be defended.

## 6.4 Closing

The finding this study set out to make was that discretisation destroys interpersonal
meaning. What it reports is that discretisation is the smaller part, that the encoder is
the larger part, and that what the encoder loses is not the acoustics but their
arrangement in time. Whether that arrangement survives tracks whether the encoder has
anything with which to represent it.

That is a less tidy result and a more actionable one. Rounding is irreducible.
Architectures are chosen.
