# SOP Case 3：上下文「中间迷失」

> 案例叙事：[case-03](../../case-library/cases/case-03-context-lost-in-middle.md)

## 现象

长文档全塞入 context，中间关键信息被遗漏。

## 根因

Attention 中间弱化；未分层检索/摘要路由。

## 系统等价物

全表扫描塞内存，无索引。

## 故障响应 SOP

| 阶段 | 时间 | 动作 |
|---|---|---|
| 观察 | 5 min | 确认 context 长度、命中页码、用户追问点 |
| 隔离 | 10 min | 限制单次注入 token 上限 |
| 定位 | 30 min | 检查是否缺摘要树/路由策略 |
| 修复验证 | 1 h | 摘要层 + 按需下钻原始层；case 回归 |
| 复盘 | 全天 | 上下文预算纳入架构约束 |

## 监控

- 检索层：按层命中率
- 模型层：输入 token 分布

## 回滚预案

恢复「摘要优先」路由配置。

## 我的项目映射

Agent 应在 observe 后 replan 读取策略（见 M1 `m1_m2/loop_engine.py`）
