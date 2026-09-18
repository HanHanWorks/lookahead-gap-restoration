"""Option A: relocate Appendices A--E from the manuscript into a separate
supplementary document, and leave the manuscript with a pointer section.

Nothing is deleted: the appendix text moves verbatim into
`SEGAN_supplementary_material_2026-09-14.md`, with the two tables they carry
renumbered Table S1 / Table S2 (they are no longer part of the article's own
table sequence, which now ends at Table 10).

Every replacement below is anchored on a string asserted to occur exactly once,
so that a stale anchor aborts the whole run instead of writing a half-edited
manuscript.  Two defects are repaired in passing:

  * a sentence of Appendix E that an earlier replacement split in two
    ("... argues from it. and the connection between ...", lowercase "and"),
    restored from the pre-fix snapshot `reviews/prev/SEGAN_manuscript_PRE_AUDITFIX_2026-09-14.md`;
  * the reference to "Table 11 of Appendix D" in the Table 4 caption, which
    moves with the table it points at.
"""
from __future__ import annotations

import pathlib
import re
import sys

WORK = pathlib.Path(__file__).resolve().parent.parent
MS = WORK / "SEGAN_manuscript_revised_2026-09-13.md"
SUPP_OUT = WORK / "SEGAN_supplementary_material_2026-09-14.md"

FAILURES: list[str] = []


def rep(doc: str, old: str, new: str, label: str, expect: int = 1) -> str:
    """Replace `old` with `new`, insisting it occurs exactly `expect` times."""
    n = doc.count(old)
    if n != expect:
        FAILURES.append(f"[x{n}, want {expect}] {label}")
        return doc
    return doc.replace(old, new)


# ---------------------------------------------------------------- read input
doc = MS.read_text(encoding="utf-8")

I_APP = doc.index("## Appendix A.")
I_FIGCAP = doc.index("---\n\n## Figure captions")
appendix_block = doc[I_APP:I_FIGCAP]
assert appendix_block.count("## Appendix ") == 5, appendix_block.count("## Appendix ")

if FAILURES:
    print("\n".join(FAILURES))
    sys.exit(1)

# ------------------------------------------------- the supplementary document
SUPP_HEADER = """# Supplementary material

> **Supplementary material for:** *How much lookahead is worth having? An exactly computable value-and-accessibility criterion for restoration prioritization*
> Prepared for SEGAN (Sustainable Energy, Grids and Networks).
>
> This document carries the five appendices cited in the main text as Appendices A--E, together
> with the two tables they contain, numbered here **Table S1** and **Table S2** because they are
> no longer part of the article's own table sequence. The appendix lettering is unchanged, so
> every cross-reference of the main text resolves directly. No numerical result of the main text
> rests on material that is only here: what these appendices add is how each number was produced,
> which released artifact carries it, and how the literature search was run.

## Contents

| Appendix | Subject |
|---|---|
| A | Protocol definition: the three places in which the two data-generation protocols differ |
| B | Dynamic-program validation record: the released artifact behind each check |
| C | Implementation and environment |
| D | Data and code availability, outstanding release items, and the quantity-to-column map (Table S1) |
| E | Literature search protocol and coverage (Table S2) |

---

"""

appendix_block_raw = appendix_block
appendix_block = rep(appendix_block, "Table 11", "Table S1", "supp: Table 11 -> Table S1")
appendix_block = rep(appendix_block, "Table 12", "Table S2", "supp: Table 12 -> Table S2 (prose + caption)", expect=2)
appendix_block = rep(
    appendix_block,
    "argues from it. and the connection",
    "argues from it; and the connection",
    "supp: repair the sentence split by the earlier fix pass",
)

if FAILURES:
    print("\n".join(FAILURES))
    sys.exit(1)

SUPP_OUT.write_text(SUPP_HEADER + appendix_block.rstrip() + "\n", encoding="utf-8")

