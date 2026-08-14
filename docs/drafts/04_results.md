# Chapter 4: Results

*(Draft. All figures from `results/`. Every macro-F1 is the mean over 25 independent
episode-to-fold partitions with its standard deviation, for the reasons in [3.7]. Fold
assignment alone contributes sd 0.010, so differences under roughly 0.03 should not be
read as ordering one representation above another. The primary window is W2 and the
primary readout is mean and standard deviation pooling, both fixed in advance [3.5,
3.6]. HuBERT-large was probed throughout and is reported in Appendix [H] rather than
here, since it duplicates WavLM as a self-supervised control and its layer selection is
not stable [3.5]. Methodological checks are in Appendix [G].)*

## 4.1 The premise check and the ceiling

Two auxiliary annotators judged a counterbalanced 60-clip subset against a hidden
reference. Transcript with discourse context reached 0.65 accuracy and audio with
transcript reached 0.73, against a three-way chance level of 0.33. Audio therefore adds
a real increment over the words, while discourse context alone recovers a substantial
part of the contrast. The agreement particles were hardest even from audio, at 0.58 for
*okay* and 0.64 for *yeah*, which is expected given that those are the phrases whose
functional ambiguity is widest (Gravano et al., 2012).

The absolute level is what the prior literature predicts rather than a shortfall.
Rockwell (2000) found listeners unable to discriminate spontaneous sarcasm from
non-sarcasm at all, and Bryant and Fox Tree (2005) argue against a single dedicated
ironic marker in favour of a family of cues recognised in context. Both predict a real
audio increment on spontaneous delivery with context contributing substantially.

Scoring the models on those same sixty clips, the only like-for-like comparison
available, places the best model condition at 0.533 against the human 0.730 [G.1]. The
representations examined below carry something closer to half of what a listener
recovers from the same audio. Everything that follows is a comparison between
representations and not a claim about approaching human performance.

## 4.2 Decodability, and the lexical control

Table 4.1 reports the three-way stance probe on the primary window.

| Representation | macro-F1 | sd |
|---|---:|---:|
| WavLM L20 | 0.557 | 0.009 |
| Whisper encoder L9 | 0.548 | 0.013 |
| Text, target word only | 0.493 | 0.004 |
| Mimi, before quantisation | 0.468 | 0.014 |
| Mimi, after quantisation | 0.441 | 0.014 |
| eGeMAPS, 88 functionals | 0.420 | 0.012 |
| DAC, before quantisation | 0.404 | 0.015 |
| EnCodec, before quantisation | 0.396 | 0.012 |
| Text, with discourse context | 0.394 | 0.013 |
| DAC, after quantisation | 0.381 | 0.013 |
| Mimi, deployed tokens | 0.371 | 0.009 |

Every representation exceeds the empirical permutation null, which sits near 0.33 in
every configuration tested [G.5]. The continuous encoders clear it by roughly 0.22,
the deployed token stream by 0.04.

Two entries need comment. **eGeMAPS** is the hand-crafted comparison, and it places the
deployed Mimi condition below 88 classical acoustic functionals, so the deployed token
stream is not recovering something a standard feature set already captures. And the **target-only
text** condition at 0.493 should not be read as text recovering stance, since the eight
phrases differ in their stance base rates and a probe can score from word identity
alone.

That confound is what the lexical control removes. Within each phrase the probe attempts
that phrase's dominant binary contrast, so word identity carries no information.

| Representation | mean within-word macro-F1 | sd | mean per-phrase sd |
|---|---:|---:|---:|
| Whisper encoder L9 | 0.658 | 0.010 | 0.030 |
| WavLM L20 | 0.656 | 0.010 | 0.030 |
| Mimi, before quantisation | 0.609 | 0.015 | 0.036 |
| Mimi, after quantisation | 0.586 | 0.015 | 0.036 |
| Text, with discourse context | 0.554 | 0.010 | 0.035 |
| eGeMAPS, 88 functionals | 0.551 | 0.010 | 0.033 |
| Mimi, deployed histogram | 0.464 | 0.010 | 0.022 |

