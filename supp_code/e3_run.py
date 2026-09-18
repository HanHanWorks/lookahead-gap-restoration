"""E3 -- train and evaluate prioritization policies under a reconnection budget.

Protocol (budget-coupled):
    env    BudgetCoupledEnv (true objective) / BudgetCoupledCriticalityEnv (surrogate)
    J      AUC@25 = sum_{t<=B} r(S_t) + (24.5 - B) * r(S_B)
    model  the same DQN configuration as the main protocol, retrained because the
           admissible action sequence changed

Each evaluated scenario also gets its exact offline reference from the subset DP
(Proposition 2 / Corollary 4b): the full-horizon optimum and Gamma_LA. That makes
"did the policy deliver the bound?" a directly answerable question.

Outputs (results/E3_budget_coupled/):
    episodes__{topo}__{severity}__{margin}.csv
    episodes.csv (merged), e3_audit.json

Usage
-----
    python e3_run.py --stage train-one --topo ieee118 --seed 42 --arm surrogate
    python e3_run.py --stage train --timesteps 100000
    python e3_run.py --stage eval --topo ieee118 --severity severe --margin 1.25
    python e3_run.py --stage merge
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import BaseCallback

# keep torch from spawning one BLAS thread pool per worker process
torch.set_num_threads(int(os.environ.get("TORCH_NUM_THREADS", "2")))

import segan_common as sc  # noqa: E402
from budget_coupled import LookaheadKAgent, make_budget_env  # noqa: E402

SUPP_MODELS = sc.SUPP / "models"
OUTD = sc.SUPP / "results" / "E3_budget_coupled"
SUPP_MODELS.mkdir(parents=True, exist_ok=True)
OUTD.mkdir(parents=True, exist_ok=True)

TRAIN_ENV_KWARGS = dict(severity="severe", margin=1.25)

# methods that run once per scenario (deterministic) vs per training seed (learned)
DET_METHODS = [
    ("Electrical-priority", "Electrical-priority"),
    ("Risk-only", "Risk-only"),
    ("One-Step Exact Maxflow", "One-Step Exact Maxflow"),
    ("Lookahead-2", "Lookahead-2"),
    ("Lookahead-3", "Lookahead-3"),
    ("Random", "Random"),
]
LEARN_ARMS = [
    ("DQN", "surrogate", False),
    ("DQN+validity-screen", "surrogate", True),
    ("DQN-true", "trueobj", False),
    ("DQN-true+validity-screen", "trueobj", True),
]


def model_path(topo: str, seed: int, arm: str, budget: int, timesteps: int) -> Path:
    return SUPP_MODELS / f"{topo}_{arm}_b{budget}_dqn_seed{seed}_{timesteps}.zip"


def build_agents(env, models_for_seed):
    from run_capacity_aware_restoration import (  # noqa: PLC0415
        ElectricalPriority, ExactMaxflow, RiskOnly, ValidityScreenedDQN)
    agents = {
        "Electrical-priority": ElectricalPriority(env),
        "Risk-only": RiskOnly(env),
        "One-Step Exact Maxflow": ExactMaxflow(env),
        "Lookahead-2": LookaheadKAgent(env, depth=2),
        "Lookahead-3": LookaheadKAgent(env, depth=3),
    }
    for label, arm, screened in LEARN_ARMS:
        model = models_for_seed.get(arm)
        if model is None:
            continue
        agents[label] = ValidityScreenedDQN(model, env) if screened else model
    return agents


def train_one(topo: str, seed: int, arm: str, budget: int, timesteps: int) -> dict:
    mp = model_path(topo, seed, arm, budget, timesteps)
    if mp.exists():
        return dict(topology=topo, seed=seed, arm=arm, budget=budget,
                    elapsed_s=0.0, status="cached")
    env = make_budget_env(topo, budget=budget, training=(arm == "surrogate"),
                          **TRAIN_ENV_KWARGS)
    model = DQN("MlpPolicy", env, learning_rate=3e-4, buffer_size=20000,
                learning_starts=500, batch_size=64, gamma=0.99, train_freq=4,
                gradient_steps=1, target_update_interval=500,
                exploration_fraction=0.2, exploration_initial_eps=1.0,
                exploration_final_eps=0.05,
                policy_kwargs=dict(net_arch=[128, 128]), seed=seed,
                verbose=0, device="cpu")

    class Progress(BaseCallback):
        def __init__(self, total: int):
            super().__init__()
            self.total, self.t0 = total, time.perf_counter()

        def _on_step(self) -> bool:
            if self.num_timesteps and self.num_timesteps % 20_000 == 0:
                print(f"    [progress] {topo} seed{seed} {arm} b{budget} "
                      f"{self.num_timesteps}/{self.total} "
                      f"{time.perf_counter()-self.t0:.0f}s", flush=True)
            return True

    t0 = time.perf_counter()
    model.learn(total_timesteps=timesteps, progress_bar=False, callback=Progress(timesteps))
    elapsed = time.perf_counter() - t0
    print(f"    [done] {topo} seed{seed} arm={arm} b{budget}: "
          f"{timesteps} steps in {elapsed:.1f}s ({timesteps/max(elapsed,1e-9):.0f} steps/s)",
          flush=True)
    model.save(str(mp))
    env.close()
    return dict(topology=topo, seed=seed, arm=arm, budget=budget,
                elapsed_s=elapsed, status="trained")


def run_episode(env, agents, method, scenario_seed, meta):
    np.random.seed(scenario_seed)
    env.action_space.seed(scenario_seed)
    obs, _ = env.reset(seed=scenario_seed)
    initial_lost = float(env.initial_lost_load)
    rec = [0.0]
    info = {}
    n_eff = 0
    while True:
        agent = agents.get(method)
        if method == "Random":
            action = int(env.action_space.sample())
        elif agent is None:
            action = env.n_switch_actions
        else:
            action = int(agent.predict(obs, deterministic=True)[0])
        obs, _, term, trunc, info = env.step(action)
        n_eff = int(info.get("reconnections_used", 0))
        after = float(info["lost_load"])
        ratio = (initial_lost - after) / initial_lost if initial_lost > 1e-9 else 0.0
        rec.append(float(np.clip(ratio * 100.0, 0.0, 100.0)))
        if term or trunc:
            break
    # AUC@25 = trapezoid over y = [0, r_1 .. r_25] (26 points).
    # NB: an episode that runs the full horizon -- which a reconnection budget
    # forces, since "fully recovered" is never reached when B < m -- must keep
    # r_25. Using rec[1:25] drops it and biases the value down by exactly r_B
    # relative to the subset DP of Proposition 2 / Corollary 4b.
    vals = list(rec[1:26])
    vals += [rec[-1]] * max(0, 25 - len(vals))
    auc25 = float(np.trapz(np.r_[0.0, np.asarray(vals, dtype=float)]))
    return dict(meta, scenario_seed=scenario_seed,
                initial_unserved_mw=initial_lost,
                final_unserved_mw=float(info["lost_load"]),
                load_recovery_pct=float(rec[-1]),
                steps=len(rec) - 1, reconnections_used=n_eff,
                auc25_recomputed=auc25)


def offline_reference(env, scenario_seed, budget, max_k):
    """Exact full-horizon optimum and Gamma_LA for one scenario (Corollary 4b)."""
    v = sc.InstanceView(env, scenario_seed, max_k=max_k)
    if not v.ok or v.K <= budget or v.init_lost <= 1e-9:
        return None
    _, auc_m, auc_o, g, term_m = v.coupled_curve(budget)
    return dict(offline_K=v.K, offline_gamma_la=g,
                offline_auc_myopic=auc_m, offline_auc_optimal=auc_o,
                offline_terminal_myopic_pct=term_m,
                offline_terminal_optimal_pct=v.rec(v.full))


def run_eval(timesteps: int, budget: int, topo: str, severity: str, margin: float,
             n_scenarios: int, max_k: int, lookahead_offline: bool,
             valid_only: bool = False):
    models = {}
    for topo_ in ([topo] if topo else sc.TOPOS):
        for arm in ("surrogate", "trueobj"):
            for seed in sc.TRAIN_SEEDS:
                p = model_path(topo_, seed, arm, budget, timesteps)
                if p.exists():
                    models[(topo_, arm, seed)] = DQN.load(str(p), device="cpu")
                else:
                    print(f"  [warn] missing model {p.name}", flush=True)

    env = make_budget_env(topo, severity=severity, margin=margin, budget=budget,
                          training=False)
    cond = dict(topology=topo, severity=severity, capacity_margin=margin, budget=budget)
    rows = []
    t0 = time.perf_counter()

    # ---- scenario selection + exact references (once per scenario).
    # valid_only=True keeps scanning the candidate pool until n_scenarios instances
    # admit an exact reference (K <= max_k, K > budget, nonzero initial loss), so the
    # head-to-head sample and the depth-curve sample contain the same instances.
    refs = {}
    seeds = []
    pool = sc.CANDIDATE_SEEDS if valid_only else sc.EVAL_SEEDS[:n_scenarios]
    for s in pool:
        if len(seeds) >= n_scenarios:
            break
        if lookahead_offline:
            r = offline_reference(env, s, budget, max_k)
            if r is None:
                if valid_only:
                    continue
            else:
                refs[s] = r
        seeds.append(s)
    if lookahead_offline:
        print(f"  offline references: {len(refs)}/{len(seeds)} scenarios "
              f"({time.perf_counter()-t0:.0f}s)", flush=True)

    # ---- one agent set per (method); learners use one model per training seed
    for s in seeds:
        for label, _ in DET_METHODS:
            agents = build_agents(env, {})
            meta = dict(cond, train_seed=-1, method=label)
            row = run_episode(env, agents, label, s, meta)
            row.update(refs.get(s, {}))
            rows.append(row)
        for label, arm, screened in LEARN_ARMS:
            per_seed = []
            for seed in sc.TRAIN_SEEDS:
                m = models.get((topo, arm, seed))
                if m is None:
                    continue
                agents = build_agents(env, {arm: m})
                meta = dict(cond, train_seed=seed, method=label)
                per_seed.append(run_episode(env, agents, label, s, meta))
            agg = {k: float(np.mean([r[k] for r in per_seed]))
                   for k in ("auc25_recomputed", "load_recovery_pct",
                             "final_unserved_mw", "reconnections_used")}
            base = dict(per_seed[0]) if per_seed else dict(cond, method=label,
                                                           scenario_seed=s, train_seed=-1)
            base.update(agg)
            base["train_seed"] = -1
            base["n_train_seeds"] = len(per_seed)
            base.update(refs.get(s, {}))
            rows.append(base)
        if len(rows) % 100 < 20:
            print(f"  [{time.perf_counter()-t0:6.0f}s] {len(rows)} rows", flush=True)
    env.close()
    return pd.DataFrame(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True,
                    choices=["train-one", "train", "eval", "merge", "smoke",
                             "validate", "rolling"])
    ap.add_argument("--timesteps", type=int, default=100_000)
    ap.add_argument("--budget", type=int, default=6)
    ap.add_argument("--topo", default="")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--arm", default="surrogate")
    ap.add_argument("--severity", default="")
    ap.add_argument("--margin", type=float, default=0.0)
    ap.add_argument("--scenarios", type=int, default=20)
    ap.add_argument("--max-k", type=int, default=12)
    ap.add_argument("--max-depth", type=int, default=6,
                    help="rolling stage, uncoupled protocol only")
    ap.add_argument("--no-offline", action="store_true")
    ap.add_argument("--valid-seeds", action="store_true",
                    help="evaluation only: keep scanning the candidate pool until "
                         "n_scenarios instances have an exact reference, so the "
                         "head-to-head sample matches the depth-curve sample")
    a = ap.parse_args()

    if a.stage == "train-one":
        print(json.dumps(train_one(a.topo, a.seed, a.arm, a.budget, a.timesteps)),
              flush=True)
        return 0

    if a.stage == "train":
        rows = []
        for arm in ("surrogate", "trueobj"):
            for topo in sc.TOPOS:
                for seed in sc.TRAIN_SEEDS:
                    info = train_one(topo, seed, arm, a.budget, a.timesteps)
                    rows.append(info)
                    print("[train]", info, flush=True)
        pd.DataFrame(rows).to_csv(sc.SUPP / "results" / "E3_budget_coupled" /
                                  f"training_log_b{a.budget}.csv", index=False)
        return 0

    if a.stage == "merge":
        parts = sorted(OUTD.glob("episodes__*.csv"))
        if not parts:
            print("no partial files")
            return 1
        df = pd.concat([pd.read_csv(p) for p in parts], ignore_index=True)
        df.to_csv(OUTD / "episodes.csv", index=False)
        audit = dict(rows=int(len(df)),
                     conditions=int(df.groupby(
                         ["topology", "severity", "capacity_margin"]).ngroups),
                     methods=int(df.method.nunique()))
        sc.write_json(OUTD / "e3_audit.json", audit)
        print(json.dumps(audit, indent=2))
        return 0

    if a.stage == "smoke":
        t0 = time.perf_counter()
        info = train_one("ieee118", 42, "surrogate", a.budget, 2000)
        print("smoke train:", info, f"wall={time.perf_counter()-t0:.1f}s")
        df = run_eval(2000, a.budget, "ieee118", "severe", 1.25, 2, 11, True)
        print(df[["method", "scenario_seed", "auc25_recomputed",
                  "offline_gamma_la", "offline_auc_optimal"]].to_string(index=False))
        return 0

    if a.stage == "validate":
        # Correctness self-check for the online depth-k agent.
        #
        # The agent re-plans at every decision (receding horizon), so its value is
        # >= the STATIC depth-k plan value computed by the DP (which commits to k
        # steps and then goes myopic). The right checks are therefore:
        #   (i)   realised(depth=B) == exact optimum  (pi_B is exact)
        #   (ii)  auc_myopic <= realised <= auc_optimal
        #   (iii) realised is non-decreasing in depth
        #   (iv)  realised >= auc_myopic + Gamma_k^static   (rolling dominates static)
        topo = a.topo or "ieee118"
        severity = a.severity or "severe"
        margin = a.margin or 1.25
        env = make_budget_env(topo, severity=severity, margin=margin, budget=a.budget)
        rows = []
        n_done = 0
        for s in sc.CANDIDATE_SEEDS:
            if n_done >= a.scenarios:
                break
            v = sc.InstanceView(env, s, max_k=a.max_k)
            if not v.ok or v.K <= a.budget or v.init_lost <= 1e-9:
                continue
            n_done += 1
            curve, auc_m, auc_o, g_la, _tm = v.coupled_curve(a.budget)
            realized = {}
            for d in range(1, a.budget + 1):
                agents = {"LA": LookaheadKAgent(env, depth=d)}
                r = run_episode(env, agents, "LA", s, dict(method=f"Lookahead-{d}"))
                realized[d] = r["auc25_recomputed"]
                rows.append(dict(
                    topology=topo, severity=severity, scenario_seed=s, K=v.K, depth=d,
                    realized=round(realized[d], 6),
                    auc_myopic=round(auc_m, 6), auc_optimal=round(auc_o, 6),
                    gamma_la_static=round(curve[d], 6),
                    static_total=round(auc_m + curve[d], 6),
                    excess_over_static=round(realized[d] - (auc_m + curve[d]), 6),
                    ge_myopic=bool(realized[d] >= auc_m - 1e-6),
                    le_optimal=bool(realized[d] <= auc_o + 1e-6)))
            block = rows[-a.budget:]
            checks = dict(
                exact_at_B=bool(abs(realized[a.budget] - auc_o) < 1e-6),
                monotone=all(realized[d] <= realized[d + 1] + 1e-6
                             for d in range(1, a.budget)),
                all_ge_myopic=all(r["ge_myopic"] for r in block),
                all_le_optimal=all(r["le_optimal"] for r in block),
            )
            print(f"  seed={s} K={v.K} myopic={auc_m:.3f} opt={auc_o:.3f} "
                  f"realized={ {d: round(x,3) for d,x in realized.items()} } "
                  f"checks={checks}", flush=True)
        env.close()
        out = pd.DataFrame(rows)
        print(out.to_string(index=False))
        if len(out):
            print(f"\nmax excess of rolling over static = "
                  f"{out.excess_over_static.max():.6f}  (>= 0 expected)")
            print(f"rows = {len(out)}")
        out.to_csv(OUTD / f"validate_agent_b{a.budget}.csv", index=False)
        return 0

    if a.stage == "rolling":
        # Deployable depth-k LOCAL: the agent re-plans at every decision, so the
        # realised value can be far above the STATIC depth-k plan value (E1's
        # Gamma_k). Both are reported side by side: E1 gives the value of a
        # committed plan, this gives what a rollout controller actually earns.
        # --budget 0 selects the uncoupled protocol (Lemma 1 tail cancels).
        topos = [a.topo] if a.topo else sc.TOPOS
        severities = [a.severity] if a.severity else ["severe"]
        margins = [a.margin] if a.margin else list(sc.MARGINS)
        max_depth = a.budget if a.budget > 0 else min(a.max_depth, 8)
        rows = []
        t0 = time.perf_counter()
        for topo in topos:
            for severity in severities:
                for margin in margins:
                    if a.budget > 0:
                        env = make_budget_env(topo, severity=severity, margin=margin,
                                              budget=a.budget)
                    else:
                        env = sc.make_env(topo, severity, margin)
                    n_done = 0
                    for s in sc.CANDIDATE_SEEDS:
                        if n_done >= a.scenarios:
                            break
                        v = sc.InstanceView(env, s, max_k=a.max_k)
                        if not v.ok or v.init_lost <= 1e-9:
                            continue
                        if a.budget > 0 and v.K <= a.budget:
                            continue
                        if a.budget > 0:
                            curve, auc_m, auc_o, g_la, _tm = v.coupled_curve(a.budget)
                        else:
                            curve = v.uncoupled_curve()
                            auc_m = v.myopic_sum() + (24.5 - v.K) * v.rec(v.full)
                            auc_o = v.exact_sum() + (24.5 - v.K) * v.rec(v.full)
                            g_la = curve.get(v.K, 0.0)
                        n_done += 1
                        for d in range(1, max_depth + 1):
                            ag = LookaheadKAgent(env, depth=d, uncoupled=(a.budget == 0))
                            r = run_episode(env, {"LA": ag}, "LA", s,
                                            dict(method=f"Lookahead-{d}"))
                            rows.append(dict(
                                topology=topo, severity=severity,
                                capacity_margin=margin, budget=a.budget,
                                scenario_seed=s, K=v.K, depth=d,
                                realized_auc=r["auc25_recomputed"],
                                auc_myopic=auc_m, auc_optimal=auc_o,
                                gamma_static=curve.get(d, np.nan),
                                gamma_realized=r["auc25_recomputed"] - auc_m,
                                gamma_la=g_la,
                                share_of_la=(r["auc25_recomputed"] - auc_m) / g_la
                                if g_la > 1e-9 else None))
                    env.close()
                    print(f"[{time.perf_counter()-t0:6.0f}s] {topo}/{severity}/"
                          f"m{margin} B={a.budget}: {n_done} scenarios", flush=True)
        df = pd.DataFrame(rows)
        tag = "uncoupled" if a.budget == 0 else f"b{a.budget}"
        df.to_csv(OUTD / f"rolling_depth_curve_{tag}.csv", index=False)
        print("\n=== rolling vs static by depth (mean over scenarios) ===")
        print(df.groupby("depth").agg(
            n=("realized_auc", "size"),
            gamma_static_mean=("gamma_static", "mean"),
            gamma_realized_mean=("gamma_realized", "mean"),
            share_la_mean=("share_of_la", "mean")).round(4).to_string())
        return 0

    topos = [a.topo] if a.topo else sc.TOPOS
    severities = [a.severity] if a.severity else ["severe"]
    margins = [a.margin] if a.margin else list(sc.MARGINS)
    for topo in topos:
        for severity in severities:
            for margin in margins:
                t0 = time.perf_counter()
                df = run_eval(a.timesteps, a.budget, topo, severity, margin,
                              a.scenarios, a.max_k, not a.no_offline,
                              valid_only=a.valid_seeds)
                tag = f"__{topo}__{severity}__{margin}"
                stem = "episodes_valid" if a.valid_seeds else "episodes"
                df.to_csv(OUTD / f"{stem}{tag}.csv", index=False)
                print(f"[eval{'/valid' if a.valid_seeds else ''}] {tag}: {len(df)} rows "
                      f"in {time.perf_counter()-t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
