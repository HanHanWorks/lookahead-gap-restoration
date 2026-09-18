#!/bin/bash
# Post-training driver: waits for the 12 budget-coupled models, then runs
#   E3 evaluation (8 methods x 6 severe conditions)  -> episodes
#   E3 merge
#   E4 timing extension (budget-coupled + uncoupled)
#   E5 third topology + its depth curve
# Thread-limited; safe to nohup.
set -u
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 TORCH_NUM_THREADS=2

U=~/segan/SEGAN_SUPP_2026-09-13
CODE=$U/code
LOGS=$U/logs
MODELS=$U/models
PY=~/miniconda3/envs/segan/bin/python
cd "$CODE"

echo "=== post-training driver start $(date -Is) ==="

# 1) wait for the full model set (max 3 h)
for i in $(seq 1 360); do
  n=$(ls "$MODELS" 2>/dev/null | grep -c '_100000.zip')
  if [ "$n" -ge 12 ]; then break; fi
  if [ $((i % 10)) -eq 1 ]; then echo "[wait] models $n/12"; fi
  sleep 30
done
n=$(ls "$MODELS" 2>/dev/null | grep -c '_100000.zip')
echo "[models] $n/12 present"
ls -la "$MODELS"

# 2) E3 evaluation per condition (severe, all margins, both topologies)
for topo in ieee118 ieee300; do
  for margin in 1.15 1.25 1.50; do
    echo "=== E3 eval $topo/severe/$margin $(date +%H:%M:%S) ==="
    "$PY" e3_run.py --stage eval --budget 6 --topo "$topo" --severity severe \
        --margin "$margin" --scenarios 20 --max-k 12 \
        > "$LOGS/E3_eval_${topo}_severe_${margin}.log" 2>&1
    echo "  rc=$?"
  done
done

# 3) merge the per-condition files
"$PY" e3_run.py --stage merge >> "$LOGS/E3_eval_merge.log" 2>&1
echo "=== merged ==="

# 4) E4 timing
"$PY" e4_timing_ext.py --budget 6 --scenarios 12 > "$LOGS/E4_timing_b6.log" 2>&1
"$PY" e4_timing_ext.py --scenarios 12           > "$LOGS/E4_timing_uncoupled.log" 2>&1
echo "=== E4 done ==="

# 5) E5 third topology + depth curve
"$PY" e5_third_topology.py --case case_illinois200 > "$LOGS/E5_build.log" 2>&1
if grep -q '"action_set_flow_share"' "$LOGS/E5_build.log"; then
  "$PY" e1_depth_curve.py --topos case_illinois200 --scenarios 12 --max-k 12 \
      > "$LOGS/E5_depth_curve.log" 2>&1
  "$PY" e1_depth_curve.py --topos case_illinois200 --severity severe \
      --budget 6 --scenarios 12 --max-k 12 > "$LOGS/E5_depth_curve_b6.log" 2>&1
fi
echo "=== E5 done ==="

echo "=== post-training driver end $(date -Is) ==="
find "$U/results" -type f -name '*.csv' | sort
