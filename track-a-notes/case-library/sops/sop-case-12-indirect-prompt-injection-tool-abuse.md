# SOP Case 12：间接 Prompt Injection 越权工具调用

> 案例叙事：[case-12](../cases/case-12-indirect-prompt-injection-tool-abuse.md)  
> **定位**：生产扩展 Case（求职增强）；主练 P3 Security + M2 Policy Engine。

## 现象

- Agent 读取网页、issue、文档或邮件后，提出与用户目标无关的高危 tool call。
- Trace 中能看到危险操作来自外部内容诱导，而不是用户显式授权。
- HITL 或 allowlist 没有拦住，因为 tool 本身在白名单内。

## 根因

1. **SEC**：系统未区分 trusted instruction 与 untrusted content。
2. **M2**：tool call 缺少模型外 policy engine，模型输出被误当成授权依据。
3. **M4**：缺少 indirect prompt injection 的固定 red team scenario。

## 系统等价物

等价于 Web 应用把用户输入当 SQL 指令执行：不是 SQL 写得不够强，而是信任边界错了。

## 故障响应 SOP

| 阶段 | 时间 | 动作 |
|---|---|---|
| 观察 | 5 min | 打开 trace：untrusted source、tool intent、policy decision、approval record |
| 隔离 | 10 min | 禁用相关 write/destructive tool；切 read-only mode；阻断同源内容继续触发 |
| 定位 | 30 min | 判断 trust label 缺失、policy 缺失、HITL 缺失，还是 tool scope 过宽 |
| 修复验证 | 1 h | 增加 policy rule；重跑 SEC scenario；确认 deny / require approval |
| 复盘 | 全天 | 新增 red team case、tool risk tier、approval transcript 与 audit rule |

## 监控

| 层 | 指标 |
|---|---|
| Tool Policy | `policy_denied_count`、`requires_approval_count` |
| Security | untrusted content → tool intent 触发率 |
| Trace | tool source provenance、side_effect_level |
| Eval | SEC scenario pass rate |

## 回滚预案

1. 临时禁用高危 tool 或降级为 dry-run。
2. 收紧 policy：untrusted content 不允许触发 write/destructive tool。
3. 复核近期同源内容触发的 tool calls。
4. 补 red team eval 后再恢复权限。

## 我的项目映射

（填写：外部内容来源、tool policy 表、deny trace、SEC eval scenario）
