"""P0 revision of the SEGAN manuscript: assumption A0, Lemma 0, the one-directional
Corollary 3, the redefined censoring indicators, and the rebuilt Table 3.

Every replacement is an exact literal pair; nothing is written unless all pairs
match exactly once.
"""
from __future__ import annotations

import pathlib
import sys

P = pathlib.Path("SEGAN_manuscript_revised_2026-09-13.md")
s = P.read_text(encoding="utf-8")
orig = s
R: list[tuple[str, str]] = []


def rep(old, new):
    R.append((old, new))


# ---------------------------------------------------------------------------
# 1.  §2.3  Assumption A0 and Lemma 0
# ---------------------------------------------------------------------------
OLD_23 = (
    "Let $S_t$ denote the reconnected set after step $t$, and $S_m = B_0$ once every broken key line "
    "has been reconnected. The recorded objective is the area under the recovery curve over the "
    "horizon,\n\n"
    "$$J = \\sum_{t=1}^{m} r(S_t) \\;+\\; (H - m - \\tfrac{1}{2})\\, r(S_m), \\tag{3}$$\n\n"
    "in recovery-percent $\\times$ step units, referred to throughout as AUC@25. The trapezoidal "
    "weight $H - m - \\tfrac{1}{2}$ applies to the terminal set because $S_m$ is held from step $m$ "
    "to the horizon. Because $S_m = B_0$ is the same set for every policy that reconnects all broken "
    "key lines within the horizon, the terminal term is order-invariant; Section 4.1 makes this the "
    "basis of the analysis rather than an observation."
)
NEW_23 = (
    "Let $S_t$ denote the reconnected set after step $t$. An action taken on a line that is not "
    "broken changes no set and consumes the step; call such a step **ineffective**, write "
    "$\\tilde m(\\pi) \\le m$ for the number of effective actions a policy takes, and index the "
    "effective steps in order. The recorded objective is the area under the recovery curve over the "
    "horizon,\n\n"
    "$$J(\\pi) \\;=\\; \\sum_{t=1}^{\\tilde m(\\pi)} r(S_t) \\;+\\; \\bigl(H - \\tilde m(\\pi) - "
    "\\tfrac{1}{2}\\bigr)\\, r\\bigl(S_{\\tilde m(\\pi)}\\bigr), \\tag{3}$$\n\n"
    "in recovery-percent $\\times$ step units, referred to throughout as AUC@25; the trapezoidal "
    "weight applies to the terminal set because it is held to the horizon.\n\n"
    "**Assumption A0.** An ineffective step realises zero recovery and leaves the state unchanged. "
    "This is a property of the environment rather than a restriction on policies: by Eq. (1) the "
    "unserved load is a function of the *set* of broken lines, and an ineffective action does not "
    "alter that set.\n\n"
    "> **Lemma 0 (effective steps should be taken first).** Under A0, with $H \\ge m$, every policy "
    "that completes the reconnection within the horizon satisfies\n"
    "> $$J(\\pi) \\;\\le\\; \\sum_{t=1}^{m} r(S_t) \\;+\\; (H - m - \\tfrac{1}{2})\\, r(S_m),$$\n"
    "> with equality if and only if the policy takes no ineffective step.\n\n"
    "*Proof.* The recovery curve of $\\pi$ is $r(S_1) \\le \\cdots \\le r(S_m)$ with one repetition of "
    "an earlier value in each ineffective position. If a position $t < H$ is ineffective, the "
    "effective action occupying some later position $t' > t$ can be moved into $t$ and the values "
    "between shifted left: every shifted value is unchanged, the moved value is at least as large as "
    "the one it displaces, and the horizon is fixed, so the trapezoidal area does not decrease. "
    "Repeating until no ineffective position remains proves the inequality, and the repetition is "
    "strictly smaller than the value it displaces whenever the chain has not yet terminated, which "
    "gives the equality condition. $\\square$\n\n"
    "Lemma 0 is what allows the rest of the paper to treat the objective as a function of the *chain* "
    "of reconnected sets: an optimal policy takes no ineffective step, and one that does only loses. "
    "The phenomenon is not marginal in the released traces. Of the 147,132 recorded decision steps of "
    "the main protocol, 51.1% are ineffective, and 4,026 of the 9,600 episodes contain at least one "
    "(Section 5.3). Because $S_m = B_0$ is the same set for every policy that reconnects all broken "
    "key lines within the horizon, the terminal term of the bound is order-invariant; Section 4.1 "
    "makes this the basis of the analysis rather than an observation."
)
rep(OLD_23, NEW_23)

