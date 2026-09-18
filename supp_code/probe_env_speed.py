"""Diagnostic: step throughput of the budget-coupled environments vs the originals."""
from __future__ import annotations

import time

import numpy as np

import segan_common as sc
from budget_coupled import make_budget_env


def time_env(env, n_steps=2000, label=""):
    obs, _ = env.reset(seed=4000)
    t0 = time.perf_counter()
    steps = 0
    while steps < n_steps:
        a = int(env.action_space.sample())
        obs, _, term, trunc, _ = env.step(a)
        steps += 1
        if term or trunc:
            obs, _ = env.reset(seed=4000 + steps)
    dt = time.perf_counter() - t0
    print(f"{label:34s} {steps} steps in {dt:7.2f}s  -> {steps/dt:8.1f} steps/s")
    return steps / dt


env = sc.make_env("ieee118", "severe", 1.25, training=True)
time_env(env, 2000, "original surrogate (uncoupled)")
env.close()

env = make_budget_env("ieee118", "severe", 1.25, budget=6, training=True)
print("  obs_space:", env.observation_space.shape, "action:", env.action_space.n)
time_env(env, 2000, "budget-coupled surrogate B=6")
env.close()

env = sc.make_env("ieee118", "severe", 1.25, training=False)
time_env(env, 300, "original capacity-aware (uncoupled)")
env.close()

env = make_budget_env("ieee118", "severe", 1.25, budget=6, training=False)
time_env(env, 300, "budget-coupled capacity-aware B=6")
env.close()
