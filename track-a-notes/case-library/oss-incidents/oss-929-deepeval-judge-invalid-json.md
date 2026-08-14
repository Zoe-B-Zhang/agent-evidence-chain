# OSS-929 — DeepEval Judge Invalid JSON

| 字段 | 值 |
|---|---|
| **ID** | oss-929 |
| **主类** | **MET** |
| **次类** | REL |
| **标签** | eval, judge, gate, structured-output |
| **关联模块** | M4 |
| **Case 库关联** | [Case 15](../cases/case-15-judge-bias-false-regression.md)；[oss-1491](oss-1491-guardrails-reask-index-crash.md)（门禁脚本不可信）；M3 #1491 |
| **Issue** | [DeepEval #929](https://github.com/confident-ai/deepeval/issues/929) |
| **对照 PR** | Issue 讨论 + structured output workaround（无单一 merged fix） |
| **TrackARuntime** | `failure_taxonomy.md` EVAL_JUDGE_FAIL；`python cli.py eval` |
| **Day1–3 笔记** | [`module-04/module-04-day1.md`](../../module-04/module-04-day1.md) · [`day3`](../../module-04/module-04-day3.md) |
| **添加日期** | 2026-07 |

## 场景

DeepEval 用 LLM 作 judge 输出 JSON 评分；Azure/小模型路径易畸形输出。

## 现象

`ValueError: Evaluation LLM outputted an invalid JSON`——全量 eval 不可信，gate_pass 无意义。

## 根因（三类）

1. max_tokens 截断 JSON。
2. AzureOpenAI 缺 `model_name` → 未走 structured output。
3. 小模型不遵守 schema → 需 Instructor/outlines。

## 系统等价物

CI 测试 runner 自身 crash → 全绿/全红都不可信。

## Design 要点（Day3 提炼）

- judge 当一等公民：health check scenario + fail closed。
- flowchart：model → structured output 分支 → parse → gate。
- failure_distribution 分列 EVAL_JUDGE_FAIL vs task fail。
- 扩展到 bias / calibration：[Case 15](../cases/case-15-judge-bias-false-regression.md) 把“judge 自身失败”扩展为 judge-human disagreement 与 rubric version 治理。

## TrackARuntime 证据

- taxonomy `EVAL_JUDGE_FAIL` 行
- eval 报告 `gate_pass` 前提 = judge 可靠

## 学习记录（自填）

- **Day3 与社区 fix 差距**：
- **M4 rubric 自评**：
