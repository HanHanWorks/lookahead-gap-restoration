## 5. Numerical verification

### 5.0 Setting and sample rules

**Test systems and conditions.** Three public test systems: the IEEE 118-bus and IEEE 300-bus systems, and a 200-bus Illinois system, all built from `pandapower` standard cases. Each of the first two is crossed with two severity levels and three capacity margins $\kappa \in \{1.15, 1.25, 1.50\}$, giving **twelve conditions**. The action set $\mathcal{K}$ holds $n_a = 20$ switchable key lines per system.

**Protocols.** The **legacy protocol** is the capacity and action-set configuration inherited from an earlier study, with $\phi = 0.01$; the **main protocol** uses $\phi = 0.002$ and a service-criticality action set (Table 1). The main protocol comprises 9,600 episodes and **147,132 recorded decision steps**; the legacy protocol 9,600 episodes and **135,297 decision steps**. All frozen records, action-set artifacts and trained models are released (Appendix D).

**Instance-selection rule.** Any distribution of the gap is meaningless without the rule that selected the instances, and the rule must not depend on the quantity being swept. Sections 5.4 and 5.5 use a single protocol-independent rule, **$K \ge 7$ broken key lines with $K \le 12$**, applied identically to both protocols and to every budget; the phase study of Section 5.6 draws its own sample, **$K \ge 9$**, because it sweeps the budget and needs the budget to bind. **Sensitivity to the cut-off.** The uncoupled protocol shows a positive gap in 11 of 12 conditions and a maximum of 16.611 at $K \ge 7$ (240 instances), at $K \ge 8$ (198) and at $K \ge 9$ (174); the budgeted protocol shows 11 of 12 at $K \ge 7$ and 8 of 12 at $K \ge 8$ and $K \ge 9$, with its extreme value fixed at 120.134 throughout. The extreme value and the qualitative phase structure are therefore insensitive to the cut-off in this range and the budgeted *incidence* is not, which is why Tables 4 and 6 carry different sample rules.

### 5.1 The identifiability pre-check, applied to a benchmark

**Table 2.** Identifiability diagnostics, read against the gap. "scenarios with load" is the fraction of scenarios with positive initial unserved load; "AUC = 0" is the fraction of episodes whose recorded objective is exactly zero; "unique maximizer" is the fraction of decision steps at which the maximizing admissible candidate is unique. The last two columns put the verdict of Section 2.6 beside the size of the gap, which is what makes the two diagnoses comparable; the pre-check diagnostics are taken at the nominal margin $\kappa = 1.15$ and the "scenarios with load" and "AUC = 0" columns span the three margins, hence their ranges.

| Protocol | Condition group | Scenarios with load | AUC = 0 | Unique maximizer | Largest single-action gain / initial unserved | Max $\Gamma_{\mathrm{LA}}$ | Pre-check verdict |
|---|---|---|---|---|---|---|---|
| Legacy | IEEE 118 moderate | 0.40 | **0.710** | 0.30 | 1.00 | **0.000** | non-identifiable |
| Legacy | IEEE 118 severe | 0.68--0.70 | **0.485** | 0.55 | 0.87 | **0.000** | non-identifiable |
| Legacy | IEEE 300 moderate | 0.92 | 0.154--0.161 | 0.954 | 0.42 | **0.000** | identifiable |
| Legacy | IEEE 300 severe | 1.00 | 0.015 | 1.00 | 0.28 | **0.000** | identifiable |
| Main | IEEE 118 moderate | **1.00** | **0.000** | 0.95 | 0.23 | 15.685 | identifiable |
| Main | IEEE 118 severe | **1.00** | 0.011 | 1.00 | 0.15 | 16.611 | identifiable |
| Main | IEEE 300 moderate | **1.00** | 0.006--0.008 | 1.00 | 0.28 | 11.594 | identifiable |
| Main | IEEE 300 severe | **1.00** | 0.001 | 1.00 | 0.16 | 8.601 | identifiable |

Two features of the legacy configuration make its IEEE 118-bus conditions uninformative about ordering, and both diagnostics of Section 2.6 fail. First, 60% of the moderate-condition scenarios and 31% of the severe-condition scenarios have *no* unserved load at all, so there is nothing to restore, and 71% of the moderate-condition episodes record an objective of exactly zero. Second, where load is unserved a single admissible action recovers essentially all of it: the largest single-action gain equals the initial unserved load in the moderate group and 87% of it in the severe group. Neither feature leaves an ordering decision anything to distribute, and the maximizing candidate is unique at only 30% and 55% of decision steps respectively.

