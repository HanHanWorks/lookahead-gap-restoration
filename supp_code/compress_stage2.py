"""Compression stage 2: long sentences, section scaffolding, and the appendices.

Same contract as stage 1: exact literal pairs, unique-match assertion, and no removal of a
number, qualifier, assumption, proof step, scope condition or cross-reference.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MS = ROOT / "SEGAN_manuscript_revised_2026-09-13.md"

doc = MS.read_text(encoding="utf-8")
before = len(doc.split())
FAILURES: list[str] = []


def rep(old: str, new: str, note: str) -> None:
    global doc
    n = doc.count(old)
    if n != 1:
        FAILURES.append(f"[x{n}] {note}")
        return
    doc = doc.replace(old, new)


# ---------------------------------------------------------------- section scaffolding
rep(
    "Section 1 identified the attribution gap: reported gains are not assigned to the "
    "mechanism that produces them. This section supplies the assignment. The construction is "
    "elementary, but it is what makes the later results interpretable, because every comparison "
    "in Section 5 is stated in its terms.",
    "Section 1 identified the attribution gap: reported gains are not assigned to the mechanism "
    "that produces them. This section supplies the assignment. The construction is elementary, "
    "but every comparison in Section 5 is stated in its terms.",
    "3 intro",
)

rep(
    "This section is the theoretical core. Sections 4.1--4.2 remove the terminal term from the "
    "ordering problem, and Section 4.3 makes the full-horizon optimum exactly computable and "
    "defines the lookahead gap.",
    "This section is the theoretical core. Sections 4.1--4.2 remove the terminal term from the "
    "ordering problem and Section 4.3 makes the full-horizon optimum exactly computable, "
    "defining the lookahead gap.",
    "4 intro",
)

rep(
    "Every result so far conditions on one capacity rule, which Section 2.2 stated explicitly "
    "for that reason. This section asks what happens to the criterion when the rule changes, "
    "because a value that exists only under one convention would be a property of the "
    "convention.",
    "Every result so far conditions on one capacity rule, which Section 2.2 stated explicitly "
    "for that reason. This section asks what happens when the rule changes, because a value "
    "that exists only under one convention is a property of the convention.",
    "6 intro",
)

# ---------------------------------------------------------------- 1.1 / 1.5
rep(
    "Of the four, the first two are named by the decomposition of Section 3, the third is a "
    "property of the condition and is addressed by the pre-check of Section 2.6, and the fourth "
    "is a property of the comparison and is addressed by the reporting standard of Section 7.",
    "Of the four, the first two are named by the decomposition of Section 3, the third is a "
    "property of the condition, addressed by the pre-check of Section 2.6, and the fourth a "
    "property of the comparison, addressed by the reporting standard of Section 7.",
    "1.1 four sources",
)

rep(
    "**Learned restoration prioritization.** Reinforcement learning has been applied to "
    "restoration ordering across distribution and transmission systems, including graph-based "
    "outage management [1], multi-agent load restoration with invalid-action masking [2], mixed "
    "discrete-continuous actions over tie switches and distributed resources [3], "
    "curriculum-based learning for critical-load restoration [4], graph-sequence scheduling [5], "
    "entropy-driven coordination of storage with microgrids [6] and heterogeneous multi-agent "
    "proximal policy optimization for distribution-system restoration [7]; surveys converge on "
    "the absence of standardised benchmarks and reproducibility [8,9].",
    "**Learned restoration prioritization.** Reinforcement learning has been applied to "
    "restoration ordering across distribution and transmission systems: graph-based outage "
    "management [1], multi-agent load restoration with invalid-action masking [2], mixed "
    "discrete-continuous actions over tie switches and distributed resources [3], "
    "curriculum-based learning for critical-load restoration [4], graph-sequence scheduling [5], "
    "entropy-driven coordination of storage with microgrids [6] and heterogeneous multi-agent "
    "PPO for distribution-system restoration [7]; surveys converge on the absence of "
    "standardised benchmarks and reproducibility [8,9].",
    "1.5 learned branch",
)

# ---------------------------------------------------------------- 4.3
rep(
    "*Proof.* Every ordering of $B_0$ corresponds to a maximal chain $\\emptyset \\subset S_1 "
    "\\subset \\cdots \\subset S_m = B_0$, and the transient sum along that chain equals "
    "$f(\\emptyset)$ as evaluated by backward induction, since $f$ satisfies the principle of "
    "optimality on the chain lattice. Conversely, each maximal chain is realized by at least one "
    "ordering, and following the arg-max branches of $f$ from $\\emptyset$ constructs one. The "
    "state count is the number of subsets of $B_0$, the transition count at most $m$ per state, "
    "and each transition costs one service evaluation. $\\square$",
    "*Proof.* Every ordering of $B_0$ corresponds to a maximal chain $\\emptyset \\subset S_1 "
    "\\subset \\cdots \\subset S_m = B_0$, along which the transient sum equals "
    "$f(\\emptyset)$ by backward induction, since $f$ satisfies the principle of optimality on "
    "the chain lattice. Conversely, each maximal chain is realized by at least one ordering, "
    "which following the arg-max branches of $f$ from $\\emptyset$ constructs. The state count "
    "is the number of subsets of $B_0$, the transition count at most $m$ per state, and each "
    "transition costs one service evaluation. $\\square$",
    "4.3 proof",
)

# ---------------------------------------------------------------- 4.6
rep(
    "Step 1 is cheap: on the instances used here the dynamic program costs at most a few "
    "thousand service evaluations (4,096 at the largest), a median of **8 s** of wall-clock "
    "time reaching **1.4 min** on the heaviest instance, and no simulator rollouts, so the "
    "procedure is usable as a benchmark design tool — which is how Section 5.1 first applies it.",
    "Step 1 is cheap: on these instances the dynamic program costs at most a few thousand "
    "service evaluations (4,096 at the largest), a median of **8 s** of wall-clock time reaching "
    "**1.4 min** on the heaviest instance, and no simulator rollouts, so the procedure is usable "
    "as a benchmark design tool — which is how Section 5.1 first applies it.",
    "4.6 cost",
)

# ---------------------------------------------------------------- 5.4
rep(
    "Under the unified rule both regimes show a positive gap in **11 of 12 conditions**: four of "
    "the six moderate conditions moved from an apparent zero to values among the largest in the "
    "uncoupled study, up to 15.685 on IEEE 118 moderate 1.50 and 11.594 on IEEE 300 moderate "
    "1.15, while IEEE 300 moderate 1.50 stayed at zero. The largest uncoupled value overall is "
    "16.611, on IEEE 118 severe 1.50, which the old rule already exposed.",
    "Under the unified rule both regimes show a positive gap in **11 of 12 conditions**: four of "
    "the six moderate conditions moved from an apparent zero to values among the largest in the "
    "uncoupled study, up to 15.685 on IEEE 118 moderate 1.50 and 11.594 on IEEE 300 moderate "
    "1.15, while IEEE 300 moderate 1.50 stayed at zero. The largest uncoupled value overall, "
    "16.611 on IEEE 118 severe 1.50, the old rule already exposed.",
    "5.4 moderate",
)

# ---------------------------------------------------------------- 5.6
rep(
    "The budget axis is **non-monotonic**, and the $B = 4$ column shows why. With four "
    "reconnections against roughly twelve broken key lines the problem degenerates towards "
    "*selecting* a subset rather than *ordering* one, and greedy selection is already "
    "near-optimal for the monotone structure of the objective; consequently no instance in the "
    "sample is long-range at $B = 4$.",
    "The budget axis is **non-monotonic**, and the $B = 4$ column shows why: with four "
    "reconnections against roughly twelve broken key lines the problem degenerates towards "
    "*selecting* a subset rather than *ordering* one, and greedy selection is already "
    "near-optimal for the monotone structure of the objective, so no instance in the sample is "
    "long-range at $B = 4$.",
    "5.6 non-monotonic",
)

rep(
    "The envelope check of Appendix B holds on the coupled instances of this sweep as well, so "
    "the non-monotonicity is a property of the problem rather than an artefact of the solver. "
    "The budget is therefore a design parameter with a non-monotone effect, and a phase diagram "
    "rather than a single-point comparison against a legacy configuration is the appropriate "
    "instrument for choosing it.",
    "The envelope check of Appendix B holds on the coupled instances of this sweep as well, so "
    "the non-monotonicity is a property of the problem rather than an artefact of the solver. "
    "The budget is therefore a design parameter with a non-monotone effect, and a phase diagram "
    "rather than a single-point comparison against a legacy configuration is the right "
    "instrument for choosing it.",
    "5.6 design parameter",
)

# ---------------------------------------------------------------- 5.8
rep(
    "On the 200-bus Illinois system the uncoupled gap is positive in **six of six** conditions, "
    "with a maximum of 71.47 and a median depth-to-90% of 4.0--7.5; that maximum is 4.3 times "
    "the largest uncoupled value on either IEEE system, consistent with the Illinois system's "
    "higher action-set flow share. Under the budget $B = 6$ the three severe conditions of the "
    "same system all carry a positive gap, with a maximum of 133.02 and a median depth-to-90% of "
    "2.0--4.0.",

    "On the 200-bus Illinois system the uncoupled gap is positive in **six of six** conditions, "
    "with a maximum of 71.47 and a median depth-to-90% of 4.0--7.5, 4.3 times the largest "
    "uncoupled value on either IEEE system and consistent with its higher action-set flow share. "
    "Under the budget $B = 6$ the three severe conditions all carry a positive gap, with a "
    "maximum of 133.02 and a median depth-to-90% of 2.0--4.0.",
    "5.8 Illinois",
)

# ---------------------------------------------------------------- 6.1
rep(
    "The standard cases carry a **uniform synthetic thermal rating**: on the IEEE 118-bus system "
    "every line's rating evaluates to 9900 MVA, against a total demand of 4242 MW and an "
    "installed generation capacity of 9161 MW. Under those ratings no line is ever binding, so "
    "the optimal power flow serves the entire demand on both the intact and the fully damaged "
    "network and the gap is identically zero. That zero is not evidence that the phenomenon is "
    "absent; it is evidence that the transplanted model has no active constraint.",

    "The standard cases carry a **uniform synthetic thermal rating**: on the IEEE 118-bus system "
    "every line's rating evaluates to 9900 MVA, against 4242 MW of demand and 9161 MW of "
    "installed generation. No line is then ever binding, so the optimal power flow serves the "
    "entire demand on both the intact and the fully damaged network and the gap is identically "
    "zero — not evidence that the phenomenon is absent, but evidence that the transplanted model "
    "has no active constraint.",
    "6.1 uniform rating",
)

rep(
    "At the main protocol's parameters the floor is not the mechanism: only **17 of the 173** "
    "lines sit on the 8.48 MW floor at $\\kappa = 1.25$, and the counts at the other margins are "
    "similar (20 at $\\kappa = 1.15$, 14 at $\\kappa = 1.50$). The remaining ratings span 8.5 MW "
    "to 562 MW, so the transfer capability of the transplanted network rests on a small number "
    "of lightly loaded lines, and the linear program fails to converge under every solver "
    "available. Relaxing the floor until it converges removes the binding structure and the gap "
    "returns to zero.",

    "At the main protocol's parameters the floor is not the mechanism: only **17 of the 173** "
    "lines sit on the 8.48 MW floor at $\\kappa = 1.25$ (20 at $\\kappa = 1.15$, 14 at "
    "$\\kappa = 1.50$). The remaining ratings span 8.5 MW to 562 MW, so the transfer capability "
    "rests on a few lightly loaded lines and the linear program fails to converge under every "
    "solver available; relaxing the floor until it converges removes the binding structure and "
    "the gap returns to zero.",
    "6.1 floor count",
)

# ---------------------------------------------------------------- 6.3
rep(
    "A benchmark adopting uniform physical ratings is testing a network with substantial unused "
    "transfer capability on every path — the installed generation exceeds demand by a factor of "
    "2.2 on the IEEE 118-bus system — so no line is binding and no ordering can matter, and a "
    "modeller can verify that before choosing the convention.",
    "A benchmark adopting uniform physical ratings tests a network with substantial unused "
    "transfer capability on every path — on the IEEE 118-bus system the installed generation "
    "exceeds demand by a factor of 2.2 — so no line is binding and no ordering can matter, which "
    "a modeller can verify before choosing the convention.",
    "6.3 over-built",
)

# ---------------------------------------------------------------- 7
rep(
    "Read against the cheapest non-learned rule that could replace it — the electrical-priority "
    "rule, at 0.0006--0.0007 ms per decision — the screened learned ranker is **48--59 times "
    "slower**, and the one-step exact rule is **290--1236 times slower** on the mean than the "
    "screened ranker while being 1.6--3.6 times faster on the median. Three conventions follow:",
    "Read against the cheapest non-learned rule that could replace it — the electrical-priority "
    "rule, at 0.0006--0.0007 ms per decision — the screened learned ranker is **48--59 times "
    "slower**, and the one-step exact rule is **290--1236 times slower** on the mean while being "
    "1.6--3.6 times faster on the median. Three conventions follow:",
    "7 read against",
)

rep(
    "Convention 3 is why this section belongs in this paper rather than being a footnote. Exact "
    "solvability is a property of the structure of the functional and of $m \\le 12$, "
    "established in Section 4.3 for the maximum-flow class; whether the gap is *non-zero* is a "
    "separate property, and it is the capacity rule of Section 6 that decides it. Timing and "
    "solvability are therefore the two halves of one reporting question, and the boundary "
    "between them is what a latency claim has to state.",

    "Convention 3 is why this section belongs in the paper rather than a footnote. Exact "
    "solvability is a property of the structure of the functional and of $m \\le 12$, "
    "established in Section 4.3 for the maximum-flow class; whether the gap is *non-zero* is "
    "separate, and the capacity rule of Section 6 decides it. Timing and solvability are "
    "therefore two halves of one reporting question, and the boundary between them is what a "
    "latency claim has to state.",
    "7 convention 3",
)

# ---------------------------------------------------------------- 8.4
rep(
    "The most transferable result is the sensitivity of the gap to how instances are selected. "
    "The incidence of a positive gap changed from 7 of 12 conditions to 11 of 12 when the rule "
    "selecting instances was made protocol-independent, and four of the six moderate conditions "
    "moved from an apparent zero to values among the largest in the uncoupled study, up to "
    "15.685 and 11.594, the second and third largest values overall. A benchmark's "
    "*instance-selection rule* is therefore not a neutral choice: changing it alone moved the "
    "reported incidence of the phenomenon by more than any single change of system, parameter or "
    "policy was observed to make in this study.",

    "The most transferable result is the sensitivity of the gap to how instances are selected. "
    "The incidence of a positive gap changed from 7 of 12 conditions to 11 of 12 when the rule "
    "selecting instances was made protocol-independent, and four of the six moderate conditions "
    "moved from an apparent zero to values among the largest in the uncoupled study, up to "
    "15.685 and 11.594, the second and third largest overall. A benchmark's *instance-selection "
    "rule* is therefore not a neutral choice: changing it alone moved the reported incidence "
    "further than any single change of system, parameter or policy did in this study.",
    "8.4 transferable",
)

# ---------------------------------------------------------------- 9
rep(
    "Capacities are synthesised from a base-case direct-current flow, so the model captures "
    "transport capacity rather than thermal security, voltage limits or losses, and Section 6 "
    "shows that the criterion's non-triviality depends on the capacity rule: the results are "
    "stated for the utilisation-proportional rule with a 0.2% floor, and under uniform thermal "
    "ratings or a 5% floor the gap vanishes identically. Resource coupling is a cardinality "
    "constraint that omits crew travel times, switching sequences, protection behaviour and time "
    "windows, all of which would change the terminal term in ways the present reduction does not "
    "model, and transfer to a full alternating-current security-constrained model is not "
    "established here.",

    "Capacities are synthesised from a base-case direct-current flow, so the model captures "
    "transport capacity rather than thermal security, voltage limits or losses; Section 6 shows "
    "the criterion's non-triviality depends on the capacity rule, since the results are stated "
    "for the utilisation-proportional rule with a 0.2% floor and the gap vanishes identically "
    "under uniform thermal ratings or a 5% floor. Resource coupling is a cardinality constraint "
    "that omits crew travel times, switching sequences, protection behaviour and time windows, "
    "all of which would change the terminal term in ways this reduction does not model, and "
    "transfer to a full alternating-current security-constrained model is not established.",
    "9 service model",
)

rep(
    "**Three boundaries of the reported evidence.** The depth profile is estimated on severe "
    "conditions alone, because a positive gap occurs only in the six severe condition groups of "
    "the two IEEE systems, so the profiles of Table 6 and Figure 5 are means over 22 budgeted "
    "and 44 uncoupled instances and it is not established whether a committed plan needs the "
    "same foresight on a moderate condition. The criterion is one-directional, so a vanishing "
    "gap does not certify that a condition is free of ordering information; only a failed "
    "pre-check certifies that, and the two diagnoses therefore disagree on two of the eight "
    "condition groups, with the paper stating for each group which one applies.",

    "**Three boundaries of the reported evidence.** The depth profile is estimated on severe "
    "conditions alone, since a positive gap occurs only in the six severe condition groups of "
    "the two IEEE systems; Table 6 and Figure 5 are means over 22 budgeted and 44 uncoupled "
    "instances, and whether a committed plan needs the same foresight on a moderate condition is "
    "not established. The criterion is one-directional, so a vanishing gap does not certify that "
    "a condition is free of ordering information; only a failed pre-check certifies that, and "
    "the two diagnoses disagree on two of the eight condition groups, with the paper stating "
    "which applies to each.",
    "9 boundaries",
)

rep(
    "The released counterfactual gain column, the brute-force validation table of the coupled "
    "recursion, the optimal-power-flow transplant diagnosis of Section 6.1, the reconciliation "
    "of the episode-record column with the instance rule, and the instance-selection constant "
    "remain outstanding release items; the first and the last affect no reported number, and the "
    "third is quoted only as a count recomputed locally. All are listed in Appendix D. Timings "
    "exclude environment advancement, and every measurement reported here comes from one 16-core "
    "host with a single NVIDIA RTX 4090 D, running the library versions of Appendix C; no second "
    "platform is reported, so the comparison of timing boundaries is a within-machine comparison "
    "and its absolute values should not be transferred to other hardware. Memory and "
    "operating-system build were not recorded in the environment snapshot.",

    "Five items remain outstanding release items, all listed in Appendix D: the counterfactual "
    "gain column, the brute-force validation table of the coupled recursion, the "
    "optimal-power-flow transplant diagnosis of Section 6.1, the reconciliation of the "
    "episode-record column with the instance rule, and the instance-selection constant. The "
    "first and the last affect no reported number, and the third is quoted only as a count "
    "recomputed locally. Timings exclude environment advancement, and every measurement comes "
    "from one 16-core host with a single NVIDIA RTX 4090 D running the library versions of "
    "Appendix C; no second platform is reported, so the boundary comparison is within-machine "
    "and its absolute values should not be transferred to other hardware. Memory and "
    "operating-system build were not recorded in the environment snapshot.",
    "9 release gaps",
)

# ---------------------------------------------------------------- 10
rep(
    "For the class of benchmarks whose service functional depends only on the set of broken "
    "lines, the full-horizon optimum is available by dynamic programming over subsets, costing "
    "$O(2^m m)$ service evaluations and no simulation. The resulting lookahead gap is an exact "
    "upper bound on the benefit of any prioritization policy over a one-step exact rule, and it "
    "is zero exactly when that rule is optimal.",
    "For benchmarks whose service functional depends only on the set of broken lines, the "
    "full-horizon optimum is available by dynamic programming over subsets, costing $O(2^m m)$ "
    "service evaluations and no simulation. The resulting lookahead gap is an exact upper bound "
    "on the benefit of any prioritization policy over a one-step exact rule, and is zero exactly "
    "when that rule is optimal.",
    "10 gap",
)

# ---------------------------------------------------------------- Appendix B / D / E
rep(
    "The first four rows are released and were re-checked when this revision was prepared. The "
    "last two are not. The paper quotes no numerical agreement for the fifth: the coupled "
    "variant of Proposition 2 rests on the envelope row, which constrains it from both sides "
    "without enumerating it, and running the pending check would change no reported number if it "
    "passes and the budgeted entries of Table 5 if it does not. The sixth would change no "
    "reported number either way, because Section 6.1 uses its counts only to explain why the "
    "transplant is not comparable rather than to support a result.",

    "The first four rows are released and were re-checked when this revision was prepared; the "
    "last two are not. No numerical agreement is quoted for the fifth: the coupled variant of "
    "Proposition 2 rests on the envelope row, which constrains it from both sides without "
    "enumerating it, and running that check would change no reported number if it passes and the "
    "budgeted entries of Table 5 if it does not. The sixth would change no reported number "
    "either way, because Section 6.1 uses its counts only to explain why the transplant is not "
    "comparable.",
    "Appendix B closing",
)

rep(
    "**Computed in this paper and not yet released.** Three items are used above and are marked "
    "rather than omitted, because a reader should be able to see what is missing: the "
    "counterfactual column $u_t(a^\\rho_t)$ that the value form of Eq. (5) requires (Section "
    "3.5); the exhaustive enumeration over ordered $B$-subsets that would validate the coupled "
    "recursion directly rather than through its envelope (`repro/bruteforce_validation.log`, "
    "command, seed and required fields recorded, run not yet executed); and the "
    "optimal-power-flow transplant diagnosis of Section 6.1, whose counts were recomputed "
    "locally for this revision without a released log. A fourth item is a reconciliation rather "
    "than a measurement: the `n_broken_key_lines` column of the frozen episode records does "
    "not reproduce the instance rule of Section 5.0, and the rule is stated in terms of the "
    "$K$ of the depth-curve artifacts, which are the files it is applied to.",

    "**Computed in this paper and not yet released.** Three items are marked rather than "
    "omitted, so that a reader can see what is missing: the counterfactual column "
    "$u_t(a^\\rho_t)$ that the value form of Eq. (5) requires (Section 3.5); the exhaustive "
    "enumeration over ordered $B$-subsets that would validate the coupled recursion directly "
    "rather than through its envelope (`repro/bruteforce_validation.log`, with the command, "
    "seed and required fields recorded and the run not yet executed); and the optimal-power-flow "
    "transplant diagnosis of Section 6.1, whose counts were recomputed locally for this revision "
    "without a released log. A fourth item is a reconciliation rather than a measurement: the "
    "`n_broken_key_lines` column of the frozen episode records does not reproduce the instance "
    "rule of Section 5.0, which is stated in terms of the $K$ of the depth-curve artifacts that "
    "the rule is applied to.",
    "Appendix D outstanding",
)

rep(
    "The search supporting Section 1.5 was run over four deliberately opposed perspectives: the "
    "mainstream RL-for-restoration school, the classical restoration-ordering school, the "
    "methodological-critique school, and adjacent theory. Keywords were grouped by research "
    "question and narrowed in a second round by the method and dataset names returned in the "
    "first. **Every reference was verified against a real source before inclusion**, using a "
    "two-step protocol: the work is located, then its bibliographic fields are confirmed from an "
    "independent record (publisher page, Crossref, arXiv, or a second index). Works whose "
    "metadata could not be confirmed were excluded rather than approximated, and 41 works are "
    "cited.",

    "The search supporting Section 1.5 ran over four deliberately opposed perspectives: the "
    "mainstream RL-for-restoration school, the classical restoration-ordering school, the "
    "methodological-critique school, and adjacent theory. Keywords were grouped by research "
    "question and narrowed in a second round by the method and dataset names returned in the "
    "first. **Every reference was verified against a real source before inclusion**: the work is "
    "located, then its bibliographic fields are confirmed from an independent record (publisher "
    "page, Crossref, arXiv, or a second index). Works whose metadata could not be confirmed were "
    "excluded rather than approximated, and 41 works are cited.",
    "Appendix E protocol",
)

if FAILURES:
    print("ABORTED:")
    for f in FAILURES:
        print("   ", f)
    sys.exit(1)

MS.write_text(doc, encoding="utf-8")
sec = doc[doc.index("## 1. Introduction"):doc.index("## Appendix A.")]
print(f"stage 2 written: {before} -> {len(doc.split())} words  ({len(doc.split())-before:+d})")
print(f"  §1-§10 now: {len(sec.split())}")
