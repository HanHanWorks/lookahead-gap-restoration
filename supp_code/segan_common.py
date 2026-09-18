"""Shared utilities for the SEGAN supplementary experiments (2026-09-13).

Layout-independent: the project root is discovered by walking upwards until a
directory containing ``IJEPES_major_revision_2026-09-07`` is found, so the same
file runs from the local mac tree and from ``$REMOTE_HOME/segan``.

Reused primitives (import only, never modified):
    algorithm/enhanced_recovery_env.py
    IJEPES_*/code/run_capacity_aware_restoration.py
"""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import numpy as np

REV_DIRNAME = "IJEPES_major_revision_2026-09-07"

# severity -> (min key lines broken, max key lines broken, other-lines ratio)
SEV_CFG = {"moderate": (3, 10, 0.03), "severe": (8, 15, 0.08)}
TOPOS = ["ieee118", "ieee300"]
SEVERITIES = ["moderate", "severe"]
MARGINS = [1.15, 1.25, 1.50]
FLOOR_SHARE = 0.002
N_ACTIONS = 20
TRAIN_SEEDS = [42, 43, 44]
HORIZON = 25
EVAL_SEEDS = [4000 + 17 * i for i in range(50)]
CANDIDATE_SEEDS = [4000 + 17 * i for i in range(60)]


def project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / REV_DIRNAME).is_dir():
            return parent
    raise RuntimeError(f"could not locate {REV_DIRNAME} above {here}")


ROOT = project_root()
REV = ROOT / REV_DIRNAME
CORECODE = REV / "code"
ACTION_SETS = REV / "data_derived" / "action_sets"
TOPOLOGY_DIR = REV / "external_data" / "benchmark_topologies"
CLIMATE = ROOT / "raw_data" / "climate" / "SouthWest_Core400_KarstClimate_2024_Copernicus.csv"
SUPP = ROOT / "SEGAN_SUPP_2026-09-13"

import sys  # noqa: E402

if str(CORECODE) not in sys.path:
    sys.path.insert(0, str(CORECODE))

from run_capacity_aware_restoration import (  # noqa: E402
    CapacityAwareEnv,
    CriticalityTrainingEnv,
    ElectricalPriority,
    ExactMaxflow,
    RiskOnly,
    ValidityScreenedDQN,
)


def topology_path(topo: str) -> Path:
    return TOPOLOGY_DIR / f"{topo}.json"


def action_set_path(topo: str) -> Path:
    return ACTION_SETS / f"{topo}_key_lines.csv"


def make_env(topo: str, severity: str = "severe", margin: float = 1.25,
             floor_share: float = FLOOR_SHARE, training: bool = False,
             n_actions: int = N_ACTIONS, **extra):
    """Mirror of run_segan_experiments.make_env_v2 (B1/B2/B3 protocol)."""
    lo, hi, ratio = SEV_CFG[severity]
    cls = CriticalityTrainingEnv if training else CapacityAwareEnv
    kw = dict(
        grid_json_path=str(topology_path(topo)),
        climate_csv_path=str(CLIMATE),
        use_microtopography=False,
        use_topology_features=True,
        n_switch_actions=n_actions,
        disaster_min_key_broken=lo,
        disaster_max_key_broken=hi,
        disaster_other_lines_ratio=ratio,
        disable_print=True,
        key_lines_path=str(action_set_path(topo)),
        disaster_rng="env",
    )
    if not training:
        kw.update(capacity_margin=margin, capacity_floor_share=floor_share)
    kw.update(extra)
    return cls(**kw)


def result_dir(name: str) -> Path:
    """results/<name>/ under the unified supplementary folder (created on demand)."""
    d = SUPP / "results" / name
    d.mkdir(parents=True, exist_ok=True)
    return d


