# Rewrite backlog

Everything proposed and not yet written into the draft. Kept here rather than in
conversation because it accumulated across many sessions and was becoming untrackable.

Nothing below is in `Dissert Draft 7.docx` yet. The measurements behind items A and B are
all run and saved; what is outstanding is the prose.

Draft stands at 10,297 words of prose excluding the abstract. Items A and B add roughly
400, so expect about 10,700 before any compensating trim.

---

## A. From the extended cue-retention run, `src/48`, `results/cue_retention_repeated.txt`

Sylber, DyCAST and Whisper were added to the cue analysis. Whisper is a control that was
missing; the two variable-rate systems had been tested for decodability but never asked
which cues they keep.

| # | where | what | why |
|---|---|---|---|
| A1 | 3.5 | a real rationale for including Sylber and DyCAST | every other model gets a sentence saying what it rules in or out; these two get a cross-reference to [4.6]. They are the test of the field's alternative mechanism and should be introduced as such |
| A2 | 4.4 | state Whisper as a control | Whisper sits at 100 to 116 per cent on every group including temporal, so the codecs' surplus is a codec property rather than a WavLM deficiency. Without this row the claim in [5.2] is open to the objection that WavLM is simply poor at cue recovery |
| A3 | 4.4 and 4.6 | move the Sylber and DyCAST cue rows out of the controls section into the main line | they are no longer only a negative result. DyCAST retains 44 per cent of temporal, the least of anything measured, which is positive evidence for the temporal account. The decodability result stays in 4.6 |
| A4 | 5.3 | stop resting the variable-rate argument on decodability alone | it can now say why those systems do not recover the loss |
| A5 | 4.5 | the rank correlation between temporal retention and the order effect is +0.82 across all ten systems, against +0.83 across the three codecs | generalises the claim beyond the three-codec comparison |

## B. From the cue-group recomputation, `src/52`, `results/cue_groups_repeated.txt`

Stance is carried by contour dynamics, +0.083 from 12 features, and barely at all by coarse
rate, +0.024 from 6. Arousal ranks the groups differently, voice quality highest at +0.107.

| # | where | what | why |
|---|---|---|---|
| B1 | 1.1 | roughly 100 words establishing that the delivery cues carrying stance are dynamic ones | RQ4 currently arrives with no prior setup. The only mention of time before it is "sequential placement", one item in a list attributed to Gardner. When [4.4] answers "temporal", the reader has nothing to connect it to |
| B2 | 2.4 | mark which of the five correlates are temporal | "slower tempo" and "reduced F0 range" are dynamic properties sitting unflagged in a list of five |
| B3 | 4.2, or a short subsection before it | the cue-group table | establishes what stance is made of before asking what the codecs do to it. Turns the [4.4] finding from a surprise into a confirmed prediction |
| B4 | 4.6 and 5.2 | make the two senses of "temporal" explicit | "timing features alone sit at chance" and "what is lost is temporal organisation" look contradictory. Contour +0.083 against coarse rate +0.024 shows they are different quantities. 5.3 makes this point late and only negatively |
| B5 | 3.3 | a third defence of the arousal separation | voice quality carries arousal at +0.107 and stance at +0.047; contour is the reverse. This is annotator-independent evidence that the two axes are different things, which neither the design argument in 3.3 nor the probe result in 4.6 provides |

## C. Citations, from checking the sources against the new result

| # | where | what |
|---|---|---|
| C1 | 1.1 or 2.4 | Gravano et al. (2012) report contextual information and **final intonation** as the most salient cues to disambiguating *okay* for human listeners. Already cited, but only for the fact that these words are ambiguous, never for which cue resolves it. Direct independent support for the contour finding, on the same word class |
| C2 | 2.4 | Rockwell (2000) leads her cue list with slower tempo, a rate property, where this corpus finds coarse rate carries the least stance. Name the tension |
| C3 | 3.6 or 2.4 | Qian et al. (2025b) emphasise duration: voiced length scores 60.49 and 56.35 per cent against 44.44 and 41.88 for Legendre contours alone. The existing characterisation in 3.6 is accurate, but citing them as support for a contour account would overreach. Their finding is that duration carries meaning |

## D. Figures, built and on disk, not yet in the document

`src/51_build_figures.py`, output in `docs/figures/`. All three read their numbers from
`results/` so they cannot drift from the chapters.

| # | what | status |
|---|---|---|
| D1 | Figure 3.1, the method: two probe points on one forward pass, and why the naive pairing is not comparable | built, not reviewed |
| D2 | Figure 4.1, the ladder: encoder step against quantiser step, three codecs | built, not reviewed |
| D3 | Figure 4.2, cue retention as a heat map, eleven rows | built and approved |
| D4 | insert all three into the .docx | not started |
| D5 | Table 4.5 moves to Appendix B, since the heat map carries all its numbers | not started. Renumbers 4.6 to 4.8 as 4.5 to 4.7, and every reference to them |

## E. Carried over, unresolved

| # | what |
|---|---|
| E1 | A consolidated `src/53_check_draft.py` running every invariant this project has checked ad hoc: table arithmetic, margins against their own columns, every figure traced to a saved results file, cross-references, punctuation, naming consistency, subject-verb agreement after renames, appendix resolution. Offered and not yet taken up. Most defects found in later passes were introduced by earlier passes, and a single checker is what stops that |
| E2 | Open the appendices document in Word and check the page breaks by eye. Only verified programmatically |
| E3 | Five sources still without a PDF is now zero, but three details in the bibliography remain marked as needing a published-version check. See `docs/citation_audit_draft6.md` |
