# SOP Case 6：上下文注入「数据毒药」

> 案例叙事：[case-06](../../case-library/cases/case-06-prompt-injection.md)

## 现象

多轮后输出偏离安全设定，极端或恶意内容。

## 根因

用户输入逐步覆盖 System Prompt；无锁定区与异常检测。

## 系统等价物

SQL 注入 + 会话状态污染。

## 故障响应 SOP

| 阶段 | 时间 | 动作 |
|---|---|---|
| 观察 | 5 min | 导出对话 trace，定位注入轮次 |
| 隔离 | 10 min | 限流涉事账号；强制 session reset |
| 定位 | 30 min | 检查 system 区隔离、轮次压缩策略 |
| 修复验证 | 1 h | 锁定 system + 输出情感/安全 classifier |
| 复盘 | 全天 | 红队用例加入 eval |

## 监控

- 应用层：情感极性波动、安全规则触发率

## 回滚预案

切换安全 Prompt 版本；清空污染 session。

## 我的项目映射

Tool allowlist 拒绝危险工具（M2 trace demo）
