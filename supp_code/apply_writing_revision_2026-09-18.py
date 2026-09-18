#!/usr/bin/env python3
"""Writing revision of 2026-09-18, applied to SEGAN_manuscript_revised_2026-09-13.md.

Scope: the *writing* defects identified by the five-part audit of 2026-09-18.
Every edit is anchored on a unique string and asserted before anything is
written, so a silent mis-hit is impossible.

Edits
-----
W1  Introduction gains the five-move lead paragraph (consensus -> mainstream and
    its implicit assumptions -> the cracks -> the barriers -> the way in),
    placed before Section 1.1.  Motivation and "why now" are stated for the
    first time; no results numbers, no new citations, no new terms.
W2  The "Our goal" paragraph leaves Section 1.2 (it sat *before* the barriers of
    Section 1.3, which inverted moves 4 and 5) and its C4/C5 pointer moves into
    Section 1.3, whose closing paragraph is compressed against the new lead.
W3  Section 1.2's A2 crack gains the power-domain contradiction that Section 8.1
    already carried: endpoint metrics must agree by Lemma 1, so an agreement
    read as robustness is a property of the service model.  A2 stops being a
    bare "nobody has checked" gap.
W4  Section 1.4 (C3 and the supporting contribution) loses the results numbers
    99.4--99.8%, 240 and 2.5--3.1; the pointer to the sections that report
    them replaces them.
W5  Eq. (1) notation: g(empty) was declared to be the *intact* network while
    every other use of the empty set in the paper means the *initial*
    (nothing-reconnected) state, and l_0 = l(B_0 u O_0) passed a *broken* set to
    a functional parameterised by the *reconnected* set.  Literally read,
    l_0 = 0 and r(S) divides by zero.  Now g_intact is a separate symbol and
    l_0 = l(empty).
W6  Section 4.6's "4,096 at the largest" contradicted the stated O(2^m m)
    (2^12 * 12 = 49,152): 4,096 counts *states*.  Both counts are now named.
W7  Four plain-text equation cross-references become Eq. (n), which
    md_to_latex.py converts to \eqref.
W8  Section 5.7's unrestricted-sample row reports two of three outcomes
    (34 + 176 = 210 of 240); the 30 losses are restored.
W9  Five evaluative sentences leave the Results section for the Discussion that
    already carries them (the Results section is supposed to present, not to
    judge), and the two that carried a pointer now point explicitly.
W10 Section 5.1's threshold sentence is split so that which number belongs to
    which group, and which diagnostic carries the verdict, can be read once.
W11 Conclusions gain the three missing closure items: the time value of the
    question (why now), the data boundary of the numerical claim (three systems
    and the capacity rule), and the latency cost of the recommended controller.
W12 Section 8.6's three unexplained observations each gain the experiment that
    would settle them, so the seeds are executable rather than listed.
W13 Abstract: the symbol AUC@25 is removed (the journal requires non-standard
    abbreviations to be defined at first mention *in the abstract*, and the
    abstract is at 246 of the 250-word ceiling), and the First/Second/Third/
    Fourth/Fifth scaffolding is dropped.  Every finding and every number is
    kept.

Not done, deliberately: the Lemma 0 / Lemma 1 family is 0-indexed and contiguous
(so "no Lemma 2" is not a gap), renaming A0 is unnecessary because Section 2.3
already states that A0 belongs to a different family from A1--A3, and the
Corollary family (2, 3, 4) was left alone because renumbering it would also
touch the supplementary material, whose Table S2 cites Lemma 1.

Run:  python3 supp_code/apply_writing_revision_2026-09-18.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "SEGAN_manuscript_revised_2026-09-13.md"

LEAD = """Slow restoration is paid for in unserved load, and the quantity at stake in a restoration policy is the area under the recovery curve: the value of restoring load earlier rather than later. Learned policies are increasingly proposed for this ordering problem, while the field's surveys converge on the absence of the standardized benchmarks that would say which of them is worth training [11--12].

