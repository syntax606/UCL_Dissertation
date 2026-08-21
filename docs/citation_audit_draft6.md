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

## Sources obtained, checked 2026-08-21

All five arrived in the Aug 6 folder and every entry was written from memory before the
PDF existed. Each is now checked against its own title page. All five were correct as
written; three gain a detail the source supplies and one is worth a note.

| citation | verified from | outcome |
|---|---|---|
| **Chen et al. (2022)** | arXiv 2110.13900v5, 17 Jun 2022 | all nineteen authors match in order. Preprint, so the JSTSP volume and pagination remain from the published version |
| **Radford et al. (2023)** | arXiv 2212.04356v1, 6 Dec 2022 | six authors match. Preprint, so the ICML year and PMLR pagination remain from the published version |
| **Cho et al. (2025)** | arXiv 2410.07168v2, 2 Mar 2025 | the title page carries its own venue line, *Published as a conference paper at ICLR 2025*, so nothing is inferred. Its abstract gives 4.27 tokens per second, which is the source of Table 2.1's rate for Sylber |
| **Schatz et al. (2013)** | Interspeech 2013, Lyon | fully verified. First page 1781, last page 1785, so the range is read rather than assumed. Gains the ISCA imprint and DOI `10.21437/Interspeech.2013-441` |
| **Schegloff (1982)** | GURT 1981 volume | fully verified. Copyright page gives 1982, contents page puts the chapter at 71 with the next at 94. See the note below |

**Schegloff's year has a defensible alternative.** The volume's own Bibliographic Notice
prescribes citing the series by Round Table year rather than by copyright year, and gives a
worked example that would make this **Schegloff (1981)**. The copyright page says 1982 and
the conversation-analytic literature cites 1982 throughout, so 1982 stands, but an examiner
who opens the front matter will find the instruction. The entry now names the GURT volume
alongside the cover title so both are visible.

Two entries carry a caveat that is not about this study's diligence. Chen and Radford are
preprints, and preprints do not state the venue of the version they became. Their volume and
pagination are the one class of detail in the bibliography not read off a title page, which
is also true of Belinkov below.

## The twelve outstanding details, cleared 2026-08-21

Every one was checked against the copy on file. None was wrong. They split into two
kinds, and only the first kind was ever a question about diligence.

**Six were answerable from the source and are now read rather than assumed.**

| citation | where the answer was | outcome |
|---|---|---|
| Bryant and Fox Tree (2005) | running head of page 1 | `LANGUAGE AND SPEECH, 2005, 48 (3), 257-277`. Entry already exact |
| Rockwell (2000) | page 1 header and last page | `Vol. 29, No. 5, 2000`, opens at 483, last page numbered 495 |
| Stivers (2008) | the publisher's own cover sheet | Taylor & Francis prints a *To cite this article* line giving 41:1, 31–57 and the DOI. Gains the DOI |
| Gravano et al. (2012) | running head and last page | `Computational Linguistics, Volume 38, Number 1`. Opens the issue at 1, last page numbered 39 |
| Du Bois (2007) | volume front matter and page numbers | the open question was the editor attribution, and the front matter settles it. Englebretson edits, Du Bois writes. Pages run 139 to 182 |
| Scherer (2003) | page 1 header and PII | `Speech Communication 40 (2003) 227-256`. Gains the DOI. Elsevier headers carry no issue number, and 1–2 is the *Speech and Emotion* double issue |

**Six were not questions about the entry at all.** In each case the copy held is the
preprint, and a preprint cannot state the venue of the version it became. Marking these
with a question mark implied a doubt about the citation when the only limitation was in
the copy. They now carry `[P]`, which says what is actually true: everything except the
venue, volume and pagination is read from the source, and the arXiv identifier of the copy
consulted is given so a reader can see which one that is.

Borsos et al., Bouthillier et al., Hewitt and Liang, Lin et al., Sicherman and Adi, and,
for consistency, Belinkov, Chen et al. and Radford et al., which already carried the same
caveat in a code comment rather than on the page. Eight entries in total.

**Sun et al. (2026) was neither.** There is no published version to be missing. The entry
put the authors' institution where a venue belongs, which is not what a venue is. It is
now cited as the preprint it is, `arXiv:2601.17085`.

Bibliography: 52 entries, 44 fully verified, 8 preprint-sourced, nothing outstanding.

## Resolved, checked against the title pages

**Steensig, corrected from 2019 to 2026.** The year was wrong and matched no edition. The
copy on file states its own provenance in the footer of its first page, *The Encyclopedia of
Applied Linguistics*, edited by Carol A. Chapelle, © 2026 John Wiley & Sons, DOI
`10.1002/9781405198431.wbeal0196.pub2`. The `pub2` suffix marks it a revision of the
original entry, which is why the internal references stop around 2011 while the publication
year does not. 2026 is the version read here and is what both the draft and the bibliography
now cite. Corrected at one site in [2.4].

**Busso et al. (2025), year confirmed, venue corrected.** The title page gives
arXiv:2509.09791v1, 11 September 2025, manuscript received 10 September 2025. The year taken
from the filename was right. The venue was not. The bibliography had *IEEE Transactions on
Affective Computing*, but no venue is stated on the paper and its revision line is still
blank, so it is cited as a preprint. The authors carry IEEE affiliations and the paper is
formatted for an IEEE journal, which is presumably where the entry came from.

**Belinkov (2022), confirmed.** The PDF is arXiv 2102.12452v4, and its own front matter
gives the venue rather than leaving it to inference: a *Computational Linguistics* squib,
ACL copyright, accepted for publication 8 September 2021. That places the published version
in 48(1) of 2022, which is what the draft cites at both sites and what the bibliography
already carried. The volume and pagination are from the published version, not from the
preprint on file, which is the one detail here not read off a title page.

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

## Version pinning, 2026-08-21

Every arXiv identifier in the bibliography now carries its version suffix, 33 in total,
each read from the stamp on the copy held rather than from the live listing.

A bare identifier resolves to whatever the latest revision happens to be, which is not
necessarily the document a sentence in the draft is true of. That matters in eight places.
The draft quotes three preprints verbatim and takes specific figures from five, and six of
those eight are 2026 papers recent enough to be revised again.

**The three quotations were checked against the pinned versions and are verbatim.**

| quoted in | source | version | note |
|---|---|---|---|
| [1.1] | Moshi | `2410.00037v2` | the text hyphenates across a line break as "segmenta- tion", which is why a naive string search misses it |
| [2.3] | FlexiCodec | `2510.00981v3` | likewise "dis- cards" |
| [2.5] | ParaS2S | `2511.08723v2` | title page also confirms the venue, "Published as a conference paper at ICLR 2026" |

The ParaS2S entry had no identifier at all, which was the weakest point in the set: a
verbatim quotation with nothing pinning it to a version. It now carries one.

**The figures are pinned to** `2605.27772v1` (Pang), `2601.17085v1` (Sun),
`2601.13835v1` (O'Connor Russell) and `2606.16969v1` (Gichamba and Busogi).

Two identifiers were held twice at different revisions. Shi is cited at `2603.10371v2`
and Guo at `2502.06490v4`, in both cases the copy in the Aug 6 working folder rather than
the older one sitting in a side folder.

Sun's "6 to 14 per cent" figure, flagged in an earlier audit as not appearing in the
abstract and needing checking against the body, is in the body: "representing a 6-14%
performance drop compared to continuous features". The surrounding characterisation in
[2.3] is also correct, including that the loss is largely recoverable.
