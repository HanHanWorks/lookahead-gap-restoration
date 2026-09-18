"""Verify the K < B tail-coefficient fix for the online depth-k lookahead agent.

Runs one episode per (seed, depth) and compares the realised AUC@25 against the
exact offline values. For K < B the budget never binds, so with the fix the
depth-2 agent must reproduce the offline optimum exactly -- and in particular can
no longer fall below the myopic rule, which it did before the fix.

Usage: python verify_tail_fix.py --topo ieee118 --severity moderate --margin 1.15 \
           --budget 6 --seeds 4068,4119 --depths 1,2
"""
from __future__ import annotations

import argparse

import numpy as np

import segan_common as sc
from budget_coupled import LookaheadKAgent, make_budget_env
from e3_run import run_episode


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topo", default="ieee118")
    ap.add_argument("--severity", default="moderate")
    ap.add_argument("--margin", type=float, default=1.15)
    ap.add_argument("--budget", type=int, default=6)
    ap.add_argument("--seeds", default="4068,4119")
    ap.add_argument("--depths", default="1,2")
    ap.add_argument("--max-k", type=int, default=20)
    a = ap.parse_args()

    env = make_budget_env(a.topo, severity=a.severity, margin=a.margin,
                          budget=a.budget)
    print(f"{a.topo}/{a.severity}/m{a.margin}  B={a.budget}  max_k={a.max_k}")
    hdr = (f"{'seed':>6} {'K':>3} | {'offline myopic':>14} {'offline opt':>12} "
           f"{'Gamma':>7} | " + " ".join(f"{'LA'+d:>12}" for d in a.depths.split(",")))
    print(hdr)
    print("-" * len(hdr))
    for s in [int(x) for x in a.seeds.split(",")]:
        v = sc.InstanceView(env, s, max_k=a.max_k)
        if v.K == 0 or v.init_lost <= 1e-9:
            print(f"{s:>6} {v.K:>3} | skipped")
            continue
        _c, auc_m, auc_o, g, _t = v.coupled_curve(a.budget)
        vals = []
        for d in [int(x) for x in a.depths.split(",")]:
            r = run_episode(env, {"LA": LookaheadKAgent(env, depth=d)}, "LA", s,
                            dict(method=f"Lookahead-{d}"))
            vals.append(r["auc25_recomputed"])
        flag = ""
        if g > 1e-9 and abs(vals[-1] - auc_o) > 1e-6:
            flag = f"  <== depth-{a.depths.split(',')[-1]} != optimum by {vals[-1]-auc_o:+.3f}"
        print(f"{s:>6} {v.K:>3} | {auc_m:>14.3f} {auc_o:>12.3f} {g:>7.3f} | "
              + " ".join(f"{x:>12.3f}" for x in vals) + flag)
    env.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