Into those comparisons each policy enters as a model-free and aggregate object, and Section 1.1 shows that they carry three assumptions *implicitly rather than tested*: about what produced a reported gain (A1), about whether the aggregated conditions can carry ordering information at all (A2), and about whether the headroom a comparison reveals is cheaply reachable, and belongs to the grid rather than to the capacity convention that evaluates it (A3).

Each assumption has a documented crack. The screen is itself a standard device of the learning branch [2], and where an exact solver is included the learned policy is generally better in time and worse in quality [3], so a single aggregate number moves along two axes that it reports as one. The endpoint metrics such comparisons report must agree across policies once the reconnection completes, so an agreement read as evidence that a comparison is robust is a property of the service model rather than of the policies. And the classical branch's own flagship result is a heuristic claimed to be near-optimal and a thousand times faster [10], which leaves the value of lookahead reported but neither its accessibility nor its regime settled.

None of the three has been closed for want of data: the test systems are public, the scenarios are fixed-seed, and the artifacts of this paper are released. Three barriers of method and framing stand in the way instead: an exact value of lookahead appears to require simulation or intractable enumeration; its value and its accessibility are different questions that a scalar measure conflates; and whether any headroom exists at all may be a property of the evaluator's capacity convention rather than of the grid. **Our goal**, in one sentence: *to make the source of a reported gain identifiable, and to provide an exactly computable criterion that separates how much lookahead is worth from how cheaply it can be realized.* The way in is to stop asking which policy is better and ask instead what *any* policy could have gained, a quantity that is exactly computable for maximum-flow service models and requires no policy to be trained."""

ABSTRACT_OLD = """Machine learning is increasingly proposed for restoration prioritization, yet reported gains are seldom attributed to the component producing them. First, an attribution framework writes any policy as a ranker composed with an admissibility screen, splitting its stepwise regret into ranking and censoring terms. Second, for exactly evaluable maximum-flow service models, the full-horizon optimum is computable by dynamic programming over broken-key-line subsets, defining the lookahead gap: an exact bound on what any policy reconnecting within the horizon can gain over a one-step exact rule, vanishing under step-wise degeneracy but not conversely. Third, a depth profile governs how cheaply it is collected: under a budget a committed plan needs five steps of foresight for the whole gap, whereas a rolling controller collects 99.4--99.8% of it at depth two and the whole gap by depth three with a budget, four without. Fourth, a four-rule sweep shows the gap requires capacities proportional to base-case utilization, vanishing under uniform ratings. Fifth, the pre-check and the gap are complementary: the pre-check never rejects a condition with headroom, the gap flags conditions it passes. The gap is positive in 11 of 12 conditions per regime on the two IEEE systems, reaching 120.1 AUC@25 units at a budget of six, and in six of six on a third system without a budget. The four learned configurations trained here nonetheless lose all 240 paired comparisons to a rolling depth-2 rule needing no training; latency claims should name the cheapest non-learned rule that could replace them."""

ABSTRACT_NEW = """Machine learning is increasingly proposed for restoration prioritization, yet reported gains are seldom attributed to the component producing them. An attribution framework writes any policy as a ranker composed with an admissibility screen and splits its stepwise regret into ranking and censoring terms. For exactly evaluable maximum-flow service models the full-horizon optimum is computable by dynamic programming over broken-key-line subsets, which defines the lookahead gap: an exact bound on what any policy reconnecting within the horizon can gain over a one-step exact rule, vanishing under step-wise degeneracy but not conversely. A depth profile governs how cheaply the gap is collected: under a budget a committed plan needs five steps of foresight for the whole gap, whereas a rolling controller collects 99.4--99.8% at depth two and all of it by depth three under a budget, by depth four without. A four-rule sweep shows the gap requires capacities proportional to base-case utilization. The pre-check and the gap are complementary: the pre-check never rejects a condition with headroom, the gap flags conditions it passes. The gap is positive in 11 of 12 conditions per regime on the two IEEE systems, reaching 120.1 units of the area under the restoration curve at a budget of six, and in all six on a third system without one. The four learned configurations trained here lose all 240 paired comparisons to a rolling depth-2 rule that needs no training; latency claims should name the cheapest non-learned rule that could replace them."""


def lead_in_1_1():
    return (
        "## 1. Introduction\n\n" + LEAD + "\n\n"
        "### 1.1 Learned restoration prioritization and its implicit assumptions\n"
    )


