# Track A 课程教案 · 以 TrackARuntime 为考核载体

> **角色**：导师设计的 **一门课**，不是索引。学完各章机理 + 完成规定动作，应能达到模块 **Exit**（核心 K 均分 ≥2.0，且 ≥1 个 K=3）并通过对应 interview drill。  
> **Greenhand 先读**：[`KNOWLEDGE-SYSTEM.md`](00-knowledge-system.md)（五条生命线 + 26 K 矩阵）  
> **索引速查**：[`KNOWLEDGE-MAP.md`](../KNOWLEDGE-MAP.md)  
> **执行细节**（Issue Day1–3、rubric 逐条）：各 `module-XX/` 目录。

---

## 0. 课程怎么学、怎样算通过

### 0.1 你在学什么

Track A 不是「会用 ChatGPT 写代码」，而是证明你能 **工程化地交付与运维 AI Agent 系统**。  
五条 **工程生命线**（详见 [`KNOWLEDGE-SYSTEM.md` §2](00-knowledge-system.md)）：

```text
M1  控制面：闭环会不会停、会不会瞎转（Agent loop）
M2  工具边界：工具会不会越权、observe 会不会说谎（Tool + Trace）
M3  配置交付：配置变更会不会把线上搞崩（Harness）
M4  质量门禁：质量有没有数据门禁（Eval）
M5  运维响应：线上坏了你会不会值班（Bad Case + SOP）
```

唯一工程考场：[`TrackARuntime/`](../TrackARuntime/)。所有「通过」都要有 **可打开的 evidence 文件**。

### 0.2 每模块固定学习路径（导师规定）

| 步骤 | 做什么 | 产出 | 对应 Level |
|---|---|---|---|
| 1 | 读 **本章** + 模块 `knowledge.md` 速查 | 能口述考核句 | L1 |
| 2 | Issue **Day1→Day3** 三日校准 | day1/2/3 笔记 | L2 认知 |
| 3 | 跑 **Runtime 任务** + 指读 JSON | `m1_m2/evidence/` 证据 | L2 实操 |
| 4 | 可选：在 runtime **写一小段设计/代码** | PR 级 diff 或 stub | L3 |
| 5 | `rubric.md` 自评 + **INTERVIEW-DRILLS** | Exit 勾选 | 出口 |

**Exit 硬门槛**（[`MASTERY-RUBRIC.md`](../MASTERY-RUBRIC.md)）：该模块核心 K **平均分 ≥ 2.0**，且 **至少 1 个 K = 3**。

### 0.3 五条证据链（全课共用）

| 文件 | 回答的问题 | 主要模块 |
|---|---|---|
| `state.json` | 状态机 **叙事**：第几轮、什么 phase、为何 DONE | M1 |
| `trace.json` | **事实**：调了什么 tool、多久、是否 fallback | M1/M2/M5 |
| `metrics-<run_id>.json` | **估算**：token / cost / route（教学 stub） | M1/M3/M5 |
| `harness-report.json` | **配置发布**是否可上线 | M3 |
| `rollout-state.json` | **跨 tick 回滚/锁定**（L3） | M3 |
| `evaluation-report.md/.json` | **全任务集**是否 regression（含 `baseline_meta` / `category_split`） | M4 |

**命令权威来源**：[`KNOWLEDGE-SYSTEM.md` §7.1](00-knowledge-system.md) · 速查 [`KNOWLEDGE-MAP.md` §8](../KNOWLEDGE-MAP.md)。原则：**所验 ⊆ 所学**——过关动作只考本章已教的机理。

---

## 第 1 课 · Agent 闭环（M1）

### 1.0 模块导论（Why M1）

| | |
|---|---|
| **生命线** | ① **控制面** — 任务能否可靠跑完、何时停、为何停 |
| **前置** | 无（全课起点） |
| **不学会** | loop 空转、fatal 被当普通 observation 继续 replan |
| **学完能回答** | Agent 与 Chat 本质区别？observe 为何必须是 branch 信号？三类 silent loop 各缺哪一层？plan 源如何可插拔？checkpoint 恢复什么？ |

**K 点详卡**：[`module-01/knowledge.md`](../module-01/knowledge.md) · **体系位置**：[`KNOWLEDGE-SYSTEM.md` §7 M1](00-knowledge-system.md)

### 1.0.1 本章校准 Case

| 优先 | Case | 补强 K 点 | 啃不动时 |
|---|---|---|---|
| **深读** | [Case 03](../case-library/cases/case-03-context-lost-in-middle.md) | M1-K01、M1-K03 | [`USAGE`](../../USAGE.md) §1.1 → [`module-01/knowledge`](../module-01/knowledge.md) |
| 交叉 | [Case 06](../case-library/cases/case-06-prompt-injection.md)（会话状态） | M1-K05 | 同上 |
| 扩展 | [Case 09](../case-library/cases/case-09-token-burn-rate-limit-cascade.md)（silent loop / quota） | M1-K06、M1-K05 | 同上 |

