"""E1 -- depth-limited lookahead curves Gamma_k for sequential restoration.

For each scenario with K broken key lines:
    pi_k = exact lookahead of depth k, then the one-step myopic rule
    Gamma_k = J(pi_k) - J(pi_1)          (AUC@25 units)

Identity checks built in:
    Gamma_1 == 0            (pi_1 is the myopic rule)
    Gamma_K == Gamma_LA     (cross-checked against the frozen lookahead_gap CSV)

With --budget B > 0 the same curve is produced under a reconnection budget
(B < m reconnections admissible), where the terminal term no longer cancels.

Outputs (results/E1_depth_curve/):
    depth_curve_uncoupled.csv / _by_condition.csv
    depth_curve_coupled_B{B}.csv / _by_condition.csv
    e1_summary.json
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

import segan_common as sc


CURVE_COLS = [f"gamma_d{k}" for k in range(1, 16)]


def run_condition(topo: str, severity: str, margin: float, budget: int,
                  n_scenarios: int, max_k: int, verbose: bool,
                  min_k: int = 0) -> list[dict]:
    env = sc.make_env(topo, severity, margin)
    rows: list[dict] = []
    t0 = time.perf_counter()
    for sc_seed in sc.CANDIDATE_SEEDS:
        if len(rows) >= n_scenarios:
            break
        v = sc.InstanceView(env, sc_seed, max_k=max_k)
        if not v.ok:
            continue
        if v.init_lost <= 1e-9:
            continue
        # min_k is the instance-selection rule, and it must NOT depend on the
        # protocol. Filtering on K > budget instead gives the coupled run a
        # different sample of scenarios than the uncoupled one (for moderate
        # conditions only 11 of 20 seeds overlapped), so a protocol difference
        # would be confounded with an instance difference.
        if v.K < min_k:
            continue
        if budget > 0:
            t = time.perf_counter()
            curve, auc_myopic, auc_opt, g_la, terminal_myopic = v.coupled_curve(budget)
        else:
            t = time.perf_counter()
            curve = v.uncoupled_curve()
            auc_myopic = v.myopic_sum() + (24.5 - v.K) * v.rec(v.full)
            auc_opt = v.exact_sum() + (24.5 - v.K) * v.rec(v.full)
            g_la = curve.get(v.K, 0.0)
            terminal_myopic = v.rec(v.full)
        elapsed = time.perf_counter() - t
        row = dict(
            topology=topo, severity=severity, capacity_margin=margin,
            budget=budget, scenario_seed=sc_seed, K=v.K,
            init_unserved_mw=v.init_lost,
            auc25_myopic=auc_myopic, auc25_optimal=auc_opt,
            gamma_la=g_la, terminal_myopic_pct=terminal_myopic,
            n_maxflow_calls=len(v._cache),
            depth_to_50pct=v.depth_to_fraction(curve, 0.50),
            depth_to_90pct=v.depth_to_fraction(curve, 0.90),
            depth_to_99pct=v.depth_to_fraction(curve, 0.99),
            eval_seconds=round(elapsed, 3),
        )
        for k in range(1, 16):
            row[f"gamma_d{k}"] = curve.get(k) if k <= v.K else None
        rows.append(row)
        if verbose:
            print(f"  [{time.perf_counter()-t0:6.0f}s] {topo}/{severity}/m{margin} "
                  f"B={budget} seed={sc_seed} K={v.K:2d} "
                  f"gamma_LA={g_la:7.3f} d90={row['depth_to_90pct']}", flush=True)
    env.close()
    return rows


def summarise(df: pd.DataFrame, tag: str) -> pd.DataFrame:
    g = df.groupby(["topology", "severity", "capacity_margin"]).agg(
        n=("K", "size"), mean_K=("K", "mean"),
        init_unserved=("init_unserved_mw", "mean"),
        gamma_mean=("gamma_la", "mean"), gamma_max=("gamma_la", "max"),
        n_nonzero=("gamma_la", lambda s: int((s > 1e-9).sum())),
        d2_mean=("gamma_d2", "mean"), d3_mean=("gamma_d3", "mean"),
        d4_mean=("gamma_d4", "mean"), d5_mean=("gamma_d5", "mean"),
        d90_median=("depth_to_90pct", "median"),
    ).round(4)
    print(f"\n=== {tag} by condition ===")
    print(g.to_string())
    return g


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topos", default=",".join(sc.TOPOS))
    ap.add_argument("--severities", default=",".join(sc.SEVERITIES))
    ap.add_argument("--margins", default=",".join(str(m) for m in sc.MARGINS))
    ap.add_argument("--scenarios", type=int, default=12)
    ap.add_argument("--max-k", type=int, default=12)
    ap.add_argument("--budget", type=int, default=0, help="0 = uncoupled protocol")
    ap.add_argument("--tag", default="")
    ap.add_argument("--frozen", default="", help="frozen lookahead_gap_*.csv for cross-check")
    ap.add_argument("--min-k", type=int, default=0,
                    help="require K >= min_k for every instance, independent of the "
                         "protocol; use the same value for the coupled and "
                         "uncoupled runs to get a protocol-controlled comparison")
    ap.add_argument("--force", action="store_true",
                    help="allow overwriting an existing depth_curve_<tag>.csv")
    a = ap.parse_args()

    topos = [x for x in a.topos.split(",") if x]
    severities = [x for x in a.severities.split(",") if x]
    margins = [float(x) for x in a.margins.split(",") if x]

    frozen = {}
    if a.frozen:
        for p in a.frozen.split(","):
            frozen.update(sc.load_frozen_gamma(Path(p)))
        print(f"frozen Gamma_LA entries loaded: {len(frozen)}")

    rows: list[dict] = []
    t0 = time.perf_counter()
    for topo in topos:
        for severity in severities:
            for margin in margins:
                rows.extend(run_condition(topo, severity, margin, a.budget,
                                          a.scenarios, a.max_k, True, a.min_k))
                print(f"[{time.perf_counter()-t0:6.0f}s] running total {len(rows)} instances",
                      flush=True)

    df = pd.DataFrame(rows)
    outd = sc.result_dir("E1_depth_curve")
    # The default tag must depend on WHICH topologies were swept, otherwise a run
    # over a non-default topology silently overwrites the main result file under
    # the same name. (That is exactly how a third-topology run once clobbered the
    # 240-instance ieee118+ieee300 uncoupled curve.)
    default_tag = "uncoupled" if a.budget == 0 else f"coupled_B{a.budget}"
    if sorted(topos) != sorted(sc.TOPOS):
        default_tag += "_" + "+".join(topos)
    tag = a.tag or default_tag

    targets = [outd / f"depth_curve_{tag}.csv",
               outd / f"depth_curve_{tag}_by_condition.csv"]
    existing = [p.name for p in targets if p.exists()]
    if existing and not a.force:
        raise SystemExit(
            f"refusing to overwrite {existing} in {outd}. Use --tag to write "
            f"elsewhere or --force to replace.")

    # ---- validation of Gamma_K == frozen Gamma_LA -------------------------
    val = {}
    if frozen:
        keys = list(zip(df.topology, df.severity, df.capacity_margin.round(4),
                        df.scenario_seed.astype(int)))
        ref = np.array([frozen.get(k, np.nan) for k in keys])
        got = df.gamma_la.to_numpy()
        m = np.isfinite(ref)
        if m.any():
            d = np.abs(got[m] - ref[m])
            val = dict(n=int(m.sum()), max_abs_diff=float(d.max()),
                       frac_gt_1e6=float((d > 1e-6).mean()))
            print(f"\n=== VALIDATION vs frozen Gamma_LA: n={val['n']} "
                  f"max|diff|={val['max_abs_diff']:.9f} "
                  f"frac>1e-6={val['frac_gt_1e6']:.3f} ===")

    # ---- Gamma_1 exists if and only if the budget binds -------------------
    # NB: curve[1] = J(pi_1) - J(greedy) is NOT identically zero. It vanishes when
    # the greedy immediate pick happens to be the best one-step choice as well, and
    # is positive otherwise -- i.e. "one step of lookahead already beats the myopic
    # rule". That distinction is a substantive finding here, so report it rather
    # than asserting zero. The real correctness check is Gamma_K vs the frozen
    # Gamma_LA, and (for the coupled protocol) the budget-binds diagnostic below.
    g1 = df.gamma_d1.dropna()
    val["gamma_d1_max_abs"] = float(g1.abs().max()) if len(g1) else None
    val["gamma_d1_nonzero"] = int((g1.abs() > 1e-9).sum()) if len(g1) else 0
    if a.budget > 0:
        binds = int((df.K > a.budget).sum())
        val["instances_with_binding_budget"] = binds
        print(f"budget binds on {binds}/{len(df)} instances "
              f"(K > B={a.budget}); on the rest K <= B and Gamma_LA == 0 by "
              f"construction, while Gamma_1 may be non-zero")
    print(f"Gamma_1 max|value| = {val['gamma_d1_max_abs']} "
          f"({val['gamma_d1_nonzero']}/{len(g1)} instances non-zero; non-zero means "
          f"one-step lookahead already beats the myopic rule)")

    df.to_csv(outd / f"depth_curve_{tag}.csv", index=False)
    g = summarise(df, tag)
    g.to_csv(outd / f"depth_curve_{tag}_by_condition.csv")
    sc.write_json(outd / f"e1_summary_{tag}.json", dict(
        tag=tag, n_instances=int(len(df)), validation=val,
        elapsed_seconds=round(time.perf_counter() - t0, 1),
        config=dict(topos=topos, severities=severities, margins=margins,
                    budget=a.budget, max_k=a.max_k, scenarios=a.scenarios),
    ))
    print(f"\nwrote -> {outd}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