# ---------------------------------------------------------------------------
# 2.  §2.6  the pre-check pointer, and the leftover "weakly identifiable"
# ---------------------------------------------------------------------------
rep("Weakly identifiable conditions are reported separately, because their means and significance "
    "tests measure the metric rather than the policies.",
    "Non-identifiable conditions are reported separately, because their means and significance tests "
    "measure the metric rather than the policies.")
rep("The pre-check is also the first application of the criterion developed in Section 4, since the "
    "lookahead gap vanishes exactly on non-identifiable conditions (Corollary 3).",
    "The pre-check is also the first application of the criterion developed in Section 4: by "
    "Corollary 3 a failing pre-check implies a vanishing gap, although the converse fails, and "
    "Section 5.1 tabulates the joint distribution of the two diagnoses over all eight condition "
    "groups.")

# ---------------------------------------------------------------------------
# 3.  Corollary 3 becomes one-directional, with the counterexample
# ---------------------------------------------------------------------------
OLD_C3 = (
    "> **Corollary 3 (the gap is an identifiability test).** $\\Gamma_{\\mathrm{LA}} = 0$ if and only "
    "if the one-step exact rule is optimal for the instance, which holds if and only if no ordering "
    "decision in the instance can change the objective. Hence the same quantity that bounds the "
    "benefit of learning also certifies whether the instance carries ordering information at all.\n\n"
    "The equivalence is the reason the framework is useful before training, not after: a vanishing "
    "gap tells the modeller that the condition cannot support a claim about orderings, and it does so "
    "at the cost of one dynamic program."
)
NEW_C3 = (
    "> **Corollary 3 (the gap is an identifiability test, in one direction only).** "
    "$\\Gamma_{\\mathrm{LA}} = 0$ if and only if the one-step exact rule is optimal for the instance, "
    "by Eq. (8). It follows that *step-wise degeneracy implies a vanishing gap*: if at every decision "
    "step all admissible candidates yield the same one-step recovery, then every ordering accumulates "
    "the same sum and $\\Gamma_{\\mathrm{LA}} = 0$. **The converse does not hold.**\n\n"
    "The converse fails on this paper's own data, and the counterexample is instructive. Under the "
    "legacy protocol all four condition groups have $\\Gamma_{\\mathrm{LA}} = 0$ to machine precision "
    "(maximum $1.1\\times10^{-13}$ on the released records), yet the maximizing candidate is unique at "
    "95.4% and 100% of the decision steps of the two IEEE 300-bus groups (Table 2). A condition can "
    "therefore present a single best immediate action at almost every step and still leave the greedy "
    "rule globally optimal, because a correct greedy choice need not be a *forced* one. The "
    "implication runs one way only: step-wise degeneracy is sufficient for a vanishing gap and not "
    "necessary, so a vanishing gap is weaker evidence about a condition than a failed pre-check.\n\n"
    "The pre-check of Section 2.6 and the gap are reported as **complementary diagnostics rather than "
    "a single test**, and Section 5.1 tabulates the relation. The pre-check is cheap, needs no "
    "dynamic program, and never rejects a condition that carries headroom; the gap is complete, "
    "certifying exactly when the one-step exact rule cannot be improved on, but it costs a dynamic "
    "program per condition."
)
rep(OLD_C3, NEW_C3)

