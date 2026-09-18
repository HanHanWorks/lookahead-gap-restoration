"""A DC-OPF served-load evaluator, used as the second axis of the E2 phase diagram.

The default service functional in these experiments is a maximum-flow construct
on synthetic capacities (exactly evaluable, cheap). This module provides an
alternative: the served load obtained from a DC optimal-power-flow redispatch in
which each load bus may shed its demand at a high penalty. It is therefore an
*exactly evaluable but far more expensive* evaluator -- which is the axis the
phase diagram needs (evaluability/cost), not an inexact one.

Served load = total demand - sum(shedding dispatch).

Implementation notes
--------------------
* A fresh network copy is built for every evaluation, so results are independent.
* All loads are modelled as fixed; a controllable generator with max_p = local
  demand and a high linear cost is added at each load bus as the shedding device.
* Results are memoised on the (frozen) set of out-of-service lines.
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandapower as pp

SHED_COST = 1.0e3     # EUR/MW -- high, so shedding is the last resort


class DCOPFService:
    def __init__(self, net_json: Path, cache_limit: int = 200_000):
        self.path = Path(net_json)
        base = pp.from_json(str(self.path))
        self.total_load = float(base.load.p_mw.sum())
        self.load_by_bus = {int(b): float(p)
                            for b, p in base.load.groupby("bus").p_mw.sum().items()}
        self.n_lines = int(len(base.line))
        self._cache: dict[frozenset, float] = {}
        self.cache_limit = cache_limit
        self.n_solves = 0
        self.n_failed = 0
        self.total_solve_ms = 0.0

    def __call__(self, broken_lines) -> float:
        key = frozenset(int(x) for x in broken_lines)
        if key in self._cache:
            return self._cache[key]
        val = self._solve(key)
        if len(self._cache) >= self.cache_limit:
            self._cache.clear()
        self._cache[key] = val
        return val

    # ------------------------------------------------------------------
    def _solve(self, broken: frozenset) -> float:
        net = pp.from_json(str(self.path))
        if broken:
            idx = [i for i in broken if 0 <= int(i) < self.n_lines]
            if idx:
                net.line.loc[idx, "in_service"] = False
        # shed-capable generators at every load bus
        shed_idx = []
        for bus, p in self.load_by_bus.items():
            if p <= 0:
                continue
            gi = pp.create_gen(net, bus=bus, p_mw=0.0, min_p_mw=0.0,
                               max_p_mw=float(p), vm_pu=1.0, controllable=True)
            pp.create_poly_cost(net, gi, "gen", cp1_eur_per_mw=SHED_COST)
            shed_idx.append(gi)
        # make the existing dispatchable units free (the objective is to serve load)
        for gi in net.gen.index:
            if gi in shed_idx:
                continue
            net.poly_cost.loc[net.poly_cost.element == gi, "cp1_eur_per_mw"] = 0.0
        t0 = time.perf_counter()
        try:
            pp.rundcopp(net, check_connectivity=True, verbose=False, numba=False)
            shed = float(net.res_gen.loc[shed_idx, "p_mw"].sum()) if shed_idx else 0.0
            served = max(0.0, self.total_load - shed)
            self.n_solves += 1
        except Exception:
            self.n_failed += 1
            served = 0.0
        finally:
            self.total_solve_ms += (time.perf_counter() - t0) * 1000.0
        return float(np.clip(served, 0.0, self.total_load))

    def stats(self) -> dict:
        return dict(n_solves=self.n_solves, n_failed=self.n_failed,
                    mean_solve_ms=(self.total_solve_ms / self.n_solves
                                   if self.n_solves else None),
                    total_solve_ms=round(self.total_solve_ms, 1))