# ------------------------------------------------------------- the manuscript
# 1. front matter: one global statement, before the abstract
doc = rep(
    doc,
    "> file of every figure.",
    "> file of every figure. Appendices A--E, and the two tables they contain, are carried in the\n"
    "> supplementary material; every cross-reference to an appendix in this article points into\n"
    "> that document.",
    "front matter: where the appendices live",
)

# 2. first mention of each appendix letter in the body
doc = rep(
    doc,
    "Appendix E records the search protocol",
    "Appendix E of the supplementary material records the search protocol",
    "S1.5: first mention of Appendix E",
)
doc = rep(
    doc,
    "Section 3.5 records this as a measurement boundary and Appendix D as a release requirement.",
    "Section 3.5 records this as a measurement boundary and Appendix D of the supplementary "
    "material as a release requirement.",
    "S3.2: first mention of Appendix D in the body",
)
doc = rep(
    doc,
    "and Appendix B names the artifact behind each record.",
    "and Appendix B of the supplementary material names the artifact behind each record.",
    "S4.3: first mention of Appendix B",
)
doc = rep(
    doc,
    "the library versions of Appendix C;",
    "the library versions of Appendix C of the supplementary material;",
    "S9: first mention of Appendix C",
)

# 3. the Table 4 caption points at the relocated supplementary table
doc = rep(
    doc,
    "mapped to its released column in Table 11 of Appendix D.",
    "mapped to its released column in Table S1 of the supplementary material.",
    "Table 4 caption: Table 11 -> Table S1",
)

# 4. the data availability statement, which Elsevier requires in the article itself
doc = rep(
    doc,
    "**Data availability.** The artifacts listed in Appendix D are provided as a co-submission "
    "with this article.",
    "**Data availability.** The artifacts listed in Appendix D of the supplementary material are "
    "provided as a co-submission with this article; that appendix states what is released and "
    "what remains outstanding.",
    "Declarations: data availability statement",
)

# 5. the appendix block gives way to a pointer section, ahead of the figure captions.
#    The body edits above sit entirely ahead of the block, so re-slice on the edited
#    text and check that the block itself came through untouched.
I_APP = doc.index("## Appendix A.")
I_FIGCAP = doc.index("---\n\n## Figure captions")
if doc[I_APP:I_FIGCAP] != appendix_block_raw:
    FAILURES.append("the appendix block changed while the body was being edited")
head, tail = doc[:I_APP].rstrip(), doc[I_FIGCAP:]

POINTER = """## Supplementary material

Supplementary material related to this article can be found, in the online version, at [DOI to be inserted on acceptance].

Five appendices are carried in that document and are cited from the text as Appendices A--E. **A** defines the two data-generation protocols and the three places in which they differ. **B** is the dynamic-program validation record: the released artifact behind each check, and the two checks that remain pending. **C** records the implementation and the environment. **D** is the data and code availability statement, the inventory of outstanding release items, and the map from every quantity of Section 3 to the column that records it (Table S1). **E** is the literature search protocol, the six directions in which no prior work was retrieved, and the timing claims of the surveyed works (Table S2).

"""

doc = head + "\n\n" + POINTER + tail

if FAILURES:
    print("\n".join(FAILURES))
    sys.exit(1)
MS.write_text(doc, encoding="utf-8")

# ------------------------------------------------------------------- summary
def words(s: str) -> int:
    return len(s.split())


sec = doc[doc.index("## 1. Introduction"):doc.index("## Figure captions")]
print(f"supplementary document : {words(SUPP_OUT.read_text(encoding='utf-8'))} words "
      f"(+ {len(re.findall(r'## Appendix ', appendix_block))} appendices, "
      f"{len(re.findall(r'[*][*]Table S[12][.]', appendix_block))} tables)")
print(f"manuscript             : {words(doc)} words total, "
      f"§1-§10 {words(sec)} words")
print(f"appendix block moved   : {words(appendix_block)} words")
print("all anchors matched exactly once")