# ---------------------------------------------------------------------------
# 4.  §3.2  define the three objects, restate Proposition 1, add Eq. (5a)
# ---------------------------------------------------------------------------
OLD_32 = (
    "Consider a policy $\\pi = \\rho \\circ \\varphi$ as decomposed in Eq. (4), and let $\\hat a_t$ "
    "be the action it executes at step $t$ (the admissibility-maximal action under $\\rho$, or the "
    "null action if none is admissible). Define the stepwise regret $\\delta_t = u^\\star_t - "
    "u_t(\\hat a_t) \\ge 0$. Write $\\mathcal{A}_t \\subseteq \\mathcal{K}$ for the admissible set "
    "$\\{a : \\varphi(S_{t-1}, a) = 1\\}$, and let $a^\\rho_t = \\operatorname{first}_{\\rho}"
    "(\\mathcal{A}_t)$ be the action the ranker favors, that is, the first admissible action in its "
    "order.\n\n"
    "> **Proposition 1 (additive regret decomposition).** For every scenario and step,\n"
    "> $$\\delta_t \\;=\\; \\underbrace{\\bigl(u^\\star_t - u_t(a^\\rho_t)\\bigr)}_{\\text{ranking "
    "error } R_t} \\;+\\; \\underbrace{\\bigl(u_t(a^\\rho_t) - u_t(\\hat a_t)\\bigr)}_{\\text{censoring "
    "loss } C_t}, \\tag{5}$$\n"
    "> where the second term is identically zero when the ranker's favored action is admissible, and "
    "the first is identically zero when the ranker places the oracle action first.\n\n"
    "*Proof.* The identity is an algebraic retelescoping of $u^\\star_t - u_t(\\hat a_t)$ through the "
    "intermediate value $u_t(a^\\rho_t)$; both brackets are non-negative because $u^\\star_t$ is a "
    "maximum and because $\\hat a_t = a^\\rho_t$ whenever $a^\\rho_t$ is admissible. $\\square$\n\n"
    "Aggregating over steps and scenarios gives the regret of the policy as the sum of two separately "
    "observable terms. The decomposition is useful only if the two terms can be measured "
    "independently, which they can: $R_t$ requires knowing the ranker's ordering *restricted to the "
    "admissible set*, whereas $C_t$ requires knowing only whether the ranker's favored action was "
    "admissible. Both are recorded from the frozen evaluation traces without additional simulation. "
    "Figure 1(ii) states the identity in diagram form."
)
NEW_32 = (
    "Consider a policy $\\pi = \\rho \\circ \\varphi$ as decomposed in Eq. (4). Write "
    "$\\mathcal{A}_t = \\{a \\in \\mathcal{K} : \\varphi(S_{t-1}, a) = 1\\}$ for the admissible set, "
    "$a^\\rho_t = \\operatorname{first}_{\\rho}(\\mathcal{A}_t)$ for the action the ranker favors "
    "*among the admissible ones*, and $\\hat a_t$ for the action the policy **actually executes**. "
    "The three objects are distinct, and the distinction is what the identity below measures: a "
    "ranker evaluated without a screen executes its unconditional favorite, which need not lie in "
    "$\\mathcal{A}_t$. Define the stepwise regret $\\delta_t = u^\\star_t - u_t(\\hat a_t) \\ge 0$; "
    "when $\\mathcal{A}_t$ is empty the step is ineffective and $\\delta_t$ is defined to be zero.\n\n"
    "> **Proposition 1 (additive regret decomposition).** For every scenario and step with "
    "$\\mathcal{A}_t \\neq \\emptyset$,\n"
    "> $$\\delta_t \\;=\\; \\underbrace{\\bigl(u^\\star_t - u_t(a^\\rho_t)\\bigr)}_{\\text{ranking "
    "error } R_t} \\;+\\; \\underbrace{\\bigl(u_t(a^\\rho_t) - u_t(\\hat a_t)\\bigr)}_{\\text{censoring "
    "loss } C_t}, \\tag{5}$$\n"
    "> with $R_t = 0$ exactly when the ranker places an oracle action first, and $C_t = 0$ exactly "
    "when the executed action is the ranker's admissible pick, $\\hat a_t = a^\\rho_t$.\n\n"
    "*Proof.* The identity is an algebraic retelescoping of $u^\\star_t - u_t(\\hat a_t)$ through the "
    "intermediate value $u_t(a^\\rho_t)$. For $R_t \\ge 0$, use that $u^\\star_t$ maximises $u_t$ "
    "over $\\mathcal{K} \\supseteq \\mathcal{A}_t$ while $a^\\rho_t \\in \\mathcal{A}_t$. For "
    "$C_t \\ge 0$, note that $\\hat a_t$ is either $a^\\rho_t$, giving $C_t = 0$, or an inadmissible "
    "action, which by A0 realises zero recovery, so that $C_t = u_t(a^\\rho_t) \\ge 0$. $\\square$\n\n"
    "Aggregating over steps and scenarios gives the regret as the sum of two terms. The identity is "
    "useful only if the terms are separately measurable, and here the released traces impose a "
    "boundary that the framework itself does not. The **indicator forms** are measurable: with "
    "$\\mathbf{1}[\\cdot]$ the indicator of an event,\n\n"
    "$$C_t \\;=\\; \\mathbf{1}\\bigl[\\hat a_t \\notin \\mathcal{A}_t\\bigr], \\qquad\n"
    "D_t \\;=\\; \\mathbf{1}\\bigl[\\hat a_t \\neq a^\\rho_t\\bigr], \\tag{5a}$$\n\n"
    "where $C_t$ records that the executed action was inadmissible and $D_t$ that the executed action "
    "deviated from the ranker's admissible pick. On the released traces the two coincide: both are "
    "zero for the screened arms by construction, and $0.766$ and $0.758$ for the two unscreened arms "
    "(Section 5.3). The **value forms** $R_t$ and $C_t$ of Eq. (5) additionally require "
    "$u_t(a^\\rho_t)$, the one-step recovery of the ranker's admissible pick; that quantity is "
    "computed at run time but is not persisted for the unscreened arms, whose trajectories diverge "
    "from the screened ones at the first ineffective step and therefore cannot be joined to recover "
    "it. Section 3.5 records this as a measurement boundary and Appendix D as a release requirement. "
    "Figure 1(ii) states the identity in diagram form."
)
rep(OLD_32, NEW_32)

