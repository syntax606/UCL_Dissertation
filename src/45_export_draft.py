#!/usr/bin/env python3
"""Export the Word draft to the markdown chapter files in docs/drafts/.

The Word document is authoritative. Several rounds of correction went into it and
not into the markdown, so the two had diverged. Rather than merge by hand, the
markdown is now generated from the docx, which makes the repo a checkable mirror
rather than a second source that can drift.

Run this after editing the draft. `git diff` then shows exactly what changed between
exports, which is what the markdown is for.

Usage:  python3 src/45_export_draft.py
        python3 src/45_export_draft.py --docx "/path/to/other.docx"
"""
import argparse, os, re
from pathlib import Path

import docx
from docx.table import Table
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "drafts"
DEFAULT = os.path.expanduser(
    "~/Library/Mobile Documents/com~apple~CloudDocs/UCL Compling/Dissertation/Aug 6/Dissert Draft 7.docx")

FILES = {  # chapter heading -> output file
    "Abstract": "00_abstract.md",
    "Chapter 1": "01_introduction.md",
    "Chapter 2": "02_literature_review.md",
    "Chapter 3": "03_methods.md",
    "Chapter 4": "04_results.md",
    "Chapter 5": "05_discussion.md",
    "Chapter 6": "06_conclusion.md",
}


def blocks(doc):
    """Walk the document body in order, yielding paragraphs and tables."""
    body = doc.element.body
    for child in body.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, doc)
        elif child.tag.endswith("}tbl"):
            yield Table(child, doc)


def clean(s):
    return re.sub(r"[ \t]+", " ", s.replace("\xa0", " ")).strip()


def table_md(t):
    rows = [[clean(c.text) for c in r.cells] for r in t.rows]
    if not rows:
        return ""
    w = len(rows[0])
    out = ["| " + " | ".join(rows[0]) + " |",
           "|" + "|".join("---" for _ in range(w)) + "|"]
    for r in rows[1:]:
        out.append("| " + " | ".join(r[:w] + [""] * (w - len(r))) + " |")
    return "\n".join(out)


def is_heading(txt):
    """Chapter title, or a numbered section like 3.7 or 6.1."""
    return bool(re.match(r"^(Abstract|Chapter \d+:|\d+\.\d+ )", txt))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docx", default=DEFAULT)
    args = ap.parse_args()

    doc = docx.Document(args.docx)
    current, buf, written = None, [], {}

    def flush():
        if current and buf:
            written[current] = "\n\n".join(x for x in buf if x.strip())

    for b in blocks(doc):
        if isinstance(b, Table):
            buf.append(table_md(b))
            continue
        txt = clean(b.text)
        if not txt:
            continue
        key = next((k for k in FILES if txt.startswith(k)), None)
        if key:
            flush()
            current, buf = key, [f"# {txt}"]
            continue
        if is_heading(txt):
            buf.append(f"## {txt}")
        else:
            buf.append(txt)
    flush()

    OUT.mkdir(parents=True, exist_ok=True)
    print(f"exporting {os.path.basename(args.docx)}\n" + "-" * 58)
    total = 0
    for key, fn in FILES.items():
        body = written.get(key)
        if body is None:
            print(f"  ** missing ** {key}")
            continue
        banner = ("<!-- GENERATED from the Word draft by src/45_export_draft.py.\n"
                  "     The .docx is authoritative. Edits made here will be overwritten. -->\n\n")
        p = OUT / fn
        p.write_text(banner + body.rstrip() + "\n")
        n = len(body.split())
        total += n
        print(f"  {fn:26} {n:>6} words")
    print("-" * 58)
    print(f"  {'total':26} {total:>6} words")
    print("\n  the .docx is authoritative; these files are generated, do not edit them")


if __name__ == "__main__":
    main()
