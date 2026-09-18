"""E4 -- decision-time benchmark extended with depth-limited lookahead.

Same methodology as benchmark_timing.py (identical decision states, no environment
advancement inside the timed region), extended with:
  * Lookahead-1 / -2 / -3   online depth-k lookahead (exact service model)
  * the budget-coupled protocol (B < m), where the myopic rule stops being optimal

The point: the offline DP that computes Gamma_k is a one-off cost, while the
ONLINE depth-k policy costs C(K, <=k) service evaluations per decision. This
script measures that online cost so the cost-quality plane in the paper has both
axes from the same protocol.

Outputs (results/E4_timing/):
    timing_ext_uncoupled.csv, timing_ext_budget{B}.csv, e4_summary.json
"""
from __future__ import annotations

import argparse
import time

import numpy as np
import pandas as pd
from stable_baselines3 import DQN

import segan_common as sc
from budget_coupled import LookaheadKAgent, make_budget_env

OUTD = sc.SUPP / "results" / "E4_timing"
OUTD.mkdir(parents=True, exist_ok=True)
MODELS = sc.SUPP / "models"

MAX_STEPS = 12
REPETITIONS = 3


def build_methods(env, budget: int, topo: str, timesteps: int):
    from run_capacity_aware_restoration import (  # noqa: PLC0415
        ElectricalPriority, ExactMaxflow, RiskOnly, ValidityScreenedDQN)

    # NB: uncoupled must be passed explicitly. With budget=0 the coupled branch
    # computes left = 0 - 0 and returns a no-op immediately, which would time the
    # lookahead agents at ~1 us and silently understate their cost by ~1e3.
    unc = budget == 0
    methods = {
        "Electrical-priority": ElectricalPriority(env),
        "Risk-only": RiskOnly(env),
        "One-Step Exact Maxflow": ExactMaxflow(env),
        "Lookahead-1": LookaheadKAgent(env, depth=1, uncoupled=unc),
        "Lookahead-2": LookaheadKAgent(env, depth=2, uncoupled=unc),
        "Lookahead-3": LookaheadKAgent(env, depth=3, uncoupled=unc),
    }
    # budget-coupled models live in $SUPP/models with a _b{budget}_ tag; the
    # unconstrained originals live in the main project without one.
    for label, arm in (("DQN", "surrogate"), ("DQN-true", "trueobj")):
        for seed in sc.TRAIN_SEEDS[:1]:
            if budget > 0:
                cands = [MODELS / f"{topo}_{arm}_b{budget}_dqn_seed{seed}_{timesteps}.zip"]
            else:
                cands = [MODELS / f"{topo}_{arm}_b0_dqn_seed{seed}_{timesteps}.zip",
                         sc.ROOT / "SEGAN_submission_2026-09" / "data_v2" / "models" /
                         f"{topo}_{arm}_dqn_seed{seed}_{timesteps}.zip"]
            p = next((c for c in cands if c.exists()), None)
            if p is None:
                print(f"  [skip] {label}: none of "
                      f"{[c.name for c in cands]} found", flush=True)
                continue
            m = DQN.load(str(p), device="cpu")
            methods[label] = m
            methods[label + "+validity-screen"] = ValidityScreenedDQN(m, env)
    return methods


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topos", default=",".join(sc.TOPOS))
    ap.add_argument("--severities", default=",".join(sc.SEVERITIES))
    ap.add_argument("--margin", type=float, default=1.25)
    ap.add_argument("--budget", type=int, default=0, help="0 = uncoupled protocol")
    ap.add_argument("--scenarios", type=int, default=12)
    ap.add_argument("--timesteps", type=int, default=100_000)
    a = ap.parse_args()

    rows = []
    for topo in [x for x in a.topos.split(",") if x]:
        for severity in [x for x in a.severities.split(",") if x]:
            if a.budget > 0:
                env = make_budget_env(topo, severity=severity, margin=a.margin,
                                      budget=a.budget)
            else:
                env = sc.make_env(topo, severity, a.margin)
            methods = build_methods(env, a.budget, topo, a.timesteps)
            driver = methods["One-Step Exact Maxflow"]
            times = {k: [] for k in methods}
            n_dec = 0
            t0 = time.perf_counter()
            for s in sc.EVAL_SEEDS[:a.scenarios]:
                np.random.seed(s)
                env.action_space.seed(s)
                obs, _ = env.reset(seed=s)
                for _ in range(MAX_STEPS):
                    if not env.broken_key_lines:
                        break
                    budget_left = (env.reconnection_budget - env.reconnections_used
                                   if a.budget > 0 else None)
                    if a.budget > 0 and budget_left <= 0:
                        break
                    # NB: use the observation as returned by reset()/step(). The
                    # budget-coupled env appends the remaining-budget slot inside
                    # those calls; re-deriving it with _get_obs() would hand the
                    # model the un-augmented (145-dim) vector and raise a shape error.
                    for name, agent in methods.items():
                        for _ in range(REPETITIONS):
                            t = time.perf_counter()
                            agent.predict(obs, deterministic=True)
                            times[name].append((time.perf_counter() - t) * 1000.0)
                    n_dec += 1
                    act = int(driver.predict(obs, deterministic=True)[0])
                    obs, _r, term, trunc, _info = env.step(act)
                    if term or trunc:
                        break
            env.close()
            for name, vals in times.items():
                v = np.asarray(vals, dtype=float)
                if not len(v):
                    continue
                rows.append(dict(
                    topology=topo, severity=severity, budget=a.budget,
                    method=name, n_decisions=n_dec, n_timed=int(len(v)),
                    mean_ms=float(v.mean()), p50_ms=float(np.median(v)),
                    p95_ms=float(np.percentile(v, 95)), max_ms=float(v.max()),
                ))
            print(f"[{time.perf_counter()-t0:6.0f}s] {topo}/{severity} "
                  f"budget={a.budget}: {n_dec} decision points, "
                  f"{len(methods)} methods", flush=True)

    df = pd.DataFrame(rows)
    tag = "uncoupled" if a.budget == 0 else f"budget{a.budget}"
    df.to_csv(OUTD / f"timing_ext_{tag}.csv", index=False)
    piv = df.pivot_table(index=["topology", "severity"], columns="method",
                         values="mean_ms")
    print("\n=== policy-side decision time (ms) ===")
    print(piv.round(4).to_string())
    if "Lookahead-1" in piv.columns:
        base = piv.get("One-Step Exact Maxflow")
        if base is not None:
            print("\n=== factor vs One-Step Exact Maxflow ===")
            print(piv.div(base, axis=0).round(2).to_string())
    sc.write_json(OUTD / f"e4_summary_{tag}.json",
                  dict(budget=a.budget, rows=int(len(df)),
                       methods=sorted(df.method.unique())))
    print(f"\nwrote -> {OUTD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
