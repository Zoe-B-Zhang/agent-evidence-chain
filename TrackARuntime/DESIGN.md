# TrackARuntime 设计说明

> 本文档说明系统的架构边界、哪些是 mock、以及扩展方向。

## 1. 架构概览

```text
CLI (cli.py)
  ├── run          → LoopEngine → ToolExecutor → TraceCollector → state.json + trace.json
  ├── harness      → pipeline → guardrails → harness-report.json (+ rollout-state.json)
  ├── eval         → runner → scenarios.json → evaluation-report.json/md
  └── demo-*       → 独立 trace 演示
```

## 2. 故意 mock 的部分

为了让教学聚焦在“控制面 / 边界 / 交付 / 门禁 / 运维”五条生命线，以下能力被有意 mock：

| 能力 | mock 方式 | 原因 |
|---|---|---|
| LLM 推理 | `MockLLMClient` / 硬编码 plan | 避免引入 API key 与网络依赖，保持可离线运行 |
| 真实 shell/容器 | `docker_exec` 返回固定字符串 | 避免误操作破坏宿主环境 |
| 真实测试执行 | `run_tests` 按 round 硬编码结果 | 让学习者关注 observe 语义而非测试框架 |
| 真实流量切换 | `rollout_controller.apply_traffic` 只改 JSON state | 避免依赖真实负载均衡 |

这些 mock 点都通过**可插拔接口**保留替换为真实实现的空间（见第 4 节）。

## 3. 已真实实现的部分

- Agent 循环状态机（`Phase` enum、history、round、checkpoint/resume）。
- 工具 allowlist、schema 校验、HITL、RETRYABLE 退避与调用审计（`TraceEvent`）。
- 只读沙箱 `read_file` / `grep`（相对项目根）。
- 四层上下文、模型路由、token/cost 估算、rate-limit stub、metrics 证据。
- Prompt 版本化、灰度、护栏、rollback 状态机。
- Golden scenarios eval、taxonomy 修复建议、baseline auto、轨迹 eval 工具。
- unittest + GitHub Actions CI + Dockerfile。

## 4. 扩展方向

| 方向 | 推荐接入点 |
|---|---|
| 接入真实 LLM | 实现 `m1_m2.llm_client.LLMClient` 并在 `LoopConfig` 注入 |
| 真实文件/检索 | `read_file` / `grep` 已支持只读沙箱；可扩展写工具 |
| 模型路由与成本 | 在 `m3.model_router` / `m3.token_counter` 实现真实策略 |
| CI 门禁 | `.github/workflows/ci.yml` 已包含 eval / harness gate |
| 真实部署 | 使用 Phase E 提供的 `Dockerfile` 容器化运行 |

### 4.1 接入 OpenAI（教学扩展，默认不实现）

本项目**故意不**捆绑 `openai` SDK，以免引入 API key 与网络依赖。若要接真实模型：

1. 新建 `class OpenAIClient(LLMClient)`，在 `generate_plan` 中调用 Chat Completions。
2. 通过环境变量读取 `OPENAI_API_KEY`；缺失时回退到 `MockLLMClient`。
3. 在 `cli.py` 为 `--llm` 增加 `openai` 选项并注入 `LoopConfig.llm_client`。
4. 将 token/cost 写入 `m1_m2.metrics` / trace 扩展字段。

CLI 当前仅支持 `--llm mock`；默认不传则使用硬编码 plan（与改造前行为兼容）。

## 5. 安全边界

- 默认不执行任何真实系统命令或网络调用。
- 危险工具（如 `docker_exec`）保留 `confirmed=True` HITL 接口，可通过 `--require-hitl` 开启。
- 所有证据文件默认写入 `m{1..4}/evidence/`，不应手动修改。
