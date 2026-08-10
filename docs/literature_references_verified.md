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

## 5. Codec design batch — verified from arXiv (web, 2026-08)

Added because the bibliography was weighted toward *evaluating* codecs and carried almost nothing
on how they are *built*, which is conspicuous the moment Chapter 6 proposes changing a training
objective. All eight verified against the arXiv abstract page. Cited in 2.2, 2.4, 3.5, 5.2, 5.4, 6.4.

| Short cite | Verified citation | arXiv / venue | Role |
|---|---|---|---|
| Zeghidour et al., 2021 | Neil Zeghidour, Alejandro Luebs, Ahmed Omran, Jan Skoglund, Marco Tagliasacchi. *SoundStream: An End-to-End Neural Audio Codec.* | 2107.03312, Jul 2021 | Origin of the RVQ codec architecture. Lineage only. |
| Défossez et al., 2022 | Alexandre Défossez, Jade Copet, Gabriel Synnaeve, Yossi Adi. *High Fidelity Neural Audio Compression* [EnCodec]. | 2210.13438, 24 Oct 2022 | Lineage. Note Défossez authors both this and Moshi, a continuity worth one clause. |
| Kumar et al., 2023 | Rithesh Kumar, Prem Seetharaman, Alejandro Luebs, Ishaan Kumar, Kundan Kumar. *High-Fidelity Audio Compression with Improved RVQGAN* [Descript Audio Codec]. | 2306.06546, 11 Jun 2023, **NeurIPS 2023** | **Required.** DAC carries a headline result in 4.6 and was previously uncited anywhere. |
| Zhang et al., 2024 | Xin Zhang, Dong Zhang, Shimin Li, Yaqian Zhou, Xipeng Qiu. *SpeechTokenizer: Unified Speech Tokenizer for Speech Large Language Models.* | 2308.16692v2, 31 Aug 2023, rev 23 Jan 2024, **ICLR 2024** | **Key cite.** Introduced guiding the first RVQ quantiser with an SSL teacher (HuBERT). Mimi's codebook 0 inherits this design. The distillation-loss detail is in the methods, **not the abstract** — cite the body. |
| Ye et al., 2024 | Zhen Ye, Peiwen Sun, Jiahe Lei, Hongzhan Lin, Xu Tan, Zheqi Dai, Qiuqiang Kong, Jianyi Chen, Jiahao Pan, Qifeng Liu, Yike Guo, Wei Xue. *Codec Does Matter: Exploring the Semantic Shortcoming of Codec for Audio Language Model* [X-Codec]. | 2408.17175, 30 Aug 2024, **AAAI 2025** | **Key cite.** Injects teacher features *before* RVQ plus a semantic reconstruction loss after. The design family the 4.6 decomposition favours. |
| Jo et al., 2025 | Daejin Jo, Jeeyoung Yun, Byungseok Roh, Sungwoong Kim. *LM-SPT: LM-Aligned Semantic Distillation for Speech Tokenization.* | 2506.16738, 20 Jun 2025 | Supports the 6.4 teacher-layer point. States the convention is HuBERT layer 9 or an all-layer average. **Verify the layer claim in the body before quoting it.** |
| Ren et al., 2024 | Wenze Ren, Yi-Cheng Lin, Huang-Cheng Chou, Haibin Wu, Yi-Chiao Wu, Chi-Chun Lee, Hung-yi Lee, Yu Tsao. *EMO-Codec: An In-Depth Look at Emotion Preservation capacity of Legacy and Neural Codec Models With Subjective and Objective Evaluations.* | 2407.15458, 22 Jul 2024 | **Qualifies a claim.** Affect under codecs has been measured, so "no metric is sensitive to it" was too strong and has been narrowed in 5.4, 6.3 and 6.4. Evaluation study rather than a reusable metric, works via resynthesis plus SER, uses IEMOCAP (acted), categorical emotion. |
| Shi et al., 2026b | Jiacheng Shi, Hongfei Du, Xinyuan Song, Y. Alicia Hong, Yanfu Zhang, Ye Gao. *AffectCodec: Emotion-Preserving Neural Speech Codec for Expressive Speech Modeling.* | 2605.11098, 11 May 2026, **ACL Findings 2026** | Emotion-guided latent modulation before quantisation, relation-preserving distillation. Nearest existing work to the 6.4 proposal, which is why 6.4 differentiates on the supervised quantity rather than the mechanism. |
| Meng et al., 2026 | Zhaoyang Meng, Zhengyao Ma, Kecan Mao, Yingming Gao, Ya Li. *AffectCodec: Emotion-Preserving Neural Speech Codec with Block-Diagonal Residual FSQ.* | 2605.23373, 22 May 2026 | Block-diagonal input/output projections separating emotion and acoustic subspaces. Operates on the same projection surface the 3.5 quantiser-space analysis identifies. |

