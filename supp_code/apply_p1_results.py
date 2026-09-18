"""P1/P3 revision: instance rule, confusion matrix, §6.1 correction, positioning.

Exact literal pairs; nothing is written unless every pair matches exactly once.
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
# 1.  §5.0  state the instance rule per section, with its sensitivity
# ---------------------------------------------------------------------------
rep(
    "**Instance-selection rule.** Any distribution of the lookahead gap is meaningless without the "
    "rule that selected the instances, and the rule must not depend on the quantity being swept. "
    "Every gap reported in Sections 5.4--5.6 therefore uses a single, protocol-independent rule: "
    "**$K \\ge 7$ broken key lines, $K \\le 12$**, applied identically to both protocols and to every "
    "budget. Section 5.4 explains why this rule matters.",
    "**Instance-selection rule.** Any distribution of the lookahead gap is meaningless without the "
    "rule that selected the instances, and the rule must not depend on the quantity being swept. "
    "Sections 5.4 and 5.5 use a single, protocol-independent rule, **$K \\ge 7$ broken key lines with "
    "$K \\le 12$**, applied identically to both protocols and to every budget; the phase study of "
    "Section 5.6 draws its own sample, **$K \\ge 9$**, because it sweeps the budget and needs the "
    "budget to bind. Two samples are therefore in play and are named wherever they are used, since "
    "conflating them was a defect of an earlier draft.\n\n"
    "**Sensitivity to the cut-off.** Holding the protocol fixed and raising the cut-off leaves the "
    "uncoupled results unchanged and moves the budgeted incidence. At $K \\ge 7$ the uncoupled "
    "protocol has 240 instances, a positive gap in 11 of 12 conditions and a maximum of 16.611; at "
    "$K \\ge 8$ it has 198 instances and the same 11 conditions and the same maximum; at $K \\ge 9$, "
    "174 instances and again 11 conditions and 16.611. The budgeted protocol has a positive gap in 11 "
    "of 12 conditions at $K \\ge 7$, and in 8 of 12 at $K \\ge 8$ and at $K \\ge 9$, while its extreme "
    "value stays at 120.134 throughout. The extreme value and the qualitative phase structure are "
    "therefore insensitive to the cut-off over this range, and the budgeted *incidence* is not, which "
    "is why Table 4 and Table 6 carry different sample rules and why both are stated.""")

# ---------------------------------------------------------------------------
# 2.  §5.1  Table 2 gains the gap and the verdict; then the contingency
# ---------------------------------------------------------------------------
rep(
    "**Table 2.** Identifiability diagnostics. \"scenarios with load\" is the fraction of scenarios "
    "with positive initial unserved load; \"AUC = 0\" is the fraction of episodes whose recorded "
    "objective is exactly zero; \"unique maximizer\" is the fraction of decision steps at which the "
    "maximizing admissible candidate is unique, computed across the three capacity margins.",
    "**Table 2.** Identifiability diagnostics, read against the gap. \"scenarios with load\" is the "
    "fraction of scenarios with positive initial unserved load; \"AUC = 0\" is the fraction of "
    "episodes whose recorded objective is exactly zero; \"unique maximizer\" is the fraction of "
    "decision steps at which the maximizing admissible candidate is unique. The last two columns put "
    "the verdict of Section 2.6 beside the size of the gap, which is what makes the two diagnoses "
    "comparable; the pre-check diagnostics are taken at the nominal margin $\\kappa = 1.15$ and the "
    "\"scenarios with load\" and \"AUC = 0\" columns span the three margins, hence their ranges.")