### 1.1 考核句

**「我会 Agent 闭环」**——讲清 plan→act→observe→replan；对照 `state.json`/`trace.json` 说明 **为何停、为何继续**；**fatal 必须 interrupt**，不能当普通 observation 继续 loop。

### 1.2 核心概念（What）

Agent 不是 Chat，是 **带 round/phase 的有状态任务机**；用户一句话触发的是 **多轮、有副作用的任务**，不是单轮补全。

| | Chat | Agent |
|---|---|---|
| 状态 | 无 persistent round | 每轮 act 可能改文件/跑测试 |
| 失败 | 常「再生成一段文字」 | observe **必须结构化**，决定分支 |
| 终止 | 自然结束 | fatal 必须 **短路** 整个 loop |

### 1.3 工作机制（How）

```text
parse_intent → plan → act(tool) → observe → 成功? → done
                              ↑失败且非 fatal↓
                           replan（换策略，不是原样再跑）
```

**与 Chat 的本质区别**（Why 需要状态机）：

- Chat：无 persistent round；无 tool 副作用；失败常「再生成一段文字」。
- Agent：每一轮 **act 可能改文件/跑测试**；observe **必须结构化**，决定分支；**fatal 必须短路**整个 loop。

**系统等价**：工作流引擎 + [**Saga 补偿**](../study-notes/saga-compensation.md)——replan 是 **读 observe 后的 forward recovery**；fatal 是 **abort**，不是再试一次。

**控制面延伸（须学，与过关命令对齐）**：

| 能力 | 教什么 | Runtime |
|---|---|---|
| 可插拔 plan | 默认硬编码 plan；`--llm mock` → `MockLLMClient`（无真实 API） | `llm_client.py` · DESIGN §4.1 |
| 四层上下文 | system / long-term / short-term / current 在 plan 前组装；long-term **不是**持久记忆库 | `context_manager.py` |
| checkpoint | 每轮落盘；`--resume-from` 续跑；`llm_client` **不**进 checkpoint，resume 须再传 `--llm mock` | M1-I05 |
| metrics | run 结束写 `metrics-*.json`（token/cost/route 估算） | `metrics.py` |

### 1.4 三个必须刻进脑子的机制

#### （1）observe 是传感器，不是日志

| 类型 | 作用 | 错用后果 |
|---|---|---|
| **log** | 给人看 | 不参与分支 → 无法自动 replan |
| **branch 信号** | 驱动 replan / fatal / success | 正确 |

`retryable` / `recoverable` / **fatal** 三类语义不同：

- **retryable**：单步可再试（同一 plan 内）。
- **recoverable**：in-loop 可补偿 → **replan**（plan/command 要变）。
- **fatal**：substrate 不可补偿（容器死了）→ **Exception 短路**，禁止 replan。

**#803 教训**：container 已死，若 observe 只是 `returncode=-1` 而不 **升维 fatal**，loop 会在尸体上空转——silent loop。

#### （2）replan ≠ blind retry

真 replan：`5fb33372` 第二轮 plan **引用**第一轮 observation。  
假 replan：`6363ddfb` `--pseudo-replan`——声称 replan，**tool+args 不变** → 无进展。

#### （3）fingerprint：meta 层 override replan

单步 observe 可以 retryable，但 **(tool, args) 跨轮重复** 说明没有 progress。  
M1 在 **dispatch 前** 用 fingerprint 计数，≥3 次相同 → **fatal**（`416be508`）。

这与 #5099「replan 在走但 args 不变」同构——**控制面要有 meta 断路器**。

### 1.5 失败模式（When wrong）

| 类型 | 代表 | 缺陷 | fix 方向 |
|---|---|---|---|
| 传感器错 | #803 | observe 未 fatal | substrate 死 → raise |
| 断路器没跳 | #4575 | fatal 进了 recoverable | controller enforce |
| 无进展空转 | #4579/#5099 | replan 无 progress | fingerprint |

### 1.6 与 M2 的接口

| M1 产出 | M2 接什么 |
|---|---|
| observe 语义层级 | tool 层 timeout / stalled 契约 |
| `state.json` 叙事 | `trace.json` 逐步事实 |
| fatal interrupt | allowlist + schema + HITL + `fallback_used` |

### 1.7 过关动作（Prove）

> 下列命令均在第 1 课已教范围内；`--llm mock` / checkpoint 见上表「控制面延伸」。

