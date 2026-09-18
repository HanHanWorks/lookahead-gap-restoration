"""E2 -- phase diagram: where does a learned prioritization policy have headroom?

Sweeps the two axes that the theory says matter:
    * reconnection budget B in {0 (uncoupled), 4, 6, 8}   -> resource coupling
    * capacity margin in {1.15, 1.25, 1.50}
over both topologies and severities, and records per scenario:
    K (broken key lines), Gamma_LA, depth-to-90% of Gamma_LA, terminal gap.

Region classification per condition:
    * "non-identifiable"  : every sampled scenario has Gamma_LA == 0
    * "shallow"           : Gamma_LA > 0 and a depth <= 3 realises >= 90%
    * "long-range"        : Gamma_LA > 0 and depth >= 4 is needed

Outputs (results/E2_phase_diagram/):
    phase_scenarios.csv, phase_by_condition.csv, e2_summary.json
"""
from __future__ import annotations

import argparse
import time

import numpy as np
import pandas as pd

import segan_common as sc

OUTD = sc.SUPP / "results" / "E2_phase_diagram"
OUTD.mkdir(parents=True, exist_ok=True)

BUDGETS = [0, 4, 6, 8]
MARGINS = [1.15, 1.25, 1.50]


def classify(gamma: float, d90) -> str:
    if gamma <= 1e-9:
        return "non-identifiable"
    if d90 is None:
        return "unresolved"
    return "shallow" if d90 <= 3 else "long-range"


def sweep_condition(topo: str, severity: str, margin: float, budget: int,
                    n_scenarios: int, max_k: int, min_k: int) -> list[dict]:
    env = sc.make_env(topo, severity, margin)
    rows = []
    for s in sc.CANDIDATE_SEEDS:
        if len(rows) >= n_scenarios:
            break
        v = sc.InstanceView(env, s, max_k=max_k)
        if not v.ok or v.init_lost <= 1e-9:
            continue
        # min_k fixes the instance sample across the BUDGET axis. Filtering on
        # K > budget instead (the natural reading) makes each budget draw a
        # different sample of scenarios, so a difference across budgets cannot be
        # attributed to the budget. Requiring K >= min_k keeps the sample identical.
        if v.K < min_k:
            continue
        t = time.perf_counter()
        if budget > 0:
            curve, auc_m, auc_o, gamma, _term_m = v.coupled_curve(budget)
        else:
            curve = v.uncoupled_curve()
            auc_m = v.myopic_sum() + (24.5 - v.K) * v.rec(v.full)
            auc_o = v.exact_sum() + (24.5 - v.K) * v.rec(v.full)
            gamma = curve.get(v.K, 0.0)
        d50 = v.depth_to_fraction(curve, 0.50)
        d90 = v.depth_to_fraction(curve, 0.90)
        rows.append(dict(
            topology=topo, severity=severity, capacity_margin=margin, budget=budget,
            scenario_seed=s, K=v.K, init_unserved_mw=v.init_lost,
            budget_binds=int(v.K > budget) if budget > 0 else 0,
            gamma_la=gamma, auc25_myopic=auc_m, auc25_optimal=auc_o,
            depth_to_50pct=d50, depth_to_90pct=d90,
            region=classify(gamma, d90),
            n_maxflow_calls=len(v._cache),
            eval_seconds=round(time.perf_counter() - t, 3),
        ))
    env.close()
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topos", default=",".join(sc.TOPOS))
    ap.add_argument("--severities", default=",".join(sc.SEVERITIES))
    ap.add_argument("--budgets", default=",".join(str(b) for b in BUDGETS))
    ap.add_argument("--margins", default=",".join(str(m) for m in MARGINS))
    ap.add_argument("--scenarios", type=int, default=12)
    ap.add_argument("--max-k", type=int, default=12)
    ap.add_argument("--min-k", type=int, default=0,
                    help="require K >= min_k for every scenario; 0 -> max(budgets)+1, "
                         "which keeps the instance sample identical across budgets")
    a = ap.parse_args()

    budgets = [int(x) for x in a.budgets.split(",") if x.strip()]
    margins = [float(x) for x in a.margins.split(",") if x.strip()]
    min_k = a.min_k or (max(budgets) + 1)
    print(f"budgets={budgets} margins={margins} min_k={min_k} "
          f"(sample fixed across budgets)", flush=True)
    rows: list[dict] = []
    t0 = time.perf_counter()
    for topo in [x for x in a.topos.split(",") if x]:
        for severity in [x for x in a.severities.split(",") if x]:
            for margin in margins:
                for budget in budgets:
                    got = sweep_condition(topo, severity, margin, budget,
                                          a.scenarios, a.max_k, min_k)
                    rows.extend(got)
                    print(f"[{time.perf_counter()-t0:7.0f}s] {topo}/{severity}/"
                          f"m{margin}/B{budget}: {len(got)} scenarios", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(OUTD / "phase_scenarios.csv", index=False,
              float_format="%.6f")

    g = df.groupby(["topology", "severity", "capacity_margin", "budget"]).agg(
        n=("K", "size"), mean_K=("K", "mean"),
        init_unserved=("init_unserved_mw", "mean"),
        share_nonzero=("gamma_la", lambda s: float((s > 1e-9).mean())),
        gamma_mean=("gamma_la", "mean"), gamma_max=("gamma_la", "max"),
        d90_median=("depth_to_90pct", "median"),
        n_shallow=("region", lambda s: int((s == "shallow").sum())),
        n_longrange=("region", lambda s: int((s == "long-range").sum())),
        n_nonident=("region", lambda s: int((s == "non-identifiable").sum())),
    ).round(4)
    g.to_csv(OUTD / "phase_by_condition.csv")
    print("\n=== phase by condition ===")
    print(g.to_string())

    print("\n=== region counts by budget ===")
    print(df.groupby(["budget", "region"]).size().unstack(fill_value=0).to_string())

    sc.write_json(OUTD / "e2_summary.json", dict(
        n_scenarios=int(len(df)),
        budgets=budgets, margins=margins,
        elapsed_seconds=round(time.perf_counter() - t0, 1),
        integration="max-flow service model (exact, cheap evaluator)",
    ))
    print(f"\nwrote -> {OUTD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
