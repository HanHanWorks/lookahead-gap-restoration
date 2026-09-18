#!/bin/bash
# Re-run the head-to-head evaluation after the K < B tail-coefficient fix.
#
# Bug: LookaheadKAgent used tail_coef = 24.5 - B, but when K < B the budget never
# binds and the correct coefficient is 24.5 - K. In that regime the agent optimised
# the wrong objective and scored BELOW the plain myopic rule -- which is impossible
# for a correct depth-k rollout, since the myopic path is one of its candidates.
# The contamination is confined to the ALL-SAMPLE head-to-head (`episodes__*`),
# because the aligned variant (`--valid-seeds`) selects only instances with K > B.
set -u
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1

U=~/segan/SEGAN_SUPP_2026-09-13
PY=~/miniconda3/envs/segan/bin/python
R=$U/results/E3_budget_coupled
cd "$U/code" || exit 1

# archive the contaminated files
mkdir -p "$R/_pre_tailfix"
for f in "$R"/episodes__*.csv "$R"/episodes.csv; do
  [ -e "$f" ] && mv "$f" "$R/_pre_tailfix/"
done
echo "archived pre-fix episodes: $(ls "$R/_pre_tailfix" | wc -l) files"

for topo in ieee118 ieee300; do
  for sev in severe moderate; do
    for m in 1.15 1.25 1.50; do
      echo "=== eval $topo/$sev/$m $(date +%H:%M:%S) ==="
      "$PY" e3_run.py --stage eval --budget 6 --topo "$topo" --severity "$sev" \
        --margin "$m" --scenarios 20 --max-k 12 \
        > "$U/logs/E3_eval_${topo}_${sev}_${m}.log" 2>&1
      echo "  rc=$?"
    done
  done
done

"$PY" e3_run.py --stage merge >> "$U/logs/E3_eval_merge.log" 2>&1
echo "=== merge done ==="
cat "$R/e3_audit.json"
echo "=== re-run complete $(date -Is) ==="
