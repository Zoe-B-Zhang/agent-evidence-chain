# Saga 补偿（Saga Compensation）

> **一句话**：长流程拆成多步本地事务；某步失败时，用 **补偿操作** 撤销已提交步骤的影响，或在 **枢轴点** 之后改为 **正向恢复**，以换取 **最终一致性**（而非 ACID 强隔离）。  
> **在本体系里**：Agent 的 **replan** 是有条件的「正向恢复」；**fatal** 是「不可补偿、强制终态」。

---

## 1. 要解决什么问题

传统 **两阶段提交（2PC）** 在长流程、跨服务场景下会 **长时间锁资源**，并发差。  
**Saga** 允许每个子步骤 **执行完就提交**（本地事务立即落库），整体只保证 **最终一致性**——中间态可能被其他读者看到，需业务自行处理。

---

## 2. 形式化模型

一个 Saga 将大事务拆为有序子事务：

\[
T_1 \rightarrow T_2 \rightarrow \cdots \rightarrow T_n
\]

- 每步 \(T_i\) 在 **单个服务 / 单个边界** 内提交。
- 若 \(T_k\) 失败（\(k \leq n\)），有两种主流策略：

### 2.1 逆向补偿（Backward Recovery）

对已成功的步骤 **按相反顺序** 执行补偿：

\[
C_{k-1}, C_{k-2}, \ldots, C_1
\]

其中 \(C_i\) 是 \(T_i\) 的 **语义逆操作**（不是数据库 undo log 本身，而是业务定义的「撤销影响」）。

**例**：订单已扣库存（\(T_1\)）→ 支付失败（\(T_2\) 失败）→ 执行加回库存（\(C_1\)）。

### 2.2 正向恢复（Forward Recovery）

超过 **枢轴事务（Pivot）** 之后，系统 **不再逆向回滚**，而是 **必须让后续正向步骤成功**（重试、换路径、人工兜底）。

**例**：订单已创建且不可删（Pivot）→ 支付网关超时 → 持续重试支付或换渠道，而不是删订单。

---

## 3. 核心组成

| 概念 | 含义 |
|---|---|
| **正向操作** \(T_i\) | Saga 链上的第 i 步；完成后 **立即提交** 本地事务 |
| **补偿操作** \(C_i\) | \(T_i\) 的逆向语义操作；仅在 backward recovery 路径触发 |
| **枢轴事务（Pivot）** | 不可逆节点；过后走 **forward recovery**，不再 \(C_{i}\ldots C_1\) 全链回滚 |

---

## 4. 设计原则

| 原则 | 要求 | 原因 |
|---|---|---|
| **幂等性** | \(T_i\) 与 \(C_i\) 均可安全重放 | 网络超时会导致重复调用 |
| **可交换性** | 补偿顺序与语义一致：先执行 \(T_1..T_{k-1}\) 再 \(C_{k-1}..C_1\) 应等价于未开始 Saga | 保证回滚语义正确 |
| **补偿必达** | \(C_i\) 设计上要尽量 **最终成功**（重试、死信、人工） | 否则已提交的正向步骤无法被撤销，数据长期不一致 |

---

## 5. 两种实现风格

| 方式 | 英文 | 谁编排 | 典型通信 |
|---|---|---|---|
| **协同驱动** | Choreography | 各服务自治，无中心大脑 | 消息队列 / 事件总线；服务订阅事件后自行决定 \(T_i\) 或 \(C_i\) |
| **协调驱动** | Orchestration | 集中 **协调者**（如 Seata、Temporal workflow） | 协调者下发「执行 T₃」「执行 C₂」指令，维护 Saga 状态机 |

**Agent 类比**：OpenHands / TrackARuntime 的 **controller + loop_engine** 更接近 **Orchestration**——由控制面决定下一步是 act、replan 还是 fatal。

---

## 6. 优缺点（面试常问）

**优点**

