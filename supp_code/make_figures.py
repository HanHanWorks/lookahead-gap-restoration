"""Paper figures for the supplementary experiments.

Writes PNG+PDF into $SUPP/results/summary/figs/.  Every figure is regenerated from
the CSVs, never hand-edited, so the numbers in the text and the plots cannot drift.

Usage:  python make_figures.py [--supp DIR]
"""
from __future__ import annotations

import argparse
import glob
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({
    "figure.dpi": 160, "savefig.dpi": 300, "font.size": 9,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 9.5, "axes.labelsize": 9, "legend.fontsize": 8,
    "legend.frameon": False, "font.family": "DejaVu Sans",
})
C_COMMIT = "#B45309"   # amber  – committed (static) plan
C_ROLL = "#1D4ED8"     # blue   – receding-horizon controller
C_ALT = "#6B7280"      # grey


def _gamma_cols(d: pd.DataFrame) -> list[str]:
    return sorted([c for c in d.columns if c.startswith("gamma_d")],
                  key=lambda c: int(c.split("gamma_d")[1]))


def _save(fig, out: Path, name: str) -> None:
    for ext in ("png", "pdf"):
        fig.savefig(out / f"{name}.{ext}", bbox_inches="tight")
    plt.close(fig)
    print("wrote", out / f"{name}.png")


# --------------------------------------------------------------------------- #
# Fig 1 — value of depth: committed plan vs receding-horizon controller
# --------------------------------------------------------------------------- #
def fig_depth(R: Path, out: Path) -> None:
    panels = []
    for proto, inst_f, roll_f in (
            ("With a reconnection budget (B = 6)",
             R / "E1_depth_curve" / "depth_curve_coupled_B6.csv",
             R / "E3_budget_coupled" / "rolling_depth_curve_b6.csv"),
            ("Without a reconnection budget",
             R / "E1_depth_curve" / "depth_curve_uncoupled.csv",
             R / "E3_budget_coupled" / "rolling_depth_curve_uncoupled.csv")):
        if not (inst_f.exists() and roll_f.exists()):
            print(f"[skip] {proto}")
            continue
        st = pd.read_csv(inst_f)
        g = _gamma_cols(st)
        live = st[st.gamma_la > 1e-9].copy()
        ks = np.array([int(c.split("gamma_d")[1]) for c in g])
        # committed plan: mean share of Gamma_LA recovered at depth k
        sm = (live[g].div(live.gamma_la, axis=0)).mean().values * 100

        ro = pd.read_csv(roll_f)
        ro = ro[ro.gamma_la > 1e-9]
        rm = (ro.groupby("depth").apply(
            lambda x: ((x.realized_auc - x.auc_myopic) / x.gamma_la).mean(),
            include_groups=False).sort_index() * 100)
        panels.append(dict(title=proto, ks=ks, static=sm,
                           roll_k=rm.index.values, roll_v=rm.values,
                           n=len(live), nroll=ro.scenario_seed.nunique()))

    if not panels:
        return
    fig, axes = plt.subplots(1, len(panels), figsize=(3.45 * len(panels), 2.7),
                             sharey=True)
    axes = np.atleast_1d(axes)
    for ax, p in zip(axes, panels):
        ax.plot(p["roll_k"], p["roll_v"], "o-", color=C_ROLL, lw=1.6, ms=4,
                label="receding-horizon controller")
        ax.plot(p["ks"], p["static"], "s--", color=C_COMMIT, lw=1.4, ms=3.5,
                label="committed ($k$-step) plan")
        ax.axhline(100, color=C_ALT, lw=0.8, ls=":", zorder=0)
        ax.set_title(p["title"], pad=6)
        ax.set_xlabel("lookahead depth $k$")
        ax.set_xlim(0.7, min(p["ks"].max(), 8.3))
        ax.set_ylim(-3, 108)
        ax.set_xticks(list(range(1, 9)))
        ax.legend(loc="lower right")
    axes[0].set_ylabel(r"share of $\Gamma_{\mathrm{LA}}$ recovered  [%]")
    fig.tight_layout()
    _save(fig, out, "fig1_value_of_depth")