```powershell
cd TrackARuntime
python cli.py run --task "fix failing test" --llm mock
python cli.py run --task "container death" --simulate-container-death 1
python cli.py run --task "stuck loop" --always-fail-tests --max-rounds 5
python cli.py run --task "pseudo replan" --always-fail-tests --pseudo-replan --max-rounds 5
# 扩展（M1-I05）：checkpoint
python cli.py run --task "ckpt" --llm mock --checkpoint-dir m1_m2/evidence/checkpoints
# 中断后：python cli.py run --task "ckpt" --llm mock --resume-from m1_m2/evidence/checkpoints/<file>.json
```

**L2 出口**：能指 `5fb33372` vs `7c3a04c8` vs `416be508` 的 **history 末行 DONE 原因**；能打开同次 run 的 `metrics-*.json` 口述估算字段。  
**L3 出口**：能写 replan policy 表或改 `ErrorClass` / fingerprint 阈值；能口述 cost 硬限额应接在哪里（当前仅记账）。  
**Drill**：60s Agent loop（见 [`INTERVIEW-DRILLS.md`](../interview/DRILLS.md) M1）。

**深读**：[`module-01/knowledge.md`](../module-01/knowledge.md) · [`module-01/GUIDE.md`](../module-01/GUIDE.md) · [`module-01/issues.md`](../module-01/issues.md)

---

## 第 2 课 · Tool + Trace（M2）

### 2.0 模块导论（Why M2）

| | |
|---|---|
| **生命线** | ② **工具边界** — 副作用是否受控、执行是否可审计 |
| **前置** | M1（act/observe 发生在 loop 内） |
| **不学会** | 越权 tool、timeout 误判导致假失败/真 hang、trace 逐步讲不清 |
| **学完能回答** | Tool 为何不是任意 shell？allowlist→schema→HITL 各拦什么？timeout 两极各是什么？state 与 trace 分工？真实只读工具为何默认不进主 loop？ |

**K 点详卡**：[`module-02/knowledge.md`](../module-02/knowledge.md) · **体系位置**：[`KNOWLEDGE-SYSTEM.md` §7 M2](00-knowledge-system.md)

### 2.0.1 本章校准 Case

| 优先 | Case | 补强 K 点 | 啃不动时 |
|---|---|---|---|
| **深读** | [Case 06](../case-library/cases/case-06-prompt-injection.md) | M2-K01、K03 | [`USAGE`](../../USAGE.md) §1.1 → `module-02/knowledge` |
| **深读** | [Case 07](../case-library/cases/case-07-latency-avalanche.md) | M2-K02、K04/K05 | 同上 |
| 扩展 | [Case 09](../case-library/cases/case-09-token-burn-rate-limit-cascade.md) | M1-K06（跨模块） | 对照 M1 fingerprint |

### 2.1 考核句

**「我会 Tool + Trace」**——tool **受控、可审计**；observe 契约清晰，含 **timeout 切太早（#7355）** 与 **hang 永不切（#8448）** 两极。

### 2.2 核心概念（What）

M1 的 `state.json` 讲 **故事**（第几轮 replan 了）；M2 的 `trace.json` 讲 **物证**（这一刀 tool 调了什么、花了多久、是否被拒绝）。

**Tool 为什么不是 shell 随便跑**（Why）：

- 有 **副作用**（写盘、exec）→ 必须 **allowlist**（等价 sudoers / API Gateway 路由）。
- 不同 tool **SLA 不同** → 不能全局 30s timeout。
- 越权必须在 **进 handler 前** 拒绝，并 `record()` 进 trace（`fallback_used: true`）。

### 2.3 工作机制（How）

在 `tool_executor.call()` **之前** 拦截，而不是让 LLM 从 stderr 猜：

| 层 | TrackARuntime | 课内要求 |
|---|---|---|
| 0 Allowlist | **已实现** | 必会：`demo-allowlist` |
| 1 Schema | **已实现**（`ToolSpec` + `validate_schema`） | 必会：M2-I03；非法 args 不进 handler |
| 2 HITL | **已实现**（`dangerous` + `--require-hitl`） | 必会：M2-I04 |
| Dry-run | **未做** | L3 设计 |
| 分路径 timeout | `_timeouts` **有配置**；`call()` **未强制中断** | 必会口述「配置有 / enforce 无」 |
| 真实只读 | `read_file`/`grep` 沙箱 **有**；主 loop **默认不调** | 必会诚实边界 |

另：**RETRYABLE 指数退避**（`--max-retries`）已实现——课内知晓；无独立 Issue（见 knowledge 标注）。

**与 M1 分工**：三层防御 = **tool 侧** 防坏请求；fingerprint = **loop 侧** 抓无进展。

### 2.4 失败模式（When wrong）

