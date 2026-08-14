# Case 10 — Provider 429 导致 fallback 失败

| 字段 | 值 |
|---|---|
| **ID** | case-10 |
| **主类** | **SLO** |
| **次类** | REL |
| **标签** | llm-gateway, provider, rate-limit, fallback, quota |
| **关联模块** | M3 配置交付、M5 运维响应、M1 错误分类 |
| **M5 深度** | 扩展（求职增强） |
| **SOP** | [sop-case-10](../sops/sop-case-10-provider-rate-limit-fallback.md) |
| **TrackARuntime** | `python cli.py run --llm mock` → `metrics-*.json`；`python cli.py harness` 灰度护栏 |
| **添加日期** | 2026-08-08 |
| **来源** | 合成生产事故 + provider rate limit 文档 + 未来 OSS issue 校准 |
| **当前状态** | 正式草稿（SOP 已落地；Runtime 可选） |
| **补强 K 点** | M3-K07 LLM Gateway；M3-K09 Rate Limit & Quota；M5-K07 Cost & Capacity Response |
| **目标扩展包** | P1 LLM Gateway + Cost + Rate Limit |

## 场景

Agent 平台接入外部 LLM Provider。某次 prompt 改动后，平均输出长度和 re-ask 次数上升，导致 TPM/RPM 使用率快速升高。Provider 开始返回 429，系统 fallback 到低配模型，但 fallback 也共用同一 org quota，最终多个 Agent 功能同时不可用。

## 现象

1. Provider 大量返回 429 / rate_limit_exceeded。
2. fallback 模型也失败或错误率继续升高。
3. 多 Agent 功能同时变慢/不可用；`fallback_rate`、`tokens/request`、`cost_per_request` 同步尖刺。

## 根因（非表面）

表面是 provider 429，根因是 **LLM Gateway 缺少配额感知的 fallback 策略**：fallback 只换模型名，没有检查 quota pool、tenant budget、retry backoff 和熔断策略。

## 缺失的工程 invariant

Provider error 不是普通 recoverable 文本错误；它必须进入统一 error taxonomy，并触发配额、fallback、限流和发布回滚策略。

## 工程解法

- LLM Gateway 统一 provider adapter。
- 对 429 / 5xx / timeout / invalid JSON / context_length 建 error taxonomy。
- 429 时先看 quota pool，不盲目 retry。
- fallback 策略必须知道 fallback model 是否共用 quota。
- M3 灰度期间观察 429 rate、fallback_rate、tokens/request。
- M5 SOP 支持降低 gray、暂停 candidate、tenant 限流、切 backup key。

## 系统等价物

共享上游 API 的微服务集群在上游限流后继续重试，并切到同一 quota pool，最终把局部配置变更放大成全平台容量事故。

## 初级 vs 高级认知

**初级**：只加 retry、换 fallback 模型、找供应商升配额。

**高级（目标）**：把 provider error 进入 LLM Gateway taxonomy，区分 429/5xx/timeout/invalid JSON；fallback 前检查 quota pool、tenant budget 与 gray rollout 指标。

## 对应 Issue / PR / 校准来源

| 来源 | 链接 | 现象 | 修复点 | 可抽象的工程规则 |
|---|---|---|---|---|
| 合成生产事故 | 本 Case | provider 429 后 fallback 共 quota，事故扩大 | quota-aware fallback、tenant limiter、gray rollback | 429 不是普通 retry，必须进入 capacity policy |
| 对照 Case | [Case 09](case-09-token-burn-rate-limit-cascade.md) | silent loop 烧穿共享配额 | early fatal + token budget | 同见 429，但 Case 09 根因在 CTL，Case 10 根因在 Gateway / REL |

## What / Why / How 抽取

| K 点 | What | Why | How | Prove |
|---|---|---|---|---|
| M3-K07 | LLM Gateway = 模型供应商适配与故障隔离层 | 没有 gateway，provider 429 会被当普通 retry，造成雪崩 | adapter + error taxonomy + structured output + fallback policy | Case 10；provider error table |
| M3-K09 | Rate Limit & Quota Delivery = 把 RPM/TPM/tenant quota 纳入发布护栏 | Prompt/模型配置变更会放大 token 和并发 | gray 期间监控 quota、fallback_rate、tokens/request | harness 发布 checklist |
| M5-K07 | Cost & Capacity Response = 429/quota/backlog 的固定止血 SOP | 盲目 retry 会扩大事故 | 降 gray、限流 tenant、暂停 candidate、切 backup key | SOP Case 10 |

## 监控与回滚

- **最先亮的监控层**：provider 429 率、quota_remaining、fallback_rate、tokens/request、candidate prompt/model 版本。
- **隔离 / 回滚**：gray_percent → 0；暂停 candidate route；对异常 tenant 限流；切独立 quota 的 backup endpoint 前先确认 pool 不共享。

## SOP 摘要

