# Chapter 2: Literature Review

*(Draft. Target budget ~2,300 words. Compressed from the long-form draft, and citations are the
verified set in docs/literature_references_verified.md. All quoted material and all figures
attributed to other papers have been checked against those papers.)*

## 2.1 The speech-language-model turn and discrete speech tokens

Discrete audio tokens have become a general-purpose interface for speech and audio modelling.
They underpin residual-quantisation codecs built for compression (Zeghidour et al., 2021; Défossez
et al., 2022; Kumar et al., 2023), tokenisers built to feed language models (Zhang et al., 2024a;
Ye et al., 2024; Défossez et al., 2024), full-duplex speech-to-speech dialogue systems (Défossez et
al., 2024), and a growing body of work on emotion recognition and paralinguistic modelling from
codes rather than waveforms (Sun et al., 2026; Zhang et al., 2024b; Ren et al., 2024). The design
space is active enough to have generated its own evaluation literature, including benchmarks for
downstream utility (Mousavi et al., 2026), reconstruction and semantic fidelity (Deng et al., 2025;
Wang et al., 2025b), behavioural evaluation of deployed systems (Jiang et al., 2025; Yang et al.,
2026), and two recent reviews (Guo et al., 2025; Arora et al., 2025).

What unites these is that the tokens, not the audio, are what the downstream model receives. That
makes the informational content of the tokenisation step a first-order design question rather than
an implementation detail, and it is the question this dissertation pursues, specifically whether the
tokens preserve the parts of speech that are invisible in the transcript.

The literature divides speech tokens into two families. *Acoustic* tokens derive from neural
codecs optimised for reconstruction and preserve signal-level detail. *Semantic* tokens derive
from self-supervised or supervised speech models and encode phonetic or linguistic content.[^sem]
This matters directly here, because pragmatic meaning sits in neither category cleanly, since
sarcasm, reluctance, and ironic agreement are not lexical content, but they are also not the
arbitrary acoustic detail a codec preserves for reconstruction. They live in a middle band of
prosody, timing, and emphasis that current tokenisation was not designed to retain.

[^sem]: The term is a misnomer. So-called semantic tokens are better described as phonetic units
(Sicherman and Adi, 2023), and generally lack semantic content in the linguistic sense (Arora et
al., 2025), a point the review literature states explicitly (Guo et al., 2025) and which codec
probing confirms directly (Shi et al., 2026). This dissertation retains the conventional term for
consistency with the systems it describes, and section 2.2 sets out why the distinction, however
resolved, does not settle anything about pragmatic force.

That division has a design history, and it matters here because the present study measures the
consequence of one step in it. Neural codecs established the residual-quantisation architecture in
service of reconstruction, first in SoundStream (Zeghidour et al., 2021) and then in EnCodec
(Défossez et al., 2022) and the Descript Audio Codec (Kumar et al., 2023), all optimised so that a
waveform can be rebuilt from a small number of codes. SpeechTokenizer (Zhang et al., 2024a)
introduced the modification that concerns this dissertation, guiding the first quantiser with a
self-supervised teacher so that the leading code stream carries content while later streams carry
refinement. Mimi (Défossez et al., 2024) inherits that arrangement with WavLM as the teacher, and
X-Codec (Ye et al., 2024) generalises it by injecting teacher features before quantisation rather
than only supervising after it. The lineage is therefore one of adding supervision to a
reconstruction objective, and which supervision is added determines what the tokens retain. This
study uses the Descript codec as its undistilled comparison precisely because it sits on the
reconstruction-only branch.

Benchmark evidence confirms that this middle band is where discretisation is weakest. The
Discrete Audio and Speech Benchmark (Mousavi et al., 2026) finds discrete representations
systematically less robust than continuous ones, with preserving phonetic content, speaker
identity, and paralinguistic cues simultaneously an open problem. The relevance for deployed
systems is sharpened by speech-to-speech behavioural evaluations, where S2S-Arena (Jiang et al., 2025)
and ParaS2S (Yang et al., 2026) both document that deployed systems underperform on
paralinguistic dimensions, which is the behavioural shadow of the representational loss this
study probes directly.

## 2.2 The representations under test

This dissertation compares six representations on a single task, recovering the pragmatic force of a
phrase whose lexical content is held constant. Table 2.1 gives their characteristics. They span four
types. Self-supervised continuous encoders (WavLM, HuBERT) are trained by masked prediction without
transcription targets. A supervised continuous encoder (the Whisper encoder) is trained to
transcribe. Two discrete neural codecs differ in exactly the property under investigation, since
Mimi distils from a self-supervised teacher and the Descript codec does not. A transcript embedding
serves as the control.