**核心句：timeout ≠ kill**——timeout 只表示「我不再等了」，进程可能仍在跑。

| 极性 | Issue | 现象 | 正确 observe 语义 |
|---|---|---|---|
| 切太早 | #7355 | 120s 测试被 30s 切 | **in_flight** 或 long-running tier，勿 fake failed |
| 永不切 | #8448 | grep 无输出 hang | **stalled** / idle cap，span 必须闭合 |

Case 7 是全链路版：**优化错层**（ASR/TTS）而瓶颈在 tool/LLM span——M5 会再用 SOP 讲。

### 2.5 过关动作（Prove）

```powershell
cd TrackARuntime
python cli.py demo-allowlist --tool rm_rf
python cli.py demo-no-output-hang --idle-timeout 1
python cli.py run --task "fix failing test" --llm mock   # 指读 trace latency_ms；读 _timeouts
python cli.py run --task "hitl check" --require-hitl       # M2-I04
python -m unittest tests.test_tool_executor -v             # M2-I03 schema 相关用例
```

**L2 出口**：**逐步讲** 一次完整 `trace.json`；对照 #7355 vs #8448；能口述 schema/HITL 与 allowlist 的差异。  
**L3 出口**：`resolve_timeout` enforce 或 dry-run 设计；或让 loop 调用 `read_file`。  
**Drill**：M2 D1 Tool+Trace · D2 #7355 debug story。

**深读**：[`module-02/knowledge.md`](../module-02/knowledge.md) · [`module-02/issues.md`](../module-02/issues.md)

---

## 第 3 课 · Harness 交付（M3）

### 3.0 模块导论（Why M3）

| | |
|---|---|
| **生命线** | ③ **配置交付** — Prompt/模型配置能否安全发布 |
| **前置** | M2（理解单次 run 的 trace 后再谈全局配置变更） |
| **不学会** | 改一句 Prompt 全量上线、靠换模型救火、无 rollback |
| **学完能回答** | Harness 与 Agent loop 改什么不同？双护栏指什么？gray 与 rollback 如何配合？router/token/cost stub 与「成本熔断」差在哪？ |

**K 点详卡**：[`module-03/knowledge.md`](../module-03/knowledge.md) · **体系位置**：[`KNOWLEDGE-SYSTEM.md` §7 M3](00-knowledge-system.md)

### 3.0.1 本章校准 Case

| 优先 | Case | 补强 K 点 | 啃不动时 |
|---|---|---|---|
| **深读** | [Case 02](../case-library/cases/case-02-prompt-butterfly.md) | M3-K02、K03、K04 | [`USAGE`](../../USAGE.md) §1.1 → `module-03/knowledge` |
| 关联 | [Case 05](../case-library/cases/case-05-catastrophic-forgetting.md) | M3-K04、K05 | 同上 |
| 关联 | [Case 08](../case-library/cases/case-08-ab-survivorship-bias.md) | M3-K03、K05 | 同上 |

### 3.1 考核句

**「我会 Harness」**——Prompt **版本化、灰度、护栏、回滚**；不靠换模型救火。

### 3.2 核心概念（What）

Harness 是 **AI 行为的交付与可靠性层**——不是 Agent loop 本身，而是 **Prompt/配置的发布系统**。

| | Agent loop (M1) | Harness (M3) |
|---|---|---|
| 改什么 | 单 task 的 plan/command | **全局** Prompt/模型配置 |
| 失败形态 | loop / fatal | 满意度断崖、风格漂移 |
| 证据 | trace 单 run | harness-report **配置能否上线** |

### 3.3 工作机制（How）

**Case 2 机理**（Why 需要版本化）：改一句 system tone → 输出 **分布** 整体偏移（蝴蝶效应），代码没 crash，业务指标崩。  
**高级 fix**：不是删 warm 词，而是 **版本 + changelog + 金丝雀 + 护栏 + rollback**。

**术语**（详见 [`module-03/GUIDE.md`](../module-03/GUIDE.md) 注释）：

- **Canary（金丝雀）**：`gray_percent` 小流量试 v2
- **SLO**：`style_formality_min` 目标线；**SLI**：`formality_score`
- **Blue-green**：v1↔v2 切换；`rollback_to_v1` = 切回 Blue

**平台 stub（须学 · 接入 loop plan，非真实网关）**：

| 模块 | 课内要点 |
|---|---|
| `model_router` | 简单/复杂 → 模型名（关键词启发式） |
| `token_counter` / `cost_monitor` | 估算记账；**无超限阻断** |
| `rate_limiter` | 超限换 fallback 模型名，非硬拒绝 |
| metrics | run/harness 均可写 JSON，**状态不共享** |

无独立 Issue——自学打开 `metrics-*.json`（knowledge 已标注）。

