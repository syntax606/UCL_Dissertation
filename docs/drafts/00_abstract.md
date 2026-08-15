# Abstract

---

Speech-to-speech dialogue systems consume discrete tokens rather than audio, so whatever
the tokeniser declines to represent is unavailable to every component downstream. Existing
work establishes that discretisation is lossy and that paralinguistic content suffers
disproportionately, but measures this by comparing a continuous encoder against a token
stream, two conditions differing simultaneously in architecture, training objective, frame
rate and feature construction. A parallel literature shows speech representations carry
pragmatic content that text discards, but compares utterances whose words differ, so
delivery and vocabulary are confounded.

This dissertation removes both confounds jointly. A corpus of 873 clips of spontaneous
political podcast speech was assembled in which one of eight short phrases occurs with
varying pragmatic force and constant wording, so no separation a probe achieves can be
attributed to vocabulary. Each codec is then probed immediately before and immediately
after quantisation on identical forward passes, so the rounding step is the only
difference between conditions.

Three findings follow. Quantisation is the smaller cost in all three codecs tested, by 3.3
to 1 in Mimi and 6.7 to 1 in DAC, with EnCodec's quantiser costing nothing measurable, so
the loss falls at the encoder. What the encoder fails to preserve is not acoustic detail,
since the codecs recover hand-crafted acoustic cues more faithfully than the model Mimi
distils from while reading stance off them far worse, but temporal organisation. And that
tracks encoder architecture rather than sampling density, since two codecs matched at 75
Hz differ by 0.040 in how much frame order contributes, separated by whether the encoder
carries a mechanism for integrating across time.

Three further hypotheses were stated before testing and are not supported, including that
variable-frame-rate tokenisation recovers the loss.

The measurements imply that interventions at the codebook operate on information the
encoder has already declined to represent, and that raising the frame rate is not the
mechanism by which timing is preserved. Decoding remains well below human performance on
the same clips, at 0.533 against 0.730, so these are comparisons between representations
rather than claims about approaching a listener.

---

