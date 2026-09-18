#!/bin/bash
# Stage B of the follow-up batch (2026-09-13).
#
#  B1) E2b service-rule axis, uncoupled protocol  -> does Gamma_LA depend on the
#      capacity rule of the service model?  (R1 = paper default, reproduced by
#      the environment's own max-flow; R2 floor 5%; R3 uniform thermal; R4 no floor)
#  B2) E2b service-rule axis, budget-coupled B=6
#  B3) E3 head-to-head on the MODERATE conditions (non-valid sample)
#  B4) E3 head-to-head on the MODERATE conditions (valid-seed sample)
#
# B1/B2 are exact-max-flow (cheap evaluator), B3/B4 reuse the 12 B=6 DQN models.
set -u
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
U=~/segan/SEGAN_SUPP_2026-09-13
PY=~/miniconda3/envs/segan/bin/python
cd "$U/code" || exit 1

$PY e2b_service_model_check.py --topos ieee118,ieee300 --severities moderate,severe \
  --margins 1.25 --budget 0 --max-k 12 --min-k 7 --scenarios 6 --tag uncoupled \
  > "$U/logs/E2b_rules_uncoupled.log" 2>&1 &
P1=$!

$PY e2b_service_model_check.py --topos ieee118,ieee300 --severities moderate,severe \
  --margins 1.25 --budget 6 --max-k 12 --min-k 7 --scenarios 4 --tag coupledB6 \
  > "$U/logs/E2b_rules_coupledB6.log" 2>&1 &
P2=$!

( for topo in ieee118 ieee300; do
    for m in 1.15 1.25 1.50; do
      echo "=== E3 moderate eval $topo/moderate/$m $(date +%H:%M:%S) ==="
      $PY e3_run.py --stage eval --budget 6 --topo $topo --severity moderate \
        --margin $m --scenarios 20 --max-k 12 \
        > "$U/logs/E3_eval_mod_${topo}_${m}.log" 2>&1
      echo "  rc=$?"
    done
  done ) &
P3=$!

( for topo in ieee118 ieee300; do
    for m in 1.15 1.25 1.50; do
      echo "=== E3 moderate eval/valid $topo/moderate/$m $(date +%H:%M:%S) ==="
      $PY e3_run.py --stage eval --budget 6 --topo $topo --severity moderate \
        --margin $m --scenarios 20 --max-k 12 --valid-seeds \
        > "$U/logs/E3_eval_mod_valid_${topo}_${m}.log" 2>&1
      echo "  rc=$?"
    done
  done ) &
P4=$!

wait $P1; echo "B1 done rc=$? $(date +%H:%M:%S)"
wait $P2; echo "B2 done rc=$? $(date +%H:%M:%S)"
wait $P3; echo "B3 done rc=$? $(date +%H:%M:%S)"
wait $P4; echo "B4 done rc=$? $(date +%H:%M:%S)"

echo "=== merging ==="
$PY - <<PYEOF
import pandas as pd, glob
from pathlib import Path
d = Path("$U/results/E3_budget_coupled")
for stem, out in (("episodes__", "episodes.csv"), ("episodes_valid__", "episodes_valid.csv")):
    parts = sorted(glob.glob(str(d / (stem + "*.csv"))))
    if not parts: continue
    df = pd.concat([pd.read_csv(p) for p in parts], ignore_index=True)
    df.to_csv(d / out, index=False)
    print(out, "rows:", len(df))
    print(df.groupby(["topology","severity","capacity_margin"]).size().to_string())
PYEOF
echo "=== stage B done $(date -Is) ==="
