"""Locate the K > max_k failure of the online depth-2 lookahead agent.

Head-to-head evidence (ieee118/moderate/1.15, B=6):
  * for every scenario with an exact reference (K <= 12) the online Lookahead-2 AUC
    equals the offline optimum EXACTLY, and exceeds the myopic rule;
  * for every scenario WITHOUT a reference (K > 12, so offline_auc_optimal is NaN)
    Lookahead-2 falls well BELOW the myopic rule.

Theory says a depth-k rollout with a myopic tail can never be worse than the plain
myopic rule -- the myopic path is one of its candidates.  So something about large K
breaks the agent.  This probe recomputes the offline myopic and optimum with
max_k raised to the true K, and prints both against the online numbers.

Usage: python probe_largeK.py --topo ieee118 --severity moderate --margin 1.15 \
           --budget 6 --seeds 4068,4119 --max-k 20
"""
from __future__ import annotations

import argparse
import time

import segan_common as sc
from budget_coupled import make_budget_env


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topo", default="ieee118")
    ap.add_argument("--severity", default="moderate")
    ap.add_argument("--margin", type=float, default=1.15)
    ap.add_argument("--budget", type=int, default=6)
    ap.add_argument("--seeds", default="4068,4119")
    ap.add_argument("--max-k", type=int, default=20)
    a = ap.parse_args()

    env = make_budget_env(a.topo, severity=a.severity, margin=a.margin,
                          budget=a.budget)
    print(f"{a.topo}/{a.severity}/m{a.margin}  B={a.budget}  max_k={a.max_k}")
    hdr = (f"{'seed':>6} {'K':>3} | {'offline myopic':>15} {'offline opt':>13} "
           f"{'Gamma_LA':>10} {'states':>8} {'sec':>6}")
    print(hdr)
    print("-" * len(hdr))
    for s in [int(x) for x in a.seeds.split(",")]:
        v = sc.InstanceView(env, s, max_k=a.max_k)
        if v.K == 0 or v.init_lost <= 1e-9:
            print(f"{s:>6} {v.K:>3} | skipped")
            continue
        t = time.perf_counter()
        n_states = sum(len(list(_iter_combos(v.K, k))) for k in range(0, a.budget + 1))
        curve, auc_m, auc_o, g, term_m = v.coupled_curve(a.budget)
        print(f"{s:>6} {v.K:>3} | {auc_m:>15.3f} {auc_o:>13.3f} {g:>10.3f} "
              f"{n_states:>8} {time.perf_counter()-t:>6.1f}")
    env.close()
    return 0


def _iter_combos(n, k):
    from itertools import combinations
    return combinations(range(n), k)


if __name__ == "__main__":
    raise SystemExit(main())
