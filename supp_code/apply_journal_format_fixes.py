"""Bring the Markdown source into line with the SEGAN (Elsevier) formatting rules.

Everything here is a formatting or house-style change; no number, claim or
argument is touched.  The rules applied, and where they come from:

* **Language.** Elsevier asks for American *or* British usage but "not a mixture
  of these".  The manuscript mixed them: it wrote `-ization` 45 times against
  `-isation` 26, and `behaviour`/`favourable`/`neighbour` against `favors`/
  `favorite`.  Normalised to American, which is the dominant variety and the one
  the title, abstract and keywords already use.
* **Abstract.** "non-standard or uncommon abbreviations should be avoided, but
  if essential they must be defined at their first mention in the abstract
  itself".  `AUC@25` and the bare symbol `B` are both written out.
* **Abbreviations.** "Define abbreviations that are not standard in this field
  in a footnote to be placed on the first page of the article."  A compact list
  is added to the front matter; the LaTeX side typesets it as a title-page
  footnote.
* **Maths.** "use the solidus (/) instead of a horizontal line for small
  fractional terms": the one inline `\\tfrac{1}{2}` becomes `1/2`.  The display
  equations keep their `\\frac`/`\\tfrac`, which is correct for display maths.
* **Undefined abbreviations in the running text.** `ROP`/`CRP` were used once
  each and never expanded, and their expansions could not be confirmed from the
  cited works, so the sentence says what they mean instead of asserting one.
  `DP` in a Highlight is written out.

Run from the project root:  python supp_code/apply_journal_format_fixes.py
"""
from __future__ import annotations

import pathlib
import re
import shutil
import sys

WORK = pathlib.Path(__file__).resolve().parent.parent
MS = WORK / "SEGAN_manuscript_revised_2026-09-13.md"
SUPP = WORK / "SEGAN_supplementary_material_2026-09-14.md"
BAK = WORK / "reviews" / "prev"

FUZZ = 0.03          # absolute tolerance for a count assertion when fuzzing


class Doc:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.text = path.read_text(encoding="utf-8")
        self.changes: list[tuple[str, int]] = []

    def sub(self, old: str, new: str, expect: int | None = 1, label: str = "") -> None:
        n = self.text.count(old)
        if expect is not None and n != expect:
            sys.exit(f"ABORT [{self.path.name}] {label}: found {n}, expected {expect}")
        self.text = self.text.replace(old, new)
        if n:
            self.changes.append((label or old[:40], n))

    def regex(self, pat: str, repl: str, label: str) -> None:
        self.text, n = re.subn(pat, repl, self.text)
        self.changes.append((label, n))

    def save(self, suffix: str) -> None:
        shutil.copy(self.path, BAK / f"{self.path.stem}_{suffix}.md")
        self.path.write_text(self.text, encoding="utf-8")
        print(f"wrote {self.path.name}")
        for label, n in self.changes:
            if n:
                print(f"    {n:4d}  {label}")


# ---------------------------------------------------------------- spelling
US = [
    (r"utilisation", "utilization"), (r"realised", "realized"),
    (r"synthesised", "synthesized"), (r"generalisation", "generalization"),
    (r"standardised", "standardized"), (r"penalised", "penalized"),
    (r"optimisation", "optimization"), (r"summarised", "summarized"),
    (r"modelling", "modeling"), (r"behaviour", "behavior"),
    (r"favourable", "favorable"), (r"neighbour", "neighbor"),
    (r"programme", "program"),
]

