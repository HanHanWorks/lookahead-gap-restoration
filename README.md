Reproduction package accompanying the manuscript:

**How much lookahead is worth having? An exactly computable value-and-accessibility criterion  
for restoration-ordering benchmarks** — submitted to *Sustainable Energy, Grids and Networks*.

This repository carries the artifacts listed in Appendix D of the paper's supplementary  
material: every number in the paper is traceable to a file here, and each claim names the file  
and the command that reproduces it.

## What this package contains

- `supp_code/` — the experiment, evaluation and figure code of the paper, including the  
  subset dynamic program that defines the lookahead gap, the attribution decomposition, the  
  identifiability pre-check, and the timing harness
- `experiment_data/` — the released records: the action-set and capacity-rule artifacts, the  
  frozen evaluation records of both protocols (9,600 episodes and 147,132 decision steps under  
  the main protocol; 9,600 episodes and 135,297 steps under the legacy protocol), the stepwise  
  oracle records behind Section 5.3, the twelve trained models, and the timing measurements
- `data_v2/` — the depth-curve dynamics and model artifacts
- `supp_results_2026-09-13/` — the four-rule capacity sweep of Section 6.2, the phase records  
  of Section 5.6, the rolling and depth-profile records of Section 5.5, the third-system  
  records of Section 5.8, the per-episode head-to-head records of Section 5.7, and the  
  dynamic-program validation logs of Appendix B
- `figures/` — the nine figures of the paper, each regenerated from the released tables by  
  `supp_code/make_figures_submission.py`; `figures/MANIFEST.txt` names the input file of every  
  panel
- `repro/` — `claims_evidence.csv` (one row per claim, naming the section, the assumption it  
  rests on, the code that produces it, the command that reproduces it and its status),  
  `session_info.txt` (the frozen commit, the random seeds and the SHA-256 digest of every  
  released file), and `FREEZE.sha256`
- `external_data/benchmark_topologies/ieee118.json` — the IEEE 118-bus case used by the  
  floor-saturation count of Section 6.1
- the manuscript and supplementary sources in Markdown, which the claims table cites by name

## How to reproduce

```bash
pip install -r requirements.txt
make reproduce     # regenerates every table and every figure
make check         # verifies the frozen manifest
```

`make reproduce` runs the P0/P1 recomputation and then `supp_code/make_figures_submission.py`,  
which rebuilds all nine figures from the released tables. `make check` re-hashes every  
released file against `repro/FREEZE.sha256`.

## What is intentionally not included

- **training console logs** (`supp_results_2026-09-13/logs/E3_train_*.log`, 13 files of about  
  128 MB in total): no claim, no Appendix B row and no Appendix D item depends on them
- **the earlier-stage scripts of `code/`**: 15 of their 17 modules hard-wire paths into the  
  working tree of the companion study, which is a different manuscript and is not released  
  here; no claim in `repro/claims_evidence.csv` refers to them
- **raw climate, geospatial and scenario assets of the companion study**: those belong to a  
  different manuscript and are not needed here
- the publisher's LaTeX class files, the internal audit reports of the drafting process, and  
  the typeset manuscript sources

## One caveat about the shell scripts

The shell scripts under `supp_code/` and `data_v2/` (`run_*.sh`, `train_remaining.sh`,  
`run_eval_all.sh`) record how the training and evaluation runs were dispatched to the compute  
node. They are kept for provenance, but the host, the login and the paths in them are  
placeholders (`$COMPUTE_NODE`, `$REMOTE_USER`, `$REMOTE_HOME`), so they are not runnable as  
they stand. Everything needed to *reproduce* the reported numbers runs locally through  
`make reproduce`.

## Environment

The experiments were run on one 16-core host with a single NVIDIA RTX 4090 D, Python 3.13.12,  
and the package versions recorded in `repro/session_info.txt` (also stated in Appendix C of the  
supplementary material). Timings exclude environment advancement and are within-machine only;  
their absolute values should not be transferred to other hardware.

## Sanitisation

The release was produced from the authors' working tree by  
`supp_code/build_github_release_2026-09-18.py`. Local account paths, the internal compute  
node's address and login, and private-volume paths were replaced with placeholders before  
publication; `docs/SANITIZATION.md` records every substitution and the residual scan that  
verifies none survived.

## Licence

MIT — see `LICENSE`. The IEEE 118-bus and IEEE 300-bus cases are redistributed here in the  
form used by the paper; the underlying test systems are public.


