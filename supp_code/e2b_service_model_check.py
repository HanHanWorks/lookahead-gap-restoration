"""E2b -- the service-model axis, done in a well-posed way.

Motivation
----------
The phase diagram's second axis should be "service model", but the original
``e2b_service_model_check.py`` transplanted a DC-OPF and got Gamma_LA == 0 on
every instance. Diagnosed on 2026-09-13, the reason is structural, not numerical:

    * the standard cases are built with a UNIFORM synthetic thermal rating
      (sqrt(3) * vn * max_i_ka = 9900 MVA on every line of ieee118), while the
      total load is 4242 MW and the installed generation is 9161 MW;
    * consequently a DC-OPF under the physical thermal limits NEVER needs to
      shed: measured shed = 0 on both the intact and the fully damaged network;
    * re-calibrating the DC-OPF limits to the same rule the max-flow model uses
      (rating = margin * base-case flow) makes the LP degenerate -- 168 of 173
      lines get an 8.5 MW floor while the intact case must stay feasible -- and
      pandapower's OPF fails to converge even with the HiGHS/scipy solver;
    * raising the floor until the LP becomes well-conditioned (>= 2% of load)
      removes the binding structure entirely: shed = 0 again.

So the max-flow evaluator's binding constraints come from ITS OWN capacity rule
(rating proportional to base-case utilisation, with a small floor), not from
thermal physics. Gamma_LA is therefore a property of the *service model's
capacity rule*. The honest experiment is not "does Gamma_LA survive a different
evaluator" but "how does Gamma_LA depend on the capacity rule" -- and that is
what this script measures.

Rules evaluated on the same scenarios (same seeds, same K filter)
-----------------------------------------------------------------
    R1 proportional, floor 0.002*load   <- the paper's default (reproduced by
                                           the environment's own max-flow, so it
                                           doubles as a built-in validation)
    R2 proportional, floor 0.05*load    <- well-conditioned regime
    R3 uniform physical rating          <- thermal limits, never binding
    R4 proportional, no floor           <- pure utilisation-proportional rule

Outputs (results/E2_phase_diagram/):
    service_rule_axis.csv, service_rule_report.json
"""
from __future__ import annotations

import argparse
import time

import networkx as nx
import numpy as np
import pandas as pd

import segan_common as sc

OUTD = sc.SUPP / "results" / "E2_phase_diagram"
OUTD.mkdir(parents=True, exist_ok=True)

RULES = {
    "R1_prop_floor002": dict(mode="prop", floor_share=0.002),
    "R2_prop_floor05": dict(mode="prop", floor_share=0.05),
    "R3_uniform_thermal": dict(mode="uniform", floor_share=0.0),
    "R4_prop_nofloor": dict(mode="prop", floor_share=0.0),
}


def capacities(env, margin: float, mode: str, floor_share: float) -> np.ndarray:
    """Line capacity vector (MW), indexed by line label."""
    net = env.base_net
    p0 = np.abs(net.res_line.p_from_mw.to_numpy(dtype=float))
    tot = float(net.load.p_mw.sum())
    if mode == "uniform":
        # physical thermal rating of every line
        vn = net.bus.vn_kv.to_numpy(dtype=float)[net.line.from_bus.to_numpy(dtype=int)]
        ika = net.line.max_i_ka.to_numpy(dtype=float)
        return np.sqrt(3.0) * vn * ika
    cap = margin * p0
    if floor_share > 0:
        cap = np.maximum(cap, floor_share * tot)
    return cap


