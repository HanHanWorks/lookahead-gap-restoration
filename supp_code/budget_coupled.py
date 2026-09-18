"""E3 -- budget-coupled restoration environment and depth-limited lookahead agents.

Corollary 4(b): when only B < m reconnections are admissible inside the horizon,
    J = sum_{t<=B} r(S_t) + (24.5 - B) * r(S_B)
and r(S_B) is no longer order-invariant, so the one-step exact rule stops being
optimal. This module adds that resource coupling to the *environment* (so a
learner can be trained in it) and adds an online depth-k lookahead agent that
buys lookahead at O(K^k) exact service evaluations per decision.

Nothing here modifies the existing environment or policy classes; the budget is
implemented as a mixin applied to the two environment classes already in use.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np
from gymnasium import spaces

import segan_common as sc

CapacityAwareEnv = sc.CapacityAwareEnv
CriticalityTrainingEnv = sc.CriticalityTrainingEnv


class BudgetMixin:
    """Cardinality-coupled reconnection: at most ``reconnection_budget`` effective
    reconnections per episode; later attempts are turned into no-ops.

    The augmented observation appends the remaining budget (scaled to [-1, 1])
    so the learner can condition on how much restoration capacity is left.
    """

    def _budget_init(self, reconnection_budget: int) -> None:
        self.reconnection_budget = int(reconnection_budget)
        self.reconnections_used = 0
        base_dim = int(self.observation_space.shape[0])
        self.observation_space = spaces.Box(
            low=-1.0, high=1.0, shape=(base_dim + 1,), dtype=np.float32)

    def _budget_augment(self, obs):
        left = 1.0 - self.reconnections_used / max(1, self.reconnection_budget)
        return np.concatenate([
            np.asarray(obs, dtype=np.float32),
            np.asarray([2.0 * left - 1.0], dtype=np.float32),
        ])

    def reset(self, seed=None, options=None):
        obs, info = super().reset(seed=seed, options=options)
        self.reconnections_used = 0
        info["reconnection_budget"] = self.reconnection_budget
        return self._budget_augment(obs), info

    def step(self, action):
        action = int(action)
        if action < self.n_switch_actions and self.key_lines[action] in self.broken_lines:
            if self.reconnections_used >= self.reconnection_budget:
                action = self.n_switch_actions          # budget exhausted -> no-op
            else:
                self.reconnections_used += 1
        obs, reward, term, trunc, info = super().step(action)
        info["reconnections_used"] = self.reconnections_used
        info["reconnection_budget"] = self.reconnection_budget
        info["budget_exhausted"] = self.reconnections_used >= self.reconnection_budget
        return self._budget_augment(obs), reward, term, trunc, info


class BudgetCoupledEnv(BudgetMixin, CapacityAwareEnv):
    """Capacity-aware (true objective) environment with a reconnection budget."""

    def __init__(self, *args, reconnection_budget: int = 6, **kwargs):
        super().__init__(*args, **kwargs)
        self._budget_init(reconnection_budget)


class BudgetCoupledCriticalityEnv(BudgetMixin, CriticalityTrainingEnv):
    """Criticality surrogate training environment with a reconnection budget."""

    def __init__(self, *args, reconnection_budget: int = 6, **kwargs):
        super().__init__(*args, **kwargs)
        self._budget_init(reconnection_budget)


def make_budget_env(topo: str, severity: str = "severe", margin: float = 1.25,
                    budget: int = 6, training: bool = False, **extra):
    """Training env = surrogate (criticality) or true-objective, both budget-coupled."""
    lo, hi, ratio = sc.SEV_CFG[severity]
    cls = BudgetCoupledCriticalityEnv if training else BudgetCoupledEnv
    kw = dict(
        grid_json_path=str(sc.topology_path(topo)),
        climate_csv_path=str(sc.CLIMATE),
        use_microtopography=False,
        use_topology_features=True,
        n_switch_actions=sc.N_ACTIONS,
        disaster_min_key_broken=lo,
        disaster_max_key_broken=hi,
        disaster_other_lines_ratio=ratio,
        disable_print=True,
        key_lines_path=str(sc.action_set_path(topo)),
        disaster_rng="env",
        reconnection_budget=budget,
    )
    if not training:
        kw.update(capacity_margin=margin, capacity_floor_share=sc.FLOOR_SHARE)
    kw.update(extra)
    return cls(**kw)


class LookaheadKAgent:
    """Online depth-k lookahead with a myopic tail, using the exact service model.

    Bottom-up value iteration over subsets of the currently broken key lines, so
    the number of states is C(K, <=d) rather than a naive K^d recursion:

        V(S) = greedy completion value            if |S| = d  (depth exhausted)
        V(S) = max_b [ r(S u b) + V(S u b) ]      otherwise
        first action = argmax_b [ r({b}) + V({b}) ]

    where the greedy completion *includes* the budget tail term
    (24.5 - B) * r(S_B), so the agent optimises the true AUC@25 objective.
    k = 1 reproduces the one-step exact rule; k = B reproduces the exact optimum.

    Cost per decision: C(K, <=k) states x K transitions exact service evaluations.
    """

    def __init__(self, env, depth: int = 2, uncoupled: bool = False):
        self.env = env
        self.depth = int(depth)
        # In the uncoupled protocol every broken key line will be reconnected
        # inside the horizon, the trapezoid tail is order-invariant (Lemma 1) and
        # therefore cancels: maximise sum_{t} r(S_t) with no terminal term.
        self.uncoupled = bool(uncoupled)
        self._rec_cache: dict[frozenset, float] = {}

    # ---- exact service model ---------------------------------------------
    def _r(self, broken_all: frozenset) -> float:
        """Recovery %% for a full broken-line set (keys and non-keys)."""
        if broken_all in self._rec_cache:
            return self._rec_cache[broken_all]
        env = self.env
        saved = env.broken_lines
        env.broken_lines = set(broken_all)
        val = float(env._calculate_lost_load())
        env.broken_lines = saved
        init = float(getattr(env, "initial_lost_load", 0.0))
        out = 0.0 if init <= 1e-9 else float(
            np.clip((init - val) / init * 100.0, 0.0, 100.0))
        self._rec_cache[broken_all] = out
        return out

    def predict(self, obs, deterministic=True):
        env = self.env
        base = frozenset(int(x) for x in env.broken_lines)
        avail = [li for li in env.key_lines if li in env.broken_lines]
        if not avail:
            return env.n_switch_actions, None
        if self.uncoupled:
            left = len(avail)          # every broken key line is reachable
            tail_coef = 0.0
        else:
            B = int(getattr(env, "reconnection_budget", 0))
            used = int(getattr(env, "reconnections_used", 0))
            # The trapezoid tail is weighted by how many effective reconnections
            # ACTUALLY happen, which is min(B, K) -- not B. When K < B the budget
            # never binds: every broken key line gets restored, the state freezes
            # there, and the tail coefficient is (24.5 - K). Using (24.5 - B)
            # mis-specifies the objective (it under-weights the terminal state), so
            # the rollout picks a worse order and can lose to the plain myopic rule
            # even though the myopic path is one of its own candidates.
            # This mirrors coupled_curve(), which sets B = min(budget, K) internally.
            n_eff = min(B, used + len(avail))
            left = n_eff - used
            if left <= 0:
                return env.n_switch_actions, None
            tail_coef = 24.5 - n_eff
        d = min(self.depth, left)

        def r_of(S: frozenset) -> float:
            return self._r(frozenset(base - S))

        tail_memo: dict = {}

        def greedy_complete(S: frozenset, steps: int) -> float:
            key = (S, steps)
            if key in tail_memo:
                return tail_memo[key]
            total, cur = 0.0, S
            for _ in range(steps):
                cands = [li for li in avail if li not in cur]
                if not cands:
                    break
                best = max(cands, key=lambda li: r_of(cur | {li}))
                cur = cur | {best}
                total += r_of(cur)
            total += tail_coef * r_of(cur)
            tail_memo[key] = total
            return total

        states: dict[frozenset, float] = {}
        for size in range(d, -1, -1):
            for combo in combinations(avail, size):
                S = frozenset(combo)
                if size == d:
                    states[S] = greedy_complete(S, left - size)
                    continue
                best = -np.inf
                for li in avail:
                    if li in S:
                        continue
                    ns = S | {li}
                    val = r_of(ns) + states[ns]
                    if val > best:
                        best = val
                states[S] = best

        best_a, best_v = env.n_switch_actions, -np.inf
        for a, li in enumerate(env.key_lines):
            if li not in base:
                continue
            S = frozenset([li])
            val = r_of(S) + states[S]
            if val > best_v:
                best_v, best_a = val, a
        return int(best_a), None
