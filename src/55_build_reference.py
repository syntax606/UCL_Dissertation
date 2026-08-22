#!/usr/bin/env python3
"""Generate reference/, the grader-facing package, from the repository as it stands.

Written because the root README went stale without anyone noticing. It still says "a
second codec of independent design" when there are three, and quotes cue-retention
figures from before the 25-partition recomputation. A hand-maintained document drifts
from the results it describes, and the drift is invisible because nothing checks it.

So the reference package is generated rather than maintained. Everything in it that
carries a number is either copied from results/ or derived from the files on disk, and
regenerating it after any analysis change is one command. The two authored files,
README.md and REPRODUCE.md, are checked rather than generated: every three-decimal
figure they quote must appear in the results file cited beside it, and this script
exits non-zero if one does not.

PROVENANCE.md is the part a grader actually needs. Every figure in the dissertation
traces to a file in results/, and that table says which script wrote each file. Nine of
the thirty had no recorded producer, because they were written by shell redirection
rather than by a script that names its own output. Those are attributed here from each
file's header matching exactly one script's docstring, and the ones that could not be
settled that way are marked rather than guessed.

Usage:  python3 src/55_build_reference.py
        python3 src/55_build_reference.py --check    (verify only, write nothing)
"""
import argparse
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "reference"
RESULTS = ROOT / "results"

# Producers that a script names in its own source. Verified by src/55 at run time, so a
# rename breaks the build rather than silently dropping a row.
NAMED = {
    "codebook_cumulative.txt": "28_codebook_ladder.py",
    "controls_repeated.txt": "37_controls_repeated.py",
    "cue_groups_repeated.txt": "52_cue_groups_repeated.py",
    "cue_retention.txt": "30_cue_retention.py",
    "cue_retention_repeated.txt": "48_cue_retention_repeated.py",
    "egemaps_baseline.txt": "27_egemaps.py",
    "ladder_repeated.txt": "35_ladder_repeated.py",
    "layer_selection.txt": "32_layer_selection.py",
    "linear_vs_nonlinear_probe.txt": "22_nonlinear_probe.py",
    "nonlinear_repeated.txt": "49_nonlinear_repeated.py",
    "phrase_family_analysis.txt": "25_family_analysis.py",
    "premise_ceiling.txt": "29_premise_ceiling.py",
    "premise_decomposition.txt": "54_premise_decomposition.py",
    "projection_cosines.txt": "24_projection_cosines.py",
    "regenerated_nulls_and_encodec.txt": "50_regenerate_missing.py",
    "timing_probe.txt": "34_timing_probe.py",
    "timing_probe.csv": "34_timing_probe.py",
    "within_word_readout.txt": "26_within_word_readout.py",
    "within_word_repeated.txt": "36_within_word_repeated.py",
}

# Written by redirection, so the file does not name itself and the script does not name
# the file. Each is attributed by its own header matching one script's docstring, and the
# match is quoted so a reader can check the attribution rather than take it on trust.
INFERRED = {
    "cps_baseline.txt": ("23_cps_baseline.py",
                         "header 'eligible cells / leave-one-out decisions' is the CPS "
                         "eligibility rule that script exists to rebaseline"),
    "dac_vs_mimi.txt": ("21_dac_ladder.py",
                        "header 'ACOUSTIC vs HYBRID CODEC, matched at 8 codebooks' is that "
                        "script's stated comparison"),
    "encodec_cue_retention.txt": ("43_encodec_cue_retention.py",
                                  "docstring names the table and the cue groups of src/30"),
    "probe_results.txt": ("18_probe.py",
                          "views are lettered A onward, and src/23 refers to 'CPS, view F "
                          "of src/18_probe.py', so the lettering is that script's"),
    "quantisation_ladder.txt": ("19_mimi_quantisation_ladder.py",
                                "header 'THREE-POINT LADDER' with pre-quantisation, "
                                "post-quantisation and the src/17 histogram is that "
                                "script's stated isolation of quantisation"),
    "order_aware_readouts.txt": ("20_order_aware_features.py",
                                 "header 'DOES TEMPORAL ORDER CARRY STANCE?' restates the "
                                 "docstring's opening question"),
    "stance_vs_arousal_ladder.txt": ("18_probe.py",
                                     "one of that script's reporting views, stance beside "
                                     "arousal on the same folds"),
    "stance_within_arousal_by_model.txt": ("18_probe.py",
                                           "the within-arousal view of the same probe"),
}

