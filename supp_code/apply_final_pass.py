"""Final pass: figure-citation order, abstract length, sentence splitting."""
from __future__ import annotations

import pathlib
import sys

P = pathlib.Path("SEGAN_manuscript_revised_2026-09-13.md")
s = P.read_text(encoding="utf-8")
orig = s
R: list[tuple[str, str]] = []


def rep(old: str, new: str) -> None:
    R.append((old, new))


# --- §4.5 must not cite Figure 5 before Figures 3 and 4 exist in the text
rep("Figure 5 reports the measured profiles.",
    "The profiles are measured in Section 5.5.")
rep("accessibility is measurable. Figure 5 reports the measured profiles, and Section 5.5 reports "
    "the corresponding numbers for both protocols and for the third test system.",
    "accessibility is measurable. Section 5.5 measures the profiles for both protocols and for the "
    "third test system.")

# --- Table 7 note: split the 57-word sentence
rep("Third, against the one-step exact rule the rolling rule wins 35 times, ties 205 times and never "
    "loses, for a mean advantage of +4.78 units; with 205 of 240 pairs tied, the evidence for that "
    "row rests on the pooled test ($p = 2.5\\times10^{-7}$) rather than on the per-condition tests, "
    "which is why Table 7 reports both.",
    "Third, against the one-step exact rule the rolling rule wins 35 times, ties 205 times and never "
    "loses, for a mean advantage of +4.78 units. Because 205 of those 240 pairs are tied, the "
    "evidence for that row rests on the pooled test ($p = 2.5\\times10^{-7}$) rather than on the "
    "per-condition tests, which is why Table 7 reports both.")

# --- §5.1 sweep sentence: split the 52-word sentence
rep("A sweep over eight values of the capacity margin and three of the floor share, 96 "
    "configurations in all, holds the fraction of decision steps with a unique maximizing candidate "
    "at or below 0.50 for both groups when $\\kappa = 1.15$, so both diagnostics fail at every "
    "setting a study would plausibly use.",
    "A sweep over eight values of the capacity margin and three of the floor share, 96 "
    "configurations in all, holds the fraction of decision steps with a unique maximizing candidate "
    "at or below 0.50 for both groups when $\\kappa = 1.15$. Both diagnostics therefore fail at every "
    "setting a study would plausibly use.")

# --- abstract: 256 -> <=250 words
rep("We make four methodological contributions. First, an attribution framework writes any "
    "prioritization policy as a ranker composed with an admissibility screen, and decomposes its "
    "stepwise regret exactly into a ranking term and a censoring term.",
    "We make four methodological contributions. First, an attribution framework writes any "
    "prioritization policy as a ranker composed with an admissibility screen, and splits its "
    "stepwise regret exactly into a ranking term and a censoring term.")
rep("This defines the lookahead gap: an exactly computable upper bound on the benefit that any "
    "prioritization policy can deliver over a one-step exact rule.",
    "This defines the lookahead gap: an exactly computable upper bound on the benefit of any "
    "prioritization policy over a one-step exact rule.")
rep("Third, the gap is a two-dimensional object. Its magnitude bounds what any policy can gain; how "
    "cheaply that gain can be collected is a separate question, governed by a depth profile that we "
    "introduce. A committed plan needs five steps of foresight to collect the whole gap; a rolling "
    "depth-2 controller collects 99.4--99.8% of it, and depth 3 collects it exactly.",
    "Third, the gap is a two-dimensional object: its magnitude bounds what any policy can gain, "
    "while how cheaply that gain can be collected is governed by a depth profile that we introduce. "
    "A committed plan needs five steps of foresight to collect the whole gap, whereas a rolling "
    "depth-2 controller collects 99.4--99.8% of it and depth 3 collects it exactly.")
rep("Across three public test systems the gap is positive in 11 of 12 conditions per protocol, and "
    "reaches 120.1 AUC@25 units under a reconnection budget.",
    "Across three public test systems the gap is positive in 11 of 12 conditions per protocol and "
    "reaches 120.1 AUC@25 units under a reconnection budget.")


def main() -> int:
    global s
    bad = 0
    for old, new in R:
        n = s.count(old)
        if n != 1:
            print(f"!! count={n}  {old[:80]!r}")
            bad += 1
            continue
        s = s.replace(old, new)
    if bad:
        print(f"\n{bad} replacement(s) did not match; nothing written.")
        return 1
    P.write_text(s, encoding="utf-8")
    print(f"applied {len(R)} replacements; file grew {len(s)-len(orig):+d} chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