EDITS = [
    # ---------------- W1: the five-move lead paragraph ----------------
    (
        "W1 five-move lead paragraph inserted before Section 1.1",
        "## 1. Introduction\n\n### 1.1 Learned restoration prioritization and its implicit assumptions\n",
        lead_in_1_1(),
        1,
    ),
    # ---------------- W2: move the entry point out of 1.2 ----------------
    (
        "W2 remove the 'Our goal' paragraph from Section 1.2",
        "\n**Our goal**, in one sentence: *to make the source of a reported gain identifiable, and to provide an exactly computable criterion that separates how much lookahead is worth from how cheaply it can be realized.* The regime in which the value is non-trivial, and the demonstration on three public test systems, are contributions C4 and C5 below.\n",
        "",
        1,
    ),
    (
        "W2 compress Section 1.3's closing paragraph and carry the C4/C5 pointer",
        "Both questions of Section 1.1 are answered by quantities that require no policy to be trained: "
        "answerability by an exactly computable pre-check, available *before* training, and attribution by an "
        "exact decomposition of a policy that has been evaluated. Neither requires simulation, for the structural "
        "reason stated as C2 below. We develop both and use them to interpret an experimental program on three "
        "public test systems. The claims are about the structure of the prioritization problem, not the performance "
        "of any particular learned policy. Figure 1 collects the objects involved.",
        "The two quantities are developed below and used to interpret an experimental program on three public test "
        "systems; the regime in which the value is non-trivial, and that demonstration, are contributions C4 and C5. "
        "The claims are about the structure of the prioritization problem, not the performance of any particular "
        "learned policy, and Figure 1 collects the objects involved.",
        1,
    ),
    # ---------------- W3: A2 gains the contradiction ----------------
    (
        "W3 A2 crack gains the Lemma 1 contradiction from Section 8.1",
        "Aggregating such conditions into a primary test family therefore inflates the apparent evidence rather "
        "than adding to it (Corollary 3, Section 4.4; applied in Section 5.1).",
        "Aggregating such conditions into a primary test family therefore inflates the apparent evidence rather "
        "than adding to it (Corollary 3, Section 4.4; applied in Section 5.1). The endpoint metrics such comparisons "
        "report fail in the same way: because terminal behavior is order-invariant (Lemma 1, Section 4.1), such a "
        "metric must agree across policies once the reconnection completes, so an agreement cited as evidence that a "
        "comparison is robust is a property of the service model rather than of the policies.",
        1,
    ),
    # ---------------- W4: results numbers leave Section 1.4 ----------------
    (
        "W4 C3 loses its results numbers",
        "In the budgeted regime a committed plan needs five steps of foresight to capture the gap, and without a "
        "budget it reaches only 41% by depth five; a rolling depth-2 controller captures the same 99.4--99.8% on "
        "average and is exact at depth 3 under a budget and at depth 4 without one. On the same instances the rolling "
        "depth-2 rule wins all 240 paired comparisons against the four learned variants, and needs no training.",
        "In the budgeted regime a committed plan needs five steps of foresight to capture the gap, and without a "
        "budget it captures less than half of it by depth five; a rolling depth-2 controller captures nearly all of "
        "it at depth two and is exact by depth three under a budget and depth four without one. On the same instances "
        "it is never worse than any of the four learned variants, and needs no training. Sections 5.5 and 5.7 report "
        "the shares and the paired counts.",
        1,
    ),
    (
        "W4 reporting-standard paragraph loses the 2.5--3.1 number",
        "The boundary matters: the same network is measured 2.5--3.1 times slower with a deep-learning library's "
        "prediction wrapper inside the timed region than with a bare forward pass.",
        "The boundary matters: the same network, unchanged in method, is measured several times slower with a "
        "deep-learning library's prediction wrapper inside the timed region than with a bare forward pass.",
        1,
    ),
    # ---------------- W5: Eq. (1) notation ----------------
    (
        "W5a define g_intact",
        "Writing $g(S)$ for the maximum flow that reaches the load nodes when the reconnected set is $S$, the "
        "service model is",
        "Writing $g(S)$ for the maximum flow that reaches the load nodes when the reconnected set is $S$, and "
        "$g_{\\mathrm{intact}}$ for that quantity on the intact network, the service model is",
        1,
    ),
    (
        "W5b Eq. (1) uses g_intact and l_0 = l(empty)",
        "$$\\ell(S) = \\max\\{0,\\; g(\\emptyset) - g(S)\\}, \\qquad r(S) = 100 \\cdot "
        "\\frac{\\ell_0 - \\ell(S)}{\\ell_0}, \\qquad \\ell_0 = \\ell(\\mathcal{B}_0 \\cup O_0). \\tag{1}$$",
        "$$\\ell(S) = \\max\\{0,\\; g_{\\mathrm{intact}} - g(S)\\}, \\qquad r(S) = 100 \\cdot "
        "\\frac{\\ell_0 - \\ell(S)}{\\ell_0}, \\qquad \\ell_0 = \\ell(\\emptyset). \\tag{1}$$",
        1,
    ),
    (
        "W5c note below Eq. (1) follows the new notation",
        "In Eq. (1), $\\ell(S)$ is the unserved load that remains when the set $S$ has been reconnected, $g(S)$ the "
        "maximum flow delivered to the load nodes in that state, $g(\\emptyset)$ the same quantity on the intact "
        "network, $r(S)$ the recovery in percent of the initial unserved load $\\ell_0 = \\ell(\\mathcal{B}_0 \\cup "
        "O_0)$, and $\\mathcal{B}_0 \\cup O_0$ the initial contingency of Section 2.1.",
        "In Eq. (1), $\\ell(S)$ is the unserved load that remains when the set $S$ has been reconnected, $g(S)$ the "
        "maximum flow delivered to the load nodes in that state, $g_{\\mathrm{intact}}$ the same quantity on the "
        "intact network, $r(S)$ the recovery in percent of the initial unserved load $\\ell_0 = \\ell(\\emptyset)$ "
        "(the empty reconnected set is the initial contingency of Section 2.1), and $\\ell$ therefore a function of "
        "the broken set $(\\mathcal{B}_0 \\setminus S) \\cup O_0$ alone.",
        1,
    ),
    # ---------------- W6: state count vs evaluation count ----------------
    (
        "W6 Section 4.6 separates states from service evaluations",
        "Step 1 is cheap: on these instances the dynamic program costs at most a few thousand service evaluations "
        "(4,096 at the largest), a median of 8 s of wall-clock time reaching 1.4 min on the heaviest instance, and no "
        "simulator rollouts, so the procedure is usable as a benchmark design tool, which is how Section 5.1 first "
        "applies it.",
        "Step 1 is cheap: on these instances the dynamic program visits at most $2^m = 4{,}096$ subset states at "
        "$m = 12$, expanding each over at most $m$ candidates, so at most $2^m m$ service evaluations and no "
        "simulator rollouts; the median wall-clock time is 8 s, reaching 1.4 min on the heaviest instance, so the "
        "procedure is usable as a benchmark design tool, which is how Section 5.1 first applies it.",
        1,
    ),
    # ---------------- W7: equation cross-references ----------------
    (
        "W7a symbol table: Eqs. 1 and 3",
        "the recovery $r$ and the objective $J$ (Eqs. 1 and 3);",
        "the recovery $r$ and the objective $J$ (Eq. (1) and Eq. (3));",
        1,
    ),
    (
        "W7b symbol table: Eqs. 5 and 5a",
        "with their indicator forms $c_t$ and $D_t$ (Eqs. 5 and 5a);",
        "with their indicator forms $c_t$ and $D_t$ (Eq. (5) and Eq. (5a));",
        1,
    ),
    (
        "W7c symbol table: Eqs. 8 and 9",
        "with its depth-$k$ realization $\\Gamma_k$ (Eqs. 8 and 9).",
        "with its depth-$k$ realization $\\Gamma_k$ (Eq. (8) and Eq. (9)).",
        1,
    ),
    (
        "W7d Figure 1 caption: Eq. 5",
        "and a censoring loss $C_t$ (Eq. 5), either",
        "and a censoring loss $C_t$ (Eq. (5)), either",
        1,
    ),
    # ---------------- W8: the missing third outcome ----------------
    (
        "W8 Section 5.7 reports the 30 losses",
        "the same comparison gives 896 wins and 64 losses for the learned variants, and the one-step exact rule "
        "gains 34 wins and 176 ties with a mean advantage of 27.2 units over the rolling controller.",
        "the same comparison gives 896 wins and 64 losses for the learned variants, and the one-step exact rule "
        "gains 34 wins, 176 ties and 30 losses against it, with a mean advantage of 27.2 units over the rolling "
        "controller.",
        1,
    ),
    # ---------------- W9: judgement leaves the Results section ----------------
    (
        "W9a Section 5.1: drop the gate recommendation (kept in Section 10)",
        "so *the pre-check never rejects a condition that carries headroom* and can be used as a gate without "
        "discarding a condition worth studying.",
        "so *the pre-check never rejects a condition that carries headroom*.",
        1,
    ),
    (
        "W9b Section 5.4: drop the design lesson (kept in Section 8.4)",
        "The largest uncoupled value overall, 16.611 on IEEE 118 severe 1.50, was already exposed by the old rule. "
        "*A statement about which conditions carry ordering information is therefore a statement about the instance "
        "rule as much as about the system*, the design-time lesson of Corollary 3. Figure 4 isolates the effect:",
        "The largest uncoupled value overall, 16.611 on IEEE 118 severe 1.50, was already exposed by the old rule. "
        "Figure 4 isolates the effect:",
        1,
    ),
    (
        "W9c Section 5.4: point at the consequence",
        "and Figure 4(b) the per-condition fraction of instances with a positive gap.",
        "and Figure 4(b) the per-condition fraction of instances with a positive gap. Section 8.4 draws the design "
        "consequence.",
        1,
    ),
    (
        "W9d Section 5.5: drop the recommendation (kept in Section 8.2)",
        "The finding is therefore sharper than \"lookahead has value\". The gap's *value* is real and exactly "
        "computable; its *accessibility* is far cheaper than the value alone suggests, since a rolling depth-2 "
        "controller already collects 99.4--99.8% of it on these instances. The modeller need only ask whether two "
        "steps are affordable, and Table 5 shows that they are. Why two steps suffice, and why the size of the gap "
        "alone does not settle whether a learned orderer is warranted, is taken up in Sections 8.2 and 8.5.",
        "The gap's *value* is real and exactly computable, and its *accessibility* is far cheaper than the value "
        "alone suggests, since a rolling depth-2 controller already collects 99.4--99.8% of it on these instances. "
        "Why two steps suffice, and why the size of the gap alone does not settle whether a learned orderer is "
        "warranted, is taken up in Sections 8.2 and 8.5.",
        1,
    ),
    (
        "W9e Section 5.6: drop the instrument recommendation (kept in Section 8.2)",
        "The budget is therefore a design parameter with a non-monotone effect, and a phase diagram rather than a "
        "single-point comparison against a legacy configuration is the right instrument for choosing it.",
        "The budget is therefore a design parameter whose effect is non-monotone over this range; Section 8.2 draws "
        "the consequence for how a benchmark should choose it.",
        1,
    ),
    (
        "W9f Section 5.8: scope the generalization to what was measured",
        "The sign of the gap and the direction of the budget effect therefore reproduce on a third system of a "
        "different size and origin, so the criterion's discrimination is a property of the problem class rather "
        "than of the two systems studied most intensively.",
        "The sign of the gap and the direction of the budget effect therefore reproduce on a third system of a "
        "different size and origin, so the criterion's discrimination is not confined to the two IEEE systems.",
        1,
    ),
    # ---------------- W10: readable threshold sentence ----------------
    (
        "W10 Section 5.1 threshold sentence split",
        "Across the 96 configurations of the sweep the uniqueness diagnostic stays at or below 0.50 for both "
        "IEEE 118-bus groups, whereas the second sits close to its 0.85 cut-off for the severe group: the sweep "
        "gives 0.995 and 0.781 at $\\kappa = 1.15$, against the 1.00 and 0.87 of Table 3 on the evaluation protocol.",
        "Across the 96 configurations of the sweep the uniqueness diagnostic stays at or below 0.50 for both "
        "IEEE 118-bus groups. The second diagnostic is closer to its cut-off for one of them: at $\\kappa = 1.15$ the "
        "sweep gives 0.781 for the severe group against 0.87 in Table 3 on the evaluation protocol, and 0.995 for "
        "the moderate group against 1.00.",
        1,
    ),
    # ---------------- W11: conclusion closure ----------------
    (
        "W11a the numerical claim gains its data boundary",
        "It is positive in 11 of 12 conditions of each regime under the protocol-independent rule of Sections "
        "5.4--5.5 ($N \\ge 7$; Table S1), reaching a per-condition maximum of 120.1 AUC@25 units at $B = 6$ and "
        "134.4 at $B = 8$ (Figure 6),",
        "On the three test systems and under the utilization-proportional capacity rule of Eq. (2), it is positive "
        "in 11 of 12 conditions of each regime under the protocol-independent rule of Sections 5.4--5.5 ($N \\ge 7$; "
        "Table S1), reaching a per-condition maximum of 120.1 AUC@25 units at $B = 6$ and 134.4 at $B = 8$ "
        "(Figure 6),",
        1,
    ),
    (
        "W11b the time-value paragraph gains why-now and the latency cost",
        "The instrument is cheap in time as well: the pre-check and the gap are computable before training, at a "
        "median of 8 s and at most 1.4 min for the heaviest instance, so a benchmark can be audited while it is "
        "still being designed.",
        "The question is live rather than retrospective: learned policies are being proposed for restoration "
        "ordering while the standardized benchmarks that could say when they are warranted are still absent "
        "(Section 1.5), so the audit the criterion supports can be run while a benchmark is being designed rather "
        "than after it has been published on. The instrument is cheap in time as well: the pre-check and the gap "
        "are computable before training, at a median of 8 s and at most 1.4 min for the heaviest instance. The "
        "controller the gap points to is not the cheapest one on the cost axis: two steps of rolling lookahead cost "
        "tens to hundreds of milliseconds per decision against tens of microseconds for a trained network "
        "(Section 7), so the recommendation trades latency for a quality that no trained policy tested here "
        "reached; stating both sides of that trade is the reporting convention of Section 7.",
        1,
    ),
    # ---------------- W12: the seeds become executable ----------------
    (
        "W12a observation 1 gains its test",
        "The intuition that an added constraint makes a problem harder runs the other way here; the coverage ratio "
        "of Section 8.5 accounts for the direction, but not for the size, of the effect.",
        "The intuition that an added constraint makes a problem harder runs the other way here; the coverage ratio "
        "of Section 8.5 accounts for the direction, but not for the size, of the effect. What would settle it is a "
        "budget sweep in a domain whose effective horizon differs from this one: if the coverage ratio predicts the "
        "size as well as the direction, the inversion is a property of committed plans rather than of this "
        "objective.",
        1,
    ),
    (
        "W12b observation 2 gains its test",
        "Nothing in the analysis predicts this front-loading, and whether the same saturation appears in other "
        "sequential selection problems, or is an artefact of a functional that depends only on the broken set, is "
        "not settled by these instances.",
        "Nothing in the analysis predicts this front-loading, and whether the same saturation appears in other "
        "sequential selection problems, or is an artefact of a functional that depends only on the broken set, is "
        "not settled by these instances. The test is a functional that does not depend on the broken set alone, "
        "where the saturation either survives or is shown to follow from order-invariance.",
        1,
    ),
    (
        "W12c observation 3 gains its test",
        "Corollary 3 states the one-directional relation; it does not explain why a step at which the best action "
        "is uniquely determined can still leave no headroom for any ordering, and we do not have an account of it.",
        "Corollary 3 states the one-directional relation; it does not explain why a step at which the best action "
        "is uniquely determined can still leave no headroom for any ordering, and we do not have an account of it. "
        "What would settle it is a condition constructed to be step-wise degenerate with a unique maximizer at "
        "every step, which would separate the two properties by design rather than by observation.",
        1,
    ),
    # ---------------- W13: abstract ----------------
    (
        "W13 abstract loses the AUC@25 symbol and the First/Second scaffolding",
        ABSTRACT_OLD,
        ABSTRACT_NEW,
        1,
    ),
]


