# M1 知识工程点 · Agent Runtime

> **生命线**：① **控制面** · **模块考核句**：**「我会 Agent 闭环」**  
> **体系位置**：[`KNOWLEDGE-SYSTEM.md` §7 M1](../curriculum/00-knowledge-system.md) · **教案**：[`COURSE.md` 第 1 课](../curriculum/01-course.md)  
> 索引：[tutor/README.md](../tutor/README.md) · 评分：[MASTERY-RUBRIC.md](../MASTERY-RUBRIC.md) · Issue：[issues.md](issues.md)

**本模块共 6 个核心 K 点**（M1-K01–K06），另有 3 个生产扩展 K 点（M1-K07–K09）用于求职增强。Level 定义：[L1 能讲清 · L2 能对照 runtime debug · L3 能设计策略/扩展代码](../tutor/README.md#0-能力递进模型)

> **Issue 标注约定**：Runtime 新能力若在 [`issues.md`](issues.md) **无对应练习**，用  
> `> **Issue 覆盖**：无对应 Issue — …`  
> 标明。

---

## 速查表

| ID | 知识点 | What 摘要 | Runtime 绑定 | Issue |
|---|---|---|---|---|
| M1-K01 | Agent = 状态机非 Chat | 带 round/phase 的任务机 | `loop_engine.py`；`context_manager` | I01–I03；**四层 context 无独立 Issue** |
| M1-K02 | observe = 结构化信号 | branch 信号，非 log | `_observe_tests` 返回值 | I01 / I02 |
| M1-K03 | replan = 条件策略 | Saga + 可插拔 plan | `_make_plan`；`llm_client` | I03B；**MockLLM 无独立 Issue** |
| M1-K04 | 多层终止 | max_rounds + checkpoint | `LoopConfig`；checkpoint/resume | I01–I03；**checkpoint → I05** |
| M1-K05 | recoverable / fatal | 错误分类决定策略 | `errors.py`, `_docker_exec` | I01 / I02 |
| M1-K06 | Loop fingerprint | meta 层无进展检测 | `_check_fingerprint_loop` | I03A / I03B |
| M1-K07 | Runtime Scale（扩展） | queue / worker / lease / idempotency | 设计题；TrackARuntime 未实现 | [Case 13](../case-library/cases/case-13-worker-death-checkpoint-resume.md) + [SOP](../case-library/sops/sop-case-13-worker-death-checkpoint-resume.md) |
| M1-K08 | Memory Policy（扩展） | memory 写入、版本、回滚、污染治理 | `context_manager` 仅短期组装；持久 memory 未实现 | [Case 14](../case-library/cases/case-14-memory-poisoning-version-rollback.md) + [SOP](../case-library/sops/sop-case-14-memory-poisoning-version-rollback.md) |
| M1-K09 | Goal Change（扩展） | cancel / interrupt / user edit 的状态转换 | 设计题；TrackARuntime 未实现 | [Case 18](../case-library/cases/case-18-approval-fatigue-destructive-action.md) + [SOP](../case-library/sops/sop-case-18-approval-fatigue-destructive-action.md) |

**面试 60s**：Agent = 工作流 + [Saga 补偿](../study-notes/saga-compensation.md)；Fatal 必须 interrupt 并 save trajectory，不能当普通 observation 继续 loop。可插拔 `LLMClient`（默认 Mock）与 checkpoint 属控制面延伸。

---

## M1-K01 · Agent = 状态机非 Chat

### What（是什么）

Agent 不是「一问一答 Chat」，而是 **带 round/phase 的有状态任务机**；每次 tool 结果必须写回状态，再决定下一步。

### Why（为什么必须有）

无 persistent 状态则无法审计「第几轮、为何停、为何继续」；Chat 式单轮补全 **无法表达有副作用的多步任务**。

### How（怎么做）

| 层 | 实现 |
|---|---|
| **TrackARuntime** | `loop_engine.py` — `Phase` enum、`_record_phase()`；5 态：parse_intent → plan → act → observe → replan → done |
| **四层上下文** | `context_manager.py`：system / long-term / short-term / current；`_make_plan` 前组装（long-term 仅为当前 task 摘要，**非持久记忆库**） |
| **metrics** | `metrics.py` → `metrics-<run_id>.json`（latency / token / cost 估算） |
| **传统系统等价** | 工作流引擎（BPMN）、Saga 补偿 |

> **Issue 覆盖**：**四层上下文 / metrics 落盘 — 无对应 Issue**（自行对照 `metrics-*.json` 与 `context_manager.py`）。子 Agent、跨 run 记忆仍为缺口（不写入「已覆盖」）。

### When wrong（典型故障）

把 Agent 当 Chat 用 → 无 round 记录、失败靠「再生成」→ 无法 debug silent loop。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能画 **5 态闭环**；口述与 **工作流引擎 / Saga 补偿** 的系统等价。 |
| **L2** | 能打开 `m1_m2/evidence/5fb33372/state.json`，**指读** history 中各 `phase` 与 `round` 顺序；说明 success 退出发生在哪一轮、哪一 phase。 |
| **L3** | 能设计 FSM **扩展点**：如新增 `await_user` phase、sub-agent delegate；说明新 phase 如何进入 history 与终止条件；能口述四层 context 各装什么。 |

### 延伸阅读

全模块基础；Case 3（context 策略也走同一状态机）。**与 M2**：M1 管 **loop 叙事**（state）；M2 管 **tool 事实**（trace）。

---

## M1-K02 · observe = 结构化信号

### What（是什么）

observe 不是把 stderr 贴给 LLM，而是 **带语义层级的结构化 branch 信号**——决定走 replan、success 还是 fatal。

### Why（为什么必须有）

log 只给人看、不参与分支 → loop **无法自动 replan/fatal** → silent loop（#803）。

### How（怎么做）

| 语义 | 含义 | TrackARuntime |
|---|---|---|
| **retryable** | 单步可再试（同一 plan 内） | history 中 `[retryable]` |
| **recoverable** | in-loop 可补偿 → replan | history 中 `[recoverable]` |
| **fatal** | substrate 不可补偿 → Exception 短路 | `trace.json` 的 `error_class: fatal` |

**传统系统等价**：health check → branch（healthy / degraded / dead）。

### When wrong（典型故障）

#803：container 已死，observe 只是 `returncode=-1` 而不 **升维 fatal** → loop 在尸体上空转。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能区分 **log** vs **branch 信号**；列举 retryable / recoverable / fatal 三类含义。 |
| **L2** | 能读 `state.json` observe 行与 `trace.json` 的 `error_class: fatal`；对照 #803。 |
| **L3** | 能设计 **observation schema**（level、retryable、error_code、substrate_health）。 |

### 延伸阅读

[oss-803](../case-library/oss-incidents/oss-803-mini-swe-container-silent-loop.md)（OBS）；#5099（单步 observe 正确但无 progress）。

---

## M1-K03 · replan = 条件策略

### What（是什么）

replan 是 **读 observation 后的补偿策略**（Saga forward recovery），不是失败后的 blind retry；**plan/command 必须能变**。

### Why（为什么必须有）

blind retry 无进展 → 烧轮次与成本；假 replan（#5099）声称 replan 但 tool+args 不变。

### How（怎么做）

| | 真 replan | 假 replan |
|---|---|---|
| **特征** | round2 plan **引用** round1 observation | `--pseudo-replan`：tool+args 不变 |
| **证据 run** | `5fb33372` | `6363ddfb` |
| **TrackARuntime** | `_make_plan()`、replan phase 写入 history | 对照 demo |

**可插拔 plan 源**：

| 模式 | 行为 |
|---|---|
| 默认（无 `--llm`） | 硬编码 plan（兼容旧证据） |
| `--llm mock` | `MockLLMClient.generate_plan`；经 `model_router` 选模型名；记录 token/cost 估算 |
| 真实 OpenAI | **未实现**；扩展见 `TrackARuntime/DESIGN.md` §4.1 |

> **Issue 覆盖**：**MockLLM / `--llm mock` — 无对应 Issue**（推荐命令见 GUIDE；与 I02 A 跑兼容）。

### When wrong（典型故障）

#4575 家族：fatal 不应进 replan；#5099：replan 在走但 args 不变。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能口述：replan ≠ 相同 command 再跑；触发条件通常是 observe 失败且未 fatal。 |
| **L2** | 能解释 `5fb33372` vs `6363ddfb` 的 plan/command 差异；能对比有/无 `--llm mock` 的 metrics。 |
| **L3** | 能写 **replan policy 表**：`(error_class, round, fingerprint_ok) → {replan, fatal, done}`；能按 DESIGN §4.1 口述如何接真实 LLM。 |

### 延伸阅读

[oss-5099](../case-library/oss-incidents/oss-5099-langgraph-pseudo-replan-loop.md)（CTL / 假恢复）。

---

## M1-K04 · 多层终止

### What（是什么）

除 success/fatal 外，需 **多层熔断**（max_rounds、step_limit、可选 cost_limit）作兜底。

### Why（为什么必须有）

**不能** 靠 max_rounds 单独修复 fatal 或 silent loop；step_limit 仅 **延迟暴露** 问题（#803）。

### How（怎么做）

| 终止原因 | TrackARuntime |
|---|---|
| success / FatalAgentError / Max rounds | `LoopConfig.max_rounds`、`loop_engine.run()` 终止分支 |
| checkpoint / resume | `--checkpoint-dir` 每轮落盘；`--resume-from` 恢复后继续 `run()`（`llm_client` **不**写入 checkpoint，resume 后需再传 `--llm mock`） |
| cost_limit（L3） | **未实现硬熔断**；`CostMonitor` 仅记账（见 M3）；类比 PR #832 wall_time_limit |

**与 M2-K04**：M1 = loop 级熔断；M2 = tool 级 timeout——互补。

> **Issue 覆盖**：checkpoint/resume → [M1-I05](issues.md)。**cost 硬限额终止 — 无对应 Issue**（且代码未做硬拦）。

### When wrong（典型故障）

只靠 max_rounds 烧满轮次才发现 silent loop，而非 early fatal。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能列举终止原因；知 **fatal 优先于** 烧满轮次。 |
| **L2** | 能指 history **末行 DONE 原因**：`5fb33372` success / `7c3a04c8` fatal / `416be508` fingerprint fatal；能跑通 I05 checkpoint。 |
| **L3** | 能在 `LoopConfig` 增加 **cost_limit** 或 round 开始前 substrate health check。 |

### 延伸阅读

- [Case 09](../case-library/cases/case-09-token-burn-rate-limit-cascade.md)（CTL+SLO · Token 空转 → 429 雪崩；对照 #803 / #4579）
- [oss-803](../case-library/oss-incidents/oss-803-mini-swe-container-silent-loop.md)（#803 空转烧 API 直至 step/cost limit）

---

## M1-K05 · 错误分类 recoverable / fatal

### What（是什么）

同一 runtime 上，**错误分类决定策略**——recoverable/retryable → replan；fatal → Exception 短路，不进 replan policy。

### Why（为什么必须有）

分类错 → fatal 进 replan（#4575）或 recoverable 不 replan → 策略与 substrate 状态不匹配。

### How（怎么做）

| 类 | 策略 | TrackARuntime |
|---|---|---|
| retryable | 单步再试 | observe 标记 |
| recoverable | replan | `5fb33372` A run |
| fatal | Exception 短路 | `errors.py`、`FatalAgentError`、`7c3a04c8` B run |

### When wrong（典型故障）

#803（observe 未升维）vs #4575（信号有了 controller 未 enforce）。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能口述 retryable / recoverable / fatal 三分。 |
| **L2** | 能 **A/B 对照** `5fb33372` vs `7c3a04c8`。 |
| **L3** | 能讲清 `ErrorClass` enum、`FatalAgentError`、fatal 路径 `trace.error_class: fatal`。 |

### 延伸阅读

[oss-803](../case-library/oss-incidents/oss-803-mini-swe-container-silent-loop.md)、[oss-4575](../case-library/oss-incidents/oss-4575-openhands-errorobs-vs-fatal.md)。

---

## M1-K06 · Loop fingerprint（meta 层）

### What（是什么）

单步 observe 可以 retryable，但 **跨轮 (tool, args) 重复** 说明无 progress——meta 层 fingerprint 应 **override replan**，达阈值 fatal。

### Why（为什么必须有）

#5099 类：**单步 observe 正确** 但 loop 无进展 → 需要 controller 级 meta 断路器。

### How（怎么做）

| | 说明 |
|---|---|
| **算法** | 对 `(tool, command)` hash 累计；**3 次相同** → fatal |
| **TrackARuntime** | `_check_fingerprint_loop()` — **act 前**调用 |
| **传统等价** | 无进展检测 / stuck detector（OpenHands `_is_stuck()`） |

### When wrong（典型故障）

#4579 / #5099：replan 无 progress；对照 `5fb33372` command **变化** + success。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能口述 fingerprint 含义与阈值。 |
| **L2** | 能读 `416be508` / `6363ddfb`：相同 command×3；history 末行 `Loop fingerprint detected...`。 |
| **L3** | 能设计 fingerprint **存储**（deque / Redis / state 字段）、阈值可配置、按 tool 分桶。 |

### 延伸阅读

[oss-4579](../case-library/oss-incidents/oss-4579-openhands-stuck-loop-fatal.md)、[oss-5099](../case-library/oss-incidents/oss-5099-langgraph-pseudo-replan-loop.md)。

---

## 生产扩展 K 点（求职增强）

> 扩展详解：[`02-production-extension-packs.md` P4](../curriculum/02-production-extension-packs.md#6-p4--runtime-scale--memory--state)。本节不改变 M1 核心 Exit；用于回答「单次 Agent loop 如何进入多任务生产 runtime」。

### M1-K07 · Runtime Scale

**What**：把单次 Agent loop 放进 queue / worker / lease / checkpoint / cancellation 组成的任务系统。

**Why**：教学 run 能证明一个任务可靠，但岗位会追问「1 万个任务同时跑，worker 死亡、重复执行、副作用重放怎么办」。

**How**：

| 能力 | 设计要点 |
|---|---|
| Job queue | HTTP request 不直接阻塞跑 Agent；写入任务队列 |
| Worker lease | worker 领取任务有租约，死亡后可被重新认领 |
| Checkpoint persistence | 每轮状态落盘，resume 时恢复 phase/round/history |
| Idempotency | 重试不能重复执行写文件、发邮件、下单等副作用 |
| Cancellation | 用户取消、超时取消、管理员 kill 都是控制面状态 |
| Backpressure | 队列积压时按 tenant quota 限流或拒绝 |

**Prove**：能复盘 [Case 13](../case-library/cases/case-13-worker-death-checkpoint-resume.md) 与 [SOP](../case-library/sops/sop-case-13-worker-death-checkpoint-resume.md)，白板画 `submit task → queue → worker lease → loop → checkpoint → done/dead-letter`；能解释 retry、resume、replay、idempotency 的区别。

### M1-K08 · Memory Policy

**What**：长期 memory 是持久状态，不是普通 context；写入、读取、删除、回滚都需要 policy。

**Why**：错误 memory 会跨 run 污染后续行为；恶意输入可能把 prompt injection 固化成长期偏好。

**How**：

| 类型 | 说明 | 风险 |
|---|---|---|
| session memory | 当前会话短期摘要 | 摘要丢关键信息 |
| project memory | 项目约定、路径、命令 | 过期后误导 Agent |
| user preference | 用户偏好 | 被恶意输入污染 |
| tool-derived memory | 工具观察写入 | provenance 不清导致信任错层 |

**Prove**：能复盘 [Case 14](../case-library/cases/case-14-memory-poisoning-version-rollback.md) 与 [SOP](../case-library/sops/sop-case-14-memory-poisoning-version-rollback.md)，说明 context、checkpoint、memory 的区别；能设计 memory write policy：来源、审批、版本、TTL、删除、回滚。

### M1-K09 · Goal Change

**What**：用户中途取消、改目标、插入约束时，Agent 需要显式状态转换，而不是继续执行旧 plan。

**Why**：长任务中用户意图变化很常见；无 interrupt 状态会导致 Agent 做完已经不需要的副作用。

**How**：

| 事件 | 状态动作 |
|---|---|
| user_cancel | cancel token → close in-flight span → checkpoint cancelled |
| user_edit_goal | invalidate current plan → replan with new goal |
| approval_reject | mark tool call denied → choose safe alternative |
| timeout_cancel | fatal 或 recoverable 取决于 substrate health |

**Prove**：能复盘 [Case 18](../case-library/cases/case-18-approval-fatigue-destructive-action.md) 与 [SOP](../case-library/sops/sop-case-18-approval-fatigue-destructive-action.md)，把 `await_user`、`cancelled`、`replan_requested` 加入 M1 状态机设计，并说明如何写入 `state.json` / `trace.json`。

---

## 三类 silent loop × K 点

| 类型 | 代表 | 主 K 点 | 缺陷层 | fix 形态 |
|---|---|---|---|---|
| 传感器错 | #803 / #807 | K02, K05 | observe 未升维 fatal | execute detect + raise |
| 断路器没跳 | #4573→#4575 | K05, K03 | controller 未 enforce | fatal 不进 recoverable 通道 |
| 无进展空转 | #4579 / #5099 | K06, K03 | replan 无 progress | fingerprint → dispatch 前 fatal |

---

## K 点 × Issue 对照

| Issue ID | OSS | 主 K 点 | Runtime 命令 | 证据 run |
|---|---|---|---|---|
| I01 | #803 | K02, K05, K04 | `--simulate-container-death 1` | `7c3a04c8/` |
| I02 | #4575 | K05, K03 | A/B fix test + container death | `5fb33372/` / `7c3a04c8/` |
| I03A | #4579 | K03, K06, K05 | `--always-fail-tests --max-rounds 5` | `416be508/` |
| I03B | #5099 | K03, K02, K06 | 上列 + `--pseudo-replan` | `6363ddfb/` |
| I05 | Runtime | K04 | `--checkpoint-dir` + `--resume-from` | 自建 checkpoint 目录 |

| Runtime 能力 | Issue |
|---|---|
| `--llm mock` / `MockLLMClient` | **无对应 Issue** |
| `context_manager` 四层组装 | **无对应 Issue** |
| `metrics-*.json` | **无对应 Issue** |
| cost 硬限额 | **无对应 Issue**（未实现） |

> **`--task` 仅为标签**；行为由 **flag** 决定。见 [issues.md](issues.md)。

---

## M1 → M2 衔接

| M1 已会（闭环） | M2 将加深 |
|---|---|
| observe 语义层级 | tool 层 timeout / stalled 契约 |
| state.json 叙事 | trace.json 逐步证据 |
| fatal interrupt | allowlist + `fallback_used` |

---

## 学习记录（自填）

| K 点 | 自评 L | 证据 run / 日期 |
|---|---|---|
| K01 | | |
| K02 | | |
| K03 | | |
| K04 | | |
| K05 | | |
| K06 | | |
| K07（扩展） | | Runtime Scale 白板 |
| K08（扩展） | | Memory policy 表 |
| K09（扩展） | | Goal change 状态图 |
