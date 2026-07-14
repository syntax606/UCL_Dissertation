# Limitations and future work

**Limitations.** The primary probing results (stance decodability, the per-phrase
within-word contrast, the matched-arousal test, and the speaker-held-out control) are
estimated over all 873 clips and are robust: each is significant under an episode-cluster
permutation test (p ≤ 0.01) and stable across context windows and fold-grouping schemes.
The training-free Contrast-Preservation Score (CPS) is weaker. Because it requires minimal
pairs in the strictest possible sense, the same speaker producing the same lexical item
with both a clearly affiliative and a clearly adversarial delivery, only 15
speaker-by-word cells met the threshold of at least three exemplars per stance, yielding
191 leave-one-out decisions in total. At this sample size the measure is sensitive to
arbitrary implementation choices: substituting cosine for Euclidean distance, or reducing
dimensionality by PCA before scoring, shifts the per-model scores by up to 0.07 and, in
some configurations, erodes the separation between the continuous representations and the
discrete Mimi tokens that is stable everywhere else. Rather than select the variant most
favourable to the hypothesis, I report CPS only as a corroborating measure and include the
full metric-by-preprocessing sensitivity table; the substantive claims rest on the
well-powered probes, with which CPS is directionally consistent (continuous audio above
discrete tokens) but too noisy to rank models reliably.

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
