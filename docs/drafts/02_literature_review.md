<!-- GENERATED from the Word draft by src/45_export_draft.py.
     The .docx is authoritative. Edits made here will be overwritten. -->

# Chapter 2: Literature Review

## 2.1 Discrete speech tokens

Discrete audio tokens have become a general-purpose interface for speech modelling (for a review, see Guo et al., 2025), underpinning codecs built for compression (Zeghidour et al., 2021; Défossez et al., 2022; Kumar et al., 2023), tokenisers built to feed language models, and full-duplex speech-to-speech dialogue (Défossez et al., 2024). What unites them is that the tokens, not the audio, are what the downstream model receives, which makes the informational content of the tokenisation step a first-order design question.

Two token families. The division follows AudioLM (Borsos et al., 2023), which generated coarse tokens before fine ones and named the two levels accordingly. Acoustic tokens derive from codecs optimised for reconstruction and preserve signal-level detail. Semantic tokens derive from self-supervised or supervised models and encode phonetic or linguistic content. The name is a misnomer, since such tokens are better described as phonetic units (Sicherman and Adi, 2023) and generally lack semantic content in the linguistic sense (Arora et al., 2025), though the conventional term is retained here for consistency with the systems it describes.

A design lineage of added supervision. Residual quantisation was established in service of reconstruction alone, in SoundStream (Zeghidour et al., 2021), EnCodec (Défossez et al., 2022) and DAC (Kumar et al., 2023). SpeechTokenizer (Zhang et al., 2024a) introduced the modification that concerns this study, guiding the first quantiser with a self-supervised teacher so that the leading stream carries content and later streams carry refinement. Mimi (Défossez et al., 2024) inherits that arrangement with WavLM as teacher, and X-Codec (Ye et al., 2024) generalises it by injecting teacher features before quantisation. Which supervision is added determines what the tokens retain, which is why the undistilled codecs serve as the comparison here.

A second axis, less often discussed. These systems also differ in how their encoders treat time, and not only in how often they sample it. DAC is purely convolutional, EnCodec adds recurrence, and Mimi adds a transformer bottleneck over the convolutional stack. That difference is orthogonal to the distillation lineage and turns out to predict what this study measures [4.5].

## 2.2 The representations under test

Ten conditions are compared on a single task, recovering the pragmatic force of a phrase whose lexical content is held constant. Eight carry the main analyses, with the text baseline supplying two of them, and the two variable-frame-rate tokenisers at the foot of the table are added for the comparison in [4.4, 4.6].

Table 2.1. Representations under test. Frame rate in Hz. Specifications read from the checkpoints and the primary papers.

| Representation | SR | FR | Layers × hidden | Vocab | Type | Encoder time handling |
|---|---|---|---|---|---|---|
| WavLM-large (Chen et al., 2022) | 16 kHz | 50 | 25 × 1024 |  | continuous, self-supervised | transformer |
| Whisper-small enc. (Radford et al., 2023) | 16 kHz | 50 | 13 × 768 |  | continuous, supervised | transformer |
| Mimi (Défossez et al., 2024) | 24 kHz | 12.5 |  | 2048 | hybrid, 8 codebooks, WavLM-distilled | conv + 8 attention layers |
| DAC (Kumar et al., 2023) | 24 kHz | 75 |  | 1024 | acoustic, first 8 of 32 codebooks | convolution only |
| EnCodec (Défossez et al., 2022) | 24 kHz | 75 |  | 1024 | acoustic, 8 codebooks | convolution + LSTM |
| MPNet text embedding |  |  | 768 |  | continuous, text | none |
| eGeMAPSv02 functionals |  |  | 88 |  | hand-crafted acoustic | none |
| Sylber (Cho et al., 2025) | 16 kHz | ~4, variable |  |  | syllabic, signal-derived units | conv + transformer, HuBERT-based |
| DyCAST (Della Libera et al., 2026) | 16 kHz | 6–24, variable |  | 4^32 | character-aligned, variable rate | conv + transformer, WavLM-based |

HuBERT-large (Hsu et al., 2021) was probed throughout as a matched self-supervised control for WavLM and is reported in Appendix [F].

Continuous encoders. WavLM (Chen et al., 2022) and HuBERT share a masked-prediction architecture and a documented layer-wise division of labour, with lower layers encoding local acoustic detail, middle layers integrating prosodic and contextual information, and upper layers abstracting toward linguistic content (Pasad et al., 2021). Qian, Figueroa and Skantze (2025) locate prosodic information primarily in middle layers across four foundation models. That the optimum is not absolute is why the full stack is probed here rather than a layer assumed. The Whisper encoder is the theoretically interesting case, since a transcription objective predicts a lexical bias the self-supervised encoders do not share.

Codecs. Mimi is used rather than a pure acoustic codec because it is the input tokeniser for deployed speech-to-speech systems. DAC and EnCodec are matched to it at eight codebooks rather than at equal bitrate, so quantiser count is held constant while frame rate and codebook geometry vary. DAC and EnCodec are additionally matched to each other at 75 Hz, which is what permits frame rate to be separated from encoder architecture [4.5].

