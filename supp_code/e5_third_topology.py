"""E5 -- third benchmark topology: generality of the identifiability / Gamma_LA result.

Adds one more independently sourced pandapower benchmark to the study (the paper's
two-case basis is a reviewer target). Two steps:

  1. write external_data/benchmark_topologies/{case}.json
  2. build data_derived/action_sets/{case}_key_lines.csv with the same electrical
     construction used for ieee118/ieee300: the twenty lines whose single-line
     outage costs the most served load under the nominal capacity model
     (margin 1.15, floor share 0.002), which keeps the construction non-circular.

After this runs, the new case can be passed to e1_depth_curve.py / e2_phase_diagram.py
via --topos {case}. No retraining is needed for the Gamma_LA generality claim,
because Gamma_LA is a property of the topology and the service model, not of any
learner.

Outputs: topology JSON + action set CSV + results/E5_third_topo/e5_report.json
"""
from __future__ import annotations

import argparse
import csv
import json

import numpy as np
import pandapower as pp
import pandapower.networks as nw

import segan_common as sc

OUTD = sc.SUPP / "results" / "E5_third_topo"
OUTD.mkdir(parents=True, exist_ok=True)

NOMINAL_MARGIN = 1.15
NOMINAL_FLOOR = 0.002
N_ACTIONS = 20

CANDIDATES = {
    "case_illinois200": nw.case_illinois200,
    "case145": nw.case145,
    "case89pegase": nw.case89pegase,
    "case57": nw.case57,
    "case24_ieee_rts": lambda: nw.case24_ieee_rts(),
    "case39": nw.case39,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default="case_illinois200",
                    help="pandapower networks case name, or a key of CANDIDATES")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    if a.list:
        available = [n for n in dir(nw) if n.startswith("case")]
        print("pandapower cases:", ", ".join(sorted(available)))
        return 0

    name = a.case
    if name in CANDIDATES:
        net = CANDIDATES[name]()
    else:
        builder = getattr(nw, name, None)
        if builder is None:
            raise SystemExit(f"unknown pandapower case: {name}")
        net = builder()

    sc.TOPOLOGY_DIR.mkdir(parents=True, exist_ok=True)
    topo_json = sc.TOPOLOGY_DIR / f"{name}.json"
    pp.to_json(net, str(topo_json))
    print(f"wrote topology -> {topo_json}  "
          f"(bus={len(net.bus)} line={len(net.line)} load={len(net.load)} "
          f"gen={len(net.gen)} sgen={len(net.sgen)} trafo={len(net.trafo)})")

    # ---- action set artifact (same electrical construction as the other cases)
    from run_capacity_aware_restoration import CapacityAwareEnv  # noqa: PLC0415
    env = CapacityAwareEnv(
        grid_json_path=str(topo_json),
        climate_csv_path=str(sc.CLIMATE),
        use_microtopography=False, use_topology_features=True,
        n_switch_actions=N_ACTIONS,
        disaster_min_key_broken=3, disaster_max_key_broken=10,
        disaster_other_lines_ratio=0.03, disable_print=True,
        capacity_margin=NOMINAL_MARGIN, capacity_floor_share=NOMINAL_FLOOR)
    base_net = env.base_net
    pp.rundcpp(base_net, check_connectivity=True)
    flow = np.abs(base_net.res_line.p_from_mw.to_numpy(dtype=float))
    base = float(env.base_service_mw)
    total_load = float(base_net.load.p_mw.sum())
    cap = env.line_capacity_mw
    floor = NOMINAL_FLOOR * total_load

    loss = [(i, base - env._maxflow_service({i})) for i in range(env.n_lines)]
    loss.sort(key=lambda x: x[1], reverse=True)
    chosen = [i for i, _ in loss[:N_ACTIONS]]

    sc.ACTION_SETS.mkdir(parents=True, exist_ok=True)
    out_csv = sc.ACTION_SETS / f"{name}_key_lines.csv"
    rows = []
    for rank, (i, l) in enumerate(loss[:N_ACTIONS], start=1):
        r = base_net.line.loc[i]
        rows.append(dict(
            rank=rank, line_index=int(i),
            from_bus=int(r.from_bus), to_bus=int(r.to_bus),
            base_flow_mw=round(float(flow[i]), 6),
            capacity_mw=round(float(cap[i]), 6),
            on_capacity_floor=bool(abs(cap[i] - floor) < 1e-9),
            single_outage_loss_mw=round(float(l), 6)))
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    all_out = float(base - env._maxflow_service(set(chosen)))
    report = dict(
        case=name, topology_json=str(topo_json), action_set_csv=str(out_csv),
        n_bus=int(len(base_net.bus)), n_lines=int(env.n_lines),
        total_load_mw=total_load, base_service_mw=base,
        action_set_flow_share=float(flow[chosen].sum() / flow.sum()),
        n_on_capacity_floor=int(sum(1 for i in chosen
                                    if abs(cap[i] - floor) < 1e-9)),
        lost_if_all_actions_out_mw=all_out,
        lost_if_all_actions_out_share_of_load=float(all_out / total_load),
        top_single_outage_loss_mw=float(loss[0][1]),
        twentieth_single_outage_loss_mw=float(loss[N_ACTIONS - 1][1]),
        nominal_margin=NOMINAL_MARGIN, nominal_floor_share=NOMINAL_FLOOR,
    )
    env.close()
    sc.write_json(OUTD / f"e5_report_{name}.json", report)
    print(json.dumps(report, indent=2))
    print(f"\nNow run:  python e1_depth_curve.py --topos {name} ...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
