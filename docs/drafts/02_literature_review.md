# Chapter 2: Literature Review

## 2.1 Discrete speech tokens

Discrete audio tokens have become a general-purpose interface for speech modelling,
underpinning codecs built for compression (Zeghidour et al., 2021; Défossez et al., 2022;
Kumar et al., 2023), tokenisers built to feed language models, and full-duplex
speech-to-speech dialogue (Défossez et al., 2024). What unites them is that the tokens,
not the audio, are what the downstream model receives, which makes the informational
content of the tokenisation step a first-order design question.

**Two token families.** *Acoustic* tokens derive from codecs optimised for reconstruction
and preserve signal-level detail. *Semantic* tokens derive from self-supervised or
supervised models and encode phonetic or linguistic content.[^sem] Pragmatic meaning sits
in neither cleanly. Sarcasm, reluctance and ironic agreement are not lexical content, but
neither are they the arbitrary signal detail a codec preserves for reconstruction. They
occupy a middle band of prosody, timing and emphasis that tokenisation was not designed
to retain.

[^sem]: The term is a misnomer. So-called semantic tokens are better described as phonetic
units (Sicherman and Adi, 2023) and generally lack semantic content in the linguistic
sense (Arora et al., 2025). This dissertation retains the conventional term for
consistency with the systems it describes.

**A design lineage of added supervision.** Residual quantisation was established in
service of reconstruction alone, in SoundStream (Zeghidour et al., 2021), EnCodec
(Défossez et al., 2022) and DAC (Kumar et al., 2023). SpeechTokenizer (Zhang et al.,
2024a) introduced the modification that concerns this study, guiding the first quantiser
with a self-supervised teacher so that the leading stream carries content and later
streams carry refinement. Mimi (Défossez et al., 2024) inherits that arrangement with
WavLM as teacher, and X-Codec (Ye et al., 2024) generalises it by injecting teacher
features before quantisation. Which supervision is added determines what the tokens
retain, which is why the undistilled codecs serve as the comparison here.

**A second axis, less often discussed.** These systems also differ in how their encoders
treat time, and not only in how often they sample it. DAC is purely convolutional,
EnCodec adds recurrence, and Mimi adds a transformer bottleneck over the convolutional
stack. That difference is orthogonal to the distillation lineage and turns out to predict
what this study measures [4.5].

## 2.2 The representations under test

Eight representations are compared on a single task, recovering the pragmatic force of a
phrase whose lexical content is held constant.

**Table 2.1.** Representations under test. Frame rate in Hz. Specifications read from the
checkpoints and the primary papers.

| Representation | SR | FR | Layers × hidden | Vocab | Type | Encoder time handling |
|---|---|---:|---|---:|---|---|
| WavLM-large (Chen et al., 2022) | 16 kHz | 50 | 25 × 1024 | | continuous, self-supervised | transformer |
| Whisper-small enc. (Radford et al., 2023) | 16 kHz | 50 | 13 × 768 | | continuous, supervised | transformer |
| Mimi (Défossez et al., 2024) | 24 kHz | 12.5 | | 2048 | hybrid, 8 codebooks, WavLM-distilled | conv + 8 attention layers |
| DAC (Kumar et al., 2023) | 24 kHz | 75 | | 1024 | acoustic, first 8 of 32 codebooks | convolution only |
| EnCodec (Défossez et al., 2022) | 24 kHz | 75 | | 1024 | acoustic, 8 codebooks | convolution + LSTM |
| MPNet text embedding | | | 768 | | continuous, text | none |
| eGeMAPSv02 functionals | | | 88 | | hand-crafted acoustic | none |

HuBERT-large (Hsu et al., 2021) was probed throughout as a matched self-supervised control
for WavLM and is reported in Appendix [H].

**Continuous encoders.** WavLM and HuBERT share a masked-prediction architecture and a
documented layer-wise division of labour, with lower layers encoding local acoustic
detail, middle layers integrating prosodic and contextual information, and upper layers
abstracting toward linguistic content (Pasad et al., 2021). Qian, Figueroa and Skantze
(2025) locate prosodic information primarily in middle layers across four foundation
models. That the optimum is not absolute is why the full stack is probed here rather than
a layer assumed. The Whisper encoder is the theoretically interesting case, since a
transcription objective predicts a lexical bias the self-supervised encoders do not
share.

