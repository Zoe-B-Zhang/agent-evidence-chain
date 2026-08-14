# Case 16 — 高基数 metrics 导致告警失效

| 字段 | 值 |
|---|---|
| **ID** | case-16 |
| **主类** | **MET** |
| **次类** | SLO |
| **标签** | observability, metrics, cardinality, alert, slo |
| **关联模块** | M5 运维响应、M2 trace |
| **M5 深度** | 扩展（求职增强） |
| **SOP** | [sop-case-16](../sops/sop-case-16-observability-cardinality-alert-fatigue.md) |
| **TrackARuntime** | `trace.json` / `metrics-*.json` 可用于 OTel 对照；真实 dashboard 未实现 |
| **添加日期** | 2026-08-08 |
| **来源** | 合成生产事故 + observability 设计模式 |
| **当前状态** | 正式草稿（SOP 已落地；Runtime 可选） |
| **补强 K 点** | M5-K05 Observability；M5-K06 Incident Feedback Loop |
| **目标扩展包** | P6 Observability + SLO + Portfolio |

## 场景

团队把 `user_id`、完整 prompt hash、document_id 全部打进 metrics label，导致 metrics cardinality 爆炸。Dashboard 延迟，alert 丢失，事故期间无法判断是哪类 tool 或 model 变慢。

## 现象

1. Dashboard 查询变慢或超时，事故窗口看不到稳定趋势。
2. Alert 丢失、重复或噪声过大。
3. metrics label 中出现 user_id、run_id、prompt hash、document_id 等高基数字段。

## 根因（非表面）

不是监控不够多，而是 observability schema 缺少 cardinality 设计。Trace、log、metric 的职责混淆。

## 缺失的工程 invariant

Metric label 必须低基数；高基数诊断信息放 trace/log，不放核心指标标签。

## 工程解法

- 设计 telemetry schema。
- metrics 只保留 low-cardinality labels：model_family、tool_name、tenant_tier、error_class。
- user_id/run_id 放 trace/log。
- alert 按 SLO 聚合，而非按单用户。
- incident 后回流 dashboard rule。

## 系统等价物

把每个请求 ID 都作为 Prometheus label，导致时序数量爆炸，监控系统在事故窗口先失效。

## 初级 vs 高级认知

**初级**：把更多字段塞进 metrics，认为“监控越多越安全”。

**高级（目标）**：metrics 保持低基数，run_id/user_id/document_id 放 trace/log；alert 按服务级 SLO 聚合。

## 对应 Issue / PR / 校准来源

| 来源 | 链接 | 现象 | 修复点 | 可抽象的工程规则 |
|---|---|---|---|---|
| Observability 设计模式 | 本 Case | 高基数 label 拖垮 dashboard 与 alert | telemetry schema、label budget、SLO alert | metric label 必须低基数，高基数诊断放 trace/log |
| TrackARuntime 教学证据 | `trace.json` / `metrics-*.json` | 本地证据可映射 span/metric | 字段分层与 redaction policy | 本地 evidence 是生产观测的教学缩影 |

## What / Why / How 抽取

| K 点 | What | Why | How | Prove |
|---|---|---|---|---|
| M5-K05 | Observability = trace/metrics/logs/alerts/SLO 分工 | 指标高基数会让告警失效 | telemetry schema + label budget + OTel span 对照 | Case 16 |
| M5-K06 | Incident Feedback Loop = 事故后修监控规则 | 只修业务 bug 不修监控会复发 | postmortem 更新 dashboard/alert/eval | alert rule checklist |

## 监控与回滚

- **最先亮的监控层**：active series、label cardinality、dashboard query latency、alert drop / noise。
- **隔离 / 回滚**：临时移除高基数 label；暂停高成本 dashboard；用低基数 SLO dashboard 恢复服务级判断后再放量。

## SOP 摘要

| 阶段 | 动作 |
|---|---|
| 观察 | 检查 metrics cardinality、dashboard query latency、alert drop |
| 隔离 | 临时关高基数 label；降采样 trace |
| 定位 | 判断 label 爆炸、query 过重、alert rule 过细 |
| 修复验证 | 重建低基数 dashboard；回放告警 |
| 复盘 | 更新 telemetry schema 和 M5-K05 文档 |

## Runtime / Evidence 映射

| 类型 | 当前状态 |
|---|---|
| 已有证据 | `trace.json` 可映射 OTel span；`metrics-*.json` 是教学指标 |
| 已生成文档 | `case-16-observability-cardinality-alert-fatigue.md` 与 [SOP](../sops/sop-case-16-observability-cardinality-alert-fatigue.md) 已生成 |
| 可选 Runtime | `demo-observability --export otel-json` |
| 面试证明 | trace vs metric vs log 字段分配表 |

## 在本体系中的位置

- **模块**：M5 Observability 为主，M2 trace 字段设计辅助。
- **Issue / runtime 任务**：M5 生产扩展 SOP 索引；`demo-observability --export otel-json` 尚未实现。
- **关联 Case**：与 [Case 17](case-17-secret-leakage-through-tool-trace.md) 都要求 trace/log/metric 分工，Case 17 额外强调 redaction。

## 面试口述路径

60s：不是所有字段都该进 metrics label。  
2min：高基数标签拖垮 dashboard，事故时失去观测。  
5min：画 telemetry schema 和 SLO alert。

## Prove 附表：alert fatigue 机制

高基数 label 不仅拖慢 dashboard，还会让 **alert pipeline** 在事故窗口失效：

1. **查询超时**：按 `user_id` 聚合的 alert rule 在 cardinality 爆炸后无法及时 evaluate → 告警 **丢失**。
2. **噪声淹没**：每条 run 一条 alert → on-call 疲劳 → 真正 SLO breach 被忽略。
3. **dedupe 失效**：高基数 label 使“相同故障”无法合并 → 重复 paging。

**与 cardinality 的关系**：cardinality 是根因，alert fatigue 是 **用户可见后果**；fix 低基数 schema 后，alert 应按 `model_family` / `tool_name` / `error_class` 聚合。

## Prove 附表：telemetry schema（TrackARuntime 对照）

| 字段 | metrics（低基数） | trace（`trace.json`） | log（生产） |
|---|---|---|---|
| `tool_name` | ✅ 聚合 | ✅ 每 step | ✅ |
| `model_family` / `route_tier` | ✅ | ✅ `fallback_used` | ✅ |
| `error_class` | ✅ | ✅ 每 event | ✅ |
| `run_id` / `trace_id` | ❌ 过高基数 | ✅ | ✅ |
| `user_id` | ❌ | ❌（仅 hash） | ✅ 受限访问 |
| `prompt` 全文 | ❌ | ❌ | ❌ 或脱敏 |
| `latency_ms` | ✅ p95 聚合 | ✅ 每 span | 可选 |

**验证**：`python cli.py run --task "fix failing test" --llm mock` → 对照 `m1_m2/evidence/<run_id>/trace.json` 与 `metrics-*.json`。

## 关联 Case：与 [Case 07](case-07-latency-avalanche.md) 分工

| Case | 监控焦点 | 第一问题 |
|---|---|---|
| Case 07 | **span latency** waterfall | “哪一段变慢？” |
| Case 16 | **label cardinality** + alert 质量 | “事故时还能不能看见趋势？” |

## 学习记录（自填）

- **Day1 根因猜测**：
- **与 PR/解法对照差距**：
- **口述练习日期 / 用时**：


