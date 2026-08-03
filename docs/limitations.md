# Limitations and future work

**Limitations.** The primary probing results (stance decodability, the per-phrase
within-word contrast, the matched-arousal test, and the show-held-out control) are
estimated over all 873 clips and are robust: each is significant under a label-permutation
test (p ≤ 0.01) and stable across context windows and fold-grouping schemes. Four
qualifications on that headline follow.

**The Contrast-Preservation Score does not clear its own baseline.** CPS was reported
against a stated chance level of 0.50, on the reasoning that a two-class leave-one-out
decision is a coin flip. That reasoning does not hold for the cells this measure actually
uses. Eligibility requires only three exemplars of the minority stance, so the qualifying
cells are class-imbalanced, and the appropriate reference is the within-cell majority rate
rather than 0.50. On the 15 qualifying cells and their 191 leave-one-out decisions that rate
is **0.670**. Every representation scores below it: wavlm 0.618, whisper 0.618, hubert 0.613,
text 0.592, mimi 0.560. Read against the correct baseline, view F therefore provides **no
positive evidence of contrast preservation** — it is a null result, not a weak corroboration,
and it should not be cited as directionally supporting the probe findings even though the
ordering of models within it happens to match. The sample-size and metric-sensitivity
concerns below are real but secondary to this: fixing the baseline changes the sign of the
conclusion, not merely its confidence.

Because the measure requires minimal pairs in the strictest sense — the same *show*
producing the same lexical item with both a clearly affiliative and a clearly adversarial
delivery — only 15 show-by-word cells met the threshold of at least three exemplars per
stance. At this sample size the measure is additionally sensitive to arbitrary
implementation choices: substituting cosine for Euclidean distance, or reducing
dimensionality by PCA before scoring, shifts the per-model scores by up to 0.07. Rather
than select the variant most favourable to the hypothesis, I include the full
metric-by-preprocessing sensitivity table; the substantive claims rest on the well-powered
probes alone.

**Best-layer selection is not nested.** For the audio encoders the reported layer is the one
that maximises out-of-fold macro-F1, and that same out-of-fold score is then reported as the
result, so view A's audio figures are optimistically biased. The permutation null compounds
this: it refits at the fixed winning layer rather than re-running the selection under
permutation, so the p-values are anticonservative. The empirical magnitude is small — the
layer curves have broad plateaus, and the winning layer exceeds the runner-up by only 0.018
(WavLM), 0.010 (HuBERT) and 0.003 (Whisper), with top-three layer means of 0.561, 0.510 and
0.561 — so the substantive ordering of representations is unaffected. But the point estimates
should be read as upper bounds, and a properly nested selection would be the correct
procedure. Mimi and the text baselines have no layer axis and are unaffected.

**The permutation test is not episode-clustered.** The confidence intervals are: they come
from a bootstrap that resamples whole episodes, respecting the nesting of clips within
episodes. The permutation test does not — it shuffles stance labels freely. Because 654 of
the 753 episodes contribute a single clip, the practical effect is small, but the null is not
clustered and should not be described as though it were.

**Pooled decodability is partly lexical, and the speaker control is a show control.** The
per-phrase stance base rates are strongly non-uniform, so word identity alone is informative:
the target-only text embedding, which encodes nothing but which word was spoken, reaches
0.487 macro-F1 against a 0.313 null. The pooled three-way figures in view A therefore
overstate how much is attributable to delivery, and the within-word analysis in view C is
the result the design's claim rests on. Separately, the "speaker" control groups folds by
*show*, not speaker: shows have multiple participants and guests recur across shows, so
train and test may share a speaker even when they share no show. Both facts are reported
here rather than in the results chapter because they qualify how those results should be
read, not what they are.

**Future work.** A better-powered training-free test would require targeted, depth-first
data collection rather than the breadth-first sampling used here: deliberately assembling a
smaller set of speaker-by-word cells, each populated with many exemplars of both stances,
so that within-cell centroids are estimated stably. This is difficult in naturalistic
political-podcast audio, where matched within-speaker minimal pairs are rare, and would
likely need scripted or elicited speech to guarantee coverage. Two methodological
refinements would complement such data. First, the distance metric and any dimensionality
reduction should be fixed in advance (ideally pre-registered) rather than chosen post hoc,
removing the sensitivity documented above. Second, a distance-based separation measure
defined on continuous scores, for example the area under the ROC curve of within-cell
inter-stance distances, would use the available evidence more efficiently than hard
leave-one-out classification and degrade more gracefully at small sample sizes.
Independently, enlarging the neutral-stance sample (concentrated here in the agreement
particles) and the thinner per-word cells would sharpen the pooled three-way and per-phrase
analyses that already carry the study's conclusions.