**Codecs.** Mimi is used rather than a pure acoustic codec because it is the input
tokeniser for deployed speech-to-speech systems. DAC and EnCodec are matched to it at
eight codebooks rather than at equal bitrate, so quantiser count is held constant while
frame rate and codebook geometry vary. DAC and EnCodec are additionally matched to each
other at 75 Hz, which is what permits frame rate to be separated from encoder
architecture [4.5].

**Naming the first codebook.** Codec probing (Shi et al., 2026) shows that distillation
from WavLM injects phonetic rather than semantic knowledge, from which an earlier version
of this chapter predicted that pragmatic force would sit in the acoustic codebooks rather
than in codebook 0. Chapter 4 shows the reverse [4.6]. The inference was a category
error, since the semantic-versus-phonetic axis concerns what a stream encodes about which
words were said, and pragmatic force is orthogonal to it.

## 2.3 What tokenisation loses, and what is proposed about it

**On affect and prosody.** DASB (Mousavi et al., 2026) finds discrete representations
systematically less robust than continuous ones. EMO-Codec (Ren et al., 2024) finds
emotion recognition degraded after codec resynthesis. Sun et al. (2026) report a 6 to 14
per cent drop on emotion recognition from discretised features, and two details matter
beyond the figure. The loss is largely recoverable through multi-layer fusion and
explicit reintroduction of paralinguistic features, which constrains how strongly any
claim here can be stated. And continuous features are stable across configurations while
discrete ones fluctuate, so instability is itself a signature of information loss. The
defensible claim is therefore not that tokenisation destroys paralinguistic content,
which that recovery falsifies, but that *default* tokenisation discards content
recoverable only with deliberate intervention, and that deployed systems consume the
defaults.

**The remedies currently proposed, and where they intervene.** One family intervenes at
the codebook, through explicit word-level prosody tokens (Qian, Y. et al., 2025a) or
quantisation at multiple segmental units (Sanders et al., 2025). A second and larger
family intervenes on the frame rate. FlexiCodec (Li et al., 2026) and CodecSlime allocate
frames dynamically on the grounds that natural speech units are inherently dynamic in
their rate of occurrence, so a fixed rate wastes capacity on silence and sustained vowels
while under-resolving transients. Sylber (Cho et al., 2025) and DyCAST (Della Libera et
al., 2026) go further, deriving the units from the signal or from character alignment
rather than from a clock.

Two things about this family bear on the present study. Its stated motivation is
predominantly semantic and phonetic rather than prosodic. FlexiCodec's own account of the
syllabic line is that it "successfully extracts semantic units at 5-8Hz but largely
discards the fine-grained acoustic details, prosody, and timing required for high-fidelity
reconstruction", and SyllableLM describes its objective as coarse semantic units at low
bitrate (Baade et al., 2025). So the literature that proposes variable rates as a fix for
timing also records, of the systems that go furthest, that prosody is what they shed. And
Gichamba and Busogi (2026), ablating frame rate on DAC from 1.6 to 100 Hz, find no
evidence that frame rate imposes a fundamental barrier at all, tracing an apparent quality
cliff to a training misconfiguration.

**A mechanism for discrete instability.** Liu et al. (2024) show that codec encoders
integrate context, so acoustically identical segments receive different token sequences
depending on their surroundings, with consistency falling as codebook depth increases.
Code identity is therefore less stable than the vector it decodes to, which bears directly
on any summary computed over indices [4.3].

**Why the standard comparisons overstate.** Both designs criticised in [1.2] fail in the
same way. A probe on utterances whose words differ measures a mixture of delivery and
vocabulary in unknown proportion. Placing a continuous encoder against a token stream and
assigning the difference to quantisation compares conditions differing simultaneously in
architecture, objective, frame rate and feature construction. In each case the fix is to
remove the intermediary and measure the step in isolation. This is not a criticism of the
findings above, which this study largely reproduces. It constrains what they can be used
to conclude.

## 2.4 The linguistic construct