**Table 2.1.** Representations under test. Frame rate in Hz. Layers times hidden width for the
continuous encoders, codebook vocabulary for the codecs. Specifications are read from the
checkpoints and from the primary papers.

| Representation | SR | FR | Layers × hidden | Vocab | Type | Quantisation |
|---|---|---:|---|---:|---|---|
| WavLM-large (Chen et al., 2022) | 16 kHz | 50 | 25 × 1024 | | continuous, self-supervised | none |
| HuBERT-large (Hsu et al., 2021) | 16 kHz | 50 | 25 × 1024 | | continuous, self-supervised | none |
| Whisper-small encoder (Radford et al., 2023) | 16 kHz | 50 | 13 × 768 | | continuous, supervised | none |
| Mimi (Défossez et al., 2024) | 24 kHz | 12.5 | | 2048 | hybrid, 8 codebooks, WavLM-distilled | RVQ |
| DAC (Kumar et al., 2023) | 24 kHz | 75 | | 1024 | acoustic, 32 codebooks, first 8 used | RVQ |
| MPNet text embedding | | | 768 | | continuous, text | none |

The two codecs are matched at eight codebooks rather than at equal bitrate, so the comparison holds
quantiser count constant while frame rate and codebook geometry vary. That is a limitation of the
cross-codec contrast and is stated as such [Ch.6], but it is the closest available approximation to
an ablation of the distillation objective without training a codec.

**Continuous encoders.** HuBERT and WavLM share a masked-prediction architecture and a
well-documented layer-wise division of labour, in which lower layers encode local acoustic detail,
middle layers integrate prosodic and contextual information, and upper layers abstract toward
linguistic content while suppressing speaker cues (Pasad et al., 2021; Chiu et al., 2025). The
mid-layer optimum is not absolute, since ParaLBench (Zhang et al., 2024b) finds the strongest WavLM
performance on paralinguistic tasks away from the final layers, which is why this study probes the
full stack. WavLM's noise and overlapped-speech augmentation is the documented reason it tends to
beat HuBERT on speaker and paralinguistic tasks, which also makes it strong on speaker identity and
therefore a nuisance for any distance-based measure [3.6]. The Whisper encoder is the theoretically
interesting case, since a transcription objective predicts a lexical bias the self-supervised
encoders do not share. If Whisper recovers a pragmatic contrast it may be leaning on surrounding
lexical material rather than on phrase-level delivery, and the context-window comparison [Ch.4] is
the instrument that separates those routes.

**Discrete tokenisation and Mimi.** This study uses Mimi (Défossez et al., 2024) rather than a
pure acoustic codec, because Mimi is the input tokeniser for deployed speech-to-speech systems
and is therefore the deployment-relevant test case rather than a strawman. Mimi applies residual
quantisation at 12.5 Hz. Its first codebook is distilled from WavLM and the remaining seven carry
acoustic refinement. A model built on Mimi consumes the whole stack, which is why the headline
condition in this study is all eight codebooks together rather than any subset of them.

The naming of the first codebook requires care, and the care is of a specific kind. Codec-probing
work (Shi et al., 2026) shows that distillation from WavLM injects phonetic rather than semantic
knowledge, and an earlier version of this chapter inferred from that a prediction that pragmatic
force would sit in the acoustic-refinement codebooks rather than in codebook 0. Chapter 4 shows the
reverse [4.5]. The inference was a category error. The semantic-versus-phonetic axis concerns what a
stream encodes about which words were said, and pragmatic force is orthogonal to that axis, so a
finding either way licenses no inference about whether a stream retains delivery. What predicts the
outcome is the distillation source rather than the stream's conventional label, which is why the
codebook-level analysis probes each stream individually.

**The transcript baseline.** The text embedding is two objects with two roles [3.5]. Because the
study holds the target word constant, an embedding of the word alone is identical across clips
and at chance by construction, so it is a manipulation check rather than a competitor. An embedding of the
surrounding discourse context is the substantive text baseline, because pragmatic cues leak into
neighbouring words. Distinguishing the two is essential to interpreting the results.

## 2.3 What tokenisation loses, and why the standard comparisons overstate it

