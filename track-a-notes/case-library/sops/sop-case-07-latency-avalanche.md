# SOP Case 7：语音/全链路「延迟雪崩」

> 案例叙事：[case-07](../../case-library/cases/case-07-latency-avalanche.md)

## 现象

部分请求稳定超时，用户体验崩溃。

## 根因

全链路 SLA 优化错位；瓶颈在 LLM TTFT 或某工具。

## 系统等价物

只优化前后端，数据库瓶颈未治理。

## 故障响应 SOP

| 阶段 | 时间 | 动作 |
|---|---|---|
| 观察 | 5 min | 分 span 看 P95：ASR/LLM/TTS/工具 |
| 隔离 | 10 min | 对慢路径降级（缓存/短答/离线） |
| 定位 | 30 min | 确认 TTFT vs 总生成时间 |
| 修复验证 | 1 h | 分路径 timeout；流式首 token |
| 复盘 | 全天 | SLA 按意图类型配置 |

## 监控

- 模型层：TTFT P50/P95
- 工具层：per-tool latencyMs

## 回滚预案

关闭联网/重工具路径，回退轻量模型。

## 我的项目映射

`TrackARuntime/m1_m2/tool_executor.py` 分工具 timeout；`trace.json` 记录 latencyMs