The cause is the action set rather than the capacity-rule parameters, and no setting of those parameters repairs the degeneracy anywhere in the operating range: over eight values of the capacity margin and three of the floor share, 96 configurations in all, the fraction of decision steps with a unique maximizing candidate stays at or below 0.50 for both groups at $\kappa = 1.15$, and the configurations that do raise it require line capacities below the base-case flow, which is a derating rather than an operating margin. Replacing the action set instead raises the fraction to 0.95--1.00, reduces the largest single-action gain to at most 28% of the unserved load, and leaves every condition with load to restore in every scenario, so an ordering genuinely allocates recovery across steps. That the IEEE 300-bus groups pass both diagnostics under the same legacy construction is the diagnostic point: the failure is an uncontrolled design choice, not a property of the test systems.

**The pre-check and the gap are complementary, and the contingency shows in which sense.** Crossing the verdict of Section 2.6 with the size of the gap over the eight condition groups gives

$$\underbrace{2}_{\text{rejects},\ \Gamma_{\mathrm{LA}}=0} \quad
\underbrace{0}_{\text{rejects},\ \Gamma_{\mathrm{LA}}>0} \qquad
\underbrace{2}_{\text{passes},\ \Gamma_{\mathrm{LA}}=0} \quad
\underbrace{4}_{\text{passes},\ \Gamma_{\mathrm{LA}}>0}.$$

The cell $(\text{rejects}, \Gamma_{\mathrm{LA}}>0)$ is empty over every group examined, so **the pre-check never rejects a condition that carries headroom** and can be used as a gate without discarding a condition worth studying. But it passes two conditions whose gap is identically zero (the two legacy IEEE 300-bus groups), which the gap flags, so it is **not equivalent to the gap and not stronger than it**. Neither test subsumes the other, and the two are reported as **complementary diagnostics** — the pre-check cheap, conservative and needing no dynamic program, the gap complete but costing a dynamic program per condition. Calling either "strictly stronger" would be wrong in one direction or the other, and the one-directional Corollary 3 is exactly the statement of which direction holds.

### 5.2 Lemma 1 in the data

Because the unserved-load functional depends only on the set of broken lines, terminal behaviour cannot separate reconnection orders. The prediction is sharp and can be checked exactly: across 600 scenarios the terminal recovery of the electrical-priority rule, the risk-only rule and the one-step exact rule agree to **0.0 percentage points in every scenario**, with no exceptions.

### 5.3 Attribution: the screen, not the ranker

**Table 3.** Attribution of stepwise regret, over the released decision traces of the main protocol. Recorded decisions differ by arm because the screens change which steps are recorded; no arm contains a step at which the admissible set is empty, so each arm's decomposition is defined on its own recorded steps. Every column name is the name of the *quantity*; Table 10 of Appendix D maps each to the released column that realises it. $C_t$ is the censoring rate of Eq. (5a); $C^{\mathrm{screen}}_t$ is the conditional screen override. Entries marked *by construction* are zero because of how the arm is defined, not because of a measurement. Figure 2 plots the same quantities.

| Arm | Recorded decisions | Ranking fidelity | Censoring rate $C_t$ | Screen override $C^{\mathrm{screen}}_t$ | Regret share from ranking | Spearman (Q, one-step gain) |
|---|---|---|---|---|---|---|
| Learned ranker, no screen | 42,567 | 0.418 | **0.766** | 0.377 | 0.646 | +0.154 |
| Learned ranker, screened | 15,912 | 0.312 | **0.000** *(by construction)* | **0.000** *(by construction)* | **1.000** | +0.030 |
| True-objective ranker, no screen | 42,285 | 0.418 | **0.758** | 0.362 | 0.664 | +0.091 |
| True-objective ranker, screened | 15,912 | 0.330 | **0.000** *(by construction)* | **0.000** *(by construction)* | **1.000** | +0.076 |

Three readings follow. First, **the censoring mechanism is about twice as large as the conditional statistic**: the unscreened arms execute an inadmissible action on 76.6% and 75.8% of their steps, so more than half of an episode's steps restore nothing at all. The screened arms are at zero *by construction*, because a screened arm executes the ranker's admissible pick by definition; those entries are properties of the arm rather than findings, and no claim of improved ordering rests on them. Second, the conditional override $C^{\mathrm{screen}}_t$ is the smaller, conditional quantity, 0.377 and 0.362 on the unscreened arms; it answers how often a correct ranker was overridden, and it is not the censoring rate. Third, the ranker itself carries little ordering information, its Spearman correlation with the true one-step gain lying between $+0.030$ and $+0.154$. The step-level means pool steps across scenarios, the stated independent unit (Section 2.5), so these entries are descriptive and carry no significance claim.

