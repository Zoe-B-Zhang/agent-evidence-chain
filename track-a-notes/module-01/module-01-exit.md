# M1 Exit — 自证检查清单

**完成日期**：2026-07-05

## 原理（口述稿，≤300 字）

Agent 不是单次 Chat，而是 **有状态任务机**：parse → plan → act(tool) → observe →（失败则）replan → done。等价于工作流引擎 + [Saga 补偿](../study-notes/saga-compensation.md)——工具失败不能把最终答案直接给用户，必须把 **带语义层级的 observation** 写回状态机，再决定 replan 还是 fatal 终止。

三类 silent loop 对应三层 fix：**observe 未升维 fatal**（#803）· **分类有了但 controller 未 enforce**（#4575）· **replan 无 progress**（#4579/#5099）。Fatal 必须 Exception 短路并 save trajectory，不能当 recoverable observation 继续烧 API。max_rounds 是兜底熔断，不是主修复。

## 自己的例子

- **载体**：TrackARuntime
- **A 侧（replan 成功）**
  - 命令：`python cli.py run --task "fix test"`
  - 证据：`TrackARuntime/m1_m2/evidence/5fb33372/state.json`
  - 要点：round1 observe `[retryable]` → replan → round2 plan **引用** observation → `[recoverable]` → `success: true`
- **B 侧（fatal 短路）**
  - 命令：`python cli.py run --task "container death" --simulate-container-death 1`
  - 证据：`TrackARuntime/m1_m2/evidence/7c3a04c8/state.json`、`trace.json`
  - 要点：round2 act 后 container dead → `error_class: fatal` → FatalAgentError → **无** round3 replan
- **演示一句话**：同一 runtime、同一 controller，**错误分类不同 → 策略不同**（M1-K05）

## Bad Case 口述（Case 3）

- **现象**：300 页维修 PDF，问轴承过热前兆，回答遗漏第 287 页「振动频率异常」。
- **根因**：全量塞 context，attention 中间弱化；未 observe「检索不充分」。
- **工程等价**：无索引的全表扫描，而非分层索引 + 按需下钻。
- **监控**：输入 token 分布、摘要层 vs 原文层命中率。
- **回滚**：恢复「摘要优先」路由配置。
- **与 M1 关联**：与 #803 同属 observe 信号不足，但 Case 3 是 **检索策略** 问题，#803 是 **substrate fatal 未升维**；fix 都在 observe 层加强结构化信号，再驱动 replan 或 fatal。

## M1 D1 — 60s Drill 口述稿（初稿，请自行计时）

> 目标 ≤60s · 提纲见 [`interview/DRILLS.md`](../interview/DRILLS.md) M1 D1

1. **状态机**：Agent = parse → plan → act → observe → replan/success；不是一问一答 Chat。
2. **系统等价**：工作流引擎 + [Saga 补偿](../study-notes/saga-compensation.md)；observe 是传感器读数，replan 是补偿策略。
3. **自己例子**：`m1_m2/evidence/5fb33372` round1 测试失败 `[retryable]`，round2 plan 引用 observation 后通过；若 substrate 死了（`7c3a04c8`），fatal 必须立刻 interrupt，不能继续 replan 烧 API。

**计时**：____ 秒（Learner 自填）  
**卡壳点**：____（Learner 自填）

## Exit Criteria

- [x] 3 分钟白板讲清 Agent loop（口述稿 + day1–3 笔记）
- [x] 能演示 replan trace（`5fb33372`）与 Fatal 中断（`7c3a04c8` + `--simulate-container-death 1`）
- [x] Case 3 口述完整（见上）
- [x] Day1–3 笔记已完成（`module-01-day1/2/3.md` + Day3 校准结论）
- [x] [`rubric.md`](rubric.md) 已填，M1 核心 K 均 ≥2.0（平均 2.6，K02/K05/K06 = 3）

## 未达标项与补救计划

| 项 | 状态 | 补救 |
|---|---|---|
| D1 60s 计时自证 | 口述稿已起草，**计时未填** | Exit 前对镜/录音练 1 次，填「计时 / 卡壳点」 |
| K01 / K03 报 2 非 3 | 可接受（Exit 要求 ≥2.0） | L3 可选：补 FSM 扩展点笔记、replan policy 表 Markdown |
| K04 未入 rubric 表 | 模块 Exit 表未列 K04 | Day2 已写 max_rounds 兜底；M2 前可单独自评 |

**M1 结论**：Day1–3 + runtime 证据 + rubric **可视为 Exit 就绪**；补完 D1 计时即可进 M2。
