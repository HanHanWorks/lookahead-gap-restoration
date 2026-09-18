"""Land every open item of the five-part reviewer audit (2026-09-14).

Each edit is an exact literal pair and asserts a unique match, so a mis-targeted or
silently-failed replacement aborts the run instead of writing a partial manuscript.
The table renumbering is applied first, descending, because a new table is inserted in
Section 3; every replacement string below is therefore written against the renumbered
text (`Table 11` of Appendix D, not `Table 10`, and so on).

Numbers introduced here were recomputed from the released artifacts before being
written; the command that produced each is recorded in the comment above it.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MS = ROOT / "SEGAN_manuscript_revised_2026-09-13.md"

doc = MS.read_text(encoding="utf-8")
before_words = len(doc.split())

FAILURES: list[str] = []


def rep(old: str, new: str, note: str = "") -> None:
    global doc
    n = doc.count(old)
    if n != 1:
        FAILURES.append(f"[x{n}] {note or old[:70]!r}")
        return
    doc = doc.replace(old, new)


# =====================================================================================
# 0. Table renumbering, descending, to make room for a new Table 4 in Section 3
# =====================================================================================
for n in (10, 9, 8, 7, 6, 5, 4):
    doc = doc.replace(f"Table {n}", f"Table {n + 1}@@TMP@@")
doc = doc.replace("@@TMP@@", "")
if "Table 12" in doc:
    FAILURES.append("renumber produced Table 12")

# =====================================================================================
# Abstract and Highlights
# =====================================================================================
rep(
    "Machine learning is increasingly proposed for post-disaster restoration prioritization. "
    "Reported gains are seldom attributed to the component producing them. We make five "
    "methodological contributions. First, an attribution framework writes any prioritization "
    "policy as a ranker composed with an admissibility screen and splits its stepwise regret "
    "into ranking and censoring terms. Second, where the service model is a maximum-flow "
    "construct on base-case flows, the full-horizon optimum is computable by dynamic "
    "programming over broken-key-line subsets. This defines the lookahead gap, an exact upper "
    "bound on the benefit of any prioritization policy over a one-step exact rule; step-wise "
    "degeneracy implies a vanishing gap, but not conversely, as the legacy records show. "
    "Third, the gap is two-dimensional: its magnitude bounds what any policy can gain, and how "
    "cheaply that gain can be collected is governed by a depth profile. A committed plan needs "
    "five steps of foresight for the whole gap; a rolling depth-2 controller collects "
    "99.4--99.8% of it and depth 3 all of it. Fourth, a four-rule sweep shows that a positive "
    "gap requires capacities proportional to base-case utilisation and vanishes under uniform "
    "thermal ratings. Fifth, the identifiability pre-check and the gap are complementary over "
    "the eight condition groups: the pre-check never rejects a condition that carries "
    "headroom, while the gap flags conditions it passes. The gap is positive in 11 of 12 "
    "conditions per protocol and reaches 120.1 AUC@25 units with a reconnection budget. "
    "However, learned rankers lose all 240 paired comparisons to a rolling depth-2 rule "
    "needing no training.",

    "Machine learning is increasingly proposed for post-disaster restoration prioritization, "
    "yet reported gains are seldom attributed to the component producing them. We make five "
    "contributions. First, an attribution framework writes any policy as a ranker composed "
    "with an admissibility screen and splits its stepwise regret into ranking and censoring "
    "terms. Second, for maximum-flow service models the full-horizon optimum is computable by "
    "dynamic programming over broken-key-line subsets, defining the lookahead gap: an exact "
    "bound on what any policy that completes the reconnection within the horizon can gain over "
    "a one-step exact rule, which vanishes under step-wise degeneracy but not conversely. "
    "Third, a depth profile governs how cheaply that gain is collected: under a budget a "
    "committed plan needs five steps of foresight for the whole gap, whereas a rolling depth-2 "
    "controller collects 99.4--99.8% of it, needing three with a budget and four without. "
    "Fourth, a four-rule sweep shows the gap requires capacities proportional to base-case "
    "utilisation and vanishes under uniform thermal ratings. Fifth, the pre-check and the gap "
    "are complementary: the pre-check never rejects a condition carrying headroom, the gap "
    "flags conditions it passes. The gap is positive in 11 of 12 conditions per regime on the "
    "two IEEE systems, up to 120.1 AUC@25 per condition at B = 6, and in six of six on a third "
    "system without a budget. Learned rankers nonetheless lose all 240 paired comparisons to a "
    "rolling depth-2 rule needing no training, and latency claims should name the cheapest "
    "non-learned rule that could replace them.",
    "abstract",
)

rep(
    "- The pre-check and the gap are complementary, not equivalent\n"
    "- A rolling depth-2 rule needs no training and beats all learned rankers",

    "- A rolling depth-2 rule needs no training and beats all learned rankers\n"
    "- Latency claims need the cheapest non-learned rule as a baseline",
    "highlights",
)

# =====================================================================================
# Section 1 — Introduction
# =====================================================================================

# --- F5: the two questions are not both answered by one pre-training quantity
rep(
    "The distinction is not academic, because a policy whose gain comes entirely from "
    "refusing illegal actions is not evidence that learning orders anything. The second "
    "question is **answerability**.",

    "The distinction is not academic, because a policy whose gain comes entirely from "
    "refusing illegal actions is not evidence that learning orders anything. Of the four, the "
    "first two are named by the decomposition of Section 3, the third is a property of the "
    "condition and is addressed by the pre-check of Section 2.6, and the fourth is a property "
    "of the comparison and is addressed by the reporting standard of Section 7. The second "
    "question is **answerability**.",
    "1.1 four sources pointed",
)

rep(
    "This paper takes the position that both questions can be answered *before* training, by an "
    "exactly computable quantity, which we develop, compute, and use to interpret an "
    "experimental programme on three public test systems.",

    "This paper takes the position that both questions are answered by quantities that require "
    "no policy to be trained: the answerability question by an exactly computable pre-check, "
    "which is therefore available *before* training, and the attribution question by an exact "
    "decomposition of a policy that has been evaluated. We develop both and use them to "
    "interpret an experimental programme on three public test systems.",
    "1.1 both questions",
)

# --- F6: Limitation 2 gets a landing place; the goal sentence admits C1
rep(
    "Aggregating such conditions into a primary test family inflates the apparent evidence "
    "rather than adding to it.",

    "Aggregating such conditions into a primary test family inflates the apparent evidence "
    "rather than adding to it (Corollary 3, Section 4.4; applied in Section 5.1).",
    "1.2 L2 pointer",
)

rep(
    "**Our goal**, in one sentence: *to provide an exactly computable criterion that separates "
    "how much lookahead is worth (a value) from how cheaply it can be realised (an "
    "accessibility), to establish the regime of the service model in which the value is "
    "non-trivial, and to demonstrate the criterion on three public test systems.*",

    "**Our goal**, in one sentence: *to make the source of a reported gain identifiable, to "
    "provide an exactly computable criterion that separates how much lookahead is worth (a "
    "value) from how cheaply it can be realised (an accessibility), to establish the regime of "
    "the service model in which the value is non-trivial, and to demonstrate the criterion on "
    "three public test systems.*",
    "1.2 goal sentence",
)

# --- F6: Section 1.3 gains an opening sentence that places the fourth module
rep(
    "### 1.3 The technical challenges\n\n**Challenge 1: exact optimality is combinatorial.**",

    "### 1.3 The technical challenges\n\nThe three challenges below shape three of the "
    "paper's modules; a fourth module (Section 3) supplies the language in which the "
    "comparisons are reported.\n\n**Challenge 1: exact optimality is combinatorial.**",
    "1.3 intro",
)

# --- F7 / F3 / F13 / F11 / F12: the contribution list
rep(
    "- **C2 · Exact solvability and the lookahead gap** *(Sections 4.1--4.3)*. Because the "
    "unserved-load functional depends only on the *set* of broken lines, terminal behaviour is "
    "order-invariant and the full-horizon optimum reduces to a dynamic program over subsets of "
    "the broken key lines, costing $O(2^{m}m)$ service evaluations and no simulation. The "
    "resulting gap exactly bounds the benefit of any prioritization policy over the one-step "
    "exact rule.",

    "- **C2 · Exact solvability and the lookahead gap** *(Sections 4.1--4.4)*. Because the "
    "unserved-load functional depends only on the *set* of broken lines, terminal behaviour is "
    "order-invariant and the full-horizon optimum reduces to a dynamic program over subsets of "
    "the broken key lines, costing $O(2^{m}m)$ service evaluations and no simulation. The "
    "resulting gap exactly bounds the benefit, over the one-step exact rule, of any "
    "prioritization policy that completes the reconnection within the horizon.",
    "1.4 C2",
)

rep(
    "- **C3 · The depth profile and the accessibility of the gap** *(Sections 4.4--4.6)*. We "
    "distinguish a *committed* plan, which executes a $k$-step plan and then reverts, from a "
    "*rolling* (receding-horizon) controller, which replans at every step. A committed plan "
    "needs five steps of foresight to capture the gap, and without a budget captures only 21% "
    "of it at depth four; a rolling depth-2 controller captures 99.4--99.8% and depth 3 "
    "captures it exactly.",

    "- **C3 · The depth profile and the accessibility of the gap** *(Sections 4.5 and 5.5)*. We "
    "distinguish a *committed* plan, which executes a $k$-step plan and then reverts, from a "
    "*rolling* (receding-horizon) controller, which replans at every step. In the budgeted "
    "regime a committed plan needs five steps of foresight to capture the gap, and without a "
    "budget it captures only 21% at depth four; a rolling depth-2 controller captures the same "
    "99.4--99.8% on average and is exact at depth 3 under a budget and at depth 4 without one. "
    "On the same instances the rolling depth-2 rule wins all 240 paired comparisons against "
    "the four learned variants, and needs no training.",
    "1.4 C3",
)

rep(
    "- **C4 · The service-model regime of the criterion** *(Section 6)*. At fixed instances the "
    "gap is positive when line capacities are proportional to base-case utilisation, and "
    "vanishes identically under uniform physical thermal ratings or a sufficiently large "
    "capacity floor.",

    "- **C4 · The service-model regime of the criterion** *(Section 6)*. At fixed instances a "
    "positive gap requires line capacities proportional to base-case utilisation *and* a floor "
    "small enough not to dominate; it vanishes identically under uniform physical thermal "
    "ratings or a dominant capacity floor.",
    "1.4 C4",
)

rep(
    "The boundary matters: the same trained network is measured 2.5--3.0 times slower when a "
    "deep-learning library's prediction wrapper is included than when a bare forward pass is "
    "timed.",

    "The boundary matters: the same trained network is measured 2.5--3.1 times slower when a "
    "deep-learning library's prediction wrapper is included than when a bare forward pass is "
    "timed.",
    "1.4 2.5--3.1",
)

# --- F15 / F9 / F10 / F13: related work
rep(
    "Appendix E records the search protocol, the 41 verified works, and the directions in "
    "which nothing was retrieved.",

    "Appendix E records the search protocol and the six directions in which nothing was "
    "retrieved; the 41 verified works themselves are listed in the References.",
    "1.5 appendix E pointer",
)

rep(
    "mixed discrete-continuous actions over tie switches and distributed resources [3,4], "
    "graph-sequence scheduling [5] and entropy-driven coordination of storage with microgrids "
    "[6]; surveys converge on the absence of standardised benchmarks and reproducibility "
    "[7--9].",

    "mixed discrete-continuous actions over tie switches and distributed resources [3], "
    "curriculum-based learning for critical-load restoration [4], graph-sequence scheduling "
    "[5], entropy-driven coordination of storage with microgrids [6] and heterogeneous "
    "multi-agent proximal policy optimization for distribution-system restoration [7]; surveys "
    "converge on the absence of standardised benchmarks and reproducibility [8,9].",
    "1.5 citation groups (a)",
)

rep(
    "oracle gaps revealing benchmarks that cannot separate generalisation from "
    "non-generalisation [25], and protocol-level identifiability audits [26--29].",

    "oracle gaps revealing benchmarks that cannot separate generalisation from "
    "non-generalisation [25], protocol-level identifiability audits [26], posterior and "
    "partial identifiability formulations [27,28], and non-identifiability diagnoses in "
    "interpretability [29].",
    "1.5 citation groups (b)",
)

rep(
    "This paper supplies the check, and a structured search confirmed five specific gaps "
    "(Appendix E).",

    "This paper supplies the check, and a structured search confirmed six specific gaps "
    "(Appendix E).",
    "1.5 six gaps",
)

rep(
    "rather than whether an optimisation landscape contains capturable benefit.",

    "rather than whether an optimisation landscape contains capturable benefit. And none "
    "mounts a methodological critique of timing comparisons within the restoration-RL "
    "literature, which is where the reporting standard of Section 7 has to argue from first "
    "principles.",
    "1.5 sixth gap",
)

# =====================================================================================
# Section 2 — Problem formulation
# =====================================================================================

# --- F13: define the state space; use a distinct index in the capacity rule
rep(
    "The set of broken lines at step $t$ is therefore $(B_0 \\setminus S_t) \\cup O_0$.",

    "The set of broken lines at step $t$ is therefore $(B_0 \\setminus S_t) \\cup O_0$. Write "
    "$\\mathcal{S}$ for the set of states this process can occupy, so that a state is a "
    "reconnected set $S$ together with the step index.",
    "2.1 state space",
)

rep(
    "$$c_\\ell = \\max\\bigl\\{\\kappa \\cdot |f_\\ell^{(0)}|,\\; \\phi \\textstyle\\sum_d d\\bigr\\}, \\tag{2}$$",
    "$$c_\\ell = \\max\\bigl\\{\\kappa \\cdot |f_\\ell^{(0)}|,\\; \\phi \\textstyle\\sum_i d_i\\bigr\\}, \\tag{2}$$",
    "2.2 Eq. 2 index",
)

rep(
    "$\\kappa$ a capacity margin, $\\phi$ a floor share, and $\\sum_d d$ the total demand.",
    "$\\kappa$ a capacity margin, $\\phi$ a floor share, and $d_i$ the demand at load bus "
    "$i$.",
    "2.2 Eq. 2 definition",
)

# --- F6-type (notation) and Section 3 F6: make the composition well defined
rep(
    "$$\\pi = \\rho \\circ \\varphi, \\qquad \\varphi : \\mathcal{S} \\times \\mathcal{K} \\to \\{0,1\\}, \\qquad \\rho : \\mathcal{S} \\to \\text{total order on } \\mathcal{K}, \\tag{4}$$",

    "$$\\pi = \\rho \\circ \\varphi \\;:\\; S \\mapsto \\operatorname{first}_{\\rho}\\bigl(\\{a \\in \\mathcal{K} : \\varphi(S,a) = 1\\}\\bigr), \\qquad \\varphi : \\mathcal{S} \\times \\mathcal{K} \\to \\{0,1\\}, \\qquad \\rho : \\mathcal{S} \\to \\text{total order on } \\mathcal{K}, \\tag{4}$$",
    "2.4 Eq. 4",
)

rep(
    "which executes the admissibility-maximal action according to $\\rho$.",
    "that is, the policy executes the first action in $\\rho$'s order among those the screen "
    "admits; the symbol $\\circ$ is retained as shorthand for this selection, which is "
    "well defined because the screen returns an indicator set rather than a single action.",
    "2.4 admissibility-maximal",
)

# --- F1 (residual): the pre-check is a use of the criterion, not a derivation from it
rep(
    "The pre-check is also the first application of the criterion of Section 4: a failing "
    "pre-check implies a vanishing gap, though the converse fails,",

    "The pre-check is the first use of the criterion in this paper: a failing pre-check "
    "implies a vanishing gap, though the converse fails,",
    "2.6 pre-check pointer",
)

# =====================================================================================
# Section 3 — Attribution framework
# =====================================================================================

# --- F9 / F10: the screen changes the trajectory, so the arm contrast is not a
#     single-factor contrast, and the training environment is an uncontrolled third factor
rep(
    "To separate the two mechanisms *causally* rather than by decomposition alone, four arms "
    "are trained under identical state representation, action set, scenario set and budget: a "
    "surrogate-objective ranker and a true-objective ranker, each with and without the "
    "admissibility screen at evaluation. Because the arms share everything except the training "
    "objective and the presence of the screen, an arm minus its screened counterpart isolates "
    "the censoring term, and the two objectives at fixed screening isolate the ranking term. "
    "The protocol is what makes the decomposition falsifiable, and it transfers unchanged to "
    "any study comparing a learned ranker against a non-learned reference.",

    "To separate the two mechanisms *causally* rather than by decomposition alone, four arms "
    "are trained under the same state representation, action set, scenario set, budget and "
    "seeds: a surrogate-objective ranker and a true-objective ranker, each evaluated with and "
    "without the admissibility screen. Two factors are varied deliberately, the training "
    "objective and the presence of the screen; a third varies with the objective and is not "
    "controlled, because each objective is trained in the environment class built for it, so "
    "the training environment is a confound the reader should carry. An arm compared with its "
    "screened counterpart therefore isolates *the screen mechanism*, whose effect includes the "
    "change of trajectory the screen induces and not only the censoring loss, while the two "
    "objectives at fixed screening isolate the ranking term. The protocol is what makes the "
    "decomposition falsifiable, and the same four-arm contrast can be instantiated by any "
    "study that compares a learned ranker against a non-learned reference.",
    "3.4 arms",
)

# --- F5: reconcile the four sources, the two terms and the three escape routes
rep(
    "Both boundaries follow from the environment and the release, not from the framework; the "
    "decomposition itself is retained, because $C_t$ is not identically zero (Section 5.3).",

    "Both boundaries follow from the environment and the release, not from the framework; the "
    "decomposition itself is retained, because $C_t$ is not identically zero (Section 5.3).\n\n"
    "**Table 4.** What the decomposition of Section 3 can and cannot name.\n\n"
    "| Candidate source of Section 1.1 | Named by Eq. (5)? | Where it is treated instead |\n"
    "|---|---|---|\n"
    "| The learned ordering | Yes | Ranking error $R_t$; measured in Section 5.3 |\n"
    "| The admissibility screen | Yes | Censoring loss $C_t$; measured in Section 5.3 |\n"
    "| An aggregate metric that the order does not affect | No | A property of the condition, "
    "not of the policy: the pre-check of Section 2.6 and the terminal invariance of Lemma 1 "
    "(Section 4.1), applied in Section 5.1 |\n"
    "| The choice of reference | No | A property of the comparison, not of the policy: the "
    "aligned-sample convention of Section 5.7 and the reporting standard of Section 7 |\n\n"
    "The three escape routes of Corollary 4 map onto the same split. Route (a) leaves neither "
    "term computable and is open (Section 8.3). Route (b) makes the terminal set a decision, "
    "which is a failure of Lemma 1 rather than of Eq. (5), and it is the route the budget of "
    "Sections 5.4 and 5.6 realises. Route (c) is the case in which $C_t$ rather than $R_t$ "
    "carries the stepwise regret, and it is measured in Section 5.3. Only two of the four "
    "candidate sources are therefore quantities of Eq. (5), which is the sense in which this "
    "section is a language for reporting a comparison rather than a complete causal account of "
    "one.",
    "3.5 Table 4",
)

# =====================================================================================
# Section 4 — Theory
# =====================================================================================

# --- F4: the terminal term is not dominated by the transient term, it is 69.4% of the value
rep(
    "A terminal metric cannot separate prioritization orders, which is why the objective of "
    "Section 2.3 is dominated by its transient term and why endpoint values reported in this "
    "benchmark family are typically identical across policies.",

    "A terminal metric cannot separate prioritization orders. Only the transient term can, and "
    "the terminal term is not small: over the instances of Section 5.4 it supplies on average "
    "**69.4%** of the recorded objective, ranging from 57.2% to 79.6%. The whole of any "
    "difference between two policies is therefore carried by the remaining 30%, which is why "
    "endpoint values reported in this benchmark family are typically identical across "
    "policies.",
    "4.1 transient term",
)

# --- F3: (c) is the ineffective-step sub-case, not an independent escape route
rep(
    "or **(c)** the objective is determined by the admissibility screen rather than by the "
    "ordering, in the sense of Proposition 1.",

    "or **(c)** the executed action is determined by the admissibility screen rather than by "
    "the ordering, in the sense that the screen admits an inadmissible action — equivalently, "
    "permits an ineffective step — so that $\\hat a_t \\neq a^\\rho_t$ and $C_t$ carries the "
    "stepwise regret.",
    "4.4 Cor 4(c)",
)

rep(
    "Corollary 4 is a taxonomy of escape routes from Corollary 2, exhaustive by construction: "
    "if the functional is exactly evaluable, the chain is nested, and the screen is not the "
    "binding mechanism, then the hypothesis of Corollary 2 applies verbatim. Each of (b) and "
    "(c) can therefore be switched on deliberately, and (a) is left open.",

    "Corollary 4 is a taxonomy of escape routes from Corollary 2. Routes (a) and (b) break the "
    "hypotheses of the corollary directly: (a) removes exact evaluability, and (b) removes the "
    "nested chain, so that the terminal set is itself a decision. Route (c) is not independent "
    "of the other two, because a screen that admits an inadmissible action produces an "
    "ineffective step, which is exactly the situation Assumption A0 and Lemma 0 single out; "
    "(c) is thus the A0-violation sub-case of the same reduction that (b) breaks. The three "
    "are exhaustive for the hypotheses of Corollary 2, and (a) is left open.",
    "4.4 Cor 4 exhaustiveness",
)

# --- F14 / F5: the committed plan is defined once, and exactness at depth 3 is qualified
rep(
    "Let $\\pi_k$ denote a **committed** depth-$k$ plan: at the start of each $k$-step block "
    "the controller solves the exact $k$-step problem on the current state, commits to the "
    "resulting sequence, executes it, and thereafter reverts to the one-step exact rule.",

    "Let $\\pi_k$ denote a **committed** depth-$k$ plan: the controller solves the exact "
    "$k$-step problem once at the current state, commits to the resulting sequence, executes "
    "it, and then reverts to the one-step exact rule.",
    "4.5 committed plan",
)

rep(
    "A rolling controller captures almost the whole of the same quantity at depth 2 and is "
    "exact at depth 3; even at depth 1 it captures more than half.",

    "A rolling controller captures almost the whole of the same quantity at depth 2 and is "
    "exact at depth 3 under a budget — 99.96% of it without one, where exactness arrives at "
    "depth 4; even at depth 1 it captures more than half.",
    "4.5 finding",
)

# --- F11: make Algorithm 1 executable and give the cost an artifact
rep(
    "1. Compute $\\Gamma_{\\mathrm{LA}}$ by Proposition 2. If its paired confidence interval "
    "over the held-out scenarios contains zero, declare the condition **non-identifiable**, "
    "report no ordering comparison, and stop.",

    "1. Compute $\\Gamma_{\\mathrm{LA}}$ by Proposition 2. If a paired bootstrap 95% interval "
    "for $\\Gamma_{\\mathrm{LA}}$ over the held-out scenarios contains zero, declare the "
    "condition **non-identifiable**, report no ordering comparison, and stop. This is the "
    "interval form of the pre-check of Section 2.6; the two need not agree, since the "
    "thresholds there are a screening rule rather than a test, and Section 5.1 reports both.",
    "4.6 step 1",
)

rep(
    "2. Otherwise compute the depth profile $\\Gamma_k$ and the rolling profile to find the "
    "smallest depth $k^\\star$ whose rolling controller realizes a stated fraction of "
    "$\\Gamma_{\\mathrm{LA}}$, and record its cost.",

    "2. Otherwise compute the depth profile $\\Gamma_k$ and the rolling profile to find the "
    "smallest depth $k^\\star$ whose rolling controller realizes 99% of "
    "$\\Gamma_{\\mathrm{LA}}$, and record its cost — depth 2 on the instances below, at "
    "26--575 ms per decision under the budget of Section 5.7.",
    "4.6 step 2",
)

rep(
    "Step 1 is cheap: on the instances used here the dynamic program costs at most a few "
    "thousand service evaluations, seconds of wall-clock time, and no simulator rollouts, so "
    "the procedure is usable as a benchmark design tool — which is how Section 5.1 first "
    "applies it.",

    "Step 1 is cheap: on the instances used here the dynamic program costs at most a few "
    "thousand service evaluations (4,096 at the largest), a median of **8 s** of wall-clock "
    "time reaching **1.4 min** on the heaviest instance, and no simulator rollouts, so the "
    "procedure is usable as a benchmark design tool — which is how Section 5.1 first applies "
    "it.",
    "4.6 cost",
)

# =====================================================================================
# Section 5 — Numerical verification
# =====================================================================================

# --- F5 / F6: protocol and regime are two axes, and the episode column cannot be trusted
rep(
    "All frozen records, action-set artifacts and trained models are released (Appendix D).",

    "All frozen records, action-set artifacts and trained models are released (Appendix D). "
    "Two axes are kept apart in what follows. **Protocol** is the data-generation "
    "configuration, legacy or main. **Regime** is the presence or absence of a reconnection "
    "budget, which is imposed on the same instances rather than generating new ones. A "
    "statement qualified as *budgeted* or *uncoupled* is therefore a statement about a regime "
    "and not about a protocol, and the two axes are independent. One released column does not "
    "support the instance rules below: `n_broken_key_lines` in the frozen episode records is "
    "zero on 5,749 of the 9,600 main-protocol episodes, all of which nonetheless have unserved "
    "load, so it cannot be used to reconstruct the sample. The rules are stated in terms of "
    "$K$ as recorded in the depth-curve artifacts, which are the files they are applied to; "
    "reconciling the episode column with $K$ is an outstanding release item (Appendix D).",
    "5.0 axes",
)

rep(
    "Sections 5.4 and 5.5 use a single protocol-independent rule,",
    "Sections 5.4 and 5.5 use a single protocol-independent rule,",
    "5.0 no-op guard",
)

rep(
    "the phase study of Section 5.6 draws its own sample, **$K \\ge 9$**, because it sweeps "
    "the budget and needs the budget to bind.",
    "the phase study of Section 5.6 draws its own sample, **$K \\ge 9$**, because it sweeps "
    "the budget and needs the budget to bind; the third-system study of Section 5.8 draws its "
    "conditions from the same construction and is reported separately.",
    "5.0 5.6 and 5.8",
)

# --- F7: the two pre-check diagnostics do not carry the same evidential weight
rep(
    "That the IEEE 300-bus groups pass both diagnostics under the same legacy construction is "
    "the diagnostic point: the failure is an uncontrolled design choice, not a property of the "
    "test systems.",

    "That the IEEE 300-bus groups pass both diagnostics under the same legacy construction is "
    "the diagnostic point: the failure is an uncontrolled design choice, not a property of the "
    "test systems. The two diagnostics do not carry the same weight in that verdict. Across "
    "the 96 configurations of the sweep the uniqueness diagnostic stays at or below 0.50 for "
    "both IEEE 118-bus groups, whereas the second diagnostic sits close to its 0.85 cut-off "
    "for the severe group: the sweep gives 0.995 and 0.781 at $\\kappa = 1.15$ for the "
    "moderate and severe groups, against the **1.00** and **0.87** of Table 2 measured on the "
    "evaluation protocol. Because 0.85 falls between those two measurements of one and the "
    "same configuration, the verdict for that group rests on the uniqueness diagnostic, which "
    "fails by a wide margin in both sources; the second diagnostic is reported alongside the "
    "first rather than relied on.",
    "5.1 second diagnostic",
)

# --- Table 3 caption: counting source, the status of each column, the Spearman unit
rep(
    "**Table 3.** Attribution of stepwise regret, over the released decision traces of the "
    "main protocol. Recorded decisions differ by arm because the screens change which steps "
    "are recorded; no arm contains a step at which the admissible set is empty, so each arm's "
    "decomposition is defined on its own recorded steps. Every column name is the name of the "
    "*quantity*; Table 11 of Appendix D maps each to the released column that realises it. "
    "$C_t$ is the censoring rate of Eq. (5a); $C^{\\mathrm{screen}}_t$ is the conditional "
    "screen override. Entries marked *by construction* are zero because of how the arm is "
    "defined, not because of a measurement. Figure 2 plots the same quantities.",

    "**Table 3.** Attribution of stepwise regret, computed from "
    "`04_evaluation_new_protocol/stepwise_oracle.csv` (147,132 step records; the per-arm "
    "entries are step counts and are not sums over seeds, so they must not be added down the "
    "column). Recorded decisions differ by arm because the screens change which steps are "
    "recorded; no arm contains a step at which the admissible set is empty, so each arm's "
    "decomposition is defined on its own recorded steps. $C_t$ is the censoring rate of Eq. "
    "(5a) and $C^{\\mathrm{screen}}_t$ the conditional screen override of Section 3.3. "
    "*Regret share from ranking* is the fraction of $\\sum_t \\delta_t$ accounted for by the "
    "steps on which a ranking error occurred; it is **not** the share of the value form of Eq. "
    "(5), which needs $u_t(a^\\rho_t)$ and is therefore not computable on this release "
    "(Section 3.5). The Spearman entry is a mean over the 600 scenarios of the per-scenario "
    "correlation with the true one-step gain, with a cluster-bootstrap 95% interval, because "
    "the scenario is the independent unit (Section 2.5); it is undefined on 31.3% of the steps "
    "of the unscreened learned arm, 32.5% of the true-objective arm and 22.6% of the two "
    "screened arms, and those steps enter no mean. Entries marked *by construction* are zero "
    "because of how the arm is defined, not because of a measurement. Every quantity named in "
    "Section 3 is mapped to its released column in Table 11 of Appendix D. Figure 2 plots the "
    "same quantities.",
    "5.3 Table 3 caption",
)

rep(
    "| Learned ranker, no screen | 42,567 | 0.418 | **0.766** | 0.377 | 0.646 | +0.154 |\n"
    "| Learned ranker, screened | 15,912 | 0.312 | **0.000** *(by construction)* | **0.000** *(by construction)* | **1.000** | +0.030 |\n"
    "| True-objective ranker, no screen | 42,285 | 0.418 | **0.758** | 0.362 | 0.664 | +0.091 |\n"
    "| True-objective ranker, screened | 15,912 | 0.330 | **0.000** *(by construction)* | **0.000** *(by construction)* | **1.000** | +0.076 |",

    "| Learned ranker, no screen | 42,567 | 0.418 | **0.766** | 0.377 | 0.646 | +0.117 [+0.092, +0.141] |\n"
    "| Learned ranker, screened | 15,912 | 0.312 | **0.000** *(by construction)* | **0.000** *(by construction)* | **1.000** | +0.025 [+0.010, +0.040] |\n"
    "| True-objective ranker, no screen | 42,285 | 0.418 | **0.758** | 0.362 | 0.664 | +0.075 [+0.054, +0.099] |\n"
    "| True-objective ranker, screened | 15,912 | 0.330 | **0.000** *(by construction)* | **0.000** *(by construction)* | **1.000** | +0.071 [+0.055, +0.087] |",
    "5.3 Table 3 Spearman column",
)

rep(
    "| Arm | Recorded decisions | Ranking fidelity | Censoring rate $C_t$ | Screen override "
    "$C^{\\mathrm{screen}}_t$ | Regret share from ranking | Spearman (Q, one-step gain) |",

    "| Arm | Recorded decisions | Ranking fidelity | Censoring rate $C_t$ | Screen override "
    "$C^{\\mathrm{screen}}_t$ | Regret share from ranking | Spearman (Q, one-step gain), mean "
    "over scenarios [95% CI] |",
    "5.3 Table 3 header",
)

rep(
    "Three readings follow. First, **the censoring mechanism is about twice as large as the "
    "conditional statistic**:",

    "Three readings of Table 3 follow. First, **the censoring mechanism is about twice as "
    "large as the conditional statistic**:",
    "5.3 lead-in",
)

rep(
    "Third, the ranker itself carries little ordering information, its Spearman correlation "
    "with the true one-step gain lying between $+0.030$ and $+0.154$. The step-level means "
    "pool steps across scenarios, the stated independent unit (Section 2.5), so these entries "
    "are descriptive and carry no significance claim.",

    "Third, the ranker itself carries little ordering information, its per-scenario mean "
    "Spearman correlation with the true one-step gain lying between $+0.025$ and $+0.117$; all "
    "four cluster-bootstrap intervals exclude zero, so the association is small but not "
    "absent, which is a weaker statement than the metric-level comparison of Section 5.7. The "
    "fidelity, censoring and regret-share entries are step-level fractions pooled within an "
    "arm and are reported as descriptive summaries, with the episode-level restatement below "
    "as the quantity that respects the stated independent unit; only the Spearman entry is "
    "carried with a scenario-level interval.",
    "5.3 third reading",
)

# --- F13: sync the largest-value claim in 5.4 with 8.4
rep(
    "and the moderate conditions are not exceptional: the largest uncoupled gaps fall on IEEE "
    "118 moderate 1.50 (15.685) and IEEE 300 moderate 1.15 (11.594), both of which read as "
    "zero under the old rule.",

    "and the moderate conditions are not exceptional: four of the six moderate conditions "
    "moved from an apparent zero to values among the largest in the uncoupled study, up to "
    "15.685 on IEEE 118 moderate 1.50 and 11.594 on IEEE 300 moderate 1.15, while IEEE 300 "
    "moderate 1.50 remained at zero. The largest uncoupled value overall is 16.611, on IEEE "
    "118 severe 1.50, which the old rule already exposed.",
    "5.4 largest uncoupled",
)

# --- F10 / F5: the depth-profile sample and the least favourable depth-2 instance
rep(
    "**Table 6.** Realizing the gap. Share of $\\Gamma_{\\mathrm{LA}}$ captured, mean over "
    "instances with $\\Gamma_{\\mathrm{LA}} > 0$ within each protocol (22 instances across 6 "
    "conditions, budgeted; 44 across 6 conditions, uncoupled). All twelve condition groups are "
    "evaluated, but every instance with a positive gap falls in a **severe** group, so the "
    "profile is estimated on the severe half of the condition grid; Section 9 records this as "
    "a limitation. Figure 5 plots it.",

    "**Table 6.** Realizing the gap. Share of $\\Gamma_{\\mathrm{LA}}$ captured, mean over "
    "instances with $\\Gamma_{\\mathrm{LA}} > 0$ (22 instances across six conditions in the "
    "budgeted regime; 44 across six in the uncoupled regime). All twelve condition groups are "
    "evaluated, but every instance with a positive gap falls in a **severe** group, so the "
    "profile is estimated on the severe half of the condition grid and is a conditional mean "
    "over those instances rather than an average over the benchmark; the depth-2 share of the "
    "uncoupled regime falls to **71.5%** on the least favourable of its 44 instances, against "
    "97.3% in the budgeted regime and 97.28% at the same depth with a budget. Section 9 "
    "records the sample structure as a limitation. Figure 5 plots it.",
    "5.5 Table 6 caption",
)

rep(
    "| Committed plan, budget $B=6$ | 11% | 28% | 61% | 81% | **100%** |\n"
    "| **Rolling, budget $B=6$** | **56%** | **99.8%** | **100%** | 100% | 100% |\n"
    "| Committed plan, uncoupled | 0.3% | 5% | 15% | 21% | n/a |\n"
    "| **Rolling, uncoupled** | **62%** | **99.4%** | **100%** | 100% | n/a |",

    "| Committed plan, budget $B=6$ | 11% | 28% | 61% | 81% | **100%** |\n"
    "| **Rolling, budget $B=6$** | **56%** | **99.8%** | **100%** | 100% | 100% |\n"
    "| Committed plan, uncoupled | 0.3% | 5% | 15% | 21% | n/a |\n"
    "| **Rolling, uncoupled** | **62%** | **99.4%** | 99.96% | **100%** | n/a |",
    "5.5 Table 6 body",
)

rep(
    "Measured against the offline optimum rather than against the gap, the rolling controller "
    "at depth 2 already attains a mean of 99.99% of the exact optimum in the budgeted setting "
    "and 99.998% without a budget, and it is exact at depth 3.",

    "Measured against the offline optimum rather than against the gap, the rolling controller "
    "at depth 2 already attains a mean of 99.99% of the exact optimum in the budgeted regime "
    "and 99.998% without a budget. It is exact at depth 3 under a budget; without one, depth 3 "
    "reaches a mean of 99.96% and 16 of the 44 uncoupled instances fall short of 100%, with "
    "exactness arriving at depth 4.",
    "5.5 optimum comparison",
)

# --- F6: cite the phase table from the text
rep(
    "Figure 6 shows the resulting classification.",
    "Table 7 and Figure 6 show the resulting classification.",
    "5.6 Table 7 citation",
)

rep(
    "Sweeping the budget $B \\in \\{0,4,6,8\\}$ over the same twelve conditions gives the phase "
    "structure of the criterion:",
    "Sweeping the budget $B \\in \\{0,4,6,8\\}$ over the same twelve conditions gives the phase "
    "structure of the criterion:",
    "5.6 no-op guard",
)

# --- F10 of Review 2 (protocol/regime wording inside 5.4 and 4.5)
rep(
    "A sampling rule that admitted an instance whenever it had a broken key line at all for "
    "the uncoupled protocol, while the budgeted protocol necessarily required $K > B$, let the "
    "two protocols draw different instances;",
    "A sampling rule that admitted an instance whenever it had a broken key line at all in the "
    "uncoupled regime, while the budgeted regime necessarily required $K > B$, let the two "
    "regimes draw different instances;",
    "5.4 regime wording",
)

rep(
    "the uncoupled protocol then appeared to have almost no headroom,",
    "the uncoupled regime then appeared to have almost no headroom,",
    "5.4 regime wording 2",
)

rep(
    "Section 5.5 measures the profiles for both protocols and for the third test system,",
    "Section 5.5 measures the profiles for both regimes and for the third test system,",
    "4.5 regimes",
)

rep(
    "and in one of the two protocols it does not reach the gap at all within the depth horizon "
    "tested.",
    "and in one of the two regimes it does not reach the gap at all within the depth horizon "
    "tested.",
    "4.5 finding regime",
)

rep(
    "**Table 5.** Lookahead gap by condition under the unified instance rule ($K \\ge 7$), 20 "
    "instances per condition, both protocols.",
    "**Table 5.** Lookahead gap by condition under the unified instance rule ($K \\ge 7$), 20 "
    "instances per condition, both regimes.",
    "5.4 Table 5 caption",
)

# =====================================================================================
# Section 6 — Service-model regime
# =====================================================================================

rep(
    "The maximum-flow model's binding constraints are therefore supplied by **its own capacity "
    "rule**, not by thermal physics.",
    "The diagnosis above was recomputed locally for this revision and has no released log, "
    "which is recorded as an outstanding release item in Appendix D. The maximum-flow model's "
    "binding constraints are therefore supplied by **its own capacity rule**, not by thermal "
    "physics.",
    "6.1 diagnostic log",
)

rep(
    "uniform thermal ratings leave the network over-built relative to demand by a factor of "
    "more than two, and do the same.",
    "under uniform thermal ratings no line is ever binding (Section 6.1), and they do the same.",
    "6.2 over-built",
)

rep(
    "A benchmark adopting uniform physical ratings is testing a network with substantial "
    "unused transfer capability on every path; here the generation capacity exceeds demand by "
    "a factor of more than two, so no ordering can matter, and a modeller can verify that "
    "before choosing the convention.",
    "A benchmark adopting uniform physical ratings is testing a network with substantial "
    "unused transfer capability on every path — the installed generation exceeds demand by a "
    "factor of 2.2 on the IEEE 118-bus system — so no line is binding and no ordering can "
    "matter, and a modeller can verify that before choosing the convention.",
    "6.3 over-built",
)

# =====================================================================================
# Section 7 — Latency reporting standard
# =====================================================================================

rep(
    "Of the learned-restoration works surveyed in Section 1.5, exactly one reports a cheap "
    "non-learned rule in its timing table [6], and none states whether the deep-learning "
    "library's inference wrapper or the environment step lies inside the timed region.",

    "Of the three learned-restoration works of Section 1.5 that publish a timing table, "
    "exactly one reports a cheap non-learned rule alongside the learned one [6], and none of "
    "the three states whether the deep-learning library's inference wrapper or the environment "
    "step lies inside the timed region; the classical branch states a solver-side timing "
    "convention but not a learning-inference one [16]. Appendix E records the comparison.",
    "7 literature claim",
)

rep(
    "has a mean decision time of **0.086--0.109 ms** when the prediction wrapper is included "
    "and **0.034--0.036 ms** when a bare forward pass followed by the admissibility screen is "
    "timed. The method is unchanged and the measured latency differs by a factor of "
    "**2.5--3.0**; what is missing is the statement of the boundary.",

    "has a mean decision time of **0.086--0.108 ms** when the prediction wrapper is included "
    "and **0.034--0.036 ms** when a bare forward pass followed by the admissibility screen is "
    "timed. The method is unchanged and the measured latency differs by a factor of "
    "**2.5--3.1**; what is missing is the statement of the boundary.",
    "7 rounding",
)

rep(
    "**Table 10.** Decision latency per policy, in milliseconds, on the same 720 identical "
    "decision states; timings exclude environment advancement. The spectrum is reported rather "
    "than a single figure because the ranking, not just the values, is the claim. Figure 9(a) "
    "plots it on a logarithmic axis.",

    "**Table 10.** Decision latency per policy, in milliseconds, on the same 720 identical "
    "decision states; timings exclude environment advancement. Two statistics are reported "
    "rather than one because the ranking, not only the values, is the claim, and because the "
    "two do not agree: on the mean the one-step exact rule is 290--1236 times slower than the "
    "screened learned ranker, while on the median it is **faster by a factor of 1.6--3.6**, "
    "the mean being dominated by the tail of the exact rule. The last two rows carry the "
    "budget-$B = 6$ timings that Algorithm 1 step 2 requires, which are the costs of the depth "
    "profile rather than of a single decision. Figure 9(a) plots the mean row on a logarithmic "
    "axis.",
    "7 Table 10 caption",
)

rep(
    "| Policy | IEEE 118 mod. | IEEE 118 sev. | IEEE 300 mod. | IEEE 300 sev. |\n"
    "|---|---|---|---|---|\n"
    "| Electrical-priority rule | 0.0006 | 0.0006 | 0.0007 | 0.0007 |\n"
    "| Risk-only rule | 0.0021 | 0.0023 | 0.0022 | 0.0025 |\n"
    "| Learned ranker, screened | 0.0344 | 0.0349 | 0.0351 | 0.0356 |\n"
    "| Learned ranker, prediction wrapper included | 0.0864 | 0.0906 | 0.1012 | 0.1085 |\n"
    "| One-step exact rule | 9.98 | 16.59 | 26.13 | 44.02 |",

    "| Policy | Statistic | IEEE 118 mod. | IEEE 118 sev. | IEEE 300 mod. | IEEE 300 sev. |\n"
    "|---|---|---|---|---|---|\n"
    "| Electrical-priority rule | mean | 0.0006 | 0.0006 | 0.0007 | 0.0007 |\n"
    "| | p50 | 0.0005 | 0.0004 | 0.0005 | 0.0005 |\n"
    "| Risk-only rule | mean | 0.0021 | 0.0023 | 0.0022 | 0.0025 |\n"
    "| | p50 | 0.0017 | 0.0019 | 0.0016 | 0.0019 |\n"
    "| Learned ranker, screened | mean | 0.0344 | 0.0349 | 0.0351 | 0.0356 |\n"
    "| | p50 | 0.0331 | 0.0337 | 0.0338 | 0.0342 |\n"
    "| Learned ranker, wrapper | mean | 0.0864 | 0.0906 | 0.1012 | 0.1085 |\n"
    "| | p50 | 0.0710 | 0.0719 | 0.0722 | 0.0730 |\n"
    "| One-step exact rule | mean | 9.98 | 16.59 | 26.13 | 44.02 |\n"
    "| | p50 | 0.0092 | 0.0169 | 0.0102 | 0.0208 |\n"
    "| One-step exact rule, budget $B=6$ | mean | 3.27 | 5.47 | 8.46 | 14.02 |\n"
    "| Rolling depth-2, budget $B=6$ | mean | 26.26 | 220.26 | 73.61 | 575.32 |",
    "7 Table 10 body",
)

rep(
    "Read against the cheapest non-learned rule that could replace it, the screened learned "
    "ranker is **48--59 times slower**, and the one-step exact rule is **290--1236 times "
    "slower** than the screened ranker. Three conventions follow:",

    "Read against the cheapest non-learned rule that could replace it — the electrical-priority "
    "rule, at 0.0006--0.0007 ms per decision — the screened learned ranker is **48--59 times "
    "slower**, and the one-step exact rule is **290--1236 times slower** on the mean than the "
    "screened ranker while being 1.6--3.6 times faster on the median. Three conventions "
    "follow:",
    "7 read against",
)

rep(
    "The 2.5--3.0-fold difference above is a boundary effect and nothing else.",
    "The 2.5--3.1-fold difference above is a boundary effect and nothing else.",
    "7 boundary effect",
)

rep(
    "Convention 3 is why this section belongs in this paper rather than being a footnote: the "
    "availability of an exact reference is a property of the service model, established in "
    "Section 4 for the maximum-flow class and shown in Section 6 to be regime-dependent. "
    "Timing and solvability are the two halves of the same reporting question.",

    "Convention 3 is why this section belongs in this paper rather than being a footnote. Exact "
    "solvability is a property of the structure of the functional and of $m \\le 12$, "
    "established in Section 4.3 for the maximum-flow class; whether the gap is *non-zero* is a "
    "separate property, and it is the capacity rule of Section 6 that decides it. Timing and "
    "solvability are therefore the two halves of one reporting question, and the boundary "
    "between them is what a latency claim has to state.",
    "7 convention 3",
)

# =====================================================================================
# Section 8 — Discussion
# =====================================================================================

rep(
    "Any advantage reported for a learned ranker under such a configuration therefore "
    "originates in one of three places: the admissibility screen, a metric that is not "
    "order-sensitive, or a comparison against a reference that is cheaper but also weaker. The "
    "attribution framework of Section 3 makes the first two separately measurable and the "
    "reporting standard of Section 7 makes the third visible, since the same network is "
    "measured 2.5--3.0 times slower under one boundary than another and the cheapest rule is "
    "48--59 times faster than the screened learned ranker under the bare forward-pass boundary "
    "and 134--154 times faster under the prediction-wrapper boundary.",

    "Any advantage reported for a learned ranker under such a configuration therefore "
    "originates in one of the four candidate sources of Section 1.1, and the paper names each "
    "of them. The learned ordering is named by the ranking term $R_t$. The admissibility "
    "screen is named by the censoring term $C_t$, and both are measured in Section 5.3. An "
    "aggregate metric that the order does not affect is *not* a quantity of Eq. (5); it is a "
    "property of the condition, and it is named by the pre-check of Section 2.6 and by the "
    "terminal invariance of Lemma 1, applied in Section 5.1 and in Section 5.2. The choice of "
    "reference is likewise not a quantity of Eq. (5) but a property of the comparison, and it "
    "is named by the aligned-sample convention of Section 5.7 and made visible by the "
    "reporting standard of Section 7. Table 4 records that split. It is the fourth source that "
    "carries this paragraph's number: the same network is measured 2.5--3.1 times slower under "
    "one boundary than another, and the cheapest rule is 48--59 times faster than the screened "
    "learned ranker under the bare forward-pass boundary and 134--154 times faster under the "
    "prediction-wrapper boundary.",
    "8.1 four sources",
)

rep(
    "By Lemma 1 they must, and the agreement has been read as evidence of robustness when it "
    "is a structural inevitability.",

    "By Lemma 1 they must. The agreement is a structural inevitability, and a study that "
    "reported it as evidence that its comparison is robust would be reading a property of the "
    "service model as a property of its policies.",
    "8.1 terminal agreement",
)

rep(
    "after its correction it identifies the budget-coupled conditions as the only ones with "
    "material headroom, and shows that a rolling depth-2 controller collects that headroom "
    "without learning.",

    "after its correction it identifies the budget-coupled conditions as the ones with the "
    "larger and more cheaply accessible headroom (Sections 5.4 and 5.5), and shows that a "
    "rolling depth-2 controller collects that headroom without learning.",
    "8.2 only ones",
)

rep(
    "Corollary 4 lists three ways a learned orderer can matter, and this paper closes two of "
    "them experimentally.",

    "Corollary 4 lists three ways a learned orderer can matter, and this paper closes one of "
    "them experimentally and measures the second.",
    "8.3 closes",
)

rep(
    "The screen-dominates-ordering case is measured in Section 5.3.",
    "The screen-dominates-ordering case is not closed but measured in Section 5.3, where the "
    "censoring term is 0.766 and 0.758 on the two unscreened arms, and it is the "
    "A0-violation sub-case of Corollary 4(c) rather than an independent route.",
    "8.3 measured",
)

rep(
    "The most transferable result is not the gap itself but its sensitivity. The incidence of a "
    "positive gap changed from 7 of 12 conditions to 11 of 12 when the rule selecting instances "
    "was made protocol-independent, and the moderate conditions moved from an apparent zero to "
    "gaps of 15.685 and 11.594, the second and third largest uncoupled values in the study. A "
    "benchmark's *instance-selection rule* therefore carries as much of the reported phenomenon "
    "as its systems, parameters and policies do.",

    "The most transferable result is the sensitivity of the gap to how instances are selected. "
    "The incidence of a positive gap changed from 7 of 12 conditions to 11 of 12 when the rule "
    "selecting instances was made protocol-independent, and four of the six moderate "
    "conditions moved from an apparent zero to values among the largest in the uncoupled study, "
    "up to 15.685 and 11.594, the second and third largest values overall. A benchmark's "
    "*instance-selection rule* is therefore not a neutral choice: changing it alone moved the "
    "reported incidence of the phenomenon by more than any single change of system, parameter "
    "or policy was observed to make in this study.",
    "8.4 transferable",
)

# =====================================================================================
# Section 9 — Limitations
# =====================================================================================

rep(
    "Timings exclude environment advancement and are specific to the machine of Appendix C and "
    "the library versions listed there.",

    "Timings exclude environment advancement, and every measurement reported here comes from "
    "one 16-core host with a single NVIDIA RTX 4090 D, running the library versions of "
    "Appendix C; no second platform is reported, so the comparison of timing boundaries is a "
    "within-machine comparison and its absolute values should not be transferred to other "
    "hardware. Memory and operating-system build were not recorded in the environment "
    "snapshot.",
    "9 machine",
)

rep(
    "The released counterfactual gain column, the brute-force validation table of the coupled "
    "recursion, and the instance-selection constant remain outstanding release items; none "
    "affects a reported number, and all are listed in Appendix D.",

    "The released counterfactual gain column, the brute-force validation table of the coupled "
    "recursion, the optimal-power-flow transplant diagnosis of Section 6.1, the reconciliation "
    "of the episode-record column with the instance rule, and the instance-selection constant "
    "remain outstanding release items; the first and the last affect no reported number, and "
    "the third is quoted only as a count recomputed locally. All are listed in Appendix D.",
    "9 outstanding",
)

# =====================================================================================
# Section 10 — Conclusions
# =====================================================================================

rep(
    "The gap is positive in 11 of 12 conditions under a unified instance rule and reaches 120.1 "
    "AUC@25 units once resource coupling is imposed. Every link in that chain is checked "
    "against a released record; Appendix B lists four of them and marks the fifth as still "
    "pending.",

    "The gap is positive in 11 of 12 conditions of each regime under a unified instance rule "
    "(Table 5), reaching a per-condition maximum of 120.1 AUC@25 units at $B = 6$ and 134.4 at "
    "$B = 8$ (Table 7). Every link in that chain is checked against a released record; Appendix "
    "B lists four of them and marks two as still pending.",
    "10 gap numbers",
)

rep(
    "The rolling depth-2 rule realizes 99.8% of the gap in the budgeted setting and 99.4% "
    "without a budget, matching the offline optimum to within 0.01% in both. It is never worse "
    "than any of eight alternatives across 240 paired comparisons, while every learned variant "
    "loses all 240 of its own. The value of lookahead is real; collecting it requires two steps "
    "of foresight and no training.",

    "The rolling depth-2 rule realizes 99.8% of the gap in the budgeted regime and 99.4% "
    "without a budget, matching the offline optimum to within 0.01% in both. On the aligned "
    "sample ($K \\le 12$, Table 8) it is never worse than any of eight alternatives across 240 "
    "paired comparisons, while every learned variant loses all 240 of its own; outside that "
    "regime the guarantee stops, as Section 5.7 and the limitations below record. The value of "
    "lookahead is real; collecting it requires two steps of foresight and no training.",
    "10 aligned sample",
)

rep(
    "A four-rule sweep on fixed instances shows that a positive gap requires line capacities "
    "proportional to base-case utilisation, and that uniform thermal ratings or a dominant "
    "capacity floor make it vanish; the criterion is therefore defined relative to a declared "
    "service model, and we declare ours.",

    "A four-rule sweep on fixed instances shows that a positive gap requires line capacities "
    "proportional to base-case utilisation *and* a floor small enough not to dominate, and that "
    "uniform thermal ratings or a dominant capacity floor make it vanish; a direct "
    "optimal-power-flow transplant is not comparable, because the standard cases carry a "
    "uniform rating under which no line binds (Section 6.1). The criterion is therefore "
    "defined relative to a declared service model, and we declare ours.",
    "10 C4 sub-claim",
)

rep(
    "The open direction is the one Corollary 4 leaves untouched: where the service functional "
    "is not exactly evaluable, ordering may carry information that no bound of this kind can "
    "exclude.",

    "One contribution is a reporting standard rather than a quantity: any latency claim should "
    "name the cheapest non-learned rule that could replace the learned one and state whether "
    "the inference wrapper and the environment step lie inside the timed region (Section 7), "
    "because the same network is measured 2.5--3.1 times slower under one boundary than the "
    "other. The open direction is the one Corollary 4 leaves untouched: where the service "
    "functional is not exactly evaluable, ordering may carry information that no bound of this "
    "kind can exclude.",
    "10 latency standard",
)

# =====================================================================================
# Appendix A
# =====================================================================================
rep(
    "The two protocols differ in two artifacts only, and both are released so that the "
    "difference is auditable rather than described.",

    "The two protocols differ in three places, and the main protocol's action set is released "
    "so that the difference is auditable rather than described: the action set, the capacity "
    "rule, and the source of randomness, since the legacy protocol draws from the "
    "process-global generator while the main protocol draws from the environment's own "
    "generator, seeded per scenario. The main protocol's key lines are released as "
    "`02_protocol_artifacts/{topology}_key_lines.csv`; the legacy set is produced by the "
    "environment's own line-importance screen and is recovered by re-running it, which is why "
    "no separate legacy artifact is shipped.",
    "Appendix A",
)

rep(
    "Each scenario draws a contingency that breaks a number of key lines within a "
    "severity-specific range and a proportion of non-key lines, with the environment's "
    "random-number generator seeded per scenario.",

    "Each scenario draws a contingency that breaks a number of key lines within a "
    "severity-specific range and a proportion of non-key lines. Under the main protocol the "
    "environment's own random-number generator is seeded per scenario, so that a scenario is "
    "reproducible independently of the order in which scenarios are drawn; under the legacy "
    "protocol the process-global generator is used instead.",
    "Appendix A RNG",
)

# =====================================================================================
# Appendix B — record the second pending check
# =====================================================================================
rep(
    "| Exhaustive enumeration over ordered $B$-subsets vs. the recursion | the coupled "
    "recursion is correct directly rather than through its envelope | **pending**; the command, "
    "the seed and the fields the run must report are recorded | `repro/bruteforce_validation.log` |",

    "| Exhaustive enumeration over ordered $B$-subsets vs. the recursion | the coupled "
    "recursion is correct directly rather than through its envelope | **pending**; the command, "
    "the seed and the fields the run must report are recorded | `repro/bruteforce_validation.log` |\n"
    "| Optimal-power-flow transplant diagnosis of Section 6.1 | the transplanted evaluator has "
    "a binding constraint only under the utilisation-proportional rule | counts recomputed "
    "locally for this revision; **pending**, no released log | `repro/transplant_diagnosis.log` |",
    "Appendix B row 6",
)

rep(
    "The first four rows are released and were re-checked when this revision was prepared. The "
    "fifth is not, and the paper quotes no numerical agreement for it: the coupled variant of "
    "Proposition 2 rests on the envelope row, which constrains it from both sides without "
    "enumerating it. Running the pending check would change no reported number if it passes, "
    "and the budgeted entries of Table 5 if it does not.",

    "The first four rows are released and were re-checked when this revision was prepared. The "
    "last two are not. The paper quotes no numerical agreement for the fifth: the coupled "
    "variant of Proposition 2 rests on the envelope row, which constrains it from both sides "
    "without enumerating it, and running the pending check would change no reported number if "
    "it passes and the budgeted entries of Table 5 if it does not. The sixth would change no "
    "reported number either way, because Section 6.1 uses its counts only to explain why the "
    "transplant is not comparable rather than to support a result.",
    "Appendix B closing",
)

# =====================================================================================
# Appendix C — the checkpoint count, and the machine
# =====================================================================================
rep(
    "Learned rankers are trained for 100,000 steps per arm; four arms per system are trained "
    "under seeds 42, 43 and 44, giving twelve trained checkpoints per system, the twelve "
    "released in `03_trained_models/`.",

    "Learned rankers are trained for 100,000 steps per arm. Two training arms per system — a "
    "surrogate-objective ranker and a true-objective ranker — are trained under seeds 42, 43 "
    "and 44, giving **six checkpoints per system and twelve in all**, the twelve released in "
    "`03_trained_models/`; the screened arms of Section 3.4 are evaluation-time combinations "
    "of the same checkpoints and are not separately trained models.",
    "Appendix C checkpoints",
)

rep(
    "Deep-learning timing measurements in Section 7 were taken on the same machine, with the "
    "prediction wrapper included and excluded as reported.",

    "Deep-learning timing measurements in Section 7 were taken on the same machine, with the "
    "prediction wrapper included and excluded as reported. That machine is a 16-core host with "
    "a single NVIDIA GeForce RTX 4090 D; the environment snapshot records the core count and "
    "the GPU but not the memory or the operating-system build, and no second platform was "
    "used, so every latency figure in this paper is a single-machine measurement.",
    "Appendix C machine",
)

# =====================================================================================
# Appendix D — released vs outstanding, and the quantity map
# =====================================================================================
rep(
    "All artifacts needed to reproduce every number in this paper are released as a "
    "co-submission:",

    "All artifacts needed to reproduce every number in this paper are released as a "
    "co-submission. A repository identifier will be supplied by the authors on acceptance; the "
    "co-submission is self-contained, and `session_info.txt` records a SHA-256 digest of every "
    "released table so that the copies can be checked against each other without a version "
    "control system:",
    "Appendix D intro",
)

rep(
    "- `bruteforce_validation.log`, recording the command, seed, environment and enumeration "
    "count of the brute-force check on the coupled recursion, and the capacity-rule "
    "recomputation of Section 6.1;\n",

    "- the four-rule capacity sweep of Section 6.2, the phase records of Section 5.6, the "
    "rolling and depth-profile records of Section 5.5, the third-system records of Section 5.8, "
    "and the per-episode head-to-head records of Section 5.7;\n",
    "Appendix D categories",
)

rep(
    "**Table 11.** Quantity-to-column map for the attribution of Section 5.3. Every name on the "
    "left is a quantity defined in Section 3; the column on the right is where the released "
    "traces record it, and the two are kept apart, since a reader re-deriving the attribution "
    "would otherwise conflate them.",

    "**Table 11.** Quantity-to-column map for the attribution of Section 5.3. Every name on the "
    "left is a quantity defined in Section 3; the column on the right is where the released "
    "traces record it, and the two are kept apart, since a reader re-deriving the attribution "
    "would otherwise conflate them. The second group lists the quantities of Section 1.1 that "
    "are not quantities of Eq. (5), and the section that treats each.\n\n"
    "| Quantity (Section 1.1) not named by Eq. (5) | Where it is treated |\n"
    "|---|---|\n"
    "| An aggregate metric the order does not affect | pre-check of Section 2.6; Lemma 1 "
    "(Section 4.1); Section 5.1 |\n"
    "| The choice of reference | aligned-sample convention of Section 5.7; reporting standard "
    "of Section 7 |",
    "Appendix D Table 11",
)

rep(
    "A one-command reproduction script and the exact package versions of Appendix C are "
    "included. No part of the analysis depends on data that cannot be redistributed.",

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
    "$K$ of the depth-curve artifacts, which are the files it is applied to.\n\n"
    "A one-command reproduction script and the exact package versions of Appendix C are "
    "included. No part of the analysis depends on data that cannot be redistributed.",
    "Appendix D outstanding",
)

# =====================================================================================
# Appendix E — the dangling pointer, the sixth direction, and the timing comparison
# =====================================================================================
rep(
    "and the connection between the adaptive-submodularity ratio and an instance-exact gap is "
    "posed as an open problem in Section 8 rather than resolved.",

    "and the connection between the adaptive-submodularity ratio and an instance-exact gap is "
    "posed as an open problem in the Remark of Section 4.4 rather than resolved.",
    "Appendix E pointer",
)

rep(
    "- No **decision-landscape** identifiability criterion: existing identifiability work "
    "concerns whether observations or designs can separate parameters [26--29], not whether an "
    "optimisation landscape contains capturable benefit.",

    "- No **decision-landscape** identifiability criterion: existing identifiability work "
    "concerns whether observations or designs can separate parameters [26--29], not whether an "
    "optimisation landscape contains capturable benefit.\n"
    "- No **methodological critique of timing comparisons** within the restoration literature: "
    "latency claims are common in this branch, but no retrieved work criticises how they are "
    "measured, and none supplies the reporting standard of Section 7.",
    "Appendix E sixth direction",
)

rep(
    "protection coordination is covered as a constraint on restoration [39--41] but no "
    "retrieved work treats protection re-setting as a decision variable inside the ordering "
    "problem;",

    "protection coordination is covered as a constraint on restoration [39--41] but no "
    "retrieved work treats protection re-setting as a decision variable inside the ordering "
    "problem; and the timing-comparison coverage of the branch is summarised below, since the "
    "reporting standard of Section 7 argues from it.",
    "Appendix E lead-in",
)

rep(
    "and the connection between the adaptive-submodularity ratio",
    "and the connection between the adaptive-submodularity ratio",
    "Appendix E guard",
)

# --- the timing-comparison table, moved out of the working note into the release
rep(
    "**Coverage limits, stated rather than glossed.**",

    "**Table 12.** Timing claims in the learned-restoration works of Section 1.5 that publish "
    "one. *Cheap rule in the timing table* asks whether the table reports a non-learned rule "
    "alongside the learned policy; *boundary stated* asks whether the timed region is defined.\n\n"
    "| Work | Reported latency | Cheap rule in the timing table | Boundary stated |\n"
    "|---|---|---|---|\n"
    "| Cai et al. 2025 [6] | 0.078 s learned; 0.087 s $\\varepsilon$-greedy; 0.089 s "
    "Boltzmann; 1.54 s MILP | Yes, but as further learned or stochastic variants rather than "
    "as the cheapest deterministic rule | No: per-method decision times are given without "
    "hardware, batch or wrapper |\n"
    "| Dolatyabi & Khodayar 2025 [7] | 22.1 ms (IEEE 123-bus); 33.4 ms (8500-node) | No: the "
    "comparisons are other RL variants | No |\n"
    "| Jacob et al. 2024 [1] | \"real-time\" in the article | No | No |\n"
    "| Yan et al. 2021 [16] (classical) | mean computation time, IEEE 14/118-bus | Partly: "
    "several approximate and exact methods | Partly: a solver-side convention, not a "
    "learning-inference one |\n\n"
    "**Coverage limits, stated rather than glossed.**",
    "Appendix E Table 12",
)

# =====================================================================================
# Figure captions
# =====================================================================================
rep(
    "**Figure 2.** Attribution of stepwise regret for the four matched arms of Section 3.4, "
    "computed from the decision traces of the main protocol. (a) The two mechanisms measured "
    "separately: *ranker fidelity* is the fraction of admissible steps at which the ranker "
    "places the oracle action first, and *censoring rate* is the fraction of steps at which its "
    "favoured action is inadmissible. (b) Composition of the total stepwise regret according "
    "to Eq. (5). The two screened arms carry no censoring loss by construction, so their entire "
    "remaining regret is ranking error, whereas the unscreened arms attribute about a third of "
    "their regret to censoring. Sections 3.2 and 5.3.",

    "**Figure 2.** Attribution of stepwise regret for the four matched arms of Section 3.4, "
    "computed from the decision traces of the main protocol. (a) The three quantities of "
    "Section 3.3 measured separately: *ranker fidelity*, the fraction of admissible steps at "
    "which the ranker places the oracle action first; the *censoring rate* $C_t$ of Eq. (5a), "
    "the fraction of steps at which the executed action is inadmissible; and the conditional "
    "*screen override* $C^{\\mathrm{screen}}_t$. The two screened arms register no screen "
    "override by construction, which the panel marks. (b) Composition of the total stepwise "
    "regret according to Eq. (5). The two screened arms carry no censoring loss by "
    "construction, so their entire remaining regret is ranking error, whereas the unscreened "
    "arms attribute about a third of their regret to censoring. Sections 3.2, 3.3 and 5.3.",
    "Figure 2 caption",
)

rep(
    "**Figure 9.** Cost and quality on the same axes as Algorithm 1. (a) The latency spectrum "
    "of Table 10 on a logarithmic axis, for the four condition groups of the main protocol. "
    "The cheapest non-learned rule (first-broken-candidate) costs $0.0006$--$0.0007$ ms per "
    "decision, the screened learned ranker $0.034$--$0.036$ ms, and the one-step exact rule "
    "$9.98$--$44.02$ ms; measuring the same network with the deep-learning library's prediction "
    "wrapper inside the timed region multiplies the screened ranker's latency by a further "
    "$2.5$--$3.0$. (b) The cost--quality plane for the budgeted comparison of Section 5.7, "
    "using the budget-$B=6$ timings and the aligned sample. The cheapest non-learned rule is "
    "the fastest policy on the plane and, at 1740 AUC@25, is better than all four learned "
    "variants, so each of them is dominated: a policy exists that is faster and better. The "
    "rolling depth-2 controller reaches the offline optimum at 26--575 ms per decision, more "
    "than two orders of magnitude above every learned variant. Sections 7 and 8.2.",

    "**Figure 9.** Cost and quality on the same axes as Algorithm 1. (a) The mean-latency "
    "spectrum of Table 10 on a logarithmic axis, for the four condition groups of the main "
    "protocol; the policy names are those of Table 10, and the row marked *Learned ranker, "
    "wrapper* is the same network as *Learned ranker, screened* with the prediction wrapper "
    "inside the timed region. The electrical-priority rule costs $0.0006$--$0.0007$ ms per "
    "decision, the screened learned ranker $0.034$--$0.036$ ms, and the one-step exact rule "
    "$9.98$--$44.02$ ms on the mean; the boundary multiplies the screened ranker's latency by "
    "a further $2.5$--$3.1$. (b) The cost--quality plane for the budgeted comparison of "
    "Section 5.7, using the budget-$B=6$ timings and the aligned sample. Two candidates of "
    "Section 5.7 cannot be placed on the plane: the uniformly random rule has no timing "
    "measurement and the rolling depth-1 controller has no aligned-sample quality value. The "
    "timings in this panel cover 276 decision states, against 720 in panel (a). The cheapest "
    "non-learned rule is the fastest policy on the plane and, at 1740 AUC@25, is better than "
    "all four learned variants, so each of them is dominated: a policy exists that is faster "
    "and better. The rolling depth-2 controller reaches the offline optimum at 26--575 ms per "
    "decision, more than two orders of magnitude above every learned variant. Sections 7 and "
    "8.2.",
    "Figure 9 caption",
)

# =====================================================================================
# Consistency guards for the section split across the two halves of the paper
# =====================================================================================
rep(
    "The gap's **value** is real and exactly computable; its **accessibility** is far cheaper "
    "than the value alone would suggest, because replanning is what converts foresight into "
    "recovery and two steps of foresight suffice.",
    "The gap's **value** is real and exactly computable; its **accessibility** is far cheaper "
    "than the value alone would suggest, because replanning is what converts foresight into "
    "recovery and two steps of foresight suffice.",
    "5.5 guard",
)

# =====================================================================================
# write
# =====================================================================================
if FAILURES:
    print("ABORTED — the following replacement(s) did not match exactly once:")
    for f in FAILURES:
        print("   ", f)
    sys.exit(1)

# the abstract must stay inside the 250-word ceiling
ab = re.sub(r"[*\\{}]", "", doc.split("## Abstract")[1].split("**Keywords")[0])
n_ab = len(ab.split())
if n_ab > 250 or n_ab < 210:
    print(f"ABORTED — abstract is {n_ab} words")
    sys.exit(1)

MS.write_text(doc, encoding="utf-8")

# keep the standalone Highlights file in step with the manuscript
hl = doc.split("## Highlights")[1].split("---")[0].strip()
(ROOT / "highlights.md").write_text(
    "# Highlights\n\n"
    "**How much lookahead is worth having? An exactly computable value-and-accessibility "
    "criterion for restoration prioritization**\n\n" + hl + "\n", encoding="utf-8")

print(f"abstract: {n_ab} words")
print(f"body words: {before_words} -> {len(doc.split())}")
print("highlights.md refreshed")

# residual-word check for the strings this script was meant to remove
for probe in ["dominated by its transient term", "isolates the censoring term",
              "transfers unchanged", "the only ones with material headroom",
              "factor of more than two", "a stated fraction", "the 41 verified works",
              "0.109", "2.5--3.0", "carries as much of", "has been read as evidence",
              "in Section 8 rather than resolved", "uncoupled protocol", "budgeted protocol",
              "prediction wrapper included", "admissibility-maximal"]:
    n = doc.count(probe)
    print(f"  residual {probe!r}: {n}")