**Episode-level censoring, and why the arms are not paired.** The arms' percentages are not directly comparable, because an episode of an unscreened arm lasts 23.65 recorded decisions on average against 8.84 for a screened arm: a screened episode ends as soon as the admissible set is exhausted, so the arms cover the same episodes with different step counts. Restating the quantity per episode, $r_e = (\text{inadmissible steps in } e)/(\text{recorded steps in } e)$, and resampling scenarios gives an episode mean of $0.731$ for the learned ranker without a screen (median $0.760$, interquartile range $0.68$--$0.84$) and a pooled rate of $0.766$ with a cluster-bootstrap 95% interval of $[0.758, 0.775]$; for the true-objective ranker without a screen, mean $0.722$ and pooled rate $0.758$ with interval $[0.749, 0.767]$. Both screened arms are exactly zero with a degenerate interval, by construction. A paired arm-to-arm test is not identified here, because the arms diverge at the first ineffective step and the surviving steps are not the same steps, so pairing them would compare different states; the four arms are therefore reported per arm, and the arm-level difference is described rather than tested. The ranker's deficit is not a consequence of little being at stake, since Section 5.4 shows headroom in 11 of the 12 conditions and Section 5.7 shows that a rule which uses it reaches the offline optimum: the deficit is a property of the ranker, and an aggregate metric would have concealed which of the two it was.

### 5.4 Proposition 2 verified, and the gap it defines

**Implementation check.** The recursion of Eq. (7) must reproduce an independently recorded quantity, and it does: the reconstructed objective of the one-step exact rule matches the frozen gap values to a maximum absolute difference of **0.000000000**, over 24 instances under the legacy rule and 18 under the unified rule. The coupled variant is checked from both sides rather than enumerated: on all 24 released instance-depth records the rolling controller's objective stays inside $[J(\pi^{\mathrm{my}}), f(\emptyset)]$, the interval the recursion defines, with a maximum excess over the static plan of $+15.970$. Appendix B names the artifact behind each record.

**Table 4.** Lookahead gap by condition under the unified instance rule ($K \ge 7$), 20 instances per condition, both protocols. AUC@25 units. Figure 3 plots it, one panel per protocol so that the two magnitudes remain legible.

| Condition | Uncoupled mean / max | Nonzero | $d_{90}$ | Budget $B=6$ mean / max | Nonzero | $d_{90}$ |
|---|---|---|---|---|---|---|
| IEEE 118 moderate 1.15 | 0.356 / 2.447 | 4/20 | 4.5 | **8.739** / 51.271 | 6/20 | 3.0 |
| IEEE 118 moderate 1.25 | 0.186 / 3.711 | 1/20 | 7.0 | 5.274 / 60.388 | 2/20 | 4.5 |
| IEEE 118 moderate 1.50 | 0.784 / **15.685** | 1/20 | 7.0 | 6.970 / 92.235 | 2/20 | 4.5 |
| IEEE 118 severe 1.15 | 0.732 / 3.300 | 9/20 | 6.0 | 4.384 / 34.493 | 4/20 | 3.5 |
| IEEE 118 severe 1.25 | 1.536 / 9.844 | 7/20 | 8.0 | 8.370 / **120.134** | 4/20 | 5.0 |
| IEEE 118 severe 1.50 | 2.072 / 16.611 | 7/20 | 7.0 | 4.934 / 73.670 | 3/20 | 5.0 |
| IEEE 300 moderate 1.15 | 0.838 / **11.594** | 2/20 | 4.0 | 8.951 / **117.353** | 2/20 | 2.0 |
| IEEE 300 moderate 1.25 | 0.248 / 4.964 | 1/20 | 7.0 | 2.511 / 50.212 | 1/20 | 5.0 |
| IEEE 300 moderate 1.50 | 0.000 / 0.000 | 0/20 | n/a | 0.000 / 0.000 | 0/20 | n/a |
| IEEE 300 severe 1.15 | 1.489 / 8.601 | 10/20 | 6.5 | 2.762 / 50.840 | 4/20 | 4.0 |
| IEEE 300 severe 1.25 | 1.284 / 8.475 | 7/20 | 7.0 | 0.731 / 11.731 | 3/20 | 3.0 |
| IEEE 300 severe 1.50 | 0.951 / 9.653 | 4/20 | 4.5 | 3.924 / 59.971 | 4/20 | 3.5 |