| 阶段 | 动作 |
|---|---|
| 观察 | 看 429 rate、quota_remaining、fallback_rate、tokens/request、candidate prompt 版本 |
| 隔离 | gray→0；暂停 candidate；对异常 tenant 限流 |
| 定位 | 判断是 prompt 变长、re-ask 循环、fallback 共 quota，还是 provider 侧限额下降 |
| 修复验证 | 加 backoff、quota-aware fallback、max token budget；小流量重放 |
| 复盘 | 新增 provider error eval / harness guardrail / M5 alert |

## Runtime / Evidence 映射

| 类型 | 当前状态 |
|---|---|
| 已有证据 | `metrics-*.json` 有 token/cost 估算；Case 09 有 token burn 叙事 |
| 已生成文档 | `case-10-provider-rate-limit-fallback.md` 与 [SOP](../sops/sop-case-10-provider-rate-limit-fallback.md) 已生成 |
| 已有命令 | `python cli.py run --task "fix failing test" --llm mock` → 打开 `m1_m2/evidence/<run_id>/metrics-*.json` |
| 可选 Runtime | `demo-llm-gateway --failure rate_limit`（未实现） |
| 面试证明 | 下文 Provider error taxonomy + fallback decision table |

## 在本体系中的位置

- **模块**：M3 配置交付为主，M5 运维响应与 M1 provider error 分类辅助。
- **Issue / runtime 任务**：M3-I03；可选 `demo-llm-gateway --failure rate_limit` 尚未实现。
- **关联 Case**：与 [Case 09](case-09-token-burn-rate-limit-cascade.md) 同见 429，但根因层不同。

## 关联 Case / 区分轴

| 对比项 | [Case 09](case-09-token-burn-rate-limit-cascade.md)：Token 空转配额雪崩 | Case 10：Provider fallback 失败 |
|---|---|---|
| 首要根因层 | **CTL**：silent loop / fingerprint 未 early fatal | **SLO / REL**：LLM Gateway fallback 不感知 quota |
| 429 触发方式 | 单个 run 持续 dispatch LLM，烧穿共享 TPM/RPM | prompt/model 变更后 token 上升，fallback 共用 quota pool |
| 第一监控 | `llm_calls_per_run`、token 斜率、fingerprint 重复 | `provider_429_rate`、`fallback_rate`、quota_remaining |
| 首要 fix | dispatch 前 fatal、per-run token budget、tenant 隔离 | quota-aware fallback、backoff、gray rollback、tenant limiter |
| 面试一句话 | “控制面没停，空转把共享配额烧穿。” | “Gateway 降级策略错，把 provider 429 放大成平台事故。” |

## Prove 附表：Provider error taxonomy + fallback decision

| Provider error | 分类 | 默认动作 | 禁止动作 | fallback 条件 |
|---|---|---|---|---|
| `429` / rate_limit | capacity | 读 quota_remaining → exponential backoff → tenant limit | 立即 blind retry；切共用 quota 的 fallback | fallback model 使用**独立** quota pool |
| `5xx` | transient | 有限 retry + circuit breaker | 无限 retry 同一 endpoint | 仅 primary 连续失败且 breaker open |
| `timeout` | transient | 降 max_tokens / 缩短 prompt；记录 span | 同步阻塞整 run | 可切更快 model，但需预算检查 |
| `invalid_json` | contract | fail closed；结构化 repair 一次 | 把畸形输出当 observation 继续 loop | 不 fallback，修 adapter/schema |
| `context_length` | input | 截断 / 摘要 / 换长上下文 model | 原样重试同一 payload | 仅当长上下文 model 有独立 quota |

**决策口诀**：先分类 → 再看 quota → 再决定是否 fallback → 最后才 retry。

## Prove 附表：`metrics-*.json` 字段映射

> 生成命令：`cd TrackARuntime && python cli.py run --task "fix failing test" --llm mock` → 打开 `m1_m2/evidence/<run_id>/metrics-*.json`。

| Case 10 监控指标 | TrackARuntime 字段 | 生产扩展 |
|---|---|---|
| `tokens/request` | `tokens.input` + `tokens.output` | 按 route / tenant 聚合 |
| `cost_per_request` | `cost_usd` | 配 harness cost guardrail |
| fallback 是否发生 | `trace.json` 事件 `fallback_used` | `fallback_rate` by model_family |
| rate limit 信号 | `rate_limited`（bool） | `provider_429_rate`、quota_remaining |
| 发布关联 | `model`、`route_tier` | candidate prompt 版本、gray bucket |
| 延迟尖刺 | `latency_ms.p95` | provider span + gateway queue depth |

## 面试口述路径

60s：429 不是简单 retry；我会放在 LLM Gateway 做 provider error taxonomy、quota-aware fallback 和 M5 止血。  
2min：讲 prompt 变更 → token/request 上升 → 429 → fallback 共 quota → 全平台不可用 → gray rollback。  
5min：画 gateway、quota pool、tenant limiter、M3 harness、M5 alert 的链路。

## 学习记录（自填）

- **Day1 根因猜测**：
- **与 PR/解法对照差距**：
- **口述练习日期 / 用时**：