# ---------------------------------------------------------------- abstract
ABSTRACT = (
    "Machine learning is increasingly proposed for restoration prioritization, yet "
    "reported gains are seldom attributed to the component producing them. First, an "
    "attribution framework writes any policy as a ranker composed with an admissibility "
    "screen, splitting its stepwise regret into ranking and censoring terms. Second, for "
    "maximum-flow service models the full-horizon optimum is computable by dynamic "
    "programming over broken-key-line subsets, defining the lookahead gap: an exact bound "
    "on what any policy reconnecting within the horizon can gain over a one-step exact "
    "rule, vanishing under step-wise degeneracy but not conversely. Third, a depth profile "
    "governs how cheaply it is collected: under a reconnection budget a committed plan "
    "needs five steps of foresight for the whole gap, whereas a rolling depth-2 controller "
    "collects 99.4--99.8% of it, needing three with a budget and four without. Fourth, a "
    "four-rule sweep shows the gap requires capacities proportional to base-case "
    "utilization, vanishing under uniform ratings. Fifth, the pre-check and the gap are "
    "complementary: the pre-check never rejects a condition carrying headroom, the gap "
    "flags conditions it passes. The gap is positive in 11 of 12 conditions per regime on "
    "the two IEEE systems, reaching a per-condition maximum of 120.1 units of the area "
    "under the restoration curve over 25 steps at a budget of six, and in six of six on a "
    "third system without a budget. Learned rankers nonetheless lose all 240 paired "
    "comparisons to a rolling depth-2 rule needing no training; latency claims should name "
    "the cheapest non-learned rule that could replace them."
)

ABBREVIATIONS = (
    "**Abbreviations.** AUC@25, area under the restoration curve over the first 25 decision "
    "steps; CI, confidence interval; DP, dynamic programming; LA, lookahead; MILP, "
    "mixed-integer linear program; PPO, proximal policy optimization; RL, reinforcement "
    "learning."
)


def main() -> None:
    BAK.mkdir(parents=True, exist_ok=True)
    ms, supp = Doc(MS), Doc(SUPP)

    # 1. spelling
    for uk, us in US:
        ms.regex(rf"\b{uk}\b", us, f"{uk} -> {us}")
        supp.regex(rf"\b{uk}\b", us, f"{uk} -> {us}")

    # 2. abstract: define the two non-standard tokens, and keep it under 250 words
    m = re.search(r"(## Abstract\n\n)(.*?)(\n\n\*\*Keywords:)", ms.text, flags=re.S)
    if not m:
        sys.exit("ABORT: abstract not found")
    words = len(re.sub(r"[*\\{}]", "", ABSTRACT).split())
    if words > 250:
        sys.exit(f"ABORT: the new abstract is {words} words, over the 250 limit")
    ms.sub(m.group(2), ABSTRACT, 1, "abstract rewritten (abbreviations defined)")

    # 3. maths: solidus for the one inline small fraction
    ms.sub(r"(H - m - \tfrac{1}{2})", "(H - m - 1/2)", 1,
           "inline tfrac{1}{2} -> 1/2 (solidus)")

    # 4. the one sentence that leaned on two abbreviations it never expanded
    ms.sub("The ROP and CRP line [10--15] formulates restoration as an ordering and "
           "routing problem",
           "The restoration-ordering and crew-routing line [10--15] formulates restoration "
           "as an ordering and routing problem",
           1, "ROP/CRP replaced by what they denote")

    # 5. a Highlight may not lean on an undefined abbreviation
    ms.sub("- An exact DP makes the full-horizon restoration optimum computable",
           "- An exact dynamic program makes the full-horizon restoration optimum "
           "computable",
           1, "Highlight: DP -> dynamic program")

    # 6. first-page abbreviation footnote, carried in the front matter
    ms.sub("**Keywords:**", ABBREVIATIONS + "\n\n**Keywords:**", 1,
           "abbreviations block added to the front matter")

    for d in (ms, supp):
        if len(re.findall(r"\b(?:isation|isations|ised|ising)\b", d.text)):
            sys.exit(f"ABORT: {d.path.name} still has -isation/-ised forms")
    if re.search(r"\b(?:behaviour|favourable|neighbour|programme|modelling)\b", ms.text):
        sys.exit("ABORT: British spellings survive in the manuscript")

    ms.save("PRE_JOURNALFORMATFIX_2026-09-14")
    supp.save("PRE_JOURNALFORMATFIX_2026-09-14")
    print(f"\nabstract: {words} words (limit 250)")


if __name__ == "__main__":
    main()