**The instance rule carries part of the result.** A sampling rule that admitted an instance whenever it had a broken key line at all for the uncoupled protocol, while the budgeted protocol necessarily required $K > B$, let the two protocols draw different instances; the uncoupled protocol then appeared to have almost no headroom, with only 7 of 12 conditions positive and the moderate conditions apparently at zero. Under the unified rule both protocols exhibit a positive gap in **11 of 12 conditions**, and the moderate conditions are not exceptional: the largest uncoupled gaps fall on IEEE 118 moderate 1.50 (15.685) and IEEE 300 moderate 1.15 (11.594), both of which read as zero under the old rule. **A statement about which conditions carry ordering information is therefore a statement about the instance rule as much as about the system**, the design-time lesson of Corollary 3. Figure 4 isolates the effect.

**What the budget changes is magnitude and accessibility, not incidence.** Imposing a reconnection budget of $B = 6$ against $m \approx 11.9$ broken key lines multiplies the extreme value by 7.2 (16.611 to **120.134**) and moves the median depth-to-90% from 7.0 to 4.0. The budget also restores the terminal term: with $B < m$ the terminal set is itself a decision, and the terminal-recovery gap between the one-step exact rule and the optimum averages **17.4 percentage points** over all conditions (80.2% versus 97.6%) and reaches **27.9 percentage points** in the most affected one (IEEE 118 severe at $\kappa = 1.15$: 69.3% versus 97.1%).

### 5.5 The depth profile, and the accessibility of the gap

**Table 5.** Realizing the gap. Share of $\Gamma_{\mathrm{LA}}$ captured, mean over instances with $\Gamma_{\mathrm{LA}} > 0$ within each protocol (22 instances across 6 conditions, budgeted; 44 across 6 conditions, uncoupled). All twelve condition groups are evaluated, but every instance with a positive gap falls in a **severe** group, so the profile is estimated on the severe half of the condition grid; Section 9 records this as a limitation. Figure 5 plots it.

| Controller | Depth 1 | Depth 2 | Depth 3 | Depth 4 | Depth 5 |
|---|---|---|---|---|---|
| Committed plan, budget $B=6$ | 11% | 28% | 61% | 81% | **100%** |
| **Rolling, budget $B=6$** | **56%** | **99.8%** | **100%** | 100% | 100% |
| Committed plan, uncoupled | 0.3% | 5% | 15% | 21% | n/a |
| **Rolling, uncoupled** | **62%** | **99.4%** | **100%** | 100% | n/a |

Measured against the offline optimum rather than against the gap, the rolling controller at depth 2 already attains a mean of 99.99% of the exact optimum in the budgeted setting and 99.998% without a budget, and it is exact at depth 3. A committed plan at the same depth reaches 28% of the gap in the budgeted setting and 5% without a budget, and without a budget it does not reach the gap within the depth horizon examined.

The finding is therefore sharper than "lookahead has value". The gap's **value** is real and exactly computable; its **accessibility** is far cheaper than the value alone would suggest, because replanning is what converts foresight into recovery and two steps of foresight suffice. Rather than asking how much foresight can be afforded, the modeller need only ask whether two steps are affordable, and Table 5 shows that they are. It is also the reason a learned orderer cannot be justified by the size of the gap alone.

### 5.6 The phase structure of the gap

Sweeping the budget $B \in \{0,4,6,8\}$ over the same twelve conditions gives the phase structure of the criterion: 132 instances under each of the four budgets, 528 evaluations in total, on one instance set shared across all budgets. Figure 6 shows the resulting classification.

**Table 6.** Instance classification by budget.

| Budget $B$ | Long-range | Non-identifiable | Shallow |
|---|---|---|---|
| 0 | 32 | 94 | 6 |
| 4 | **0** | **124** | 8 |
| 6 | 9 | 112 | 11 |
| 8 | 29 | 97 | 6 |

The budget axis is **non-monotonic**, and the $B = 4$ column shows why. With four reconnections against roughly twelve broken key lines the problem degenerates towards *selecting* a subset rather than *ordering* one, and greedy selection is already near-optimal for the monotone structure of the objective; consequently no instance in the sample is long-range at $B = 4$. The largest gaps appear at $B = 8$ (up to 134.4, 116.2 and 105.3 in the three most affected conditions). The envelope check of Appendix B holds on the coupled instances of this sweep as well, so the non-monotonicity is a property of the problem rather than an artefact of the solver. The budget is therefore a design parameter with a non-monotone effect, and a phase diagram rather than a single-point comparison against a legacy configuration is the appropriate instrument for choosing it.

### 5.7 Head-to-head: dominance on the aligned sample

Ten policies are evaluated on all twelve conditions with 20 scenarios each, giving **240 paired comparisons** per baseline, on the aligned sample, in which every scenario has an exact offline reference. The unrestricted sample is reported alongside because the two answer different questions, and Figure 7 reports the same comparison condition by condition.