# --------------------------------------------------------------------------- #
# Fig 2 — Gamma_LA by condition, both protocols
# --------------------------------------------------------------------------- #
def fig_gap(R: Path, out: Path) -> None:
    parts = []
    for proto, f in (("uncoupled", "depth_curve_uncoupled_by_condition.csv"),
                     ("B = 6", "depth_curve_coupled_B6_by_condition.csv")):
        p = R / "E1_depth_curve" / f
        if p.exists():
            d = pd.read_csv(p)
            d["proto"] = proto
            parts.append(d)
    if not parts:
        return
    d = pd.concat(parts, ignore_index=True)
    d["cond"] = d.topology.str.replace("ieee", "") + "/" + d.severity.str[:3] + \
                "/m" + d.capacity_margin.astype(str)
    order = sorted(d.cond.unique())
    fig, ax = plt.subplots(figsize=(7.0, 2.8))
    w = 0.38
    for i, (proto, col) in enumerate((("uncoupled", C_ALT), ("B = 6", C_ROLL))):
        s = d[d.proto == proto].set_index("cond").reindex(order)
        x = np.arange(len(order)) + (i - 0.5) * w
        ax.bar(x, s.gamma_mean.values, width=w, color=col, label=proto)
        ax.plot(x, s.gamma_max.values, "k_", ms=9, mew=1.3,
                label="max over instances" if i == 0 else None)
    ax.set_xticks(np.arange(len(order)))
    ax.set_xticklabels(order, rotation=65, ha="right", fontsize=7.5)
    ax.set_ylabel(r"$\Gamma_{\mathrm{LA}}$  [AUC@25 units]")
    ax.legend(ncol=3, loc="upper left")
    fig.tight_layout()
    _save(fig, out, "fig2_gamma_la_by_condition")


# --------------------------------------------------------------------------- #
# Fig 3 — head-to-head
# --------------------------------------------------------------------------- #
def fig_headtohead(R: Path, out: Path) -> None:
    parts = sorted(glob.glob(str(R / "E3_budget_coupled" / "episodes__*.csv")))
    if not parts:
        return
    e = pd.concat([pd.read_csv(p).assign(
        cond=Path(p).name.split("__", 1)[1].replace(".csv", "")) for p in parts],
        ignore_index=True)
    order = ["Lookahead-2", "Lookahead-3", "One-Step Exact Maxflow",
             "Electrical-priority", "Risk-only", "DQN+validity-screen",
             "DQN-true+validity-screen", "DQN", "DQN-true", "Random"]
    order = [m for m in order if m in set(e.method)]
    m = e.groupby("method").auc25_recomputed.mean().reindex(order)
    sem = e.groupby("method").auc25_recomputed.sem().reindex(order)
    learn = {"DQN", "DQN+validity-screen", "DQN-true", "DQN-true+validity-screen"}
    cols = [C_ALT if x in learn else C_ROLL for x in order]
    cols[0] = "#111827"
    fig, ax = plt.subplots(figsize=(5.0, 2.9))
    y = np.arange(len(order))[::-1]
    ax.barh(y, m.values, xerr=sem.values, color=cols, height=0.68,
            error_kw=dict(ecolor="#374151", lw=0.8, capsize=2))
    ax.set_yticks(y)
    ax.set_yticklabels([x.replace("+validity-screen", "\n+ validity screen") for x in order],
                       fontsize=7.5)
    ax.set_xlabel("AUC@25  [mean $\\pm$ s.e.m. over all conditions]")
    ax.set_xlim(0, m.max() * 1.16)
    for yy, v in zip(y, m.values):
        ax.text(v + m.max() * 0.015, yy, f"{v:.0f}", va="center", fontsize=7)
    fig.tight_layout()
    _save(fig, out, "fig3_head_to_head")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--supp", default=str(Path(__file__).resolve().parents[1]))
    a = ap.parse_args()
    S = Path(a.supp).expanduser()
    R = S / "results"
    out = R / "summary" / "figs"
    out.mkdir(parents=True, exist_ok=True)
    fig_depth(R, out)
    fig_gap(R, out)
    fig_headtohead(R, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