**Stance.** Du Bois (2007) formalises stancetaking as a single act that evaluates an
object, positions the speaker and calibrates alignment with an interlocutor, and it is
alignment that this study operationalises. Biber and Finegan (1988) give the complementary
account of lexical and grammatical stance marking, which matters because the design
removes those markers by holding the word constant. What remains is the
conversation-analytic notion of affiliation and disaffiliation (Stivers, 2008; Steensig,
2019).

**Response tokens.** *Yeah*, *okay*, *right* and *sure* are response tokens. Schegloff
(1982) establishes their function as continuers, signalling that a turn is passing rather
than being taken, and that function is carried by delivery because the words themselves
carry no propositional content. Gravano et al. (2012) show them to be
systematically ambiguous between agreeing, signalling continued attention and marking a
topic shift, with those functions distinguished in spontaneous dialogue by prosodic
realisation rather than by wording, and they frame that ambiguity as a problem for spoken
dialogue systems, which is what this dissertation measures one stage earlier.

**That delivery is separable from wording** is not assumed here. O'Connor Russell et al.
(2026) vocoder speech to remove lexical content while preserving prosody and find
turn-taking prediction retaining 87 to 91 per cent of clean-speech accuracy, concluding
that prosodic and lexical cues are encoded in self-supervised representations with limited
interdependence. Qian, Figueroa and Skantze (2025b) reach the same design decision
independently, grouping stimuli by lexical form to eliminate the effects of lexical
semantics.

**The acoustic signature.** An experimental literature converges on a small set of
correlates for ironic delivery, namely slower tempo, greater intensity, lowered pitch,
reduced F0 range and altered voice quality (Rockwell, 2000; Lan et al., 2019), while
disputing whether these amount to a dedicated ironic tone or a family of cues recognised
in context (Bryant and Fox Tree, 2005). That dispute bears on the premise check in [4.1],
where context alone recovers much of the contrast. Appendix [E] gives the inventory.

**Spontaneous against acted delivery.** Rockwell (2000) found listeners able to
discriminate posed sarcasm and unable to discriminate spontaneous sarcasm, so the two are
not interchangeable stimuli. Scherer (2003) sets that problem out for vocal emotion
research generally, and it is why naturalistic podcast-derived corpora were built (Lotfian
and Busso, 2019).

## 2.5 Position of this study

**Table 2.2.** Prior work on paralinguistic content in speech representations. *Lexical
control* means wording is held constant so delivery is the only variable. *Stage-resolved*
means the pipeline is decomposed rather than compared end to end.

| Study | Corpus | Lexical control | Discrete | Stage-resolved | Axis measured |
|---|---|---|---|---|---|
| Lin et al. (2022) | acted television | no | no | no | sarcasm, binary |
| Mousavi et al. (2026) | mixed | no | yes | no | multi-task |
| Ren et al. (2024) | acted | no | yes | no | emotion, categorical |
| Sun et al. (2026) | spontaneous podcast | no | yes | no | emotion, categorical |
| Qian, Figueroa and Skantze (2025b) | spontaneous feedback | **yes, lexical form** | no | no | perceived similarity |
| O'Connor Russell et al. (2026) | spontaneous dyads | by vocoding | no | no | turn-taking |
| Gichamba and Busogi (2026) | read speech | n/a | yes | by frame rate | reconstruction |
| Yang et al. (2026) | synthesised and acted | yes, system level | n/a | no | behavioural |
| **This study** | **spontaneous podcast** | **yes, phrase level** | **yes** | **yes, and by architecture** | **stance and arousal** |

Two entries are close siblings and neither closes the question. Qian, Figueroa and Skantze
(2025) adopt the same lexical control on the same class of words, but compare continuous
representations only and measure perceived similarity rather than a decomposed pipeline.
Gichamba and Busogi (2026) run a controlled single-variable ablation on a codec, but the
variable is frame rate and the outcome is reconstruction quality.

Yang et al. (2026) independently adopt the same control at the level of whole systems,
requiring benchmark queries to carry neutral textual content so that a model "cannot infer
the speaker's state from words alone and must attend to vocal cues". That the construction
rule was arrived at separately is evidence the move is right rather than idiosyncratic.
The two studies are complementary, theirs behavioural and asking whether a system responds
appropriately, this one representational and asking whether the contrast is present to be
responded to.
