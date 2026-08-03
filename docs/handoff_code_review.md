# Handoff: code review of this repository

Written for a fresh Claude Code session picking this up. Everything below was verified
against the repository's own data; nothing here is inferred from memory of a previous
conversation.

**Branch:** `claude/ucl-dissertation-review-frq9wm` (4 commits, pushed).
**Base:** the branch point is the last commit before `141f49c`.
**Nothing is merged.** No pull request has been opened.

---

## 1. What this project is

A diagnostic probing study. The same short word ("yeah") carries different pragmatic
force depending on delivery — sincere agreement vs. sarcasm. The question is whether
modern speech representations preserve that contrast, and in particular whether it
survives **discrete tokenization** (Mimi, the tokenizer deployed speech-to-speech
systems consume).

The design's core move is **lexical control**: hold the word constant, vary only the
delivery. That separates loss of meaning from loss of sound.

Pipeline: `src/00`–`src/05` index a podcast corpus and cut clips; `src/07`–`src/13b`
annotate them; `src/14`–`src/16` run a human premise check; `src/17` extracts features
(GPU); `src/18` runs the probes.

---

## 2. Verified facts — do not re-derive these

All confirmed against `labels/labels.csv` and `results/probe_results.txt`.

| Fact | Value |
|---|---|
| Labelled clips | 873 (of 3,342 rows; 917 discarded, 1,552 unreviewed) |
| Stance distribution | affiliative 364, **neutral 147**, adversarial 362 |
| Episodes / shows | 753 / 32 |
| Arousal | low 528, high 345 (high-arousal neutral is only 26) |
| Episode clustering | 654 of 753 episodes contribute exactly 1 clip |
| Clip provenance | 240 from the `04`/`05`/`09` path, 633 from targeted pulls `10`–`12` |
| Duplicate ids | **none** — the `src/10` idempotency bug never fired |
| CPS cells | 15 cells, 191 leave-one-out decisions |
| **CPS correct baseline** | **0.670** (within-cell majority over the same 191 decisions) |
| CPS scores | wavlm .618, whisper .618, hubert .613, text .592, mimi .560 — **all below 0.670** |
| CPS cells by threshold | 42 at min 2, **15 at min 3 (current)**, 8 at min 4, 5 at min 5 |
| Cells one clip short | **27** sit at exactly 2 |
| `text:targetonly` | 0.487 macro-F1 vs a 0.313 permutation null — word identity alone |
| Layer-selection inflation | winner beats runner-up by 0.018 (wavlm), 0.010 (hubert), 0.003 (whisper) |
| Top-3 layer means | 0.561 / 0.510 / 0.561 |
| Phrase fold | 168 clips, exactly 2 rules, verified 0 mismatches |
| Balanced subsample | 630 of 873 clips |
| Mimi shape | all 8 codebooks, `(n, 16384)` — the README previously said 1–7 / 14336 |

---

## 3. What was changed, and why

Files touched: `.gitignore`, `DATA_AVAILABILITY.md`, `README.md`, `docs/limitations.md`,
`results/probe_results.txt`, `src/18_probe.py`, plus two new files
`src/13b_fold_target_phrases.py` and `tests/make_synthetic_features.py`.

**`src/00`–`src/17` were not modified.** See §5 for the known bugs still in them.

### Commit 1 (`141f49c`) — documentation and reporting corrections

Claims that were contradicted by the code or the shipped data.

- **CPS baseline.** View F was reported against a stated chance of 0.50. Cell eligibility
  requires only 3 exemplars of the minority stance, so eligible cells are class-imbalanced
  and the correct reference is the within-cell majority rate, 0.670. Every representation
  falls below it — view F is a **null result**, not a weak corroboration. This reverses a
  conclusion, so it is the most important single finding.
- **Layer selection** disclosed as non-nested and optimistically biased, with magnitude.
- **Permutation null** was not episode-clustered although the bootstrap was.
- **View E** groups by *show*, not speaker — guests recur across shows. Renamed.
- **Lexical confound** on view A documented, with the 0.487 target-only figure.
- **README/code mismatches:** Mimi all-8 not 1–7; eight views not six (G and H were
  undocumented); paths are hardcoded in `src/00`–`src/04` and `src/09`–`src/13` despite the
  README claiming otherwise; stance is balanced between the two poles only; the
  `--limit`/`--overwrite` smoke-test trap; `--perm 0` not suppressing view H.
- **`DATA_AVAILABILITY.md`** promised reproduction from shipped `features/` + `labels.csv`.
  Neither works: `features/` is gitignored and absent, and `src/18` reads `manifest.csv`.
  Corrected with the working procedure.
- `results/probe_results.txt` got an **errata header** rather than being edited, since it is
  generated output.

### Commit 2 (`980e9d2`) — `src/13b_fold_target_phrases.py` (new)

The step reconciling targeted-pull phrase labels with the eight base phrases used in
view C was done by hand and never committed, making the per-phrase cells irreproducible.

Reconstructed from clip provenance. Only **two rules** fire:

