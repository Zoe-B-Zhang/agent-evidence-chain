# OSS-2643 — DeepEval Agent Loop Detection Metric Scaffold

| 字段 | 值 |
|---|---|
| **ID** | oss-2643 |
| **主类** | **MET** |
| **次类** | CTL |
| **标签** | eval, loop, trace, fingerprint |
| **关联模块** | M4, M1 |
| **Case 库关联** | [oss-4579](oss-4579-openhands-stuck-loop-fatal.md)、[oss-5099](oss-5099-langgraph-pseudo-replan-loop.md)；M1 online fingerprint |
| **Issue** | [DeepEval #2643](https://github.com/confident-ai/deepeval/issues/2643) |
| **对照 PR** | [PR #2782](https://github.com/confident-ai/deepeval/pull/2782)（scaffold only） |
| **TrackARuntime** | `eval/runner.py` loop_detection stub；M1 `_check_fingerprint_loop()` |
| **Day1–3 笔记** | [`module-04/module-04-day1.md`](../../module-04/module-04-day1.md) · [`day3`](../../module-04/module-04-day3.md) |
| **添加日期** | 2026-07 |

## 场景

DeepEval 评 agentic run 的 completion/quality，但缺 **infinite loop / cyclical tool-call** 专用 metric。

## 现象

同一 tool+args 重复 N 次；reasoning 停滞；call graph 成环——final output 可能仍「看起来完成」。

## 根因

**Eval 维度缺口**（非单纯 Agent bug）：过程 pathology 无离线传感器。

## 系统等价物

集成测试只 assert HTTP 200，不查 retry 风暴或相同 SQL 执行 50 次。

## Design 要点（Day3 提炼）

- taxonomy 设计阶段并列 **过程类** failure code（LOOP_DETECTED、OBSERVE_STALL）。
- online/offline 共用 hash(tool,args) flowchart，防算法 drift。
- scaffold PR = 先占坑；L3 实现 fingerprint + S21 scenario。

## TrackARuntime 证据

- M1 run `416be508`：相同 docker_exec 3 次 → fatal
- `failure_taxonomy.md` LOOP_DETECTED 行

## 学习记录（自填）

- **Day3 与 PR #2782 差距**：
- **M4 rubric 自评**：
