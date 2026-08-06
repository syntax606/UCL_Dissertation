# Chapter 4: Results

*(Draft. Target budget ~1,900 words. All figures from `results/`. Margins are macro-F1 minus the
mean of that configuration's own permutation null, 200 permutations unless stated. Intervals are
episode-cluster bootstrap. The primary window is W2 and the primary readout is mean and standard
deviation pooling, both fixed in advance [3.5, 3.6].)*

## 4.1 The premise check

Two auxiliary annotators judged a counterbalanced 60-clip subset against a hidden reference.
Transcript with discourse context reached 0.65 accuracy and audio with transcript reached 0.73,
against a three-way chance level of 0.33. Audio therefore adds a real increment over the words,
while discourse context alone recovers a substantial part of the contrast. The agreement particles
were hardest even from audio, at 0.58 for *okay* and 0.64 for *yeah*.

This outcome shapes how the text conditions are read below. Stance is partly recoverable from
surrounding words, so the interesting quantity is what audio adds rather than whether text fails.

## 4.2 Pooled stance decodability

Table 4.1 reports the three-way stance probe on the primary window. Chance is the mean of each
configuration's own permutation null. The majority-class figure of 0.196 is given for completeness
and is not the reference used, for the reasons set out in [3.6].

| Representation | layer | macro-F1 | 95% CI | chance | margin | p |
|---|---|---|---|---|---|---|
| WavLM | 20 | 0.573 | [0.54, 0.61] | 0.332 | +0.241 | 0.005 |
| Whisper encoder | 9 | 0.564 | [0.53, 0.60] | 0.332 | +0.232 | 0.005 |
| HuBERT | 23 | 0.520 | [0.49, 0.56] | 0.334 | +0.186 | 0.005 |
| Text, target word only | | 0.487 | [0.46, 0.52] | 0.313 | +0.174 | 0.005 |
| Mimi, all 8 codebooks | | 0.381 | [0.35, 0.41] | 0.311 | +0.070 | 0.005 |
| Text, with discourse | | 0.378 | [0.35, 0.41] | 0.333 | +0.045 | 0.010 |

Every representation exceeds its own null. The three continuous encoders clear it by 0.19 to 0.24,
while Mimi clears it by 0.070 and discourse text by 0.045.

Two entries need comment. The Whisper encoder performs within 0.01 of WavLM despite being a
supervised transcription model and a considerably smaller one, 13 layers of 1,536 units against 25
of 2,048. Section 4.5 returns to this. And the target-only text condition reaches 0.487, which
should not be read as text recovering stance. Because the eight phrases differ in their stance base
rates, a probe can score from word identity alone, and this condition is at chance only within a
phrase. The within-word analysis in 4.3 removes that route entirely.

## 4.3 The lexical control

Within each phrase the probe attempts that phrase's dominant binary stance contrast, so word
identity carries no information. Means over the eight phrases are given in Table 4.2.

| Representation | mean within-word macro-F1 |
|---|---|
| Whisper encoder | 0.672 |
| WavLM | 0.659 |
| HuBERT | 0.616 |
| Text, with discourse | 0.534 |
| Mimi | 0.466 |

The ordering changes from Table 4.1 in one instructive way. Mimi sits fractionally above discourse
text when pooled and clearly below it once the word is held constant, which is consistent with part
of Mimi's pooled figure resting on phrase identity in the same manner as the target-only text
condition.

Whisper is the strongest representation under the lexical control, marginally ahead of WavLM. Since
the word cannot help here, this cannot be attributed to Whisper's lexical bias.

## 4.4 Controls

**Arousal.** Stance was decoded within each arousal level separately, so that energy is constant
within each analysis. WavLM reaches 0.531 on low-arousal clips and 0.549 on high, against 0.573
pooled. Whisper reaches 0.526 and 0.514, HuBERT 0.459 and 0.518. The same test on the discrete
representations, run separately, leaves Mimi significant at both levels, at p 0.025 and p 0.017.
Margins fall by roughly a quarter to a third relative to the pooled analysis, so the two axes are
partly entangled, but stance is not reducible to arousal in any representation tested.

**Speaker.** Regrouping folds by show, so that no show appears in both training and testing, moves
WavLM from 0.573 to 0.530, Whisper from 0.564 to 0.536 and Mimi from 0.381 to 0.362. HuBERT falls
further, from 0.520 to 0.450. The probe is therefore not principally recovering speaker identity.
Because the corpus carries show names rather than speaker labels, and guests recur across shows,
this control is properly described as held-out shows rather than unseen speakers.

**Context window.** Across the local, segment and discourse windows WavLM scores 0.561, 0.573 and
0.511, Whisper 0.545, 0.564 and 0.531, HuBERT 0.537, 0.520 and 0.488. Performance is broadly flat
and does not rise with more surrounding speech, which indicates the continuous encoders are reading
delivery rather than leaning on discourse context. Mimi is the exception, at 0.392, 0.381 and 0.411.

**Readout.** Three summarisation methods were compared on identical forward passes. For WavLM the
choice is immaterial, giving margins of +0.244 for mean and standard deviation pooling, +0.250 for
four-segment pooling and +0.241 with frame-to-frame deltas added. For Mimi it is not, at +0.100,
+0.097 and +0.153. Delta features recover 53 per cent more margin from Mimi while doing nothing for
WavLM. This is not a capacity effect, since four-segment pooling gives Mimi four times the
dimensions without benefit and WavLM's delta condition doubles its dimensions without benefit.

