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

Two features of this outcome shape how the conditions below are read. Stance is partly recoverable
from surrounding words, so the interesting quantity is what audio adds rather than whether text
fails. And the absolute level is what the prior literature predicts rather than a shortfall.
Rockwell (2000) found listeners unable to discriminate spontaneous sarcasm from non-sarcasm at all,
and Bryant and Fox Tree (2005) argue against a single dedicated ironic marker in favour of a family
of cues recognised in context. An audio condition reaching 0.73 on spontaneous delivery, with
context contributing substantially, is consistent with both. The agreement particles being hardest
is consistent in the same way, since those are the phrases whose functional ambiguity is widest
(Gravano et al., 2012).

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

| Representation | Readout | mean within-word macro-F1 | degenerate cells |
|---|---|---|---|
| Whisper encoder | embedding, 1,536 | 0.672 | 0 of 8 |
| WavLM | embedding, 2,048 | 0.659 | 0 of 8 |
| HuBERT | embedding, 2,048 | 0.616 | 0 of 8 |
| Mimi, pre-quantisation | embedding, 1,024 | 0.606 | 0 of 8 |
| Mimi, post-quantisation | embedding, 1,024 | 0.594 | 0 of 8 |
| Text, with discourse | embedding, 768 | 0.534 | 0 of 8 |
| Mimi, deployed histogram | histogram, 16,384 | 0.466 | 3 of 8 |

Whisper is the strongest representation under the lexical control, marginally ahead of WavLM. Since
the word cannot help here, this cannot be attributed to Whisper's lexical bias.

**Mimi appears twice, and the gap between the two entries is the readout rather than the
representation.** Under an embedding readout matched to what every other representation receives,
Mimi reaches 0.594 and separates all eight phrases. Under the deployed histogram it reaches 0.466 and
fails to separate three of them at all, emitting a single class for every clip on *yeah*, *sure* and
*come on* and therefore scoring exactly the within-phrase majority. Those are the only degenerate
cells in the study.

The cause is dimensionality against cell size. The histogram is 16,384 sparse dimensions and each
phrase cell holds between 58 and 129 clips, where the continuous encoders receive at most 2,048. The
same asymmetry costs 0.031 of margin when pooled over all 873 clips [4.6], and 0.128 here, because
the penalty scales with how few examples each probe sees.

Two consequences follow. Mimi under the lexical control sits above the discourse-text baseline of
0.534 rather than below it, and any statement to the contrary is a statement about the histogram.
And the readout dependence observed pooled in [4.4], where Mimi's margin moves by 0.056 across
summarisation choices while WavLM's moves by 0.009, is not a minor sensitivity but the largest single
determinant of Mimi's measured performance under this analysis. Per-phrase figures for all three
Mimi readouts are in [C.1], and `src/26_within_word_readout.py` reproduces the table.

## 4.4 Controls

**Arousal.** Stance was decoded within each arousal level separately, so that energy is constant
within each analysis. WavLM reaches 0.531 on low-arousal clips and 0.549 on high, against 0.573
pooled. Whisper reaches 0.526 and 0.514, HuBERT 0.459 and 0.518. The same test on the discrete
representations, run separately, leaves Mimi significant at both levels, at p 0.025 and p 0.017.
Margins are reduced relative to the pooled analysis in seven of the eight model-by-level cells, by
between 6 and 37 per cent, with the largest reductions in the discrete representations and the
smallest in WavLM. The exception is Mimi before quantisation at high arousal, which is essentially
unchanged. The two axes are therefore partly entangled, but stance is not reducible to arousal in any
representation tested.

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

**Probe capacity.** A non-linear probe was run on identical features and identical folds under six
capacity settings, because gains under any single setting move by up to 0.06 and some change sign, so
one configuration is not a sound basis for the conclusion. Under the primary setting the gain over
the linear probe is negative for six of the eight representations, from -0.075 for the Whisper
encoder to -0.006 for discourse text, with two small positive values, +0.019 for Mimi after
quantisation and +0.004 for the Mimi histogram. The probe is functioning rather than failing to
train, clearing its own permutation null by +0.229 on WavLM and +0.129 on Mimi at p 0.032 in both
cases.

Two consequences follow from the sweep rather than from the primary setting. Linear accessibility is
not the limiting factor, since the largest gain anywhere across the six settings is +0.025 against a
continuous-to-discrete gap of roughly 0.14, so any non-linear reserve is bounded at about a sixth of
the quantity being interpreted. And the gains that occur track headroom rather than representation
type. Every representation scoring above 0.500 gains at most +0.003 anywhere in the sweep, every
representation below it gains between +0.010 and +0.025, the largest single gain falls on the
continuous text embedding rather than on any discrete representation, and Mimi before quantisation
gains less than Mimi after it. This does not rule out a mild penalty on quantised vectors. It bounds
one.

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
| Codebooks 2, 4, 5, 6, 7 | 0.329 to 0.348 | ~0.330 | −0.001 to +0.018 | 0.159 to 0.552 |
| All 8, the deployed condition | 0.381 | 0.310 | +0.071 | 0.005 |
| Codebooks 1 to 7 only | 0.352 | 0.311 | +0.041 | 0.015 |