### 3.4 双护栏与回滚（When wrong + How）

- **M2 allowlist / schema / HITL**：tool **入口** 防越权副作用
- **M3 formality 等**：Prompt **出口** 防语义副作用（**成本不在此熔断**）

面试串讲：**「入口拦 rm_rf，出口拦 Amazing!!!」**。

`formal_tone_score()`：规则型 SLI（感叹号、hype 词扣分），对比 SLO 阈值。  
**L3 dashboard**：正式度 + 长度 + 敏感词，**任一跌破** → rollback（防单指标 gaming，衔接 Case 8）。

**L2 vs L3 回滚**：

- **L2** `run_harness()`：单次报告写 `rollback_to_v1`
- **L3** [`rollout_controller`](../TrackARuntime/m3/rollout_controller.py)：`fail_streak` 连续 N 次 → **lock** + promote 需 **eval gate**

深读：[`study-notes/rollout-auto-rollback.md`](../study-notes/rollout-auto-rollback.md)

### 3.5 re-ask（#1491）与 Harness 可靠性

Validator 失败后的 re-ask 是 **Harness 内循环**，也要有上界与 **边界安全**（空 `fail_results` 不索引 `[0]`）。  
与 M1 fingerprint 对照：一个是 **validator 循环**，一个是 **agent act 循环**。

### 3.6 过关动作（Prove）

```powershell
cd TrackARuntime
python cli.py harness --prompt v2 --gray-percent 10
python cli.py harness --prompt v1 --gray-percent 0
python cli.py harness --prompt v2 --gray-percent 10 --watch   # L3
python cli.py harness --reset-rollout
# 平台 stub 数字（所学延伸）：
python cli.py run --task "fix failing test" --llm mock
# → 打开 m1_m2/evidence/<run_id>/metrics-<run_id>.json
```

**L2 出口**：讲清 `guardrail_ok` / `action` / `rollback_reason`；v1 vs v2 yaml diff；能区分 formality 护栏 vs cost 记账。  
**L3 出口**：rollout 状态机或 `--watch` 三连 lock；设计 cost 硬护栏接 loop。  
**Drill**：60s Harness = 配置中心 + 金丝雀 + 熔断。

**深读**：[`module-03/knowledge.md`](../module-03/knowledge.md) · [`module-03/issues.md`](../module-03/issues.md)

---

## 第 4 课 · Eval 门禁（M4）

### 4.0 模块导论（Why M4）

| | |
|---|---|
| **生命线** | ④ **质量门禁** — 行为质量有无数据证明、merge 能否 block |
| **前置** | M3（Harness 管在线单变更；Eval 管离线全任务集回归） |
| **不学会** | merge 靠感觉、失败只有 pass/fail%、eval judge 坏了门禁失灵 |
| **学完能回答** | Harness vs Eval 分工？taxonomy + remediation？baseline 固定 vs auto？为何 eval 报告可能没有 trace 指标？`_simulate` 与真跑 Agent 差在哪？ |

**K 点详卡**：[`module-04/knowledge.md`](../module-04/knowledge.md) · **体系位置**：[`KNOWLEDGE-SYSTEM.md` §7 M4](00-knowledge-system.md)

### 4.0.1 本章校准 Case

| 优先 | Case | 补强 K 点 | 啃不动时 |
|---|---|---|---|
| 关联 | [Case 01](../case-library/cases/case-01-rag-surrender-hallucination.md) | M4-K02、K04 | [`USAGE`](../../USAGE.md) §1.1 → `module-04/knowledge` |
| 关联 | [Case 04](../case-library/cases/case-04-data-time-travel.md) | M4-K01、K04 | 同上 |
| 关联 | [Case 08](../case-library/cases/case-08-ab-survivorship-bias.md) | M4-K02、K03 | 同上 |

### 4.1 考核句

**「我会 Eval」**——**固定 scenarios + failure taxonomy + gate_pass**；用数据证 Agent 质量，不靠感觉。

### 4.2 核心概念（What）

Eval = **固定 scenarios + failure taxonomy + gate_pass**；用数据证 Agent 质量，不靠感觉。

| 没有 Eval 时 | 有 Eval 时 |
|---|---|
| 「好像还能用」 | 20 条 scenario 可重复跑 |
| 只有 pass/fail% | **Top3 failure_code** 指导 fix |
| merge 靠感觉 | `gate_pass` false → block |

**Harness vs Eval**（Why 两个门禁）：

- Harness：**一次配置变更** 能否上线（在线/灰度）
- Eval：**全任务集 regression**（离线 merge 前）

### 4.3 工作机制（How）