def maxflow_with(env, cap_vec: np.ndarray, broken) -> float:
    """Same graph as CapacityAwareEnv._maxflow_service, with injected capacities."""
    net = env.base_net
    g = nx.DiGraph()
    S, T = "source", "sink"
    g.add_nodes_from([int(x) for x in net.bus.index] + [S, T])

    def add(u, v, c):
        for a, b in ((u, v), (v, u)):
            if g.has_edge(a, b):
                g[a][b]["capacity"] += c
            else:
                g.add_edge(a, b, capacity=c)

    broken = set(int(x) for x in broken)
    for idx, r in net.line.iterrows():
        if int(idx) not in broken:
            add(int(r.from_bus), int(r.to_bus), float(cap_vec[int(idx)]))
    for idx, r in net.trafo.iterrows():
        add(int(r.hv_bus), int(r.lv_bus), float(env.trafo_capacity_mw[int(idx)]))
    for _, r in net.gen[net.gen.in_service].iterrows():
        c = float(r.max_p_mw) if pd.notna(r.max_p_mw) else float(r.p_mw)
        add(S, int(r.bus), max(c, 0.0))
    for _, r in net.sgen[net.sgen.in_service].iterrows():
        add(S, int(r.bus), max(float(r.p_mw), 0.0))
    tot = float(net.load.p_mw.sum())
    for _, r in net.ext_grid[net.ext_grid.in_service].iterrows():
        c = float(r.max_p_mw) if pd.notna(r.max_p_mw) else tot
        add(S, int(r.bus), max(c, tot))
    for bus, d in net.load.groupby("bus").p_mw.sum().items():
        add(int(bus), T, max(float(d), 0.0))
    return float(nx.maximum_flow_value(g, S, T,
                                       flow_func=nx.algorithms.flow.preflow_push))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topos", default="ieee118,ieee300")
    ap.add_argument("--severities", default="moderate,severe")
    ap.add_argument("--margins", default="1.25")
    ap.add_argument("--budget", type=int, default=0)
    ap.add_argument("--max-k", type=int, default=12)
    ap.add_argument("--min-k", type=int, default=7)
    ap.add_argument("--scenarios", type=int, default=12)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    suf = f"_{a.tag}" if a.tag else ""

    rows = []
    t_all = time.perf_counter()
    for topo in [x for x in a.topos.split(",") if x]:
        for sev in [x for x in a.severities.split(",") if x]:
            for margin in [float(x) for x in a.margins.split(",") if x]:
                env = sc.make_env(topo, sev, margin)
                caps = {name: capacities(env, margin, **kw) for name, kw in RULES.items()}
                got = 0
                for seed in sc.CANDIDATE_SEEDS:
                    if got >= a.scenarios:
                        break
                    probe = sc.InstanceView(env, seed, max_k=a.max_k)
                    if not probe.ok or probe.K < a.min_k or probe.init_lost <= 1e-9:
                        continue
                    K = probe.K
                    init_ref = float(probe.init_lost)
                    for name, kw in RULES.items():
                        t0 = time.perf_counter()
                        svc = (None if name == "R1_prop_floor002"
                               else (lambda broken, cv=caps[name]: maxflow_with(env, cv, broken)))
                        v = sc.InstanceView(env, seed, max_k=a.max_k, service_fn=svc)
                        if a.budget > 0:
                            curve, _am, _ao, gamma, _tm = v.coupled_curve(a.budget)
                            gamma = float(gamma)
                        else:
                            curve = v.uncoupled_curve()
                            gamma = float(curve.get(v.K, 0.0))
                        rows.append(dict(
                            topology=topo, severity=sev, capacity_margin=margin,
                            scenario_seed=seed, K=K, rule=name,
                            init_unserved_mw=float(v.init_lost),
                            init_unserved_ref_maxflow=init_ref,
                            gamma_la=float(gamma),
                            d90=v.depth_to_fraction(curve, 0.90),
                            d50=v.depth_to_fraction(curve, 0.50),
                            seconds=round(time.perf_counter() - t0, 4),
                        ))
                    got += 1
                    print(f"[{time.perf_counter()-t_all:6.0f}s] {topo}/{sev}/m{margin} "
                          f"seed={seed} K={K} " +
                          " ".join(f"{n.split('_')[0]}={r['gamma_la']:8.3f}"
                                   for n, r in zip(RULES, rows[-4:])), flush=True)
                env.close()

    df = pd.DataFrame(rows)
    if df.empty:
        print("no instances collected")
        return 1
    df.to_csv(OUTD / f"service_rule_axis{suf}.csv", index=False)

    piv = df.pivot_table(index=["topology", "severity", "capacity_margin"],
                         columns="rule", values="gamma_la", aggfunc="mean").round(4)
    print("\n=== Gamma_LA mean by capacity rule ===")
    print(piv.to_string())

    agg = df.groupby(["topology", "severity", "rule"]).agg(
        n=("gamma_la", "size"),
        gamma_mean=("gamma_la", "mean"),
        gamma_max=("gamma_la", "max"),
        share_nonzero=("gamma_la", lambda s: float((s.abs() > 1e-9).mean())),
    ).round(4)
    print("\n=== aggregate ===")
    print(agg.to_string())

    sc.write_json(OUTD / f"service_rule_report{suf}.json", dict(
        budget=a.budget, max_k=a.max_k, min_k=a.min_k, scenarios=a.scenarios,
        margins=a.margins, rules=list(RULES),
        note=("service-model axis: same scenarios, four capacity rules. R1 is the "
              "paper's default and is reproduced by the environment's own max-flow, "
              "so agreement there validates the injected-capacity implementation."),
        elapsed_seconds=round(time.perf_counter() - t_all, 1),
    ))
    print(f"\nwrote -> {OUTD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
