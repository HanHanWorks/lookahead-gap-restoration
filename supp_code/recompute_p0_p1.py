"""Recompute the P0/P1 quantities requested in the correction list.

Writes `reviews/p1_recomputation.json` so every number quoted in the manuscript can be
traced to this run.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd
from scipy import stats

HERE = pathlib.Path(__file__).resolve().parent
WORK = HERE.parent
SUPP = WORK / "supp_results_2026-09-13"
EXP = WORK / "experiment_data"
OUT: dict = {}


# --------------------------------------------------------------------------- #
# 1. Table 4 sensitivity to the instance rule K >= k
# --------------------------------------------------------------------------- #
def k_sensitivity() -> None:
    res = {}
    for tag, f in (("uncoupled", "depth_curve_uncoupled_mk7.csv"),
                   ("budgetB6", "depth_curve_coupled_B6_mk7.csv")):
        d = pd.read_csv(SUPP / "results/E1_depth_curve" / f)
        rows = {}
        for k in (7, 8, 9):
            s = d[d.K >= k]
            g = s.groupby(["topology", "severity", "capacity_margin"]).agg(
                n=("gamma_la", "size"), mean=("gamma_la", "mean"),
                mx=("gamma_la", "max"), nz=("gamma_la", lambda z: int((z > 1e-9).sum())))
            rows[k] = dict(n_instances=int(len(s)),
                           n_conditions_positive=int((g.mx > 1e-9).sum()),
                           n_conditions=len(g),
                           global_max=round(float(s.gamma_la.max()), 3),
                           mean_of_condition_means=round(float(g["mean"].mean()), 3),
                           per_condition={f"{t}/{s_[:3]}/{m}": dict(mean=round(r["mean"], 3),
                                                                   mx=round(r["mx"], 3),
                                                                   nz=int(r["nz"]), n=int(r["n"]))
                                          for (t, s_, m), r in g.iterrows()})
        res[tag] = rows
    OUT["table4_k_sensitivity"] = res


# --------------------------------------------------------------------------- #
# 2. Episode-level censoring rate + cluster bootstrap
# --------------------------------------------------------------------------- #
def censoring() -> None:
    so = pd.read_csv(EXP / "04_evaluation_new_protocol/stepwise_oracle.csv",
                     usecols=["topology", "severity", "capacity_margin", "train_seed", "method",
                              "scenario_seed", "step_index", "n_candidates", "best_gain_mw",
                              "chosen_gain_mw", "realized_gain_mw", "regret_mw", "top1_hit",
                              "chosen_is_candidate", "best_rank_in_q", "chosen_rank_in_q"])
    so["cens"] = ~so.chosen_is_candidate.astype(bool)          # C_t = 1[executed action inadmissible]
    arms = ["DQN", "DQN-true", "DQN+validity-screen", "DQN-true+validity-screen"]
    res = {}
    rng = np.random.default_rng(20260914)
    for m in arms:
        d = so[so.method == m]
        if d.empty:
            continue
        ep = d.groupby(["topology", "severity", "capacity_margin", "train_seed",
                        "scenario_seed"]).agg(cens_steps=("cens", "sum"),
                                              steps=("cens", "size")).reset_index()
        ep["rate"] = ep.cens_steps / ep.steps
        # cluster bootstrap: resample scenarios (the stated independent unit)
        scen = ep.scenario_seed.unique()
        boots = []
        for _ in range(2000):
            pick = rng.choice(scen, size=len(scen), replace=True)
            boots.append(ep[ep.scenario_seed.isin(pick)].cens_steps.sum()
                         / ep[ep.scenario_seed.isin(pick)].steps.sum())
        boots = np.array(boots)
        res[m] = dict(
            step_level_rate=round(float(d.cens.mean()), 4),
            step_level_denominator=int(len(d)),
            n_episodes=int(len(ep)),
            steps_per_episode=round(float(ep.steps.mean()), 2),
            episode_mean_rate=round(float(ep.rate.mean()), 4),
            episode_median_rate=round(float(ep.rate.median()), 4),
            episode_iqr=[round(float(ep.rate.quantile(.25)), 4), round(float(ep.rate.quantile(.75)), 4)],
            ci95=[round(float(np.percentile(boots, 2.5)), 4),
                  round(float(np.percentile(boots, 97.5)), 4)],
            n_candidates_mean=round(float(d.n_candidates.mean()), 2),
            steps_with_empty_candidate_set=int((d.n_candidates == 0).sum()),
        )
        # C_t^screen : the ranker was right, the screen still overrode it
        r1 = d.best_rank_in_q == 1
        c1 = d.chosen_rank_in_q == 1
        hit = d.top1_hit.astype(bool)
        res[m]["C_screen_step_level"] = round(float((r1 & ~hit & ~c1).mean()), 4)
    # paired test on the shared (condition, seed, scenario) grid where both arms exist
    piv = so.pivot_table(index=["topology", "severity", "capacity_margin", "train_seed",
                                "scenario_seed", "step_index"],
                         columns="method", values="cens", aggfunc="mean")
    pairs = {}
    for a, b in (("DQN", "DQN+validity-screen"), ("DQN-true", "DQN-true+validity-screen")):
        if a in piv and b in piv:
            dd = (piv[a] - piv[b]).dropna()
            pairs[f"{a} vs {b}"] = dict(
                comparable_steps=int(len(dd)),
                note="step-level, only where both arms recorded the same step index")
    res["_pairwise_note"] = ("arms diverge after the first step, so a paired arm comparison is "
                             "not identified; report per-arm episode-level rates instead")
    res["_pairwise"] = pairs
    OUT["censoring"] = res


# --------------------------------------------------------------------------- #
# 3. Confusion matrix: pre-check vs Gamma_LA
# --------------------------------------------------------------------------- #
def confusion() -> None:
    rec = pd.read_csv(EXP / "07_diagnostics/routeB_recommended_protocol_test.csv")
    fix = pd.read_csv(EXP / "07_diagnostics/routeB_actionset_fix_test.csv")

    def label(unique, share):
        return "non-identifiable" if (unique < 0.60 or share > 0.85) else "identifiable"

    pre = {}
    cur = rec[rec.config == "current protocol"]
    for _, r in cur.iterrows():
        pre[("legacy", r.topology, r.severity)] = label(r.frac_unique_top1,
                                                        r.mean_max_gain_mw / max(r.mean_lost_mw, 1e-9))
    m = fix[fix.action_set == "service-criticality + floor 0.002"]
    for _, r in m.iterrows():
        pre[("main", r.topology, r.severity)] = label(r.frac_unique_top1,
                                                      r.mean_max_gain_mw / max(r.mean_lost_mw, 1e-9))
    legacy = pd.read_csv(EXP / "06_analysis_results/lookahead_gap_old_by_condition.csv")
    legacy_map = {(r.topology, r.severity): float(r.gamma_la_max) for _, r in legacy.iterrows()}
    u = pd.read_csv(SUPP / "results/E1_depth_curve/depth_curve_uncoupled_mk7_by_condition.csv")
    cells = {"precheck_fail__gap_zero": 0, "precheck_fail__gap_positive": 0,
             "precheck_pass__gap_zero": 0, "precheck_pass__gap_positive": 0}
    detail = []
    for (proto, t, s), lab in sorted(pre.items()):
        if proto == "legacy":
            gmax = legacy_map.get((t, s), float("nan"))
            npos = int(gmax > 1e-9)
        else:
            sub = u[(u.topology == t) & (u.severity == s)]
            gmax = float(sub.gamma_max.max())
            npos = int((sub.gamma_max > 1e-9).sum())
        key = ("precheck_fail__" if lab == "non-identifiable" else "precheck_pass__") + \
              ("gap_positive" if gmax > 1e-9 else "gap_zero")
        cells[key] += 1
        detail.append(dict(protocol=proto, topology=t, severity=s, precheck=lab,
                           gamma_la_max=round(gmax, 4), conditions_positive=npos))
    OUT["confusion_precheck_vs_gap"] = dict(
        cells=cells, detail=detail,
        reading=("no condition that the pre-check rejects carries a positive gap, so the pre-check "
                 "never discards a condition with headroom; but the pre-check passes conditions "
                 "whose gap is identically zero (legacy IEEE 300), so it is not equivalent to "
                 "Gamma_LA = 0. The two are complementary: the pre-check is cheap and conservative, "
                 "the gap is complete but costs a DP."))


# --------------------------------------------------------------------------- #
# 4. Max uncoupled gap and its owner
# --------------------------------------------------------------------------- #
def maxima() -> None:
    u = pd.read_csv(SUPP / "results/E1_depth_curve/depth_curve_uncoupled_mk7_by_condition.csv")
    c = pd.read_csv(SUPP / "results/E1_depth_curve/depth_curve_coupled_B6_mk7_by_condition.csv")
    top_u = u.sort_values("gamma_max", ascending=False).head(3)
    top_c = c.sort_values("gamma_max", ascending=False).head(3)
    OUT["maxima"] = dict(
        uncoupled_top=[dict(cond=f"{r.topology}/{r.severity}/{r.capacity_margin}",
                            gamma_max=round(r.gamma_max, 4), n_nonzero=int(r.n_nonzero))
                       for _, r in top_u.iterrows()],
        coupled_top=[dict(cond=f"{r.topology}/{r.severity}/{r.capacity_margin}",
                          gamma_max=round(r.gamma_max, 4), n_nonzero=int(r.n_nonzero))
                     for _, r in top_c.iterrows()],
        condition_mean_uncoupled=round(float(u.gamma_mean.mean()), 3),
        condition_mean_coupled=round(float(c.gamma_mean.mean()), 3))


# --------------------------------------------------------------------------- #
# 5. Eq. (3) assumption A0: does removing ineffective steps raise J?
# --------------------------------------------------------------------------- #
def assumption_a0() -> None:
    ep = pd.read_csv(EXP / "04_evaluation_new_protocol/episodes.csv")
    so = pd.read_csv(EXP / "04_evaluation_new_protocol/stepwise_oracle.csv",
                     usecols=["topology", "severity", "capacity_margin", "train_seed", "method",
                              "scenario_seed", "step_index", "realized_gain_mw",
                              "chosen_is_candidate"])
    n_ineff = so.groupby(["topology", "severity", "capacity_margin", "train_seed", "method",
                          "scenario_seed"]).apply(
        lambda z: pd.Series({"steps": len(z),
                             "ineffective": int((~z.chosen_is_candidate.astype(bool)).sum())}),
        include_groups=False).reset_index()
    OUT["assumption_a0"] = dict(
        episodes_recorded=int(len(ep)),
        steps_lt_25=int((ep.steps < 25).sum()),
        share_steps_lt_25=round(float((ep.steps < 25).mean()), 4),
        step_records=int(len(so)),
        ineffective_steps_total=int(n_ineff.ineffective.sum()),
        share_steps_ineffective=round(float(n_ineff.ineffective.sum() / n_ineff.steps.sum()), 4),
        n_episodes_with_ineffective_step=int((n_ineff.ineffective > 0).sum()),
        n_episode_rows=int(len(n_ineff)),
        note=("an ineffective step realises zero recovery, so deleting it can only raise the "
              "cumulative sum; the assumption is therefore benign, but it is currently implicit"))


if __name__ == "__main__":
    k_sensitivity()
    censoring()
    confusion()
    maxima()
    assumption_a0()
    (HERE / "p1_recomputation.json").write_text(
        json.dumps(OUT, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote reviews/p1_recomputation.json")
    print(json.dumps({k: (v if not isinstance(v, dict) else "…") for k, v in OUT.items()}, ensure_ascii=False))