**Table 7.** Rolling depth-2 lookahead against every alternative. Aligned sample: 12 conditions $\times$ 20 scenarios, 240 paired comparisons per alternative. $\Delta$ = mean AUC@25 advantage of the rolling depth-2 rule. Worst $p$ is the largest of the twelve per-condition Wilcoxon $p$-values; pooled $p$ is the Wilcoxon $p$-value over all 240 pairs.

| Alternative | Wins | Ties | Losses | Mean $\Delta$ | Worst $p$ | Pooled $p$ |
|---|---|---|---|---|---|---|
| Learned ranker | 240 | 0 | **0** | +946.1 | $1.9\times10^{-6}$ | $4.0\times10^{-41}$ |
| Risk-only rule | 240 | 0 | **0** | +783.5 | $1.9\times10^{-6}$ | $4.0\times10^{-41}$ |
| Uniformly random | 240 | 0 | **0** | +750.4 | $1.9\times10^{-6}$ | $4.0\times10^{-41}$ |
| True-objective ranker | 240 | 0 | **0** | +727.1 | $1.9\times10^{-6}$ | $4.0\times10^{-41}$ |
| Learned ranker, screened | 240 | 0 | **0** | +419.4 | $1.9\times10^{-6}$ | $4.0\times10^{-41}$ |
| True-objective ranker, screened | 240 | 0 | **0** | +324.0 | $1.9\times10^{-6}$ | $4.0\times10^{-41}$ |
| Electrical-priority rule | 213 | 27 | **0** | +80.6 | 0.0015 | $1.1\times10^{-36}$ |
| One-step exact rule | 35 | 205 | **0** | +4.78 | **1.00** | $2.5\times10^{-7}$ |

Three results are worth separating. **The rolling depth-2 rule is never worse than any alternative in any of the 240 comparisons**, and it attains the exact offline optimum in ten of the twelve conditions and no less than 99.995% of it in the other two. **Every learned variant loses in all 240 comparisons**, by 324 to 946 AUC@25 units; the least-penalised variant is the one that both screens and trains against the true objective, and it is also the variant whose advantage over the cheapest rule is smallest. Against the one-step exact rule the rolling rule wins 35 times, ties 205 times and never loses, for a mean advantage of +4.78 units; because 205 of those pairs are tied, the per-condition tests for that row are underpowered and its evidence rests on the pooled test, which is why Table 7 reports both. The pooled column saturates for the six arm-level alternatives because not one of their pairs is tied.

The third comparison connects the two halves of the paper. Because the rolling depth-2 rule attains the offline optimum, its advantage over the one-step exact rule **is** the lookahead gap, instance by instance: the measured per-condition advantages of 8.74, 5.27, 6.97, 4.38, 8.37, 4.93, 8.95, 2.51, 0.00, 2.70, 0.73 and 3.84 agree with the dynamic program's values of Table 4 (8.739, 5.274, 6.970, 4.384, 8.370, 4.934, 8.951, 2.511, 0, 2.762, 0.731, 3.924) to the precision printed, so the theoretical quantity is reproduced by an entirely separate code path. It also fixes the interpretation of Table 7: those advantages average 4.78 over all 240 pairs, whereas the learned variants lose by 324.0 to 946.1 units. The deficit is a shortfall of the ranker, not of headroom.

**Where the guarantee stops.** On the unrestricted sample, which includes scenarios with $K > 12$ for which no exact reference exists, the same comparison gives 896 wins and 64 losses for the learned variants, and the one-step exact rule gains 34 wins and 176 ties with a mean advantage of 27.2 units over the rolling controller. The rolling depth-2 rule is therefore optimal where the gap is computable and **not** guaranteed outside that regime: with more than twelve broken key lines, two steps of foresight can allocate recovery worse than the greedy rule. We state this boundary rather than restricting the reported sample to the favourable one, and it is the empirical form of the limitation recorded in Section 9.

### 5.8 Generalization to a third test system

On the 200-bus Illinois system the uncoupled gap is positive in **six of six** conditions, with a maximum of 71.47 and a median depth-to-90% of 4.0--7.5; that maximum is 4.3 times the largest uncoupled value on either IEEE system, consistent with the Illinois system's higher action-set flow share. Under the budget $B = 6$ the three severe conditions of the same system all carry a positive gap, with a maximum of 133.02 and a median depth-to-90% of 2.0--4.0. The sign of the gap and the direction of the budget effect therefore reproduce on a third system of a different size and origin, so the criterion's discrimination is a property of the problem class rather than of the two systems studied most intensively.

---
