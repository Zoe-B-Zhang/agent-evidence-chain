# AI Assistant 开发求职 — Agent 指南（AI 编程助手版）

> 本文件面向需要在此仓库工作的 AI 编程助手。阅读前默认你对本项目一无所知。
> **展示名 / 项目全名**：**AI Assistant 开发求职 — 轨道 A（Residency v2）**（GitHub 仓库名 `agent-evidence-chain`）。**学习主轴**是 `track-a-notes/`；自检用 mock 子项目目录与边界**仅**在 [`STRUCTURE.md`](STRUCTURE.md) 展开，勿与仓库名、展示名并列理解。

## 1. 项目概览

这是一个教学/能力验证型的 Python Anchor Project，用于演示 AI Agent 从开发到上线运维的 **五条工程生命线**：

| 模块 | 生命线 | 核心能力 | CLI 子命令 |
|---|---|---|---|
| M1+M2 | 控制面 / 工具边界 | Agent loop、trace、allowlist、schema、HITL、checkpoint | `run`, `demo-*` |
| M3 | 配置交付 | Prompt 版本、灰度发布、护栏、回滚、模型路由/成本 stub | `harness` |
| M4 | 质量门禁 | 场景回归、taxonomy 建议、baseline auto、轨迹 eval | `eval` |
| M5* | 运维响应 | 只在 `track-a-notes/` 中以 SOP/monitoring-layers 形式存在 | — |

> M5 没有代码落点；M6 作品集见根目录 `portfolio/`。

项目不是生产服务，而是一个**可运行的最小验证系统**。所有命令都会把执行证据写入 `TrackARuntime/m{1..4}/evidence/`，用于后续复盘与面试举证。

### 1.1 双层材料

| 层 | 路径 | 用途 |
|---|---|---|
| **Runtime** | `TrackARuntime/` | 自检模拟：loop / harness / eval（mock CLI + 物证） |
| **Notes** | `track-a-notes/` | **学习主轴**：课程、K 点、module-XX（PR 分析）、Case、SOP |

求职增强不新增 M6 工程模块，而以 **Production Extension Packs（P1–P6）** 回挂 M1–M5：见 `track-a-notes/curriculum/02-production-extension-packs.md`。对应 Case **10–18** + SOP 已落地；**可选 Runtime demo 尚未实现**——文档中出现的 `demo-llm-gateway` / `eval-rag` 等是规划命令，不要写成已存在 CLI。

## 2. 仓库结构

```text
.
├── README.md                    # 仓库总入口（中文）
├── AGENTS.md                    # 本文件
├── portfolio/                   # M6 模板 + 示例；personal/ 为本地成稿（gitignore）
├── temp/                        # 改进 handoff（非学习主路径）
├── .github/workflows/ci.yml     # CI：unittest → harness → eval
├── TrackARuntime/               # Anchor 自检子项目（M1–M4 模拟代码）
│   ├── cli.py                   # 统一 CLI 入口
│   ├── requirements.txt         # PyYAML
│   ├── Dockerfile               # 容器化
│   ├── DESIGN.md                # mock 边界与扩展点
│   ├── scripts/self_check.py    # 环境自查
│   ├── tests/                   # unittest
│   ├── m1_m2/                   # M1 控制面 + M2 工具边界
│   │   ├── loop_engine.py
│   │   ├── tool_executor.py     # allowlist / schema / retry / HITL / 真实只读工具
│   │   ├── llm_client.py        # LLMClient + MockLLMClient
│   │   ├── context_manager.py   # 四层上下文
│   │   ├── metrics.py           # latency/token/cost 证据
│   │   ├── trace.py
│   │   ├── errors.py
│   │   └── evidence/
│   ├── m3/                      # M3 配置交付 + 平台 stub
│   │   ├── pipeline.py
│   │   ├── guardrails.py
│   │   ├── rollout_controller.py
│   │   ├── model_router.py
│   │   ├── token_counter.py
│   │   ├── cost_monitor.py
│   │   ├── rate_limiter.py
│   │   ├── prompts/
│   │   └── evidence/
│   └── m4/                      # M4 质量门禁
│       ├── runner.py
│       ├── baseline.py
│       ├── trace_eval.py
│       ├── golden_dataset.py
│       ├── judge.py
│       ├── scenarios.json
│       ├── failure_taxonomy.md
│       └── evidence/
├── track-a-notes/               # 学习笔记、课程、案例库（非代码主线）
│   ├── curriculum/              # 00 世界观 → 01 教案 → 02 生产扩展
│   ├── case-library/            # Case 01–18 + OSS + SOP
│   ├── module-01 … 05/          # knowledge / issues / day 笔记
│   ├── KNOWLEDGE-MAP.md         # K 点索引
│   └── interview/               # 面试 drill（含 M6 demo 计时）
└── _archive/                    # 归档资料
```