The ordering survives the control, which is the result the rest of the chapter depends
on. Whatever the codecs are losing, they are not losing it because the probe was reading
the word.

Two things follow from the third column. Individual phrase cells hold 68 to 127 clips
and move by roughly 0.030 with the partition alone, three times as much as the averaged
figure, so per-phrase results are reported in Appendix [C] and are not read as
orderings. And WavLM and Whisper are separated by 0.002 against an sd of 0.010, so they
are not distinguishable here. The layer sweep reaches the same conclusion from a
different direction [G.6].

## 4.3 Where the loss is

Table 4.1 confounds quantisation with feature construction, frame rate, architecture and
training objective. This section isolates the stages. Because the word is held constant
throughout, a loss localised to a stage is a loss of pragmatic rather than phonetic
sensitivity. Mimi's residual quantiser operates in a projected space, so the comparable
pair is the projected encoder latent against the summed codebook vectors before output
projection, whose cosine is 0.821 against 0.004 for the naive pairing that would
otherwise be used [3.5].

Costs are paired across the same 25 partitions, so partition noise cancels.

| Step | cost | sd | t |
|---|---:|---:|---:|
| encoder, WavLM to Mimi | +0.089 | 0.014 | 30.8 |
| quantiser, Mimi | +0.027 | 0.015 | 9.4 |
| encoder, WavLM to DAC | +0.153 | 0.017 | 45.8 |
| quantiser, DAC | +0.023 | 0.013 | 9.0 |
| encoder, WavLM to EnCodec | +0.161 | 0.011 | 75.5 |
| quantiser, EnCodec | −0.005 | 0.015 | −1.5 |

**In all three codecs the encoder is the dominant contributor**, by 3.3 to 1 in Mimi and
6.7 to 1 in DAC, with EnCodec's quantiser costing nothing measurable. Three codecs of
independent design, differing in objective, frame rate and quantiser, agree on where the
loss falls.

Summarising the token stream costs a further 0.070, from Mimi's post-quantisation
vectors at 0.441 to the deployed histogram at 0.371. That is a property of the histogram
as a summarisation choice rather than of the deployed system, which consumes token
sequences. Liu et al. (2024) give a mechanism, since codec encoders integrate context
and therefore assign different codes to acoustically identical segments depending on
their surroundings, which destabilises code identity while leaving the vector those
codes decode to intact.

## 4.4 What is lost

The decomposition locates the loss without saying what is lost. Two measurements
answer that, and they disagree with the intuitive account.

**The acoustic cues are retained.** Recovering hand-crafted cue groups from each rung by
ridge regression, reported as a fraction of what WavLM supports:

| Representation | contour | level | voice quality | temporal | spectral |
|---|---:|---:|---:|---:|---:|
| WavLM, ceiling, absolute R² | 0.283 | 0.607 | 0.225 | 0.557 | 0.345 |
| Mimi, before quantisation | 153% | 147% | 158% | 106% | 170% |
| Mimi, after quantisation | 139% | 143% | 139% | 97% | 162% |
| Mimi, deployed histogram | 98% | 106% | 109% | 78% | 121% |
| DAC, before quantisation | 122% | 130% | 123% | 68% | 161% |
| DAC, after quantisation | 117% | 127% | 113% | 63% | 157% |

The codecs recover the acoustic cues **better** than WavLM does, with half the feature
dimensions, including the contour group that stance is built from. A reconstruction
objective is meant to retain waveform-recoverable descriptors and eGeMAPS functionals
are waveform descriptors, so this is less surprising alone than it is in combination
with the previous section. The codec stores the cues more faithfully and reads stance
off them far worse.

Only the temporal group falls below WavLM, and it falls furthest for DAC at 75 Hz rather
than Mimi at 12.5, which is the wrong direction for a frame-rate account.

