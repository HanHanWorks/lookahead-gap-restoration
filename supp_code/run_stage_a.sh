#!/bin/bash
# Stage A of the follow-up batch.
#
#  1) E1 protocol-controlled pair: the same instance-selection rule (K >= 7) for
#     both budgets. The first E1 run filtered on K > budget, which gave the two
#     protocols different samples (moderate conditions shared only 11 of 20
#     seeds), so a protocol difference was confounded with an instance difference.
#  2) E5 budget-coupled depth curve for the third topology. The earlier attempt
#     died on "--severity" (the flag is --severities).
set -u
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1

U=~/segan/SEGAN_SUPP_2026-09-13
PY=~/miniconda3/envs/segan/bin/python
cd "$U/code" || exit 1

echo "=== E1 uncoupled, min_k=7 (controlled) $(date +%H:%M:%S) ==="
"$PY" e1_depth_curve.py --budget 0 --min-k 7 --scenarios 20 --max-k 12 \
  --tag uncoupled_mk7 --frozen ../meta/frozen/lookahead_gap_new.csv \
  > "$U/logs/E1_uncoupled_mk7.log" 2>&1
echo "  rc=$?"

echo "=== E1 coupled B=6, min_k=7 (controlled) $(date +%H:%M:%S) ==="
"$PY" e1_depth_curve.py --budget 6 --min-k 7 --scenarios 20 --max-k 12 \
  --tag coupled_B6_mk7 > "$U/logs/E1_coupled_B6_mk7.log" 2>&1
echo "  rc=$?"

echo "=== E5 case_illinois200, coupled B=6 $(date +%H:%M:%S) ==="
"$PY" e1_depth_curve.py --topos case_illinois200 --severities severe \
  --budget 6 --scenarios 12 --max-k 12 --tag coupled_B6_case_illinois200 \
  > "$U/logs/E5_depth_curve_b6.log" 2>&1
echo "  rc=$?"

echo "=== stage A done $(date -Is) ==="
ls -la "$U/results/E1_depth_curve/"
