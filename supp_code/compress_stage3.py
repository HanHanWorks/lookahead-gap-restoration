"""Compression stage 3: remaining prose padding and the figure captions.

Figure captions count towards manuscript length and are the least information-dense text in
the paper, so they carry a disproportionate share of the achievable saving.
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


# ---------------------------------------------------------------- 2.3 / 2.6
rep(
    "This is a property of the environment rather than a restriction on policies: by Eq. (1) "
    "the unserved load is a function of the *set* of broken lines, and an ineffective action "
    "does not alter that set.",
    "This is a property of the environment rather than a restriction on policies: by Eq. (1) "
    "the unserved load is a function of the *set* of broken lines, which an ineffective action "
    "does not alter.",
    "2.3 A0",
)

rep(
    "The phenomenon is not marginal, 51.1% of the 147,132 recorded decision steps of the main "
    "protocol being ineffective and 4,026 of 9,600 episodes containing at least one (Section "
    "5.3).",
    "The phenomenon is not marginal: 51.1% of the 147,132 recorded decision steps of the main "
    "protocol are ineffective, and 4,026 of 9,600 episodes contain at least one (Section 5.3).",
    "2.3 incidence",
)

rep(
    "Before any comparison we therefore report three diagnostics per condition: the fraction of "
    "scenarios with positive initial unserved load; the fraction of decision steps at which the "
    "maximizing candidate is unique; and the ratio of the largest single-action recovery gain to "
    "the initial unserved load. The last two bear on identifiability for different reasons: a "
    "low fraction of unique maximizers means most steps present a tie and cannot reward a "
    "correct order, while a ratio close to one means a single action recovers almost "
    "everything, leaving no ordering decision anything to distribute.",
    "We therefore report three diagnostics per condition before any comparison: the fraction of "
    "scenarios with positive initial unserved load; the fraction of decision steps at which the "
    "maximizing candidate is unique; and the ratio of the largest single-action recovery gain to "
    "the initial unserved load. The last two bear on identifiability differently: a low fraction "
    "of unique maximizers means most steps present a tie and cannot reward a correct order, "
    "while a ratio close to one means a single action recovers almost everything, leaving no "
    "ordering decision anything to distribute.",
    "2.6 diagnostics",
)

# ---------------------------------------------------------------- 5.0
rep(
    "The rules are stated in terms of $K$ as recorded in the depth-curve artifacts, the files "
    "they are applied to; reconciling the episode column with $K$ is an outstanding release "
    "item (Appendix D).",
    "The rules are stated in terms of $K$ as recorded in the depth-curve artifacts; reconciling "
    "the two is an outstanding release item (Appendix D).",
    "5.0 column",
)

# ---------------------------------------------------------------- 7 conventions
rep(
    "1. **Report the cheapest non-learned rule alongside any latency claim.** In this benchmark "
    "that rule costs 0.0006--0.0007 ms per decision, so a latency claim is a claim about a "
    "factor of 48--59 rather than about an absolute number.",
    "1. **Report the cheapest non-learned rule alongside any latency claim.** Here that rule "
    "costs 0.0006--0.0007 ms per decision, so a latency claim is about a factor of 48--59 rather "
    "than an absolute number.",
    "7 conv 1",
)

rep(
    "2. **State the measurement boundary**, in particular whether the deep-learning library's "
    "inference wrapper and the environment step are inside the timed region. The 2.5--3.1-fold "
    "difference above is a boundary effect and nothing else.",
    "2. **State the measurement boundary**, in particular whether the library's inference "
    "wrapper and the environment step lie inside the timed region. The 2.5--3.1-fold difference "
    "above is a boundary effect and nothing else.",
    "7 conv 2",
)

rep(
    "3. **State the exact-solvability status of the evaluator.** This determines whether an "
    "exact reference exists at all, and therefore whether the reported comparison is against a "
    "bound or against another heuristic.",
    "3. **State the exact-solvability status of the evaluator.** This determines whether an "
    "exact reference exists, and therefore whether the comparison is against a bound or another "
    "heuristic.",
    "7 conv 3",
)

# ---------------------------------------------------------------- 8.1 / 8.3
rep(
    "Any advantage reported for a learned ranker under such a configuration therefore originates "
    "in one of the four candidate sources of Section 1.1, and the paper names each of them. The "
    "learned ordering is named by the ranking term $R_t$. The admissibility screen is named by "
    "the censoring term $C_t$, and both are measured in Section 5.3. An aggregate metric that "
    "the order does not affect is *not* a quantity of Eq. (5); it is a property of the "
    "condition, and it is named by the pre-check of Section 2.6 and by the terminal invariance "
    "of Lemma 1, applied in Section 5.1 and in Section 5.2. The choice of reference is likewise "
    "not a quantity of Eq. (5) but a property of the comparison, and it is named by the "
    "aligned-sample convention of Section 5.7 and made visible by the reporting standard of "
    "Section 7. Table 2 records that split.",

    "Any advantage reported for a learned ranker under such a configuration therefore originates "
    "in one of the four candidate sources of Section 1.1. The learned ordering is named by the "
    "ranking term $R_t$, the admissibility screen by the censoring term $C_t$, and both are "
    "measured in Section 5.3. An aggregate metric that the order does not affect is *not* a "
    "quantity of Eq. (5) but a property of the condition, named by the pre-check of Section 2.6 "
    "and by the terminal invariance of Lemma 1 (Sections 5.1 and 5.2). The choice of reference "
    "is likewise a property of the comparison, named by the aligned-sample convention of Section "
    "5.7 and made visible by the reporting standard of Section 7. Table 2 records that split.",
    "8.1 sources",
)

rep(
    "Corollary 4 lists three ways a learned orderer can matter, and this paper closes one of "
    "them experimentally and measures the second. Resource coupling is realized as a cardinality "
    "budget in Section 5.4, where it multiplies the extreme gap by 7.2 and lifts the "
    "condition-average gap from 0.87 to 4.80; that case is informative precisely because it "
    "breaks the hypothesis of Corollary 2, the terminal set then being a decision rather than an "
    "invariant.",
    "Corollary 4 lists three ways a learned orderer can matter, and this paper closes one "
    "experimentally and measures the second. Resource coupling is realized as a cardinality "
    "budget in Section 5.4, where it multiplies the extreme gap by 7.2 and lifts the "
    "condition-average gap from 0.87 to 4.80; the case is informative because it breaks the "
    "hypothesis of Corollary 2, the terminal set then being a decision rather than an invariant.",
    "8.3 closes",
)

# ---------------------------------------------------------------- Appendix A
rep(
    "the action set, the capacity rule, and the source of randomness, since the legacy protocol "
    "draws from the process-global generator while the main protocol draws from the "
    "environment's own generator, seeded per scenario. The main protocol's key lines are "
    "released as `02_protocol_artifacts/{topology}_key_lines.csv`; the legacy set is produced by "
    "the environment's own line-importance screen and is recovered by re-running it, which is "
    "why no separate legacy artifact is shipped.",
    "the action set, the capacity rule, and the source of randomness, the legacy protocol "
    "drawing from the process-global generator and the main protocol from the environment's own "
    "generator, seeded per scenario. The main protocol's key lines are released as "
    "`02_protocol_artifacts/{topology}_key_lines.csv`; the legacy set is produced by the "
    "environment's own line-importance screen and recovered by re-running it, which is why no "
    "separate legacy artifact is shipped.",
    "Appendix A",
)

# ---------------------------------------------------------------- figure captions
rep(
    "**Figure 1.** The three objects of the framework, drawn as a guide to Sections 3 and 4. "
    "(i) Any policy of the class is a ranker composed with an admissibility screen: the screen "
    "decides which candidates are legal, the ranker orders them, and the recovery of the "
    "executed action is evaluated by the service model of Eq. (1). (ii) Its stepwise regret "
    "splits exactly into a ranking error $R_t$ and a censoring loss $C_t$ (Eq. 5); either term "
    "vanishes on the steps where its mechanism is inactive, which is what makes the two "
    "separately measurable. (iii) The optimum $f(\\emptyset)$ is obtained by Eq. (7) over the "
    "subset lattice of the broken key lines, and the lookahead gap of Eq. (8) is the amount of "
    "cumulative recovery that the one-step exact rule forfeits against it. Conceptual diagram; "
    "the measured quantities appear in Figures 2--9.",

    "**Figure 1.** The three objects of the framework, as a guide to Sections 3 and 4. (i) Any "
    "policy of the class is a ranker composed with an admissibility screen: the screen decides "
    "which candidates are legal, the ranker orders them, and the recovery of the executed action "
    "is evaluated by the service model of Eq. (1). (ii) Its stepwise regret splits exactly into "
    "a ranking error $R_t$ and a censoring loss $C_t$ (Eq. 5), either vanishing on the steps "
    "where its mechanism is inactive, which is what makes the two separately measurable. (iii) "
    "The optimum $f(\\emptyset)$ is obtained by Eq. (7) over the subset lattice of the broken key "
    "lines, and the lookahead gap of Eq. (8) is the cumulative recovery the one-step exact rule "
    "forfeits against it. Conceptual diagram; the measured quantities appear in Figures 2--9.",
    "Figure 1 caption",
)

rep(
    "**Figure 5.** Value and accessibility are different quantities. Share of "
    "$\\Gamma_{\\mathrm{LA}}$ captured as a function of foresight depth $k$, over the instances "
    "with $\\Gamma_{\\mathrm{LA}} > 0$: 22 budgeted instances (a) and 44 uncoupled instances (b). "
    "A *committed* $k$-step plan executes its $k$-step solution and then reverts, so in the "
    "budgeted regime it must look 5 steps ahead to capture the whole gap and captures only 28% "
    "of it at depth 2; a *rolling* (receding-horizon) controller replans at every step and "
    "captures 99.8% at depth 2 and 100% at depth 3. Without a budget the committed plan does not "
    "reach the gap within the depth horizon examined (21% at depth 4), while the rolling "
    "controller still reaches 99.4% at depth 2. Sections 4.5 and 5.5.",

    "**Figure 5.** Value and accessibility are different quantities. Share of "
    "$\\Gamma_{\\mathrm{LA}}$ captured against foresight depth $k$, over the instances with "
    "$\\Gamma_{\\mathrm{LA}} > 0$: 22 budgeted (a) and 44 uncoupled (b). A *committed* $k$-step "
    "plan executes its $k$-step solution and then reverts, so under a budget it must look 5 "
    "steps ahead to capture the whole gap and captures only 28% at depth 2; a *rolling* "
    "(receding-horizon) controller replans at every step and captures 99.8% at depth 2 and 100% "
    "at depth 3. Without a budget the committed plan does not reach the gap within the horizon "
    "examined (21% at depth 4), while the rolling controller still reaches 99.4% at depth 2. "
    "Sections 4.5 and 5.5.",
    "Figure 5 caption",
)

rep(
    "**Figure 6.** The phase structure of the gap over the reconnection budget. (a) Each of the "
    "132 shared instances classified as non-identifiable (zero gap), shallow (positive gap, "
    "small depth requirement) or long-range, under each of the four budgets. No instance is "
    "long-range at $B = 4$, which is the non-monotonicity discussed in Section 5.6. (b) Maximum "
    "$\\Gamma_{\\mathrm{LA}}$ per condition and budget; the budget axis has an interior minimum "
    "at $B = 4$ and its extremes at $B = 8$ (134.4 in IEEE 118 moderate 1.50). Section 5.6.",

    "**Figure 6.** The phase structure of the gap over the reconnection budget. (a) The 132 "
    "shared instances classified as non-identifiable (zero gap), shallow (positive gap, small "
    "depth requirement) or long-range, under each of the four budgets; no instance is long-range "
    "at $B = 4$, the non-monotonicity discussed in Section 5.6. (b) Maximum "
    "$\\Gamma_{\\mathrm{LA}}$ per condition and budget; the budget axis has an interior minimum "
    "at $B = 4$ and its extremes at $B = 8$ (134.4 in IEEE 118 moderate 1.50). Section 5.6.",
    "Figure 6 caption",
)

rep(
    "**Figure 8.** The service-model regime of the criterion: the same instances under four "
    "capacity rules. (a) Fraction of instances with a positive gap; (b) maximum "
    "$\\Gamma_{\\mathrm{LA}}$. Rules R2 (a five-percent capacity floor) and R3 (uniform physical "
    "thermal ratings) make the gap vanish identically, while R4 (the utilisation-proportional "
    "rule with no floor) leaves it intact and enlarges its extreme value in the budgeted regime "
    "by 57%, from 45.1 to 70.8. Rule R1 is the rule used elsewhere in the paper and reproduces "
    "the frozen values to $0.000000$ on all 40 shared instances, which validates the "
    "implementation. Section 6.2.",

    "**Figure 8.** The service-model regime of the criterion: the same instances under four "
    "capacity rules. (a) Fraction of instances with a positive gap; (b) maximum "
    "$\\Gamma_{\\mathrm{LA}}$. Rules R2 (a five-percent capacity floor) and R3 (uniform physical "
    "thermal ratings) make the gap vanish identically, while R4 (the utilisation-proportional "
    "rule with no floor) leaves it intact and enlarges its extreme value under a budget by 57%, "
    "from 45.1 to 70.8. Rule R1 is used elsewhere in the paper and reproduces the frozen values "
    "to $0.000000$ on all 40 shared instances, validating the implementation. Section 6.2.",
    "Figure 8 caption",
)

rep(
    "**Figure 9.** Cost and quality on the same axes as Algorithm 1. (a) The mean-latency "
    "spectrum of Table 10 on a logarithmic axis, for the four condition groups of the main "
    "protocol; the policy names are those of Table 10, and the row marked *Learned ranker, "
    "wrapper* is the same network as *Learned ranker, screened* with the prediction wrapper "
    "inside the timed region. The electrical-priority rule costs $0.0006$--$0.0007$ ms per "
    "decision, the screened learned ranker $0.034$--$0.036$ ms, and the one-step exact rule "
    "$9.98$--$44.02$ ms on the mean; the boundary multiplies the screened ranker's latency by a "
    "further $2.5$--$3.1$. (b) The cost--quality plane for the budgeted comparison of Section "
    "5.7, using the budget-$B=6$ timings and the aligned sample. Two candidates of Section 5.7 "
    "cannot be placed on the plane: the uniformly random rule has no timing measurement and the "
    "rolling depth-1 controller has no aligned-sample quality value. The timings in this panel "
    "cover 276 decision states, against 720 in panel (a). The cheapest non-learned rule is the "
    "fastest policy on the plane and, at 1740 AUC@25, is better than all four learned variants, "
    "so each of them is dominated: a policy exists that is faster and better. The rolling "
    "depth-2 controller reaches the offline optimum at 26--575 ms per decision, more than two "
    "orders of magnitude above every learned variant. Sections 7 and 8.2.",

    "**Figure 9.** Cost and quality on the same axes as Algorithm 1. (a) The mean-latency "
    "spectrum of Table 10 on a logarithmic axis, for the four condition groups of the main "
    "protocol; policy names are those of Table 10, and the row marked *Learned ranker, wrapper* "
    "is the same network as *Learned ranker, screened* with the prediction wrapper inside the "
    "timed region. The electrical-priority rule costs $0.0006$--$0.0007$ ms per decision, the "
    "screened learned ranker $0.034$--$0.036$ ms and the one-step exact rule $9.98$--$44.02$ ms "
    "on the mean; the boundary multiplies the screened ranker's latency by a further "
    "$2.5$--$3.1$. (b) The cost--quality plane for the budgeted comparison of Section 5.7, using "
    "the budget-$B=6$ timings and the aligned sample. Two candidates of Section 5.7 cannot be "
    "placed on it: the uniformly random rule has no timing measurement and the rolling depth-1 "
    "controller no aligned-sample quality value. These timings cover 276 decision states, "
    "against 720 in panel (a). The cheapest non-learned rule is the fastest policy on the plane "
    "and, at 1740 AUC@25, better than all four learned variants, so each is dominated: a policy "
    "exists that is faster and better. The rolling depth-2 controller reaches the offline "
    "optimum at 26--575 ms per decision, more than two orders of magnitude above every learned "
    "variant. Sections 7 and 8.2.",
    "Figure 9 caption",
)

if FAILURES:
    print("ABORTED:")
    for f in FAILURES:
        print("   ", f)
    sys.exit(1)

MS.write_text(doc, encoding="utf-8")
sec = doc[doc.index("## 1. Introduction"):doc.index("## Appendix A.")]
ab = doc.split("## Abstract")[1].split("**Keywords")[0]
print(f"stage 3 written: {before} -> {len(doc.split())} words  ({len(doc.split())-before:+d})")
print(f"  §1-§10 now: {len(sec.split())}")