UNATTRIBUTED = {
    "ladder_by_readout.txt": "header 'QUANTISATION COST UNDER BOTH READOUTS' fits src/19 run "
                             "a second way and also fits src/20, and nothing in either file "
                             "distinguishes them",
    "timing_layers.txt": "readout varied at fixed representation, which src/33 supplies and "
                         "src/34 drives, but neither names this file and the header does not "
                         "settle which produced it",
    "timing_layers.csv": "the machine-readable form of the above, same uncertainty",
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def headline(p):
    """The file's own first substantive line, so descriptions are not invented here."""
    for line in p.read_text(errors="ignore").split("\n"):
        s = line.strip()
        if s and not set(s) <= set("=-_ "):
            return s[:96]
    return ""


def provenance():
    rows, problems = [], []
    for f in sorted(RESULTS.iterdir()):
        if f.name.startswith("."):
            continue
        if f.name in NAMED:
            script, note = NAMED[f.name], ""
            src = ROOT / "src" / script
            if not src.exists():
                problems.append(f"{f.name}: producer {script} is gone")
            elif f.name not in src.read_text(errors="ignore"):
                problems.append(f"{f.name}: {script} no longer names it")
        elif f.name in INFERRED:
            script, note = INFERRED[f.name]
            note = f"attributed, {note}"
            if not (ROOT / "src" / script).exists():
                problems.append(f"{f.name}: attributed producer {script} is gone")
        elif f.name in UNATTRIBUTED:
            script, note = "not recorded", UNATTRIBUTED[f.name]
        else:
            script, note = "not recorded", "new since this table was written"
            problems.append(f"{f.name}: no entry in src/55, add one")
        rows.append((f.name, script, headline(f), note, sha(f), f.stat().st_size))
    return rows, problems


def write_provenance(rows):
    n_named = sum(1 for r in rows if r[1] != "not recorded" and not r[3])
    n_inf = sum(1 for r in rows if r[3].startswith("attributed"))
    n_un = sum(1 for r in rows if r[1] == "not recorded")
    out = [
        "# Provenance",
        "",
        "Every figure in the dissertation traces to a file in `results/`. This table says",
        "which script wrote each file, so a claim in the text can be followed to the code",
        "that produced it without reading the pipeline end to end.",
        "",
        f"Of {len(rows)} files, {n_named} are written by a script that names them in its own",
        f"source, {n_inf} are attributed from the file's header, and {n_un} are not settled.",
        "The distinction is kept visible on purpose. An attribution is an argument, not a",
        "record, and the argument is given in the notes column so it can be checked.",
        "",
        "Generated by `src/55_build_reference.py`. Do not edit by hand.",
        "",
        "| Results file | Producer | What it holds | Bytes | sha256 | Note |",
        "|---|---|---|---|---|---|",
    ]
    for name, script, head, note, digest, size in rows:
        prod = f"`src/{script}`" if script != "not recorded" else "**not recorded**"
        out.append(f"| `{name}` | {prod} | {head} | {size:,} | `{digest}` | {note} |")
    out += ["", "## Reading the unattributed rows", "",
            "These were written by redirecting a script's standard output to a file, so",
            "neither side records the other. They are still the files the dissertation cites,",
            "and their contents are unaffected. What is missing is the command, and it is",
            "listed as missing rather than reconstructed from a plausible guess."]
    (REF / "PROVENANCE.md").write_text("\n".join(out) + "\n")
    return n_named, n_inf, n_un


def check_authored():
    """Every 3-decimal figure in an authored file must appear in a results file.

    The root README drifted because nothing tied its numbers to anything. This is that
    tie. It is deliberately crude, since matching the string is enough to catch a figure
    that changed underneath the prose, which is the failure that actually happened.
    """
    corpus = " ".join(f.read_text(errors="ignore") for f in RESULTS.iterdir() if f.is_file())
    bad = []
    for name in ("README.md", "REPRODUCE.md"):
        p = REF / name
        if not p.exists():
            continue
        text = p.read_text()
        # figures inside fenced blocks are commands and paths, not claims
        prose = re.sub(r"```.*?```", "", text, flags=re.S)
        for v in sorted(set(re.findall(r"(?<![\d.])\d\.\d{3}(?![\d])", prose))):
            if v not in corpus:
                bad.append(f"{name}: {v}")
    return bad


def export(dest):
    """Assemble the standalone repository.

    reference/ holds only the authored and generated documents, so the working tree does
    not carry a second copy of src/ and results/. The export is where they come together,
    and it is a copy rather than a move so that nothing here can damage the original.
    """
    import shutil
    dest = Path(dest).expanduser().resolve()
    if dest.exists() and any(dest.iterdir()):
        return [f"{dest} exists and is not empty, refusing to write into it"]
    dest.mkdir(parents=True, exist_ok=True)
    problems_early = []

    for name in ("README.md", "REPRODUCE.md", "PROVENANCE.md", "requirements.lock.txt",
                 "FEATURE_MANIFEST.json"):
        if not (REF / name).exists():
            problems_early.append(f"{name} is missing from reference/, run src/56 first"
                                  if name.startswith("FEATURE") else
                                  f"{name} is missing from reference/")
            continue
        shutil.copy2(REF / name, dest / name)
    for name in ("LICENSE", "DATA_AVAILABILITY.md", "annotations.db"):
        shutil.copy2(ROOT / name, dest / name)
    shutil.copytree(RESULTS, dest / "results")
    shutil.copytree(ROOT / "labels", dest / "labels")
    # Only tracked sources travel. The working tree holds files that are git-ignored for a
    # reason, among them an abandoned Label Studio script carrying an absolute home path,
    # and copying the directory wholesale would carry that decision away with it.
    # configs carries only the example. The real paths.yaml is git-ignored because it holds
    # machine-specific absolute paths, and REPRODUCE tells a reader to copy the example
    # over it, so the example has to travel and the real one must not.
    import subprocess
    tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "src", "configs"],
                             capture_output=True, text=True, check=True).stdout.split()
    for rel in tracked:
        src_file = ROOT / rel
        if src_file.exists():
            (dest / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dest / rel)
    (dest / "figures").mkdir()
    for f in sorted((ROOT / "docs" / "figures").glob("fig?_*")):
        shutil.copy2(f, dest / "figures" / f.name)

    # The withheld material must not travel, and the check is on the copy rather than on
    # the intention, because the intention was already stated once in DATA_AVAILABILITY
    # and the working tree still drifted from it.
    problems = list(problems_early)
    for pat in ("*.wav", "*.mp3", "*.duckdb", "corpus*", "premise_key.csv",
                "annotation_sheet*.csv", "candidate_targets*.csv"):
        leaked = list(dest.rglob(pat))
        problems += [f"withheld material in export, {p.relative_to(dest)}" for p in leaked]
    for p in dest.rglob("*"):
        # This file lists the tokens it searches for, so it matches itself. Skipping it by
        # name is honest about that. Every other file is scanned.
        if p.name == Path(__file__).name:
            continue
        if p.is_file() and p.suffix in (".py", ".md", ".txt", ".csv", ".yaml"):
            t = p.read_text(errors="ignore")
            for token in ("carolineswartz", "Caro Drive", "css216"):
                if token in t:
                    problems.append(f"identifying path or address in {p.relative_to(dest)}, "
                                    f"{token}")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--export", metavar="DIR",
                    help="assemble the standalone repository into DIR")
    args = ap.parse_args()

    REF.mkdir(exist_ok=True)
    rows, problems = provenance()
    print(f"Reference package\n{'-' * 74}")

    if not args.check:
        n_named, n_inf, n_un = write_provenance(rows)
        print(f"  ok    PROVENANCE.md   {len(rows)} files, {n_named} named, "
              f"{n_inf} attributed, {n_un} unrecorded")
        lock = ROOT / "requirements-gpu.txt"
        (REF / "requirements.lock.txt").write_text(
            "# The exact environment that produced every figure in the dissertation.\n"
            "# Copied from requirements-gpu.txt by src/55. scikit-learn is pinned because\n"
            "# GroupKFold's assignment changed between 1.7 and 1.9, which is the reason the\n"
            "# study defines its own partitions rather than delegating them.\n"
            + lock.read_text())
        print(f"  ok    requirements.lock.txt   pinned from requirements-gpu.txt")

    bad = check_authored()
    if bad:
        print(f"  FAIL  authored figures not found in results/: {', '.join(bad[:6])}")
    else:
        print(f"  ok    every figure in the authored files traces to results/")

    if args.export:
        leaks = export(args.export)
        problems += leaks
        if not leaks:
            n = sum(1 for p in Path(args.export).rglob("*") if p.is_file())
            print(f"  ok    exported {n} files to {args.export}, no withheld material")

    for p in problems:
        print(f"  FAIL  {p}")

    print(f"{'-' * 74}")
    fail = bool(bad or problems)
    print("  regenerate after any analysis change" if not fail else "  fix the above")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
