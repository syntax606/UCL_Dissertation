<!-- GENERATED from the Word draft by src/45_export_draft.py.
     The .docx is authoritative. Edits made here will be overwritten. -->

# Chapter 4: Results

Every macro-F1 reported here is the mean over 25 independent episode-to-fold partitions with its standard deviation, for the reasons given in [3.7]. Fold assignment alone contributes a standard deviation of 0.010, so differences under roughly 0.03 should not be read as ordering one representation above another. The primary window is the 10 s segment window and the primary readout is mean and standard deviation pooling, both fixed in advance [3.5, 3.6]. HuBERT-large was probed throughout on identical folds and features and is reported in Appendix [H] rather than here, since it duplicates WavLM as a self-supervised control and its layer selection is not stable [3.7]. Methodological checks that bear on how these figures should be read, rather than on what they say, are in Appendix [G].

## 4.1 The premise check and the ceiling

Two auxiliary annotators judged a counterbalanced 60-clip subset against a hidden reference. Transcript with discourse context reached 0.65 accuracy and audio with transcript reached 0.73, against a three-way chance level of 0.33. Audio therefore adds a real increment over the words, while discourse context alone recovers a substantial part of the contrast. The agreement particles were hardest even from audio, at 0.58 for okay and 0.64 for yeah, which is expected given that those are the phrases whose functional ambiguity is widest (Gravano et al., 2012).

The absolute level is what the prior literature predicts rather than a shortfall. Rockwell (2000) found listeners unable to discriminate spontaneous sarcasm from non-sarcasm at all, and Bryant and Fox Tree (2005) argue against a single dedicated ironic marker in favour of a family of cues recognised in context. Both predict a real audio increment on spontaneous delivery with context contributing substantially.

Scoring the models on those same sixty clips, the only like-for-like comparison available, places the best model condition at 0.533 against the human 0.730 [G.1]. The representations examined below carry something closer to half of what a listener recovers from the same audio. Everything that follows is a comparison between representations and not a claim about approaching human performance.

## 4.2 Decodability, and the lexical control

Table 4.1 reports the three-way stance probe on the primary window. Sylber and DyCAST are the two variable-frame-rate tokenisers, included for the comparison in [4.6] and discussed there rather than here.

| Representation | macro-F1 | sd |
|---|---|---|
| WavLM L20 | 0.557 | 0.009 |
| Whisper encoder L9 | 0.548 | 0.013 |
| Text, target word only | 0.493 | 0.004 |
| Mimi, before quantisation | 0.468 | 0.014 |
| Sylber | 0.446 | 0.011 |
| Mimi, after quantisation | 0.441 | 0.014 |
| eGeMAPS, 88 functionals | 0.420 | 0.012 |
| DAC, before quantisation | 0.404 | 0.015 |
| DyCAST, after quantisation | 0.403 | 0.010 |
| DyCAST, before quantisation | 0.401 | 0.009 |
| EnCodec, after quantisation | 0.400 | 0.010 |
| EnCodec, before quantisation | 0.396 | 0.012 |
| Text, with discourse context | 0.394 | 0.013 |
| DAC, after quantisation | 0.381 | 0.013 |
| Mimi, deployed tokens | 0.371 | 0.009 |

Every representation exceeds its own empirical permutation null, obtained by refitting on shuffled labels under the same partitioning. The null is not constant across configurations, ranging from 0.311 to 0.337, so every margin below is given against that configuration's own null rather than against a single assumed value [B.2]. What lowers it is not width but degenerate structure. The two lowest belong to Mimi's 16,384-dimensional histogram at 0.311 and the 768-dimensional target-only text at 0.313, one sparse and one near-constant within a phrase by construction, while a 1,024-dimensional representation carries the highest at 0.337. A shuffled-label probe has least to work with where the representation has least effective structure, which is why the null has to be measured per configuration rather than assumed from dimensionality. One consequence is visible in the table. Mimi's deployed tokens score lower than DAC after quantisation, at 0.371 against 0.381, but clear a lower null and so carry the larger margin, at +0.060 against +0.050.

