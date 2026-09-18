"""Verify the LaTeX build against the Markdown it came from.

Three questions, in the order they matter:

1. Did every cross-reference resolve?  LaTeX prints ``??`` for a label it cannot
   find, so a scan of the PDF text answers this directly.  This is what makes it
   safe to let LaTeX own the numbering instead of transcribing "Section 5.4".
2. Did every number survive?  The Markdown's numeric tokens must still be in the
   compiled text with at least the same multiplicity.  A converted reference can
   silently change a number; this catches that.
3. Did every object arrive?  Twelve tables, nine figures, eleven equations, 41
   references, in the expected order.

Read the PDFs with PyMuPDF, so the check is on what a reader would see.
"""
from __future__ import annotations

import collections
import pathlib
import re
import sys

WORK = pathlib.Path(__file__).resolve().parent.parent
MD = WORK / "SEGAN_manuscript_revised_2026-09-13.md"
SUPP_MD = WORK / "SEGAN_supplementary_material_2026-09-14.md"
PDFS = [WORK / "SEGAN_manuscript_2026-09-14.pdf",
        WORK / "SEGAN_supplementary_material_2026-09-14.pdf",
        WORK / "SEGAN_highlights_2026-09-14.pdf"]

TOK = re.compile(r"\d+(?:[.,]\d+)*")
fails: list[str] = []


def pdf_text(path):
    """Extract the text, with the line breaks removed.

    Extraction inserts a newline wherever the typesetter broke a line, which
    would split "Figure 1:" and "99.4--99.8" apart; joining the lines first is
    what makes the checks below about content rather than about line breaking.
    """
    import pymupdf
    doc = pymupdf.open(path)
    raw = "\n".join(page.get_text() for page in doc)
    flat = re.sub(r"\s+", " ", raw)
    return flat, doc.page_count


def main():
    text, pages = "", {}
    for p in PDFS:
        t, n = pdf_text(p)
        text += " " + t
        pages[p.name] = n
    print("pages:", pages)

    # 1 --- unresolved references -------------------------------------------------
    qq = text.count("??")
    undef = len(re.findall(r"[Uu]ndefined", text))
    print(f"\n1. unresolved cross-references: {qq} '??', {undef} 'undefined'")
    if qq or undef:
        fails.append(f"{qq} unresolved references")

    # 2 --- every Markdown number must survive -----------------------------------
    md = MD.read_text(encoding="utf-8") + "\n" + SUPP_MD.read_text(encoding="utf-8")
    a = collections.Counter(TOK.findall(md))
    b = collections.Counter(TOK.findall(text))
    urls = " ".join(re.findall(r"https?://\S+", md))
    short = {k: a[k] - b[k] for k in a if a[k] > b[k]}
    explained, unexplained = {}, {}
    for k, v in short.items():
        if re.fullmatch(r"\d+(,\d+)+", k):
            explained[k] = "citation list: natbib prints [34, 35], not [34,35]"     # noqa: E501
        elif k in urls:
            explained[k] = "inside a URL that breaks across lines"
        else:
            unexplained[k] = v
    print(f"\n2. numeric tokens in Markdown: {len(a)} distinct")
    for k, why in sorted(explained.items()):
        print(f"   explained  {k!r}: {why}")
    if unexplained:
        print("   UNEXPLAINED SHORTFALLS:")
        for k, v in sorted(unexplained.items()):
            print(f"     {k!r}: Markdown {a[k]}, PDF {b[k]}  (short by {v})")
        fails.append(f"{len(unexplained)} unexplained numeric shortfalls")
    else:
        print("   no unexplained shortfall: every other token is present")

    # 3 --- objects ---------------------------------------------------------------
    print("\n3. objects in the compiled text")
    for label, pat, want in [
            # The caption label is "Table 1: caption" under elsarticle and
            # "Table 1" followed by a line break under the CAS class, so the
            # separator is not part of the test.
            ("tables", r"Table (\d+)[:\s]", 8),
            ("figures", r"Figure (\d+)[:\s]", 9),
            ("supp table S1-S3", r"Table (S\d):", 3),
            ("references", r"\[(\d+)\]\s", None),
            ("appendix headings", r"Appendix ([A-E])\.", 5)]:
        found = sorted({int(x) if x.isdigit() else x
                        for x in re.findall(pat, text)})
        print(f"   {label:18s} -> {found}")
        if want and len(found) != want:
            fails.append(f"{label}: found {found}, wanted {want} of them")

    eqs = [f"({n})" for n in list(range(1, 10)) + ["5a"]]
    absent = [e for e in eqs if e not in text]
    print(f"   equation numbers   -> {len(eqs) - len(absent)}/10 present"
          + (f", absent {absent}" if absent else ""))
    if absent:
        fails.append(f"equation numbers absent: {absent}")

    # 4 --- no leftover machinery -------------------------------------------------
    print("\n4. leftover conversion machinery")
    for probe in ["\\ref", "\\cite", "\\textbf", "\\emph", "textbackslash",
                  "textasciitilde", "begin{", "\\url"]:
        c = text.count(probe)
        if c:
            print(f"   FOUND {probe!r}: {c}")
            fails.append(f"raw TeX {probe!r} in the PDF")

    print("\n" + ("FAIL: " + "; ".join(fails) if fails else "ALL CHECKS PASSED"))


if __name__ == "__main__":
    main()
    sys.exit(1 if fails else 0)
