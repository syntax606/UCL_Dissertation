# Dissertation outline and word budget

**Working title:** Transcript-Equivalent Pragmatic Contrast in Speech Representations:
A Diagnostic Probing Study

**Word limit:** 10,000 words, **excluding references** (confirmed). Abstract, tables and
captions, and appendices are assumed excluded too — confirm against the module handbook and
rebalance if not. Budgets below sum to 10,000 for the main body (Chapters 1–6).

| Section | Budget | Running total |
|---|---:|---:|
| Abstract (excluded) | ~250 | — |
| 1. Introduction | 1,200 | 1,200 |
| 2. Literature Review | 2,300 | 3,500 |
| 3. Data and Methods | 2,600 | 6,100 |
| 4. Results | 1,900 | 8,000 |
| 5. Discussion | 1,200 | 9,200 |
| 6. Conclusion, Limitations, Future Work | 800 | 10,000 |
| References (excluded) | — | — |
| Appendices (excluded) | — | — |

---

## Abstract (~250, excluded)
One-line result (continuous audio preserves stance, deployed discrete tokens collapse most of
it), plus method (lexical-control probing, naturalistic podcast audio) and headline numbers.

## 1. Introduction (~1,200)
- 1.1 Motivation: the same word carries opposite pragmatic force ("yeah" sincere vs sarcastic),
  and deployed speech-to-speech systems make this a live problem, not a curiosity.
- 1.2 The gap: prior pragmatic-speech results confound delivery with word choice.
- 1.3 Contribution: the lexical-control move (hold the word constant), plus the
  continuous-versus-deployed-discrete comparison absent from prior probing work.
- 1.4 Research questions and hypotheses (H1–H5, including the matched-arousal hypothesis).
- 1.5 Roadmap.

## 2. Literature Review (~2,300)  [compress from the ~14-page draft]
- 2.1 The speech-language-model turn and discrete speech tokens (acoustic vs semantic).
- 2.2 The five representations under test and their known granularity (WavLM/HuBERT layer
  hierarchy; Whisper's lexical bias; Mimi and codebook 0; the two text baselines).
- 2.3 What quantization loses: prosody and paralinguistics under discretization
  (recoverable-with-effort vs default-loss; the deployment-relevant framing).
- 2.4 Pragmatics and same-word meaning contrasts (the linguistic grounding).
- 2.5 The closest precedent (Lin et al. 2022) and the precise gap.
- 2.6 Methodological consequences the literature forces onto the design.
- **Cut plan:** lead on the gap; trim survey breadth; push benchmark enumeration to a
  compressed related-work density. This is the section most over budget as drafted.

## 3. Data and Methods (~2,600)
- 3.1 Corpus and the eight target phrases; naturalistic (not acted) audio.
- 3.2 Two-tier annotation scheme (fine function tag -> stance + arousal + confidence) and why
  two orthogonal axes rather than a single scale.
- 3.3 Premise check: human validation as the go/no-go gate before any modelling.
- 3.4 Representations and feature extraction: mean+std per-layer pooling for WavLM/HuBERT/
  Whisper (valid-frame for Whisper), Mimi codebook-1..7 histograms, target-only and
  discourse-context text embeddings; three context windows.
- 3.5 Probing protocol: logistic-regression probes, GroupKFold by episode, macro-F1,
  episode-cluster bootstrap CIs, permutation tests.
- 3.6 The six analysis views: pooled 3-way (A), context-window (B), per-phrase within-word
  lexical control (C), matched-arousal (D), speaker-identity control (E), training-free CPS (F).

## 4. Results (~1,900)
- 4.1 Premise check (transcript-with-context 0.65, audio+transcript 0.73; chance 0.33).
- 4.2 Pooled stance decodability with permutation significance (headline table:
  WavLM 0.573, Whisper 0.564, HuBERT 0.520, Mimi 0.352, text 0.38-0.49; all p<=0.01).
- 4.3 Layer-wise and context-window sweep.
- 4.4 Per-phrase within-word contrast (the lexical control): WavLM mean 0.659 vs text 0.534.
- 4.5 Matched-arousal and speaker-identity controls (both hold for the audio models).
- 4.6 CPS with the metric-sensitivity/underpowered caveat.

## 5. Discussion (~1,200)
- 5.1 Continuous preserves, deployed-discrete collapses: interpretation.
- 5.2 Deployment relevance (Moshi/Mimi; default off-the-shelf tokenization is the condition
  that matters; loss is recoverable only with deliberate effort).
- 5.3 Reading the text baselines (discourse-recoverable vs delivery-borne contribution).
- 5.4 Relation to prior work: what Lin et al. established, what the lexical control adds.

## 6. Conclusion, Limitations, Future Work (~800)
- Contribution restated; CPS limitation and future work (draw from docs/limitations.md).

## References (excluded)
Verified list in docs/literature_references_verified.md.

## Appendices (excluded)
Codebook; per-phrase x stance x arousal counts; full six-view results table
(results/probe_results.txt); probe hyperparameters; annotator instructions; premise-check design.
