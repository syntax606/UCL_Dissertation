# Chapter 4: Results

*(Draft. All figures from `results/`. Margins are macro-F1 minus the mean of that configuration's own
permutation null, 200 permutations unless stated. Intervals are episode-cluster bootstrap. The
primary window is W2 and the primary readout is mean and standard deviation pooling, both fixed in
advance [3.5, 3.6]. Methodological checks that bear on how these figures should be read, rather than
on what they say, are in Appendix [G].)*

## 4.1 The premise check

Two auxiliary annotators judged a counterbalanced 60-clip subset against a hidden reference.
Transcript with discourse context reached 0.65 accuracy and audio with transcript reached 0.73,
against a three-way chance level of 0.33. Audio therefore adds a real increment over the words, while
discourse context alone recovers a substantial part of the contrast. The agreement particles were
hardest even from audio, at 0.58 for *okay* and 0.64 for *yeah*, which is expected given that those
are the phrases whose functional ambiguity is widest (Gravano et al., 2012).

The absolute level is what the prior literature predicts rather than a shortfall. Rockwell (2000)
found listeners unable to discriminate spontaneous sarcasm from non-sarcasm at all, and Bryant and
Fox Tree (2005) argue against a single dedicated ironic marker in favour of a family of cues
recognised in context. Both predict exactly this, a real audio increment on spontaneous delivery with
context contributing substantially.

Scoring the models on those same sixty clips, which is the only like-for-like comparison available,
places the best model condition at 0.533 against the human 0.730 [G.1]. The representations examined
below therefore carry something closer to half of what a listener recovers from the same audio, and
the figures that follow should be read as relative to one another rather than as approaching human
performance.

## 4.2 Pooled stance decodability

Table 4.1 reports the three-way stance probe on the primary window. Chance is the mean of each
configuration's own permutation null, for the reasons in [3.6].

| Representation | layer | macro-F1 | 95% CI | chance | margin | p |
|---|---|---|---|---|---|---|
| WavLM | 20 | 0.573 | [0.54, 0.61] | 0.332 | +0.241 | 0.005 |
| Whisper encoder | 9 | 0.564 | [0.53, 0.60] | 0.332 | +0.232 | 0.005 |
| HuBERT | 23 | 0.520 | [0.49, 0.56] | 0.334 | +0.186 | 0.005 |
| Text, target word only | | 0.487 | [0.46, 0.52] | 0.313 | +0.174 | 0.005 |
| eGeMAPS, 88 functionals | | 0.431 | | 0.327 | +0.104 | 0.010 |
| Mimi, all 8 codebooks | | 0.381 | [0.35, 0.41] | 0.311 | +0.070 | 0.005 |
| Text, with discourse | | 0.378 | [0.35, 0.41] | 0.333 | +0.045 | 0.010 |

Every representation exceeds its own null. The three continuous encoders clear it by 0.19 to 0.24,
while Mimi clears it by 0.070 and discourse text by 0.045.

Three entries need comment. **eGeMAPS** is the hand-crafted comparison, and it establishes that
WavLM's margin is roughly 2.3 times what a standard acoustic feature set recovers, so the deep
representation is doing work beyond pitch and energy. It also places the deployed Mimi condition
**below** 88 classical features, an ordering that holds under the lexical control where eGeMAPS
reaches 0.550 against Mimi's 0.466. **Whisper** performs within 0.01 of WavLM despite being a
supervised transcription model and half the size, 13 layers of 768 units against 25 of 1,024, which
[4.5] returns to. And the **target-only text** condition at 0.487 should not be read as text
recovering stance, since the eight phrases differ in their stance base rates and a probe can score
from word identity alone. It is at chance only within a phrase, which the next section enforces.

## 4.3 The lexical control

Within each phrase the probe attempts that phrase's dominant binary stance contrast, so word identity
carries no information.

| Representation | Readout | mean within-word macro-F1 |
|---|---|---|
| Whisper encoder | embedding, 1,536 | 0.672 |
| WavLM | embedding, 2,048 | 0.659 |
| HuBERT | embedding, 2,048 | 0.616 |
| Mimi, pre-quantisation | embedding, 1,024 | 0.606 |
| Mimi, post-quantisation | embedding, 1,024 | 0.594 |
| eGeMAPS | 88 functionals | 0.550 |
| Text, with discourse | embedding, 768 | 0.534 |
| Mimi, deployed histogram | histogram, 16,384 | 0.466 |

