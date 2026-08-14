# Case 17 — Secret 泄露进入 trace/provider

| 字段 | 值 |
|---|---|
| **ID** | case-17 |
| **主类** | **SEC** |
| **次类** | SLO |
| **标签** | secret, redaction, data-boundary, provider, trace |
| **关联模块** | M2 工具边界、M5 运维 |
| **M5 深度** | 扩展（求职增强） |
| **SOP** | [sop-case-17](../sops/sop-case-17-secret-leakage-through-tool-trace.md) |
| **TrackARuntime** | 概念级；`trace.json` 可讨论字段边界，redaction 未实现 |
| **添加日期** | 2026-08-08 |
| **来源** | 安全规范 + 合成生产事故 |
| **当前状态** | 正式草稿（SOP 已落地；Runtime 可选） |
| **补强 K 点** | M2-K08 Data Boundary；M5-K05 Observability |
| **目标扩展包** | P3 Security + Tool Sandbox + Privacy |

## 场景

Agent 调用工具读取配置文件，工具输出包含 API token。系统把完整 tool output 写入 trace，并发送给外部 LLM provider 继续推理。后续日志检索中能看到明文 secret。

## 现象

1. Tool output 含 API token、cookie、private key 或 PII。
2. 明文 secret 出现在 trace、日志或 provider request 中。
3. 需要判断是否已外发给第三方模型供应商。

## 根因（非表面）

工具输出缺少 data classification 和 redaction；trace 被当成普通 debug log，而不是敏感数据载体。

## 缺失的工程 invariant

Secret / PII 不得进入 prompt、provider request、可见 trace 或长期 memory。

## 工程解法

- Tool output classification。
- Secret detector / redaction。
- Trace attribute allowlist。
- Provider-bound data policy。
- Incident secret rotation SOP。

## 系统等价物

把生产密钥写进日志系统和外部 SaaS 请求：日志和 provider request 本身成为数据泄露面。

## 初级 vs 高级认知

**初级**：把 trace 当 debug log，事故后手动删日志。

**高级（目标）**：tool output 先分类，secret/PII 先 redaction，再决定是否能进入 trace、prompt、provider request 或 memory。

## 对应 Issue / PR / 校准来源

| 来源 | 链接 | 现象 | 修复点 | 可抽象的工程规则 |
|---|---|---|---|---|
| 安全规范 | secret handling / data minimization | secret 进入日志或第三方请求 | detector、redaction、rotation | trace 也是敏感数据载体 |
| 合成生产事故 | 本 Case | tool output 含 token，进入 trace/provider | data classification + provider-bound policy | secret 不进 prompt/provider/可见 trace |

## What / Why / How 抽取

| K 点 | What | Why | How | Prove |
|---|---|---|---|---|
| M2-K08 | Data Boundary = PII/secret/tenant/provider policy | trace/provider 都可能成为泄露面 | classify → redact → block provider-bound data | Case 17 |
| M5-K05 | Observability 需包含 redaction policy | 观测数据本身也有安全边界 | redacted trace + audit log | incident SOP |

## 监控与回滚

- **最先亮的监控层**：secret_detected_in_tool_output、redaction hit rate、provider-bound policy deny、affected artifact count。
- **隔离 / 回滚**：立即 rotate secret；停用相关 tool / 禁用外发；限制日志访问；清理或封存泄露 artifact 后再恢复。

## SOP 摘要

| 阶段 | 动作 |
|---|---|
| 观察 | 确认 secret 出现在哪些 trace/log/provider request |
| 隔离 | 停止相关 tool；禁用外发；限制日志访问 |
| 定位 | 判断 secret detector 缺失、trace policy 缺失、provider policy 缺失 |
| 修复验证 | rotate secret；重跑 redaction test |
| 复盘 | 新增 SEC eval 和 redaction checklist |

## Runtime / Evidence 映射

| 类型 | 当前状态 |
|---|---|
| 已有证据 | M2 trace 字段可讨论，但未实现 redaction |
| 已生成文档 | `case-17-secret-leakage-through-tool-trace.md` 与 [SOP](../sops/sop-case-17-secret-leakage-through-tool-trace.md) 已生成 |
| 可选 Runtime | redaction check demo |
| 面试证明 | data boundary table |

## 在本体系中的位置

- **模块**：M2 Data Boundary 为主，M5 secret leakage 响应与 observability redaction 辅助。
- **Issue / runtime 任务**：M2-I06；redaction check demo 尚未实现。
- **关联 Case**：与 [Case 12](case-12-indirect-prompt-injection-tool-abuse.md) 同属 SEC，Case 12 管不可信指令，Case 17 管敏感数据外流。

## 面试口述路径

60s：trace 也是数据泄露面。  
2min：tool output 含 secret → trace 明文 → provider 外发 → rotate + redact。  
5min：画 data classification、redaction、provider policy、incident SOP。

## Prove 附表：data boundary table

| 数据类型 | prompt / LLM 上下文 | 可见 trace | provider request | 长期 memory |
|---|---|---|---|---|
| 业务代码片段 | ✅ 需授权 | ✅ | ✅ | ⚠️ 视策略 |
| PII（邮箱、手机） | ❌ 脱敏后 | ❌ 哈希/掩码 | ❌ | ❌ |
| API token / secret | ❌ | ❌ `[REDACTED]` | ❌ | ❌ |
| tool output 全文 | ⚠️ 分类后 | ⚠️ allowlist 字段 | ⚠️ 最小必要 | ❌ 默认不落 |

## Prove 附表：`trace.json` 泄露面与 redaction 目标

TrackARuntime 当前 `TraceEvent` 会把 **完整** `input` / `output` 写入 trace（见 `m1_m2/trace.py`）：

| 字段 | 现状风险 | redaction 后目标 |
|---|---|---|
| `output.stdout` / tool 返回正文 | 可能含 `api_key=...` | `[REDACTED:secret]` + `secret_detected=true` |
| `input` 完整 payload | 可能含用户粘贴的 token | 仅保留 tool 名 + 非敏感参数 |
| `trace_id` | 低敏 | 保留（用于关联） |

**最小讨论命令**：`python cli.py run --task "read config" --llm mock` → 检查 `trace.json` 是否应过滤 `output` 中的 key 模式。

## Prove 附表：secret rotation 验证步骤

1. **rotate**：在 secret store 签发新 key，旧 key 标记 `deprecated`。
2. **deploy**：各服务切换新 key；确认无服务仍读旧配置。
3. **verify**：用旧 key 调用应 **401/403**；审计日志无新请求带旧 key。
4. **purge**：按 retention 策略清理含明文的 trace/log artifact（或替换为 redacted 副本）。
5. **regression**：重跑 redaction / SEC eval scenario，确认同类 tool output 不再外泄。

## 学习记录（自填）

- **Day1 根因猜测**：
- **与 PR/解法对照差距**：
- **口述练习日期 / 用时**：