| pull-time value | folds to | source | clips |
|---|---|---|---|
| `oh_<base>` | `<base>` | `src/10` | 143 |
| `yeah_right` | `right` | `src/11` | 25 |

`src/12` sets `target_phrase = --label` at pull time, so its clips need no folding —
confirmed because each `idprefix` maps to exactly one base phrase regardless of the source
row's phrase.

`--verify labels/labels.csv` reconstructs each clip's pre-fold phrase from its
`candidate_id` and checks the rules reproduce the shipped labels: **873 clips, 168 folded,
0 mismatches.** Counts also reconcile with published view C once its top-2-stance filter is
applied (okay 128 − 12 affiliative = 116, right 129 − 22 = 107, etc.).

Also writes `target_phrase_raw`, preserving the pull-time value so the lexical-variant
question is measurable.

**Note for the write-up:** all 25 "yeah right" clips fold to **right**, not yeah, despite
every one being pulled from a `yeah`-suffixed row. Defensible, but previously invisible and
worth a sentence in the methods chapter.

### Commit 3 (`b756463`) — probing procedure fixes in `src/18_probe.py`

These change how numbers are produced. `results/probe_results.txt` is now stale.

- **Nested layer selection** is the default. The layer is chosen by inner CV on each outer
  fold's training data only. Per-fold choices are printed. `--layer-selection best` restores
  the legacy behaviour.
- **Permutation preserves episode clustering** — whole episodes' label blocks are exchanged
  between equal-size episodes, matching the bootstrap.
- **Views C/D/E/F report permutation nulls** instead of only the majority score that section
  A itself argues understates chance.
- **View F** adds a within-cell permutation null alongside the `cell-maj` baseline.
- **`--perm 0`** now disables every permutation test, view H included (was `args.perm or 100`).
- **Mimi's codebook size** is read from the features' `meta` array, not assumed to be 2048.
- **Per-analysis seeded RNGs**, using md5 not `hash()` (Python randomises string hashing per
  process). `--models wavlm` now gives identical wavlm figures to `--models wavlm text`.
- **View C2** (new) re-runs the within-word contrast on bare tokens only, excluding folded
  variants.
- `tests/make_synthetic_features.py` (new) writes a fake `features/` matching `src/17`'s
  output contract, so the analysis can be smoke-tested without a GPU.

### Commit 4 (`9e1bdc8`) — view A2, phrase-balanced subsample

Equalises the two commonest stances within each phrase and re-runs the pooled analysis on
the resulting **630 clips**, so base rates carry no stance information. Removes the lexical
confound from the pooled figure at zero annotation cost.

**Important caveat, stated in the code and README:** balancing does **not** reduce a
word-identity probe to chance. Knowing the phrase still narrows three stances to two
(`come_on` is never neutral). So `text:targetonly` on this subsample is the *empirical*
baseline to beat, not a guaranteed floor. Do not write "at chance by construction".

`--no-balanced` skips it.

README also gained a **Dataset balance** section recording which imbalances were addressed
and which were deliberately left alone.

---

## 4. Verification performed

`features/` does not exist on the author's machine, so no real numbers could be produced.
Instead `tests/make_synthetic_features.py` builds a fake `features/` with the same contract
`src/17` writes, and the full analysis was run against it. Confirmed:

- All ten sections run end to end.
- `--perm 0` blanks every permutation column, view H included.
- Mimi's `K` is read from `meta` (found 8 codebooks in a `K=32` synthetic matrix).
- `--models wavlm` and `--models wavlm text` produce byte-identical wavlm rows.
- View A2 selects exactly the predicted 630 clips.
- `src/13b --verify` reproduces `labels/labels.csv` with 0 mismatches.
- `py_compile` and `pyflakes` clean on all changed files.

**Scores produced from synthetic features are meaningless.** Never cite them.

---

## 5. Known bugs NOT fixed

All documented in the README, none patched. They live in Phase 0–1 scripts that could not
be tested without the corpus.

| Script | Bug | Severity |
|---|---|---|
| `05` | Never creates its clip output directories — ffmpeg fails on every clip on a clean checkout. One line. | blocks a fresh run |
| `02` vs `05` | `02` matches `okay|ok`, `05` only locates `"okay"`, so "ok" candidates are silently dropped | coverage gap |
| `05` | `come_on` centres on the first bare `"come"` in the segment, which may be the wrong token | affects ≤36 clips |
| `10` | Dedups on the base id but emits `oh_`-prefixed ids, so re-running appends duplicates. `11` does this correctly | latent; has not fired |
| `08` | Superseded by `13` but still present and still writes the same output file | footgun |
| `08`/`13` | `label = "literal_affiliative" if literal else "nonliteral"` conflates literalness with stance. Nothing reads it | cosmetic |
| `config.py` | Does not strip quotes from YAML values; treats `#` as a comment anywhere | documented workaround |
| `01` | References loop variable `n` after the loop — `NameError` on an empty file list | edge case |
| `14` | `--bitrate` is threaded through but never used; embeds raw WAV, ~8× larger files | cosmetic |
| `07` | `localStorage` key is batch-id based, so two sheets built with the same batch numbering share state | latent |
| `07` | Clips whose `audio_path` is empty are still included, producing silent cards | latent |
| all Phase 0–1 | Hardcoded `~/Desktop/pragmatic_contrast` working directory | documented limitation |