**Cumulatively.** Probing CB0, then CB0 to 1, and so on to the full stack, the endpoints settle the
question and the middle does not. Codebook 0 alone reaches +0.069 and all eight together reach
+0.071, so seven additional codebooks and 14,336 additional dimensions buy 0.002. In the reverse
direction the seven acoustic codebooks without CB0 reach only +0.041, and adding CB0 takes them to
+0.071. The intermediate blocks are not flat, rising to +0.092 at CB0 to 3 and falling to +0.052 at
CB0 to 6 before recovering. That excursion is non-monotonic and spans 0.040, most of the margin
itself, and it tracks accumulated dimensionality rather than accumulated content, since each
codebook adds 2,048 sparse dimensions to an 873-clip problem. It is the same effect measured at 0.031
pooled and 0.128 within a phrase [4.3], appearing here a third time.

The distilled codebook is the strongest single block. Two acoustic refinement codebooks clear their
nulls weakly, at p 0.020 and p 0.035, and the remaining five are statistically indistinguishable from
chance. What the acoustic stack does not do is add to the distilled one, since all eight together
reach 0.381 against 0.402 for codebook 0 alone, and the seven acoustic codebooks without it reach
0.352. Chapter 2 predicted the opposite distribution, and 2.3.3
reports that as a corrected expectation.

## 4.6 Locating the loss

The comparison in Table 4.1 confounds quantisation with feature construction, frame rate,
architecture and training objective. This section isolates the stages. Because the probe task holds
the word constant throughout, the margins below are margins on delivery, so a loss localised to a
stage is a loss of pragmatic rather than phonetic sensitivity. Mimi's residual quantiser
operates in a projected space, so the comparable pair is the projected encoder latent against the
summed codebook vectors before output projection, both pooled identically. Measured over all 873
clips the cosine between them is 0.821 for Mimi and 0.773 for DAC, against 0.004 for the naive
comparison that pairing would replace, confirming a shared space [3.5].

| Representation | margin | encoder costs | quantisation costs |
|---|---|---|---|
| WavLM, continuous | +0.244 | | |
| Mimi, before quantisation | +0.132 | 0.112 | |
| Mimi, after quantisation | +0.099 | | +0.034 |
| DAC, before quantisation | +0.062 | 0.182 | |
| DAC, after quantisation | +0.087 | | −0.025 |

In both codecs the encoder is the dominant contributor. For Mimi it costs roughly three times what
quantisation does. For DAC it costs more still, and quantisation is marginally beneficial.

DAC is a purely acoustic codec with no distillation objective, running at 75 Hz against Mimi's 12.5
and compared at the first eight of its 32 codebooks [3.5]. Its encoder retains 47 per cent of what
Mimi's does. The two converge at the token stage, where DAC
reaches 88 per cent of Mimi, because quantisation helps DAC and hurts Mimi.

**The deployed condition.** The rungs above stop at post-quantisation embeddings, one step short of
what Table 4.1 reports. A single run covering all four rungs on Mimi gives WavLM at +0.239, Mimi
before quantisation at +0.130, Mimi after quantisation at +0.100 and the deployed histogram at
+0.069, so on that run the encoder costs 0.109, quantisation 0.030 and the histogram readout a
further 0.031. Summarising the token stream therefore costs about as much as quantising it, and
four times as much again within a single phrase, where the cells are small enough for the
dimensionality of a sparse histogram to bite [4.3].

**Stability.** The two costs behave differently under a change of readout. The encoder cost holds at
0.116 under mean and standard deviation pooling and 0.121 with deltas. The quantisation cost ranges
from +0.056 under four-segment pooling to −0.036 with deltas, a swing sufficient to change its sign.
Reported quantisation costs are therefore contingent on a readout choice that is rarely stated.[^runs]

[^runs]: The readout comparison is a separate run from the cross-codec comparison above, which is why
the encoder cost appears as 0.116 here and 0.112 there. The difference is run-to-run variation in
permutation sampling and no argument turns on it. The encoder cost under four-segment pooling was not
computed in that run, so the stability claim rests on two readouts rather than three.

## 4.7 The contrast-preservation score

Within each speaker-by-word cell with at least three exemplars of the minority stance, leave-one-out
nearest-centroid classification was performed on distances alone. Fifteen cells qualify, giving 191
decisions.

The originally stated chance level of 0.50 is wrong, because eligibility requires only three minority
exemplars, so eligible cells are imbalanced and a constant predictor already beats it. Two
replacements are defensible and they disagree. The whole-cell majority rate is 0.670, but it counts
the held-out item's own label when determining which class is the majority, which is the leakage
leave-one-out exists to prevent. The leave-one-out majority, predicting the most frequent class among
the other n minus one, is 0.545, but it is anti-correlated with the truth on near-balanced cells,
where removing an item flips the majority against it.

WavLM and Whisper reach 0.618, HuBERT 0.613, text 0.592 and Mimi 0.560. **Every representation falls
inside the interval between the two baselines.** The measure therefore does not discriminate in
either direction. It is uninformative rather than a clean failure, and it neither corroborates the
probing results nor contradicts them.

The measure's closest established relative is the minimal-pair ABX discriminability task (Schatz et
al., 2013), which is likewise training-free and defined on distances between representations, and
which is reported as the acoustic-level metric inside multi-level evaluation suites for exactly that
reason (Dunbar et al., 2021). ABX avoids the difficulty encountered here by fixing the comparison as
a triplet rather than estimating a class centroid, so it does not depend on cell size in the way a
nearest-centroid measure does. That is the design lesson, and [Ch.6] takes it up.

Two factors compound this. Only 15 of the available cells qualify, with 27 more one exemplar short of
eligibility. And the measure is sensitive to implementation, with cosine distance or prior PCA
moving scores by up to 0.07. Baselines and cell counts are computed exactly, from labels alone, in
`src/23_cps_baseline.py`.