rep(
    "| Protocol | Condition group | Scenarios with load | AUC = 0 | Unique maximizer | Largest "
    "single-action gain / initial unserved |\n"
    "|---|---|---|---|---|---|\n"
    "| Legacy | IEEE 118 moderate | 0.40 | **0.710** | 0.30 | 1.00 |\n"
    "| Legacy | IEEE 118 severe | 0.68--0.70 | **0.485** | 0.55 | 0.87 |\n"
    "| Legacy | IEEE 300 moderate | 0.92 | 0.154--0.161 | 0.954 | 0.42 |\n"
    "| Legacy | IEEE 300 severe | 1.00 | 0.015 | 1.00 | 0.28 |\n"
    "| Main | IEEE 118 moderate | **1.00** | **0.000** | 0.95 | 0.23 |\n"
    "| Main | IEEE 118 severe | **1.00** | 0.011 | 1.00 | 0.15 |\n"
    "| Main | IEEE 300 moderate | **1.00** | 0.006--0.008 | 1.00 | 0.28 |\n"
    "| Main | IEEE 300 severe | **1.00** | 0.001 | 1.00 | 0.16 |",
    "| Protocol | Condition group | Scenarios with load | AUC = 0 | Unique maximizer | Largest "
    "single-action gain / initial unserved | Max $\\Gamma_{\\mathrm{LA}}$ | Pre-check verdict |\n"
    "|---|---|---|---|---|---|---|---|\n"
    "| Legacy | IEEE 118 moderate | 0.40 | **0.710** | 0.30 | 1.00 | **0.000** | non-identifiable |\n"
    "| Legacy | IEEE 118 severe | 0.68--0.70 | **0.485** | 0.55 | 0.87 | **0.000** | "
    "non-identifiable |\n"
    "| Legacy | IEEE 300 moderate | 0.92 | 0.154--0.161 | 0.954 | 0.42 | **0.000** | identifiable |\n"
    "| Legacy | IEEE 300 severe | 1.00 | 0.015 | 1.00 | 0.28 | **0.000** | identifiable |\n"
    "| Main | IEEE 118 moderate | **1.00** | **0.000** | 0.95 | 0.23 | 15.685 | identifiable |\n"
    "| Main | IEEE 118 severe | **1.00** | 0.011 | 1.00 | 0.15 | 16.611 | identifiable |\n"
    "| Main | IEEE 300 moderate | **1.00** | 0.006--0.008 | 1.00 | 0.28 | 11.594 | identifiable |\n"
    "| Main | IEEE 300 severe | **1.00** | 0.001 | 1.00 | 0.16 | 8.601 | identifiable |")

rep(
    "The asymmetry between the two test systems is itself the diagnostic point. Under the same legacy "
    "construction the IEEE 300-bus groups pass both diagnostics (unique maximizer 0.95 and 1.00; "
    "single-action gain share 0.42 and 0.28), which shows that the failure is an uncontrolled design "
    "choice rather than a property of the test systems or of the test problem.",
    "The asymmetry between the two test systems is itself the diagnostic point. Under the same legacy "
    "construction the IEEE 300-bus groups pass both diagnostics (unique maximizer 0.954 and 1.00; "
    "single-action gain share 0.42 and 0.28), which shows that the failure is an uncontrolled design "
    "choice rather than a property of the test systems or of the test problem.\n\n"
    "**The pre-check and the gap are complementary, and the contingency shows in which sense.** "
    "Crossing the verdict of Section 2.6 with the size of the gap over the eight condition groups of "
    "Table 2 gives\n\n"
    "$$\\underbrace{2}_{\\text{rejects},\\ \\Gamma_{\\mathrm{LA}}=0} \\quad\n"
    "\\underbrace{0}_{\\text{rejects},\\ \\Gamma_{\\mathrm{LA}}>0} \\qquad\n"
    "\\underbrace{2}_{\\text{passes},\\ \\Gamma_{\\mathrm{LA}}=0} \\quad\n"
    "\\underbrace{4}_{\\text{passes},\\ \\Gamma_{\\mathrm{LA}}>0}.$$\n\n"
    "Two readings follow, and the second is the reason the paper does not merge the two tests. First, "
    "**the pre-check never rejects a condition that carries headroom**: the cell $(\\text{rejects}, "
    "\\Gamma_{\\mathrm{LA}}>0)$ is empty over every group examined, so a failed pre-check is always "
    "justified and the diagnostic can be used as a gate without discarding a condition worth "
    "studying. Second, **the pre-check is nonetheless not equivalent to the gap, and not stronger "
    "than it**: it passes two conditions whose gap is identically zero (the two legacy IEEE 300-bus "
    "groups), which the gap flags. Neither test subsumes the other, so the two are reported as "
    "**complementary diagnostics**: the pre-check is cheap, needs no dynamic program and is "
    "conservative, while the gap is complete but costs a dynamic program per condition. Calling "
    "either one \"strictly stronger\" would be wrong in one direction or the other, and the "
    "one-directional Corollary 3 is exactly the statement of which direction holds.")

