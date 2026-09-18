"""Compression stage 1: Sections 1--3 and 5.

Every edit is an exact literal pair with a unique-match assertion.  Nothing is removed
that carries a number, a qualifier, an assumption, a proof step, a scope condition or a
cross-reference; the cuts are (i) sentences that restate values already carried by a
table, (ii) hedging and connective padding, and (iii) the long disclosure paragraphs
added in the previous revision, tightened without dropping a fact.

A pre-compression snapshot is kept at reviews/prev/SEGAN_manuscript_PRE_COMPRESSION2_2026-09-14.md.
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


# =====================================================================================
# 1.1
# =====================================================================================
rep(
    "Machine learning has been applied to this ordering problem at a steady rate, and the "
    "typical study reports that its learned policy outperforms a set of reference rules on "
    "one or two published test systems.",
    "Learned policies are increasingly proposed for this ordering, and the typical study "
    "reports that they outperform a set of reference rules on one or two published test "
    "systems.",
    "1.1 p1",
)

rep(
    "The candidates are the learned ordering, the admissibility screen that decides whether an "
    "action is legal, the aggregate metric, and the choice of reference. The distinction is "
    "not academic, because a policy whose gain comes entirely from refusing illegal actions "
    "is not evidence that learning orders anything.",
    "The candidates are the learned ordering, the admissibility screen, the aggregate metric, "
    "and the choice of reference; the distinction is not academic, because a gain that comes "
    "entirely from refusing illegal actions is not evidence that learning orders anything.",
    "1.1 candidates",
)

rep(
    "The second question is **answerability**. If at a given decision step every admissible "
    "action yields the same immediate benefit, then no ordering is better than any other at "
    "that step, and averages and significance tests computed over such steps describe the "
    "metric rather than the policies.",
    "The second is **answerability**: if every admissible action yields the same immediate "
    "benefit at a step, no ordering is better than any other there, and averages and "
    "significance tests computed over such steps describe the metric rather than the policies.",
    "1.1 answerability",
)

rep(
    "This paper takes the position that both questions are answered by quantities that require "
    "no policy to be trained: the answerability question by an exactly computable pre-check, "
    "which is therefore available *before* training, and the attribution question by an exact "
    "decomposition of a policy that has been evaluated. We develop both and use them to "
    "interpret an experimental programme on three public test systems. The resulting claims "
    "are about the structure of the prioritization problem, not the performance of any "
    "particular learned policy.",
    "Both questions are answered by quantities that require no policy to be trained: "
    "answerability by an exactly computable pre-check, available *before* training, and "
    "attribution by an exact decomposition of a policy that has been evaluated. We develop "
    "both and use them to interpret an experimental programme on three public test systems. "
    "The claims are about the structure of the prioritization problem, not the performance of "
    "any particular learned policy.",
    "1.1 position",
)

# =====================================================================================
# 1.2 / 1.3
# =====================================================================================
rep(
    "A value that requires an intractable plan is not deployable, and a value that exists only "
    "under one capacity convention is a property of the convention as much as of the grid.",
    "A value requiring an intractable plan is not deployable, and one that exists only under a "
    "single capacity convention is a property of the convention as much as of the grid.",
    "1.2 L3",
)

rep(
    "The value of lookahead is naturally the difference between the best achievable horizon "
    "objective and the objective of the *one-step exact rule*, which repeatedly reconnects the "
    "admissible line of greatest immediate recovery.",
    "The value of lookahead is the difference between the best achievable horizon objective and "
    "that of the *one-step exact rule*, which repeatedly reconnects the admissible line of "
    "greatest immediate recovery.",
    "1.3 C1",
)

rep(
    "The service functional here is a maximum-flow construct whose capacities are synthesised "
    "from a base-case direct-current power flow. Whether the resulting headroom reflects the "
    "power system or merely the capacity convention is not determined by the benchmark itself; "
    "establishing it requires varying the convention at fixed instances.",
    "The service functional is a maximum-flow construct whose capacities are synthesised from a "
    "base-case direct-current power flow. Whether the resulting headroom reflects the power "
    "system or merely the capacity convention is not settled by the benchmark itself; "
    "establishing it requires varying the convention at fixed instances.",
    "1.3 C3",
)

# =====================================================================================
# 1.4 / 1.5
# =====================================================================================
rep(
    "any latency figure should be accompanied by the cheapest non-learned rule that could "
    "replace the learned one, and the measurement boundary should be stated. The boundary "
    "matters: the same trained network is measured 2.5--3.1 times slower when a deep-learning "
    "library's prediction wrapper is included than when a bare forward pass is timed.",
    "any latency figure should name the cheapest non-learned rule that could replace the "
    "learned one, and state the measurement boundary. The boundary matters: the same network is "
    "measured 2.5--3.1 times slower with a deep-learning library's prediction wrapper inside "
    "the timed region than with a bare forward pass.",
    "1.4 support",
)

rep(
    "Two features matter here. The reported advantage of learning is conditional on the "
    "reference, holding against greedy, $\\varepsilon$-greedy, Boltzmann or evolutionary "
    "baselines, and where an exact solver is included the learned policy is generally better "
    "in time and worse in quality [6]. And the primary evidence is an aggregate metric over "
    "one or two systems, with the component that produced the gain left unisolated.",

    "Two features matter. The reported advantage is conditional on the reference — greedy, "
    "$\\varepsilon$-greedy, Boltzmann or evolutionary baselines — and where an exact solver is "
    "included the learned policy is generally better in time and worse in quality [6]; and the "
    "primary evidence is an aggregate metric over one or two systems, with the gain left "
    "unisolated.",
    "1.5 learned branch",
)

rep(
    "Its own flagship result, however, is a heuristic claimed to be near-optimal and a thousand "
    "times faster [12], which weakens the absoluteness of the *heuristics are insufficient* "
    "position and suggests the operating axis is the compute--quality trade-off rather than "
    "policy quality.",
    "Its flagship result, however, is a heuristic claimed to be near-optimal and a thousand "
    "times faster [12], which weakens the *heuristics are insufficient* position and suggests "
    "the operating axis is compute--quality rather than policy quality.",
    "1.5 classical branch",
)

rep(
    "This paper supplies the check, and a structured search confirmed six specific gaps "
    "(Appendix E). No prior work treats the capacity or constraint *rule* of a service model as "
    "the thing that decides whether a positive gap exists [30 is the nearest analogue, for a "
    "different object]. None defines an exactly computable myopic-versus-optimal gap for power "
    "restoration [16 is the nearest, and is approximate]. None distinguishes a committed "
    "depth-$k$ profile from a rolling controller's realised profile. None applies the "
    "minimum-latency theory of [34,35] to restoration ordering. And none proposes a "
    "*decision-landscape* identifiability criterion, since the existing literature asks whether "
    "observations or designs can separate parameters [26--29] rather than whether an "
    "optimisation landscape contains capturable benefit. And none mounts a methodological "
    "critique of timing comparisons within the restoration-RL literature, which is where the "
    "reporting standard of Section 7 has to argue from first principles.",

    "This paper supplies the check, and a structured search confirmed six specific gaps "
    "(Appendix E): no prior work treats the capacity or constraint *rule* of a service model as "
    "the thing that decides whether a positive gap exists [30 is the nearest analogue, for a "
    "different object]; none defines an exactly computable myopic-versus-optimal gap for power "
    "restoration [16 is the nearest, and is approximate]; none distinguishes a committed "
    "depth-$k$ profile from a rolling realised profile; none applies the minimum-latency theory "
    "of [34,35] to restoration ordering; none proposes a *decision-landscape* identifiability "
    "criterion, the existing literature asking whether observations or designs can separate "
    "parameters [26--29]; and none mounts a methodological critique of timing comparisons, "
    "which is where the reporting standard of Section 7 has to argue from first principles.",
    "1.5 gaps",
)

# =====================================================================================
# 2.2 / 2.3 / 2.4 / 2.6
# =====================================================================================
rep(
    "Eq. (2) ties each line's capacity to its base-case utilisation, with a floor preventing a "
    "lightly loaded line from being closed outright. Section 6 varies this rule; Table 1 records "
    "the parameters of both configurations.",
    "Eq. (2) ties each line's capacity to its base-case utilisation, the floor preventing a "
    "lightly loaded line from being closed outright. Section 6 varies this rule; Table 1 "
    "records both configurations.",
    "2.2 tail",
)

rep(
    "Moving the effective action at any later position $t' > t$ into an ineffective $t$ and "
    "shifting the intervening values left leaves every shifted value unchanged, places at $t$ a "
    "value at least as large as the one it displaces, and fixes the horizon, so the trapezoidal "
    "area does not decrease; repeating until no ineffective position remains proves the "
    "inequality, and the equality condition follows because the repetition is strictly smaller "
    "than the value it displaces whenever the chain has not terminated. $\\square$",

    "Moving the effective action at any later position into an ineffective one and shifting the "
    "intervening values left leaves every shifted value unchanged, places at that position a "
    "value at least as large as the one it displaces, and fixes the horizon, so the trapezoidal "
    "area does not decrease; repeating until no ineffective position remains proves the "
    "inequality. Equality follows because each repetition is strictly smaller than the value it "
    "displaces whenever the chain has not terminated. $\\square$",
    "2.3 Lemma 0 proof",
)

rep(
    "that is, the policy executes the first action in $\\rho$'s order among those the screen "
    "admits; the symbol $\\circ$ is retained as shorthand for this selection, which is well "
    "defined because the screen returns an indicator set rather than a single action.",
    "; $\\circ$ is shorthand for this selection, well defined because the screen returns an "
    "indicator set rather than a single action.",
    "2.4 composition",
)

rep(
    "The thresholds are stated because a criterion of this kind is only as useful as its cut-off "
    "is explicit; they were chosen so that the two diagnostics agree on the cases examined below "
    "and separate those cases widely (Section 5.1).",
    "The thresholds are stated because a criterion is only as useful as its cut-off is explicit; "
    "they were chosen so that the two diagnostics agree on the cases below and separate them "
    "widely (Section 5.1).",
    "2.6 thresholds",
)

# =====================================================================================
# 3.4 / 3.5
# =====================================================================================
rep(
    "Two factors are varied deliberately, the training objective and the presence of the screen; "
    "a third varies with the objective and is not controlled, because each objective is trained "
    "in the environment class built for it, so the training environment is a confound the reader "
    "should carry.",
    "Two factors are varied deliberately, the training objective and the presence of the screen; "
    "a third is not controlled, because each objective is trained in the environment class "
    "built for it, so the training environment is a confound the reader should carry.",
    "3.4 confound",
)

rep(
    "The three escape routes of Corollary 4 map onto the same split. Route (a) leaves neither "
    "term computable and is open (Section 8.3). Route (b) makes the terminal set a decision, "
    "which is a failure of Lemma 1 rather than of Eq. (5), and it is the route the budget of "
    "Sections 5.4 and 5.6 realises. Route (c) is the case in which $C_t$ rather than $R_t$ "
    "carries the stepwise regret, and it is measured in Section 5.3. Only two of the four "
    "candidate sources are therefore quantities of Eq. (5), which is the sense in which this "
    "section is a language for reporting a comparison rather than a complete causal account of "
    "one.",

    "The three escape routes of Corollary 4 map onto the same split: (a) leaves neither term "
    "computable and is open (Section 8.3); (b) makes the terminal set a decision, a failure of "
    "Lemma 1 rather than of Eq. (5), and is the route the budget of Sections 5.4 and 5.6 "
    "realises; and (c) is the case in which $C_t$ rather than $R_t$ carries the regret, and it "
    "is measured in Section 5.3. Only two of the four candidate sources are therefore quantities "
    "of Eq. (5), which is the sense in which this section is a language for reporting a "
    "comparison rather than a complete causal account of one.",
    "3.5 escape routes",
)

# =====================================================================================
# 5.0
# =====================================================================================
rep(
    "Two axes are kept apart in what follows. **Protocol** is the data-generation "
    "configuration, legacy or main. **Regime** is the presence or absence of a reconnection "
    "budget, which is imposed on the same instances rather than generating new ones. A statement "
    "qualified as *budgeted* or *uncoupled* is therefore a statement about a regime and not "
    "about a protocol, and the two axes are independent. One released column does not support "
    "the instance rules below: `n_broken_key_lines` in the frozen episode records is zero on "
    "5,749 of the 9,600 main-protocol episodes, all of which nonetheless have unserved load, so "
    "it cannot be used to reconstruct the sample. The rules are stated in terms of $K$ as "
    "recorded in the depth-curve artifacts, which are the files they are applied to; "
    "reconciling the episode column with $K$ is an outstanding release item (Appendix D).",

    "Two axes are kept apart below. **Protocol** is the data-generation configuration, legacy or "
    "main. **Regime** is the presence or absence of a reconnection budget, imposed on the same "
    "instances rather than generating new ones, so a statement qualified as *budgeted* or "
    "*uncoupled* is about a regime and not a protocol. One released column does not support the "
    "instance rules: `n_broken_key_lines` is zero on 5,749 of the 9,600 main-protocol episodes, "
    "all of which nonetheless have unserved load, so the sample cannot be reconstructed from it. "
    "The rules are stated in terms of $K$ as recorded in the depth-curve artifacts, the files "
    "they are applied to; reconciling the episode column with $K$ is an outstanding release item "
    "(Appendix D).",
    "5.0 axes",
)

# =====================================================================================
# 5.1
# =====================================================================================
rep(
    "The two diagnostics do not carry the same weight in that verdict. Across the 96 "
    "configurations of the sweep the uniqueness diagnostic stays at or below 0.50 for both IEEE "
    "118-bus groups, whereas the second diagnostic sits close to its 0.85 cut-off for the severe "
    "group: the sweep gives 0.995 and 0.781 at $\\kappa = 1.15$ for the moderate and severe "
    "groups, against the **1.00** and **0.87** of Table 3 measured on the evaluation protocol. "
    "Because 0.85 falls between those two measurements of one and the same configuration, the "
    "verdict for that group rests on the uniqueness diagnostic, which fails by a wide margin in "
    "both sources; the second diagnostic is reported alongside the first rather than relied on.",

    "The two diagnostics do not carry the same weight in that verdict. Across the 96 "
    "configurations of the sweep the uniqueness diagnostic stays at or below 0.50 for both IEEE "
    "118-bus groups, whereas the second sits close to its 0.85 cut-off for the severe group: the "
    "sweep gives 0.995 and 0.781 at $\\kappa = 1.15$, against the **1.00** and **0.87** of "
    "Table 3 on the evaluation protocol. Since 0.85 falls between two measurements of one and "
    "the same configuration, the verdict for that group rests on the uniqueness diagnostic, "
    "which fails widely in both sources; the second is reported alongside rather than relied on.",
    "5.1 second diagnostic",
)

# =====================================================================================
# 5.3
# =====================================================================================
rep(
    "**Table 4.** Attribution of stepwise regret, computed from "
    "`04_evaluation_new_protocol/stepwise_oracle.csv` (147,132 step records; the per-arm entries "
    "are step counts and are not sums over seeds, so they must not be added down the column). "
    "Recorded decisions differ by arm because the screens change which steps are recorded; no "
    "arm contains a step at which the admissible set is empty, so each arm's decomposition is "
    "defined on its own recorded steps. $C_t$ is the censoring rate of Eq. (5a) and "
    "$C^{\\mathrm{screen}}_t$ the conditional screen override of Section 3.3. *Regret share from "
    "ranking* is the fraction of $\\sum_t \\delta_t$ accounted for by the steps on which a "
    "ranking error occurred; it is **not** the share of the value form of Eq. (5), which needs "
    "$u_t(a^\\rho_t)$ and is therefore not computable on this release (Section 3.5). The "
    "Spearman entry is a mean over the 600 scenarios of the per-scenario correlation with the "
    "true one-step gain, with a cluster-bootstrap 95% interval, because the scenario is the "
    "independent unit (Section 2.5); it is undefined on 31.3% of the steps of the unscreened "
    "learned arm, 32.5% of the true-objective arm and 22.6% of the two screened arms, and those "
    "steps enter no mean. Entries marked *by construction* are zero because of how the arm is "
    "defined, not because of a measurement. Every quantity named in Section 3 is mapped to its "
    "released column in Table 11 of Appendix D. Figure 2 plots the same quantities.",

    "**Table 4.** Attribution of stepwise regret, computed from "
    "`04_evaluation_new_protocol/stepwise_oracle.csv` (147,132 step records; the per-arm entries "
    "are step counts and must not be added down the column). Recorded decisions differ by arm "
    "because the screens change which steps are recorded, and no arm contains a step at which "
    "the admissible set is empty, so each decomposition is defined on its own recorded steps. "
    "$C_t$ is the censoring rate of Eq. (5a) and $C^{\\mathrm{screen}}_t$ the conditional screen "
    "override of Section 3.3. *Regret share from ranking* is the fraction of "
    "$\\sum_t \\delta_t$ on the steps where a ranking error occurred; it is **not** the share of "
    "the value form of Eq. (5), which needs $u_t(a^\\rho_t)$ and is not computable on this "
    "release (Section 3.5). The Spearman entry is a per-scenario mean over the 600 scenarios "
    "with a cluster-bootstrap 95% interval, because the scenario is the independent unit "
    "(Section 2.5); it is undefined on 31.3% and 32.5% of the steps of the two unscreened arms "
    "and on 22.6% of both screened arms, and those steps enter no mean. Entries marked *by "
    "construction* are zero because of how the arm is defined, not because of a measurement. "
    "Every quantity of Section 3 is mapped to its released column in Table 11 of Appendix D. "
    "Figure 2 plots the same quantities.",
    "5.3 Table 4 caption",
)

rep(
    "First, **the censoring mechanism is about twice as large as the conditional statistic**: "
    "the unscreened arms execute an inadmissible action on 76.6% and 75.8% of their steps, so "
    "more than half of an episode's steps restore nothing at all. The screened arms are at zero "
    "*by construction*, because a screened arm executes the ranker's admissible pick by "
    "definition; those entries are properties of the arm rather than findings, and no claim of "
    "improved ordering rests on them.",

    "First, **the censoring mechanism is about twice the conditional statistic**: the unscreened "
    "arms execute an inadmissible action on 76.6% and 75.8% of their steps, so more than half "
    "of an episode's steps restore nothing. The screened arms are zero *by construction*, since "
    "a screened arm executes the ranker's admissible pick by definition; those entries are "
    "properties of the arm rather than findings, and no claim of improved ordering rests on them.",
    "5.3 reading 1",
)

rep(
    "The fidelity, censoring and regret-share entries are step-level fractions pooled within an "
    "arm and are reported as descriptive summaries, with the episode-level restatement below as "
    "the quantity that respects the stated independent unit; only the Spearman entry is carried "
    "with a scenario-level interval.",
    "The fidelity, censoring and regret-share entries are step-level fractions pooled within an "
    "arm and are descriptive summaries, the episode-level restatement below being the quantity "
    "that respects the stated independent unit; only the Spearman entry carries a scenario-level "
    "interval.",
    "5.3 summaries",
)

rep(
    "The arms' percentages are not directly comparable, because an episode of an unscreened arm "
    "lasts 23.65 recorded decisions on average against 8.84 for a screened arm: a screened "
    "episode ends as soon as the admissible set is exhausted, so the arms cover the same "
    "episodes with different step counts. Restating the quantity per episode, $r_e = "
    "(\\text{inadmissible steps in } e)/(\\text{recorded steps in } e)$, and resampling "
    "scenarios gives an episode mean of $0.731$ for the learned ranker without a screen (median "
    "$0.760$, interquartile range $0.68$--$0.84$) and a pooled rate of $0.766$ with a "
    "cluster-bootstrap 95% interval of $[0.758, 0.775]$; for the true-objective ranker without "
    "a screen, mean $0.722$ and pooled rate $0.758$ with interval $[0.749, 0.767]$. Both "
    "screened arms are exactly zero with a degenerate interval, by construction. A paired "
    "arm-to-arm test is not identified here, because the arms diverge at the first ineffective "
    "step and the surviving steps are not the same steps, so pairing them would compare "
    "different states; the four arms are therefore reported per arm, and the arm-level "
    "difference is described rather than tested. The ranker's deficit is not a consequence of "
    "little being at stake, since Section 5.4 shows headroom in 11 of the 12 conditions and "
    "Section 5.7 shows that a rule which uses it reaches the offline optimum: the deficit is a "
    "property of the ranker, and an aggregate metric would have concealed which of the two it "
    "was.",

    "The arms' percentages are not directly comparable, because an unscreened episode lasts "
    "23.65 recorded decisions on average against 8.84 for a screened one: a screened episode "
    "ends as soon as the admissible set is exhausted, so the arms cover the same episodes with "
    "different step counts. Restating the quantity per episode, $r_e = (\\text{inadmissible "
    "steps in } e)/(\\text{recorded steps in } e)$, and resampling scenarios gives an episode "
    "mean of $0.731$ for the learned ranker without a screen (median $0.760$, interquartile "
    "range $0.68$--$0.84$) and a pooled rate of $0.766$ with a cluster-bootstrap 95% interval "
    "of $[0.758, 0.775]$; for the true-objective ranker without a screen, mean $0.722$ and "
    "pooled rate $0.758$ with interval $[0.749, 0.767]$. Both screened arms are exactly zero "
    "with a degenerate interval. A paired arm-to-arm test is not identified, because the arms "
    "diverge at the first ineffective step and the surviving steps are not the same steps; the "
    "four arms are therefore reported per arm, and the arm-level difference is described rather "
    "than tested. The ranker's deficit is not a consequence of little being at stake, since "
    "Section 5.4 shows headroom in 11 of the 12 conditions and Section 5.7 shows that a rule "
    "which uses it reaches the offline optimum; an aggregate metric would have concealed which "
    "of the two it was.",
    "5.3 episode level",
)

# =====================================================================================
# 5.4
# =====================================================================================
rep(
    "**The instance rule carries part of the result.** A sampling rule that admitted an instance "
    "whenever it had a broken key line at all in the uncoupled regime, while the budgeted regime "
    "necessarily required $K > B$, let the two regimes draw different instances; the uncoupled "
    "regime then appeared to have almost no headroom, with only 7 of 12 conditions positive and "
    "the moderate conditions apparently at zero. Under the unified rule both protocols exhibit a "
    "positive gap in **11 of 12 conditions**, and the moderate conditions are not exceptional: "
    "four of the six moderate conditions moved from an apparent zero to values among the largest "
    "in the uncoupled study, up to 15.685 on IEEE 118 moderate 1.50 and 11.594 on IEEE 300 "
    "moderate 1.15, while IEEE 300 moderate 1.50 remained at zero. The largest uncoupled value "
    "overall is 16.611, on IEEE 118 severe 1.50, which the old rule already exposed. **A "
    "statement about which conditions carry ordering information is therefore a statement about "
    "the instance rule as much as about the system**, the design-time lesson of Corollary 3. "
    "Figure 4 isolates the effect.",

    "**The instance rule carries part of the result.** A rule that admitted an instance whenever "
    "it had a broken key line at all in the uncoupled regime, while the budgeted regime required "
    "$K > B$, let the two regimes draw different instances; the uncoupled regime then appeared "
    "to have almost no headroom, with only 7 of 12 conditions positive. Under the unified rule "
    "both regimes show a positive gap in **11 of 12 conditions**: four of the six moderate "
    "conditions moved from an apparent zero to values among the largest in the uncoupled study, "
    "up to 15.685 on IEEE 118 moderate 1.50 and 11.594 on IEEE 300 moderate 1.15, while IEEE "
    "300 moderate 1.50 stayed at zero. The largest uncoupled value overall is 16.611, on IEEE "
    "118 severe 1.50, which the old rule already exposed. **A statement about which conditions "
    "carry ordering information is therefore a statement about the instance rule as much as "
    "about the system**, the design-time lesson of Corollary 3. Figure 4 isolates the effect.",
    "5.4 instance rule",
)

# =====================================================================================
# 5.5
# =====================================================================================
rep(
    "the profile is estimated on the severe half of the condition grid and is a conditional mean "
    "over those instances rather than an average over the benchmark; the depth-2 share of the "
    "uncoupled regime falls to **71.5%** on the least favourable of its 44 instances, against "
    "97.3% in the budgeted regime and 97.28% at the same depth with a budget. Section 9 records "
    "the sample structure as a limitation.",
    "the profile is estimated on the severe half of the grid and is a conditional mean over "
    "those instances rather than an average over the benchmark; its least favourable uncoupled "
    "instance reaches only **71.5%** at depth 2, against 97.28% at the same depth under a "
    "budget. Section 9 records the sample structure as a limitation.",
    "5.5 Table 6 caption",
)

rep(
    "Measured against the offline optimum rather than against the gap, the rolling controller at "
    "depth 2 already attains a mean of 99.99% of the exact optimum in the budgeted regime and "
    "99.998% without a budget. It is exact at depth 3 under a budget; without one, depth 3 "
    "reaches a mean of 99.96% and 16 of the 44 uncoupled instances fall short of 100%, with "
    "exactness arriving at depth 4. A committed plan at the same depth reaches 28% of the gap in "
    "the budgeted regime and 5% without a budget, and without a budget it does not reach the gap "
    "within the depth horizon examined.",

    "Measured against the offline optimum rather than the gap, the rolling controller at depth 2 "
    "already attains a mean of 99.99% of the exact optimum in the budgeted regime and 99.998% "
    "without a budget. It is exact at depth 3 under a budget; without one, depth 3 reaches "
    "99.96% and 16 of the 44 uncoupled instances fall short of 100%, exactness arriving at depth "
    "4. A committed plan at the same depth reaches 28% of the gap under a budget and 5% without "
    "one, and without a budget it does not reach the gap within the horizon examined.",
    "5.5 optimum",
)

rep(
    "The finding is therefore sharper than \"lookahead has value\". The gap's **value** is real "
    "and exactly computable; its **accessibility** is far cheaper than the value alone would "
    "suggest, because replanning is what converts foresight into recovery and two steps of "
    "foresight suffice. Rather than asking how much foresight can be afforded, the modeller need "
    "only ask whether two steps are affordable, and Table 6 shows that they are. It is also the "
    "reason a learned orderer cannot be justified by the size of the gap alone.",

    "The finding is therefore sharper than \"lookahead has value\". The gap's **value** is real "
    "and exactly computable; its **accessibility** is far cheaper than the value alone suggests, "
    "because replanning is what converts foresight into recovery and two steps suffice. The "
    "modeller need only ask whether two steps are affordable, and Table 6 shows that they are. "
    "It is also why a learned orderer cannot be justified by the size of the gap alone.",
    "5.5 finding",
)

# =====================================================================================
# 5.7
# =====================================================================================
rep(
    "the measured per-condition advantages of 8.74, 5.27, 6.97, 4.38, 8.37, 4.93, 8.95, 2.51, "
    "0.00, 2.70, 0.73 and 3.84 agree with the dynamic program's values of Table 5 (8.739, "
    "5.274, 6.970, 4.384, 8.370, 4.934, 8.951, 2.511, 0, 2.762, 0.731, 3.924) to the precision "
    "printed.",

    "the twelve measured per-condition advantages reproduce the dynamic program's values of "
    "Table 5 (8.739, 5.274, 6.970, 4.384, 8.370, 4.934, 8.951, 2.511, 0, 2.762, 0.731, 3.924) "
    "to the precision printed.",
    "5.7 number list",
)

rep(
    "It also fixes the interpretation of Table 8: those advantages average 4.78 over all 240 "
    "pairs, whereas the learned variants lose by 324.0 to 946.1 units. The deficit is a "
    "shortfall of the ranker, not of headroom.",
    "It also fixes the interpretation of Table 8: those advantages average 4.78 over all 240 "
    "pairs, whereas the learned variants lose by 324.0 to 946.1 units, so the deficit is a "
    "shortfall of the ranker rather than of headroom.",
    "5.7 interpretation",
)

# =====================================================================================
# 7
# =====================================================================================
rep(
    "Claims that a learned policy is fast enough for real-time restoration are common in this "
    "literature, and they are not currently comparable for a reason that has nothing to do with "
    "the policies. Of the three learned-restoration works of Section 1.5 that publish a timing "
    "table, exactly one reports a cheap non-learned rule alongside the learned one [6], and none "
    "of the three states whether the deep-learning library's inference wrapper or the "
    "environment step lies inside the timed region; the classical branch states a solver-side "
    "timing convention but not a learning-inference one [16]. Appendix E records the comparison. "
    "The methodological literature outside the power domain has established that protocol "
    "choices of this kind can reverse the ranking of two methods [23], so the omission is not a "
    "formality. The same trained network, evaluated on the same decision states under two timing "
    "boundaries, has a mean decision time of **0.086--0.108 ms** when the prediction wrapper is "
    "included and **0.034--0.036 ms** when a bare forward pass followed by the admissibility "
    "screen is timed. The method is unchanged and the measured latency differs by a factor of "
    "**2.5--3.1**; what is missing is the statement of the boundary.",

    "Claims that a learned policy is fast enough for real-time restoration are common here, and "
    "they are not comparable for a reason that has nothing to do with the policies. Of the three "
    "learned-restoration works of Section 1.5 that publish a timing table, exactly one reports a "
    "cheap non-learned rule alongside the learned one [6], and none states whether the "
    "deep-learning library's inference wrapper or the environment step lies inside the timed "
    "region; the classical branch states a solver-side convention but not a learning-inference "
    "one [16], and Appendix E records the comparison. The methodological literature has "
    "established that protocol choices of this kind can reverse the ranking of two methods [23], "
    "so the omission is not a formality. The same network, on the same decision states under two "
    "timing boundaries, has a mean decision time of **0.086--0.108 ms** with the prediction "
    "wrapper included and **0.034--0.036 ms** for a bare forward pass followed by the screen. "
    "The method is unchanged and the measured latency differs by **2.5--3.1**; what is missing "
    "is the statement of the boundary.",
    "7 opening",
)

rep(
    "**Table 10.** Decision latency per policy, in milliseconds, on the same 720 identical "
    "decision states; timings exclude environment advancement. Two statistics are reported "
    "rather than one because the ranking, not only the values, is the claim, and because the two "
    "do not agree: on the mean the one-step exact rule is 290--1236 times slower than the "
    "screened learned ranker, while on the median it is **faster by a factor of 1.6--3.6**, the "
    "mean being dominated by the tail of the exact rule. The last two rows carry the budget-$B = "
    "6$ timings that Algorithm 1 step 2 requires, which are the costs of the depth profile "
    "rather than of a single decision. Figure 9(a) plots the mean row on a logarithmic axis.",

    "**Table 10.** Decision latency per policy, in milliseconds, on the same 720 identical "
    "decision states; timings exclude environment advancement. Two statistics are reported "
    "because the ranking, not only the values, is the claim, and the two do not agree: on the "
    "mean the one-step exact rule is 290--1236 times slower than the screened learned ranker, on "
    "the median **faster by 1.6--3.6**, the mean being dominated by the exact rule's tail. The "
    "last two rows carry the budget-$B = 6$ timings that Algorithm 1 step 2 requires, which are "
    "depth-profile costs rather than per-decision costs. Figure 9(a) plots the mean on a "
    "logarithmic axis.",
    "7 Table 10 caption",
)

if FAILURES:
    print("ABORTED:")
    for f in FAILURES:
        print("   ", f)
    sys.exit(1)

MS.write_text(doc, encoding="utf-8")
print(f"stage 1 written: {before} -> {len(doc.split())} words  ({len(doc.split())-before:+d})")
sec = doc[doc.index("## 1. Introduction"):doc.index("## Appendix A.")]
print(f"  §1-§10 now: {len(sec.split())}")
