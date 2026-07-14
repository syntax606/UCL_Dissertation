# Literature: verified references and gap audit

Cross-check of the Chapter 2 reference list against the actual PDFs on disk
(`~/Desktop/Dissert and Paper Archive/Dissert_Papers/`). Author lists, arXiv IDs, and
dates below were read directly from each paper's title page. Venues are only asserted where
the title page states them; otherwise flagged "verify venue". Nothing here is from memory
except the four clearly-standard references in section 2, which are noted as such.

## 1. Verified from the PDFs on disk

| # | Verified citation | arXiv (as printed) | Notes / correction to draft |
|---|---|---|---|
| Pasad 2021 | Ankita Pasad, Ju-Chieh Chou, Karen Livescu. *Layer-wise Analysis of a Self-Supervised Speech Representation Model.* | 2107.04734 | Draft correct (ASRU 2021 — verify venue). |
| Lin 2022 | Guan-Ting Lin, Chi-Luen Feng, Wei-Ping Huang, Yuan Tseng, Tzu-Han Lin, Chen-An Li, Hung-yi Lee, Nigel G. Ward. *On the Utility of Self-supervised Models for Prosody-related Tasks.* | 2210.07185v2, 26 Oct 2022 | Full author list now confirmed. Venue (IEEE SLT 2022) not on title page — verify. This is the SUPERB-prosody paper and your closest-precedent cite. |
| DASB | Pooneh Mousavi, Jarod Duret, Darius Petermann, Artem Ploujnikov, Luca Della Libera, Anastasia Kuznetsova, Cem Subakan, Mirco Ravanelli. *DASB — Discrete Audio and Speech Benchmark.* | 2406.14294v4, 21 Apr 2026 | **Published in TMLR 04/2026** (stated on title page). Add authors "Mousavi et al." and the TMLR venue. |
| ParaLBench | Zixing Zhang, Weixiang Xu, Zhongren Dong, Kanglin Wang, Yimeng Wu, Jing Peng, Runming Wang, Dong-Yan Huang. *ParaLBench: A Large-Scale Benchmark for Computational Paralinguistics over Acoustic Foundation Models.* | 2411.09349v1, 14 Nov 2024 | Add authors "Zhang et al. 2024." |
| Speaker-attrib probing | Aemon Yat Fei Chiu, Kei Ching Fung, Roger Tsz Yeung Li, Jingyu Li, Tan Lee. *A Large-Scale Probing Analysis of Speaker-Specific Attributes in Self-Supervised Speech Representations.* | 2501.05310v2, 18 Sep 2025 | Add authors "Chiu et al. 2025" (CUHK). Confirms the three-stage layer hierarchy you cite. |
| Discrete-token review | Yiwei Guo, Zhihan Li, Hankun Wang, Bohan Li, Chongtian Shao, Hanglei Zhang, Chenpeng Du, Xie Chen, Shujie Liu, Kai Yu. *Recent Advances in Discrete Speech Tokens: A Review.* | 2502.06490v1, 10 Feb 2025 | Add authors "Guo et al. 2025." |
| SER-from-discrete (recovery) | Esther Sun, Abinay Reddy Naini, Carlos Busso. *Recovering Performance in Speech Emotion Recognition from Discrete Tokens via Multi-Layer Fusion and Paralinguistic Feature Integration.* | 2601.17085v1, 23 Jan 2026 | **Key cite** for your "loss is recoverable" framing (CMU). Abstract confirms multi-layer fusion + openSMILE close the gap, and compares SpeechTokenizer/DAC/EnCodec. **The specific "6 to 14 percent drop" figure is NOT in the abstract — verify it against the paper body before quoting.** |
| Codec probing | Xuan Shi, Chang Zeng, Tiantian Feng, Shih-Heng Wang, Jianbo Ma, Shrikanth Narayanan. *Speech Codec Probing from Semantic and Phonetic Perspectives.* | 2603.10371v1, 11 Mar 2026 | **Key cite** for "semantic tokens are actually phonetic" and your codebook-0 reasoning (USC/Dolby). Add authors "Shi et al. 2026." |
| Moshi / Mimi | Alexandre Défossez, Laurent Mazaré, Manu Orsini, Amélie Royer, Patrick Pérez, Hervé Jégou, Edouard Grave, Neil Zeghidour (Kyutai). *Moshi: a speech-text foundation model for real-time dialogue.* | 2410.00037v2, 2 Oct 2024 | **Add the arXiv ID (2410.00037)** to your "Kyutai technical report" cite. This is the primary Mimi source. |

## 2. Standard references (not in the folder, but well-established — confident)

- **Chen, S., et al. (2022).** WavLM: Large-Scale Self-Supervised Pre-Training for Full Stack Speech Processing. *IEEE JSTSP* 16(6).
- **Hsu, W.-N., et al. (2021).** HuBERT: Self-Supervised Speech Representation Learning by Masked Prediction of Hidden Units. *IEEE/ACM TASLP.*
- **Radford, A., et al. (2023).** Robust Speech Recognition via Large-Scale Weak Supervision [Whisper]. *ICML.*
- **Castro, S., et al. (2019).** Towards Multimodal Sarcasm Detection (An _Obviously_ Perfect Paper) [MUStARD]. *ACL.*

## 3. Previously-unsourced citations — now VERIFIED against arXiv (web, 2026-07)

All six were confirmed to be real papers with correct IDs. Full details:

| Draft cite | Verified title | Authors | arXiv / venue |
|---|---|---|---|
| S2S-Arena (Jiang 2025) | *S2S-Arena: Evaluating Paralinguistic Instruction Following in Speech-to-Speech Models* | Feng Jiang, Zhiyu Lin, Yiyang Liu, Liumeng Xue, Fan Bu, Yuhao Du, Xiangying Chen, Benyou Wang, Haizhou Li | 2503.05085, Mar 2025 — draft **correct** |
| ParaS2SBench (Yang 2026, ICLR) | *ParaS2S: Benchmarking and Aligning Spoken Language Models for Paralinguistic-aware Speech-to-Speech Interaction* (the benchmark inside it is ParaS2SBench) | Shu-wen Yang, Ming Tu, Andy T. Liu, Xinghua Qu, Hung-yi Lee, Lu Lu, Yuxuan Wang, Yonghui Wu | 2511.08723, Nov 2025, **ICLR 2026** — "Yang et al." **correct**; add ID + full title |
| ProsodyLM | *ProsodyLM: Uncovering the Emerging Prosody Processing Capabilities in Speech Language Models* | Kaizhi Qian, Xulin Fan, Junrui Ni, Slava Shechtman, Mark Hasegawa-Johnson, Chuang Gan, Yang Zhang | 2507.20091, Jul 2025 |
| Segmentation-Variant Codebooks | *Segmentation-Variant Codebooks for Preservation of Paralinguistic and Prosodic Information* | Nicholas Sanders, Yuanchao Li, Korin Richmond, Simon King (Edinburgh) | 2505.15667, May 2025 |
| CodecBench | *CodecBench: A Comprehensive Benchmark for Acoustic and Semantic Evaluation* | Ruifan Deng, Yitian Gong, Qinghui Gao, Luozhijie Jin, Qinyuan Cheng, Zhaoye Fei, Shimin Li, Xipeng Qiu | 2508.20660, Aug 2025 — add subtitle |
| AudioCodecBench | *AudioCodecBench: A Comprehensive Benchmark for Audio Codec Evaluation* | Lu Wang, Hao Chen, Siyu Wu, Zhiyue Wu, Hao Zhou, Chengfeng Zhang, Ting Wang, Haodi Zhang | 2509.02349, Sep 2025 |
| "Modality Evolving Perspective" (placeholder) | *Why Do Speech Language Models Fail to Generate Semantically Coherent Outputs? A Modality Evolving Perspective* | Hankun Wang, Haoran Wang, Yiwei Guo, Zhihan Li, Chenpeng Du, Kai Yu (SJTU X-LANCE) | **2412.17048**, updated Jan 2026 — gap now filled |

Note: the Modality-Evolving paper (2412.17048) shares authors with the discrete-token review
(Guo, Li, Du, Yu) and directly supports §2.4 — it finds speech tokens are mainly phonetic not
semantic (factor A), and that paralinguistic variability is the most disruptive factor (factor
C). Strong cite for the framing, not just a placeholder.

## 4. On disk but currently UNCITED — candidates to add (or consciously drop)

These are in your paper folder but do not appear in the Chapter 2 reference list. Each has a
plausible home; decide whether to fold them in:

- **Mohebbi, Chrupała, Zuidema, Alishahi, Titov (2410.03037, 2024).** *Disentangling Textual and Acoustic Features of Neural Speech Representations.* Directly supports §2.3/§2.7 (separating content from acoustic/speaker) — arguably worth citing.
- **Sun/... wait** — see below, mostly emotion-adjacent:
- **Gong, Liu, Luo, Karlinsky, Glass (2309.14405, 2023).** *Joint Audio and Speech Understanding* (LTU-AS). Speech+paralinguistics understanding; optional for §2.3.
- **Zhao et al. (2502.18186, 2025).** *Steering LM to Stable SER via Contextual Perception and CoT* (C2SER). SER stability; optional for §2.4.
- **Mitra, Romana, Tran, Azemi / Apple (2503.22711, ICLR 2025 workshop).** *Modeling Speech Emotion with Label Variance ... Across Speakers and Unseen Acoustic Conditions.* Supports your label-confidence and speaker-generalization choices (§2.7 / Ch. 3).
- **Ma et al. (2509.08454, 2026).** *Mechanistic Interpretability of LoRA-Adapted Whisper for SER.* Optional for §2.3.2 (Whisper + emotion + interpretability).
- **Chapariniya et al. / U Zürich (2603.23650, FG 2026).** *Foundation Model Embeddings Meet Blended Emotions (BLEMORE).* Tangential, but its finding that Wav2Vec2 prosody layers 6–12 beat finetuning echoes your mid-layer point.

## 5. Specific factual claims to double-check before submission

1. **The "6 to 14 percent drop in macro F1"** attributed to 2601.17085 — not stated in the abstract; confirm from the paper body.
2. **Mimi codebook count.** Draft §2.3.3 says "eight residual quantizers at 12.5 Hz"; the Frisson Labs blog says Mimi emits "32 token streams" at 12.5 Hz (one frame / 80 ms). Both can be reconciled (Mimi is trained with up to 32 quantizers; Moshi/deployment uses the first 8), but state it precisely so it is not read as a contradiction. Cite the Moshi paper, not the blog, for the number.
3. **Blog is not a citable source** for the mechanism; use it for intuition only and cite Défossez et al. (2410.00037) for all Mimi/Moshi technical claims.