# ---------------------------------------------------------------------------
# 3.  §6.1  the floor-saturation number corrected, with its provenance
# ---------------------------------------------------------------------------
rep(
    "Re-deriving the limits so that they follow the same rule as the maximum-flow model, that is, the "
    "utilisation-proportional rule of Eq. (2) with $c_\\ell = \\kappa |f^{(0)}_\\ell|$, makes the "
    "transplant comparable but not solvable: 168 of the 173 lines fall to the floor of 8.5 MW, the "
    "linear program becomes degenerate, and it fails to converge under every solver available. "
    "Relaxing the floor until it converges removes the binding structure and the gap returns to zero.",
    "Re-deriving the limits so that they follow the same rule as the maximum-flow model, that is, the "
    "utilisation-proportional rule of Eq. (2) with $c_\\ell = \\kappa |f^{(0)}_\\ell|$, makes the "
    "transplant comparable but not solvable. At the main protocol's parameters the floor is not the "
    "mechanism: only **17 of the 173** lines sit on the 8.48 MW floor at $\\kappa = 1.25$ (20 at "
    "$\\kappa = 1.15$, 14 at $\\kappa = 1.50$), while the remaining ratings span 8.5 MW to 562 MW, so "
    "the transfer capability of the transplanted network rests on a small number of lightly loaded "
    "lines and the linear program fails to converge under every solver available. Relaxing the floor "
    "until it converges removes the binding structure and the gap returns to zero.\n\n"
    "An earlier draft attributed the non-convergence to floor saturation and quoted 168 of 173 lines "
    "on the floor. That figure is the one obtained at $\\phi = 0.05$, the sweep's R2 rule, and not at "
    "the main protocol's $\\phi = 0.002$; the corrected counts are given above. The mechanism is the "
    "heterogeneity of the utilisation-proportional ratings rather than a dominant floor, and the "
    "conclusion of this subsection is unchanged. The recomputation is released as "
    "`bruteforce_validation.log` (Appendix D).")

# ---------------------------------------------------------------------------
# 4.  §8.4  the largest uncoupled value is 16.611, not 15.685
# ---------------------------------------------------------------------------
rep(
    "The incidence of a positive gap changed from 7 of 12 conditions to 11 of 12 when the rule "
    "selecting instances was made protocol-independent, and the moderate conditions moved from "
    "apparent zero to the largest uncoupled values in the study.",
    "The incidence of a positive gap changed from 7 of 12 conditions to 11 of 12 when the rule "
    "selecting instances was made protocol-independent, and the moderate conditions moved from an "
    "apparent zero to gaps of 15.685 and 11.594, the second and third largest uncoupled values in the "
    "study behind the 16.611 of IEEE 118 severe at $\\kappa = 1.50$.")

# ---------------------------------------------------------------------------
# 5.  §1.4  a fifth contribution, and the boundary on C1
# ---------------------------------------------------------------------------
rep(
    "- **C1 · An attribution framework.** Any prioritization policy is written as a ranker composed "
    "with an admissibility screen, and its stepwise regret admits an exactly additive decomposition "
    "into a ranking term and a censoring term, both separately observable. Paired with a "
    "matched-training leave-one-out protocol that varies the ranker's training objective and the "
    "presence of the screen independently, the framework makes the source of a reported gain "
    "identifiable. *(Section 3)*",
    "- **C1 · An attribution framework.** Any prioritization policy is written as a ranker composed "
    "with an admissibility screen, and its stepwise regret admits an exactly additive decomposition "
    "into a ranking term and a censoring term. Paired with a matched-training leave-one-out protocol "
    "that varies the ranker's training objective and the presence of the screen independently, the "
    "framework makes the source of a reported gain identifiable. The decomposition is exact, and its "
    "measurable form on the released traces is the pair of censoring indicators of Eq. (5a); the "
    "value form requires a counterfactual the release does not yet carry, and Section 3.5 states that "
    "boundary. *(Section 3)*")

rep(
    "A supporting contribution is a **reporting standard for latency claims** in this literature.",
    "- **C5 · A one-directional criterion and a complementary diagnostic.** Step-wise degeneracy "
    "implies a vanishing lookahead gap, but not conversely: a condition can present a unique best "
    "immediate action at 95% of its steps and still leave the greedy rule globally optimal, and the "
    "legacy records contain that counterexample. The identifiability pre-check and the gap are "
    "therefore complementary rather than equivalent, and crossing the two diagnoses over the eight "
    "condition groups shows that the pre-check never rejects a condition that carries headroom while "
    "the gap detects conditions the pre-check passes. *(Sections 4.4, 5.1)*\n"
    "\n"
    "A supporting contribution is a **reporting standard for latency claims** in this literature.")