## Linguistics batch (verified 2026-08-09 from title pages of PDFs in
## iCloud/UCL COMPLING/DISSERTATION/Aug 6, except where noted)

Closes the structural gap that every citation in the drafts was a speech-engineering paper and none
was linguistics. Read directly from each PDF's first page, not from memory.

### Prosody of irony and sarcasm

| Short cite | Verified citation | Venue | What it gives you |
|---|---|---|---|
| Rockwell, 2000 | Patricia Rockwell. *Lower, Slower, Louder: Vocal Cues of Sarcasm.* | Journal of Psycholinguistic Research 29(5) | Cue inventory: slower tempo, greater intensity, lower pitch. **And the key caveat.** Listeners discriminated *posed* sarcasm from nonsarcasm but **not spontaneous sarcasm**. |
| Bryant and Fox Tree, 2002 | Gregory A. Bryant, Jean E. Fox Tree. *Recognizing Verbal Irony in Spontaneous Speech.* | Metaphor and Symbol 17(2), 99-119 | Spontaneous irony recognition. |
| Bryant and Fox Tree, 2005 | Gregory A. Bryant, Jean E. Fox Tree. *Is there an Ironic Tone of Voice?* | Language and Speech 48(3), 257-277 | The dedicated-marker versus contextual-recognition controversy. |
| Lan et al., 2019 | Chen Lan, Pak Long Hui, Wenwei Xu, Peggy Mok. *Revisiting Acoustic Markers of Sarcasm in Cantonese.* | ICPhS 2019, CUHK | Six measured features: speech rate, mean F0, F0 range, mean amplitude, amplitude range, HNR. Cross-linguistic. |

### Stance as a construct

| Short cite | Verified citation | Venue |
|---|---|---|
| Du Bois, 2007 | John W. Du Bois. *The stance triangle.* In *Stancetaking in Discourse: Subjectivity, evaluation, interaction* | Benjamins. **Verify the editor attribution**, the PDF header runs Du Bois and Englebretson together. |
| Biber and Finegan, 1988 | Douglas Biber, Edward Finegan. *Adverbial stance types in English.* | Discourse Processes 11(1), 1-34 |
| Stivers, 2008 | Tanya Stivers. *Stance, Alignment, and Affiliation During Storytelling: When Nodding Is a Token of Affiliation.* | Research on Language and Social Interaction 41(1), 31-57 |
| Steensig, 2019 | Jakob Steensig. *Conversation Analysis and Affiliation and Alignment.* | The Encyclopedia of Applied Linguistics |

### Response tokens

| Short cite | Verified citation | Venue |
|---|---|---|
| Gravano et al., 2012 | Agustín Gravano, Julia Hirschberg, Štefan Beňuš. *Affirmative Cue Words in Task-Oriented Dialogue.* | Computational Linguistics 38(1) |

Better aimed than the CA classics for this study. It is specifically about *okay* and *alright*, their
functional ambiguity between agreement, continued attention and topic shift, their differing
acoustic and prosodic realisation in spontaneous dialogue, and it frames that ambiguity as a problem
for spoken dialogue systems. It is the citation for the claim in the README that neutral stance
concentrates in the agreement particles as a linguistic property rather than a sampling artefact.

### Response tokens, expanded (verified 2026-08-09 from publisher and archive records, not on disk)

Added because [3.2] previously rested the entire phrase-set justification on one citation. The
agreement particles now have four sources; the evaluative and challenge families have none, and
[3.2] says so explicitly rather than implying an established classification.

| Short cite | Verified citation | Venue | Role |
|---|---|---|---|
| Gardner, 2001 | Rod Gardner. *When Listeners Talk: Response Tokens and Listener Stance.* | John Benjamins, Pragmatics and Beyond New Series 92 | **The key addition.** Book-length treatment of the class (*uh-huh*, *oh*, *mm*, *yeah*, *right*, *mm-hm*), arguing these carry no dictionary meaning but convey listener stance through phonetic form, prosodic shape, placement and timing. The subtitle carries the analytic term used throughout this study. |
| Schegloff, 1982 | Emanuel A. Schegloff. *Discourse as an interactional achievement: some uses of "uh huh" and other things that come between sentences.* In Deborah Tannen (ed.), *Analyzing Discourse: Text and Talk* | Georgetown University Press, 71-93 | The canonical source for continuers, supporting the claim that backchannelling is a function of this class rather than a sampling artefact. |
| Beach, 1993 | Wayne A. Beach. *Transitional regularities for "casual" Okay usages.* | Journal of Pragmatics 19(4), 325-352 | *Okay* pivoting at transition spaces, receipting prior talk while shifting to next matters. Describes the `topic_closure` tag and explains why *okay* carries 51 of the 121 low-arousal neutral clips [B.5]. |
| Gardner, 2007 | Rod Gardner. *The Right connections: Acknowledging epistemic progression in talk.* | Language in Society 36(3), 319-341 | Three distinct uses of *right*, namely epistemic progression, confirmation, and change of activity. |