Naming the first codebook. Codec probing (Shi et al., 2026) shows that distillation from WavLM injects phonetic rather than semantic knowledge. The natural inference is that pragmatic force would sit in the acoustic codebooks rather than in the distilled one, and [4.6] shows the reverse. The inference is a category error, since the semantic-versus-phonetic axis concerns what a stream encodes about which words were said, and pragmatic force is orthogonal to it.

## 2.3 What tokenisation loses, and what is proposed about it

On affect and prosody. DASB (Mousavi et al., 2026) finds discrete representations systematically less robust than continuous ones. EMO-Codec (Ren et al., 2024) finds emotion recognition degraded after codec resynthesis. Sun et al. (2026) report a 6 to 14 per cent drop on emotion recognition from discretised features, and two details matter beyond the figure. The loss is largely recoverable through multi-layer fusion and explicit reintroduction of paralinguistic features, which constrains how strongly any claim here can be stated. And continuous features are stable across configurations while discrete ones fluctuate, so instability is itself a signature of information loss. The defensible claim is therefore not that tokenisation destroys paralinguistic content, which that recovery falsifies, but that default tokenisation discards content recoverable only with deliberate intervention, and that deployed systems consume the defaults.

The remedies currently proposed, and where they intervene. One family intervenes at the codebook, through explicit word-level prosody tokens (Qian, K. et al., 2025) or quantisation at multiple segmental units (Sanders et al., 2025). A second and larger family intervenes on the frame rate. FlexiCodec (Li et al., 2026) allocates frames dynamically on the grounds that natural speech units are inherently dynamic in their rate of occurrence, so a fixed rate wastes capacity on silence and sustained vowels while under-resolving transients. Sylber (Cho et al., 2025) and DyCAST (Della Libera et al., 2026) go further, deriving the units from the signal or from character alignment rather than from a clock.

That family's stated motivation is predominantly semantic and phonetic rather than prosodic. FlexiCodec's own account of the syllabic line is that it "successfully extracts semantic units at 5-8Hz but largely discards the fine-grained acoustic details, prosody, and timing required for high-fidelity reconstruction", and SyllableLM describes its objective as coarse semantic units at low bitrate (Baade et al., 2025). So the literature that proposes variable rates as a fix for timing also records, of the systems that go furthest, that prosody is what they shed. And Gichamba and Busogi (2026), ablating frame rate on DAC from 1.6 to 100 Hz, find no evidence that frame rate imposes a fundamental barrier at all, tracing an apparent quality cliff to a training misconfiguration.

A mechanism for discrete instability. Liu et al. (2024) show that codec encoders integrate context, so acoustically identical segments receive different token sequences depending on their surroundings, with consistency falling as codebook depth increases. Code identity is therefore less stable than the vector it decodes to, which bears directly on any summary computed over indices [4.3].

Why the standard comparisons overstate. Both designs criticised in [1.2] fail in the same way. A probe on utterances whose words differ measures a mixture of delivery and vocabulary in unknown proportion. Placing a continuous encoder against a token stream and assigning the difference to quantisation compares conditions differing simultaneously in architecture, objective, frame rate and feature construction. In each case the fix is to remove the intermediary and measure the step in isolation. This is not a criticism of the findings above, which this study largely reproduces. It constrains what they can be used to conclude.

## 2.4 The linguistic construct

Stance. Du Bois (2007) formalises stancetaking as a single act with three faces, evaluating an object, positioning the speaker and calibrating alignment with an interlocutor, and it is the third that a response token performs almost to the exclusion of the other two. Biber and Finegan (1988) give the complementary account of stance marking as lexical and grammatical, which is precisely what this design removes by holding the word constant, so what remains once those markers are gone is the interactional layer that conversation analysis describes as affiliation and disaffiliation. Stivers (2008) shows that layer being negotiated turn by turn during storytelling, where a nod can affiliate or withhold affiliation without any lexical content at all, and Steensig (2026) separates alignment, which concerns the structural progress of the activity, from affiliation, which concerns endorsement of the stance being displayed. The axis annotated here maps onto affiliation rather than alignment, which is why a structurally cooperative backchannel can still be adversarial, and why the neutral category is not an absence of stance but a distinct interactional move.

Response tokens. Yeah, okay, right and sure are response tokens. Schegloff (1982) establishes their function as continuers, signalling that a turn is passing rather than being taken, and that function is carried by delivery because the words themselves carry no propositional content. Gravano et al. (2012) show them to be systematically ambiguous between agreeing, signalling continued attention and marking a topic shift, with those functions distinguished in spontaneous dialogue by prosodic realisation rather than by wording, and they frame that ambiguity as a problem for spoken dialogue systems, which is what this dissertation measures one stage earlier.

