#!/bin/bash
# E3: retrain the 12 DQN models under the reconnection budget (B=6).
# 2 topologies x 3 seeds x 2 arms (surrogate / trueobj), PAR jobs in parallel.
set -u
# Single-threaded BLAS: prevents N workers x 16 BLAS threads from thrashing the
# 16-core box (this was the cause of a ~60x training slowdown on the first try).
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export CODE=~/segan/SEGAN_SUPP_2026-09-13/code
export LOGS=~/segan/SEGAN_SUPP_2026-09-13/logs
export PY=~/miniconda3/envs/segan/bin/python
export BUDGET="${BUDGET:-6}"
export TIMESTEPS="${TIMESTEPS:-100000}"
export TORCH_NUM_THREADS="${TORCH_NUM_THREADS:-2}"
PAR="${PAR:-4}"

mkdir -p "$LOGS"
echo "=== E3 training start $(date -Is) budget=$BUDGET timesteps=$TIMESTEPS par=$PAR ==="

for arm in surrogate trueobj; do
  for topo in ieee118 ieee300; do
    for seed in 42 43 44; do
      echo "$arm $topo $seed"
    done
  done
done | xargs -n 3 -P "$PAR" bash -c '
  arm="$1"; topo="$2"; seed="$3"
  cd "$CODE" || exit 1
  log="$LOGS/E3_train_${topo}_${arm}_${seed}.log"
  echo "[start $(date +%H:%M:%S)] arm=$arm topo=$topo seed=$seed" >> "$log"
  "$PY" e3_run.py --stage train-one --arm "$arm" --topo "$topo" \
      --seed "$seed" --budget "$BUDGET" --timesteps "$TIMESTEPS" >> "$log" 2>&1
  echo "[end   $(date +%H:%M:%S)] rc=$?" >> "$log"
' _

echo "=== E3 training done $(date -Is) ==="
ls -la ~/segan/SEGAN_SUPP_2026-09-13/models/
