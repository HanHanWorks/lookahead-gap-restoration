"""Apply the SEGAN compression to the manuscript.

Reads the compressed section bodies from supp_code/compressed_sections/ and
splices them into the manuscript between fixed section anchors.  Every anchor
is asserted to be unique, so a mis-targeted splice aborts the run rather than
writing a corrupted file.  Reports the before/after word counts per section and
in total so the reduction is auditable rather than asserted.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MS = ROOT / "SEGAN_manuscript_revised_2026-09-13.md"
SEC = ROOT / "supp_code" / "compressed_sections"

doc = MS.read_text(encoding="utf-8")
before = len(doc.split())


def sec_words(text: str) -> int:
    return len(text.split())


def splice(doc: str, start: str, end: str, body: str) -> str:
    if doc.count(start) != 1:
        raise SystemExit(f"start anchor x{doc.count(start)}: {start!r}")
    if doc.count(end) != 1:
        raise SystemExit(f"end anchor x{doc.count(end)}: {end!r}")
    i = doc.index(start)
    j = doc.index(end, i)
    return doc[:i] + body + doc[j:]


PLAN = [
    ("## 1. Introduction",
     "## 3. An attribution framework for prioritization policies",
     "sec01_02.md"),
    ("## 3. An attribution framework for prioritization policies",
     "## 5. Numerical verification",
     "sec03_04.md"),
    ("## 5. Numerical verification",
     "## 6. The service-model regime of the criterion",
     "sec05.md"),
    ("## 6. The service-model regime of the criterion",
     "## 8. Discussion",
     "sec06_07.md"),
    ("## 8. Discussion",
     "## Appendix A. Protocol definition",
     "sec08_10.md"),
]

report = []
for start, end, fname in PLAN:
    body = (SEC / fname).read_text(encoding="utf-8")
    if not body.startswith(start):
        raise SystemExit(f"{fname} does not start with {start!r}")
    i = doc.index(start)
    j = doc.index(end, i)
    old = doc[i:j]
    report.append((fname, start.split("\n")[0], sec_words(old), sec_words(body)))
    doc = doc[:i] + body + doc[j:]

# --- drop the revision change record: a submitted manuscript does not narrate
#     its own drafts, and the note it points to is a private working document.
marker = "\n---\n\n## Change record for this revision\n"
if doc.count(marker) != 1:
    raise SystemExit(f"change-record marker x{doc.count(marker)}")
doc = doc[: doc.index(marker)].rstrip() + "\n"

# --- remove the last revision-history self-reference in the appendix
old = ("and the two are kept apart because an earlier draft labelled a table column "
       "after the wrong one.")
new = ("and the two are kept apart, since a reader re-deriving the attribution "
       "would otherwise conflate them.")
if doc.count(old) != 1:
    raise SystemExit(f"appendix self-reference x{doc.count(old)}")
doc = doc.replace(old, new)

MS.write_text(doc, encoding="utf-8")
after = len(doc.split())

print(f"{'file':<16} {'section':<44} {'before':>7} {'after':>7} {'cut':>7}")
for fname, head, b, a in report:
    print(f"{fname:<16} {head[:43]:<44} {b:>7} {a:>7} {b-a:>7}")

# per-section counts of the spliced result
body = doc.split("## 1. Introduction")[1].split("## Appendix A.")[0]
print("\n--- spliced result, section by section ---")
tot = 0
for part in re.split(r"\n## ", "## " + body):
    head = part.split("\n")[0][:52]
    n = sec_words(part)
    tot += n
    print(f"  {n:6d}  {head}")
print(f"  {tot:6d}  TOTAL sections 1-10 (incl. headings, tables)")

ab = re.sub(r"[*\\{}]", "", doc.split("## Abstract")[1].split("**Keywords")[0])
print(f"\nabstract: {len(ab.split())} words (limit 250)")
print(f"whole file: {before} -> {after} words ({after-before:+d})")