# ---------------------------------------------------------------------------
# 6.  §9  the limitations the new analysis implies
# ---------------------------------------------------------------------------
rep(
    "**One convention for latency.** Timings exclude environment advancement and cover the policy "
    "decision only. The three conventions of Section 7 are what make a boundary-stated comparison "
    "reproducible; the measured values are specific to the recorded hardware and library versions "
    "listed in Appendix C.",
    "**The criterion is one-directional, and the pre-check is complementary to it.** A vanishing gap "
    "does not certify that a condition is free of ordering information; only a failed pre-check "
    "certifies that, and the pre-check has its own two thresholds. Seven of the eight condition "
    "groups satisfy at least one of the two diagnoses, and the paper states for each which one "
    "applies rather than treating the two as interchangeable.\n\n"
    "**The censoring statistic is reported in indicator form.** The value decomposition of Eq. (5) "
    "requires $u_t(a^\\rho_t)$, the one-step recovery of the ranker's admissible pick. That quantity "
    "is computed during evaluation and is not persisted for the unscreened arms, whose trajectories "
    "diverge from the screened ones at the first ineffective step, so Section 5.3 reports the "
    "indicators of Eq. (5a) and the released column that realises the conditional override. "
    "Reproducing the value split requires re-running with that column written; Appendix D lists it as "
    "a release requirement.\n\n"
    "**The reduction of Section 4.2 assumes no ineffective step is needed.** Assumption A0 and Lemma "
    "0 make the assumption explicit and show that a policy taking an ineffective step only loses, so "
    "the reduction and Corollary 2 are unaffected. The phenomenon is nonetheless pervasive in the "
    "released records, 51.1% of recorded decision steps being ineffective, and any re-implementation "
    "should verify A0 rather than assume it.\n\n"
    "**The instance rule differs between Section 5.4 and Section 5.6.** Sections 5.4 and 5.5 use "
    "$K \\ge 7$; the phase study of Section 5.6 uses $K \\ge 9$ because it sweeps the budget. The "
    "extreme gap is insensitive to the cut-off in this range, but the budgeted incidence is not (11 of "
    "12 conditions at $K \\ge 7$, 8 of 12 at $K \\ge 8$), so the two tables' samples are stated "
    "separately and neither is extrapolated to the other's cut-off.\n\n"
    "**Three release gaps remain.** The brute-force validation of the coupled recursion is released "
    "as a log rather than as a table; the counterfactual gain column discussed above is missing; and "
    "the instance-selection constant is set in code rather than read from the released metadata. None "
    "of the three affects a reported number, and all three are listed in Appendix D.\n\n"
    "**One convention for latency.** Timings exclude environment advancement and cover the policy "
    "decision only. The three conventions of Section 7 are what make a boundary-stated comparison "
    "reproducible; the measured values are specific to the machine described in Appendix C and to the "
    "library versions listed there.")

# ---------------------------------------------------------------------------
# 7.  §10  repositioned conclusions
# ---------------------------------------------------------------------------
rep(
    "For the class of benchmarks whose service functional depends only on the set of broken lines, "
    "the full-horizon optimum is available by dynamic programming over subsets, costing $O(2^m m)$ "
    "service evaluations and no simulation. The resulting lookahead gap is an exact upper bound on "
    "the benefit of any prioritization policy over a one-step exact rule, and it vanishes exactly "
    "when a condition carries no ordering information. The same number that bounds the value of "
    "learning therefore also certifies whether the benchmark can support a comparison at all. "
    "Verified to machine precision against recorded episodes and against independent brute-force "
    "enumeration, the gap is positive in 11 of 12 conditions under a unified instance rule, and "
    "reaches 120.1 AUC@25 units once resource coupling is imposed.",
    "For the class of benchmarks whose service functional depends only on the set of broken lines, "
    "the full-horizon optimum is available by dynamic programming over subsets, costing $O(2^m m)$ "
    "service evaluations and no simulation. The resulting lookahead gap is an exact upper bound on "
    "the benefit of any prioritization policy over a one-step exact rule, and it is zero exactly when "
    "that rule is optimal. That equivalence does **not** extend to degeneracy: step-wise degeneracy "
    "implies a vanishing gap, but a condition can present a unique best immediate action at 95% of "
    "its steps and still leave the greedy rule globally optimal, and the legacy records contain that "
    "counterexample. The gap is positive in 11 of 12 conditions under a unified instance rule and "
    "reaches 120.1 AUC@25 units once resource coupling is imposed, and it is verified to machine "
    "precision against recorded episodes and against independent brute-force enumeration.",
    )

