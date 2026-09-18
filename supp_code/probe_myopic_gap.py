"""Why does the ONLINE myopic rule beat the OFFLINE optimum in moderate conditions?

The head-to-head says LA2 == the exact offline optimum on every valid instance, yet
the online one-step myopic agent scores higher than LA2 there. Both cannot be true
unless the offline model is not a faithful description of the environment, so this
probe compares the two directly on the same instance:

  * offline: InstanceView.rec(mask) -- recovery for a reconnected-key-line set,
    derived by temporarily setting env.broken_lines and calling the service model;
  * online : step the env with the one-step myopic rule and read info["lost_load"].

If the online trajectory's recovery ever exceeds rec(mask) for the same set of
reconnected key lines, the environment's loss is not a function of the broken set
alone (path dependence), or the two use different service evaluations.

Usage: python probe_myopic_gap.py --topo ieee118 --severity moderate --margin 1.15 \
           --budget 6 --seed 4034
"""
from __future__ import annotations

import argparse

import numpy as np

import segan_common as sc
from budget_coupled import make_budget_env


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topo", default="ieee118")
    ap.add_argument("--severity", default="moderate")
    ap.add_argument("--margin", type=float, default=1.15)
    ap.add_argument("--budget", type=int, default=6)
    ap.add_argument("--seed", type=int, default=4034)
    ap.add_argument("--max-k", type=int, default=12)
    a = ap.parse_args()

    env = make_budget_env(a.topo, severity=a.severity, margin=a.margin,
                          budget=a.budget)
    v = sc.InstanceView(env, a.seed, max_k=a.max_k)
    print(f"{a.topo}/{a.severity}/m{a.margin} B={a.budget} seed={a.seed}")
    print(f"  K (broken key lines) = {v.K}   init_lost = {v.init_lost:.3f} mw")
    print(f"  rec(all key lines)   = {v.rec(v.full):.6f} %")

    obs, _ = env.reset(seed=a.seed)
    init_lost = float(env.initial_lost_load)
    print(f"\n{'t':>3} {'action':>7} {'used':>5} {'online%':>10} {'model%':>10} "
          f"{'diff':>10}  reconnected_key")
    reconn: set[int] = set()
    for t in range(1, 26):
        avail = [li for li in env.key_lines if li in env.broken_lines]
        if not avail:
            print(f"{t:>3} {'--':>7}  (nothing broken)")
            break
        # one-step myopic on the ONLINE service model
        env_state = env.broken_lines
        best, best_val = None, -np.inf
        for li in avail:
            env.broken_lines = set(env_state) - {li}
            val = float(env._calculate_lost_load())
            if val < best_val or best is None:
                best_val, best = val, li
        env.broken_lines = env_state
        action = env.key_lines.index(best)

        obs, _r, term, trunc, info = env.step(action)
        if info.get("reconnections_used", 0) > len(reconn):
            reconn.add(best)
        online = (init_lost - float(info["lost_load"])) / init_lost * 100.0

        mask = 0
        for i in range(v.K):
            if v.keys[i] in reconn:
                mask |= 1 << i
        model = v.rec(mask)
        flag = "  <== ONLINE BETTER" if online > model + 1e-6 else ""
        print(f"{t:>3} {best:>7} {info.get('reconnections_used', 0):>5} "
              f"{online:>10.4f} {model:>10.4f} {online - model:>10.4f}{flag}")
        if term or trunc:
            break
    env.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
