# Chapter 2: Literature Review

*(Draft. Target budget ~2,300 words. Compressed from the long-form draft, and citations are the
verified set in docs/literature_references_verified.md. One claim flagged [verify] remains to be
checked against the paper body before submission.)*

## 2.1 Introduction

This chapter situates the dissertation within three converging literatures, namely the move to
discrete speech tokens in speech-language modelling, the body of probing work on what speech
representations encode about prosody and paralinguistics, and the linguistic study of how
identical words perform different speech acts. The argument the chapter builds toward is
specific. Prior work has established that speech representations carry pragmatic and affective
information that text discards, and that discretising speech into tokens loses paralinguistic
content. The question this dissertation takes up is whether that loss is a loss of *meaning*
rather than merely of *sound*, which can only be settled by holding lexical content constant
while pragmatic force varies. That is the space this dissertation occupies, and isolating it is what
turns the uncontroversial observation that tokenisation is lossy into the substantive claim
that tokenisation, as deployed, drops the meaning-bearing part of speech.

## 2.2 The speech-language-model turn and discrete speech tokens

Speech-language modelling increasingly converts continuous waveforms into sequences of discrete
tokens before passing them to language-model architectures (Guo et al., 2025). This makes
speech tractable for autoregressive models trained on text and underpins deployed
speech-to-speech systems, but it raises the question this dissertation pursues, which is whether the
tokens preserve the parts of speech that are invisible in the transcript.

The literature divides speech tokens into two families. *Acoustic* tokens derive from neural
codecs optimised for reconstruction and preserve signal-level detail. *Semantic* tokens derive
from self-supervised or supervised speech models and encode phonetic or linguistic content. The
distinction is real but imperfect, and the review literature is explicit that "semantic" tokens
often behave phonetically, capturing the sounds that distinguish words rather than the meanings
those words carry (Guo et al., 2025). This matters directly here, because pragmatic meaning sits
in neither category cleanly, since sarcasm, reluctance, and ironic agreement are not lexical content,
but they are also not the arbitrary acoustic detail a codec preserves for reconstruction. They
live in a middle band of prosody, timing, and emphasis that current tokenisation was not
designed to retain.

Benchmark evidence confirms that this middle band is where discretisation is weakest. The
Discrete Audio and Speech Benchmark (Mousavi et al., 2026) finds discrete representations
systematically less robust than continuous ones, with preserving phonetic content, speaker
identity, and paralinguistic cues simultaneously an open problem. The relevance for deployed
systems is sharpened by speech-to-speech behavioural evaluations, where S2S-Arena (Jiang et al., 2025)
and ParaS2S (Yang et al., 2026) both document that deployed systems underperform on
paralinguistic dimensions, which is the behavioural shadow of the representational loss this
study probes directly.

## 2.3 The representations under test

This dissertation compares five representations on a single task, recovering the pragmatic force
of a phrase whose lexical content is held constant. They fall into three types. Self-supervised
continuous encoders (WavLM, HuBERT) are trained by masked prediction without transcription
targets. A supervised continuous encoder (the Whisper encoder) is trained to transcribe. A
discrete neural codec (Mimi) quantises audio for speech-language models, and a transcript-only
text embedding serves as the control.

**Self-supervised encoders.** HuBERT (Hsu et al., 2021) and WavLM (Chen et al., 2022) share a
masked-prediction architecture and exhibit a well-documented layer-wise division of labour, in which
lower layers encode local acoustic detail, middle layers integrate prosodic and contextual
information, and upper layers abstract toward linguistic content while suppressing speaker-
specific cues (Pasad et al., 2021; Chiu et al., 2025). For affective and prosodic tasks this
places the useful signal in the middle band rather than the final layer. Two qualifications bear
on the design. First, the mid-layer optimum is not absolute, since ParaLBench (Zhang et al., 2024)
finds the strongest WavLM performance across paralinguistic tasks did not always come from the
final layers, which is why this study probes the full layer stack rather than assuming a fixed
optimum [Ch.4]. Second, WavLM augments the HuBERT objective with simulated noise and overlapped-
speech mixing, the documented reason it tends to outperform HuBERT on speaker and paralinguistic
tasks. This grounds the expectation that WavLM preserves pragmatic contrast at least as well as
HuBERT, but it also makes WavLM strong on speaker identity, a nuisance variable for any
distance-based contrast measure [3.6].

**Supervised encoder.** The Whisper encoder (Radford et al., 2023) is the theoretically
interesting case, because its transcription objective predicts a lexical bias the self-
supervised encoders do not share. Whisper features carry paralinguistic information, but the
supervised objective leaves a trace, in that acoustic information in the final encoder layers is reduced
in favour of transcription capability. The consequence is that if Whisper recovers a pragmatic
contrast, it may be leaning on surrounding lexical material rather than on phrase-level delivery,
since its representations are organised around what was said. The context-window comparison
[Ch.4] is the instrument that separates these routes.

**Discrete tokenisation and Mimi.** This study uses Mimi (Défossez et al., 2024) rather than a
pure acoustic codec, because Mimi is the input tokeniser for deployed speech-to-speech systems
and is therefore the deployment-relevant test case rather than a strawman. Mimi applies residual
quantisation at 12.5 Hz. Its first codebook is distilled from WavLM and the remaining seven carry
acoustic refinement. A model built on Mimi consumes the whole stack, which is why the headline
condition in this study is all eight codebooks together rather than any subset of them.

