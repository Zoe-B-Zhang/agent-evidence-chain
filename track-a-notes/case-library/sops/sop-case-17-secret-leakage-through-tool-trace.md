# SOP Case 17：Secret 泄露进入 trace/provider

> 案例叙事：[case-17](../cases/case-17-secret-leakage-through-tool-trace.md)  
> **定位**：生产扩展 Case（求职增强）；主练 P3 Data Boundary + M5 安全事件响应。

## 现象

- Tool output 含 API token、cookie、private key 或 PII。
- 明文 secret 出现在 `trace.json`、日志检索、debug artifact 或 provider request 中。
- 事故后需要判断是否已经外发给第三方模型供应商。

## 根因

1. **SEC**：tool output 缺少 data classification，secret 被当成普通文本。
2. **M2**：trace policy 没有 attribute allowlist / redaction。
3. **M5**：secret leakage 没有 rotation、访问收敛和证据清理 SOP。

## 系统等价物

等价于把生产密钥写进日志系统和外部 SaaS 请求：日志本身成为数据泄露面。

## 故障响应 SOP

| 阶段 | 时间 | 动作 |
|---|---|---|
| 观察 | 5 min | 确认 secret 出现在哪些 trace/log/provider request；记录 affected run_id、tenant、tool |
| 隔离 | 10 min | 停用相关 tool 或改 dry-run；禁用 provider 外发；限制日志/trace 访问 |
| 定位 | 30 min | 判断 detector 缺失、redaction 缺失、trace allowlist 缺失、provider-bound policy 缺失 |
| 修复验证 | 1 h | rotate secret；清理或封存泄露 artifact；重跑 redaction test 与 SEC scenario |
| 复盘 | 全天 | 新增 data classification、redaction checklist、provider data policy、rotation runbook |

## 监控

| 层 | 指标 |
|---|---|
| Tool Boundary | `secret_detected_in_tool_output`、data_class |
| Trace / Log | redaction hit rate、raw secret write block count |
| Provider | provider-bound data policy deny count |
| Security | rotation status、affected artifact count |

## 回滚预案

1. 立即 rotate 已暴露 secret。
2. 暂停能读取敏感文件的 tool 或收紧路径范围。
3. 从 trace/log/provider artifact 中删除、封存或降低访问权限。
4. 恢复前必须通过 redaction test 和 provider-bound policy check。

## 我的项目映射

（填写：secret detector 规则、trace allowlist、provider-bound policy、rotation 记录）
