"""Consolidate the supplementary-experiment artefacts into paper-ready tables.

Reads everything under $SUPP/results and writes $SUPP/results/summary/*.csv plus a
plain-text digest. Every table states the exact instance sample it was computed on,
because the single most common way to mis-state these results is to average over a
sample that mixes instances with and without an exact reference.

Usage:  python analyze_supp.py [--supp DIR]
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

LEARNERS = ["DQN", "DQN+validity-screen", "DQN-true", "DQN-true+validity-screen"]


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _read_csvs(pattern: str) -> pd.DataFrame:
    parts = sorted(glob.glob(pattern))
    if not parts:
        return pd.DataFrame()
    out = []
    for p in parts:
        d = pd.read_csv(p)
        # condition tag from the file name, e.g. episodes__ieee118__severe__1.25.csv
        tag = Path(p).name.split("__", 1)[1].replace(".csv", "")
        d["cond"] = tag
        out.append(d)
    return pd.concat(out, ignore_index=True)


def _paired(la: pd.Series, other: pd.Series) -> dict:
    d = (la - other).dropna()
    if d.empty:
        return dict(n=0, delta=np.nan, wins=0, p=np.nan)
    t = stats.wilcoxon(d) if (d != 0).any() else None
    return dict(n=int(len(d)), delta=float(d.mean()), wins=int((d > 0).sum()),
                p=float(t.pvalue) if t else 1.0)


def _table(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


# --------------------------------------------------------------------------- #
# E1 — static depth curves
# --------------------------------------------------------------------------- #
def _gamma_cols(d: pd.DataFrame) -> list[str]:
    cols = [c for c in d.columns if c.startswith("gamma_d")]
    return sorted(cols, key=lambda c: int(c.split("gamma_d")[1]))


def e1(R: Path, digest: list) -> None:
    _table("E1  committed (static) depth-lookahead plan: value curve, exact DP")
    for proto, inst, cond in (
            ("uncoupled", "depth_curve_uncoupled.csv",
             "depth_curve_uncoupled_by_condition.csv"),
            ("coupled B=6", "depth_curve_coupled_B6.csv",
             "depth_curve_coupled_B6_by_condition.csv"),
            ("uncoupled, controlled min_k=7", "depth_curve_uncoupled_mk7.csv",
             "depth_curve_uncoupled_mk7_by_condition.csv"),
            ("coupled B=6, controlled min_k=7", "depth_curve_coupled_B6_mk7.csv",
             "depth_curve_coupled_B6_mk7_by_condition.csv")):
        fi, fc = R / "E1_depth_curve" / inst, R / "E1_depth_curve" / cond
        if not fc.exists():
            print(f"[skip] {fc.name}")
            continue
        C = pd.read_csv(fc)
        print(f"\n-- {proto}: {len(C)} conditions, "
              f"{int(C.n.sum())} instances total --")
        print(C[["topology", "severity", "capacity_margin", "mean_K", "gamma_mean",
                 "gamma_max", "n_nonzero", "d90_median"]].to_string(index=False))
        # normalised value curve: mean share of Gamma_LA recovered by a committed
        # depth-k plan, over the instances that have Gamma_LA > 0
        if fi.exists():
            d = pd.read_csv(fi)
            g = _gamma_cols(d)
            live = d[d.gamma_la > 1e-9].copy()
            if len(live):
                norm = live.groupby(["topology", "severity", "capacity_margin"])[
                    g].mean()
                for c in g:
                    norm[c] = norm[c] / live.groupby(
                        ["topology", "severity", "capacity_margin"]).gamma_la.mean()
                print(f"\n   share of Gamma_LA recovered by a committed depth-k plan "
                      f"(instances with Gamma_LA>0, n={len(live)}):")
                print((norm[g[:8]] * 100).round(1).to_string())
        digest.append(
            f"E1 {proto}: {len(C)} conditions, Gamma_LA max={C.gamma_max.max():.3f}, "
            f"conditions with a nonzero gamma={int((C.gamma_max > 1e-9).sum())}/{len(C)}, "
            f"median depth-to-90%={C.d90_median.median():.1f}")


# --------------------------------------------------------------------------- #
# E3 — rolling curves
# --------------------------------------------------------------------------- #
def e3_rolling(R: Path, digest: list) -> None:
    _table("E3  receding-horizon (rolling) depth-lookahead vs the committed plan")
    for proto, fname in (("coupled B=6", "rolling_depth_curve_b6.csv"),
                         ("uncoupled", "rolling_depth_curve_uncoupled.csv")):
        f = R / "E3_budget_coupled" / fname
        if not f.exists():
            print(f"[skip] {f.name}")
            continue
        d = pd.read_csv(f)
        if d.empty:
            print(f"[skip] {f.name} (empty)")
            continue
        d["cond"] = d.topology + "/m" + d.capacity_margin.astype(str)
        base = d.groupby("cond").agg(myo=("auc_myopic", "mean"),
                                     opt=("auc_optimal", "mean"),
                                     gla=("gamma_la", "mean"),
                                     gla_max=("gamma_la", "max"))
        rows = []
        for c, g in d.groupby("cond"):
            b = base.loc[c]
            r = dict(cond=c, K=round(g.K.mean(), 1),
                     Gamma_LA_mean=round(b.gla, 3), Gamma_LA_max=round(b.gla_max, 3))
            for dd in (1, 2, 3):
                s = g[g.depth == dd]
                if s.empty:
                    continue
                # share of Gamma_LA realised by the ROLLING depth-dd controller
                live = s[s.gamma_la > 1e-9]
                r[f"roll_d{dd}_%opt"] = round(s.realized_auc.mean() / b.opt * 100, 2)
                r[f"roll_d{dd}_%G"] = (round(((live.realized_auc - live.auc_myopic)
                                              / live.gamma_la).mean() * 100, 1)
                                       if len(live) else None)
            # share of Gamma_LA of the best COMMITTED (static) plan at the same depth
            for dd in (1, 2, 3):
                s = d[(d.depth == dd) & (d.cond == c) & (d.gamma_la > 1e-9)]
                if len(s):
                    r[f"static_d{dd}_%G"] = round(
                        ((s.gamma_static / s.gamma_la).mean() * 100), 1)
            rows.append(r)
        out = pd.DataFrame(rows)
        print(f"\n-- {proto}  (min depth at which the rolling controller reaches the"
              f" exact optimum) --")
        print(out.to_string(index=False))
        digest.append(f"E3 rolling {proto}: rolling depth-2 reaches "
                      f"{out['roll_d2_%opt'].min():.2f}-{out['roll_d2_%opt'].max():.2f}% "
                      f"of the exact optimum across {len(out)} conditions; "
                      f"a committed plan at depth 2 only reaches "
                      f"{out['static_d2_%G'].min():.1f}-{out['static_d2_%G'].max():.1f}% "
                      f"of Gamma_LA")


# --------------------------------------------------------------------------- #
# E3 — head-to-head
# --------------------------------------------------------------------------- #
def e3_headtohead(R: Path, digest: list) -> None:
    _table("E3  head-to-head: rolling depth-2 lookahead vs every alternative")
    for stem, note in (("episodes__", "ALL 20 scenarios (8 lack an exact reference)"),
                       ("episodes_valid__", "ALIGNED sample: 20 scenarios, all "
                                            "with an exact reference")):
        e = _read_csvs(str(R / "E3_budget_coupled" / f"{stem}*.csv"))
        if e.empty:
            print(f"[skip] {stem}*")
            continue
        has_ref = e.offline_auc_optimal.notna()
        print(f"\n-- {stem}*  ({note}) --")
        print(f"   rows={len(e)}  conditions={e.cond.nunique()}  "
              f"scenarios/cond={e.scenario_seed.nunique()}  "
              f"scenarios with an exact reference={int(has_ref.sum() / e.method.nunique())}")
        agg = []
        for c, g in e.groupby("cond"):
            p = g.pivot_table(index="scenario_seed", columns="method",
                              values="auc25_recomputed")
            if "Lookahead-2" not in p:
                continue
            ref = g.groupby("scenario_seed").offline_auc_optimal.first()
            valid = ref.notna()
            la = p["Lookahead-2"]
            row = dict(cond=c, n=len(p), n_valid=int(valid.sum()),
                       LA2=round(la.mean(), 1))
            if valid.any():
                row["opt"] = round(ref[valid].mean(), 1)
                row["LA2_%opt(valid)"] = round(
                    la[valid].sum() / ref[valid].sum() * 100, 2)
            for m in sorted(p.columns):
                if m in ("Lookahead-2", "Lookahead-3"):
                    continue
                out = _paired(la, p[m])
                row[f"d_{m}"] = round(out["delta"], 1)
            agg.append(row)
        A = pd.DataFrame(agg)
        print(A.to_string(index=False))

        # pooled paired test on the aligned sample
        e["_valid"] = e.offline_auc_optimal.notna()
        sub = e[e._valid] if "valid" in stem else e
        rows = []
        # NOTE: the pairing key must be the FULL condition key, not the bare tag.
        # Grouping by tag alone silently mixes conditions whenever two of them
        # share a tag prefix, and it discards the tie count -- which is exactly
        # the statistic that matters here: LA2 is *never worse* than the one-step
        # exact rule, so ties (not losses) are the norm and a "wins/n" ratio
        # alone reads as a near-tie when the real statement is "never worse".
        KEY = ["topology", "severity", "capacity_margin", "scenario_seed"]
        for c, g in sub.groupby(["topology", "severity", "capacity_margin"]):
            p = g.pivot_table(index=KEY, columns="method",
                              values="auc25_recomputed")
            if "Lookahead-2" not in p:
                continue
            la = p["Lookahead-2"]
            for m in sorted(p.columns):
                if m in ("Lookahead-2", "Lookahead-3"):
                    continue
                dd = (la - p[m]).dropna()
                if dd.empty:
                    continue
                t = stats.wilcoxon(dd) if (dd != 0).any() else None
                rows.append(dict(method=m, cond="/".join(str(x) for x in c),
                                 n=int(len(dd)), delta=float(dd.mean()),
                                 wins=int((dd > 0).sum()),
                                 ties=int((dd == 0).sum()),
                                 losses=int((dd < 0).sum()),
                                 p=float(t.pvalue) if t else 1.0))
        P = pd.DataFrame(rows)
        if not P.empty:
            s = P.groupby("method").agg(
                wins=("wins", "sum"), ties=("ties", "sum"),
                losses=("losses", "sum"), n=("n", "sum"),
                mean_delta=("delta", "mean"),
                worst_p=("p", "max")).round(4).sort_values("mean_delta",
                                                           ascending=False)
            print(f"\n   pooled paired test ({sub.scenario_seed.nunique()} scenarios "
                  f"per condition, {sub.cond.nunique()} conditions):")
            print(s.to_string())
            digest.append(f"E3 h2h [{stem}] pooled: "
                          f"{s.loc[LEARNERS, 'wins'].sum()}/{s.loc[LEARNERS, 'n'].sum()}"
                          f" learner-vs-LA2 wins, {s.loc[LEARNERS, 'losses'].sum()} "
                          f"losses, worst p="
                          f"{s.loc[LEARNERS, 'worst_p'].max():.5f}, "
                          f"mean margin {s.loc[LEARNERS, 'mean_delta'].min():.1f}-"
                          f"{s.loc[LEARNERS, 'mean_delta'].max():.1f} AUC units")


# --------------------------------------------------------------------------- #
# E4 / E5
# --------------------------------------------------------------------------- #
def e4_e5(R: Path, digest: list) -> None:
    _table("E4  timing  /  E5  third topology")
    for f in sorted((R / "E4_timing").glob("*.csv")):
        d = pd.read_csv(f)
        print(f"\n-- {f.name} --")
        print(d.to_string(index=False) if len(d) <= 30 else d.head(30).to_string(index=False))
        digest.append(f"E4 {f.name}: {len(d)} rows")
    for f in sorted((R / "E5_third_topo").glob("*.json")):
        try:
            j = json.loads(f.read_text())
        except Exception:
            continue
        print(f"\n-- {f.name} --")
        print(json.dumps(j, indent=2, ensure_ascii=False)[:1500])
        digest.append(f"E5 {f.name}: present")
    for f in sorted((R / "E5_third_topo").glob("*.csv")):
        d = pd.read_csv(f)
        print(f"\n-- E5 {f.name} ({len(d)} rows) --")
        print(d.head(20).to_string(index=False))
        digest.append(f"E5 {f.name}: {len(d)} rows")


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--supp", default=str(Path(__file__).resolve().parents[1]))
    a = ap.parse_args()
    S = Path(a.supp).expanduser()
    R = S / "results"
    (R / "summary").mkdir(parents=True, exist_ok=True)
    digest: list = []
    e1(R, digest)
    e3_rolling(R, digest)
    e3_headtohead(R, digest)
    e4_e5(R, digest)
    _table("DIGEST")
    for line in digest:
        print(" *", line)
    (R / "summary" / "digest.txt").write_text("\n".join(digest), encoding="utf-8")
    print(f"\nwrote {R / 'summary' / 'digest.txt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