**Why the standard comparisons overstate.** Both designs criticised in [1.2] fail in the same way,
and the failure is worth naming precisely because the remedy follows from it. A probe on utterances
whose words differ measures a mixture of delivery and vocabulary in unknown proportion, and more data
does not separate them, because the confound is in the comparison rather than in the representation.
Placing a continuous encoder against a token stream and assigning the difference to quantisation
compares conditions differing simultaneously in architecture, objective, frame rate and feature
construction, so the figure is real but is not a measurement of discretisation. The parallel is
reconstruction-based codec evaluation, where a strong decoder masks deficiencies in the tokens and
inflates apparent token quality (Mousavi et al., 2026). In each case the fix is to remove the
intermediary and measure the step in isolation. None of this is a criticism of the findings below,
which this study largely reproduces. It constrains what they can be used to conclude.

A growing body of work supports the concern that discretisation specifically damages prosodic
and paralinguistic information, and it is this work that both motivates the central hypothesis
and constrains how strongly it can be stated. On prosody, ProsodyLM (Qian et al., 2025) argues
that mainstream token-then-model training is suboptimal for prosody and proposes explicit word-
level prosody tokens. Segmentation-Variant Codebooks (Sanders et al., 2025) makes the
complementary argument that a single flat token rate fails to preserve prosodic and paralinguistic
information. Both imply that standard tokenisation is not built to retain what this study targets.

On affect the evidence is more direct. EMO-Codec (Ren et al., 2024) resynthesises speech through
legacy and neural codecs and finds emotion recognition degraded afterwards, with subjective
listening tests agreeing, and reports the loss as uneven across categories. Two codecs published in
2026 respond by making affect an explicit training target, one through emotion-guided modulation of
the latent before quantisation (Shi et al., 2026b) and one by imposing block-diagonal projections
that separate emotion and acoustic subspaces inside the quantiser (Meng et al., 2026). The
existence of that response matters for how the present contribution is framed. Emotion preservation
is an active design objective, so the open question is not whether affect can be built into a codec
but which affective quantity the objective is supervised on. This study separates stance from
arousal and measures them independently [3.3], and Chapter 5 returns to what that separation
implies for objectives supervised on categorical emotion labels.

The most precise recent evidence both supports and tempers the loss hypothesis. Sun et al. (2026)
discretise a fine-tuned WavLM and evaluate speech emotion recognition on MSP-Podcast, reporting
that discrete tokens reach macro-F1 between 0.3133 and 0.3479, a 6 to 14 per cent drop relative to
continuous features. Two details of that result matter here beyond the headline figure. The loss is
largely recoverable, through attention-based multi-layer fusion and the explicit reintroduction of
paralinguistic features, which is the constraint discussed below. And continuous features are
stable across layer configurations while discrete ones fluctuate, so instability across
configurations is itself a signature of information loss, a diagnostic this study returns to in
[Ch.4]. This recoverability is the single most important constraint on the
framing. The defensible claim is therefore not that tokenisation destroys paralinguistic content,
which that recovery falsifies, but that *default* tokenisation discards content that is
recoverable only with deliberate intervention, and that deployed systems consume the defaults off
the shelf. The dissertation tests the deployment-relevant condition and frames its claim
accordingly. A related line (Wang et al., 2026) identifies paralinguistic complexity as a
disruptive factor in speech-language modelling, reinforcing that this information is structurally
important rather than decorative. Poorly represented, it does not merely go missing, it can
destabilise modelling.

## 2.4 The linguistic construct

The preceding sections concern what representations retain. This section establishes that the thing
they might retain is a describable linguistic object rather than a label of convenience, since the
probing results are only interpretable if it is.

**Stance.** The analytic axis used here, affiliative against neutral against adversarial, is a
narrowing of a construct with an established literature. Du Bois (2007) formalises stancetaking as a
single act that simultaneously evaluates an object, positions the speaker, and calibrates alignment
with an interlocutor, and it is the third of those, alignment, that this study operationalises.
Biber and Finegan (1988) provide the complementary account of how stance is marked lexically and
grammatically, which matters here because the design deliberately removes those markers by holding
the word constant. What remains is the conversation-analytic notion of affiliation and
disaffiliation, the degree to which a response cooperates with the stance of the prior turn
(Stivers, 2008; Steensig, 2019). That distinction maps onto the three-way axis used here closely
enough that the annotation scheme is best understood as an operationalisation of it rather than as
an independent invention [3.3].

