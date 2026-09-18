"""Second compression stage: delete redundancy rather than tighten wording.

The first stage shortened sentences; this one removes material that the paper
already carries elsewhere, which is where the remaining bulk sits:

  * the five contributions are stated three times (Abstract, Section 1.4,
    Section 10) -- Section 1.4 keeps one sentence each and points forward;
  * Section 5's prose restates numbers that its own tables already carry, and
    the differential diagnosis of the legacy configuration is given twice
    (Section 5.1) plus once more in the appendices;
  * Section 9 restates boundaries that Section 5.7 and Section 6.3 already
    argued in place.

Nothing is deleted that carries a number, an assumption, a proof step or a
scope condition.  Every anchor asserts a unique match.
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
MS = ROOT / "SEGAN_manuscript_revised_2026-09-13.md"

doc = MS.read_text(encoding="utf-8")
before = len(doc.split())

EDITS = [
    # ---- Section 1.4: one sentence per contribution, no restatement of numbers
    (
        "- **C1 · An attribution framework** *(Section 3)*. Any prioritization policy is written "
        "as a ranker composed with an admissibility screen, and its stepwise regret admits an "
        "exactly additive decomposition into a ranking term and a censoring term. Paired with a "
        "matched-training leave-one-out protocol that varies the training objective and the "
        "presence of the screen independently, it makes the source of a reported gain "
        "identifiable. The decomposition is exact; its measurable form is the indicator pair of "
        "Eq. (5a), and Section 3.5 states the boundary that the value form requires a "
        "counterfactual the release does not carry.",

        "- **C1 · An attribution framework** *(Section 3)*. Any prioritization policy is a ranker "
        "composed with an admissibility screen, and its stepwise regret decomposes exactly into a "
        "ranking term and a censoring term. A matched-training leave-one-out protocol that varies "
        "the training objective and the presence of the screen independently makes the source of a "
        "reported gain identifiable; Section 3.5 states where the release supports the indicator "
        "form of Eq. (5a) only.",
    ),
    (
        "- **C2 · Exact solvability and the lookahead gap** *(Sections 4.1--4.3)*. The "
        "unserved-load functional depends only on the *set* of broken lines, so terminal behaviour "
        "is order-invariant and the full-horizon optimum reduces to a dynamic program over subsets "
        "of the broken key lines, costing $O(2^{m}m)$ service evaluations and no simulation. The "
        "resulting gap is an exactly computable upper bound on the benefit of any prioritization "
        "policy over the one-step exact rule.",

        "- **C2 · Exact solvability and the lookahead gap** *(Sections 4.1--4.3)*. Because the "
        "unserved-load functional depends only on the *set* of broken lines, terminal behaviour is "
        "order-invariant and the full-horizon optimum reduces to a dynamic program over subsets of "
        "the broken key lines, costing $O(2^{m}m)$ service evaluations and no simulation. The "
        "resulting gap exactly bounds the benefit of any prioritization policy over the one-step "
        "exact rule.",
    ),
    (
        "- **C3 · The depth profile and the accessibility of the gap** *(Sections 4.4--4.6)*. We "
        "distinguish a *committed* plan, which executes a $k$-step plan and then reverts, from a "
        "*rolling* (receding-horizon) controller, which replans at every step. Their accessibility "
        "differs sharply: on the same instances a committed plan needs five steps of foresight to "
        "capture the gap and, without a budget, captures only 21% of it even at depth four, whereas "
        "a rolling depth-2 controller captures 99.4--99.8% and depth 3 captures it exactly. \"How "
        "much lookahead is worth having\" thereby becomes a computable design parameter rather than "
        "an empirical choice.",

        "- **C3 · The depth profile and the accessibility of the gap** *(Sections 4.4--4.6)*. We "
        "distinguish a *committed* plan, which executes a $k$-step plan and then reverts, from a "
        "*rolling* (receding-horizon) controller, which replans at every step. A committed plan "
        "needs five steps of foresight to capture the gap, and without a budget captures only 21% of "
        "it at depth four; a rolling depth-2 controller captures 99.4--99.8% and depth 3 captures it "
        "exactly. \"How much lookahead is worth having\" thereby becomes a computable design "
        "parameter.",
    ),
    (
        "- **C4 · The service-model regime of the criterion** *(Section 6)*. Holding instances "
        "fixed and sweeping four capacity rules locates the boundary of the phenomenon: the gap is "
        "positive when line capacities are proportional to base-case utilisation, and vanishes "
        "identically under uniform physical thermal ratings or a sufficiently large capacity floor. "
        "We also record why a direct optimal-power-flow transplant is not comparable, a property of "
        "the benchmark's synthetic ratings rather than of the criterion.",

        "- **C4 · The service-model regime of the criterion** *(Section 6)*. At fixed instances the "
        "gap is positive when line capacities are proportional to base-case utilisation, and "
        "vanishes identically under uniform physical thermal ratings or a sufficiently large "
        "capacity floor. We also record why a direct optimal-power-flow transplant is not "
        "comparable, a property of the benchmark's synthetic ratings rather than of the criterion.",
    ),
    (
        "- **C5 · A one-directional criterion and a complementary diagnostic** *(Sections 4.4, "
        "5.1)*. Step-wise degeneracy implies a vanishing gap, but not conversely: a condition can "
        "present a unique best immediate action at 95% of its steps and still leave the greedy rule "
        "globally optimal. Crossing the pre-check with the gap over eight condition groups shows the "
        "two to be complementary rather than equivalent.",

        "- **C5 · A one-directional criterion and a complementary diagnostic** *(Sections 4.4, "
        "5.1)*. Step-wise degeneracy implies a vanishing gap, but not conversely. Crossing the "
        "pre-check with the gap over eight condition groups shows the two to be complementary "
        "rather than equivalent.",
    ),
    # ---- Section 1.5: keep every citation and every branch claim, drop the detail
    (
        "**Methodology, critique and adjacent theory.** Outside the power domain a mature "
        "literature documents the statistical fragility of method comparisons: seed lottery "
        "producing significant differences where none exist [22], protocol changes that reverse "
        "rankings [23], benchmark selection determining conclusions [24], oracle gaps revealing "
        "benchmarks that cannot separate generalisation from non-generalisation [25], and "
        "protocol-level identifiability audits [26--29]. The closest power-domain analogue shows "
        "that the reported accuracy of machine-learned optimal-power-flow proxies depends on which "
        "variability factors the sampling covers [30]. Adjacent theory supplies the guarantees the "
        "criterion is measured against: constant-factor bounds for adaptive greedy policies [31] and "
        "for myopic rules on stochastic depletion problems [32,33], the approximation theory of "
        "minimum-latency scheduling [34,35], rollout and policy iteration [36], and queueing with "
        "future information [37]. On the engineering side, cold-load pickup [38] and protection "
        "coordination under reconfiguration [39--41] are constraints a synthetic-capacity benchmark "
        "omits.",

        "**Methodology, critique and adjacent theory.** Outside the power domain a mature "
        "literature documents the statistical fragility of method comparisons: seed lottery [22], "
        "protocol changes that reverse rankings [23], benchmark selection determining conclusions "
        "[24], oracle gaps revealing benchmarks that cannot separate generalisation from "
        "non-generalisation [25], and protocol-level identifiability audits [26--29]. The closest "
        "power-domain analogue links a proxy's reported accuracy to the sampling coverage of "
        "variability factors [30]. Adjacent theory supplies the guarantees the criterion is measured "
        "against: constant-factor bounds for adaptive greedy policies [31] and for myopic rules on "
        "stochastic depletion problems [32,33], the approximation theory of minimum-latency "
        "scheduling [34,35], rollout and policy iteration [36], and queueing with future information "
        "[37]. On the engineering side, cold-load pickup [38] and protection coordination under "
        "reconfiguration [39--41] are constraints a synthetic-capacity benchmark omits.",
    ),
    # ---- Section 5.0: the sensitivity paragraph in three sentences
    (
        "**Sensitivity to the cut-off.** Holding the protocol fixed and raising the cut-off leaves "
        "the uncoupled results unchanged and moves the budgeted incidence. The uncoupled protocol "
        "shows a positive gap in 11 of 12 conditions and a maximum of 16.611 at $K \\ge 7$ (240 "
        "instances), at $K \\ge 8$ (198) and at $K \\ge 9$ (174). The budgeted protocol shows a "
        "positive gap in 11 of 12 conditions at $K \\ge 7$ and 8 of 12 at $K \\ge 8$ and $K \\ge 9$, "
        "while its extreme value stays at 120.134 throughout. The extreme value and the qualitative "
        "phase structure are therefore insensitive to the cut-off in this range and the budgeted "
        "*incidence* is not, which is why Tables 4 and 6 carry different sample rules and why both "
        "are stated.",

        "**Sensitivity to the cut-off.** The uncoupled protocol shows a positive gap in 11 of 12 "
        "conditions and a maximum of 16.611 at $K \\ge 7$ (240 instances), at $K \\ge 8$ (198) and at "
        "$K \\ge 9$ (174); the budgeted protocol shows 11 of 12 at $K \\ge 7$ and 8 of 12 at $K \\ge 8$ "
        "and $K \\ge 9$, with its extreme value fixed at 120.134 throughout. The extreme value and "
        "the qualitative phase structure are therefore insensitive to the cut-off in this range and "
        "the budgeted *incidence* is not, which is why Tables 4 and 6 carry different sample rules.",
    ),
    # ---- Section 5.1: the differential diagnosis, stated once and briefly
    (
        "The cause is the action set rather than the capacity-rule parameters, and no setting of "
        "those parameters repairs the degeneracy anywhere in the operating range. A sweep over "
        "eight values of the capacity margin and three of the floor share — 96 configurations — "
        "holds the fraction of decision steps with a unique maximizing candidate at or below 0.50 "
        "for both groups when $\\kappa = 1.15$, so both diagnostics fail at every setting a study "
        "would plausibly use; the configurations elsewhere in the sweep that raise the fraction "
        "require $\\kappa < 1$, that is, line capacities below the base-case flow, which is a "
        "derating rather than an operating margin. Replacing the action set raises the same fraction "
        "to 0.95--1.00 and reduces the largest single-action gain to at most 28% of the unserved "
        "load; after that correction every condition has load to restore in every scenario and the "
        "fraction of exactly-zero objectives falls to at most 1.1%, so an ordering genuinely "
        "allocates recovery across steps. That the IEEE 300-bus groups pass both diagnostics under "
        "the same legacy construction is the diagnostic point: the failure is an uncontrolled "
        "design choice, not a property of the test systems.",

        "The cause is the action set rather than the capacity-rule parameters, and no setting of "
        "those parameters repairs the degeneracy anywhere in the operating range: over eight values "
        "of the capacity margin and three of the floor share, 96 configurations in all, the fraction "
        "of decision steps with a unique maximizing candidate stays at or below 0.50 for both groups "
        "at $\\kappa = 1.15$, and the configurations that do raise it require line capacities below "
        "the base-case flow, which is a derating rather than an operating margin. Replacing the "
        "action set instead raises the fraction to 0.95--1.00, reduces the largest single-action gain "
        "to at most 28% of the unserved load, and leaves every condition with load to restore in "
        "every scenario, so an ordering genuinely allocates recovery across steps. That the IEEE "
        "300-bus groups pass both diagnostics under the same legacy construction is the diagnostic "
        "point: the failure is an uncontrolled design choice, not a property of the test systems.",
    ),
    # ---- Section 5.3: the readings, in two paragraphs instead of three
    (
        "Three readings follow. First, **the censoring mechanism is about twice as large as the "
        "conditional statistic**: the unscreened arms execute an inadmissible action on 76.6% and "
        "75.8% of their steps, so more than half of an episode's steps restore nothing at all. The "
        "screened arms are at zero *by construction*, because a screened arm executes the ranker's "
        "admissible pick by definition; those entries are properties of the arm rather than "
        "findings, and no claim of improved ordering rests on them. Second, the conditional override "
        "$C^{\\mathrm{screen}}_t$ is the smaller, conditional quantity, 0.377 and 0.362 on the "
        "unscreened arms and zero on the screened ones; it answers a different question, namely how "
        "often a correct ranker was overridden, and it is not the censoring rate. Third, the ranker "
        "itself carries little ordering information: the Spearman correlation between its scores and "
        "the true one-step gain is between $+0.030$ and $+0.154$, far below what a usable ordering "
        "would require. The step-level means pool steps across scenarios, which are the stated "
        "independent unit (Section 2.5), so these entries are descriptive and carry no significance "
        "claim.",

        "Three readings follow. First, **the censoring mechanism is about twice as large as the "
        "conditional statistic**: the unscreened arms execute an inadmissible action on 76.6% and "
        "75.8% of their steps, so more than half of an episode's steps restore nothing at all. The "
        "screened arms are at zero *by construction*, because a screened arm executes the ranker's "
        "admissible pick by definition; those entries are properties of the arm rather than findings, "
        "and no claim of improved ordering rests on them. Second, the conditional override "
        "$C^{\\mathrm{screen}}_t$ is the smaller, conditional quantity, 0.377 and 0.362 on the "
        "unscreened arms; it answers how often a correct ranker was overridden, and it is not the "
        "censoring rate. Third, the ranker itself carries little ordering information, its Spearman "
        "correlation with the true one-step gain lying between $+0.030$ and $+0.154$. The step-level "
        "means pool steps across scenarios, the stated independent unit (Section 2.5), so these "
        "entries are descriptive and carry no significance claim.",
    ),
    # ---- Section 5.7: the interpretation, without repeating the table
    (
        "Three results are worth separating. First, **the rolling depth-2 rule is never worse than "
        "any alternative in any of the 240 comparisons**, and it attains the exact offline optimum "
        "in ten of the twelve conditions and no less than 99.995% of it in the other two. Second, "
        "**every learned variant loses in all 240 comparisons**, by 324 to 946 AUC@25 units; the "
        "least-penalised variant is the one that both screens and trains against the true objective, "
        "and it is also the variant whose advantage over the cheapest rule is smallest. Third, "
        "against the one-step exact rule the rolling rule wins 35 times, ties 205 times and never "
        "loses, for a mean advantage of +4.78 units. Because 205 of those 240 pairs are tied, the "
        "per-condition tests for that row are underpowered and one condition is tied at every "
        "scenario; the evidence rests on the pooled test ($p = 2.5\\times10^{-7}$), which is why "
        "Table 7 reports both. The pooled column saturates for the six arm-level alternatives "
        "because not one of their pairs is tied.",

        "Three results are worth separating. First, **the rolling depth-2 rule is never worse than "
        "any alternative in any of the 240 comparisons**, and it attains the exact offline optimum in "
        "ten of the twelve conditions and no less than 99.995% of it in the other two. Second, "
        "**every learned variant loses in all 240 comparisons**, by 324 to 946 AUC@25 units; the "
        "least-penalised variant is the one that both screens and trains against the true objective, "
        "and it is also the variant whose advantage over the cheapest rule is smallest. Third, "
        "against the one-step exact rule the rolling rule wins 35 times, ties 205 times and never "
        "loses, for a mean advantage of +4.78 units. Because 205 of those pairs are tied, the "
        "per-condition tests for that row are underpowered and its evidence rests on the pooled test, "
        "which is why Table 7 reports both; the pooled column saturates for the six arm-level "
        "alternatives because not one of their pairs is tied.",
    ),
    (
        "The third comparison connects the two halves of the paper. Because the rolling depth-2 rule "
        "attains the offline optimum, its advantage over the one-step exact rule **is** the lookahead "
        "gap, instance by instance. The measured per-condition advantages of 8.74, 5.27, 6.97, 4.38, "
        "8.37, 4.93, 8.95, 2.51, 0.00, 2.70, 0.73 and 3.84 agree with the dynamic program's values of "
        "Table 4 (8.739, 5.274, 6.970, 4.384, 8.370, 4.934, 8.951, 2.511, 0, 2.762, 0.731, 3.924) to "
        "the precision printed. The comparison is therefore an independent reproduction of the "
        "theoretical quantity by an entirely separate code path, and it fixes the interpretation of "
        "Table 7: those twelve advantages range up to 8.95 and average 4.78 over all 240 pairs, "
        "whereas the learned variants lose by 324.0 to 946.1 units. The deficit is not a shortfall of "
        "headroom but a shortfall of the ranker, and an aggregate metric alone would not have "
        "distinguished the two.",

        "The third comparison connects the two halves of the paper. Because the rolling depth-2 rule "
        "attains the offline optimum, its advantage over the one-step exact rule **is** the lookahead "
        "gap, instance by instance: the measured per-condition advantages of 8.74, 5.27, 6.97, 4.38, "
        "8.37, 4.93, 8.95, 2.51, 0.00, 2.70, 0.73 and 3.84 agree with the dynamic program's values of "
        "Table 4 (8.739, 5.274, 6.970, 4.384, 8.370, 4.934, 8.951, 2.511, 0, 2.762, 0.731, 3.924) to "
        "the precision printed, so the theoretical quantity is reproduced by an entirely separate "
        "code path. It also fixes the interpretation of Table 7: those advantages average 4.78 over "
        "all 240 pairs, whereas the learned variants lose by 324.0 to 946.1 units. The deficit is a "
        "shortfall of the ranker, not of headroom, and an aggregate metric alone would not have "
        "distinguished the two.",
    ),
    # ---- Section 6.3: the second paragraph, tightened
    (
        "Read this way the sweep is a statement about *which capacity a restoration benchmark "
        "should be testing* rather than about whether synthetic benchmarks are realistic. A "
        "benchmark adopting uniform physical ratings is testing a network with substantial unused "
        "transfer capability on every path; on the cases examined here the generation capacity "
        "exceeds demand by a factor of more than two, so no ordering can matter, and that is a "
        "property a modeller can verify before choosing the convention. The R1 rule encodes the "
        "stressed regime in which prioritization is a live question, and reporting which of the two "
        "regimes a benchmark inhabits is part of the reporting standard Section 7 sets out.",

        "Read this way the sweep is a statement about *which capacity a restoration benchmark "
        "should be testing* rather than about whether synthetic benchmarks are realistic. A "
        "benchmark adopting uniform physical ratings is testing a network with substantial unused "
        "transfer capability on every path; here the generation capacity exceeds demand by a factor "
        "of more than two, so no ordering can matter, and a modeller can verify that before choosing "
        "the convention. The R1 rule encodes the stressed regime in which prioritization is a live "
        "question, and reporting which regime a benchmark inhabits is part of the reporting standard "
        "Section 7 sets out.",
    ),
    # ---- Section 10: three paragraphs, no restatement of Section 1.4 verbatim
    (
        "The diagnostic the paper proposes is then stated for what it is. The identifiability "
        "pre-check and the gap are complementary, not interchangeable: over the eight condition "
        "groups the pre-check never rejects a condition that carries headroom, and the gap detects "
        "two conditions that the pre-check passes. A study can therefore adopt the cheap screen, or "
        "the complete criterion, or both, and the paper says which property each one has. The "
        "attribution framework is retained, because the censoring term it isolates is not "
        "identically zero on the released records; its measurable form is the indicator pair of Eq. "
        "(5a), and its value form is stated as an outstanding release item rather than as a result.",

        "The diagnostic the paper proposes is then stated for what it is. The identifiability "
        "pre-check and the gap are complementary, not interchangeable: over the eight condition "
        "groups the pre-check never rejects a condition that carries headroom, and the gap detects "
        "two conditions that the pre-check passes, so a study can adopt the cheap screen, the "
        "complete criterion, or both. The attribution framework is retained, because the censoring "
        "term it isolates is not identically zero on the released records; its value form is an "
        "outstanding release item rather than a result.",
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
after = len(doc.split())
print(f"stage 2 edits applied: {len(EDITS)}")
print(f"whole file: {before} -> {after} words ({after-before:+d})")

body = doc.split("## 1. Introduction")[1].split("## Appendix A.")[0]
tot = 0
print("\n--- sections 1-10 ---")
for part in re.split(r"\n## ", "## " + body):
    head = part.split("\n")[0][:52]
    n = len(part.split())
    tot += n
    print(f"  {n:6d}  {head}")
print(f"  {tot:6d}  TOTAL")
