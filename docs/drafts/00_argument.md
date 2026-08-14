# The argument

*Reference point for the rewrite. Not a chapter. Every chapter serves this and
nothing that fails to serve it belongs in the body.*

---

## The paragraph

Speech-to-speech systems consume discrete tokens, and those tokens carry less
interpersonal meaning than the continuous representations they derive from. Holding
the word constant and varying only delivery separates that loss from the
uncontroversial fact that compression discards signal. Measured this way across three
codecs of independent design, the loss falls overwhelmingly at the encoder rather than
the quantiser, by 3.3 to 1 in Mimi and 6.7 to 1 in DAC, with EnCodec's quantiser
costing nothing measurable. The codec has not discarded the prosody, since it recovers
hand-crafted acoustic cues more faithfully than the model it distils from. What it
fails to preserve is temporal organisation. The probe's gain from frame order,
measured against a shuffled control matched on dimensionality, falls along the same
ladder the stance decoding falls along, from 0.113 in WavLM to 0.080 before
quantisation in Mimi, 0.048 after, and nothing at all in DAC. That decline tracks
encoder architecture rather than sampling density, because DAC and EnCodec run at the
same 75 Hz and differ only in whether the encoder can integrate across time.

---

## Framing

**Abstract opens on deployment.** A reader has to want the answer before they will
follow the method. The tokens that deployed systems consume are the hook.

**Introduction opens on method.** Holding the word constant is what makes any of this
more than a restatement that compression is lossy, and a reader who has not accepted
that move will not accept anything downstream of it. Say it once, early, in full, and
never argue for it again.

The effect sizes are modest and the human ceiling is not approached, so trust is worth
more here than excitement.

---

## The three moves

Each is one results section and one table. If a number does not belong in one of these
three tables or in a single controls paragraph, it goes to the appendix.

### Move 1. Where is the loss?

At the encoder, not the quantiser, replicated across three codecs.

| step | cost | sd | t |
|---|---:|---:|---:|
| encoder, WavLM to Mimi pre | +0.089 | 0.014 | 30.8 |
| quantiser, Mimi pre to post | +0.027 | 0.015 | 9.4 |
| encoder, WavLM to DAC pre | +0.153 | 0.017 | 45.8 |
| quantiser, DAC pre to post | +0.023 | 0.013 | 9.0 |
| encoder, WavLM to EnCodec pre | +0.161 | 0.011 | 75.5 |
| quantiser, EnCodec pre to post | −0.005 | 0.015 | −1.5 |

Source `results/ladder_repeated.txt`, `src/35`. Mean over 25 episode-to-fold
partitions, costs paired across them.

### Move 2. What kind of loss is it?

Temporal, and it drains progressively rather than at one step.

| representation | order effect | sd | t |
|---|---:|---:|---:|
| WavLM L20 | +0.113 | 0.013 | 44.6 |
| Mimi pre-quantisation | +0.080 | 0.018 | 21.9 |
| Whisper L9 | +0.070 | 0.015 | 23.6 |
| Mimi post-quantisation | +0.048 | 0.019 | 13.0 |
| EnCodec pre-quantisation | +0.033 | 0.017 | 9.8 |
| DAC pre-quantisation | −0.007 | 0.019 | −1.9 |

HuBERT-large is omitted from the body and reported in Appendix H. It duplicates WavLM as
a self-supervised control and its layer selection is not stable, ranging over L10 to L23
across folds. It was probed throughout and its figures are reported rather than dropped,
since removing a condition after seeing its results would be selective reporting.

Source `results/timing_probe.csv`, `src/34`. Each readout is compared against its own
frame-shuffled control, which matches on dimensionality and on every feature's
marginal distribution while destroying order, paired on identical partitions.

### Move 3. Why?

Encoder architecture, not sampling density.

| codec | temporal mechanism | frame rate | order effect |
|---|---|---|---:|
| DAC | none, pure CNN | 75 Hz | −0.007 |
| EnCodec | LSTM | 75 Hz | +0.033 |
| Mimi | 8 self-attention layers | 12.5 Hz | +0.080 |

DAC and EnCodec are matched at 75 Hz and differ by 0.040, above the partition-noise
threshold, so frame rate is excluded by a controlled comparison rather than by
inference. Convolutional receptive fields are comparable and DAC's is the larger, 221
ms against 178 ms, so convolutional depth is excluded too. Architectures read from the
loaded checkpoints, not from published descriptions.

---

## Supporting, not headlining

One sentence each in the body. Detail to the appendix.

- Cue retention. Mimi reaches 153 per cent of WavLM on contour and 158 per cent on
  voice quality with half the dimensions, so the deficit is organisation rather than
  fidelity. State the caveat with it, since a reconstruction objective is meant to
  retain waveform descriptors and eGeMAPS functionals are waveform descriptors. The
  force is in the pairing with Move 1, not in the retention alone.
- Variable-frame-rate tokenisers do not help. Sylber 0.446 and DyCAST 0.40 both sit
  below Mimi pre-quantisation at 0.468, and syllabic tokenisers are described in the
  literature as discarding fine acoustic detail by design, so this is confirmatory.
- Timing features alone sit at chance. Token count, rate and duration moments reach
  0.316 and 0.338 against a null near 0.33.
- Order-aware summaries of the discrete streams score below the unigram histogram they
  were meant to improve on.
- Controls. Stance survives at matched arousal, survives regrouping folds by show, and
  the ordering is unchanged under a non-linear probe.

---

## Deliberately not claimed

- **Not** that machines approach human performance. 0.533 against 0.730, and a human
  reading only the transcript reaches 0.650, above every model condition including the
  ones given both modalities.
- **Not** that deployed systems fail. This measures whether information is linearly
  readable from a frozen representation, not whether any system uses it. The bridge is
  a necessary condition, not a sufficient one.
- **Not** that distillation causes the retention. Codebook 0 carries the stance signal
  and codebook 0 is the distilled one, but that is a correlation and settling it needs
  a codec trained twice.
- **Not** that architecture is the only possible account of the DAC result. Gichamba
  and Busogi (arXiv 2606.16969) showed an apparent architectural limit in DAC turning
  out to be a training misconfiguration, and frozen checkpoints cannot rule that out
  here.

---

## The prediction

If temporal structure survives to the degree the encoder has a mechanism for
representing it, a codec with attention should retain more order information than one
with recurrence, which should retain more than one with neither. That ordering held on
the first test it was put to. It is stated as a prediction because the next codec added
can falsify it.

---

## Precision

Fold assignment alone contributes sd 0.010 with range up to 0.06, and `GroupKFold`
assigns folds differently across scikit-learn versions, moving WavLM L20 from 0.553 to
0.573 on byte-identical inputs. **Differences under roughly 0.03 are not robust.**
Every figure above is a mean over 25 partitions defined in `src/34` rather than
delegated to a library.

This is a methods paragraph and a limitation, not a fifth finding. It is worth separate
treatment elsewhere and it should not compete for attention here.

---

## Word budget

| chapter | target |
|---|---:|
| Introduction | 1,200 |
| Literature | 1,800 |
| Methods | 2,000 |
| Results | 2,200 |
| Discussion | 1,800 |
| Conclusion | 1,000 |
| **body** | **10,000** |

Current body is 13,200 and the timing result still has to go in, so the real cut from
existing prose is closer to 4,500 words. Methods is the largest overspend at 3,265 and
most of the excess is procedural detail that belongs in the appendices, which do not
count.
