# SOP Case 10：Provider 429 导致 fallback 失败

> 案例叙事：[case-10](../cases/case-10-provider-rate-limit-fallback.md)  
> **定位**：生产扩展 Case（求职增强）；主练 P1 LLM Gateway + M3/M5 配额响应。

## 现象

- Provider 开始返回大量 **429 / rate_limit_exceeded**。
- fallback 模型也不可用，或 fallback 后错误率继续升高。
- 多个 Agent 功能同时变慢或失败，`cost_per_request`、`tokens/request`、`fallback_rate` 同步尖刺。

## 根因

1. **SLO**：LLM Gateway 缺少 quota-aware fallback；429 被当成普通可重试错误。
2. **REL**：prompt / model / re-ask 配置变更未把 RPM/TPM 纳入灰度护栏。
3. **M5**：缺少 provider error taxonomy 和容量止血 SOP。

## 系统等价物

共享上游 API 的服务集群出现 **retry storm**：上游限流后，下游继续重试并切到同一 quota pool，导致全平台雪崩。

## 故障响应 SOP

| 阶段 | 时间 | 动作 |
|---|---|---|
| 观察 | 5 min | 查 429 rate、quota_remaining、fallback_rate、tokens/request、candidate prompt/model 版本 |
| 隔离 | 10 min | `gray_percent → 0`；暂停 candidate prompt/model route；对异常 tenant 限流；停止无界 retry |
| 定位 | 30 min | 判断是 prompt 变长、re-ask 循环、fallback 共 quota、tenant burst，还是 provider 限额变化 |
| 修复验证 | 1 h | 加 backoff、quota-aware fallback、max token budget；小流量重放 Case 10 |
| 复盘 | 全天 | 新增 provider error taxonomy、429 告警、harness cost/rate guardrail、M5 capacity runbook |

## 监控

| 层 | 指标 |
|---|---|
| 模型 / Provider | `provider_429_rate`、`provider_5xx_rate`、`quota_remaining` |
| 应用 | `fallback_rate`、`tokens_per_request`、`cost_per_request` |
| 发布 | candidate prompt/model route、gray bucket、rollback action |
| 租户 | tenant RPM/TPM、tenant error rate |

## 回滚预案

1. 回滚 candidate prompt/model route。
2. 暂停触发异常 token 增长的 tenant 或任务类型。
3. 切 backup provider / backup key 前先确认 quota pool 独立。
4. 修复 gateway 策略后小流量重放，不做全量无差别重启。

## 我的项目映射

（填写：Provider 指标、model route、gray 配置、tenant quota、Case 10 复盘链接）
