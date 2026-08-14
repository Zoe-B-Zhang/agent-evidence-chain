# Case 13 — Worker 死亡后 checkpoint resume

| 字段 | 值 |
|---|---|
| **ID** | case-13 |
| **主类** | **CTL** |
| **次类** | SLO |
| **标签** | runtime-scale, worker, checkpoint, lease, idempotency |
| **关联模块** | M1 控制面、M5 运维 |
| **M5 深度** | 扩展（求职增强） |
| **SOP** | [sop-case-13](../sops/sop-case-13-worker-death-checkpoint-resume.md) |
| **TrackARuntime** | `--checkpoint-dir` / `--resume-from` 已有教学路径；queue/worker/lease 为概念级 |
| **添加日期** | 2026-08-08 |
| **来源** | 合成生产事故 + 分布式任务系统模式 |
| **当前状态** | 正式草稿（SOP 已落地；Runtime 可选） |
| **补强 K 点** | M1-K07 Runtime Scale；M5-K05 Observability |
| **目标扩展包** | P4 Runtime Scale + Memory + State |

## 场景

长任务 Agent 执行到第 7 步时 worker 崩溃。用户刷新页面看到任务卡在 running；后台重新调度后，部分 tool side effect 被重复执行。

## 现象

1. 长任务卡在 running，用户刷新看不到明确失败。
2. Worker 重启或重调度后，部分 tool side effect 被重复执行。
3. queue backlog、lease_age、resume_count、worker_heartbeat_lag 异常。

## 根因（非表面）

单 run checkpoint 有了，但缺少生产任务系统的 **lease、idempotency、resume contract**。Worker death 被当成普通 timeout，而非 runtime-level state transition。

## 缺失的工程 invariant

任务状态必须由 durable state 驱动，worker 只是租约持有者；resume 不得重复已提交副作用。

## 工程解法

- Job queue + worker lease。
- 每步 checkpoint 持久化。
- Tool call 带 idempotency key。
- Worker heartbeat 超时后重新认领。
- Dead letter queue 保存无法恢复任务。

## 系统等价物

分布式任务队列中 worker 拿到任务后宕机，但没有租约过期与幂等保护，导致任务卡死或副作用重复执行。

## 初级 vs 高级认知

**初级**：worker 崩了就重跑任务。

**高级（目标）**：任务状态必须 durable，worker 只是 lease holder；resume 前要核对 checkpoint 与 side effect ledger。

## 对应 Issue / PR / 校准来源

| 来源 | 链接 | 现象 | 修复点 | 可抽象的工程规则 |
|---|---|---|---|---|
| 分布式任务系统模式 | 本 Case | worker death 后 running 卡死或重复副作用 | lease、checkpoint、idempotency、DLQ | 任务状态不能依赖 worker 内存 |
| TrackARuntime 教学路径 | `--checkpoint-dir` / `--resume-from` | 单 run checkpoint 可恢复 | 扩展为 durable job state | checkpoint 是 resume 基础，不等于生产任务系统 |

## What / Why / How 抽取

| K 点 | What | Why | How | Prove |
|---|---|---|---|---|
| M1-K07 | Runtime Scale = queue/worker/lease/checkpoint/idempotency 的控制面扩展 | 单 loop 无法支撑多任务与 worker failure | durable job state + lease + checkpoint resume | Case 13；runtime queue 白板 |
| M5-K05 | Observability = worker/run/tool span 可定位 | 没有 heartbeat/lease 指标，running 卡死不可见 | worker_heartbeat、lease_expired、resume_count | M5 dashboard 草图 |

## 监控与回滚

- **最先亮的监控层**：queue_depth、worker_heartbeat_lag、lease_expired_count、checkpoint_age、resume_failure_rate。
- **隔离 / 回滚**：暂停该 tenant 新任务；冻结高风险 write tool；从最后完整 checkpoint 单任务 resume，无法证明幂等则进 DLQ / 人工处理。

## SOP 摘要

| 阶段 | 动作 |
|---|---|
| 观察 | 看 queue_depth、worker heartbeat、lease_age、last checkpoint |
| 隔离 | 暂停该 tenant 新任务；冻结可能重复副作用 tool |
| 定位 | 判断 worker crash、lease 未释放、checkpoint 不完整、idempotency 缺失 |
| 修复验证 | 从 checkpoint resume；确认 side effect 未重复 |
| 复盘 | 加 lease alert、idempotency test、dead letter SOP |

## Runtime / Evidence 映射

| 类型 | 当前状态 |
|---|---|
| 已有证据 | M1 checkpoint/resume 概念已有 |
| 已生成文档 | `case-13-worker-death-checkpoint-resume.md` 与 [SOP](../sops/sop-case-13-worker-death-checkpoint-resume.md) 已生成 |
| 可选 Runtime | `demo-runtime-queue --simulate-worker-death` |
| 面试证明 | queue/worker/lease/idempotency 架构图 |

## 在本体系中的位置

- **模块**：M1 Runtime Scale 为主，M5 worker/queue 观测辅助。
- **Issue / runtime 任务**：M1-I05；生产 queue/worker/lease demo 尚未实现。
- **关联 Case**：与 [Case 14](case-14-memory-poisoning-version-rollback.md) 同属 P4，前者管任务状态，后者管长期 memory 状态。

## Prove 附表：Job state machine

| 状态 | 触发条件 | 允许动作 | 禁止动作 |
|---|---|---|---|
| `queued` | 任务入队 | worker 认领 | 直接执行副作用 |
| `leased` | worker 拿到 lease | 执行 loop step | 另一 worker 并发执行 |
| `checkpointed` | 每步持久化 | resume 从 last good step | 跳过已提交副作用 |
| `running` | 正在执行 | heartbeat 续租 | 无 lease 执行 write |
| `failed` | 不可恢复错误 | 进 DLQ / 人工介入 | 自动无限重试 |
| `done` | 成功完成 | 归档 evidence | 再次 resume |

## Prove 附表：TrackARuntime 能演示 / 不能演示

| 能力 | TrackARuntime 现状 | 生产目标（Case 13） |
|---|---|---|
| 单 run checkpoint | ✅ `--checkpoint-dir` / `--resume-from` | durable job store |
| worker lease | ❌ 未实现 | heartbeat + lease_expired 重认领 |
| idempotency key | ❌ 未实现 | tool call 带幂等键 |
| 副作用账本 | ❌ 未实现 | 已提交副作用不可重复 |
| DLQ | ❌ 未实现 | 无法恢复任务隔离 |
| 观测 | ✅ `state.json` / `trace.json` | + `worker_heartbeat`、`resume_count` |

教学命令：

```powershell
python cli.py run --task "fix failing test" --checkpoint-dir m1_m2/evidence/checkpoints --llm mock
# 中断后：
python cli.py run --task "fix failing test" --resume-from m1_m2/evidence/checkpoints/<run_id> --llm mock
```

## Prove 附表：副作用重复示例

Worker 在第 7 步崩溃前已执行 `docker_exec` 部署脚本，resume 后若无 idempotency：

1. 第一次：`docker_exec` → 生产配置已更新。
2. resume 从 step 7 重放 → **第二次** `docker_exec` → 重复发布 / 双写。

等价于支付系统 retry 未带 idempotency key 导致重复扣款。

## 面试口述路径

60s：worker 只是租约持有者，任务状态必须 durable。  
2min：worker crash → lease expire → resume from checkpoint → idempotency 防副作用重复。  
5min：画 job state machine 和 failure recovery。

## 学习记录（自填）

- **Day1 根因猜测**：
- **与 PR/解法对照差距**：
- **口述练习日期 / 用时**：


