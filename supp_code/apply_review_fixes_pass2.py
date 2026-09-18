"""Second pass: fix the table ordering introduced by the new Section 3 table, and clear
the residual regime/attribution wording that the first pass did not reach.

The first pass inserted the Section 3 coverage table as "Table 4" while leaving the old
Tables 2 and 3 in place, which put the tables out of order of first mention.  The fix is a
three-cycle: old 2 -> 3, old 3 -> 4, the new Section 3 table -> 2.  Applied with
placeholders so that no number is visited twice.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MS = ROOT / "SEGAN_manuscript_revised_2026-09-13.md"

doc = MS.read_text(encoding="utf-8")
FAILURES: list[str] = []


def rep(old: str, new: str, note: str, count: int = 1) -> None:
    global doc
    n = doc.count(old)
    if n != count:
        FAILURES.append(f"[x{n}, want {count}] {note}")
        return
    doc = doc.replace(old, new)


# ---------------------------------------------------------------- table three-cycle
# sanity: the numbers must appear where the first pass left them, and nowhere else.
# "Table 2" is cited three times (§4.4, table caption, §5.1), "Table 3" twice (§5.3), and
# the new Section 3 table twice (its caption and the pointer from §8.1).
for probe, want in [("Table 2", 3), ("Table 3", 2), ("Table 4", 2)]:
    n = doc.count(probe)
    if n != want:
        FAILURES.append(f"[x{n}, want {want}] pre-cycle probe {probe}")

if not FAILURES:
    doc = doc.replace("Table 2", "@@T2@@")
    doc = doc.replace("Table 3", "@@T3@@")
    doc = doc.replace("Table 4", "Table 2")
    doc = doc.replace("@@T2@@", "Table 3")
    doc = doc.replace("@@T3@@", "Table 4")

# ---------------------------------------------------------------- regime wording
rep(
    "**Sensitivity to the cut-off.** The uncoupled protocol shows a positive gap in 11 of 12 "
    "conditions and a maximum of 16.611 at $K \\ge 7$ (240 instances), at $K \\ge 8$ (198) and "
    "at $K \\ge 9$ (174); the budgeted protocol shows 11 of 12 at $K \\ge 7$ and 8 of 12 at "
    "$K \\ge 8$ and $K \\ge 9$,",

    "**Sensitivity to the cut-off.** The uncoupled regime shows a positive gap in 11 of 12 "
    "conditions and a maximum of 16.611 at $K \\ge 7$ (240 instances), at $K \\ge 8$ (198) and "
    "at $K \\ge 9$ (174); the budgeted regime shows 11 of 12 at $K \\ge 7$ and 8 of 12 at "
    "$K \\ge 8$ and $K \\ge 9$,",
    "5.0 regimes in sensitivity",
)

rep(
    "which is why Tables 4 and 6 carry different sample rules.",
    "which is why Tables 5 and 7 carry different sample rules.",
    "5.0 table pair",
)

rep(
    "| Dynamic program vs. the frozen gap values, uncoupled protocol |",
    "| Dynamic program vs. the frozen gap values, uncoupled regime |",
    "Appendix B row label",
)

rep(
    "(a) Uncoupled protocol; (b) reconnection budget $B = 6$.",
    "(a) Uncoupled regime; (b) reconnection budget $B = 6$.",
    "Figure 3 caption",
)

# ---------------------------------------------------------------- Figure 4 caption
rep(
    "**Figure 4.** The instance-selection rule carries as much of the reported phenomenon as "
    "the systems and policies do.",

    "**Figure 4.** The instance-selection rule is not a neutral choice: changing it alone moved "
    "the reported incidence of the phenomenon from 7 of 12 conditions to 11 of 12.",
    "Figure 4 caption",
)

if FAILURES:
    print("ABORTED:")
    for f in FAILURES:
        print("   ", f)
    sys.exit(1)

MS.write_text(doc, encoding="utf-8")
print("second pass written")
for probe in ["uncoupled protocol", "budgeted protocol", "Uncoupled protocol",
              "carries as much of", "Tables 4 and 6"]:
    print(f"  residual {probe!r}: {doc.count(probe)}")
print("  Table order as they appear:", re.findall(r"\*\*Table (\d+)\.\*\*", doc))