**taxonomy**（Why 没有分类就没有 engineering）：仅有成功率，无法回答「该改检索还是改 plan」。  
M4 要求 **6+ 类**（`RETRIEVAL_MISS`、`PLAN_ERROR`、`OVER_EDIT`…）；报告可带 **remediation**（解析 `failure_taxonomy.md`）。

**执行诚实边界（须学）**：`runner._simulate()` 按 `expect` **造结果**，**不驱动** `LoopEngine`——仍是可回归的任务集门禁，但不是端到端 Agent 回放。

**#9415 机理**：检索 UI 有 chunks，答案仍错 → **不是 embedding 问题**，是 **注入链/overflow**；必须 **拆分 metric**（report `category_split`）。

**门禁自身要可靠（#929）**：eval judge 输出畸形 JSON → **gate_pass 无意义**（质检仪坏了）。  
fix 方向：structured output、schema enforce——**fail closed**。Judge 接口默认关闭；开启时轨迹常为空（stub）。

**baseline**：

| 模式 | 用法 | 课内要求 |
|---|---|---|
| 固定 | `--baseline 0.45`（**CI 当前**） | 知 CI 用法 |
| auto | `--baseline auto` → `baseline_meta` | **过关主命令**（M4-I03） |

**过程 metric（#2643）**：`trace_eval.py` **有实现+单测**，但 **`run_eval` 未接入**——须会讲「库有 / 主路径无」；与 M1 fingerprint **同构**。接 runner 为 L3。

### 4.4 过关动作（Prove）

```powershell
cd TrackARuntime
python cli.py eval --baseline auto
# 对照 CI：
python cli.py eval --baseline 0.45
```

**L2 出口**：读 report——success_rate、gate_pass、`baseline_meta`、Top3 failure + remediation、`category_split`、P95；能说明 `_simulate` 与「无 trace 指标」原因。  
**L3 出口**：新增 failure code + scenario；把 `trace_eval` 接入 `run_eval`。  
**Drill**：5min 四层架构（M4 后）。

**深读**：[`module-04/knowledge.md`](../module-04/knowledge.md) · [`module-04/issues.md`](../module-04/issues.md)

---

## 第 5 课 · 值班思维（M5）

### 5.0 模块导论（Why M5）

| | |
|---|---|
| **生命线** | ⑤ **运维响应** — 告警来了先干什么、证据在哪、如何止血 |
| **前置** | M1–M4（SOP 指向 state/trace/harness/eval 文件） |
| **不学会** | panic 换模型、在错误监控层打补丁、Case 与己项目脱节 |
| **学完能回答** | Case 7 vs Case 2 第一步各开什么文件？监控五层如何填（含 metrics）？五步 SOP 各段目标？成本有仪表无告警意味着什么？ |

**K 点详卡**：[`module-05/knowledge.md`](../module-05/knowledge.md) · **体系位置**：[`KNOWLEDGE-SYSTEM.md` §7 M5](00-knowledge-system.md)

### 5.0.1 本章校准 Case（合成层）

M5 不新增独立机理，用 Case **串证据链**。深读四 Case：**02、03、06、07**；浅读：**01、04、05、08**；扩展：**09**。

| M5 深读 | Case | 第一步开什么证据 |
|---|---|---|
| 配置变更 | [Case 02](../case-library/cases/case-02-prompt-butterfly.md) | `harness-report.json` |
| 上下文/控制 | [Case 03](../case-library/cases/case-03-context-lost-in-middle.md) | `state.json` + replan 叙事 |
| 安全边界 | [Case 06](../case-library/cases/case-06-prompt-injection.md) | `trace.json` + allowlist |
| 延迟/SLO | [Case 07](../case-library/cases/case-07-latency-avalanche.md) | `trace.json` 分 span P95 |

啃不动时：[`USAGE`](../../USAGE.md) §1.1 · [`monitoring-layers.md`](../module-05/monitoring-layers.md) · 各 Case **补强 K 点** 行。

### 5.1 考核句

**「我会值班思维」**——**五步 SOP**、**监控分层**、**项目映射**；把 trace/harness/eval 串成 **故障响应叙事**。

### 5.2 核心概念（What）

M1–M4 教 **设计**；M5 教 **告警来了先干什么**。同一根因，两种语言：

| | M2–M4 | M5 |
|---|---|---|
| Case 7 | `resolve_timeout()` 设计 | 打开 trace **分 span P95** |
| Case 2 | harness gray + formality | 打开 **harness-report**，gray→0 隔离 |

**初级反应（禁止作为 SOP 第一步）**：换模型、改一句 Prompt、调 temperature。  
**高级反应**：分 span 定位 → 隔离/回滚 → 最小 fix → 更新监控/eval。

### 5.3 工作机制（How）· 五步 SOP

