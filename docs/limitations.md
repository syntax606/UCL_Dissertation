# Limitations and future work

## What the primary results rest on

The core probing results are estimated over all 873 clips and are robust. Stance
decodability, the per-phrase within-word contrast, the matched-arousal test and the
held-out-show control are each significant against an empirical permutation null, and each
is stable across context windows and fold-grouping schemes. The matched-arousal control is
stronger than originally reported, because it has since been run on every representation
rather than only the continuous ones, and stance survives at fixed arousal in all of them.

## The contrast-preservation score is a null result

This is stated plainly because an earlier draft described it as weak corroboration, which
was wrong.

CPS was reported against a stated chance level of 0.50 on the grounds that the within-cell
contrast is binary. That reference is incorrect. Cell eligibility requires only three
exemplars of the minority stance, so eligible cells are class-imbalanced, and the
appropriate baseline is the within-cell majority rate. Measured over the same 15 cells and
191 leave-one-out decisions, that baseline is **0.670**. Every representation falls below
it, WavLM and Whisper at 0.618, HuBERT at 0.613, text at 0.592 and Mimi at 0.560. The
measure therefore does not support the hypothesis, and it should be reported as a null
rather than as directional agreement.

Two things compound this. The measure is underpowered, since only 15 of the available
speaker-by-word cells clear the eligibility threshold and 27 more sit exactly one clip
short. It is also sensitive to implementation choices, with substituting cosine for
Euclidean distance or applying PCA before scoring moving per-model scores by up to 0.07.
Rather than select the most favourable variant, the full sensitivity table is reported.

## The strong security hypothesis was tested and not supported

It was hypothesised that these representations might encode activation and be read
downstream as though it were intent, so that a system would in effect mistake loudness for
emotional stance. That is testable directly, since holding arousal constant should remove
any stance signal that is really arousal in disguise.

It does not. Stance remains significant within each arousal level in every representation,
including the discrete ones, at p 0.025 and p 0.017 for the Mimi histogram. Margins fall by
roughly a quarter to a third, so the two axes are partly entangled, but stance is not
reducible to arousal anywhere tested. The claim that these systems confuse the two is
therefore not supported by this data and is not made.

What the data does support is an asymmetry of availability rather than a confusion, and
that weaker claim is developed in the discussion.

## Feature construction is confounded with representation type

The headline Mimi figure summarises the code stream as per-codebook unigram histograms,
which is a sparse and order-free tally, roughly 125 tokens spread over 2,048 bins per
codebook with about 95 percent of bins empty. The continuous encoders are summarised as
mean and standard deviation over roughly 500 dense frames. Both discard order, so that much
is symmetric, but the sparsity is not, and it disadvantages the discrete representation for
reasons unrelated to quantisation.

This is quantified rather than left as a worry. Decomposing the gap shows the histogram
readout costs 0.031 of margin, which is almost exactly what quantisation itself costs. Any
future version of this study should use embedding pooling for the discrete representation
as well, so that the only difference between conditions is quantisation.

## The distillation estimate is an upper bound

In the three-point ladder, WavLM contributes 2,048 pooled features against Mimi's 1,024, so
part of the 0.109 attributed to distillation and the codec encoder could be dimensionality
rather than information loss. The quantisation estimate does not suffer from this, because
pre-quantisation and post-quantisation representations have identical dimensionality,
identical pooling and an identical source. Trust the 0.030 and treat the 0.109 as a ceiling.

## Other constraints

Target-only text is at chance only within a phrase, not pooled across phrases, because the
eight phrases differ in their stance base rates and a probe can score above chance from word
identity alone. The pooled figure of 0.487 should be read with that artefact in mind.

Speaker identity is controlled by grouping folds by show rather than by speaker, since the
corpus carries show names but no speaker labels. Guests recur across shows, so this does not
guarantee that train and test share no speaker, and the control should be described as
held-out shows rather than unseen speakers.

Neutral stance is concentrated in the agreement particles, and high-arousal neutral is
represented by only 26 clips, so any analysis crossing those two axes is thin.

## Future work

A better-powered training-free measure would require depth-first collection, assembling a
smaller set of speaker-by-word cells each populated with many exemplars of both stances, so
that within-cell centroids are estimated stably. Naturalistic political-podcast audio makes
this hard, since matched within-speaker minimal pairs are rare, and scripted or elicited
speech would probably be needed to guarantee coverage. Given that every representation
currently sits below the correct baseline, more power would most likely sharpen a null
rather than reverse it.

Two methodological refinements would help. The distance metric and any dimensionality
reduction should be fixed in advance rather than chosen after seeing results. And a measure
defined on continuous scores, such as the area under the ROC curve of within-cell
inter-stance distances, would use the available evidence more efficiently than hard
leave-one-out classification and degrade more gracefully at small samples.

Independently, enlarging the neutral-stance sample and the thinner per-word cells would
sharpen the pooled three-way and per-phrase analyses that already carry the conclusions.
