# 模块 2 学习指南：Tool Use + Trace

> **导师补充**：知识工程点 [`M2-K01–K05`](knowledge.md) · 精选 Issue [`M2-I01–I04`](issues.md) · 评分 [`rubric.md`](rubric.md)

## 本模块在系统中的位置

| | |
|---|---|
| **生命线** | ② **工具边界** — 副作用受控、执行可审计 |
| **依赖** | M1（act/observe 在 loop 内） |
| **主证据** | `trace.json` |
| **体系详述** | [`KNOWLEDGE-SYSTEM.md` §7 M2](../curriculum/00-knowledge-system.md) · [`COURSE.md` 第 2 课](../curriculum/01-course.md) |

## 原理（3 分钟版）

Tool = 带副作用的受控 API。Trace = Agent 场景的分布式链路追踪。

**三层防御（当前 Runtime）**：

1. Allowlist（调用前）
2. Schema 校验（`ToolSpec`）
3. HITL（`--require-hitl` + `dangerous`）

Dry-run 仍为 L3 概念；分路径 timeout **有配置、强制中断未接线**（见 knowledge M2-K04）。

| AI 概念 | 系统等价 |
|---|---|
| Tool allowlist | 命令白名单 / sudoers |
| Schema + HITL | API 校验 + 人工审批 |
| Trace span | OpenTelemetry span |
| 分路径 timeout | 按 API 类型的 SLA |

## OSS 阅读清单

1. **Cline**：`src/core/prompts/system.ts` + tool approval 流程
2. **aider**：命令执行与 git 集成
3. **Logfire / TruLens**：step 级 logging 模式

## 三日校准（导师指定 Issue）

| 天 | 任务 | 链接 |
|---|---|---|
| Day1 主修 1 | 30s timeout vs 长命令 | [Cline #7355](https://github.com/cline/cline/issues/7355) · [M2-I01](issues.md) |
| Day1 主修 2 | 无输出命令 hang | [Cline #8448](https://github.com/cline/cline/issues/8448) · [M2-I02](issues.md) |
| Day2 扩展 | schema / HITL | [M2-I03](issues.md) · [M2-I04](issues.md) |
| Day3 对照 | 分 tier timeout | [PR #9159](https://github.com/cline/cline/pull/9159) |

## 关联 Bad Case

- **Case 7**：只优化 ASR/TTS，忽略 LLM TTFT → 工具链需分桶监控
- **Case 6**：注入 / 越权 tool → allowlist + schema

## TrackARuntime（主线）

```powershell
cd TrackARuntime
python cli.py run --task "fix failing test"
python cli.py demo-allowlist --tool rm_rf
python cli.py demo-no-output-hang --idle-timeout 1
python cli.py run --task "hitl check" --require-hitl
# trace：m1_m2/evidence/<run_id>/trace.json 或 m2-8448-demo/
```

**边界 vs 主路径**：`demo-*` / `--require-hitl` 验边界；默认 loop 仍走 mock `docker_exec`/`run_tests`。详见 [`knowledge.md`](knowledge.md) M2-K01。

见 [`m1_m2/tool_executor.py`](../../TrackARuntime/m1_m2/tool_executor.py) · [`m1_m2/trace.py`](../../TrackARuntime/m1_m2/trace.py)