# ---------------------------------------------------------------------------
# 5.  §3.3  three distinct reported quantities
# ---------------------------------------------------------------------------
OLD_33 = (
    "Two derived quantities are therefore reported for each policy. The **ranking fidelity** is the "
    "fraction of admissible steps at which the ranker's order places the oracle action first; the "
    "**censoring rate** is the fraction of steps at which the favored action is inadmissible. A policy "
    "with low fidelity and zero censoring has been made to look better by removing an error that has "
    "nothing to do with ordering; a policy with high censoring and low fidelity is being penalised "
    "for a mechanism unrelated to its ranking."
)
NEW_33 = (
    "Three derived quantities are therefore reported for each policy. The names are kept distinct "
    "because an earlier version of this analysis conflated the last two.\n\n"
    "- **Ranking fidelity**: the fraction of decision steps at which the ranker's order places an "
    "oracle action first, restricted to the admissible set.\n"
    "- **Censoring rate** $C_t$: the fraction of steps at which the executed action is inadmissible, "
    "Eq. (5a). This is the mechanism a screen exists to remove, and it is what a ranker without a "
    "screen incurs.\n"
    "- **Conditional screen override** $C^{\\mathrm{screen}}_t$: the fraction of steps at which the "
    "ranker's admissible pick *was* an oracle action and was nonetheless not the one executed. This "
    "is a conditional quantity, bounded above by the censoring rate and roughly half its size here; it "
    "measures only the part of censoring that is visible when the ranker is already right.\n\n"
    "A policy with low fidelity and zero censoring has been made to look better by removing an error "
    "that has nothing to do with ordering; a policy with high censoring and low fidelity is being "
    "penalised for a mechanism unrelated to its ranking. Reporting $C^{\\mathrm{screen}}_t$ in place "
    "of $C_t$ understates the mechanism by a factor of about two, and is not done here."
)
rep(OLD_33, NEW_33)

