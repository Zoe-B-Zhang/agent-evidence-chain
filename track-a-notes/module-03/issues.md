# M3 精选 Issue（第 3 周）

> 索引：[tutor/README.md](../tutor/README.md) · 知识工程点：[knowledge.md](knowledge.md)

## M3-I01 主修 — re-ask 边界（#1491）

| 项 | 内容 |
|---|---|
| Issue | [guardrails #1491](https://github.com/guardrails-ai/guardrails/issues/1491) |
| Day3 PR | [PR #1492](https://github.com/guardrails-ai/guardrails/pull/1492) |
| K 点 | M3-K06, M3-K01 |
| **Runtime 任务** | 阅读 `guardrails.py`；文档记录 max re-ask 应如何实现 |

## M3-I02 主修 — Case 2 蝴蝶效应

| 项 | 内容 |
|---|---|
| **Runtime 任务** | `python cli.py harness --prompt v2 --gray-percent 10` → `rollback_to_v1` |
| **L3 扩展** | `harness --watch` → `m3/evidence/rollout-state.json`（见 `m3/rollout_controller.py`） |
| K 点 | M3-K02–K05 |
| **L2 证明** | 截图/复制 harness-report.json + 口述 Case 2 |

## M3-I03 生产扩展 — Provider 429 与 quota-aware fallback

| 项 | 内容 |
|---|---|
| Case | [Case 10](../case-library/cases/case-10-provider-rate-limit-fallback.md) |
| SOP | [sop-case-10](../case-library/sops/sop-case-10-provider-rate-limit-fallback.md) |
| K 点 | M3-K07, M3-K09, M5-K07 |
| **学习任务** | 把 429 与 5xx 区分为不同 error class；设计 model route / fallback / quota budget 的灰度护栏 |
| **L2 Pass** | 能解释为什么 fallback 共用 quota pool 会扩大事故；能给出 rollback 到 prompt/model v1 的止血路径 |
| **L3 扩展** | 将 `model_router`、`rate_limiter`、`cost_monitor` 的教学 stub 串入 `harness` report |

> **无对应 Issue**：`model_router` / `token_counter` / `cost_monitor` / `rate_limiter` / `metrics-*.json` 精读——见 [`knowledge.md`](knowledge.md) M3-K01、K03 标注。可选自学：`python cli.py run --task "fix failing test" --llm mock` 后打开 `metrics-*.json`。Case 10 用于把这些 stub 升级为可讲述的生产事故路径。