- 无 2PC 式全局锁，**并发与可用性**更好
- 适合 **步骤多、耗时长、跨服务** 的业务（订机票+酒店+支付）

**缺点**

- **无隔离性**：\(T_1\) 已提交后、\(T_2\) 未完成前，外部可能读到 **中间态**（脏读 / 需业务语义容忍或加「待确认」状态）
- 补偿逻辑 **业务侵入强**：每个 \(T_i\) 都要设计对应的 \(C_i\) 或 Pivot 策略
- 调试与审计比单体事务难，需要 **Saga 日志 / 状态机 trace**

---

## 7. 在本项目里（Track A · M1）

本仓库 **没有实现** 分布式 Saga 框架；[`module-01/GUIDE.md`](../module-01/GUIDE.md) 与 [`module-01-exit.md`](../module-01/module-01-exit.md) 用 Saga 作 **系统等价物**，帮助把 **replan** 从「再试一次」里区分出来。

### 7.1 Agent loop ↔ Saga 映射

| Saga | Agent（TrackARuntime） |
|---|---|
| \(T_i\) 正向子事务 | 一轮 **act(tool)** + observe |
| 某步失败 | tool 失败、测试 `[retryable]`、substrate 不可用 |
| **Forward recovery** | **replan**：读 observation，**换 plan/command**，再 act（`m1_m2/evidence/5fb33372/`） |
| **Backward recovery** | 本项目中 **很少字面「撤销」**；更常见是换策略前进，而非 undo 已写文件 |
| **Pivot / 不可回退** | **fatal** 态：容器已死、fingerprint 达阈值 → **不再 replan**，Exception 短路 + save trajectory |
| Orchestrator | `loop_engine.py` + `cli.py` controller |
| Saga 日志 | `state.json` history + `trace.json` |

### 7.2 三种失败路径（对照 M1 Issue）

| 路径 | 像 Saga 的什么 | 本项目证据 |
|---|---|---|
| recoverable → replan 成功 | Forward recovery，换 \(T_{i+1}\) 策略 | `m1_m2/evidence/5fb33372/` |
| fatal substrate | 无有效 \(C_i\)，Saga **abort** | `m1_m2/evidence/7c3a04c8/` |
| 相同 args 重复 act | **假补偿**：声称 replan 但 \(T_i\) 未变 | `m1_m2/evidence/416be508/`、`6363ddfb/` → meta fingerprint fatal |

### 7.3 口述模板（≤30s，可嵌入 D1 drill）

> Agent loop 像 Saga 的 orchestration：每轮 act 是一个本地子步骤；observe 写入失败语义；**replan 是 forward recovery**——换 plan 再试；**fatal 是 abort**——环境不可补偿，必须停 loop 并落 trace。replan 不等于 blind retry，就像 Saga 补偿不等于把同一步再执行一遍。

---

## 8. 与相关概念的分界

| 概念 | 与 Saga 的关系 |
|---|---|
| **2PC / XA** | 强一致 + 锁资源；Saga 用最终一致换性能 |
| **TCC（Try-Confirm-Cancel）** | 另一种分布式事务模式；Try 阶段预留资源，Cancel 类似补偿 |
| **Agent replan** | 工程类比，非严格 Saga 实现；强调 **observe 驱动策略变更** |
| **Workflow / BPMN** | 同族：长流程 + 失败分支；Saga 偏 **数据一致性**，BPMN 偏 **流程编排** |

---

## 9. 学习记录（自填）

- **第一次理解日期**：
- **仍易混淆的点**（如 Pivot vs fatal）：
- **自己的非 Agent 例子**（订酒店/支付等）：

---

## 参考

- [module-01/GUIDE.md](../module-01/GUIDE.md) — replan ↔ Saga 补偿
- [module-01/module-01-exit.md](../module-01/module-01-exit.md) — 原理口述稿
- [case-library/README.md](../case-library/README.md) — CTL 类（控制面与终止）
