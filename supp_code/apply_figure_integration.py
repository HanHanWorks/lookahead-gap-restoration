"""Integrate the figure set into the SEGAN manuscript: citations and captions."""
from __future__ import annotations

import pathlib
import sys

P = pathlib.Path("SEGAN_manuscript_revised_2026-09-13.md")
s = P.read_text(encoding="utf-8")
orig = s
R: list[tuple[str, str]] = []


def rep(old: str, new: str) -> None:
    R.append((old, new))


# ------------------------------------------------------------------ citations
rep("The resulting claims are about the structure of the prioritization problem, not about the "
    "performance of any particular learned policy.",
    "The resulting claims are about the structure of the prioritization problem, not about the "
    "performance of any particular learned policy. Figure 1 collects the objects involved: the "
    "decomposition of a policy, the split of its regret, and the chain over which the optimum is "
    "computed.")

rep("Both are recorded from the frozen evaluation traces without additional simulation.",
    "Both are recorded from the frozen evaluation traces without additional simulation. "
    "Figure 1(ii) states the identity in diagram form.")

rep("Value alone therefore cannot justify a learned orderer: what matters is accessibility, and "
    "accessibility is measurable. Section 5.5 reports the profiles and the rolling comparisons for "
    "both protocols and for the third test system.",
    "Value alone therefore cannot justify a learned orderer: what matters is accessibility, and "
    "accessibility is measurable. Figure 5 reports the measured profiles, and Section 5.5 reports "
    "the corresponding numbers for both protocols and for the third test system.")

rep("Section 5.5 reports the measured profiles.",
    "Figure 5 reports the measured profiles.")

rep("over the released decision traces of the main protocol; Figure 1 shows the two components for "
    "the same four arms.",
    "over the released decision traces of the main protocol; Figure 2 shows the two components for "
    "the same four arms.")

rep("so the exact values used throughout this section are verified rather than asserted. Figure 2 "
    "compares the resulting gap under the two protocols.",
    "so the exact values used throughout this section are verified rather than asserted. Figure 3 "
    "compares the resulting gap under the two protocols, one panel per protocol so that the two "
    "magnitudes remain legible.")

rep("The consequence for interpretation is general: **a statement about which conditions carry "
    "ordering information is a statement about the instance rule as much as about the system**, "
    "which is the design-time lesson of Corollary 3.",
    "The consequence for interpretation is general: **a statement about which conditions carry "
    "ordering information is a statement about the instance rule as much as about the system**, "
    "which is the design-time lesson of Corollary 3. Figure 4 isolates the effect: the five "
    "moderate conditions whose maximum changes when the rule is unified, and the incidence of a "
    "positive gap per condition under each rule.")

rep("Table 5 reports the depth profile of Section 4.5 on the instances that share both protocols. "
    "The distinction between a committed plan and a rolling controller is decisive.",
    "Table 5 reports the depth profile of Section 4.5 on the instances that share both protocols, "
    "and Figure 5 plots it. The distinction between a committed plan and a rolling controller is "
    "decisive.")

rep("Sweeping the budget $B \\in \\{0,4,6,8\\}$ over the same twelve conditions gives the phase "
    "structure of the criterion: 132 instances are evaluated under each of the four budgets, 528 "
    "evaluations in total, on one instance set shared across all budgets. Classifying each instance "
    "by whether its gap is zero (non-identifiable), positive with a shallow depth requirement, or "
    "positive and long-range:",
    "Sweeping the budget $B \\in \\{0,4,6,8\\}$ over the same twelve conditions gives the phase "
    "structure of the criterion: 132 instances are evaluated under each of the four budgets, 528 "
    "evaluations in total, on one instance set shared across all budgets. Figure 6 shows the "
    "resulting classification and the magnitudes behind it. Classifying each instance by whether "
    "its gap is zero (non-identifiable), positive with a shallow depth requirement, or positive and "
    "long-range:")

