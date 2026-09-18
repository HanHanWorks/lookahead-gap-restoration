"""Stage-B analysis: service-rule axis (E2b) + its validation + moderate head-to-head.

Run after run_stage_b.sh finishes:

    python analyze_stage_b.py

Writes results/summary/stage_b_digest.txt

Three things are checked here.

1. VALIDATION. Rule R1 is the paper's default capacity rule, and the script
   reproduces it with the environment's own max-flow. So R1 must agree with the
   frozen E1 Gamma_LA instance by instance. If it does not, the injected-capacity
   re-implementation is wrong and nothing else in the table can be believed.

2. THE AXIS ITSELF. Gamma_LA under four capacity rules on the same scenarios.

3. MODERATE HEAD-TO-HEAD. The E3 domination result originally covered only the
   severe conditions; the moderate conditions are summarised separately here.
"""
from __future__ import annotations

import argparse
import glob
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

RULES = ["R1_prop_floor002", "R2_prop_floor05", "R3_uniform_thermal", "R4_prop_nofloor"]
LEARNERS = ["DQN", "DQN+validity-screen", "DQN-true", "DQN-true+validity-screen"]


def _t(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def validate(R: Path, digest: list) -> None:
    _t("E2b VALIDATION  rule R1 must reproduce the frozen E1 Gamma_LA exactly")
    pairs = [("uncoupled", "depth_curve_uncoupled_mk7.csv"),
             ("coupledB6", "depth_curve_coupled_B6_mk7.csv")]
    for tag, frozen_name in pairs:
        f = R / "E2_phase_diagram" / f"service_rule_axis_{tag}.csv"
        g = R / "E1_depth_curve" / frozen_name
        if not f.exists() or not g.exists():
            print(f"[skip] {tag}: missing {f.name if not f.exists() else g.name}")
            continue
        d = pd.read_csv(f)
        e = pd.read_csv(g)
        key = ["topology", "severity", "capacity_margin", "scenario_seed"]
        m = d[d.rule == RULES[0]].merge(e[key + ["gamma_la", "K"]], on=key,
                                        suffixes=("_rule", "_frozen"))
        if m.empty:
            print(f"[skip] {tag}: no overlapping instances")
            continue
        diff = (m.gamma_la_rule - m.gamma_la_frozen).abs()
        print(f"\n-- {tag}: n={len(m)} shared instances, "
              f"max|diff| = {diff.max():.3e}, "
              f"K mismatch = {int((m.K_rule != m.K_frozen).sum())} --")
        print(m[["topology", "severity", "scenario_seed", "K_frozen",
                 "gamma_la_frozen", "gamma_la_rule", ]].to_string(index=False))
        ok = "PASS" if diff.max() < 1e-6 else "FAIL"
        digest.append(f"E2b validation [{tag}]: {ok} max|diff|={diff.max():.3e} "
                      f"on n={len(m)} shared instances")


def axis(R: Path, digest: list) -> None:
    _t("E2b  Gamma_LA under four service-model capacity rules (same scenarios)")
    for tag, proto in (("uncoupled", "uncoupled protocol, B=0"),
                       ("coupledB6", "budget-coupled B=6")):
        f = R / "E2_phase_diagram" / f"service_rule_axis_{tag}.csv"
        if not f.exists():
            print(f"[skip] {f.name}")
            continue
        d = pd.read_csv(f)
        d["g_nonzero"] = d.gamma_la.abs() > 1e-9
        print(f"\n-- {tag} ({proto}), {d.scenario_seed.nunique()} seeds x "
              f"{d.groupby(['topology', 'severity']).ngroups} conditions --")
        piv = d.pivot_table(index=["topology", "severity"], columns="rule",
                            values="gamma_la", aggfunc="mean").round(3)
        print("\n   mean Gamma_LA by rule:")
        print(piv[RULES].to_string())
        piv2 = d.pivot_table(index=["topology", "severity"], columns="rule",
                             values="g_nonzero", aggfunc="mean").round(3)
        print("\n   share of instances with Gamma_LA > 0:")
        print(piv2[RULES].to_string())
        agg = d.groupby("rule").agg(n=("gamma_la", "size"),
                                    mean=("gamma_la", "mean"),
                                    max=("gamma_la", "max"),
                                    share_nonzero=("g_nonzero", "mean"),
                                    sec_per_eval=("seconds", "mean")).round(4)
        print("\n   pooled across all conditions:")
        print(agg.loc[RULES].to_string())
        for r in RULES:
            digest.append(f"E2b [{tag}] {r}: share_nonzero="
                          f"{agg.loc[r, 'share_nonzero']:.3f}, "
                          f"mean={agg.loc[r, 'mean']:.3f}, max={agg.loc[r, 'max']:.3f}")


def moderate_h2h(R: Path, digest: list) -> None:
    _t("E3  head-to-head on the MODERATE conditions (new in stage B)")
    for stem, note in (("episodes__", "ALL 20 scenarios"),
                       ("episodes_valid__", "valid-seed sample")):
        parts = sorted(glob.glob(str(R / "E3_budget_coupled" / f"{stem}*.csv")))
        if not parts:
            print(f"[skip] {stem}*")
            continue
        d = pd.concat([pd.read_csv(p) for p in parts], ignore_index=True)
        if "severity" not in d:
            continue
        d = d[d.severity == "moderate"]
        if d.empty:
            print(f"[skip] {stem}*: no moderate rows")
            continue
        d["cond"] = d.topology + "/m" + d.capacity_margin.astype(str)
        print(f"\n-- {stem}* moderate ({note}), {len(d)} rows, "
              f"{d.cond.nunique()} conditions --")
        rows = []
        for c, g in d.groupby("cond"):
            p = g.pivot_table(index="scenario_seed", columns="method",
                              values="auc25_recomputed")
            if "Lookahead-2" not in p:
                continue
            la = p["Lookahead-2"]
            best = p[LEARNERS].max(axis=1)
            row = dict(cond=c, n=len(p), LA2=round(la.mean(), 1),
                       best_learner=round(best.mean(), 1))
            for m in sorted(p.columns):
                if m in ("Lookahead-2", "Lookahead-3"):
                    continue
                row[f"d_{m}"] = round((la - p[m]).mean(), 1)
            dd = (la - best).dropna()
            if len(dd):
                t = stats.wilcoxon(dd) if (dd != 0).any() else None
                row["LA2_minus_best"] = round(dd.mean(), 1)
                row["wins_vs_best"] = f"{int((dd > 0).sum())}/{len(dd)}"
                row["p"] = f"{t.pvalue:.2e}" if t else "1.0"
            rows.append(row)
        A = pd.DataFrame(rows)
        print(A.to_string(index=False))
        if "LA2_minus_best" in A:
            digest.append(f"E3 moderate h2h [{stem}]: LA2 beats the best learner by "
                          f"{A.LA2_minus_best.min():.1f}-{A.LA2_minus_best.max():.1f} "
                          f"AUC units over {len(A)} conditions")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--supp", default=str(Path(__file__).resolve().parents[1]))
    a = ap.parse_args()
    R = Path(a.supp).expanduser() / "results"
    digest: list = []
    validate(R, digest)
    axis(R, digest)
    moderate_h2h(R, digest)
    _t("STAGE B DIGEST")
    for line in digest:
        print(" *", line)
    out = R / "summary" / "stage_b_digest.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(digest), encoding="utf-8")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