**What is lost is temporal organisation.** Probing frame sequences rather than pooled
summaries measures this directly. Each readout is compared against its own
frame-shuffled control, which preserves dimensionality and every feature's marginal
distribution while destroying order, paired on identical partitions.

| Representation | order effect | sd | t |
|---|---:|---:|---:|
| WavLM L20 | +0.113 | 0.013 | 44.6 |
| Mimi, before quantisation | +0.080 | 0.018 | 21.9 |
| Whisper encoder L9 | +0.070 | 0.015 | 23.6 |
| Mimi, after quantisation | +0.048 | 0.019 | 13.0 |
| EnCodec, before quantisation | +0.033 | 0.017 | 9.8 |
| DAC, before quantisation | −0.007 | 0.019 | −1.9 |

The gain from frame order declines along the same ladder the stance decoding declines
along, and reaches nothing in DAC. Two independent measurements therefore point the same
way, since temporal is also the one cue group the codecs fail to retain.

The loss is not an artefact of the pooled readout. Time-aware readouts recover at most
+0.031 at a fixed layer, and no representation moves past another on the strength of it
[G.6].

## 4.5 Why

Frame rate does not explain the ordering, and a controlled comparison shows what does.

| Codec | temporal mechanism | frame rate | order effect |
|---|---|---|---:|
| DAC | none, pure convolution | 75 Hz | −0.007 |
| EnCodec | LSTM | 75 Hz | +0.033 |
| Mimi | 8 self-attention layers | 12.5 Hz | +0.080 |

**DAC and EnCodec run at the same 75 Hz and differ by 0.040**, above the threshold set
by partition noise, so sampling density is excluded by a matched comparison rather than
by inference. Convolutional receptive fields are comparable and DAC's is the larger, 221
ms against 178 ms, so convolutional depth is excluded too. Architectures were read from
the loaded checkpoints rather than from published descriptions [3.5].

The ordering follows the presence of a mechanism for integrating across time. Gichamba
and Busogi (2026) reach a compatible conclusion from reconstruction quality, finding no
evidence that frame rate imposes a fundamental barrier, and attribute Mimi's performance
at 12.5 Hz to its transformer bottleneck. Their DAC configuration reconstructs almost
perfectly at 75 Hz while carrying no order information here, so reconstruction fidelity
and temporal organisation come apart.

One alternative account cannot be excluded. Gichamba and Busogi also show that an
apparent architectural limit in DAC turned out to be a training misconfiguration, and
frozen checkpoints cannot separate architecture from training history.

## 4.6 Controls, and what does not hold

**Arousal.** Stance was decoded within each arousal level separately. WavLM reaches
0.531 on low-arousal clips and 0.549 on high, Whisper 0.526 and 0.514, and Mimi remains
significant at both levels. Margins fall in most cells but stance is not reducible to
arousal in any representation tested.

**Speaker.** Regrouping folds by show moves WavLM from 0.573 to 0.530, Whisper from
0.564 to 0.536 and Mimi from 0.381 to 0.362. Because the corpus carries show names
rather than speaker labels, this is properly described as held-out shows.

**Probe capacity.** A non-linear probe under six capacity settings recovers at most
+0.025 anywhere, against a continuous-to-discrete gap of roughly 0.14, so linear
accessibility is not the limiting factor [G.3].

**Codebooks.** Probed cumulatively, Mimi's distilled codebook 0 alone reaches +0.069 and
all eight together reach +0.071, so seven further codebooks and 14,336 further
dimensions buy 0.002 [G.4]. Codebook 0 is the one distilled from WavLM. This is a
correlation and not evidence that distillation causes the retention, which would need a
codec trained twice.

**Three hypotheses are not supported**, and all three were stated before the run.
Variable-frame-rate tokenisation does not preserve more, with Sylber at 0.446 and DyCAST
at 0.40 sitting below Mimi before quantisation at 0.468. Timing features alone sit at
chance, with token count, rate and duration moments reaching 0.316 and 0.338. And
order-aware summaries of the discrete streams score below the unigram histogram they
were intended to improve on.
