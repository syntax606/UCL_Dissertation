# Chapter 2: Literature Review

*(Draft, restructured on the S2S-Arena related-work pattern. Two tables carry the per-item detail so
the prose characterises families rather than individual papers. Citations are the verified set in
docs/literature_references_verified.md, and all quoted material and all figures attributed to other
papers have been checked against those papers.)*

## 2.1 Discrete speech tokens

Discrete audio tokens have become a general-purpose interface for speech modelling. They underpin
codecs built for compression (Zeghidour et al., 2021; Défossez et al., 2022; Kumar et al., 2023),
tokenisers built to feed language models (Zhang et al., 2024a; Ye et al., 2024; Défossez et al.,
2024), full-duplex speech-to-speech dialogue systems (Défossez et al., 2024), and paralinguistic
modelling from codes rather than waveforms (Sun et al., 2026; Zhang et al., 2024b; Ren et al., 2024),
with an evaluation literature of its own (Mousavi et al., 2026; Deng et al., 2025; Wang et al.,
2025b; Guo et al., 2025; Arora et al., 2025). What unites them is that the tokens, not the audio, are
what the downstream model receives, which makes the informational content of the tokenisation step a
first-order design question.

**Two token families.** *Acoustic* tokens derive from codecs optimised for reconstruction and
preserve signal-level detail. *Semantic* tokens derive from self-supervised or supervised speech
models and encode phonetic or linguistic content.[^sem] Pragmatic meaning sits in neither cleanly.
Sarcasm, reluctance and ironic agreement are not lexical content, but neither are they the arbitrary
signal detail a codec preserves for reconstruction. They occupy a middle band of prosody, timing and
emphasis that current tokenisation was not designed to retain.

[^sem]: The term is a misnomer. So-called semantic tokens are better described as phonetic units
(Sicherman and Adi, 2023) and generally lack semantic content in the linguistic sense (Arora et al.,
2025), a point the review literature states explicitly (Guo et al., 2025) and codec probing confirms
(Shi et al., 2026). This dissertation retains the conventional term for consistency with the systems
it describes, and 2.2 sets out why the distinction settles nothing about pragmatic force.

**A design lineage of added supervision.** Residual quantisation was established in service of
reconstruction alone, in SoundStream (Zeghidour et al., 2021), EnCodec (Défossez et al., 2022) and
the Descript codec (Kumar et al., 2023). SpeechTokenizer (Zhang et al., 2024a) introduced the
modification that concerns this study, guiding the first quantiser with a self-supervised teacher so
that the leading stream carries content and later streams carry refinement. Mimi (Défossez et al.,
2024) inherits that arrangement with WavLM as teacher, and X-Codec (Ye et al., 2024) generalises it
by injecting teacher features before quantisation rather than only supervising after. Which
supervision is added determines what the tokens retain, which is why this study uses the Descript
codec as its undistilled comparison.

**Where the loss shows up.** DASB (Mousavi et al., 2026) finds discrete representations
systematically less robust than continuous ones, with preserving phonetic content, speaker identity
and paralinguistic cues simultaneously an open problem. Behavioural evaluations of deployed systems
report the same weakness downstream (Jiang et al., 2025; Yang et al., 2026).

## 2.2 The representations under test

Six representations are compared on a single task, recovering the pragmatic force of a phrase whose
lexical content is held constant. Table 2.1 gives their characteristics.

**Table 2.1.** Representations under test. Frame rate in Hz. Layers times hidden width for the
continuous encoders, codebook vocabulary for the codecs. Specifications read from the checkpoints and
the primary papers.

| Representation | SR | FR | Layers × hidden | Vocab | Type | Quantisation |
|---|---|---:|---|---:|---|---|
| WavLM-large (Chen et al., 2022) | 16 kHz | 50 | 25 × 1024 | | continuous, self-supervised | none |
| HuBERT-large (Hsu et al., 2021) | 16 kHz | 50 | 25 × 1024 | | continuous, self-supervised | none |
| Whisper-small encoder (Radford et al., 2023) | 16 kHz | 50 | 13 × 768 | | continuous, supervised | none |
| Mimi (Défossez et al., 2024) | 24 kHz | 12.5 | | 2048 | hybrid, 8 codebooks, WavLM-distilled | RVQ |
| DAC (Kumar et al., 2023) | 24 kHz | 75 | | 1024 | acoustic, 32 codebooks, first 8 used | RVQ |
| MPNet text embedding | | | 768 | | continuous, text | none |