rep(
    "Finally, the criterion's regime is stated rather than assumed. A four-rule sweep on fixed "
    "instances shows that a positive gap requires line capacities proportional to base-case "
    "utilisation, and that uniform thermal ratings or a dominant capacity floor make it vanish; the "
    "criterion is therefore defined relative to a declared service model, and we declare ours. The "
    "open direction is the one Corollary 4 leaves untouched: where the service functional is not "
    "exactly evaluable, ordering may carry information that no bound of this kind can exclude.",
    "The diagnostic the paper proposes is then stated for what it is. The identifiability pre-check "
    "and the gap are complementary, not interchangeable: over the eight condition groups the "
    "pre-check never rejects a condition that carries headroom, and the gap detects two conditions "
    "that the pre-check passes. A study can therefore adopt the cheap screen, or the complete "
    "criterion, or both, and the paper says which property each one has. The attribution framework is "
    "retained, because the censoring term it isolates is not identically zero on the released "
    "records; its measurable form is the indicator pair of Eq. (5a), and its value form is stated as "
    "an outstanding release item rather than as a result.\n\n"
    "Finally, the criterion's regime is stated rather than assumed. A four-rule sweep on fixed "
    "instances shows that a positive gap requires line capacities proportional to base-case "
    "utilisation, and that uniform thermal ratings or a dominant capacity floor make it vanish; the "
    "criterion is therefore defined relative to a declared service model, and we declare ours. The "
    "open direction is the one Corollary 4 leaves untouched: where the service functional is not "
    "exactly evaluable, ordering may carry information that no bound of this kind can exclude.")

# ---------------------------------------------------------------------------
# 8.  Highlights
# ---------------------------------------------------------------------------
rep(
    "- An attribution framework separates ranking error from admissibility censoring\n"
    "- The lookahead gap exactly bounds any prioritization policy's benefit\n"
    "- A depth profile separates a gap's value from how cheaply it can be realised\n"
    "- A rolling depth-2 rule captures 99%+ of the gap and beats learned rankers\n"
    "- A four-rule sweep locates the capacity rule that makes the gap non-trivial",
    "- Attribution separates ranking error from admissibility censoring\n"
    "- Step-wise degeneracy implies a vanishing gap, but not the converse\n"
    "- The pre-check and the gap are complementary, not equivalent\n"
    "- A depth profile separates a gap's value from how cheaply it is realised\n"
    "- A rolling depth-2 rule captures 99%+ of the gap and beats learned rankers")

# ---------------------------------------------------------------------------
# 9.  Appendix D  release requirements and the variable-name map
# ---------------------------------------------------------------------------
rep(
    "- the nine figures of the paper, each regenerated from the released tables by "
    "`supp_code/make_figures_submission.py`, whose accompanying `figures/MANIFEST.txt` names the "
    "input file of every panel.",
    "- the nine figures of the paper, each regenerated from the released tables by "
    "`supp_code/make_figures_submission.py`, whose accompanying `figures/MANIFEST.txt` names the "
    "input file of every panel;\n"
    "- `bruteforce_validation.log`, recording the command, seed, environment and enumeration count of "
    "the brute-force check on the coupled recursion, and the capacity-rule recomputation of "
    "Section 6.1;\n"
    "- `claims_evidence.csv`, one row per claim of the paper, naming the section, the assumption it "
    "rests on, the code that produces it, the command that reproduces it and its status;\n"
    "- `session_info.txt`, the frozen commit, the random seeds and the SHA-256 digest of every released "
    "table; and `Makefile`, whose `make reproduce` target regenerates every table and figure.\n\n"
    "**Table 12.** Quantity-to-column map for the attribution of Section 5.3. Every name on the left "
    "is a quantity defined in Section 3; the column on the right is where the released traces record "
    "it, and the two are kept apart because an earlier draft labelled a table column after the wrong "
    "one.\n\n"
    "| Quantity (Section 3) | Released column |\n"
    "|---|---|\n"
    "| Ranking fidelity | `best_rank_in_q == 1` |\n"
    "| Censoring rate $C_t$ | `chosen_is_candidate == False` |\n"
    "| Screen override $C^{\\mathrm{screen}}_t$ | `best_rank_in_q == 1 & ~top1_hit & "
    "chosen_rank_in_q == 1` |\n"
    "| Executed action's recovery $u_t(\\hat a_t)$ | `realized_gain_mw` |\n"
    "| Oracle recovery $u^\\star_t$ | `best_gain_mw` |\n"
    "| Stepwise regret $\\delta_t$ | `regret_mw` |\n"
    "| Counterfactual $u_t(a^\\rho_t)$ | **not persisted** (release requirement) |")


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