That delivery is separable from wording is not assumed here. O'Connor Russell et al. (2026) vocoder speech to remove lexical content while preserving prosody and find turn-taking prediction retaining 87 to 91 per cent of clean-speech accuracy, concluding that prosodic and lexical cues are encoded in self-supervised representations with limited interdependence. Qian, Figueroa and Skantze (2025) reach the same design decision independently, grouping stimuli by lexical form to eliminate the effects of lexical semantics.

The acoustic signature. An experimental literature converges on a small set of correlates for ironic delivery, namely slower tempo, greater intensity, lowered pitch, reduced F0 range and altered voice quality (Rockwell, 2000; Lan et al., 2019), while disputing whether these amount to a dedicated ironic tone or a family of cues recognised in context (Bryant and Fox Tree, 2005). The convergence is partial even within that list, since Rockwell reports greater intensity where Lan et al. find lower mean amplitude. That dispute bears on the premise check in [4.1], where context alone recovers much of the contrast. Two of those five describe movement rather than position, since tempo is a rate and a reduced range is a narrowed excursion, which is the distinction [4.2] measures on this corpus. One tension follows. Rockwell leads with tempo where coarse rate carries the least stance here, at +0.024 against contour's +0.083, and the two are not the same quantity since hers is a perceptual coding of filtered speech, but the emphasis differs. Appendix [C] gives the inventory.

Spontaneous against acted delivery. Rockwell (2000) found listeners able to discriminate posed sarcasm and unable to discriminate spontaneous sarcasm, so the two are not interchangeable stimuli. Scherer (2003) sets that problem out for vocal emotion research generally, and it is why naturalistic podcast-derived corpora were built (Busso et al., 2025).

## 2.5 Position of this study

Table 2.2. Prior work on paralinguistic content in speech representations. Lexical control means wording is held constant so delivery is the only variable. Stage-resolved means the pipeline is decomposed rather than compared end to end.

| Study | Corpus | Lexical control | Discrete | Stage-resolved | Axis measured |
|---|---|---|---|---|---|
| Lin et al. (2022) | acted television | no | no | no | sarcasm, binary |
| de Seyssel et al. (2023) | read speech | by construction | no | no | prosodic boundary and pause |
| Mousavi et al. (2026) | mixed | no | yes | no | multi-task |
| Ren et al. (2024) | acted | no | yes | no | emotion, categorical |
| Sun et al. (2026) | spontaneous podcast | no | yes | no | emotion, categorical |
| Qian, Figueroa and Skantze (2025b) | spontaneous feedback | yes, lexical form | no | no | perceived similarity |
| O'Connor Russell et al. (2026) | spontaneous dyads | by vocoding | no | no | turn-taking |
| Gichamba and Busogi (2026) | read speech | n/a | yes | by frame rate | reconstruction |
| Yang et al. (2026) | synthesised and acted | yes, system level | n/a | no | behavioural |
| Pasad et al. (2021) | read speech | no | no | no | layer-wise, phonetic and word |
| Shi et al. (2026) | read speech | no | yes | partial, by codebook | semantic and phonetic |
| Sanders et al. (2025) | acted and read | no | yes | no | paralinguistic and prosodic |
| Pang et al. (2026) | synthesised | yes, system level | n/a | no | behavioural |
| This study | spontaneous podcast | yes, phrase level | yes | yes, and by architecture | stance and arousal |

Two entries are close siblings and neither closes the question. Qian, Figueroa and Skantze (2025) adopt the same lexical control on the same class of words, but compare continuous representations only and measure perceived similarity rather than a decomposed pipeline. Gichamba and Busogi (2026) run a controlled single-variable ablation on a codec, but the variable is frame rate and the outcome is reconstruction quality.

Pang et al. (2026) describe their benchmark as an adversarial stress test that does not substitute for naturalistic paralinguistic evaluation, and recommend reporting both. The present corpus is naturalistic by construction, and the lexical control is a property of the speech rather than of a synthesis procedure, which supplies the counterpart their design calls for while sacrificing the guarantee of a clean conflict that synthesis provides.

That the measurement has not been made is not an oversight. The pre-quantisation latent is not an output of a codec, which exposes a waveform and a token stream by design, so obtaining it requires reaching into the forward pass and establishing which intermediate representation is comparable to which, and the naive pairing is not comparable at all [3.5]. The number is also of no use to the literature that would most easily obtain it, since codec development is evaluated at the waveform and the latent has no role in reconstruction, while the probing literature that would want it treats codecs as black boxes emitting tokens. The two moves are informative jointly and weak separately, which is why neither has previously been made in the presence of the other.

Yang et al. (2026) independently adopt the same control at the level of whole systems, requiring benchmark queries to carry neutral textual content so that a model "cannot infer the speaker's state from words alone and must attend to vocal cues". That the construction rule was arrived at separately is evidence the move is right rather than idiosyncratic. The two studies are complementary, theirs behavioural and asking whether a system responds appropriately, this one representational and asking whether the contrast is present to be responded to.
