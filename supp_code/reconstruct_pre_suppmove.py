"""Reconstruct the pre-move manuscript (recovery point) from the two files the
move produced, and prove the reconstruction by round-tripping it back.

The move is a set of literal replacements, so its inverse is too.  The check at
the end is what matters: re-running `move_appendices_to_supplementary.py` on the
reconstruction must reproduce both output files byte for byte.  A snapshot that
cannot be round-tripped is not a snapshot.
"""
from __future__ import annotations

import hashlib
import pathlib
import shutil
import subprocess
import sys

WORK = pathlib.Path(__file__).resolve().parent.parent
MS = WORK / "SEGAN_manuscript_revised_2026-09-13.md"
SUPP = WORK / "SEGAN_supplementary_material_2026-09-14.md"
SNAP = WORK / "reviews" / "prev" / "SEGAN_manuscript_PRE_SUPPMOVE_2026-09-14.md"
DRIVER = WORK / "supp_code" / "move_appendices_to_supplementary.py"


def rep(doc: str, new: str, old: str, expect: int, label: str) -> str:  # new -> old
    n = doc.count(new)
    assert n == expect, f"[x{n}, want {expect}] {label}"
    return doc.replace(new, old)


# ---------------------------------------------------------------- the inverse
supp = SUPP.read_text(encoding="utf-8")
block = supp[supp.index("## Appendix A."):].rstrip() + "\n"
block = rep(block, "Table S1", "Table 11", 1, "S1 -> 11")
block = rep(block, "Table S2", "Table 12", 2, "S2 -> 12")
block = rep(block, "; and the connection", ". and the connection", 1, "repair the split sentence")

doc = MS.read_text(encoding="utf-8")
I_SUP = doc.index("## Supplementary material")
I_FIGCAP = doc.index("---\n\n## Figure captions")
doc = doc[:I_SUP] + block + doc[I_FIGCAP:]

doc = rep(doc, "> file of every figure. Appendices A--E, and the two tables they contain, are carried in the\n"
               "> supplementary material; every cross-reference to an appendix in this article points into\n"
               "> that document.", "> file of every figure.", 1, "front matter")
doc = rep(doc, "Appendix E of the supplementary material records", "Appendix E records", 1, "S1.5")
doc = rep(doc, "measurement boundary and Appendix D of the supplementary "
               "material as a release requirement.", "measurement boundary and Appendix D as a release requirement.", 1, "S3.2")
doc = rep(doc, "and Appendix B of the supplementary material names", "and Appendix B names", 1, "S4.3")
doc = rep(doc, "the library versions of Appendix C of the supplementary material;",
          "the library versions of Appendix C;", 1, "S9")
doc = rep(doc, "mapped to its released column in Table S1 of the supplementary material.",
          "mapped to its released column in Table 11 of Appendix D.", 1, "Table 4 caption")
doc = rep(doc, "**Data availability.** The artifacts listed in Appendix D of the supplementary material are "
               "provided as a co-submission with this article; that appendix states what is released and "
               "what remains outstanding.",
          "**Data availability.** The artifacts listed in Appendix D are provided as a co-submission "
          "with this article.", 1, "Declarations")

SNAP.write_text(doc, encoding="utf-8")
print(f"snapshot written: {SNAP.name}  ({len(doc.split())} words)")

# ------------------------------------------------------------- round-trip test
before = {MS: hashlib.sha256(MS.read_bytes()).hexdigest(),
          SUPP: hashlib.sha256(SUPP.read_bytes()).hexdigest()}
shutil.copy(MS, MS.with_suffix(".tmp_rt"))
shutil.copy(SUPP, SUPP.with_suffix(".tmp_rt"))
shutil.copy(SNAP, MS)                                   # feed the reconstruction back in
shutil.copy(SNAP, SUPP)                                 # (SUPP is overwritten by the driver)
r = subprocess.run([sys.executable, str(DRIVER)], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
after = {MS: hashlib.sha256(MS.read_bytes()).hexdigest(),
         SUPP: hashlib.sha256(SUPP.read_bytes()).hexdigest()}
print("round-trip manuscript  :", "identical" if before[MS] == after[MS] else "DIFFERENT")
print("round-trip supplementary:", "identical" if before[SUPP] == after[SUPP] else "DIFFERENT")
shutil.move(MS.with_suffix(".tmp_rt"), MS)
shutil.move(SUPP.with_suffix(".tmp_rt"), SUPP)
print("working tree restored to the moved state")