# ---------------------------------------------------------------------------
# 6.  §3.5  the two stated boundaries
# ---------------------------------------------------------------------------
OLD_35 = (
    "The decomposition is a bookkeeping identity: it says where a deficit sits, not that either term "
    "could be reduced. Whether the ranking term *can* be made small by learning is precisely the "
    "question Section 4 answers, and the answer is a property of the instance. Section 5.3 reports the "
    "measured sizes of both terms, and Section 4 provides the bound against which the ranking term "
    "must be judged."
)
NEW_35 = (
    "The decomposition is a bookkeeping identity: it says where a deficit sits, not that either term "
    "could be reduced. Whether the ranking term *can* be made small by learning is precisely the "
    "question Section 4 answers, and the answer is a property of the instance. Section 5.3 reports the "
    "measured sizes, and Section 4 supplies the bound $\\Gamma_{\\mathrm{LA}}$ against which a "
    "policy's advantage over the one-step exact rule must be judged.\n\n"
    "Two boundaries are stated rather than left implicit. First, **the identity is exact but the "
    "release is not complete**: the value forms of Eq. (5) need $u_t(a^\\rho_t)$, which the released "
    "traces do not persist for the unscreened arms, so Section 5.3 reports the indicator forms of "
    "Eq. (5a) and marks which entries are measured and which hold by construction. Second, **the "
    "identity is conditional on A0**: on a step where the executed action is inadmissible the realised "
    "recovery is zero, so the censoring term carries the whole stepwise regret. Both boundaries follow "
    "from the environment and from the release, not from the framework; the decomposition itself is "
    "retained, because $C_t$ is not identically zero (Section 5.3)."
)
rep(OLD_35, NEW_35)

