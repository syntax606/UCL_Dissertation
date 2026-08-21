<!-- GENERATED from the Word draft by src/45_export_draft.py.
     The .docx is authoritative. Edits made here will be overwritten. -->

# Chapter 5: Discussion

## 5.1 The loss is upstream, and the encoder is why

The study was designed on the assumption that discretisation was the culprit, and the stage decomposition does not support it [4.3]. Three designs differing in objective, frame rate and quantiser agree on where the loss falls.

What the codecs do not agree on is how much they lose, and that variation is what carries the account. Temporal structure survives to the degree the encoder has an architectural mechanism for representing it, and sampling density is not that mechanism [4.4, 4.5].

This bears directly on two recent proposals. ProsodyLM (Qian, Y. et al., 2025a) introduces explicit word-level prosody tokens and Segmentation-Variant Codebooks (Sanders et al., 2025) quantises at multiple segmental units. Both are codebook-level interventions aimed at a prosody problem. If the majority of the loss precedes quantisation, a redesigned codebook operates on information the encoder has already declined to represent, and the ceiling on what it can recover is set upstream of the change. A second design family is better placed by the same reasoning, since X-Codec (Ye et al., 2024) injects teacher features before quantisation. The measurements predict an ordering between the two families rather than a verdict on any single system, and that ordering is testable on a common corpus.

Interventions at the encoder-LLM interface rather than at the codebook are consistent with this account. Pang et al. (2026) combine multiple audio encoder layers adaptively and apply preference optimisation to favour acoustically supported responses, raising one system from 17.40 to 65.20 per cent on their benchmark. That such gains are available without modifying the tokeniser supports the present conclusion that leverage sits upstream of the quantiser, though it addresses utilisation rather than the encoder loss measured here.

## 5.2 What is lost is organisation, and the organisation is temporal

The natural reading of a codec losing pragmatic content is that it discards the acoustic detail that content is built from. That reading is wrong. Recovering hand-crafted acoustic cues from each rung, the codecs do better than WavLM on every group except one, reaching 152 per cent on the contour features that stance is built from and 162 per cent on voice quality, using half the feature dimensions [4.4].

That result is weaker alone than it looks. A reconstruction objective is meant to retain waveform-recoverable descriptors, and eGeMAPS functionals are waveform descriptors, so a codec outperforming a masked-prediction model on them is close to what the training objectives predict. Its force comes from the pairing. The representation that stores the cues most faithfully reads stance off them worst, and the representation that stores them least faithfully reads stance best. Fidelity and readability are not the same quantity, and the deficit is in the second.

Two independent measurements say the missing organisation is temporal. Temporal is the one cue group the codecs fail to retain, falling to 78 per cent for the deployed histogram and 61 to 67 per cent for DAC while every other group holds at or above 97 per cent. And the order effect, measured against a frame-shuffled control at matched dimensionality, declines along the same ladder. Those two measurements share no machinery, so their agreement is not an artefact of either.

The deployed condition loses a further 0.070 through summarisation alone [4.3]. Liu et al. (2024) supply a mechanism that is not simply dimensionality. Codec encoders integrate context, so acoustically identical segments receive different codes depending on what surrounds them, and consistency falls as codebook depth increases. Code identity is therefore unstable in a way the vector those codes decode to is not, since reconstruction would otherwise fail. A summary over code indices inherits that instability and a summary over decoded vectors does not. This reaches further than the present measurement, because a deployed system consumes indices rather than decoded vectors.

One finding here sits against a near neighbour, and it concerns which layer of Whisper carries prosodic information rather than anything about the codec ladder. Qian, Figueroa and Skantze (2025b) report prosody concentrated in middle layers with Whisper the weakest of four models, where Whisper is among the strongest here and peaks at its final encoder layer. The disagreement, and two candidate accounts of it, are set out in [E.6].

## 5.3 What the negative results rule out

Three hypotheses were stated before testing and are not supported, and each removes a candidate explanation.

Variable-frame-rate tokenisation does not recover the loss. Measured against each configuration's own null, Mimi before quantisation reaches +0.139 against Sylber's +0.118 and DyCAST's +0.081 [4.6]. DyCAST is clearly below and Sylber is level, since 0.021 is inside the partition-noise threshold. Neither exceeds Mimi. This is consistent with what those systems set out to do rather than a failure of them. The syllabic lineage Sylber belongs to is built to extract coarse semantic units at low bitrate, and observes that existing tokenisations predominantly capture phonetic information (Baade et al., 2025). DyCAST aligns to characters, which is again a linguistic unit. A literature proposing dynamic frame rates to preserve timing (FlexiCodec, CodecSlime) is therefore proposing the right diagnosis with a mechanism these results suggest is insufficient [6.3].

Timing features alone carry no stance. Token count, rate and duration moments reach 0.316 and 0.338 against a null near 0.33. Whatever the temporal organisation consists of, it is not the coarse statistics of the segmentation, which rules out the simplest account of the order effect.

Order-aware summaries of the discrete streams score below the unigram histogram they were intended to improve on. Run lengths and change rates are meaningful operations on categorical codes, and they lose to counting. Taken with the instability Liu et al. describe, the reading is that code identity is too unstable a quantity to support temporal statistics over it.

## 5.4 What these results cannot say

Decodability above chance is not decodability at a useful level. On the sixty clips human annotators judged, the best model condition reaches 0.533 against their 0.730, and a human reading only the transcript reaches 0.650, exceeding every model condition including the one given both modalities [4.1]. The claims here concern what these representations carry relative to one another, not what they carry relative to a listener.

The architectural account is the best supported of the available explanations and it is not the only one. Gichamba and Busogi (2026) show an apparent architectural limit in DAC resolving into a training misconfiguration once sequence length was matched. Frozen public checkpoints cannot separate what an architecture can represent from what a particular training run taught it to represent. Settling that needs codecs trained under matched conditions differing only in the temporal mechanism.

The distillation observation is a correlation. Mimi's codebook 0 carries the stance signal and codebook 0 is the one distilled from WavLM, but seven acoustic codebooks adding 0.002 to what codebook 0 achieves alone does not establish that distillation caused it. That requires a codec trained twice.

Finally, this study measures whether information is linearly decodable from a frozen representation. It does not measure whether a system uses that information, and it addresses comprehension rather than generation. The defensible bridge to deployment is a necessary condition. A system cannot act on what its input representation does not carry, so these probes bound what any downstream model built on these tokens could achieve. That bound is worth knowing alongside work documenting audio language models failing to use paralinguistic information that is present, since the two failure modes are distinct and the remedies differ. Better modelling can address information that is available and ignored. Nothing downstream can address information that was never organised into a usable form.