**Continuous encoders.** HuBERT and WavLM share a masked-prediction architecture and a documented
layer-wise division of labour, with lower layers encoding local acoustic detail, middle layers
integrating prosodic and contextual information, and upper layers abstracting toward linguistic
content (Pasad et al., 2021; Chiu et al., 2025). The mid-layer optimum is not absolute (Zhang et al.,
2024b), which is why the full stack is probed. WavLM's noise and overlapped-speech augmentation makes
it strong on speaker identity, a nuisance for any distance-based measure [3.6]. The Whisper encoder
is the theoretically interesting case, since a transcription objective predicts a lexical bias the
self-supervised encoders do not share, and the context-window comparison [Ch.4] separates that route
from phrase-level delivery.

**Codecs.** Mimi is used rather than a pure acoustic codec because it is the input tokeniser for
deployed speech-to-speech systems, and a model built on it consumes the whole stack, which is why
the headline condition is all eight codebooks together. The two codecs are matched at eight codebooks
rather than at equal bitrate, so quantiser count is held constant while frame rate and codebook
geometry vary. That is a limitation of the cross-codec contrast [Ch.6] and the closest available
approximation to an ablation of the distillation objective without training a codec.

**Naming the first codebook.** Codec probing (Shi et al., 2026) shows that distillation from WavLM
injects phonetic rather than semantic knowledge, from which an earlier version of this chapter
predicted that pragmatic force would sit in the acoustic codebooks rather than in codebook 0. Chapter
4 shows the reverse [4.5]. The inference was a category error. The semantic-versus-phonetic axis
concerns what a stream encodes about which words were said, and pragmatic force is orthogonal to it,
so a finding either way licenses no inference about delivery. What predicts the outcome is the
distillation source rather than the stream's conventional label.

**The transcript baseline.** The text embedding is two objects with two roles [3.5]. Because the word
is held constant, an embedding of the word alone is at chance within a phrase by construction and is
a manipulation check rather than a competitor. An embedding of the surrounding discourse is the
substantive text baseline, since pragmatic cues leak into neighbouring words.

## 2.3 What tokenisation loses

**On prosody.** ProsodyLM (Qian et al., 2025) argues that token-then-model training is suboptimal for
prosody and proposes explicit word-level prosody tokens, while Segmentation-Variant Codebooks
(Sanders et al., 2025) argues that a single flat token rate cannot preserve prosodic and
paralinguistic information. Both imply that standard tokenisation is not built to retain what this
study targets.

**On affect.** EMO-Codec (Ren et al., 2024) resynthesises speech through legacy and neural codecs and
finds emotion recognition degraded afterwards, with listening tests agreeing and the loss uneven
across categories. Two codecs published in 2026 respond by making affect a training target, through
emotion-guided modulation of the latent before quantisation (Shi et al., 2026b) and through
block-diagonal projections separating emotion and acoustic subspaces inside the quantiser (Meng et
al., 2026). Emotion preservation is therefore an active design objective, and the open question is
not whether affect can be built into a codec but which affective quantity supervises it. This study
separates stance from arousal and measures them independently [3.3], and Chapter 5 returns to what
that separation implies.

**How much is lost, and how recoverable.** Sun et al. (2026) discretise a fine-tuned WavLM and
evaluate emotion recognition on MSP-Podcast, reporting macro-F1 between 0.3133 and 0.3479, a 6 to 14
per cent drop against continuous features. Two details matter beyond the figure. The loss is largely
recoverable through multi-layer fusion and explicit reintroduction of paralinguistic features, which
is the single most important constraint on how strongly the present claim can be stated. And
continuous features are stable across configurations while discrete ones fluctuate, so instability is
itself a signature of information loss, a diagnostic returned to in [Ch.4]. The defensible claim is
therefore not that tokenisation destroys paralinguistic content, which that recovery falsifies, but
that *default* tokenisation discards content recoverable only with deliberate intervention, and that
deployed systems consume the defaults. A related line (Wang et al., 2026) finds paralinguistic
complexity the most disruptive factor in speech-language modelling, so poorly represented, this
information does not merely go missing but can destabilise modelling.

**Why the standard comparisons overstate.** Both designs criticised in [1.2] fail in the same way. A
probe on utterances whose words differ measures a mixture of delivery and vocabulary in unknown
proportion, and more data does not separate them, because the confound is in the comparison rather
than in the representation. Placing a continuous encoder against a token stream and assigning the
difference to quantisation compares conditions differing simultaneously in architecture, objective,
frame rate and feature construction, so the figure is real but is not a measurement of
discretisation. The parallel is reconstruction-based codec evaluation, where a strong decoder masks
deficiencies in the tokens and inflates apparent token quality (Mousavi et al., 2026). In each case
the fix is to remove the intermediary and measure the step in isolation. None of this is a criticism
of the findings above, which this study largely reproduces. It constrains what they can be used to
conclude.

## 2.4 The linguistic construct

The preceding sections concern what representations retain. This section establishes that the thing
they might retain is a describable linguistic object rather than a label of convenience.