| representation | macro-F1 | null | margin |
|---|---|---|---|
| WavLM L20 | 0.557 | 0.330 | +0.226 |
| Whisper encoder L9 | 0.548 | 0.333 | +0.215 |
| Text, target word only | 0.493 | 0.313 | +0.179 |
| Mimi, before quantisation | 0.468 | 0.329 | +0.139 |
| Sylber | 0.446 | 0.328 | +0.118 |
| Mimi, after quantisation | 0.441 | 0.337 | +0.104 |
| eGeMAPS, 88 functionals | 0.420 | 0.324 | +0.096 |
| DyCAST, after quantisation | 0.403 | 0.317 | +0.086 |
| DyCAST, before quantisation | 0.401 | 0.320 | +0.081 |
| EnCodec, after quantisation | 0.400 | 0.328 | +0.072 |
| EnCodec, before quantisation | 0.396 | 0.326 | +0.070 |
| DAC, before quantisation | 0.404 | 0.336 | +0.068 |
| Text, with discourse context | 0.394 | 0.333 | +0.061 |
| Mimi, deployed tokens | 0.371 | 0.311 | +0.060 |
| DAC, after quantisation | 0.381 | 0.331 | +0.050 |

Two entries need comment. eGeMAPS is the hand-crafted comparison, and it places the deployed Mimi condition below 88 classical acoustic functionals, so the deployed token stream is not recovering something a standard feature set already captures. And the target-only text condition at 0.493 should not be read as text recovering stance, since the eight phrases differ in their stance base rates and a probe can score from word identity alone.

That confound is what the lexical control removes. Within each phrase the probe attempts that phrase's dominant binary contrast, so word identity carries no information.

| Representation | mean within-word macro-F1 | sd | mean per-phrase sd |
|---|---|---|---|
| Whisper encoder L9 | 0.658 | 0.010 | 0.030 |
| WavLM L20 | 0.656 | 0.010 | 0.030 |
| Mimi, before quantisation | 0.609 | 0.015 | 0.036 |
| Mimi, after quantisation | 0.586 | 0.015 | 0.036 |
| Text, with discourse context | 0.554 | 0.010 | 0.035 |
| eGeMAPS, 88 functionals | 0.551 | 0.010 | 0.033 |
| Mimi, deployed histogram | 0.464 | 0.010 | 0.022 |

The ordering survives the control, which is the result the rest of the chapter depends on. Whatever the codecs are losing, they are not losing it because the probe was reading the word. Mimi appears twice because the difference between those two rows is the readout rather than the representation, decomposed in [G.2].

Two things follow from the third column. Individual phrase cells hold 68 to 127 clips and move by roughly 0.030 with the partition alone, three times as much as the averaged figure, so per-phrase results are reported in Appendix [C] and are not read as orderings. And WavLM and Whisper are separated by 0.002 against an sd of 0.010, so they are not distinguishable here. The layer sweep reaches the same conclusion from a different direction [G.6].

## 4.3 Where the loss is

Table 4.1 confounds quantisation with feature construction, frame rate, architecture and training objective. This section isolates the stages. Because the word is held constant throughout, a loss localised to a stage is a loss of pragmatic rather than phonetic sensitivity. Mimi's residual quantiser operates in a projected space, so the comparable pair is the projected encoder latent against the summed codebook vectors before output projection, whose cosine is 0.821 against 0.004 for the naive pairing that would otherwise be used [3.5].

Costs are paired across the same 25 partitions, so partition noise cancels.

| Step | cost | sd | t |
|---|---|---|---|
| encoder, WavLM to Mimi | +0.089 | 0.014 | 30.8 |
| quantiser, Mimi | +0.027 | 0.015 | 9.4 |
| encoder, WavLM to DAC | +0.153 | 0.017 | 45.8 |
| quantiser, DAC | +0.023 | 0.013 | 9.0 |
| encoder, WavLM to EnCodec | +0.161 | 0.011 | 75.5 |
| quantiser, EnCodec | −0.005 | 0.015 | −1.5 |

In all three codecs the encoder is the dominant contributor, by 3.3 to 1 in Mimi and 6.7 to 1 in DAC, with EnCodec's quantiser costing nothing measurable. Three codecs of independent design, differing in objective, frame rate and quantiser, agree on where the loss falls.

Summarising the token stream costs a further 0.070, from Mimi's post-quantisation vectors at 0.441 to the deployed histogram at 0.371. That is a property of the histogram as a summarisation choice rather than of the deployed system, which consumes token sequences. Liu et al. (2024) give a mechanism, since codec encoders integrate context and therefore assign different codes to acoustically identical segments depending on their surroundings, which destabilises code identity while leaving the vector those codes decode to intact.

## 4.4 What is lost

The decomposition locates the loss without saying what is lost. Two measurements answer that, and they disagree with the intuitive account.

The acoustic cues are retained. Recovering hand-crafted cue groups from each rung by ridge regression, reported as a fraction of what WavLM supports. Each retention figure is the mean over the same 25 partitions the rest of the chapter uses, with the ratio formed within each partition before averaging so that it carries a spread of its own [3.7]. No cell has a standard deviation above three points and most sit at one.