**Acquire before submission.** None of these four is in the iCloud library. Author, year, title and
venue were verified against publisher and archive records rather than title pages, which is a weaker
standard than the rest of this document. Page ranges in particular should be confirmed from the
sources themselves.

**Nothing found for the other two families.** No source was located for *sure*, *great*, *fine*,
*really* or *come on*. [3.2] therefore states that the evaluative and challenge groupings are made on
functional grounds for this study.

### Acted against spontaneous speech

| Short cite | Verified citation | Venue |
|---|---|---|
| Lotfian and Busso, 2019 | Reza Lotfian, Carlos Busso. *Building Naturalistic Emotionally Balanced Speech Corpus by Retrieving Emotional Speech from Existing Podcast Recordings.* | IEEE Trans. Affective Computing |
| Busso et al., 2025 | Carlos Busso, Reza Lotfian, Kusha Sridhar, Ali N. Salman, Wei-Cheng Lin, Lucas Goncalves, Srinivas Parthasarathy, Abinay Reddy Naini, Seong-Gyun Leem, Luz Martinez-Lucas, Huang-Cheng Chou, Pravin Mote. *The MSP-Podcast Corpus.* | 2509.09791 |
| Scherer, 2003 | Klaus R. Scherer. *Vocal communication of emotion: A review of research paradigms.* | Speech Communication 40, 227-256 |

Lotfian and Busso is the corpus-design justification: podcast-derived, built expressly because acted
emotion is unrepresentative. Sun et al. (2026), already cited, evaluates on MSP-Podcast.

### Probing methodology

| Short cite | Verified citation | Venue |
|---|---|---|
| Hewitt and Liang, 2019 | John Hewitt, Percy Liang. *Designing and Interpreting Probes with Control Tasks.* | 1909.03368 |
| Belinkov, 2022 | Yonatan Belinkov. *Probing Classifiers: Promises, Shortcomings, and Advances.* | 2102.12452, Computational Linguistics |
| de la Fuente and Jurafsky, 2024 | Antón de la Fuente, Dan Jurafsky. *A layer-wise analysis of Mandarin and English suprasegmentals in SSL speech models.* | 2408.13678 |
| Schatz et al., 2013 | Thomas Schatz, Vijayaditya Peddinti, Francis Bach, Aren Jansen, Hynek Hermansky, Emmanuel Dupoux. *Evaluating speech features with the Minimal-Pair ABX task: Analysis of the classical MFC/PLP pipeline.* | Interspeech 2013. **Not on disk, web-verified. Cite this as the method.** |
| Schatz, 2016 | Thomas Schatz. *ABX-Discriminability Measures and Applications.* | PhD dissertation, Université Paris 6. HAL tel-01407461. The fuller treatment, and the reference Dunbar et al. use. Optional second cite. |
| Dunbar et al., 2021 | Ewan Dunbar, Mathieu Bernard, Nicolas Hamilakis, Tu Anh Nguyen, Maureen de Seyssel, Patricia Rozé, Morgane Rivière, Eugene Kharitonov, Emmanuel Dupoux. *The Zero Resource Speech Challenge 2021: Spoken language modelling.* | 2104.14700, Interspeech 2021. On disk. **Uses** ABX rather than introducing it. Cite for the pattern of a training-free distance measure reported inside a multi-level evaluation suite, which is the precedent for the Chapter 6 metric proposal. |

### Expressive speech systems and benchmarks

| Short cite | Verified citation | Venue |
|---|---|---|
| de Seyssel et al., 2023 | Maureen de Seyssel, Antony D'Avirro, Adina Williams, Emmanuel Dupoux. *EmphAssess: a Prosodic Benchmark on Assessing Emphasis Transfer in Speech-to-Speech Models.* | 2312.14069, Meta AI |
| Nguyen et al., 2023 | Tu Anh Nguyen, Wei-Ning Hsu, Antony D'Avirro, Bowen Shi, Itai Gat and others. *EXPRESSO: A Benchmark and Analysis of Discrete Expressive Speech Resynthesis.* | Meta AI |
| Nguyen et al., 2024 | Tu Anh Nguyen, Benjamin Muller, Bokai Yu, Marta R. Costa-jussà and others. *SPIRIT-LM: Interleaved Spoken and Written Language Model.* | Meta AI |
| Choi et al., 2024 | Kwanghee Choi, Ankita Pasad, Tomohiko Nakamura, Satoru Fukayama, Karen Livescu, Shinji Watanabe. *Self-Supervised Speech Representations are More Phonetic than Semantic.* | 2406.08619 |