**Probe capacity.** A non-linear probe on identical features and folds recovers no additional
stance from any representation. Gains over the linear probe are negative throughout, ranging from
-0.059 for the Whisper encoder to -0.009 for Mimi after quantisation, with WavLM at -0.037 and the
Mimi histogram at -0.036. The non-linear probe is functioning, clearing its own permutation null by
+0.204 on WavLM and +0.104 on Mimi at p 0.032 in both cases, so the shortfall reflects the cost of
fitting a more flexible model to 873 examples rather than a failure to train.

Two consequences follow. Linear accessibility is not the limiting factor, so the reported figures
describe content rather than reach. And the continuous-against-discrete comparison is not distorted
by representation type. Had quantised vectors been systematically harder for a linear probe, Mimi
would have gained most from the additional flexibility. It gained least, -0.009 against WavLM's
-0.037, which is the opposite of that confound.

## 4.5 Where the contrast lives

**Across layers.** WavLM rises from 0.402 at layer 0 to a peak of 0.573 at layer 20 of 24, then
declines to 0.490 at the final layer. HuBERT is flatter and noisier, peaking late at 0.520. Whisper
rises to 0.561 by layer 8 and then plateaus across its top third, reaching 0.564, 0.539, 0.557 and
0.548 at layers 9 to 12.

The WavLM curve matches the three-stage account in which upper layers abstract toward linguistic
content and shed paralinguistic detail. Whisper does not show that decline. Its supervised
transcription objective was expected to reduce acoustic information in the final encoder layers,
and on this task it does not, which is consistent with prior findings that ASR encoders retain
paralinguistic content and extends them to pragmatic stance under a lexical control.

**Across Mimi's codebooks.** Each codebook was probed alone, with its own permutation null.

| Block | macro-F1 | chance | margin | p |
|---|---|---|---|---|
| Codebook 0, WavLM-distilled | 0.402 | 0.330 | +0.072 | 0.005 |
| Codebook 1 | 0.377 | 0.331 | +0.046 | 0.020 |
| Codebook 3 | 0.368 | 0.331 | +0.037 | 0.035 |
| Codebooks 2, 4, 5, 6, 7 | 0.329 to 0.348 | ~0.330 | +0.006 to +0.018 | 0.159 to 0.552 |
| All 8, the deployed condition | 0.381 | 0.310 | +0.071 | 0.005 |
| Codebooks 1 to 7 only | 0.352 | 0.311 | +0.041 | 0.015 |

The distilled codebook is the only one carrying appreciable signal, and five of the seven acoustic
refinement codebooks are statistically indistinguishable from chance. Adding all seven to codebook 0
does not improve on codebook 0 alone. Chapter 2 predicted the opposite distribution, and 2.3.3
reports that as a corrected expectation.

## 4.6 Locating the loss

The comparison in Table 4.1 confounds quantisation with feature construction, frame rate,
architecture and training objective. This section isolates the stages. Mimi's residual quantiser
operates in a projected space, so the comparable pair is the projected encoder latent against the
summed codebook vectors before output projection, both pooled identically. Measured cosine between
them is 0.808 for Mimi and 0.773 for DAC, confirming a shared space.

| Representation | margin | encoder costs | quantisation costs |
|---|---|---|---|
| WavLM, continuous | +0.244 | | |
| Mimi, before quantisation | +0.132 | 0.112 | |
| Mimi, after quantisation | +0.099 | | +0.034 |
| DAC, before quantisation | +0.062 | 0.182 | |
| DAC, after quantisation | +0.087 | | −0.025 |

In both codecs the encoder is the dominant contributor. For Mimi it costs roughly three times what
quantisation does. For DAC it costs more still, and quantisation is marginally beneficial.

DAC is a purely acoustic codec with no distillation objective, running at 75 Hz against Mimi's 12.5.
Its encoder retains 47 per cent of what Mimi's does. The two converge at the token stage, where DAC
reaches 88 per cent of Mimi, because quantisation helps DAC and hurts Mimi.

**Stability.** The encoder cost is stable across readouts, at 0.116 under mean and standard
deviation pooling and 0.121 with deltas. The quantisation cost is not, ranging from +0.056 under
four-segment pooling to −0.036 with deltas, a swing sufficient to change its sign. Reported
quantisation costs are therefore contingent on a readout choice that is rarely stated.

## 4.7 The contrast-preservation score

Within each speaker-by-word cell with at least three exemplars of the minority stance, leave-one-out
nearest-centroid classification was performed on distances alone. Fifteen cells qualify, giving 191
decisions.

The appropriate baseline is the within-cell majority rate over those same decisions, which is 0.670,
because eligibility requires only three minority exemplars and eligible cells are therefore
imbalanced. WavLM and Whisper reach 0.618, HuBERT 0.613, text 0.592 and Mimi 0.560. **Every
representation falls below the baseline.** The measure is a null and does not corroborate the
probing results.

Two factors compound this. Only 15 of the available cells qualify, with 27 more one clip short of
eligibility. And the measure is sensitive to implementation, with cosine distance or prior PCA
moving scores by up to 0.07.

## 4.8 Summary

Pragmatic stance is decodable from continuous representations under lexical control, at matched
arousal, on held-out shows, and under every readout tested. The representation deployed systems
consume retains a fraction of it. That loss is concentrated in the codec encoder rather than at
quantisation, in two codecs of different design, and what survives inside Mimi sits almost entirely
in the codebook distilled from WavLM.