## 3. 技术栈

- **语言**：Python 3.11+
- **依赖**：仅标准库 + **PyYAML 6.0+**（见 `TrackARuntime/requirements.txt`）
- **CI**：GitHub Actions（`.github/workflows/ci.yml`）
- **测试**：标准库 `unittest`（`TrackARuntime/tests/`）
- **安装**：
  ```powershell
  cd TrackARuntime
  pip install -r requirements.txt
  python scripts/self_check.py
  ```

## 4. 构建与运行

### 4.1 环境准备

```powershell
cd TrackARuntime
pip install -r requirements.txt
python scripts/self_check.py
```

### 4.2 核心 CLI 命令

入口脚本：`TrackARuntime/cli.py`

```powershell
# M1+M2：Agent loop
python cli.py run --task "fix failing test" --llm mock
python cli.py run --task "container death" --simulate-container-death 1
python cli.py run --task "x" --require-hitl          # HITL 拦截 docker_exec
python cli.py run --task "fix failing test" --checkpoint-dir m1_m2/evidence/checkpoints

# M2 边界演示
python cli.py demo-allowlist --tool rm_rf
python cli.py demo-no-output-hang --idle-timeout 1

# M3：配置/灰度/护栏
python cli.py harness --prompt v2 --gray-percent 10
python cli.py harness --prompt v1 --gray-percent 0
python cli.py harness --reset-rollout
python cli.py harness --prompt v2 --gray-percent 10 --watch --promote-if-ready

# M4：质量门禁
python cli.py eval --baseline auto
python -m unittest discover tests
```

### 4.3 退出码约定

- `0`：成功 / gate 通过 / 护栏通过
- `1`：任务失败 / gate 失败 / 护栏失败但已记录报告
- `2`：Fatal 错误（如容器死亡、循环指纹重复、HITL 拒绝、空白 task、baseline/gray/max-rounds 越界、checkpoint 缺失或损坏）或 candidate 被锁定

## 5. 代码组织与模块划分

### 5.1 `m1_m2/` — 控制面 + 工具边界

- `LoopEngine`：`parse → plan → act → observe → replan`；支持 LLM 注入、checkpoint/resume。
- `ToolExecutor`：allowlist、schema 校验、RETRYABLE 退避、HITL；`read_file`/`grep` 真实只读沙箱。
- `llm_client.MockLLMClient`：默认离线 plan；OpenAI 扩展见 `DESIGN.md` §4.1。
- `context_manager` / `metrics`：四层上下文与 token/cost 证据。

### 5.2 `m3/` — 配置交付 + 平台 stub

- `pipeline` / `guardrails` / `rollout_controller`：原有 harness 灰度回滚。
- `model_router` / `token_counter` / `cost_monitor` / `rate_limiter`：教学 stub（无网络）。

### 5.3 `m4/` — 质量门禁

- `runner.py`：golden scenarios、taxonomy 修复建议、检索/生成拆分、baseline meta。
- `baseline.py`：`--baseline auto` 从历史报告校准。
- `trace_eval.py` / `golden_dataset.py` / `judge.py`：轨迹指标、数据集校验、Judge 接口（默认关闭）。

## 6. 开发约定