The naming of the first codebook requires care. Although it is conventionally called the semantic
stream, codec-probing work (Shi et al., 2026) shows that distillation from WavLM injects
*phonetic* rather than semantic knowledge, and that such tokenisers encode a higher proportion of
phonetic and acoustic than linguistic-semantic information. The Moshi report itself notes that
phonetic discriminability is poor without distillation and that distillation's contribution is
specifically phonetic.

An earlier version of this chapter drew a prediction from that finding. It reasoned that because
codebook 0 is phonetic rather than semantic, pragmatic force would not concentrate there, and
that if pragmatic prosody survived anywhere it would more plausibly sit in the acoustic-refinement
codebooks, which carry timbre and prosodic texture. Chapter 4 shows the reverse. Codebook 0 is
the only codebook carrying appreciable pragmatic signal, and five of the seven acoustic codebooks
are statistically indistinguishable from chance.

The prediction failed because it rested on a category error, and the correction is worth stating
explicitly. The semantic-versus-phonetic axis that Shi et al. characterise concerns what a token
stream encodes about linguistic content, which is to say which words were said. Pragmatic force
is orthogonal to that axis. It is neither semantic in their sense nor phonetic, so a finding that
codebook 0 is phonetically rather than semantically loaded licenses no inference either way about
whether it retains delivery. What does predict the outcome, in hindsight, is the distillation
source. Codebook 0 is distilled from WavLM, which of the representations tested here preserves
pragmatic contrast best, so it inherits a trace of that sensitivity, heavily degraded by
quantisation. The acoustic codebooks, optimised for waveform reconstruction, evidently spend their
capacity on signal detail that does not align with pragmatic categories.

The wider implication is that the paralinguistic content of a distilled codebook may track its
teacher model rather than the semantic or phonetic character conventionally attributed to that
stream. This is a claim the literature does not currently make, and it is one this study is
positioned to test rather than assume, which is why the codebook-level analysis in Chapter 4
probes every codebook individually instead of accepting a stream's conventional label.

**The transcript baseline.** The text embedding is two objects with two roles [3.5]. Because the
study holds the target word constant, an embedding of the word alone is identical across clips
and at chance by construction, so it is a manipulation check rather than a competitor. An embedding of the
surrounding discourse context is the substantive text baseline, because pragmatic cues leak into
neighbouring words. Distinguishing the two is essential to interpreting the results.

## 2.4 What tokenisation loses: prosody and paralinguistics under quantisation

A growing body of work supports the concern that discretisation specifically damages prosodic
and paralinguistic information, and it is this work that both motivates the central hypothesis
and constrains how strongly it can be stated. On prosody, ProsodyLM (Qian et al., 2025) argues
that mainstream token-then-model training is suboptimal for prosody and proposes explicit word-
level prosody tokens. Segmentation-Variant Codebooks (Sanders et al., 2025) makes the
complementary argument that a single flat token rate fails to preserve prosodic and paralinguistic
information. Both imply that standard tokenisation is not built to retain what this study targets.

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

## 2.5 Pragmatics and same-word meaning contrasts

The linguistic grounding of the project is a basic but powerful observation, which is that identical lexical
material can perform different speech acts depending on delivery and discourse context. "Yeah"
can signal agreement, backchannelling, disbelief, or impatience. "Right" can signal agreement,
correction, sarcasm, or challenge. "Sure" can signal consent, reluctance, or disbelief. "Great"
can signal approval, sarcasm, or resignation. In each, the words are fixed and the meaning is
carried by something else.

Operationalising pragmatic meaning through controlled same-phrase contrasts is what distinguishes
a substantive claim from a weak one. The weak version, "prosody matters," is uncontroversial and
untestable as a contribution. The strong version tests a concrete failure mode, namely whether a
representation collapses different meanings when the transcript is held constant. This framing
also disciplines interpretation. Because the lexical item is fixed, a representation that
separates the pragmatic classes cannot be doing so on lexical grounds, which removes the most
common confound in pragmatic and affective classification. It introduces a different risk, that
the separation tracks arousal rather than pragmatic force, which the design controls for directly
by labelling arousal independently and testing separability at matched arousal [3.3, Ch.4].

## 2.6 The closest precedent and the gap

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

A note on convergent design. Yang et al. (2026) independently adopt the same control at the level
of whole systems, requiring benchmark queries to carry neutral textual content so that a model
"cannot infer the speaker's state from words alone and must attend to vocal cues". That their
construction rule and this study's lexical control were arrived at separately is evidence the move
is the right one rather than an idiosyncrasy of this design. Their result also supplies the stake.
A cascaded pipeline that transcribes the query and discards speaking style entirely scores 3.18 on
their benchmark, while leading end-to-end speech-to-speech models reach only 3.37, and two score
below the pipeline. Systems built to preserve paralinguistic information perform close to systems
that throw it away. The present study asks whether the representation those systems consume is part
of the reason.

The two studies are complementary rather than overlapping. Theirs is behavioural and asks whether a
system responds appropriately, this one is representational and asks whether the contrast is
present to be responded to. Theirs uses mostly synthesised queries and acted corpora, this one
spontaneous speech. Theirs covers emotion, sarcasm, age and gender at the level of a dialogue turn,
this one pragmatic force within a single held-constant word.

The literature thus establishes three things and frames a fourth question. It establishes that discrete
tokenisation is lossy and weakest in the prosodic-paralinguistic band, that continuous self-
supervised encoders retain that band better than supervised or discretised alternatives, and that
speech representations recover pragmatic phenomena such as sarcasm better than text. The question
it frames, and what Chapter 3 is designed to test, is whether the loss under tokenisation is a loss
of meaning rather than of sound.
