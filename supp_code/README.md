# SEGAN 补充实验统一工作区

**位置**：`$REMOTE_HOME/segan/SEGAN_SUPP_2026-09-13/`（服务器 $COMPUTE_NODE）
**建立**：2026-09-13
**用途**：B+C 合并方案的全部补充实验（E1–E5），统一收纳代码、日志、结果与模型。

---

## 1. 目录结构

```
SEGAN_SUPP_2026-09-13/
├── README.md                 本文件：清单、复现命令、结果索引
├── code/                     全部实验脚本（本工作区自包含，不修改原有工程）
│   ├── segan_common.py       公共库：路径发现、环境构造、InstanceView、DP
│   ├── budget_coupled.py     E3：预算耦合环境 + 在线深度-k 前瞻智能体
│   ├── dcopf_service.py      E2：DC-OPF 服务评估器（相图的"求值成本"轴）
│   ├── e1_depth_curve.py     E1：深度-k 前瞻曲线 Γ_k
│   ├── e2_phase_diagram.py   E2：学习收益相图（预算 × 裕度）
│   ├── e2b_service_model_check.py  E2b：服务模型符号检查（max-flow vs DC-OPF）
│   ├── e3_run.py             E3：训练 / 评估 / 合并 / 验证
│   ├── e4_timing_ext.py      E4：时延基准扩展（含深度-k 在线代价）
│   ├── e5_third_topology.py  E5：第三算例（拓扑 + 动作集工件）
│   ├── inspect_coupled.py    一次性诊断工具
│   ├── probe_env_speed.py    环境步进吞吐诊断
│   └── run_e3_train.sh       E3 训练驱动（线程受限、并行 3）
├── logs/                     每个实验一个日志（nohup）
├── models/                   E3 重训的 12 个 DQN（b6 预算）
├── meta/
│   ├── env_snapshot.txt      环境版本快照
│   └── frozen/               冻结的 Γ_LA 参照文件（用于交叉校验）
└── results/
    ├── E1_depth_curve/       Γ_k 曲线
    ├── E2_phase_diagram/     相图 + 服务模型检查
    ├── E3_budget_coupled/    预算耦合训练/评估
    ├── E4_timing/            时延表
    └── E5_third_topo/        第三算例工件
```

**与被复用工程的关系（只读）**

| 路径 | 内容 |
|---|---|
| `~/segan/algorithm/enhanced_recovery_env.py` | 基础环境 `EnhancedDisasterRecoveryEnv` |
| `~/segan/IJEPES_major_revision_2026-09-07/code/run_capacity_aware_restoration.py` | `CapacityAwareEnv`、`CriticalityTrainingEnv`、确定性策略类 |
| `~/segan/IJEPES_major_revision_2026-09-07/external_data/benchmark_topologies/` | 算例 JSON |
| `~/segan/IJEPES_major_revision_2026-09-07/data_derived/action_sets/` | 动作集工件 |
| `~/segan/raw_data/climate/` | 气候输入 |
| `~/segan/SEGAN_submission_2026-09/` | 主协议代码、12 个原始模型、9,600 episodes |

本工作区的脚本**不修改**上述任何文件；`segan_common.py` 仅做导入复用。

---

## 2. 环境

`~/miniconda3/envs/segan`（版本清单见 `meta/env_snapshot.txt`）。
并行作业前必须限制 BLAS 线程，否则 N 进程 × 16 线程会把 16 核机器拖慢约 40 倍：

```bash
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
```

---

## 3. 实验清单与复现命令

### E1 · 深度-k 前瞻曲线 Γ_k

π_k = 前瞻 k 步（精确）＋ 其余退回近视规则；Γ_k = J(π_k) − J(π_0)，π_0 为单步近视规则。
内置校验：Γ_0 = 0；无耦合下 Γ_1 = 0；Γ_K = Γ_LA（与冻结文件逐位比对）。