| 阶段 | 时间 | 目标 |
|---|---|---|
| 观察 | 5 min | 第一份证据（trace / harness / eval / **metrics**） |
| 隔离 | 10 min | 止血：rollback、gray→0、降级 |
| 定位 | 30 min | 主类 + 根因一句话 + 系统等价物 |
| 修复验证 | 1 h | 最小 diff + before/after |
| 复盘 | 全天 | monitoring-layers、scenario、SOP 更新 |

**Case 7 vs Case 2 第一步**：前者 `trace.json` latency（可兼看 metrics）；后者 `harness-report` formality。

深读：[`study-notes/five-step-incident-sop.md`](../study-notes/five-step-incident-sop.md)

### 5.4 监控分层与项目映射（When wrong → 动作）

业务 → 应用 → 检索/工具 → 模型 → 基础设施。  
**Case 7 为何 ASR 优化无效**：瓶颈在 **模型 TTFT / tool tier**，却在错误层打补丁。

TrackARuntime 增补一层证据：`metrics-*.json`（token/cost 估算）——**只记账、无告警通道、无自动 bad-case→scenario**（须会讲缺口）。

填表：[`monitoring-layers.md`](../module-05/monitoring-layers.md)

### 5.5 项目映射

每 Case 一行：**现象 | 监控红灯 | 证据路径 | 回滚动作**。  
深做 Case **2, 3, 6, 7**；浅读 1, 4, 5, 8（各 1 句系统等价物 + SOP 速读）。  
Case 6 映射可写到 allowlist/**schema/HITL**；Case 9 说明「有 metrics 无 cost 熔断」。

填表：[`project-mapping.md`](../module-05/project-mapping.md)

### 5.6 过关动作（Prove）

- 选 Case 7：写 **带时间戳** SOP（可不写代码）；观察步列出打开的文件（含 metrics）
- 填 monitoring-layers **每层 1 指标 + 阈值 + 动作**
- 填 project-mapping **≥4 行**（深 Case）
- **≤10min** 口述 2 个 Case（现象→根因→监控→回滚）

**深读**：[`module-05/knowledge.md`](../module-05/knowledge.md) · [`module-05/issues.md`](../module-05/issues.md) · [`case-library/METHODOLOGY.md`](../case-library/METHODOLOGY.md)

---

## 第 6 课 · 串讲与总考核（Capstone）

### 6.1 五句连背（五条生命线 · 面试就绪线）

1. Agent = 状态机 + fatal interrupt + fingerprint；可插拔 Mock plan + checkpoint  
2. Tool = allowlist → schema → HITL + trace 物证 + timeout 两极（enforce 诚实）  
3. Harness = Prompt 发布 + Canary + SLO 护栏 + rollback；router/cost 为 stub  
4. Eval = scenarios（`_simulate`）+ taxonomy + baseline/auto + gate_pass；`trace_eval` 未进主路径  
5. 值班 = SOP 五步 + 分层监控（含 metrics）+ 证据文件对号入座  

### 6.2 一张图串证据

```text
用户任务 ──► cli.py run [--llm mock] ──► state + trace + metrics     (M1/M2)
配置变更 ──► cli.py harness ──► harness-report (+ rollout)           (M3)
发版前   ──► cli.py eval --baseline auto ──► evaluation-report       (M4)
线上事故 ──► SOP ──► 指上述文件 + mapping 回滚                       (M5)
```

### 6.3 总考核自检（M1–M4 Exit + M5 出口）

| 检查项 | 通过标准 |
|---|---|
| M1–M4 rubric | 每模块核心 K **均分 ≥2.0**，**≥1 个 K=3** |
| Runtime 证据 | state / trace / metrics / harness / eval 均能打开讲解 |
| 所学↔所验 | 过关命令均在对应课「工作机制」出现过（见 [`KNOWLEDGE-SYSTEM` §7.1](00-knowledge-system.md)） |
| Issue Day3 | 主修 Issue 与 PR/本地对照完成 |
| M5 | 4 Case 深做 + mapping ≥4 行 + 2 Case 口述 ≤10min |
| Drills | [`INTERVIEW-DRILLS.md`](../interview/DRILLS.md) 各模块 D1 计时通过 |

### 6.4 本课 **不教** 什么（避免范围蔓延）

- 生产 LLM 调用、向量 RAG 平台实现 → 见 [`KNOWLEDGE-MAP.md` §10](../KNOWLEDGE-MAP.md) 与 [`02-production-extension-packs.md`](02-production-extension-packs.md)
- M6 作品集叙事 → 仓库根 [`portfolio/`](../../portfolio/README.md)（含 M6 Exit、case study、demo）
- 未绑定 runtime 的 OSS Issue → [`tutor/README.md`](../tutor/README.md)「刻意不读」
- 成本硬熔断 / `trace_eval`→runner / timeout enforce → **教缺口、不考未实现能力为必过**

### 6.5 求职增强 Capstone（生产扩展包）

核心 Exit 通过后，再读 [`02-production-extension-packs.md`](02-production-extension-packs.md)。这一步不改变 M1–M5 的必过命令，而是把系统软件工程师面试中最常见的生产追问挂回五条生命线。

| 扩展包 | 面试追问 | 回答时先挂哪条生命线 | 最低证明 |
|---|---|---|---|
| **P1 LLM Gateway** | Provider 429、timeout、invalid JSON、fallback 怎么办 | M3 配置交付 + M1 错误分类 + M5 告警 | provider error taxonomy + [Case 10](../case-library/cases/case-10-provider-rate-limit-fallback.md) |
| **P2 RAG** | 检索命中但答案错，怎么定位 | M4 质量门禁 + M1 observe | retrieval / generation / citation 三分 |
| **P3 Security** | Agent 被文档诱导调用危险工具怎么办 | M2 工具边界 | policy engine：模型输出不是授权依据 |
| **P4 Runtime Scale / Memory** | 多任务并发、worker 死亡、长期记忆污染怎么办 | M1 控制面 | queue / lease / checkpoint / memory rollback 白板 |
| **P5 Eval Reliability** | LLM-as-Judge 本身不可信怎么办 | M4 质量门禁 | judge calibration + human label 对照 |
| **P6 Observability** | 本地 trace 如何变生产告警和 SLO | M5 运维响应 + M2 trace | OTel span 对照 + dashboard 指标草图 |

**30 分钟面试串讲顺序**：

1. 先用 §6.1 五句证明核心 M1–M5 已会。
2. 再从 P1–P6 各挑 1 个生产追问，说明它并入哪个模块。
3. 每个追问都说清：现有 Runtime 已覆盖什么、未实现什么、生产系统会怎么扩展。
4. 最后落到 Portfolio：架构图、demo script、eval report、incident case study 分别支撑哪些 claim。

**诚实边界**：生产扩展包中的真实 LLM/RAG、分布式 queue、OTel 后端、告警通道目前不是 TrackARuntime 已实现能力。面试时应说「我用教学 runtime 证明控制面和证据链，并能设计生产扩展」，不要说成已经上线生产平台。

---

## 附录 A · 与 KNOWLEDGE-SYSTEM / KNOWLEDGE-MAP 的分工

| 文档 | 用途 |
|---|---|
| [`KNOWLEDGE-SYSTEM.md`](00-knowledge-system.md) | **世界观 + 26 K 矩阵 + 所学↔所验/命令全库（§7.1）** |
| **本文件 COURSE.md** | **逐课机理、过关路径、导师动作清单** |
| [`02-production-extension-packs.md`](02-production-extension-packs.md) | **求职增强**：生产级 Agent 平台追问如何映射回 M1–M5 |
| [`KNOWLEDGE-MAP.md`](../KNOWLEDGE-MAP.md) | **纯索引速查**：术语、K 点表、命令 |
| `module-XX/knowledge.md` | 单 K 点详卡 + Prove L1/L2/L3 + Issue 覆盖标注 |
| `module-XX-day*.md` | Issue 校准过程稿 |

---

## 附录 B · 推荐周历（与 Residency 对齐）

| 周 | 读本课章节 | 并行 |
|---|---|---|
| 0（预习） | [`KNOWLEDGE-SYSTEM.md`](00-knowledge-system.md) §2–§7.1 | 建立五条生命线 + 命令全库 |
| 1 | 第 1 课 | M1 Issue · `run --llm mock` · checkpoint(I05) |
| 2 | 第 2 课 | M2 I01–I04 · schema/HITL · #8448 |
| 3 | 第 3 课 | M3 harness · Case 2 · metrics 精读 |
| 4 | 第 4 课 | M4 `eval --baseline auto` · taxonomy |
| 5 | 第 5 课 | M5 Case 深做 · mapping · SOP（含 metrics） |
| 6 | 第 6 课 | Capstone 自检 · M6 portfolio（可选） |
| 7（求职增强） | [`02-production-extension-packs.md`](02-production-extension-packs.md) | P1–P6 生产追问串讲 · portfolio 材料对齐 |

---

## 附录 C · 学习记录（自填）

| 课 | 机理是否讲通（自评） | Runtime 证据 | rubric 均分 | Exit |
|---|---|---|---|---|
| 1 M1 | | | | ☐ |
| 2 M2 | | | | ☐ |
| 3 M3 | | | | ☐ |
| 4 M4 | | | | ☐ |
| 5 M5 | | | | ☐ |
| 6 Capstone | | | | ☐ |
