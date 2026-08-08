# Limitations and future work

## What the primary results rest on

The core probing results are estimated over all 873 clips and are robust. Stance
decodability, the per-phrase within-word contrast, the matched-arousal test and the
held-out-show control are each significant against an empirical permutation null, and each
is stable across context windows and fold-grouping schemes. The matched-arousal control is
stronger than originally reported, because it has since been run on every representation
rather than only the continuous ones, and stance survives at fixed arousal in all of them.

## The contrast-preservation score does not discriminate

This is stated plainly because an earlier draft described it as weak corroboration, which
was wrong.

CPS was reported against a stated chance level of 0.50 on the grounds that the within-cell
contrast is binary. That reference is incorrect. Cell eligibility requires only three
exemplars of the minority stance, so eligible cells are class-imbalanced and a constant
predictor already beats 0.50.

An intermediate draft replaced it with the within-cell majority rate of **0.670** and said every
representation falls below it. That was also too strong, in the opposite direction. The whole-cell
majority counts the held-out item's own label when deciding which class is the majority, which is
exactly the leakage leave-one-out is designed to prevent, so it is optimistic. The leave-one-out
majority, which sees only what the classifier sees, is **0.545**, but it is anti-correlated with the
truth on near-balanced cells and so is pessimistic. Neither is clean.

Over the same 15 cells and 191 decisions the defensible interval is therefore **[0.545, 0.670]**, and
every representation falls inside it, WavLM and Whisper at 0.618, HuBERT at 0.613, text at 0.592 and
Mimi at 0.560. The correct report is that the measure does not discriminate in either direction. It
is uninformative rather than a clean null, and it should not be presented as evidence for or against
the hypothesis. Both baselines and the cell counts are computed exactly from labels alone in
`src/23_cps_baseline.py`, so this no longer rests on a figure with no provenance.

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
between 6 and 37 per cent in seven of the eight cells and not at all in the eighth,
so the two axes are partly entangled, but stance is not
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

In the ladder, WavLM contributes 2,048 pooled features against Mimi's 1,024, so part of the
0.112 attributed to distillation and the codec encoder could be dimensionality rather than
information loss. The quantisation estimate does not suffer from this, because pre-quantisation
and post-quantisation representations have identical dimensionality, identical pooling and an
identical source. Trust the 0.034 and treat the 0.112 as a ceiling.

## The distillation attribution is associational

Section 3 of the discussion attributes Mimi's comparative retention of pragmatic stance to its
WavLM distillation objective. Two comparisons support that, one across codecs and one within Mimi,
and the internal one holds architecture, frame rate, training data and audio constant. Neither is
the decisive experiment, which would be training the same codec with and without the distillation
objective and comparing. That is beyond the compute available here, so the claim is that
distillation is associated with better retention, twice and once cleanly, rather than that it
causes it.

The cross-codec half of the evidence carries a further confound worth naming. DAC runs at 75 Hz
with 1024-entry codebooks against Mimi's 12.5 Hz and 2048, so frame rate and codebook geometry vary
alongside the training objective. The direction of the effect is large, roughly a factor of two,
but it is not a clean ablation of distillation alone.

## Linear probing measures accessibility, and that was tested

A linear probe reports whether information is linearly accessible rather than whether it is
present, so a low score is in principle ambiguous between a representation having lost the
distinction and a representation encoding it in a form the probe cannot reach. That ambiguity would
bear most heavily on the continuous-against-discrete comparison, since quantised vectors occupy a
finite set of fixed positions and there is no guarantee they are as linearly separable as a
continuous manifold carrying equivalent information.

The concern was tested rather than argued around, and the first version of that test was reported
too strongly. An earlier draft said the non-linear probe recovered no additional stance from any
representation and that Mimi gained least of all, which would have meant the direction ran against
the confound. That rested on a single probe configuration whose generating script was not preserved,
and it does not hold. Re-run under six capacity settings, Mimi after quantisation is in fact the
discrete representation that gains most consistently, positive in five of six. A mild penalty on
quantised vectors therefore cannot be ruled out and is not ruled out here.

What the sweep does establish is a bound, and the bound is what the argument needs. The largest gain
observed anywhere across the six settings and eight representations is +0.025, against a
continuous-to-discrete gap of roughly 0.14. Any probe-reach explanation is therefore confined to
about a sixth of the quantity being interpreted. The probe is functioning rather than failing to
train, clearing its own permutation null on both WavLM and Mimi at p 0.032.

A second observation weakens the confound further without depending on it being absent. The gains
track headroom rather than representation type. Every representation scoring above 0.500 under the
linear probe gains at most +0.003 anywhere in the sweep, every representation scoring below 0.500
gains between +0.010 and +0.025, and the largest single gain falls on the continuous text embedding
rather than on any discrete representation. Mimi before quantisation also gains less than Mimi after
it, which a discreteness account would not predict. The pattern is better explained by how much
unexplained variance a weak representation leaves available than by discreteness.

Three residual points remain. The non-linear probe was kept deliberately small and strongly
regularised, because a sufficiently powerful probe can learn a task from almost any representation
and thereby report on itself, so this rules out modest non-linear encoding rather than any
conceivable encoding. Accessibility to a probe is not the same as usability by a downstream model,
which is why the claims in the discussion are framed as a ceiling rather than a prediction about
system behaviour. And the episode from which this section was rewritten is itself a limitation worth
recording, in that a result reported from an unpreserved script could not be regenerated, which is
why `src/22_nonlinear_probe.py` now produces `results/linear_vs_nonlinear_probe.txt` deterministically.

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
speech would probably be needed to guarantee coverage. More power would also narrow the gap between
the two candidate baselines, since both artefacts that separate them, the leakage in one and the
near-balanced-cell pathology in the other, shrink as cells grow. That is the main reason to expect a
better-powered version to be interpretable at all, rather than to expect it to reverse the sign.

Two methodological refinements would help. The distance metric and any dimensionality
reduction should be fixed in advance rather than chosen after seeing results. And a measure
defined on continuous scores, such as the area under the ROC curve of within-cell
inter-stance distances, would use the available evidence more efficiently than hard
leave-one-out classification and degrade more gracefully at small samples.

Independently, enlarging the neutral-stance sample and the thinner per-word cells would
sharpen the pooled three-way and per-phrase analyses that already carry the conclusions.
