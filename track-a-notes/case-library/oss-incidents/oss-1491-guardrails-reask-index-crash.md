# OSS-1491 — Re-ask 空 fail_results IndexError

| 字段 | 值 |
|---|---|
| **ID** | oss-1491 |
| **主类** | **REL** |
| **次类** | CTL |
| **标签** | harness, re-ask, boundary, guard |
| **关联模块** | M3 |
| **Case 库关联** | 与 [oss-803](oss-803-mini-swe-container-silent-loop.md) 同构（默认路径未处理）；[Case 02](../cases/case-02-prompt-butterfly.md) 互补（REL 交付层） |
| **Issue** | [guardrails #1491](https://github.com/guardrails-ai/guardrails/issues/1491) |
| **对照 PR** | [PR #1492](https://github.com/guardrails-ai/guardrails/pull/1492) |
| **TrackARuntime** | 阅读 `harness/guardrails.py`；类比 re-ask 有界 |
| **Day1–3 笔记** | [`module-03/module-03-day1.md`](../../module-03/module-03-day1.md) · [`day3`](../../module-03/module-03-day3.md) |
| **添加日期** | 2026-07 |

## 场景

Guardrails Harness 对 validation 失败的 field 做 re-ask；`FieldReAsk` 默认 `fail_results=None`。

## 现象

`sub_reasks_with_fixed_values` 在空 fail_results 上 **IndexError**；3 行 repro、无 LLM 即可触发——Harness 自身 crash。

## 根因（Day1 猜测，对照 PR 前）

1. **边界条件遗漏**：`fail_results or []` 后立刻 `[0]`，guard 写在索引之后不可达。
2. **默认值路径未测试**——与 oss-803「未检查 substrate 存活」同构。
3. Optional 默认 None vs [] 语义混用（#891 同类）。

## 系统等价物

消息队列 consumer 对空 dead-letter 队列直接 `queue[0]`；readiness probe 假设 `details[0]` 存在时脚本 crash。

## Design 要点（Day3 提炼）

- 设计 re-ask 状态机 flowchart：**先判 empty → 再索引**。
- merge 前单测覆盖 None/[]/有值三条路径。
- L3：schema 默认 `[]` + max re-ask counter。

## TrackARuntime 证据

- `guardrails.py` formality 护栏失败 → `rollback_to_v1`（交付决策类比 refrain）
- Day2 flowchart：`on_validation_fail` 分支

## 学习记录（自填）

- **Day3 与 PR #1492 差距**：
- **M3 rubric 自评**：
