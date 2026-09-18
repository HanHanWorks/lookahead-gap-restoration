"""Figure set for the SEGAN submission.

One script generates every figure of the manuscript, so that a caption and the
data behind it cannot drift apart.  `figures/MANIFEST.txt` records the input
files of each figure.

Sources
-------
supp_results_2026-09-13/   supplementary batch (E1--E5 and E2b)
experiment_data/          primary batch (attribution, timing, protocol artifacts)

Outputs  figures/figN_*.pdf  and  figures/figN_*.png

Usage:  python make_figures_submission.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch, Rectangle

HERE = Path(__file__).resolve().parent          # .../SEGAN_submission_2026-09/supp_code
WORK = HERE.parent                              # .../SEGAN_submission_2026-09
SUPP = WORK / "supp_results_2026-09-13"
EXP = WORK / "experiment_data"
FIG = WORK / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- #
# Style: one visual language for the whole set
# --------------------------------------------------------------------------- #
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 12.8,
    "axes.labelsize": 12.8,
    "axes.titlesize": 13.6,
    "xtick.labelsize": 12.0,
    "ytick.labelsize": 12.0,
    "legend.fontsize": 12.0,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.7,
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "axes.grid": True,
    "grid.alpha": 0.22,
    "grid.linewidth": 0.5,
    "legend.frameon": True,
    "legend.framealpha": 0.90,
    "legend.edgecolor": "none",
    "legend.borderpad": 0.3,
    "figure.dpi": 200,
    "savefig.dpi": 400,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

# Okabe-Ito, colour-blind safe
CB = {"blue": "#0072B2", "orange": "#E69F00", "green": "#009E73",
      "vermillion": "#D55E00", "purple": "#CC79A7", "sky": "#56B4E9",
      "yellow": "#F0E442", "grey": "#9A9A9A", "dark": "#2B2B2B"}
UNCOUPLED, BUDGET = CB["grey"], CB["blue"]
COMMITTED, ROLLING = CB["orange"], CB["blue"]
MCOL = {"Electrical-priority": CB["green"], "Risk-only": CB["sky"],
        "DQN": "#7F7F7F", "DQN+validity-screen": CB["orange"],
        "DQN-true": "#8C6D00", "DQN-true+validity-screen": CB["vermillion"],
        "Lookahead-1": CB["purple"], "Lookahead-2": CB["blue"],
        "Lookahead-3": "#00405F", "One-Step Exact Maxflow": CB["dark"]}
# Policy names are written once here and reused by every figure and by the tables of
# the manuscript, so that a reader can match a figure label to a row of Table 3, 7 or 9
# without a lookup.  The screen axis (Figures 2 and 7) and the timing-boundary axis
# (Figure 9) share CSV method keys but name different things, so Figure 9 overrides the
# one learned entry whose name depends on the axis, in MLAB9 below.
MLAB = {"DQN": "Learned ranker", "DQN+validity-screen": "Learned ranker, screened",
        "DQN-true": "True-objective ranker",
        "DQN-true+validity-screen": "True-objective ranker, screened",
        "Electrical-priority": "Electrical-priority rule",
        "Risk-only": "Risk-only rule", "Lookahead-1": "rolling depth-1",
        "Lookahead-2": "rolling depth-2", "Lookahead-3": "rolling depth-3",
        "One-Step Exact Maxflow": "One-step exact rule", "Random": "uniformly random"}
MLAB9 = dict(MLAB, **{"DQN": "Learned ranker, wrapper"})
# Figure 9 draws ten policies on one plane.  The full names of Table 10 are too
# wide for that, so the axis labels abbreviate them; the caption says so.
MLAB9S = {"Electrical-priority": "Electrical-priority", "Risk-only": "Risk-only",
          "DQN+validity-screen": "Learned, screened",
          "DQN-true+validity-screen": "True-obj., scr.",
          "DQN": "Learned, wrapper", "DQN-true": "True-objective",
          "Lookahead-1": "rolling depth-1", "Lookahead-2": "rolling depth-2",
          "Lookahead-3": "rolling depth-3", "One-Step Exact Maxflow": "One-step exact"}
FIG9_ONE_LABEL = {"Lookahead-2": "rolling depth-2 and 3"}   # depths 2 and 3 coincide

MANIFEST: list[str] = []


def save(fig, name: str, sources) -> None:
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"{name}.{ext}")
    plt.close(fig)
    parts = []
    for s in sources:
        try:
            parts.append(str(Path(s).relative_to(WORK)))
        except (ValueError, TypeError):
            parts.append(str(s))
    MANIFEST.append(f"{name}.pdf | " + " ; ".join(parts))
    print("wrote", FIG / f"{name}.png")


def clab(t: str, s: str, m) -> str:
    return f"{t.replace('ieee','').replace('case_','')}/{s[:3]}/{m}"


def legend_outside(ax, ncol=None, fontsize=10.4, **kw):
    """Put the legend in one row between the panel title and the axes.

    The corner placement used earlier sat the frame on top of the plotted marks
    in Figures 2, 3 and 4: in those panels every corner carries a bar or a
    marker, so an in-axes legend necessarily hides something (Figure 4(a) had
    twelve marks under the frame).  `savefig.bbox = "tight"` keeps the row in
    the saved file.
    """
    handles, labels = ax.get_legend_handles_labels()
    if not handles:
        return None
    if ncol is None:
        ncol = min(len(handles), 2)
    kw.setdefault("handlelength", 1.1)
    kw.setdefault("columnspacing", 1.0)
    kw.setdefault("handletextpad", 0.5)
    kw.setdefault("frameon", False)
    # The row is anchored just above the axes and the title is pushed up by
    # the row's own height, so the reading order is title, legend, data.
    nrows = (len(labels) + ncol - 1) // ncol
    if ax.get_title():
        ax.set_title(ax.get_title(), pad=nrows * fontsize * 1.75 + 8.0)
    return ax.legend(handles, labels, loc="lower center",
                     bbox_to_anchor=(0.5, 1.00), ncol=ncol, fontsize=fontsize, **kw)


def box(ax, x, y, w, h, text, fc="#F2F5F9", ec=CB["dark"], fs=11.5, lw=0.8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.06",
                                fc=fc, ec=ec, lw=lw, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            zorder=3, linespacing=1.25)


def arrow(ax, p, q, color=CB["dark"], lw=0.9, style="-|>", rad=0.0, ms=9.1):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=ms,
                                 color=color, lw=lw, zorder=1,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))


# --------------------------------------------------------------------------- #
# Figure 1 — the framework (conceptual; no data)
# --------------------------------------------------------------------------- #
def fig1_framework() -> None:
    fig, ax = plt.subplots(figsize=(7.4, 4.35))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # --- row (i): a policy is a ranker composed with a screen
    bw, bh, by = 1.66, 1.24, 8.30
    xs = [0.06, 2.08, 4.10, 6.12, 8.14]
    labels = [("state\n$S_{t-1}$", "#F2F5F9"),
              ("candidate set\n$\\mathcal{K},\\ |\\mathcal{K}|{=}20$", "#EFF3F7"),
              ("admissibility\nscreen $\\varphi \\to \\mathcal{A}_t$", "#E3F0EA"),
              ("ranker\n$\\rho \\to a^{\\rho}_t$", "#E7EEF8"),
              ("executed\naction $\\hat a_t$", "#F2F5F9")]
    for x, (txt, col) in zip(xs, labels):
        box(ax, x, by, bw, bh, txt, fc=col)
    for i in range(4):
        arrow(ax, (xs[i] + bw, by + bh / 2), (xs[i + 1], by + bh / 2))
    ax.text(5.0, 7.86, "$u_t(a) = r(S_{t-1} \\cup \\{a\\})$  evaluated exactly by the service model "
                       "of Eq. (1)", ha="center", fontsize=11.2, color="#3D3D3D")
    ax.text(0.06, 9.68, "(i)  every policy of the class is $\\pi = \\rho \\circ \\varphi$",
            fontsize=12.2, color=CB["dark"])

    # --- row (ii): the additive regret decomposition
    x0, wR, wC, yb, hb = 1.30, 4.45, 2.95, 5.62, 0.86
    ax.add_patch(Rectangle((x0, yb), wR, hb, fc="#D9E4F1", ec=CB["blue"], lw=0.9, zorder=2))
    ax.add_patch(Rectangle((x0 + wR, yb), wC, hb, fc="#FAE3C0", ec=CB["orange"], lw=0.9, zorder=2))
    ax.text(x0 + wR / 2, yb + hb / 2, "$R_t$   ranking error", ha="center", va="center",
            fontsize=11.5, color="#123A5E")
    ax.text(x0 + wR + wC / 2, yb + hb / 2, "$C_t$   censoring loss", ha="center", va="center",
            fontsize=11.5, color="#6B4A12")
    arrow(ax, (x0, yb + hb + 0.22), (x0 + wR + wC, yb + hb + 0.22),
          style="<|-|>", lw=0.8, ms=7.8)
    ax.text(x0 + (wR + wC) / 2, yb + hb + 0.52,
            "stepwise regret  $\\delta_t = u^{\\star}_t - u_t(\\hat a_t)$   (Eq. 5)",
            ha="center", fontsize=11.5, color=CB["dark"])
    ax.text(0.06, 7.40, "(ii)  its deficit splits into two separately observable terms",
            fontsize=12.2, color=CB["dark"])
    ax.text(5.0, 5.04, "$R_t = 0$ where $\\rho$ puts the oracle action first;    "
                       "$C_t = 0$ where $\\rho$'s favoured action is admissible",
            ha="center", fontsize=11.0, color="#3D3D3D")

    # --- row (iii): the bound, drawn on the nested chain of reconnected sets
    yc = 2.62
    nx = [0.86, 2.82, 4.78, 6.74, 8.70]
    nlab = ["$\\emptyset$", "$\\{a\\}$", "$\\{a,b\\}$", "$\\{a,b,c\\}$", "$\\mathcal{B}_0$"]
    ax.add_patch(Rectangle((0.14, yc - 0.60), 9.28, 1.20, fc="#F5F6F8", ec="#DCE0E5",
                           lw=0.7, zorder=0))
    for i in range(len(nx) - 1):
        arrow(ax, (nx[i] + 0.64, yc), (nx[i + 1] - 0.64, yc), lw=0.9)
    for x, t in zip(nx, nlab):
        ax.add_patch(Ellipse((x, yc), 1.25, 0.90, fc="white", ec=CB["dark"], lw=0.9, zorder=3))
        ax.text(x, yc, t, ha="center", va="center", fontsize=10.6, zorder=4)
    arrow(ax, (nx[0] - 0.05, yc + 1.12), (nx[-1] + 0.05, yc + 1.12), style="<|-|>",
          color=CB["vermillion"], lw=0.9, ms=7.8)
    ax.text(5.0, yc + 1.44, "$\\Gamma_{\\mathrm{LA}} = f(\\emptyset) - \\sum_t r(S^{\\mathrm{my}}_t)$"
                            "   (Eq. 8), the ceiling on every policy",
            ha="center", fontsize=11.4, color=CB["vermillion"])
    ax.text(9.42, yc + 0.76, "subset lattice of $\\mathcal{B}_0$", fontsize=10.1, color="#7A7F86",
            ha="right")
    ax.text(0.06, 4.62, "(iii)  the optimum, and the chain it bounds", fontsize=12.2,
            color=CB["dark"])
    ax.text(5.0, 1.34, "Eq. (7) evaluates $f(\\emptyset)$ over the whole lattice; "
                       "the one-step exact rule writes one maximal chain",
            ha="center", fontsize=11.0, color="#3D3D3D")

    fig.tight_layout()
    save(fig, "fig1_framework", ["(conceptual; no data source)"])


# --------------------------------------------------------------------------- #
# Figure 2 — attribution of stepwise regret
# --------------------------------------------------------------------------- #
def fig2_attribution() -> None:
    """Attribution of stepwise regret (Table 3).

    Panel (a) reports the three quantities of Section 3.3 separately: ranking fidelity,
    the censoring rate C_t = 1[executed action inadmissible], and the conditional screen
    override C_screen.  The first two are recomputed here from the released stepwise
    traces, because the summary CSV labels the conditional quantity "censoring_rate".
    """
    src_sum = EXP / "06_analysis_results/attribution_summary.csv"
    src_so = EXP / "04_evaluation_new_protocol/stepwise_oracle.csv"
    d = pd.read_csv(src_sum)
    so = pd.read_csv(src_so, usecols=["method", "top1_hit", "chosen_is_candidate",
                                      "best_rank_in_q", "chosen_rank_in_q"])
    arms = ["DQN", "DQN-true", "DQN+validity-screen", "DQN-true+validity-screen"]
    rec = []
    for m in arms:
        g = so[so.method == m]
        r1 = g.best_rank_in_q == 1
        c1 = g.chosen_rank_in_q == 1
        hit = g.top1_hit.astype(bool)
        rec.append(dict(method=m,
                        fidelity=float((g.best_rank_in_q == 1).mean()),
                        cens=float((~g.chosen_is_candidate.astype(bool)).mean()),
                        cscreen=float((r1 & ~hit & ~c1).mean())))
    d = pd.DataFrame(rec)
    # Four arms in one panel.  The names are abbreviated for the axis only, so
    # that they do not collide at the printed size; the caption and Table 4
    # carry the full names.
    SHORT = {"DQN": "Learned\nno screen", "DQN-true": "True-obj.\nno screen",
             "DQN+validity-screen": "Learned\nscreened",
             "DQN-true+validity-screen": "True-obj.\nscreened"}
    lab = [SHORT[m] for m in d.method]
    x = np.arange(len(d))

    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.85))

    ax = axes[0]
    w = 0.26
    ax.bar(x - w, d.fidelity, w, color=CB["blue"], label="ranking fidelity")
    ax.bar(x, d.cens, w, color=CB["orange"], label="censoring rate $C_t$")
    ax.bar(x + w, d.cscreen, w, color="#F2C98A", edgecolor=CB["orange"], lw=0.5,
           label="screen override $C^{\\mathrm{screen}}_t$")
    for xi, r in zip(x, d.itertuples()):
        if r.method.endswith("validity-screen"):
            ax.text(xi, 0.45, "by\nconstr.", ha="center", va="center", fontsize=9.6,
                    color="#666666", linespacing=1.1)
    ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=10.9, rotation=42, ha="right")
    ax.set_ylabel("fraction of steps")
    ax.set_ylim(0, 1.22)
    ax.set_title("(a)  the three quantities", pad=6)
    legend_outside(ax, ncol=2)

    ax = axes[1]
    rank = d.merge(pd.read_csv(src_sum)[["method", "regret_share_from_ranking"]],
                   on="method").regret_share_from_ranking.values
    ax.bar(x, rank, 0.58, color="#8FB8DC", label="ranking error $R_t$")
    ax.bar(x, 1 - rank, 0.58, bottom=rank, color="#F0C98A", label="censoring loss $C_t$")
    ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=10.9, rotation=42, ha="right")
    ax.set_ylabel("share of the regret")
    ax.set_ylim(0, 1.28)
    ax.set_title("(b)  regret composition (Eq. 5)", pad=6)
    legend_outside(ax, ncol=2)
    for xi, r in zip(x, rank):
        ax.text(xi, r / 2, f"{r:.2f}", ha="center", va="center", fontsize=10.7, color="#123A5E")
        if r < 0.999:
            ax.text(xi, r + (1 - r) / 2, f"{1-r:.2f}", ha="center", va="center",
                    fontsize=10.7, color="#6B4A12")

    fig.tight_layout(w_pad=1.4)
    save(fig, "fig2_attribution", [src_sum, src_so])

# --------------------------------------------------------------------------- #
# Figure 3 — the gap by condition, one panel per protocol
# --------------------------------------------------------------------------- #
def fig3_gap_by_condition() -> None:
    su = SUPP / "results/E1_depth_curve/depth_curve_uncoupled_mk7_by_condition.csv"
    sc = SUPP / "results/E1_depth_curve/depth_curve_coupled_B6_mk7_by_condition.csv"
    u, c = pd.read_csv(su), pd.read_csv(sc)
    key = ["topology", "severity", "capacity_margin"]
    lab = [clab(t, s, m) for t, s, m in zip(u.topology, u.severity, u.capacity_margin)]
    x = np.arange(len(u))

    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.05))
    for ax, d, col, ttl, ymax in (
            (axes[0], u, UNCOUPLED, "(a)  uncoupled regime", 25),
            (axes[1], c, BUDGET, "(b)  budget $B=6$", 155)):
        ax.bar(x, d.gamma_mean, 0.56, color=col, alpha=0.9)
        ax.plot(x, d.gamma_max, "v", color=CB["dark"], ms=4.4, ls="none")
        ax.set_xticks(x)
        ax.set_xticklabels(lab, rotation=90, ha="center", fontsize=10.1)
        ax.set_ylabel("$\\Gamma_{\\mathrm{LA}}$  [AUC@25]")
        ax.set_ylim(0, ymax)
        ax.set_title(ttl, pad=6)
        ax.plot([], [], "v", color=CB["dark"], ms=4.4, ls="none", label="max (20 inst.)")
        ax.bar([], [], color=col, label="mean")
        legend_outside(ax, ncol=2)
    # both notes sit to the right of the legend, which is wide at this type size
    axes[1].annotate("120.1", xy=(4, 120.1), xytext=(6.2, 131), fontsize=10.4,
                     arrowprops=dict(arrowstyle="-", lw=0.6, color="#555555"))
    axes[0].annotate("16.7", xy=(5, 16.6), xytext=(6.3, 19.5), fontsize=10.4,
                     arrowprops=dict(arrowstyle="-", lw=0.6, color="#555555"))
    fig.tight_layout(w_pad=1.3)
    save(fig, "fig3_gap_by_condition", [su, sc])


# --------------------------------------------------------------------------- #
# Figure 4 — the instance-selection rule changes the picture
# --------------------------------------------------------------------------- #
def fig4_instance_rule() -> None:
    fo = SUPP / "results/E1_depth_curve/depth_curve_uncoupled_by_condition.csv"
    fn = SUPP / "results/E1_depth_curve/depth_curve_uncoupled_mk7_by_condition.csv"
    o, n = pd.read_csv(fo), pd.read_csv(fn)
    key = ["topology", "severity", "capacity_margin"]
    d = o[key + ["gamma_max", "n_nonzero"]].merge(
        n[key + ["gamma_max", "n_nonzero"]], on=key, suffixes=("_o", "_n"))
    lab = [clab(t, s, m) for t, s, m in zip(d.topology, d.severity, d.capacity_margin)]
    y = np.arange(len(d))[::-1]

    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.25), sharey=True)
    ax = axes[0]
    for yi, (a, b) in zip(y, zip(d.gamma_max_o, d.gamma_max_n)):
        ax.plot([a, b], [yi, yi], color="#C7CDD6", lw=1.2, zorder=1)
    ax.scatter(d.gamma_max_o, y, s=26.0, color=UNCOUPLED, zorder=3, label="rule $N>0$ (legacy)")
    ax.scatter(d.gamma_max_n, y, s=26.0, color=CB["vermillion"], zorder=3,
               label="rule $N\\geq 7$ (unified)")
    ax.set_xlabel("max $\\Gamma_{\\mathrm{LA}}$ [AUC@25]")
    ax.set_title("(a)  per-condition maximum", pad=6)
    legend_outside(ax, ncol=2)
    ax.set_xlim(-0.5, 19.5)
    ax.annotate("0 $\\to$ 15.7", xy=(15.7, y[2]), xytext=(8.0, y[2] + 0.85), fontsize=10.4,
                color=CB["vermillion"],
                arrowprops=dict(arrowstyle="-", lw=0.6, color=CB["vermillion"]))

    ax = axes[1]
    h = 0.34
    ax.barh(y + h / 2, d.n_nonzero_o / 20, h, color=UNCOUPLED, label="rule $N>0$")
    ax.barh(y - h / 2, d.n_nonzero_n / 20, h, color=CB["vermillion"], label="rule $N\\geq 7$")
    ax.set_xlabel("fraction with $\\Gamma_{\\mathrm{LA}}>0$")
    ax.set_title("(b)  per-condition incidence", pad=6)
    ax.set_xlim(0, 0.80)
    legend_outside(ax, ncol=2, fontsize=11.0)
    ax.set_yticks(y)
    ax.set_yticklabels(lab, fontsize=10.6)
    ax.grid(axis="y", alpha=0)

    fig.tight_layout(w_pad=1.0)
    save(fig, "fig4_instance_rule", [fo, fn])


# --------------------------------------------------------------------------- #
# Figure 5 — committed versus rolling: the accessibility of the gap
# --------------------------------------------------------------------------- #
def fig5_depth_profile() -> None:
    pairs = (("(a)  budget $B = 6$",
              SUPP / "results/E3_budget_coupled/rolling_depth_curve_b6.csv", 22),
             ("(b)  uncoupled",
              SUPP / "results/E3_budget_coupled/rolling_depth_curve_uncoupled.csv", 44))
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.95), sharey=True)
    for ax, (ttl, rf, nlive) in zip(axes, pairs):
        ro = pd.read_csv(rf)
        ro = ro[ro.gamma_la.abs() > 1e-9]
        g = ro.groupby("depth").apply(
            lambda z: pd.Series({
                "roll": ((z.realized_auc - z.auc_myopic) / z.gamma_la).mean() * 100,
                "stat": (z.gamma_static / z.gamma_la).mean() * 100}),
            include_groups=False).sort_index()
        ax.plot(g.index.values, g.roll.values, "o-", color=ROLLING, lw=1.5, ms=4.7,
                label="rolling (receding-horizon)")
        ax.plot(g.index.values, g.stat.values, "s--", color=COMMITTED, lw=1.3, ms=4.2,
                label="committed $k$-step plan")
        ax.axhline(100, color=CB["vermillion"], lw=0.8, ls=":")
        ax.set_xlim(0.7, 6.4)
        ax.set_ylim(-18, 116)
        ax.set_xticks(range(1, 7))
        ax.set_xlabel("foresight depth $k$")
        ax.set_title(ttl, pad=6)
        ax.text(0.03, 0.97, f"{nlive} instances with $\\Gamma_{{\\mathrm{{LA}}}}>0$",
                transform=ax.transAxes, ha="left", va="top", fontsize=10.4, color="#666666")
    axes[0].set_ylabel("share of $\\Gamma_{\\mathrm{LA}}$  [%]")
    axes[0].legend(loc="lower right", handlelength=1.5, fontsize=11.0)
    fig.tight_layout(w_pad=1.2)
    save(fig, "fig5_depth_profile",
         [SUPP / "results/E3_budget_coupled/rolling_depth_curve_b6.csv",
          SUPP / "results/E3_budget_coupled/rolling_depth_curve_uncoupled.csv"])


# --------------------------------------------------------------------------- #
# Figure 6 — the phase structure of the gap
# --------------------------------------------------------------------------- #
def fig6_phase() -> None:
    src = SUPP / "results/E2_phase_diagram/phase_scenarios.csv"
    d = pd.read_csv(src)
    budgets = [0, 4, 6, 8]
    regions = ["non-identifiable", "shallow", "long-range"]
    cnt = d.pivot_table(index="budget", columns="region", values="scenario_seed",
                        aggfunc="count").reindex(budgets).fillna(0)
    n_per = int(cnt.sum(axis=1).iloc[0])

    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.30),
                             gridspec_kw=dict(width_ratios=[1.05, 1.42]))
    ax = axes[0]
    x = np.arange(len(regions))
    w = 0.20
    shades = [plt.cm.Blues(v) for v in (0.30, 0.48, 0.66, 0.85)]
    for k, b in enumerate(budgets):
        v = [cnt.loc[b, r] for r in regions]
        ax.bar(x + (k - 1.5) * w, v, w, color=shades[k], label=f"$B={b}$",
               edgecolor="white", lw=0.4)
    ax.set_xticks(x)
    ax.set_xticklabels(["non-\nidentifiable", "shallow", "long-range"], fontsize=11.0,
                       rotation=20, ha="right")
    ax.set_ylabel(f"instances  [of {n_per} shared]")
    ax.set_ylim(0, 172)
    ax.set_title("(a)  class by budget", pad=6)
    # shifted right so its left edge clears the rotated count labels
    ax.legend(ncol=2, loc="upper right", bbox_to_anchor=(1.10, 1.0),
              handlelength=0.9, fontsize=10.9, columnspacing=0.8)
    # the counts are printed on the bars so that Figure 6(a) carries the whole
    # classification and no separate table is needed for it
    for k, b in enumerate(budgets):
        for xi, r in zip(x, regions):
            ax.text(xi + (k - 1.5) * w, cnt.loc[b, r] + 3.0, f"{int(cnt.loc[b, r])}",
                    ha="center", va="bottom", rotation=90, fontsize=9.6, color="#333333")
    ax.annotate("0 at $B=4$", xy=(2 + 0.5 * w, 0), xytext=(1.30, 55), fontsize=10.4,
                color=CB["vermillion"], ha="center",
                arrowprops=dict(arrowstyle="-", lw=0.6, color=CB["vermillion"]))

    ax = axes[1]
    key = ["topology", "severity", "capacity_margin"]
    piv = d.pivot_table(index=key, columns="budget", values="gamma_la", aggfunc="max")
    piv = piv.reindex(sorted(piv.index, key=lambda t: (t[0], t[1], t[2])))
    im = ax.imshow(piv.values, aspect="auto", cmap="YlGnBu", vmin=0, vmax=134)
    ax.set_xticks(range(len(piv.columns)))
    ax.set_xticklabels([str(c) for c in piv.columns])
    ax.set_yticks(range(len(piv)))
    ax.set_yticklabels([clab(*t) for t in piv.index], fontsize=10.4)
    ax.set_xlabel("budget $B$")
    ax.set_title("(b)  max $\\Gamma_{\\mathrm{LA}}$ by condition", pad=6)
    ax.grid(False)
    for i in range(len(piv)):
        for j in range(len(piv.columns)):
            v = piv.values[i, j]
            ax.text(j, i, f"{max(v, 0):.0f}", ha="center", va="center", fontsize=9.6,
                    color="white" if v > 80 else "#333333")
    cb = fig.colorbar(im, ax=ax, fraction=0.030, pad=0.015)
    cb.set_label("max $\\Gamma_{\\mathrm{LA}}$", fontsize=10.9)
    cb.ax.tick_params(labelsize=10.2)
    fig.tight_layout(w_pad=1.3)
    save(fig, "fig6_phase", [src])


# --------------------------------------------------------------------------- #
# Figure 7 — head-to-head on the aligned sample
# --------------------------------------------------------------------------- #
def fig7_headtohead() -> None:
    src = SUPP / "results/E3_budget_coupled/episodes_valid.csv"
    e = pd.read_csv(src)
    alts = ["Lookahead-2", "Lookahead-3", "One-Step Exact Maxflow", "Electrical-priority",
            "Risk-only", "Random", "DQN+validity-screen", "DQN-true+validity-screen",
            "DQN", "DQN-true"]
    m = e.groupby("method").auc25_recomputed.mean()
    opt = e.groupby(["topology", "severity", "capacity_margin", "scenario_seed"]).offline_auc_optimal.mean().mean()
    alts = [a for a in alts if a in m.index]

    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.45),
                             gridspec_kw=dict(width_ratios=[1.25, 1.15]))
    ax = axes[0]
    y = np.arange(len(alts))[::-1]
    cols = [CB["blue"] if a.startswith("Lookahead") else
            (CB["dark"] if a.startswith("One-Step") else
             (CB["green"] if a == "Electrical-priority" else
              (CB["sky"] if a == "Risk-only" else "#7F7F7F"))) for a in alts]
    ax.barh(y, [m[a] for a in alts], 0.62, color=cols)
    ax.axvline(opt, color=CB["vermillion"], lw=1.0, ls="--")
    ax.set_yticks(y)
    ax.set_yticklabels([MLAB.get(a, a) for a in alts], fontsize=10.7)
    ax.set_xlabel("mean AUC@25")
    ax.set_xlim(0, opt * 1.22)
    ax.set_ylim(-1.20, len(alts) - 0.10)
    ax.set_title("(a)  mean objective", pad=6)
    ax.grid(axis="y", alpha=0)
    ax.text(opt, -1.02, "mean offline optimum", ha="right", fontsize=10.2,
            color=CB["vermillion"])

    ax = axes[1]
    key = ["topology", "severity", "capacity_margin", "scenario_seed"]
    piv = e.pivot_table(index=key, columns="method", values="auc25_recomputed")
    learners = ["DQN", "DQN-true", "DQN+validity-screen", "DQN-true+validity-screen"]
    best = piv[learners].max(axis=1)
    delta = (piv["Lookahead-2"] - best).groupby(level=[0, 1, 2]).mean()
    delta.index = [clab(*t) for t in delta.index]
    xx = np.arange(len(delta))
    ax.axhline(0, color=CB["dark"], lw=0.8)
    ax.bar(xx, delta.values, 0.6, color=CB["blue"])
    ax.set_xticks(xx); ax.set_xticklabels(delta.index, rotation=90, ha="center", fontsize=9.8)
    ax.set_ylabel("$\\Delta$ AUC@25\nvs. best learner")
    ax.set_ylim(0, delta.max() * 1.15)
    ax.set_title("(b)  advantage over the best learner", pad=6)
    fig.tight_layout(w_pad=1.3)
    save(fig, "fig7_headtohead", [src])


# --------------------------------------------------------------------------- #
# Figure 8 — the capacity-rule sweep
# --------------------------------------------------------------------------- #
def fig8_capacity_rules() -> None:
    su = SUPP / "results/E2_phase_diagram/service_rule_axis_uncoupled.csv"
    sc = SUPP / "results/E2_phase_diagram/service_rule_axis_coupledB6.csv"
    frames = {}
    for tag, f in (("uncoupled", su), ("budget $B=6$", sc)):
        d = pd.read_csv(f)
        frames[tag] = d.groupby("rule").gamma_la.agg(
            share=lambda s: float((s.abs() > 1e-9).mean()), mx="max")
    rules = ["R1_prop_floor002", "R2_prop_floor05", "R3_uniform_thermal", "R4_prop_nofloor"]
    x = np.arange(len(rules))
    w = 0.34

    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.80))
    for ax, field, ylab, ttl, ymax, fmt in (
            (axes[0], "share", "fraction with $\\Gamma_{\\mathrm{LA}}>0$",
             "(a)  incidence", 0.44, "{:.2f}"),
            (axes[1], "mx", "max $\\Gamma_{\\mathrm{LA}}$ [AUC@25]",
             "(b)  extreme value", 105, "{:.1f}")):
        for i, (tag, col) in enumerate((("uncoupled", UNCOUPLED), ("budget $B=6$", BUDGET))):
            v = [frames[tag].loc[r, field] for r in rules]
            ax.bar(x + (i - 0.5) * w, v, w, color=col, label=tag)
        # one label per rule: R2 and R3 are 0 in both regimes, and two adjacent
        # "0.00" labels over zero-height bars collide, so print a single label
        # centred on the rule
        vu = [frames["uncoupled"].loc[r, field] for r in rules]
        vb = [frames["budget $B=6$"].loc[r, field] for r in rules]
        for xi, a, b in zip(x, vu, vb):
            if abs(a - b) <= ymax * 5e-3:
                ax.text(xi, max(a, b) + ymax * 0.018, fmt.format(a), ha="center",
                        fontsize=9.9)
            else:
                ax.text(xi - w / 2, a + ymax * 0.018, fmt.format(a), ha="center",
                        fontsize=9.9)
                ax.text(xi + w / 2, b + ymax * 0.018, fmt.format(b), ha="center",
                        fontsize=9.9)
        ax.set_xticks(x)
        ax.set_xticklabels([r.split("_")[0] for r in rules])
        ax.set_ylabel(ylab)
        ax.set_ylim(0, ymax)
        ax.set_title(ttl, pad=6)
        ax.legend(loc=("upper right" if field == "share" else "upper left"),
                  handlelength=1.0, fontsize=11.0)
    fig.text(0.5, -0.15,
             "R1 utilization-proportional, $\\phi = 0.002$   |   R2 same rule, $\\phi = 0.05$\n"
             "R3 uniform thermal ratings   |   R4 utilization-proportional, no floor",
             ha="center", va="top", fontsize=10.1, linespacing=1.5)
    fig.tight_layout(w_pad=1.2)
    save(fig, "fig8_capacity_rules", [su, sc])


# --------------------------------------------------------------------------- #
# Figure 9 — cost and quality
# --------------------------------------------------------------------------- #
def fig9_cost_quality() -> None:
    tb = EXP / "06_analysis_results/timing_benchmark.csv"
    te = SUPP / "results/E4_timing/timing_ext_budget6.csv"
    ep = SUPP / "results/E3_budget_coupled/episodes_valid.csv"

    t = pd.read_csv(tb)
    present = set(t.method)
    rows = [r for r in ["Electrical-priority", "Risk-only", "DQN+validity-screen",
                        "DQN-true+validity-screen", "DQN", "One-Step Exact Maxflow"]
            if r in present]
    tp = t.pivot_table(index=["topology", "severity"], columns="method", values="mean_ms")
    conds = list(tp.index)

    # Panel (b) carries nine labels around three clusters, so it needs more
    # vertical room than the other figures; the extra height is spent on label
    # spacing, not on the plotted range.
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 4.05),
                             gridspec_kw=dict(width_ratios=[1.22, 1.18]))
    ax = axes[0]
    y = np.arange(len(rows))[::-1]
    h = 0.19
    for k, c in enumerate(conds):
        v = tp.loc[c].reindex(rows).astype(float).values
        ax.barh(y + (1.5 - k) * h, v, h,
                label=f"{c[0].replace('ieee','')} {c[1][:3]}.",
                color=plt.cm.Blues(0.34 + 0.19 * k), edgecolor="white", lw=0.3)
    ax.set_xscale("log")
    ax.set_xlim(3e-4, 3e3)
    ax.set_yticks(y)
    ax.set_yticklabels([MLAB9S.get(r, r) for r in rows], fontsize=10.7)
    ax.set_ylim(-0.62, len(rows) - 0.05)
    ax.set_xlabel("mean decision time  [ms, log]")
    ax.set_title("(a)  latency spectrum", pad=6)
    ax.legend(ncol=2, loc="upper right", fontsize=10.1, handlelength=0.9,
              columnspacing=0.8, borderaxespad=0.4)
    ax.grid(axis="y", alpha=0)
    # the boundary brackets the two rows that measure the same network
    arrow(ax, (0.062, 1.0), (0.062, 3.0), color=CB["vermillion"], style="<|-|>", lw=0.8, ms=8.4)
    ax.text(0.078, 2.0, "2.5--3.1$\\times$\nboundary", fontsize=10.4, ha="left", va="center",
            color=CB["vermillion"], linespacing=1.15)

    ax = axes[1]
    e = pd.read_csv(ep)
    q = e.groupby("method").auc25_recomputed.mean()
    lat = pd.read_csv(te).groupby("method").mean_ms.mean()
    opt = e.groupby(["topology", "severity", "capacity_margin", "scenario_seed"]).offline_auc_optimal.mean().mean()
    ax.axhline(opt, color=CB["vermillion"], lw=0.9, ls="--")
    ax.text(6e-4, opt + 26, "offline optimum", fontsize=10.2, ha="left", color=CB["vermillion"])
    pts = [m for m in ["Electrical-priority", "Risk-only", "DQN+validity-screen",
                       "DQN-true+validity-screen", "DQN", "DQN-true",
                       "Lookahead-1", "Lookahead-2", "Lookahead-3",
                       "One-Step Exact Maxflow"] if m in lat.index and m in q.index]
    for m_ in pts:
        ax.scatter(lat[m_], q[m_], s=28.6, color=MCOL.get(m_, CB["grey"]), zorder=3,
                   edgecolor="white", lw=0.4)
    fr = []
    for m_ in sorted(pts, key=lambda z: lat[z]):
        if not fr or q[m_] > q[fr[-1]] + 1e-9:
            fr.append(m_)
    ax.plot([lat[m_] for m_ in fr], [q[m_] for m_ in fr], color="#C7CDD6", lw=0.9, zorder=2)
    off = {"Electrical-priority": (8, -4), "Risk-only": (8, -12),
           "DQN+validity-screen": (8, 16), "DQN-true+validity-screen": (8, -20),
           "DQN": (8, -6), "DQN-true": (8, 6),
           "One-Step Exact Maxflow": (8, -14), "Lookahead-2": (-9, -34),
           "Lookahead-3": None}
    for m_ in pts:
        if off.get(m_, (5, 3)) is None:
            continue                      # depths 2 and 3 share one label
        dx, dy = off.get(m_, (5, 3))
        name = FIG9_ONE_LABEL.get(m_, MLAB9S.get(m_, m_))
        # the two coincident rolling points share one label, so it gets a leader
        lead = (dict(arrowprops=dict(arrowstyle="-", lw=0.6, color=CB["blue"]))
                if m_ in FIG9_ONE_LABEL else {})
        ax.annotate(name, (lat[m_], q[m_]), textcoords="offset points",
                    xytext=(dx, dy), fontsize=10.0,
                    ha="right" if dx < 0 else "left", **lead)
    ax.set_xscale("log")
    ax.set_xlim(1.6e-4, 2e4)
    ax.set_ylim(q.min() - 125, opt + 145)
    ax.set_xlabel("mean decision time  [ms, log]")
    ax.set_ylabel("mean AUC@25")
    ax.set_title("(b)  cost--quality plane", pad=6)
    fig.tight_layout(w_pad=1.3)
    save(fig, "fig9_cost_quality", [tb, te, ep])


def main() -> int:
    for fn in (fig1_framework, fig2_attribution, fig3_gap_by_condition, fig4_instance_rule,
               fig5_depth_profile, fig6_phase, fig7_headtohead, fig8_capacity_rules,
               fig9_cost_quality):
        fn()
    (FIG / "MANIFEST.txt").write_text(
        "Figure | input files\n" + "\n".join(MANIFEST) + "\n", encoding="utf-8")
    print("manifest written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
