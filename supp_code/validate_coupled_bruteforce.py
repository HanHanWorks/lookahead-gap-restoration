"""Independent brute-force validator for the budget-coupled exact DP.

With a reconnection budget B the exact optimum is a maximum over ORDERED B-subsets
of the broken key lines, and the objective is

    J(S_1..S_B) = sum_{t<=B} rec(S_t)  +  (24.5 - B) * rec(S_B)

(the trapezoid AUC@25 with the state frozen after the budget is exhausted; 24.5-B
follows from summing the 24 interior ordinates plus the half weight of the last).

K <= 12 and B <= 6 make outright enumeration feasible (12P6 = 665 280), and this
shares no code with InstanceView.coupled_curve -- so it is a genuine check on the
DP, and in particular on the counter-intuitive B = 4 results.

Usage:  python validate_coupled_bruteforce.py --topo ieee118 --severity severe \
            --margin 1.25 --budgets 2,4,6 --seeds 4051,4119
"""
from __future__ import annotations

import argparse
import itertools

import numpy as np

import segan_common as sc


def brute_force(v: sc.InstanceView, budget: int):
    """(myopic_greedy, exact_optimum, exact_order) over ordered B-subsets."""
    K = v.K
    B = min(int(budget), K)
    tail = 24.5 - B
    rec = v.rec                                   # cached, shares the service model

    def value(seq):
        mask, tot = 0, 0.0
        for i in seq:
            mask |= 1 << i
            tot += rec(mask)
        return tot + tail * rec(mask)

    # greedy / myopic: take the line with the largest immediate recovery
    mask, myopic = 0, 0.0
    for _ in range(B):
        best, bv = None, -np.inf
        for i in range(K):
            if mask >> i & 1:
                continue
            val = rec(mask | (1 << i))
            if val > bv:
                bv, best = val, i
        if best is None:
            break
        mask |= 1 << best
        myopic += bv
    myopic += tail * rec(mask)

    best_sum, best_seq = -np.inf, ()
    for seq in itertools.permutations(range(K), B):
        val = value(seq)
        if val > best_sum:
            best_sum, best_seq = val, seq
    return myopic, best_sum, best_seq


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topo", default="ieee118")
    ap.add_argument("--severity", default="severe")
    ap.add_argument("--margin", type=float, default=1.25)
    ap.add_argument("--budgets", default="2,4,6")
    ap.add_argument("--seeds", default="4051,4119")
    ap.add_argument("--max-k", type=int, default=12)
    a = ap.parse_args()

    env = sc.make_env(a.topo, a.severity, a.margin)
    print(f"{a.topo}/{a.severity}/m{a.margin}\n")
    hdr = (f"{'seed':>6} {'K':>3} {'B':>2} | {'DP myopic':>13} {'BF myopic':>13} "
           f"{'diff':>10} | {'DP opt':>13} {'BF opt':>13} {'diff':>10} | "
           f"{'DP Gamma':>10} {'BF Gamma':>10}")
    print(hdr)
    print("-" * len(hdr))
    worst = 0.0
    for s in [int(x) for x in a.seeds.split(",")]:
        v = sc.InstanceView(env, s, max_k=a.max_k)
        if not v.ok or v.init_lost <= 1e-9:
            print(f"{s:>6}  skipped (K={v.K}, ok={v.ok})")
            continue
        for B in [int(x) for x in a.budgets.split(",")]:
            if v.K <= B:
                continue
            _c, dp_myo, dp_opt, dp_g, _t = v.coupled_curve(B)
            bf_myo, bf_opt, _seq = brute_force(v, B)
            d1, d2 = dp_myo - bf_myo, dp_opt - bf_opt
            worst = max(worst, abs(d1), abs(d2))
            print(f"{s:>6} {v.K:>3} {B:>2} | {dp_myo:>13.6f} {bf_myo:>13.6f} "
                  f"{d1:>10.2e} | {dp_opt:>13.6f} {bf_opt:>13.6f} {d2:>10.2e} | "
                  f"{dp_g:>10.6f} {bf_opt-bf_myo:>10.6f}")
    env.close()
    print(f"\nmax |DP - brute force| over myopic and optimum = {worst:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
