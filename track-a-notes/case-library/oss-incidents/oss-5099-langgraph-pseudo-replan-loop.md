# OSS-5099 — Replan 在走但 Action 不变（假恢复 / Pseudo-Replan）

| 字段 | 值 |
|---|---|
| **ID** | oss-5099 |
| **标签** | agent, replan, progress, fingerprint |
| **关联模块** | M1 |
| **Case 库关联** | 与 [oss-4579](oss-4579-openhands-stuck-loop-fatal.md) **同机制**（fingerprint fatal），叙事侧重 **observe/replan 路径正确但无 progress** |
| **Issue** | [LangGraph #5099](https://github.com/langchain-ai/langgraph/issues/5099) |
| **对照 PR** | 课程 **无 merged fix PR**；Issue 已 close（maintainer 新版本无法复现）；相关未合并 [langgraph PR #6889](https://github.com/langchain-ai/langgraph/pull/6889) |
| **TrackARuntime** | `python cli.py run --task "pseudo replan" --always-fail-tests --pseudo-replan --max-rounds 5` |
| **Day1–3 笔记** | [`module-01/module-01-day1.md`](../../module-01/module-01-day1.md) Issue 3B · [`module-01-day2.md`](../../module-01/module-01-day2.md) · [`module-01-day3.md`](../../module-01/module-01-day3.md) Issue 3B |
| **添加日期** | 2026-07 |

## 场景

`create_react_agent` + MCP tool（如 Elastic `list_indices`）：ToolMessage 报参数错误（`indexPattern` Required，agent 用了 `index_pattern`）。

## 现象

- Tool 返回 **recoverable** 错误（`Please fix your mistakes`）——单步 observe **分类正确**。
- Agent 文本：「Let me fix the parameter name」——**replan 路径在走**。
- 后续多轮 tool call **参数完全相同** → 无限 loop 直到 `recursion_limit`。
- 同一 MCP 在 Claude Code / pydanticAI 可正常工作（非纯 tool bug）。

## 根因

- **不是** #803 式 observe 未升维；**不是** #4575 式 controller 漏停 fatal。
- **是** **replan 无 progress**：`(tool, args)` fingerprint 不变 → **假恢复**（M1-K03：replan ≠ blind retry）。
- **缺 meta 层门禁**（M1-K06）：N 次相同 pattern 后应 escalate fatal 或换策略。
- TrackARuntime 用 `--pseudo-replan` 冻结 plan 模拟此场景。

> **勿与 #5165 混淆**：#5165 是 `astream_events` streaming 层 MCP 参数 schema bug，与本 case 的 pseudo-replan 叙事无关。

## 系统等价物

CI 日志写「fixing flaky test」，但 diff 为空仍重跑——不是 replan，是空转 retry。

## TrackARuntime 证据

- **Run**：`m1_m2/evidence/6363ddfb/`
- CLI：同 3A，`Fatal: Loop fingerprint detected...`
- `trace.json`：round2+ 的 `command` **均为** `Let me fix the parameter name...`
- `state.json`：多轮 `[retryable]` 后 fatal；round4 无 `act`
- **真 replan 对照**：`m1_m2/evidence/5fb33372/` event1 vs 3 command **不同** + `success=true`

## 学习记录（自填）

- **Day3 对照物**（Issue 无 merged PR，以 TrackARuntime 为 L2 证据）：
- **M1 rubric 自评**：