---

## 6. What to do next, in order

### Step 1 — smoke test locally (free, do this first)

```bash
python3 tests/make_synthetic_features.py
cp labels/labels.csv manifest.csv
python3 src/18_probe.py --perm 20 --perm-secondary 10
rm -rf features manifest.csv
```

Catches any environment problem while it costs nothing.

### Step 2 — regenerate features (GPU, ~10 min on an A100)

```bash
pip install torch transformers soundfile librosa sentence-transformers "numpy<2"
python3 src/17_extract_features.py --limit 5      # smoke test
python3 src/17_extract_features.py --overwrite    # --overwrite is REQUIRED after --limit
```

Requires `data/clips/` and therefore the audio.

### Step 3 — regenerate results

```bash
cp labels/labels.csv manifest.csv     # or point MANIFEST at the labeled sheet
python3 src/18_probe.py > results/probe_results.txt
```

This replaces the errata-headed file. Expect these differences from the published run:

- Audio scores in view A slightly **lower** (nested selection removes the optimistic bias).
- View C now shows a permutation chance near **0.50** for the binary contrasts, not the
  0.335–0.417 majority figures. This **widens** the audio models' margins and is likely to
  put **mimi at or below chance** within-word — a *stronger* result for the tokenizer-collapse
  claim, but confirm rather than assume it.
- View F gains `cell-maj` (0.670) and a permutation null. Expect it to read as a clean null.
- New views A2 and C2.

### Step 4 — update the thesis text

Three places where the numbers or framing change:

1. **View F is a null result.** `docs/limitations.md` has the corrected wording.
2. **View C's baseline** was wrong; mimi's within-word standing likely changes.
3. **Do not write "target-only is at chance by construction"** pooled across phrases — it
   is only true within a phrase. `03_methods.md` already gets this right; keep it that way.

---

## 7. Open decisions for the author

**a. Mimi feature representation (recommended, not implemented).**
`src/17` summarises Mimi as a per-codebook unigram histogram — a tally of token counts with
order discarded. Two concerns:

- Order loss is real but *symmetric*: WavLM/HuBERT/Whisper are mean+std pooled, which is also
  order-free. So this is a limitation of the whole design, not an unfairness to Mimi.
- **Sparsity is the bigger problem and is asymmetric.** Mimi runs at ~12.5 Hz, so a 10 s W2
  clip yields ~125 frames spread across 2,048 bins per codebook. Over 90% of bins are empty.
  WavLM gets ~500 frames of continuous vectors averaged into something stable. Supporting
  evidence from the repo's own view H: codebook 0 alone (0.402) **beats** all 8 together
  (0.381) — extra codebooks are adding noise, the signature of under-sampling.

  *Verify the frame count from an actual Mimi `.npz` before relying on this arithmetic.*

**Proposed fix:** look up each token's codebook embedding vector and mean+std pool those,
exactly as WavLM is handled. Then the only difference between Mimi and WavLM is quantization
— which is precisely what the study wants to isolate. Cheap: a change to `src/17` plus a GPU
re-run. Keep the histogram alongside as a robustness pair.

**b. View F top-up (optional).** 27 cells sit one clip short of eligibility; ~27 targeted
clips would take view F from 15 to 42 cells. `src/12 --shows` can pull by exact show and
pattern; at the observed ~50% keep rate that means labelling 60–80 candidates. Weigh against:
every representation is currently *below* the majority baseline, so more power most likely
sharpens a null rather than reversing it. `docs/limitations.md` scopes this as future work.

**c. Exact nested permutation.** `--perm-nested` exists but costs ~100× (hours per model).
The plateau evidence suggests it is not worth it; the current disclosure is honest.

**d. Phase 0–1 bug fixes.** The §5 table. None are needed to finish the analysis; they matter
for anyone reproducing from raw audio.

---

## 8. Things not to do

- **Do not cite any number produced from `tests/make_synthetic_features.py`.**
- **Do not hand-edit `results/probe_results.txt`** — regenerate it.
- **Do not commit `manifest.csv`** — it is gitignored; it is a copy of `labels/labels.csv`.
- **Do not run `src/08_merge_offline_annotations.py`** — superseded by `src/13`; it would
  overwrite the store-derived labeled sheet with an export-derived one.
- **Do not re-run `src/10_build_oh_topup.py`** without fixing its dedup check first — it
  would append duplicate `oh_*` rows.
- **Do not run `src/17` without `--overwrite`** after a `--limit` smoke test.
- **No re-annotation is required.** Every issue found is a documentation or analysis fix.
  The 873 labels and `annotations.db` are sound.