- **语言**：模块 docstring 和项目文档使用中文；代码标识符、类名、函数名使用英文。
- **类型注解**：使用 `from __future__ import annotations` 与 Python 3.11 语法（如 `str | None`）。
- **文件编码**：所有文本文件均为 UTF-8。
- **路径处理**：统一使用 `pathlib.Path`。
- **时间戳**：统一使用 `datetime.now(timezone.utc).isoformat()`。
- **JSON 输出**：统一 `indent=2`。
- **不要改动证据文件**：`*/evidence/` 由 CLI 生成，不应手动修改。
- **不要重命名模块**：`m1_m2`、`m3`、`m4` 是课程模块代号。

### 6.1 文档约定（Notes / Case）

- Case 文件对齐 `track-a-notes/case-library/cases/_TEMPLATE.md`（含元数据、现象、校准来源、SOP 摘要、学习记录）。
- 正式 SOP 放在 `track-a-notes/case-library/sops/`；Case 内只用「SOP 摘要」，不要写「SOP 草案」。
- 生产扩展 K 点回填时，同步：`module-0X/knowledge.md`、`module-0X/issues.md`、`KNOWLEDGE-MAP.md`、相关 Case/SOP 链接。
- Case 09 vs Case 10 都涉及 429：区分轴是 CTL（silent loop）vs Gateway/REL（quota-aware fallback），勿混写。
- PowerShell 改 Markdown 时避免在双引号/`@"..."@` 中使用反引号包裹指标名（会被吃掉）。

## 7. 测试说明

```powershell
cd TrackARuntime
python -m unittest discover tests
```

CLI 证据：
- `m1_m2/evidence/<run_id>/state.json` + `trace.json` + `metrics-<run_id>.json`
- `m3/evidence/harness-report.json` + `rollout-state.json`
- `m4/evidence/evaluation-report.json` + `evaluation-report.md`

## 8. 安全与边界注意事项

- **默认无网络、无真实 shell**：`docker_exec` / `run_tests` 仍为 mock；`read_file`/`grep` 仅项目根只读沙箱。
- **Allowlist + schema + HITL**：修改 `BASE_TOOL_SPECS` 需同步测试与文档。
- **容器死亡是模拟**：`--simulate-container-death` 只改 `_container_alive`。
- **依赖最小化**：仅 PyYAML；不要引入 openai/pytest 等。

## 9. 常见扩展点

- 新增 tool：在 `tool_executor.BASE_TOOL_SPECS` 注册。
- 接入真实 LLM：实现 `LLMClient`，见 `DESIGN.md` §4.1。
- 新增 guardrail：`m3/guardrails.py` + `pipeline.py`。
- 新增 eval 场景：编辑 `m4/scenarios.json`（含 `category`），失败码对齐 `failure_taxonomy.md`。
- 新增生产扩展 Case：先写 `_TEMPLATE.md` 对齐的 Case + SOP，再回填 K 点与 `case-library/README.md`；可选 Runtime 另开阶段，勿伪造已有 CLI。

## 10. 参考文档

- 项目目的：`README.md`（少改）
- **使用指引**：`USAGE.md`（学习路径、命令、Case 用法）
- **仓库组成**：`STRUCTURE.md`
- 设计边界：`TrackARuntime/DESIGN.md`
- TrackARuntime 命令：`TrackARuntime/README.md`
- 知识体系：`track-a-notes/curriculum/00-knowledge-system.md`
- 生产扩展：`track-a-notes/curriculum/02-production-extension-packs.md`
- K 点索引：`track-a-notes/KNOWLEDGE-MAP.md`
- 案例库：`track-a-notes/case-library/README.md`
- 失败分类：`TrackARuntime/m4/failure_taxonomy.md`
- Runtime 改进 handoff：`temp/IMPROVEMENT-PLAN.md`
- 知识/Case 落地 handoff：`temp/AGENT-ENGINEERING-KNOWLEDGE-IMPROVEMENT-PLAN.md`、`temp/AGENT-ENGINEERING-CASE-PACKET-PLAN.md`