rep("the unrestricted sample is reported alongside because the two answer different questions. "
    "Figure 3 reports the same comparison condition by condition.",
    "the unrestricted sample is reported alongside because the two answer different questions. "
    "Figure 7 reports the same comparison condition by condition.")

rep("so the injected-capacity implementation is verified before its results are read.",
    "so the injected-capacity implementation is verified before its results are read. Figure 8 "
    "plots the sweep.")

rep("Timings cover 720 identical decision states and exclude environment advancement; the full "
    "table is released.",
    "Timings cover 720 identical decision states and exclude environment advancement; the full "
    "table is released, and Figure 9(a) plots it on a logarithmic axis.")

rep("it identifies the budget-coupled conditions as the only ones with material headroom, and it "
    "also shows that a rolling depth-2 controller collects that headroom without learning.",
    "it identifies the budget-coupled conditions as the only ones with material headroom, and it "
    "also shows that a rolling depth-2 controller collects that headroom without learning. "
    "Figure 9(b) is the cost-quality plane on which that comparison is made: the rolling controller "
    "sits on the frontier at the offline optimum, while every learned variant is dominated, being "
    "both slower and worse.")

# ------------------------------------------------------------------- captions
rep("""**Figure 1.** Decomposition of stepwise regret into ranking error and censoring loss, for the four matched arms of Section 3.4, computed from the decision traces of the main protocol. Sections 3.2 and 5.3.

**Figure 2.** Lookahead gap by condition under the two protocols, in AUC@25 units. The gap is zero in exactly one of the twelve conditions under the unified instance rule of Section 5.0, and is multiplied by 7.2 at its extreme once the reconnection budget is imposed. Sections 4.3, 5.4.

**Figure 3.** Paired comparison of the rolling depth-2 rule against each alternative, condition by condition, on the aligned sample of Section 5.7. The rolling rule is never worse than any alternative in any of the 240 paired comparisons. Sections 5.7.""",
    """**Figure 1.** The three objects of the framework, drawn as a guide to Sections 3 and 4. (i) Any policy of the class is a ranker composed with an admissibility screen: the screen decides which candidates are legal, the ranker orders them, and the recovery of the executed action is evaluated by the service model of Eq. (1). (ii) Its stepwise regret splits exactly into a ranking error $R_t$ and a censoring loss $C_t$ (Eq. 5); either term vanishes on the steps where its mechanism is inactive, which is what makes the two separately measurable. (iii) The optimum $f(\\emptyset)$ is obtained by Eq. (7) over the subset lattice of the broken key lines, and the lookahead gap of Eq. (8) is the amount of cumulative recovery that the one-step exact rule forfeits against it. Conceptual diagram; the measured quantities appear in Figures 2--9.

**Figure 2.** Attribution of stepwise regret for the four matched arms of Section 3.4, computed from the decision traces of the main protocol. (a) The two mechanisms measured separately: *ranker fidelity* is the fraction of admissible steps at which the ranker places the oracle action first, and *censoring rate* is the fraction of steps at which its favoured action is inadmissible. (b) Composition of the total stepwise regret according to Eq. (5). The two screened arms carry no censoring loss by construction, so their entire remaining regret is ranking error, whereas the unscreened arms attribute about a third of their regret to censoring. Sections 3.2 and 5.3.

**Figure 3.** The lookahead gap by condition under the unified instance rule ($K \\geq 7$, 20 instances per condition), in AUC@25 units. Bars are condition means and markers are the maximum over the 20 instances. (a) Uncoupled protocol; (b) reconnection budget $B = 6$. The gap is zero in one of the twelve conditions (IEEE 300 moderate 1.50), and imposing the budget multiplies the extreme value by 7.2, from 16.7 to 120.1. Sections 4.3 and 5.4.

**Figure 4.** The instance-selection rule carries as much of the reported phenomenon as the systems and policies do. Same instances, two rules: $K > 0$ (the legacy rule, grey) and $K \\geq 7$ (the unified rule, orange). (a) Per-condition maximum of $\\Gamma_{\\mathrm{LA}}$; the five moderate conditions whose maximum changes are joined by a horizontal rule, and IEEE 118 moderate 1.50 moves from zero to 15.7. (b) Per-condition fraction of the 20 instances with a positive gap. The six severe conditions are unchanged under either rule, which is why the correction concerns the moderate groups alone. Section 5.4.

**Figure 5.** Value and accessibility are different quantities. Share of $\\Gamma_{\\mathrm{LA}}$ captured as a function of foresight depth $k$, over the instances with $\\Gamma_{\\mathrm{LA}} > 0$: 22 budgeted instances (a) and 44 uncoupled instances (b). A *committed* $k$-step plan executes its $k$-step solution and then reverts, so it must look 5 steps ahead to capture the whole gap and captures only 28% of it at depth 2; a *rolling* (receding-horizon) controller replans at every step and captures 99.8% at depth 2 and 100% at depth 3. Without a budget the committed plan does not reach the gap within the depth horizon examined (21% at depth 4), while the rolling controller still reaches 99.4% at depth 2. Sections 4.5 and 5.5.

**Figure 6.** The phase structure of the gap over the reconnection budget. (a) Each of the 132 shared instances classified as non-identifiable (zero gap), shallow (positive gap, small depth requirement) or long-range, under each of the four budgets. No instance is long-range at $B = 4$, which is the non-monotonicity discussed in Section 5.6. (b) Maximum $\\Gamma_{\\mathrm{LA}}$ per condition and budget; the budget axis has an interior minimum at $B = 4$ and its extremes at $B = 8$ (134.4 in IEEE 118 moderate 1.50). Section 5.6.

**Figure 7.** Head-to-head comparison on the aligned sample of Section 5.7 (12 conditions $\\times$ 20 scenarios, every scenario with an exact offline reference). (a) Mean objective by policy, against the mean offline optimum. The rolling depth-2 and depth-3 controllers and the one-step exact rule all sit at the optimum, and the learned variants sit 100 to 950 AUC@25 units below it. (b) Per-condition advantage of the rolling depth-2 rule over the *best* of the four learned variants, which is the most favourable choice of baseline available; the advantage is positive in all twelve conditions. Section 5.7.

**Figure 8.** The service-model regime of the criterion: the same instances under four capacity rules. (a) Fraction of instances with a positive gap; (b) maximum $\\Gamma_{\\mathrm{LA}}$. Rules R2 (a five-percent capacity floor) and R3 (uniform physical thermal ratings) make the gap vanish identically, while R4 (the utilisation-proportional rule with no floor) leaves it intact and enlarges its extreme value in the budgeted setting by 57%, from 45.1 to 70.8. Rule R1 is the rule used elsewhere in the paper and reproduces the frozen values to $0.000000$ on all 40 shared instances, which validates the implementation. Section 6.2.

**Figure 9.** Cost and quality on the same axes as Algorithm 1. (a) The latency spectrum of Table 9 on a logarithmic axis, for the four condition groups of the main protocol. The cheapest non-learned rule (first-broken-candidate) costs $0.0006$--$0.0007$ ms per decision, the screened learned ranker $0.034$--$0.036$ ms, and the one-step exact rule $9.98$--$44.02$ ms; measuring the same network with the deep-learning library's prediction wrapper inside the timed region multiplies the screened ranker's latency by a further $2.5$--$3.0$. (b) The cost--quality plane for the budgeted comparison of Section 5.7, using the budget-$B=6$ timings and the aligned sample. The rolling depth-2 rule lies on the frontier at the offline optimum and dominates every learned variant, which is both slower and worse. Sections 7 and 8.2.""")


def main() -> int:
    global s
    bad = 0
    for old, new in R:
        n = s.count(old)
        if n != 1:
            print(f"!! count={n}  {old[:78]!r}")
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