```bash
cd code
python e1_depth_curve.py --scenarios 20 --max-k 12 \
    --frozen ../meta/frozen/lookahead_gap_new.csv          # 无耦合
python e1_depth_curve.py --budget 6 --scenarios 20 --max-k 12   # 预算耦合 B=6
```
产出：`results/E1_depth_curve/depth_curve_{uncoupled,coupled_B6}.csv` + `_by_condition.csv`。

### E2 · 学习收益相图

```bash
python e2_phase_diagram.py --scenarios 12 --max-k 12
python e2b_service_model_check.py --topos ieee118 --budget 4 --scenarios 4
```
产出：`phase_scenarios.csv`、`phase_by_condition.csv`、`service_model_sign_check.csv`。

### E3 · 预算耦合下的学习排序器（硬前置）

```bash
cd ..
PAR=3 bash code/run_e3_train.sh          # 重训 12 个模型（2 拓扑 × 3 种子 × 2 臂）
cd code
python e3_run.py --stage validate --budget 6            # 智能体正确性自检
python e3_run.py --stage eval --budget 6 --scenarios 20 # 逐条件评估
python e3_run.py --stage merge                          # 合并
```
产出：`models/*_b6_*.zip`、`results/E3_budget_coupled/episodes*.csv`、`validate_agent_b6.csv`。

**正确性自检（重要）**：网上深度-k 策略的实测 AUC 必须等于离线 DP 值
`auc_myopic + Γ_k`。首轮自检暴露了一个真实缺陷：预算耦合下 episode 跑满 25 步，
而原 AUC 代码用 `rec[1:25]` 丢掉第 25 步，使实测系统性偏低 `r_B`。已修正为
`rec[1:26]` 并补齐填充。

### E4 · 时延基准扩展

```bash
python e4_timing_ext.py --budget 6 --scenarios 12   # 预算耦合协议
python e4_timing_ext.py --scenarios 12              # 无耦合协议
```
产出：`results/E4_timing/timing_ext_{uncoupled,budget6}.csv`。

### E5 · 第三算例（可选）

```bash
python e5_third_topology.py --case case_illinois200
python e1_depth_curve.py --topos case_illinois200 --scenarios 20 --max-k 12
python e2_phase_diagram.py --topos case_illinois200
```
产出：拓扑 JSON、动作集工件、`results/E5_third_topo/e5_report_*.json`。

---

## 4. 关键定义（与论文公式对应）

| 符号 | 定义 | 实现 |
|---|---|---|
| ℓ(S) | `max(0, base_service − maxflow(all_broken \ S))` | `InstanceView.lost` |
| r(S) | 恢复率 % = (ℓ(∅)−ℓ(S))/ℓ(∅)×100 | `InstanceView.rec` |
| J(π) | AUC@25 | `e3_run.run_episode` |
| π_k | 前瞻 k 步 + 近视尾部 | `LookaheadKAgent(depth=k)` |
| Γ_k | J(π_k) − J(π_0) | `uncoupled_curve` / `coupled_curve` |
| Γ_LA | Γ_K（无耦合）或 Γ_B（预算 B） | 同上末项 |

**口径说明（易混淆，务必注意）**：参考策略是 π_0 = 单步近视规则，故 Γ_0 ≡ 0。

* 无耦合协议下 **Γ_1 = 0**（深度-1 前瞻无法超越近视规则），已逐实例验证；
* 预算耦合协议下 **Γ_1 可以 > 0**（资源稀缺使"多做一步前瞻"本身就有价值），
  例如 ieee118/severe/m1.25 seed 4119 的 Γ_1 = 111.67、Γ_6 = 120.13。

---

## 5. 运行状态与结果索引

见 `results/` 各子目录内的 `*.json` 摘要文件与本目录日志。
最终汇总（含关键数字）由本地 `SEGAN_submission_2026-09/supp_results_2026-09-13/` 镜像保存。