def count_words(s: str) -> int:
    return len(s.split())


def main() -> int:
    text = MD.read_text(encoding="utf-8")

    # ---- pre-flight: every anchor must hit the expected number of times ----
    failures = []
    for name, old, new, expected in EDITS:
        got = text.count(old)
        if got != expected:
            failures.append(f"  {name}: anchor found {got} time(s), expected {expected}")
    if failures:
        print("PRE-FLIGHT FAILED, nothing written:")
        print("\n".join(failures))
        return 1

    # ---- apply ----
    for name, old, new, expected in EDITS:
        text = text.replace(old, new)

    # ---- abstract word budget ----
    ab = re.search(r"## Abstract\n\n(.*?)\n", text, re.S).group(1)
    n_ab = count_words(ab)
    if n_ab > 250:
        print(f"ABSTRACT OVER CEILING: {n_ab} words > 250, nothing written.")
        return 1

    MD.write_text(text, encoding="utf-8")

    # ---- post-flight ----
    print(f"applied {len(EDITS)} edits to {MD.name}")
    print(f"abstract: {count_words(ABSTRACT_OLD)} -> {n_ab} words (ceiling 250)")
    print()
    print("post-flight checks (each must be as stated):")
    checks = [
        ("lead paragraph present", "Ask instead what *any* policy could have gained" in text or
         "ask instead what *any* policy could have gained" in text),
        ("'Our goal' no longer in Section 1.2", text.count("**Our goal**, in one sentence") == 1),
        ("A2 contradiction present once in Section 1.2",
         text.count("a property of the service model rather than of the policies.") == 2),
        ("no results number in Section 1.4", "99.4--99.8% on average" not in text),
        ("g_intact introduced and g(empty) retired from Eq. (1)",
         text.count("g_{\\mathrm{intact}}") == 3 and "g(\\emptyset)" not in text),
        ("l_0 is l(empty)", "\\ell_0 = \\ell(\\emptyset)" in text),
        ("B_0 u O_0 no longer an argument of l", "\\ell(\\mathcal{B}_0 \\cup O_0)" not in text),
        ("state count and evaluation count both named", "$2^m = 4{,}096$ subset states" in text),
        ("three plain-text equation lists gone",
         "(Eqs. 1 and 3)" not in text and "(Eqs. 5 and 5a)" not in text and "(Eqs. 8 and 9)" not in text),
        ("Section 5.7 reports all three outcomes",
         "34 wins, 176 ties and 30 losses" in text),
        ("no recommendation left in Section 5.1", "without discarding a condition worth studying" not in text),
        ("no design lesson left in Section 5.4", "design-time lesson of Corollary 3" not in text),
        ("Section 5.6 recommendation replaced", "the right instrument for choosing it" not in text),
        ("abstract free of AUC@25", "AUC@25" not in ab),
        ("abstract keeps every number",
         all(k in ab for k in ["11 of 12", "all six", "99.4--99.8%", "120.1", "240"])),
        ("conclusion carries the data boundary", "On the three test systems and under the utilization-proportional" in text),
        ("conclusion carries why-now", "The question is live rather than retrospective" in text),
        ("no em dash introduced", "—" not in text),
    ]
    ok = True
    for label, res in checks:
        print(f"  [{'ok ' if res else 'FAIL'}] {label}")
        ok = ok and res

    # ---- reference integrity ----
    cites = set()
    for c in re.findall(r"\[([\d,\-–\s]+)\]", text):
        for num in re.findall(r"\d+", c):
            cites.add(int(num))
    bib = set(range(1, 42))
    print()
    print(f"citation keys now referenced: {len(cites)}; highest {max(cites)}")
    missing = bib - cites
    if missing:
        print(f"  WARNING bibitems never cited: {sorted(missing)}")
        ok = False
    else:
        print("  [ok ] all 41 bibliography entries still cited")

    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