| Representation | contour | level | voice quality | temporal | spectral |
|---|---|---|---|---|---|
| WavLM, ceiling, absolute R² | 0.289 | 0.610 | 0.219 | 0.558 | 0.345 |
| Mimi, before quantisation | 152% | 146% | 162% | 106% | 170% |
| Mimi, after quantisation | 137% | 143% | 143% | 96% | 161% |
| Mimi, deployed histogram | 97% | 107% | 111% | 78% | 121% |
| EnCodec, before quantisation | 127% | 145% | 145% | 71% | 164% |
| EnCodec, after quantisation | 127% | 144% | 137% | 69% | 162% |
| DAC, before quantisation | 121% | 130% | 127% | 67% | 160% |
| DAC, after quantisation | 115% | 127% | 117% | 61% | 156% |

The codecs recover the acoustic cues better than WavLM does, with half the feature dimensions, including the contour group that stance is built from. A reconstruction objective is meant to retain waveform-recoverable descriptors and eGeMAPS functionals are waveform descriptors, so this is less surprising alone than it is in combination with the previous section. The codec stores the cues more faithfully and reads stance off them far worse.

Among the continuous rungs, temporal is the only group falling below WavLM, and it falls furthest for DAC at 75 Hz rather than Mimi at 12.5, which is the wrong direction for a frame-rate account. The deployed histogram is the exception to the pattern as a whole, dropping to 97 per cent on contour and 78 per cent on temporal, which is a property of that summarisation rather than of the token stream [4.3]. Adding EnCodec to that column orders it by encoder architecture rather than by frame rate. Temporal retention runs 106 and 96 per cent for Mimi, which carries attention, 71 and 69 per cent for EnCodec, which carries recurrence, and 67 and 61 per cent for DAC, which carries neither, while DAC and EnCodec share a frame rate. That is the same ordering the order effect gives in [4.5], produced by a different measurement on different machinery, and it was not available when this analysis was first run.

What is lost is temporal organisation. Probing frame sequences rather than pooled summaries measures this directly. Each readout is compared against its own frame-shuffled control, which preserves dimensionality and every feature's marginal distribution while destroying order, paired on identical partitions.

| Representation | order effect | sd | t |
|---|---|---|---|
| WavLM L20 | +0.113 | 0.013 | 44.6 |
| Mimi, before quantisation | +0.080 | 0.018 | 21.9 |
| Whisper encoder L9 | +0.070 | 0.015 | 23.6 |
| EnCodec, after quantisation | +0.063 | 0.021 | 15.0 |
| Mimi, after quantisation | +0.048 | 0.019 | 13.0 |
| Sylber | +0.042 | 0.016 | 13.1 |
| EnCodec, before quantisation | +0.033 | 0.017 | 9.8 |
| DyCAST, before quantisation | +0.025 | 0.014 | 8.7 |
| DyCAST, after quantisation | +0.022 | 0.017 | 6.6 |
| DAC, before quantisation | −0.007 | 0.019 | −1.9 |
| DAC, after quantisation | −0.018 | 0.018 | −4.9 |

The gain from frame order declines along the same ladder the stance decoding declines along, and reaches nothing in DAC. Two rows do not fit that pattern, both of them quantiser steps rather than encoder steps, and neither is accounted for here. EnCodec gains order information at quantisation where Mimi loses it, and DAC's post-quantisation representation scores reliably better with frame order destroyed. Both are set out in [G.7].

The monotone decline therefore holds across the encoder rungs, where the claim in [4.5] is made, and not across the quantiser rungs. Two independent measurements point the same way, since temporal is also the one cue group the codecs fail to retain.

Whisper's figure is layer-sensitive in a way the others are not, and the sweep in [G.6] should be read alongside it.

The loss is not an artefact of the pooled readout. Time-aware readouts recover at most +0.031 at a fixed layer, and no representation moves past another on the strength of it [G.6].

## 4.5 Why

Frame rate does not explain the ordering, and a controlled comparison shows what does.

| Codec | temporal mechanism | frame rate | order effect |
|---|---|---|---|
| DAC | none, pure convolution | 75 Hz | −0.007 |
| EnCodec | LSTM | 75 Hz | +0.033 |
| Mimi | 8 self-attention layers | 12.5 Hz | +0.080 |

DAC and EnCodec run at the same 75 Hz and differ by 0.040, above the threshold set by partition noise, so sampling density is excluded by a matched comparison rather than by inference. Convolutional receptive fields are comparable and DAC's is the larger, 221 ms against EnCodec's 113 ms, so the codec with the wider convolutional context is the one carrying no order information [3.5].

Three properties of the comparison are worth separating, because the claim rests on all of them holding together.

