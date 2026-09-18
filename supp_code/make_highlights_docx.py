"""Write the Highlights file Elsevier asks for.

The guide is specific: "Highlights should be submitted in the following way:
unless otherwise instructed ... as a separate source file (i.e. Microsoft Word
not PDF).  Select 'Highlights' from the drop-down file list ... Use 'Highlights'
as the file name.  Include 3 to 5 highlights.  Each individual Highlight should
be a maximum of 85 characters long, including spaces."

So the file is named `Highlights.docx`, it is Word, and it holds nothing but the
bullets.  The text comes from the manuscript's Highlights section, which stays
the single source of truth; this script only changes the container.

  python supp_code/make_highlights_docx.py
"""
from __future__ import annotations

import pathlib
import re
import sys

WORK = pathlib.Path(__file__).resolve().parent.parent
MD = WORK / "SEGAN_manuscript_revised_2026-09-13.md"
OUT = WORK / "Highlights.docx"
PREVIEW = WORK / "highlights.md"

LIMIT = 85
MIN, MAX = 3, 5


def bullets() -> list[str]:
    md = MD.read_text(encoding="utf-8")
    block = md[md.index("## Highlights"):md.index("## 1. Introduction")]
    out = []
    for line in block.split("\n"):
        line = line.strip()
        if line.startswith("- "):
            text = line[2:].strip()
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)      # no markup in Word
            text = text.replace("\u2013", "-").replace("\u2014", "-")
            out.append(text)
    return out


def main() -> None:
    items = bullets()
    if not (MIN <= len(items) <= MAX):
        sys.exit(f"ABORT: {len(items)} highlights, the guide allows {MIN}-{MAX}")
    over = [(len(x), x) for x in items if len(x) > LIMIT]
    if over:
        for n, x in over:
            print(f"  {n:3d} chars: {x}")
        sys.exit(f"ABORT: {len(over)} highlight(s) over {LIMIT} characters")

    import docx

    doc = docx.Document()
    for x in items:
        doc.add_paragraph(x, style="List Bullet")
    doc.save(OUT)

    # keep the project's own plain-text copy in step with it
    PREVIEW.write_text("".join(f"- {x}\n" for x in items), encoding="utf-8")

    print(f"wrote {OUT.name} ({len(items)} bullets, longest {max(len(x) for x in items)} chars)")
    print(f"wrote {PREVIEW.name}")


if __name__ == "__main__":
    main()
