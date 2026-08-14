# TrackARuntime — 自检用 Anchor 子项目

本目录是仓库内的 **Anchor 子项目**：用 mock CLI 对 [`track-a-notes`](../track-a-notes/) 主轴中的 module 知识点做**教学模拟**，重现类似 PR 现场，供学习者**自测指读**（`state.json` / `trace.json` / `metrics` 等）。

**学习主轴**在 [`track-a-notes/`](../track-a-notes/)（curriculum · `module-01`…`05` · Case/OSS PR · rubric）。K 点定义、PR 分析与 Exit 自评均在主轴完成；本目录**不阅卷、不认证合格**。

K 点「主轴材料 vs Anchor 模拟」对照表 → 根目录 [`README.md` · 主轴 K 点](../README.md#主轴-k-点)。

## 与主轴的对应

| 本目录 | 对应主轴模块 | 说明 |
|---|---|---|
| `m1_m2/` | M1 控制面 + M2 工具边界 | `run`、`demo-*` |
| `m3/` | M3 配置交付 | `harness` |
| `m4/` | M4 质量门禁 | `eval` |
| — | M5 运维响应 | 无代码；见 `track-a-notes/module-05/` |

物证指读 walkthrough → [`USAGE.md` §2.1](../USAGE.md#21-证据文件怎么用m1m2-示例) · 设计边界 [`DESIGN.md`](DESIGN.md)

## 目录结构

```text
TrackARuntime/
├── cli.py
├── requirements.txt
├── Dockerfile
├── DESIGN.md
├── scripts/self_check.py
├── tests/
├── m1_m2/                 # 控制面 + 工具边界 + 上下文/metrics
├── m3/                    # 配置交付 + 路由/token/cost/限流
└── m4/                    # 质量门禁 + baseline/trace_eval/judge
```

## 快速开始

```powershell
cd TrackARuntime
pip install -r requirements.txt
python scripts/self_check.py

# M1+M2（跑完后见下文「一次 run 之后」）
python cli.py run --task "fix failing test" --llm mock
python cli.py run --task "container death" --simulate-container-death 1
python cli.py demo-allowlist --tool rm_rf
python cli.py demo-no-output-hang --idle-timeout 1

# M3
python cli.py harness --prompt v2 --gray-percent 10
python cli.py harness --reset-rollout
python cli.py harness --prompt v2 --gray-percent 10 --watch

# M4
python cli.py eval --baseline auto
python -m unittest discover tests
```

### M4 Eval 数字真源

> 其他文档应引用本节，避免 20/22 场景或 0.5/0.45 baseline 混用。

| 项 | 当前值（2026-08-09） |
|---|---|
| 场景总数 | **22**（S01–S22） |
| 通过 / 失败 | **10 pass / 12 fail**（教学 stub `_simulate`） |
| 成功率 | **45.5%**（10÷22） |
| CI baseline | **`0.45`**（[`.github/workflows/ci.yml`](../.github/workflows/ci.yml)） |
| 本地校准 | `--baseline auto`（读 `m4/evidence/evaluation-report.json` 历史 `success_rate`） |

**生产扩展场景绑定**：

| ID | failure_code | case_ref |
|---|---|---|
| S21 | `STALE_INDEX` | case-11（RAG 旧索引） |
| S22 | `JUDGE_BIAS` | case-15（Judge 误判 regression） |
| S23 | `RETRIEVAL_OK_GEN_FAIL` | 计划给 oss-9415；**尚未实现** |

```powershell
python cli.py eval --baseline 0.45   # 与 CI 一致
```

### 常用 run 选项

| 选项 | 作用 |
|---|---|
| `--llm mock` | 注入 MockLLMClient |
| `--checkpoint-dir PATH` | 每轮写 checkpoint |
| `--resume-from PATH` | 从 checkpoint 恢复 |
| `--require-hitl` | 危险工具需 confirmed（loop 内会 Fatal） |
| `--max-retries` / `--retry-backoff-s` | RETRYABLE 退避 |

### Docker

```powershell
docker build -t agent-evidence-chain .
docker run --rm agent-evidence-chain
```

## 证据路径（默认）

> **策略**：evidence 由 CLI 自动生成，**请勿手改**。仓库内文件为教学指读样本；本地 `run`/`harness`/`eval` 会更新或新增物证。提交 PR 时只保留与改动相关的 evidence diff。详见根目录 [`CONTRIBUTING.md`](../CONTRIBUTING.md#证据文件evidence策略)。

| 模块 | 命令 | 证据 |
|---|---|---|
| M1+M2 | `cli.py run` | `m1_m2/evidence/<run_id>/` + `metrics-<run_id>.json` |
| M2 demo | `demo-no-output-hang` | `m1_m2/evidence/m2-8448-demo/` |
| M3 | `cli.py harness` | `m3/evidence/harness-report.json` |
| M3 L3 | `harness --watch` | `m3/evidence/rollout-state.json` |
| M4 | `cli.py eval` | `m4/evidence/evaluation-report.md` |

每次 run 生成新 `<run_id>`，非固定标准答案。

**Evidence 提交策略**：仓库内保留了一组**文档对照用示例**；本地自测可用 `--out <目录>` 避免改动已提交物证。详见根目录 [`CONTRIBUTING.md`](../CONTRIBUTING.md#evidence物证策略)。

### 一次 `run` 之后

命令成功只打印路径；**学习动作在打开文件之后**。完整 checklist 见 [`USAGE.md` §2.1](../USAGE.md#21-证据文件怎么用m1m2-示例)。

| 文件 | 回答的问题 |
|---|---|
| `state.json` | 第几轮、什么 phase、**为何** DONE / replan / fatal |
| `trace.json` | 每步调了什么 **tool**、输入输出、latency |
| `metrics-<run_id>.json` | token / cost / route **估算**（教学 stub） |

## 自检命令速查（对照主轴 module）

下列命令在主轴 [`module-XX/issues.md`](../track-a-notes/module-01/issues.md) 中有 PR 对照说明；跑通后物证供自评，**是否过关**见主轴 rubric。

| 主轴模块 | 自检命令（示例） |
|---|---|
| M1 | `run --llm mock`；`--simulate-container-death`；`stuck loop` / `pseudo replan`；checkpoint |
| M2 | `demo-allowlist`；`demo-no-output-hang`；`--require-hitl` |
| M3 | `harness --prompt v2 --gray-percent 10`；`--watch` |
| M4 | `eval --baseline auto` |

## 与 OSS Issue 的绑定

见 [`track-a-notes/tutor/README.md`](../track-a-notes/tutor/README.md) 中 **Runtime 任务** 列（将主轴 PR 阅读与本目录命令配对）。
