# SOP Case 9：Token 空转引发「配额雪崩」

> 案例叙事：[case-09](../cases/case-09-token-burn-rate-limit-cascade.md)  
> **定位**：扩展 Case（浅读）；**M1 Day3 扩展 Issue 4** 完成后填本 SOP；M5 复习时对照 Case 7。

## 现象

- 单 Agent 任务长时间「运行中」无产出。
- 随后 **全平台 LLM 429**，多服务同时不可用。
- 账单 / `cost_per_request` 在故障窗口内尖刺。

## 根因

1. **CTL**：silent loop 未 early fatal（环境死 / 无 progress fingerprint）。
2. **SLO**：共享 API 配额无 tenant/run 隔离；429 后 retry 加剧雪崩。

## 系统等价物

单服务 retry storms 打满共享连接池 → 全集群不可用。

## 故障响应 SOP

| 阶段 | 时间 | 动作 |
|---|---|---|
| 观察 | 5 min | 查 **429 率** + 单 run `trace.json` 事件数 / `state.json` 轮次；定位 **最耗 LLM call 的 run_id** |
| 隔离 | 10 min | **Kill 空转 run**；对该 tenant 暂停新 dispatch；必要时切换 backup key / 只读模式 |
| 定位 | 30 min | 对照 oss-803（substrate fatal 未升维）或 oss-4579（fingerprint 未 dispatch 前 enforce） |
| 修复验证 | 1 h | 补 fatal / fingerprint 门禁；加 **per-run token budget** 告警（先于 cost_limit） |
| 复盘 | 全天 | 429 纳入 infra 监控；Runbook：空转 run → CTL fix，429 全网 → SLO 隔离 |

## 监控

| 层 | 指标 |
|---|---|
| 应用 | `cost_per_request`、`llm_calls_per_run`、单 run token 斜率 |
| 基础设施 | API **429 率**、TPM/RPM 使用率、`quota_exhausted` |
| 控制面 | fingerprint 重复次数、round 无 progress 时长 |

## 回滚预案

1. 停止空转任务，释放 in-flight quota。
2. 等待 RPM 窗口恢复或切 backup endpoint。
3. 修复控制面后再重跑 **单任务**，禁止无 diff 全量重启。

## 与 Case 7 对照

| | Case 7 延迟雪崩 | Case 9 配额雪崩 |
|---|---|---|
| 主类 | SLO | CTL（次 SLO） |
| 症状 | 慢 / 超时 | 空转 + 429 全网 |
| 先看 | TTFT / per-tool latency | LLM call 数 / 429 率 |
| Fix 层 | 分路径 timeout | early fatal + 配额隔离 |

## 我的项目映射

（填写：共享 API Key 场景下的 run_id、429 告警、M1 fatal 证据路径）