**Stance.** Du Bois (2007) formalises stancetaking as a single act that evaluates an object, positions
the speaker and calibrates alignment with an interlocutor, and it is alignment that this study
operationalises. Biber and Finegan (1988) give the complementary account of lexical and grammatical
stance marking, which matters because the design removes those markers by holding the word constant.
What remains is the conversation-analytic notion of affiliation and disaffiliation (Stivers, 2008;
Steensig, 2019), onto which the three-way axis maps closely enough that the annotation scheme is best
understood as an operationalisation of it [3.3].

**Response tokens.** The target phrases are not arbitrary short words. *Yeah*, *okay*, *right* and
*sure* are response tokens, and their defining property is the one this study exploits. Gravano,
Hirschberg and Beňuš (2012) show them to be systematically ambiguous between agreeing, signalling
continued attention and marking a topic shift, with those functions distinguished in spontaneous
dialogue by prosodic realisation rather than by wording, and they frame that ambiguity as a problem
for spoken dialogue systems, which is what this dissertation measures one stage earlier. Their
account also explains why neutral stance concentrates almost entirely in the agreement particles
[B.5], since backchannelling is a function of that class specifically.

**The acoustic signature.** An experimental literature converges on a small set of correlates for
ironic and sarcastic delivery, namely slower tempo, greater intensity, lowered pitch, reduced F0
range and altered voice quality (Rockwell, 2000; Lan et al., 2019), while disputing whether these
amount to a dedicated ironic tone or a family of cues recognised in context (Bryant and Fox Tree,
2002, 2005). That dispute bears on the premise check in [4.1], where context alone recovers much of
the contrast, which a family-of-cues account predicts. The cues are also not uniform in how much a
reconstruction objective needs them, which [Ch.5] takes up. Appendix [E] gives the inventory.

**Spontaneous against acted delivery.** Rockwell (2000) found listeners able to discriminate posed
sarcasm and unable to discriminate spontaneous sarcasm at all, so the two are not interchangeable
stimuli. Scherer (2003) sets that problem out for vocal emotion research generally, and it is why
naturalistic podcast-derived corpora were built (Lotfian and Busso, 2019; Busso et al., 2025). This
is the strongest reason to prefer spontaneous podcast audio over MUStARD, IEMOCAP or RAVDESS, and it
calibrates expectations for the premise check, since spontaneous delivery is harder for human
listeners and not only for models.

## 2.5 Position of this study

Table 2.2 places this study against the work closest to it on the dimensions that distinguish them.

**Table 2.2.** Prior work on paralinguistic content in speech representations. *Lexical control*
means the wording is held constant so delivery is the only variable. *Stage-resolved* means the
pipeline is decomposed rather than compared end to end.

| Study | Corpus | Lexical control | Continuous | Discrete | Stage-resolved | Axis measured |
|---|---|---|---|---|---|---|
| Lin et al. (2022) | acted television | no | yes | no | no | sarcasm, binary |
| Zhang et al. (2024b) | acted and spontaneous | no | yes | no | no | paralinguistic, multi-task |
| Mousavi et al. (2026) | mixed | no | yes | yes | no | multi-task |
| Ren et al. (2024) | acted | no | no | yes | no | emotion, categorical |
| Sun et al. (2026) | spontaneous podcast | no | yes | yes | no | emotion, categorical |
| Shi et al. (2026) | read speech | no | no | yes | partial | semantic and phonetic |
| Yang et al. (2026) | synthesised and acted | yes, system level | n/a | n/a | no | behavioural |
| **This study** | **spontaneous podcast** | **yes, phrase level** | **yes** | **yes** | **yes** | **stance and arousal** |

The closest precedent is Lin et al. (2022), who probed self-supervised models on prosody-related
tasks including sarcasm using MUStARD (Castro et al., 2019), and found acoustic models beating a
text-only baseline and low-level layers helping sarcasm specifically. That work establishes that
speech representations carry pragmatic-prosodic signal text loses, so the generic claim that speech
beats text is not available here as a finding. What its design leaves open is the lexical route,
since MUStARD utterances differ in their words.

Yang et al. (2026) independently adopt the same control at the level of whole systems, requiring
benchmark queries to carry neutral textual content so that a model "cannot infer the speaker's state
from words alone and must attend to vocal cues". That the two construction rules were arrived at
separately is evidence the move is right rather than idiosyncratic. The two studies are
complementary, theirs behavioural and asking whether a system responds appropriately, this one
representational and asking whether the contrast is present to be responded to.

Overall, existing work establishes that discretisation is lossy and weakest in the
prosodic-paralinguistic band, but measures it either without holding wording constant, so delivery
and vocabulary are confounded, or without decomposing the pipeline, so the loss cannot be localised.
This study does both.