**Response tokens.** The eight target phrases are not arbitrary short words. *Yeah*, *okay*, *right*
and *sure* belong to a class variously called response tokens, continuers or affirmative cue words,
and their defining property is exactly the one this study exploits. Gravano, Hirschberg and Beňuš
(2012) show that such words are systematically ambiguous between agreeing with the interlocutor,
signalling continued attention, and marking the start of a new topic, and that these functions are
distinguished in spontaneous dialogue by acoustic and prosodic realisation rather than by wording.
They frame that ambiguity as a problem for spoken dialogue systems, which is the same problem this
dissertation measures one stage earlier. Their account also explains a property of the corpus that
would otherwise look like a sampling failure, namely that neutral stance concentrates almost
entirely in the agreement particles [B.5]. Backchannelling is a function of that class specifically,
so its distribution follows from what these words do.

**The acoustic signature, and why it is not uniform.** An experimental literature asks whether
ironic and sarcastic delivery has identifiable acoustic correlates and converges on a small set,
namely slower tempo, greater intensity, lowered pitch, reduced F0 range and altered voice quality
(Rockwell, 2000; Lan et al., 2019), while disputing whether these amount to a dedicated ironic tone
or a family of cues recognised in context (Bryant and Fox Tree, 2002, 2005). Two consequences
follow. That dispute bears on the premise check in [4.1], where context alone recovers much of the
contrast, which a family-of-cues account predicts rather than an anomaly. And the cues are not
uniform in how much a reconstruction objective needs them, which [Ch.5] takes up in interpreting why
the two annotated axes are retained so unevenly. Appendix [E] gives the inventory in full.

**Spontaneous against acted delivery.** Rockwell (2000) found listeners able to discriminate posed
sarcasm from non-sarcasm and unable to discriminate spontaneous sarcasm at all, so acted and
naturalistic renditions of the same category are not interchangeable stimuli. Scherer (2003) sets
that problem out for vocal emotion research generally, and it is why naturalistic podcast-derived
corpora were built (Lotfian and Busso, 2019; Busso et al., 2025). This is the strongest reason to
prefer spontaneous political-podcast audio over MUStARD, IEMOCAP or RAVDESS, and it calibrates
expectations for the premise check, since spontaneous delivery is the harder condition for human
listeners and not only for models.

**What the design does with all this.** It tests whether a representation collapses distinct
interpersonal meanings when the transcript is held constant, which is the strong form of a claim
whose weak form, that prosody matters, is uncontroversial. It measures whether the category is
recoverable, not which acoustic cue carries it, and cue-level attribution is named as future work in
[Ch.6] rather than attempted here.

## 2.5 The closest precedent and the gap

The work most directly adjacent to this dissertation is Lin et al. (2022), who probed self-
supervised models on prosody-related tasks including sarcasm. Their framing matches this study's, in that
sarcasm is prosody-intensive precisely because its marker is a mismatch between lexical content
and prosodic delivery. Probing on the MUStARD corpus (Castro et al., 2019), they found that
HuBERT and WavLM improved on the prior audio-only state of the art and that acoustic models
outperformed the text-only baseline, and further that integrating low-level layers helped sarcasm
specifically while it did not help sentiment, indicating that pragmatic-prosodic tasks draw on
different representational depths than content-driven ones. This precedent does most of the work
of establishing that speech representations carry pragmatic-prosodic signal that text loses, and
must be credited as such. The generic claim that speech beats text is therefore not available as
a novel finding here.

Their design, however, lets lexical content vary. MUStARD utterances differ in their words, so the
result is confounded with lexical content, since the model may be exploiting word choice rather
than delivery. The corpus is also acted television speech, it carries a single binary sarcasm
label, and the comparison is between continuous representations only. The space this dissertation
occupies is therefore narrow and precise. It removes the lexical confound by probing the same lexical item under divergent
pragmatic force, uses naturalistic speech rather than acted corpora, and adds a comparison between
continuous representations and the discrete tokens deployed systems consume. The contribution is
not that speech beats text. It is that speech beats text *when the word is held constant*, which
isolates delivery from lexical choice, and it is this isolation that licenses the inadequacy
claim about deployed tokenisation.

A note on convergent design. Yang et al. (2026) independently adopt the same control at the level of
whole systems, requiring benchmark queries to carry neutral textual content so that a model "cannot
infer the speaker's state from words alone and must attend to vocal cues". That the two construction
rules were arrived at separately is evidence the move is right rather than idiosyncratic. The two
studies are complementary. Theirs is behavioural and asks whether a system responds appropriately,
using mostly synthesised queries at the level of a dialogue turn. This one is representational and
asks whether the contrast is present to be responded to, using spontaneous speech within a single
held-constant word.
