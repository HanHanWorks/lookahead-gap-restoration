"""Final polish pass: equation reference closure, sentence splitting, one word fix.

Three targeted classes of change, no content removed:
  1. Eq. (9) was numbered but never cited in the prose -- Elsevier requires every
     numbered display equation to be referred to from the text.
  2. Sentences above 48 words, created by the compression's longer compound
     constructions, are split at their natural boundary.
  3. One connective "yet" replaced, per the house style rule for this manuscript.
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MS = ROOT / "SEGAN_manuscript_revised_2026-09-13.md"
doc = MS.read_text(encoding="utf-8")
before = len(doc.split())

EDITS = [
    # 1. cite Eq. (9)
    (
        "non-decreasing in $k$ and satisfying $\\Gamma_m = \\Gamma_{\\mathrm{LA}}$. It answers a "
        "design question: **how much foresight is needed to capture the value?**",
        "The profile of Eq. (9) is non-decreasing in $k$ and satisfies "
        "$\\Gamma_m = \\Gamma_{\\mathrm{LA}}$. It answers a design question: **how much foresight is "
        "needed to capture the value?**",
    ),
    # 3. connective "yet"
    (
        "all four condition groups have $\\Gamma_{\\mathrm{LA}} = 0$ to machine precision (maximum "
        "$1.1\\times10^{-13}$), yet the maximizing candidate is unique at 95.4% and 100% of the "
        "decision steps of the two IEEE 300-bus groups (Table 2).",
        "all four condition groups have $\\Gamma_{\\mathrm{LA}} = 0$ to machine precision (maximum "
        "$1.1\\times10^{-13}$). The maximizing candidate is nonetheless unique at 95.4% and 100% of "
        "the decision steps of the two IEEE 300-bus groups (Table 2).",
    ),
    # --- 2. sentence splitting
    (
        "The first is **attribution**. When a learned policy outperforms a reference, which "
        "component produced the gain: the learned ordering, the admissibility screen that decides "
        "whether an action is legal, the aggregate metric, or the choice of reference? A policy "
        "whose gain comes entirely from refusing illegal actions is not evidence that learning "
        "orders anything.",

        "The first is **attribution**: when a learned policy outperforms a reference, which "
        "component produced the gain? The candidates are the learned ordering, the admissibility "
        "screen that decides whether an action is legal, the aggregate metric, and the choice of "
        "reference. The distinction is not academic, because a policy whose gain comes entirely "
        "from refusing illegal actions is not evidence that learning orders anything.",
    ),
    (
        "and the measurement boundary should be stated, because the same trained network is "
        "measured 2.5--3.0 times slower when a deep-learning library's prediction wrapper is "
        "included than when a bare forward pass is timed.",

        "and the measurement boundary should be stated. The boundary matters: the same trained "
        "network is measured 2.5--3.0 times slower when a deep-learning library's prediction "
        "wrapper is included than when a bare forward pass is timed.",
    ),
    (
        "This section is the theoretical core: Sections 4.1--4.2 remove the terminal term from the "
        "ordering problem, Section 4.3 makes the full-horizon optimum exactly computable and "
        "defines the lookahead gap, Section 4.4 turns the gap into a benefit bound and an "
        "identifiability test, Section 4.5 separates the gap's *value* from its *accessibility*, "
        "and Section 4.6 closes with a cost-aware decision procedure.",

        "This section is the theoretical core. Sections 4.1--4.2 remove the terminal term from the "
        "ordering problem, and Section 4.3 makes the full-horizon optimum exactly computable and "
        "defines the lookahead gap. Section 4.4 turns the gap into a benefit bound and an "
        "identifiability test, Section 4.5 separates its *value* from its *accessibility*, and "
        "Section 4.6 closes with a cost-aware decision procedure.",
    ),
    (
        "If a budget caps the number of effective actions at $B < m$, the terminal set is no longer "
        "$B_0$ but the policy's chosen subset of size $B$, the terminal term becomes "
        "order-dependent, and the nested-chain structure is replaced by a selection *and* "
        "sequencing problem — the subject of Corollary 4(b).",

        "If a budget caps the number of effective actions at $B < m$, the terminal set is no longer "
        "$B_0$ but the policy's chosen subset of size $B$. The terminal term then becomes "
        "order-dependent, and the nested-chain structure is replaced by a selection *and* "
        "sequencing problem — the subject of Corollary 4(b).",
    ),
    (
        "That quantity is computed at run time but is not persisted for the unscreened arms, whose "
        "trajectories diverge from the screened ones at the first ineffective step and so cannot be "
        "joined to recover it; Section 3.5 records this as a measurement boundary and Appendix D as "
        "a release requirement.",

        "That quantity is computed at run time but is not persisted for the unscreened arms, whose "
        "trajectories diverge from the screened ones at the first ineffective step and so cannot be "
        "joined to recover it. Section 3.5 records this as a measurement boundary and Appendix D as "
        "a release requirement.",
    ),
    (
        "Section 5.4 reports the implementation check, and Appendix B names the artifact behind each "
        "record: the recursion reproduces the frozen gap values to $0.000000000$ on both protocols, "
        "the injected-capacity implementation reproduces them to $0.000000$ on all 40 shared "
        "instances, and the rolling controller stays inside the envelope "
        "$[J(\\pi^{\\mathrm{my}}), f(\\emptyset)]$ that the recursion defines.",

        "Section 5.4 reports the implementation check, and Appendix B names the artifact behind each "
        "record. The recursion reproduces the frozen gap values to $0.000000000$ on both protocols, "
        "and the injected-capacity implementation reproduces them to $0.000000$ on all 40 shared "
        "instances. The rolling controller stays inside the envelope "
        "$[J(\\pi^{\\mathrm{my}}), f(\\emptyset)]$ that the recursion defines.",
    ),
    (
        "The pre-check of Section 2.6 and the gap are therefore reported as **complementary "
        "diagnostics rather than a single test**: the pre-check is cheap, needs no dynamic program, "
        "and never rejects a condition that carries headroom, while the gap is complete, certifying "
        "exactly when the one-step exact rule cannot be improved on, at the cost of a dynamic "
        "program per condition.",

        "The pre-check of Section 2.6 and the gap are therefore reported as **complementary "
        "diagnostics rather than a single test**. The pre-check is cheap, needs no dynamic program, "
        "and never rejects a condition that carries headroom. The gap is complete, certifying "
        "exactly when the one-step exact rule cannot be improved on, at the cost of a dynamic "
        "program per condition.",
    ),
    (
        "The cause is the action set rather than the capacity-rule parameters, and no setting of "
        "those parameters repairs the degeneracy anywhere in the operating range: over eight values "
        "of the capacity margin and three of the floor share, 96 configurations in all, the fraction "
        "of decision steps with a unique maximizing candidate stays at or below 0.50 for both groups "
        "at $\\kappa = 1.15$, and the configurations that do raise it require line capacities below "
        "the base-case flow, which is a derating rather than an operating margin.",

        "The cause is the action set rather than the capacity-rule parameters, and no setting of "
        "those parameters repairs the degeneracy anywhere in the operating range. Over eight values "
        "of the capacity margin and three of the floor share, 96 configurations in all, the fraction "
        "of decision steps with a unique maximizing candidate stays at or below 0.50 for both groups "
        "at $\\kappa = 1.15$. The configurations that do raise it require line capacities below the "
        "base-case flow, which is a derating rather than an operating margin.",
    ),
    (
        "Against the one-step exact rule the rolling rule wins 35 times, ties 205 times and never "
        "loses, for a mean advantage of +4.78 units; because 205 of those pairs are tied, the "
        "per-condition tests for that row are underpowered and its evidence rests on the pooled "
        "test, which is why Table 7 reports both.",

        "Against the one-step exact rule the rolling rule wins 35 times, ties 205 times and never "
        "loses, for a mean advantage of +4.78 units. Because 205 of those pairs are tied, the "
        "per-condition tests for that row are underpowered and its evidence rests on the pooled "
        "test, which is why Table 7 reports both.",
    ),
    (
        "the measured per-condition advantages of 8.74, 5.27, 6.97, 4.38, 8.37, 4.93, 8.95, 2.51, "
        "0.00, 2.70, 0.73 and 3.84 agree with the dynamic program's values of Table 4 (8.739, "
        "5.274, 6.970, 4.384, 8.370, 4.934, 8.951, 2.511, 0, 2.762, 0.731, 3.924) to the precision "
        "printed, so the theoretical quantity is reproduced by an entirely separate code path.",

        "the measured per-condition advantages of 8.74, 5.27, 6.97, 4.38, 8.37, 4.93, 8.95, 2.51, "
        "0.00, 2.70, 0.73 and 3.84 agree with the dynamic program's values of Table 4 (8.739, "
        "5.274, 6.970, 4.384, 8.370, 4.934, 8.951, 2.511, 0, 2.762, 0.731, 3.924) to the precision "
        "printed. The theoretical quantity is therefore reproduced by an entirely separate code "
        "path.",
    ),
    (
        "The remaining ratings span 8.5 MW to 562 MW, so the transfer capability of the transplanted "
        "network rests on a small number of lightly loaded lines, and the linear program fails to "
        "converge under every solver available; relaxing the floor until it converges removes the "
        "binding structure and the gap returns to zero.",

        "The remaining ratings span 8.5 MW to 562 MW, so the transfer capability of the transplanted "
        "network rests on a small number of lightly loaded lines, and the linear program fails to "
        "converge under every solver available. Relaxing the floor until it converges removes the "
        "binding structure and the gap returns to zero.",
    ),
    (
        "A positive gap requires capacities tied to base-case utilisation **and** a floor small "
        "enough not to dominate: raising the floor to 5% of demand sets every line's capacity well "
        "above its base-case usage and the gap vanishes identically, and uniform thermal ratings "
        "leave the network over-built relative to demand by a factor of more than two and do the "
        "same.",

        "A positive gap requires capacities tied to base-case utilisation **and** a floor small "
        "enough not to dominate. Raising the floor to 5% of demand sets every line's capacity well "
        "above its base-case usage, and the gap vanishes identically; uniform thermal ratings leave "
        "the network over-built relative to demand by a factor of more than two, and do the same.",
    ),
]

bad = 0
for old, new in EDITS:
    n = doc.count(old)
    if n != 1:
        print(f"!! anchor x{n}: {old[:80]!r}")
        bad += 1
        continue
    doc = doc.replace(old, new)
if bad:
    raise SystemExit(f"{bad} anchors failed; nothing written")

MS.write_text(doc, encoding="utf-8")
print(f"polish edits applied: {len(EDITS)}")
print(f"whole file: {before} -> {len(doc.split())} words")