Whisper is the strongest representation under the lexical control, marginally ahead of WavLM. Since
the word cannot help here, this cannot be attributed to Whisper's lexical bias.

Mimi appears twice, and the difference between the two entries is the readout rather than the
representation. Given an embedding readout matched to what every other representation receives, it
reaches 0.594 and separates all eight phrases. Given the deployed 16,384-dimensional histogram it
reaches 0.466 and fails to separate three of them at all. The cause is sparse dimensionality against
cells of 58 to 129 clips, and the full decomposition is in [G.2]. What matters for the argument is
that Mimi's measured within-word performance is determined more by how the token stream is summarised
than by anything the tokens contain.

## 4.4 Controls

**Arousal.** Stance was decoded within each arousal level separately, so that energy is constant
within each analysis. WavLM reaches 0.531 on low-arousal clips and 0.549 on high, against 0.573
pooled. Whisper reaches 0.526 and 0.514, HuBERT 0.459 and 0.518, and Mimi remains significant at both
levels, at p 0.025 and p 0.017. Margins are reduced in seven of the eight model-by-level cells, by
between 6 and 37 per cent. The two axes are therefore partly entangled, but stance is not reducible
to arousal in any representation tested.

**Speaker.** Regrouping folds by show moves WavLM from 0.573 to 0.530, Whisper from 0.564 to 0.536
and Mimi from 0.381 to 0.362, with HuBERT falling further from 0.520 to 0.450. The probe is therefore
not principally recovering speaker identity. Because the corpus carries show names rather than
speaker labels, this control is properly described as held-out shows rather than unseen speakers.

**Context window.** Across the local, segment and discourse windows WavLM scores 0.561, 0.573 and
0.511, Whisper 0.545, 0.564 and 0.531, HuBERT 0.537, 0.520 and 0.488. Performance is flat and does
not rise with more surrounding speech, which indicates the continuous encoders are reading delivery
rather than leaning on discourse context. Mimi is the exception, rising slightly to 0.411 at the
discourse window.

**Readout and probe capacity.** Two further controls are reported in [G.2] and [G.3]. Summarisation
choice is immaterial for WavLM, moving its margin by 0.009 across three readouts, and material for
Mimi, moving it by 0.056. And a non-linear probe run under six capacity settings recovers at most
+0.025 anywhere, against a continuous-to-discrete gap of roughly 0.14, so linear accessibility is not
the limiting factor and the reported figures describe content rather than reach.

## 4.5 Where the contrast lives

**Across layers.** WavLM rises from 0.402 at layer 0 to a peak of 0.573 at layer 20 of 24, then
declines to 0.490 at the final layer. HuBERT is flatter and noisier, peaking late at 0.520. Whisper
rises to 0.561 by layer 8 and then plateaus across its top third, reaching 0.564, 0.539, 0.557 and
0.548 at layers 9 to 12.

The WavLM curve matches the three-stage account in which upper layers abstract toward linguistic
content and shed paralinguistic detail. Whisper does not show that decline. Its supervised
transcription objective was expected to reduce acoustic information in the final encoder layers and
on this task it does not, which is consistent with prior findings that ASR encoders retain
paralinguistic content (Gong et al., 2023; Ma et al., 2026) and extends them to pragmatic stance
under a lexical control.

**Across Mimi's codebooks.** Each codebook was probed alone, with its own permutation null.

| Block | macro-F1 | chance | margin | p |
|---|---|---|---|---|
| Codebook 0, WavLM-distilled | 0.402 | 0.330 | +0.072 | 0.005 |
| Codebook 1 | 0.377 | 0.331 | +0.046 | 0.020 |
| Codebook 3 | 0.368 | 0.331 | +0.037 | 0.035 |
| Codebooks 2, 4, 5, 6, 7 | 0.329 to 0.348 | ~0.330 | −0.001 to +0.018 | 0.159 to 0.552 |
| All 8, the deployed condition | 0.381 | 0.310 | +0.071 | 0.005 |
| Codebooks 1 to 7 only | 0.352 | 0.311 | +0.041 | 0.015 |

