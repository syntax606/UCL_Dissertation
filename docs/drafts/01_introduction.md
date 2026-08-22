<!-- GENERATED from the Word draft by src/45_export_draft.py.
     The .docx is authoritative. Edits made here will be overwritten. -->

# Chapter 1: Introduction

## 1.1 The same word, three different moves

Response tokens such as yeah, okay and right have long been problematic for accounts of meaning that must proceed from lexical content. Their propositional contribution is negligible, yet they are among the most frequent items in spontaneous dialogue, and the work they perform varies sharply across instances of what is orthographically a single word, from a neutral backchannel function to bitter sarcasm. Gardner (2001) characterises this class as deriving its interpretive force from phonetic form, prosodic shape and sequential placement rather than from lexical semantics. These properties are referred to throughout as delivery, meaning how something is said as distinct from which words are said. Gravano et al. (2012) demonstrate that the competing functions of affirmative cue words are distinguished in spontaneous speech by delivery. A warm yeah, a grudging yeah and a mocking yeah share a transcript and perform three distinct communicative acts. Two of Gardner's three properties are dynamic. Prosodic shape is a contour, a movement of pitch and loudness through the phrase, and sequential placement is a position in time. The experimental literature on ironic delivery reports the same emphasis, listing slower tempo and reduced F0 range alongside static properties such as pitch level (Rockwell, 2000; Lan et al., 2019), and Gravano et al. find word-final intonation among the most salient cues by which listeners disambiguate okay. What carries the contrast is therefore expected to be a matter of how the signal moves rather than only where it sits, which is why [1.3] asks whether what a codec loses is acoustic content or temporal organisation. Listeners recover that distinction from audio at 0.73 in the present study, against 0.65 from the transcript alone and a three-way chance level of 0.33, so the contrast is available without being categorical [4.1]. Items of this kind are therefore of methodological as well as descriptive interest, since they constitute naturally occurring minimal pairs in which lexical content is fixed and interpersonal force varies.

Spoken interaction with machines is meanwhile moving from turn-taking exchange to full-duplex conversation. The Moshi report states the limitation it was built to remove, that prior systems "rely on a segmentation into speaker turns, which does not take into account overlapping speech, interruptions and interjections" (Défossez et al., 2024), and its training explicitly includes backchannelling in both streams. Both streams are encoded by the same neural codec, which passes the waveform through an encoder and then quantises the result before anything reaches the language model. The codec therefore stands between the speaker and every component downstream, in two architecturally distinct stages, and what the codec declines to represent is rendered unavailable after passing through.

There is converging evidence that such systems handle delivery poorly, including end-to-end models scoring below a cascaded pipeline that discards it entirely (Yang et al., 2026), models following lexical content over acoustic evidence when the two conflict, at 8.60 per cent accuracy on acoustic ground truth against 81.55 per cent agreement with the language-implied answer for one system (Pang et al., 2026), and attacks that hold wording constant and vary only delivery succeeding far more often (Qian and Li, 2026). Behaviour cannot distinguish information that never reached the model from information that reached it and was ignored, and only the second is recoverable downstream.

## 1.2 Approach

A lexical control. A corpus of 873 clips of naturalistic political podcast audio, across 32 shows and 753 episodes, each containing one of eight short phrases whose pragmatic force varies while their wording does not. Each clip carries a fine-grained pragmatic function tag, from which interpersonal stance is derived, and separately and without conditioning on that tag, a judgement of arousal. Because the word is fixed within every contrast a probe cannot be reading lexical content, and because arousal is labelled independently, the design tests directly whether stance reduces to vocal energy.

A stage decomposition. Rather than comparing a continuous encoder against a token stream, each codec is probed immediately before and immediately after quantisation, on identical forward passes with identical pooling, so the rounding step is the only difference between conditions. This is run on three codecs of independent design, one distilled from a self-supervised teacher and two purely acoustic, two of which share a frame rate and differ in encoder architecture.

The dependence between the two moves is what licenses the result. A stage decomposition on an uncontrolled task localises the loss of something, and for a codec the likely something is phonetic detail, which such a system is built to preserve and which says nothing about the interpersonal layer. Holding the word fixed makes the cost assigned to each stage a cost in delivery specifically.

## 1.3 Research questions and hypotheses

RQ1. Is interpersonal pragmatic force recoverable from speech representations when lexical content is held constant?

RQ2. How much of it is retained by the representation deployed systems consume?

RQ3. Which stage of the pipeline is responsible for what is lost, and why?

RQ4. Is what is lost a matter of acoustic content or of temporal organisation?

Five hypotheses were formed before the analyses.

H1. Human listeners recover more stance from audio than from the transcript. A premise check rather than a finding, but a negative result would have ended this study. H2. Stance is linearly decodable from continuous representations under lexical control. H3. Stance is substantially less decodable from the deployed discrete representation. H4. The loss is principally attributable to quantisation, on the grounds that discretisation is the only step capable of rendering two distinct inputs identical. H5. Stance decodability is not reducible to arousal and survives when energy is held constant.

H1, H2, H3 and H5 are supported. H4 is not. Its falsification redirected the study, and four further hypotheses were formed and tested afterwards.

H6. The measured loss reflects the order-free readout rather than the representation. H7. Variable-frame-rate tokenisers, which allocate tokens to linguistic units rather than to a fixed clock, retain more. H8. The segmentation itself carries stance, through token count, rate and duration. H9. Order retention tracks whether the encoder has an architectural mechanism for representing time, rather than tracking frame rate.

H6, H7 and H8 are not supported. H9 was formed after an anomalous result on one codec and was then tested on a fourth codec not previously included, which is the strongest form of support available without retraining anything.

## 1.4 Contributions

A lexically controlled diagnostic corpus of 873 clips of naturalistic spontaneous speech across eight target phrases, annotated on two independently judged axes.

A stage-resolved measurement of codec loss, replicated on three codecs of independent design, showing the encoder to be the dominant contributor in every case and quantisation to cost little or nothing.

An account of what is lost. Not acoustic detail, since the codecs recover hand-crafted acoustic cues more faithfully than the model one of them distils from, but temporal organisation, shown by two measurements that share no machinery.

A controlled test of why. Two codecs matched at 75 Hz and differing in encoder architecture differ in how much frame order contributes, which excludes sampling density as the mechanism and yields a prediction that the next codec added can falsify.

Reporting of four unsupported hypotheses. H4 from the first round and H6 to H8 from the second. And of a measurement problem found in the study's own pipeline, namely that fold assignment alone moves scores by as much as several of the differences reported in this literature [3.7].

## 1.5 Structure

Chapter 2 situates the study in the literatures on discrete speech tokens, probing of speech representations, and the pragmatics of same-word contrasts. Chapter 3 describes the corpus, the annotation scheme, the representations, the readouts and the probing protocol. Chapter 4 reports five analyses. Chapter 5 makes three moves, locating the loss upstream of the tokens, establishing that what is lost is organisation rather than fidelity, and identifying the architectural property that predicts it. Chapter 6 states the limitations and sets out a programme of repair.