Frame rate is held constant, not controlled for statistically. DAC and EnCodec are both 75 Hz by construction, so the comparison does not depend on modelling rate as a covariate or on assuming its effect is linear. It is the same clock, twice.

The remaining convolutional difference runs against the result. If convolutional context were the operative variable, DAC should carry more order information than EnCodec, since its receptive field is roughly twice as wide. It carries less, and by a margin above the noise threshold. The variable that does covary with the ordering is whether anything above the convolutional stack integrates across frames.

The ordering is monotone across three points rather than a single contrast. None, recurrence and attention give −0.007, +0.033 and +0.080, with the third supplied by a codec added after the prediction was made [1.4]. And a second measurement gives the same ordering independently, since temporal cue retention runs 106 per cent for Mimi, 71 for EnCodec and 67 for DAC [4.4]. The gap between the two codecs matched at 75 Hz is the narrow one, so it is tested rather than read off. Paired across the same 25 partitions, EnCodec retains 3.5 points more than DAC before quantisation and 7.7 points more after, and does so in every one of the 25. Two quantities that share no machinery rank the three codecs identically.

The ordering follows the presence of a mechanism for integrating across time. Gichamba and Busogi (2026) reach a compatible conclusion from a different quantity, finding no evidence that frame rate imposes a fundamental barrier to reconstruction quality, and describe Mimi as engineered for low frame rate tokenisation through a transformer bottleneck and split-RVQ design. That description is their characterisation of the architecture rather than a finding of their ablation, so it is consistent with the account here rather than independent evidence for it. Their DAC configuration reconstructs almost perfectly at 75 Hz while carrying no order information here, so reconstruction fidelity and temporal organisation come apart.

One alternative account cannot be excluded. These are three independently trained public checkpoints, and Gichamba and Busogi also show that an apparent architectural limit in DAC turned out to be a training misconfiguration, so frozen checkpoints cannot separate what an architecture can represent from what a particular training run taught it to represent. The account is therefore offered as the best supported of the available explanations rather than as established, and the limitation is stated in full in [6.2].

## 4.6 Controls, and what does not hold

Both controls were rerun under the partitioning in [3.7], so their baselines match Table 4.1 rather than the single-partition figures they were first computed against [controls_repeated.txt].

Arousal. Stance decoded within each arousal level separately, against the pooled figure.

| representation | pooled | low arousal | high arousal |
|---|---|---|---|
| WavLM L20 | 0.557 | 0.517 | 0.519 |
| Whisper encoder L9 | 0.548 | 0.542 | 0.518 |
| Mimi, before quantisation | 0.468 | 0.421 | 0.446 |
| eGeMAPS, 88 functionals | 0.420 | 0.389 | 0.409 |
| Mimi, deployed tokens | 0.371 | 0.363 | 0.361 |

Decoding falls when energy is held constant, by 0.038 for WavLM and 0.009 for Mimi, so the two axes are partly entangled. It does not fall to the null in any representation, so stance is not reducible to arousal.

Speaker. Regrouping folds by show rather than episode moves WavLM from 0.557 to 0.534, Whisper from 0.548 to 0.530, Mimi's tokens from 0.371 to 0.343 and eGeMAPS from 0.420 to 0.391. The cost is between 0.019 and 0.034 and is similar across representations, so the probe is not principally recovering speaker identity. Because the corpus carries show names rather than speaker labels, this is properly described as held-out shows.

Probe capacity. A non-linear probe under six capacity settings recovers at most +0.025 anywhere, against a continuous-to-discrete gap of roughly 0.14, so linear accessibility is not the limiting factor [G.3].

Codebooks. Probed cumulatively, Mimi's distilled codebook 0 alone reaches +0.069 and all eight together reach +0.071, so seven further codebooks and 14,336 further dimensions buy 0.002 [G.4]. Codebook 0 is the one distilled from WavLM. This is a correlation and not evidence that distillation causes the retention, which would need a codec trained twice.

Three hypotheses are not supported, and all three were stated before the run. Variable-frame-rate tokenisation does not preserve more. Against each configuration's own null, Mimi before quantisation reaches a margin of +0.139, Sylber +0.118 and DyCAST +0.081 before quantisation and +0.086 after. DyCAST is clearly below. Sylber is separated from Mimi by 0.021, which is inside the threshold set by partition noise, so it is level rather than below. Neither exceeds Mimi, which is what H7 predicted, so the hypothesis is unsupported either way. Timing features alone sit at chance, with token count, rate and duration moments reaching 0.316 and 0.338. And order-aware summaries of the discrete streams score below the unigram histogram they were intended to improve on.