# ---------------------------------------------------------------------------
# 7.  §5.3  rebuilt Table 3, with the episode-level restatement
# ---------------------------------------------------------------------------
OLD_T3 = (
    "**Table 3.** Attribution of stepwise regret. Step counts differ by arm because the screens change "
    "which decision steps are recorded: no arm contains a step at which the admissible set is empty, "
    "so the denominators are the recorded-decision counts on which each arm's decomposition is "
    "defined.\n\n"
    "| Arm | Admissible decisions | Ranking fidelity | Censoring rate | Regret share from ranking | "
    "Spearman (Q, one-step gain) |\n"
    "|---|---|---|---|---|---|\n"
    "| Learned ranker, no screen | 42,567 | 0.418 | **0.377** | 0.646 | +0.154 |\n"
    "| Learned ranker, screened | 15,912 | 0.312 | **0.000** | **1.000** | +0.030 |\n"
    "| True-objective ranker, no screen | 42,285 | 0.418 | 0.362 | 0.664 | +0.091 |\n"
    "| True-objective ranker, screened | 15,912 | 0.330 | **0.000** | **1.000** | +0.076 |\n\n"
    "Three readings follow. First, for both screened arms the censoring term is zero *by "
    "construction*, so 100% of their remaining regret is ranking error; on the steps where the ranker "
    "places the oracle action first, the realized regret is exactly zero. Second, the unscreened arms "
    "suffer censoring on 36--38% of their steps, and removing that mechanism accounts for the entire "
    "advantage that screening confers. This is exactly the confound Proposition 1 was built to "
    "expose. Third, the ranker itself carries little ordering information: the Spearman correlation "
    "between its scores and the true one-step gain is between +0.030 and +0.154, far below what a "
    "usable ordering would require. This last reading is what makes the attribution worth performing. "
    "The ranker's deficit is not a consequence of there being little at stake: Section 5.4 shows that "
    "headroom exists in 11 of the 12 conditions, and Section 5.7 shows that a rule which uses that "
    "headroom reaches the offline optimum. The deficit is a property of the ranker, and reporting an "
    "aggregate metric would have concealed which of the two it was."
)
NEW_T3 = (
    "Table 3 decomposes the stepwise regret of the four matched arms over the released decision traces "
    "of the main protocol; Figure 2 plots the same quantities. Every column name below is the name of "
    "the *quantity*; Table 12 of Appendix D maps each to the released column that realises it, because "
    "two of them previously shared a name.\n\n"
    "**Table 3.** Attribution of stepwise regret. Recorded decisions differ by arm because the screens "
    "change which steps are recorded; no arm contains a step at which the admissible set is empty, so "
    "each arm's decomposition is defined on its own recorded steps. $C_t$ is the censoring rate of "
    "Eq. (5a); $C^{\\mathrm{screen}}_t$ is the conditional screen override. Entries marked *by "
    "construction* are zero because of how the arm is defined, not because of a measurement.\n\n"
    "| Arm | Recorded decisions | Ranking fidelity | Censoring rate $C_t$ | Screen override "
    "$C^{\\mathrm{screen}}_t$ | Regret share from ranking | Spearman (Q, one-step gain) |\n"
    "|---|---|---|---|---|---|---|\n"
    "| Learned ranker, no screen | 42,567 | 0.418 | **0.766** | 0.377 | 0.646 | +0.154 |\n"
    "| Learned ranker, screened | 15,912 | 0.312 | **0.000** *(by construction)* | **0.000** *(by "
    "construction)* | **1.000** | +0.030 |\n"
    "| True-objective ranker, no screen | 42,285 | 0.418 | **0.758** | 0.362 | 0.664 | +0.091 |\n"
    "| True-objective ranker, screened | 15,912 | 0.330 | **0.000** *(by construction)* | **0.000** "
    "*(by construction)* | **1.000** | +0.076 |\n\n"
    "Three readings follow, and the first corrects the interpretation of an earlier draft of this "
    "table. First, **the censoring mechanism is about twice as large as the conditional statistic "
    "previously reported**: the unscreened arms execute an inadmissible action on 76.6% and 75.8% of "
    "their steps, so more than half of an episode's steps restore nothing at all. The screened arms "
    "are at zero *by construction*, because a screened arm executes the ranker's admissible pick by "
    "definition; those entries are properties of the arm rather than findings, and no claim of "
    "improved ordering rests on them. Second, the conditional override $C^{\\mathrm{screen}}_t$ is the "
    "smaller, conditional quantity, $0.377$ and $0.362$ on the unscreened arms and zero on the "
    "screened ones; it answers a different question, namely how often a correct ranker was overridden, "
    "and it is not the censoring rate. Third, the ranker itself carries little ordering information: "
    "the Spearman correlation between its scores and the true one-step gain is between $+0.030$ and "
    "$+0.154$, far below what a usable ordering would require.\n\n"
    "Two cautions belong with the table. The arms' percentages are not directly comparable, because an "
    "episode of an unscreened arm lasts 23.65 recorded decisions on average against 8.84 for a "
    "screened arm: a screened episode ends as soon as the admissible set is exhausted, so the two arms "
    "cover the same episodes with different step counts. And the step-level means pool steps across "
    "scenarios, which are the stated independent unit (Section 2.5); the entries are descriptive and "
    "no significance claim is attached to them. Both cautions are answered by the episode-level "
    "restatement below.\n\n"
    "**Episode-level censoring, and why the arms are not paired.** Restating the quantity per episode, "
    "$r_e = (\\text{inadmissible steps in } e)/(\\text{recorded steps in } e)$, and resampling "
    "scenarios (the independent unit of Section 2.5) gives an episode mean of $0.731$ for the learned "
    "ranker without a screen (median $0.760$, interquartile range $0.68$--$0.84$) and a pooled rate of "
    "$0.766$ with a cluster-bootstrap 95% interval of $[0.758, 0.775]$; for the true-objective ranker "
    "without a screen, an episode mean of $0.722$, a median of $0.760$, and a pooled rate of $0.758$ "
    "with interval $[0.749, 0.767]$. Both screened arms are exactly zero with a degenerate interval, "
    "by construction. A paired arm-to-arm test is not identified here: the arms diverge at the first "
    "ineffective step, so the steps that survive are not the same steps and pairing them would compare "
    "different states. The four arms are therefore reported per arm, and the arm-level difference is "
    "described rather than tested. The episode-level estimate also removes a second artefact of the "
    "step-level mean, namely that 51.1% of all recorded steps come from the two unscreened arms, which "
    "are precisely the arms whose episodes run longest.\n\n"
    "The ranker's deficit is not a consequence of there being little at stake: Section 5.4 shows that "
    "headroom exists in 11 of the 12 conditions, and Section 5.7 shows that a rule which uses that "
    "headroom reaches the offline optimum. The deficit is a property of the ranker, and reporting an "
    "aggregate metric would have concealed which of the two it was."
)
rep(OLD_T3, NEW_T3)


def main() -> int:
    global s
    bad = 0
    for old, new in R:
        n = s.count(old)
        if n != 1:
            print(f"!! count={n}  {old[:90]!r}")
            bad += 1
            continue
        s = s.replace(old, new)
    if bad:
        print(f"\n{bad} pair(s) did not match exactly once; nothing written.")
        return 1
    P.write_text(s, encoding="utf-8")
    print(f"applied {len(R)} replacements; file grew {len(s)-len(orig):+d} chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
