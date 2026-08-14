# 模块 1 学习指南：Agent Workflow

> **导师补充**：知识工程点 [`M1-K01–K06`](knowledge.md) · 精选 Issue [`M1-I01–I05`](issues.md) · 评分 [`rubric.md`](rubric.md)

## 本模块在系统中的位置

| | |
|---|---|
| **生命线** | ① **控制面** — 任务能否可靠跑完、何时停 |
| **依赖** | 无（全课起点） |
| **主证据** | `state.json` + `trace.json` + `metrics-<run_id>.json` |
| **体系详述** | [`KNOWLEDGE-SYSTEM.md` §7 M1](../curriculum/00-knowledge-system.md) · [`COURSE.md` 第 1 课](../curriculum/01-course.md) |

## 原理（3 分钟版）

Agent = **有状态的任务机**，不是单次 Prompt 调用。

```
parse_intent → plan → act(tool) → observe(result) → [success | replan]
```

Plan 源可插拔（`--llm mock` → `MockLLMClient`）；中断可用 checkpoint/resume。四层 context 在 plan 前组装（见 knowledge M1-K01）。

| AI 概念 | 系统等价 |
|---|---|
| Agent loop | 工作流引擎（BPMN / 状态机） |
| observe | 传感器读数 / 事务执行结果 |
| replan | Saga 补偿 / 重试策略 |
| 最大轮次 / checkpoint | 断路器 / 作业快照恢复 |

## OSS 阅读清单

1. **mini-SWE-agent**（主读）：`mini_swe_agent/agents/` — 看 issue 如何被分解为步骤
2. **LangGraph**：`StateGraph`、条件边 `add_conditional_edges`
3. **OpenHands**：`agenthub` 目录 — 浏览 planner 与 controller 分离

## 三日校准（导师指定 Issue）

| 天 | 任务 | 链接 |
|---|---|---|
| Day1 主修 1 | container 死后 silent loop | [#803](https://github.com/SWE-agent/mini-swe-agent/issues/803) |
| Day1 主修 2 | ErrorObs vs Exception | [PR #4575](https://github.com/All-Hands-AI/OpenHands/pull/4575) |
| Day3 对照 | ContainerNotRunning | [PR #807](https://github.com/SWE-agent/mini-swe-agent/pull/807) |
| **Day3 扩展** | Case 9 平台后果（I04） | [Case 9](../case-library/cases/case-09-token-burn-rate-limit-cascade.md) · 完成 I01–I03B 后 |

Day1 写：#803 属于 **observe 类型错误**（致命态被当普通 observation），不是 replan 条件未定义。  
Day3 Issue 4：把 I01–I03 的 **单 run 缺陷** 升维到 **共享配额 / 429**（Case 9）。

## 关联 Bad Case

- **Case 3**：[上下文中间迷失](../case-library/cases/case-03-context-lost-in-middle.md) — 全量塞 context 而不 observe 检索质量 → 应 replan 到摘要层
- **Case 6**：[多轮注入](../case-library/cases/case-06-prompt-injection.md) — System 被覆盖 → observe 应检测漂移并 reset
- **Case 9（扩展）**：[Token 配额雪崩](../case-library/cases/case-09-token-burn-rate-limit-cascade.md) — #803/#4579 未 early fatal → 烧 Token → 共享 API 429；M1 Exit 前可选口述

## TrackARuntime（主线）

```powershell
cd TrackARuntime
python cli.py run --task "fix failing test" --llm mock
python cli.py run --task "container death" --simulate-container-death 1
python cli.py run --task "ckpt" --llm mock --checkpoint-dir m1_m2/evidence/checkpoints
# 中断后：python cli.py run --task "ckpt" --llm mock --resume-from m1_m2/evidence/checkpoints/<file>.json
```

主修 Issue 仍见 [`issues.md`](issues.md) I01–I04；checkpoint 见 **I05**。`--llm mock` / context / metrics **无独立 Issue**（knowledge 已标注）。

跑通第一条 `run` 后：**先读**根目录 [`USAGE.md` §2.1](../../USAGE.md#21-证据文件怎么用m1m2-示例)（`state` / `trace` / `metrics` 指读 checklist），再对照本模块 [`issues.md`](issues.md) 的证据 run。

见 [`TrackARuntime/README.md`](../../TrackARuntime/README.md)
