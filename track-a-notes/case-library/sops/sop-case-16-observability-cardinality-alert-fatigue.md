# SOP Case 16：高基数 metrics 导致告警失效

> 案例叙事：[case-16](../cases/case-16-observability-cardinality-alert-fatigue.md)  
> **定位**：生产扩展 Case（求职增强）；主练 P6 Observability + M5 telemetry schema。

## 现象

- Dashboard 查询变慢或超时，事故窗口无法看到稳定趋势。
- Alert 丢失、重复或噪声过大，值班者无法判断影响范围。
- Metrics label 中出现 `user_id`、`run_id`、完整 prompt hash、document id 等高基数字段。

## 根因

1. **M5**：trace、log、metric 的职责混淆，高基数诊断字段被放进核心指标标签。
2. **SLO**：alert rule 按单用户 / 单 run 细粒度触发，而不是按服务级 SLO 聚合。
3. **M6/Portfolio**：只展示“有监控”，没有说明 telemetry schema 与 cardinality budget。

## 系统等价物

等价于把每个请求 ID 都作为 Prometheus label，导致时序数量爆炸，监控系统在最需要时先失效。

## 故障响应 SOP

| 阶段 | 时间 | 动作 |
|---|---|---|
| 观察 | 5 min | 查 active series、top label cardinality、dashboard query latency、alert drop / noise |
| 隔离 | 10 min | 临时移除高基数 label；暂停高成本 dashboard；对 trace 做采样 |
| 定位 | 30 min | 判断是 label 爆炸、query 过重、alert 过细、span/log/metric 边界混乱 |
| 修复验证 | 1 h | 重建低基数 dashboard；回放告警规则；确认 SLO 聚合指标稳定 |
| 复盘 | 全天 | 更新 telemetry schema、label budget、dashboard review checklist 与 runbook |

## 监控

| 层 | 指标 |
|---|---|
| Metrics backend | active series、label cardinality、query latency |
| Alert | alert fanout、dedupe rate、dropped alert count |
| Runtime | `error_class`、`tool_name`、`model_family`、`tenant_tier` |
| Trace / Log | run_id、user_id、document_id、prompt hash 放入可采样诊断面 |

## 回滚预案

1. 先降噪：停用高基数 label 与过细 alert。
2. 保留 trace/log 诊断字段，避免丢失排障能力。
3. 用低基数 SLO dashboard 恢复服务级判断。
4. 通过 review checklist 后再恢复新指标。

## 我的项目映射

（填写：metric label 白名单、trace/log 字段表、dashboard 截图或草图、alert rule）
