# Citation audit, Draft 6 to Draft 7

Every citation in Draft 6 checked against the PDFs in
`iCloud/UCL Compling/Dissertation/Aug 6` and its subfolders. 51 unique citations, 79
source files.

## Fixed in Draft 7

| change | reason |
|---|---|
| `Qian, Figueroa and Skantze (2025)` unified to `(2025b)` | the same paper appeared in two forms, at six sites. An a/b suffix only works if applied everywhere |
| Gichamba and Busogi downgraded from attribution to characterisation | the sentence is in their §4.1, but it describes Mimi's architecture rather than reporting a finding of their ablation, so it cannot serve as independent evidence for the architectural account |
| `Lotfian and Busso (2019)` replaced by `Busso et al. (2025)`, two sites | the PDF on file is *The MSP-Podcast Corpus* by Busso, Lotfian, Sridhar, Salman, Lin and others, which is a different and later paper |
| Dunbar et al. (2021) added alongside Schatz et al. (2013) | `ABX.pdf` is the ZeroSpeech **website**, not a paper. Dunbar et al. 2021 is on file, discusses ABX sixteen times, and supports the claim about multi-level evaluation suites |
| §6.2's opening rewritten | it repeated §5.4 near-verbatim. It now points back rather than restating |

## Sources still to obtain

None of these has a PDF anywhere in the folders. All four citations are correct as
written, verified against reference lists in papers that are on file, but the sources
themselves are absent.

| citation | full reference | why it matters |
|---|---|---|
| **Chen et al. (2022)** | WavLM: Large-Scale Self-Supervised Pre-Training for Full Stack Speech Processing. *IEEE JSTSP* 16(6), 1505–1518 | the distillation teacher, characterised in Table 2.1 |
| **Radford et al. (2023)** | Robust Speech Recognition via Large-Scale Weak Supervision. *ICML*, PMLR, 28492–28518 | Whisper, characterised in Table 2.1 |
| **Cho et al. (2025)** | Sylber: Syllabic Embedding Representation of Speech from Raw Audio. arXiv 2410.07168, ICLR 2025 | a system tested in [4.6] |
| **Schegloff (1982)** | Discourse as an interactional achievement. In Tannen (ed.), *Analyzing Discourse*, Georgetown UP, 71–93 | the continuer claim in [2.4], documented in `literature_references_verified.md` |
| **Schatz et al. (2013)** | Evaluating speech features with the minimal-pair ABX task. *Interspeech* | origin of the ABX design in [6.3]. Dunbar now carries the claim, so this is optional |

## To verify before submission

**Steensig (2019).** The PDF is a handbook chapter, *Conversation Analysis and
Affiliation and Alignment*, whose internal references stop around 2011. The year needs
checking against the volume.

**Busso et al. (2025).** The year is taken from the filename. No date appears in the
first two pages of the PDF, so the venue and year need confirming.

**Belinkov (2022).** Your PDF is arXiv 2102.12452v4 dated September 2021. The journal
version is *Computational Linguistics* 2022. Citing 2022 is right for the published
version, so cite the journal rather than the preprint.

## Checked and correct, despite appearances

**Biber and Finegan (1988).** The file is named 2009 but the content is *Discourse
Processes* 1988. The citation is right and the filename misleads.

**Mousavi et al. (2026).** `DASB.pdf` is TMLR 04/2026 and matches. Note that
`Mousavi et al 2025.pdf` is a **different** paper by the same first author, the TMLR
09/2025 survey, currently uncited. If the survey is ever cited it needs its own year.

**Gichamba and Busogi (2026).** Filed as `Gisamba 2026.pdf`. The filename is
misspelled, the citation is not.

## Adequacy

Paragraphs attributing something to other work without a citation were flagged
automatically. Six hits, five of them false positives in the abstract, a table caption
or an internal cross-reference, where citations are conventionally absent. The three
methodological citations, Bengio and Grandvalet, Bouthillier et al. and Misra et al.,
each sit at the sentence they license.