Choi et al. shares Pasad and Livescu with the 2021 layer-wise paper already cited, and is the primary
source for the phonetic-not-semantic point currently attributed to Sicherman and Adi and to Arora et
al. in the 2.2 footnote. EmphAssess, Expresso and Spirit-LM are one Meta group under Dupoux, who is
also an author on the ABX paper, so the four can be introduced together.

### Do not cite

Awasthi and Chavan (2025), *Advancing Sarcasm Detection: The Case for Naturalistic Conversational
Datasets*, IJLTEMAS. Present in the Sarcasm detection folder. The venue is not one to cite in a UCL
dissertation.

### Terminology batch (added 2026-08, cited in the 2.2 footnote)

| Short cite | Verified citation | arXiv / venue | Role |
|---|---|---|---|
| Sicherman and Adi, 2023 | Amitay Sicherman, Yossi Adi. *Analysing Discrete Self Supervised Speech Representation for Spoken Language Modeling.* | 2301.00591, **ICASSP 2023** | The canonical cite for "semantic" units being phonetic. Finds units correlate strongly with phonemes and phoneme families and weakly with speaker or gender. |
| Arora et al., 2025 | *On The Landscape of Spoken Language Models: A Comprehensive Survey.* | 2504.08528 | Major survey that deliberately adopts "phonetic tokens" over "semantic tokens" for this reason. Worth citing as a survey independent of the footnote. **Verify the full author list from the title page before submission.** |

### Three citation collisions to handle consistently

1. **Two unrelated papers named AffectCodec**, eleven days apart in May 2026, with entirely
   different author lists (2605.11098 and 2605.23373). Never refer to "AffectCodec" unqualified.
   Cite by author and arXiv ID.
2. **Two different Shi et al. 2026.** Xuan Shi et al. (2603.10371, codec probing) is cited
   throughout as *Shi et al., 2026*. Jiacheng Shi et al. (2605.11098) is therefore entered as
   **Shi et al., 2026b**. Confirm the final reference list preserves the a/b suffixes.
3. **Two different Zhang et al. 2024, and two different Wang et al. 2025.** Xin Zhang et al.
   (SpeechTokenizer, 2308.16692) is **2024a**; Zixing Zhang et al. (ParaLBench, 2411.09349) is
   **2024b**. Wang et al. on contextual paralinguistics (2508.07273) is **2025a**; Lu Wang et al.
   (AudioCodecBench, 2509.02349) is **2025b**. Both pairs were briefly ambiguous in the drafts and
   are now suffixed throughout.

### What this batch changed in the drafts

- 2.2 gained a codec-design lineage paragraph, and 2.4 gained an affect-preservation paragraph.
  Chapter 2 is now further over its 2,300 budget and needs a trim pass.
- 3.5 gained a DAC paragraph and an *Isolating quantisation* paragraph. 3.6 went from six analyses
  to seven, adding the quantisation ladder. Both were reported in Chapter 4 with no methods entry.
- 5.2 gained the prediction that pre-quantisation interventions are better placed than
  codebook-level ones, which converts a criticism of two papers into a testable ordering.
- 5.4, 6.3 and 6.4 narrowed the metric-insensitivity claim from "no standard codec metric" to
  "the metrics routinely reported for codecs", and 5.4 now argues that categorical emotion
  supervision is arousal-loaded and so favours the axis this study finds surviving.

## 6. Specific factual claims to double-check before submission

1. **The "6 to 14 percent drop in macro F1"** attributed to 2601.17085 — not stated in the abstract; confirm from the paper body.
2. **Mimi codebook count.** Draft §2.3.3 says "eight residual quantizers at 12.5 Hz"; the Frisson Labs blog says Mimi emits "32 token streams" at 12.5 Hz (one frame / 80 ms). Both can be reconciled (Mimi is trained with up to 32 quantizers; Moshi/deployment uses the first 8), but state it precisely so it is not read as a contradiction. Cite the Moshi paper, not the blog, for the number.
3. **Blog is not a citable source** for the mechanism; use it for intuition only and cite Défossez et al. (2410.00037) for all Mimi/Moshi technical claims.