The distilled codebook is the strongest single block. Two acoustic codebooks clear their nulls weakly
and the remaining five are indistinguishable from chance. What the acoustic stack does not do is add
to the distilled one. Probed cumulatively, codebook 0 alone reaches +0.069 and all eight together
reach +0.071, so seven further codebooks and 14,336 further dimensions buy 0.002, while the seven
acoustic codebooks without codebook 0 reach only +0.041 [G.4]. Chapter 2 predicted the opposite
distribution and 2.2 reports that as a corrected expectation.

## 4.6 Locating the loss

The comparison in Table 4.1 confounds quantisation with feature construction, frame rate,
architecture and training objective. This section isolates the stages. Because the word is held
constant throughout, the margins below are margins on delivery, so a loss localised to a stage is a
loss of pragmatic rather than phonetic sensitivity. Mimi's residual quantiser operates in a projected
space, so the comparable pair is the projected encoder latent against the summed codebook vectors
before output projection, both pooled identically. Measured over all 873 clips their cosine is 0.821
for Mimi and 0.773 for DAC, against 0.004 for the naive comparison that pairing would replace [3.5].

| Representation | margin | encoder costs | quantisation costs |
|---|---|---|---|
| WavLM, continuous | +0.244 | | |
| Mimi, before quantisation | +0.132 | 0.112 | |
| Mimi, after quantisation | +0.099 | | +0.034 |
| DAC, before quantisation | +0.062 | 0.182 | |
| DAC, after quantisation | +0.087 | | −0.025 |

**In both codecs the encoder is the dominant contributor.** For Mimi it costs roughly three times
what quantisation does. For DAC it costs more still, and quantisation is marginally beneficial.

DAC is a purely acoustic codec with no distillation objective, running at 75 Hz against Mimi's 12.5
and compared at the first eight of its 32 codebooks [3.5]. Its encoder retains 47 per cent of what
Mimi's does, and the two converge at the token stage where DAC reaches 88 per cent of Mimi, because
quantisation helps DAC and hurts Mimi.

Adding the deployed histogram as a fourth rung, a single run gives WavLM +0.239, Mimi before
quantisation +0.130, after quantisation +0.100 and the deployed histogram +0.069, so the encoder
costs 0.109, quantisation 0.030 and the histogram readout a further 0.031. Summarising the token
stream costs about as much as quantising it. The stability of these two costs under a change of
readout is reported in [G.2].

## 4.7 What the codec retains

The decomposition above locates the loss without saying what is lost. If the encoder discards the
acoustic detail that stance is built from, that would explain it. This section tests that directly by
asking how well each acoustic cue group can be recovered from each rung, using ridge regression
cross-validated by episode and reported as a fraction of what WavLM supports.

| Representation | contour | level | voice quality | temporal | spectral |
|---|---:|---:|---:|---:|---:|
| WavLM, ceiling, absolute R² | 0.283 | 0.607 | 0.225 | 0.557 | 0.345 |
| Mimi, pre-quantisation | 153% | 147% | 158% | 106% | 170% |
| Mimi, post-quantisation | 139% | 143% | 139% | 97% | 162% |
| Mimi, deployed histogram | 98% | 106% | 109% | 78% | 121% |
| DAC, pre-quantisation | 122% | 130% | 123% | 68% | 161% |
| DAC, post-quantisation | 117% | 127% | 113% | 63% | 157% |

**The codecs recover the acoustic cues better than WavLM does**, and they do so with half the
features, 1,024 dimensions against 2,048, so the comparison runs against them. That includes the
contour group, which is what stance is built from. Only the temporal group falls below WavLM, and it
falls furthest for DAC at 75 Hz rather than Mimi at 12.5, which is the wrong direction for a
frame-rate account.

Splitting the same 88 features by what they carry confirms where the two annotated axes live. Setting
aside the spectral block, which holds 51 of the 88 and is not size-comparable, stance is carried most
by contour at +0.082 against +0.052 for level and +0.044 for voice quality, and arousal most by voice
quality at +0.110 against +0.085 and +0.084. Removing the level cues from the full set leaves stance
decoding unchanged at +0.107 against +0.104. Arousal is separately predictable from eGeMAPS at
+0.108, so the annotated axis is grounded in measured acoustics rather than resting on annotator
judgement alone.

Taken together these say something the ladder alone does not. The codec has not discarded the
prosody. It represents the acoustic cues stance is built from more faithfully than the model that
decodes stance best. What it lacks is the organisation that makes an interpersonal category readable
off those cues, and Chapter 5 takes that up.
