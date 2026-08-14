# SOP Case 13：Worker 死亡后 checkpoint resume

> 案例叙事：[case-13](../cases/case-13-worker-death-checkpoint-resume.md)  
> **定位**：生产扩展 Case（求职增强）；主练 P4 Runtime Scale + M1 durable control plane。

## 现象

- 长任务 Agent 卡在 `running`，用户刷新后没有明确失败状态。
- Worker 重启或重新调度后，部分 tool side effect 被重复执行。
- Queue backlog 上升，`resume_count`、`lease_age`、`worker_heartbeat_lag` 异常。

## 根因

1. **CTL**：任务状态依赖 worker 进程内存，而不是 durable job state。
2. **REL**：checkpoint 只保存 loop 内状态，未定义 side effect idempotency contract。
3. **M5**：缺少 worker lease / heartbeat / dead letter queue 的响应 SOP。

## 系统等价物

等价于分布式任务队列里 worker 拿到任务后宕机，但任务没有租约过期和幂等保护，导致卡死或重复扣款。

## 故障响应 SOP

| 阶段 | 时间 | 动作 |
|---|---|---|
| 观察 | 5 min | 查 queue depth、worker heartbeat、lease age、last checkpoint、side effect ledger |
| 隔离 | 10 min | 暂停该 tenant 新任务；冻结高风险 write/destructive tool；禁止盲目全量 retry |
| 定位 | 30 min | 判断 worker crash、lease 未释放、checkpoint 缺失、idempotency key 缺失、DLQ 未接入 |
| 修复验证 | 1 h | 从最后完整 checkpoint resume；核对 side effect ledger；验证重复执行被跳过 |
| 复盘 | 全天 | 增加 lease alert、resume contract test、idempotency test、dead letter SOP |

## 监控

| 层 | 指标 |
|---|---|
| Queue | `queue_depth`、`oldest_job_age`、`dead_letter_count` |
| Worker | `worker_heartbeat_lag`、`lease_expired_count` |
| Runtime | `checkpoint_age`、`resume_count`、`resume_failure_rate` |
| Tool | `idempotency_key_conflict`、side effect ledger mismatch |

## 回滚预案

1. 暂停受影响队列或 tenant。
2. 对已经完成 side effect 的 step 标记 committed，禁止重复执行。
3. 从最后完整 checkpoint 单任务恢复。
4. 无法证明幂等时进入人工处理 / dead letter queue。

## 我的项目映射

（填写：checkpoint 文件、job state machine、lease/heartbeat 字段、idempotency key 设计）
