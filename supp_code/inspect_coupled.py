"""One-off inspection of the budget-coupled depth curve for a single scenario."""
from __future__ import annotations

import sys

import segan_common as sc

topo = sys.argv[1] if len(sys.argv) > 1 else "ieee118"
severity = sys.argv[2] if len(sys.argv) > 2 else "severe"
margin = float(sys.argv[3]) if len(sys.argv) > 3 else 1.25
budget = int(sys.argv[4]) if len(sys.argv) > 4 else 6
seeds = [int(x) for x in sys.argv[5].split(",")] if len(sys.argv) > 5 else [4119]

env = sc.make_env(topo, severity, margin)
for s in seeds:
    v = sc.InstanceView(env, s, max_k=12)
    print(f"--- seed {s}: K={v.K} init_lost={v.init_lost:.3f} "
          f"budget={budget} ok={v.ok}")
    if not v.ok or v.K <= budget or v.init_lost <= 1e-9:
        continue
    curve, auc_m, auc_o, g_la, term_m = v.coupled_curve(budget)
    print("    curve  =", {k: round(x, 4) for k, x in sorted(curve.items())})
    print(f"    auc_myopic={auc_m:.6f} auc_opt={auc_o:.6f} "
          f"gamma_la={g_la:.6f} curve[B]={curve[max(curve)]:.6f}")
    print(f"    d50={v.depth_to_fraction(curve, 0.50)} "
          f"d90={v.depth_to_fraction(curve, 0.90)} "
          f"d99={v.depth_to_fraction(curve, 0.99)}")
    print(f"    n_states={len(v.masks_by_size(range(0, budget + 1)))}")
env.close()