class InstanceView:
    """One reset scenario as an exactly-evaluable set-scheduling problem.

        lost(S) = max(0, base_service - maxflow(all_broken \\ S))

    depends only on the SET S of reconnected key lines, so the full-horizon
    optimum is a DP over subsets of the broken key lines (Proposition 2).
    """

    def __init__(self, env, scenario: int, max_k: int | None = None,
                 service_fn=None):
        np.random.seed(scenario)
        env.action_space.seed(scenario)
        env.reset(seed=scenario)
        self.env = env
        self.scenario = scenario
        self.all_broken = set(int(x) for x in env.broken_lines)
        self.keys = [int(li) for li in env.key_lines if int(li) in self.all_broken]
        self.K = len(self.keys)
        # service functional: default = the environment's exact max-flow model;
        # a callable may be injected to swap in a different evaluator (e.g. DC-OPF)
        self.service = service_fn if service_fn is not None else env._maxflow_service
        self.base_service = float(self.service(set()))
        self.base_broken = frozenset(self.all_broken)
        self.full = (1 << self.K) - 1
        self._cache: dict[frozenset, float] = {}
        self._tail_memo: dict[int, float] = {}
        self.init_lost = self.lost(self.base_broken)
        self.ok = max_k is None or self.K <= max_k

    # ---------------- service functional -----------------------------------
    def lost(self, broken_fs: frozenset) -> float:
        if broken_fs not in self._cache:
            self._cache[broken_fs] = max(0.0, self.base_service - self.service(set(broken_fs)))
        return self._cache[broken_fs]

    def rec(self, mask: int) -> float:
        """Recovery % after reconnecting the key lines in ``mask``."""
        if self.init_lost <= 1e-9:
            return 0.0
        reconnected = frozenset(self.keys[i] for i in range(self.K) if mask >> i & 1)
        cur = self.lost(self.base_broken - reconnected)
        return float(np.clip((self.init_lost - cur) / self.init_lost * 100.0, 0.0, 100.0))

    @staticmethod
    def popcount(mask: int) -> int:
        return bin(mask).count("1")

    def nxt(self, mask: int):
        return [mask | 1 << i for i in range(self.K) if not mask >> i & 1]

    def masks_by_size(self, sizes):
        out = []
        for size in sizes:
            for combo in combinations(range(self.K), size):
                m = 0
                for i in combo:
                    m |= 1 << i
                out.append(m)
        return out

    # ---------------- uncoupled policies -----------------------------------
    def myopic_sum(self) -> float:
        mask, total = 0, 0.0
        for _ in range(self.K):
            cands = self.nxt(mask)
            if not cands:
                break
            best = max(cands, key=self.rec)
            total += self.rec(best)
            mask = best
        return total

    def exact_sum(self) -> float:
        f = {self.full: 0.0}
        for mask in range(self.full - 1, -1, -1):
            f[mask] = max(self.rec(m) + f[m] for m in self.nxt(mask))
        return f[0]

    def greedy_tail(self, mask: int) -> float:
        """Sum of r along the myopic completion from ``mask`` (memoised)."""
        if mask in self._tail_memo:
            return self._tail_memo[mask]
        cands = self.nxt(mask)
        if not cands:
            self._tail_memo[mask] = 0.0
            return 0.0
        best = max(cands, key=self.rec)
        val = self.rec(best) + self.greedy_tail(best)
        self._tail_memo[mask] = val
        return val

    def uncoupled_curve(self, max_depth: int | None = None) -> dict[int, float]:
        """Gamma_k = J(pi_k) - J(pi_1), k = 1..K.  Gamma_1 = 0, Gamma_K = Gamma_LA.

        The order-invariant trapezoid tail (Lemma 1) cancels in the difference,
        so only sum_{t<=m} r(S_t) needs to be tracked.
        """
        if self.K == 0:
            return {1: 0.0}
        max_depth = self.K if max_depth is None else min(max_depth, self.K)
        f_prev = [self.greedy_tail(m) for m in range(self.full + 1)]
        base = f_prev[0]
        curve = {1: 0.0}
        for d in range(1, max_depth + 1):
            f_new = [0.0] * (self.full + 1)
            for mask in range(self.full - 1, -1, -1):
                best = -np.inf
                for m in self.nxt(mask):
                    val = self.rec(m) + f_prev[m]
                    if val > best:
                        best = val
                f_new[mask] = best
            curve[d] = f_new[0] - base
            f_prev = f_new
        return curve

    # ---------------- budget-coupled policies (Corollary 4b) ---------------
    def _greedy_budget_value(self, mask: int, B: int) -> float:
        """Greedy completion with terminal accounting:
        sum_{t} r(S_t) for the remaining reconnections + (24.5 - B) * r(S_B).
        """
        total, cur, last = 0.0, mask, self.rec(mask)
        done = self.popcount(mask)
        while done < B:
            cands = self.nxt(cur)
            if not cands:
                break
            best = max(cands, key=self.rec)
            last = self.rec(best)
            total += last
            cur = best
            done += 1
        return total + (24.5 - B) * last

    def coupled_curve(self, budget: int, max_depth: int | None = None):
        """Depth curves under a reconnection budget B.

        Returns (curve, auc_myopic, auc_opt, gamma_la_coupled, terminal_myopic_pct).
        curve[1] == 0, curve[B] == gamma_la_coupled.
        """
        K = self.K
        B = min(int(budget), K)
        if K == 0:
            return {1: 0.0}, 0.0, 0.0, 0.0, 0.0
        max_depth = B if max_depth is None else min(max_depth, B)
        tail_const = 24.5 - B

        states = self.masks_by_size(range(0, B + 1))
        # f_0 = greedy completion value (the myopic policy under the budget)
        f_prev = {m: self._greedy_budget_value(m, B) for m in states}
        base = f_prev[0]

        curve = {1: 0.0}
        for d in range(1, max_depth + 1):
            f_new = {}
            for mask in states:
                if self.popcount(mask) >= B:
                    f_new[mask] = tail_const * self.rec(mask)
                    continue
                best = -np.inf
                for m in self.nxt(mask):
                    val = self.rec(m) + f_prev[m]
                    if val > best:
                        best = val
                f_new[mask] = best
            curve[d] = f_new[0] - base
            f_prev = f_new

        # myopic / optimal terminal sets for reporting
        def myopic_terminal():
            cur, last = 0, self.rec(0)
            for _ in range(B):
                cands = self.nxt(cur)
                if not cands:
                    break
                best = max(cands, key=self.rec)
                last = self.rec(best)
                cur = best
            return last

        auc_myopic = base
        # exact optimum: same DP but with the exact terminal at |S| = B
        exact = {}
        for mask in states:
            if self.popcount(mask) == B:
                exact[mask] = tail_const * self.rec(mask)
        for size in range(B - 1, -1, -1):
            for mask in states:
                if self.popcount(mask) != size:
                    continue
                exact[mask] = max(self.rec(m) + exact[m] for m in self.nxt(mask))
        auc_opt = exact[0]
        return curve, auc_myopic, auc_opt, auc_opt - auc_myopic, myopic_terminal()

    def depth_to_fraction(self, curve: dict[int, float], frac: float):
        total = curve.get(max(curve), 0.0)
        if total <= 1e-9:
            return None
        for k in sorted(curve):
            if curve[k] >= frac * total - 1e-12:
                return k
        return None


def write_json(path: Path, obj) -> None:
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=float),
                          encoding="utf-8")


def load_frozen_gamma(path) -> dict:
    """(topology, severity, margin, scenario_seed) -> gamma_la from a frozen CSV."""
    import pandas as pd
    p = Path(path)
    if not p.exists():
        return {}
    df = pd.read_csv(p)
    out = {}
    for r in df.itertuples():
        key = (r.topology, r.severity, round(float(r.capacity_margin), 4),
               int(r.scenario_seed))
        out[key] = float(r.gamma_la)
    return out
