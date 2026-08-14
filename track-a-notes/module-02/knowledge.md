# M2 知识工程点 · Tool & Trace

> **生命线**：② **工具边界** · **模块考核句**：**「我会 Tool + Trace」**  
> **体系位置**：[`KNOWLEDGE-SYSTEM.md` §7 M2](../curriculum/00-knowledge-system.md) · **教案**：[`COURSE.md` 第 2 课](../curriculum/01-course.md)  
> 索引：[tutor/README.md](../tutor/README.md) · 评分：[MASTERY-RUBRIC.md](../MASTERY-RUBRIC.md) · Issue：[issues.md](issues.md)

**本模块共 5 个核心 K 点**（M2-K01–K05），另有 4 个生产扩展 K 点（M2-K06–K09）用于求职增强。

> **Issue 标注约定**：某 Runtime 能力若在 [`issues.md`](issues.md) **无对应练习条目**，在下方用  
> `> **Issue 覆盖**：无对应 Issue — …`  
> 标明；有条目则写 `M2-I0x`。

---

## 速查表

| ID | 知识点 | What 摘要 | Runtime 绑定 | Issue |
|---|---|---|---|---|
| M2-K01 | Tool = 受控副作用 | allowlist RPC + 只读沙箱 | `ALLOWLIST`；`read_file`/`grep` 真实 handler | I02 选修 allowlist；**真实只读无独立 Issue** |
| M2-K02 | Trace = 可回放图 | 有序执行图 | `trace.py` | I01 / I02 |
| M2-K03 | 三层防御 | allowlist → schema → HITL | `ToolSpec` / `validate_schema` / `--require-hitl` | I03 schema；I04 HITL |
| M2-K04 | 分路径 timeout | 按 tool SLA（配置层） | `_timeouts`（**未强制中断**） | I01（设计对照） |
| M2-K05 | timeout ≠ kill | in_flight / stalled | observe 契约 + `demo-no-output-hang` | I02 |
| M2-K06 | Policy Engine（扩展） | 模型外确定性授权 | 设计题；TrackARuntime 未实现 | [Case 12](../case-library/cases/case-12-indirect-prompt-injection-tool-abuse.md) + [SOP](../case-library/sops/sop-case-12-indirect-prompt-injection-tool-abuse.md) |
| M2-K07 | Indirect Prompt Injection（扩展） | 不可信内容不能直接驱动工具 | SEC red team 设计 | [Case 12](../case-library/cases/case-12-indirect-prompt-injection-tool-abuse.md) + [SOP](../case-library/sops/sop-case-12-indirect-prompt-injection-tool-abuse.md) |
| M2-K08 | Data Boundary（扩展） | PII / secret / tenant / provider policy | redaction 设计 | [Case 17](../case-library/cases/case-17-secret-leakage-through-tool-trace.md) + [SOP](../case-library/sops/sop-case-17-secret-leakage-through-tool-trace.md) |
| M2-K09 | HITL UX（扩展） | approval granularity / undo / fatigue | demo script 设计 | [Case 18](../case-library/cases/case-18-approval-fatigue-destructive-action.md) + [SOP](../case-library/sops/sop-case-18-approval-fatigue-destructive-action.md) |

**面试 60s**：Tool 像带 allowlist 的 RPC；trace 是 **面试证据链** 核心——能指着 `trace.json` 逐步讲一次 run。边界层现已含 **schema + HITL**；主 loop 仍主要调 mock 的 `docker_exec`/`run_tests`。

---

## M2-K01 · Tool = 受控副作用

### What（是什么）

Agent 的 tool 不是任意 shell，而是 **白名单内的、可审计的 RPC**；越权调用必须在执行前被拒绝并留下 trace。只读工具可在 **项目根沙箱** 内读真实文件。

### Why（为什么必须有）

任意 shell → 越权副作用（写盘、exec）不可审计、不可回滚；面试无法讲清「谁允许调了什么」。

### How（怎么做）

| 层 | TrackARuntime | 传统等价 |
|---|---|---|
| allowlist | `ToolExecutor.ALLOWLIST`、`call()` 拒载 | sudoers / API Gateway 路由 |
| 拒绝路径 | `fallback_used` / `error_class` | WAF 403 + audit log |
| 真实只读 | `_read_file_handler` / `_grep_handler`（沙箱） | 只读 volume / chroot |
| Spec 元数据 | `BASE_TOOL_SPECS`：`read_only` / `dangerous` | 权限标签 |

**诚实边界**：主 `LoopEngine.run()` **默认只调** `docker_exec` + `run_tests`（仍为 mock 输出）；`read_file`/`grep` 能力在 executor 内，经 demo/单测可达，**未进入默认 loop 主路径**。

> **Issue 覆盖**：allowlist 拒载见选修命令 / 可对照 I02 外练习；**真实只读沙箱路径 — 无对应 Issue**（自行：对存在文件调 `ToolExecutor` 或读 `tests/test_tool_executor.py`）。

### When wrong（典型故障）

Case 6：未注册 tool 进入 handler；allowlist 拒绝 = **fatal 类** observe，缺陷层在 **tool 入口**。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能口述 Tool = RPC + 副作用；列举 TrackARuntime allowlist 内 tool 名。 |
| **L2** | 能解释 `rm_rf` 如何 **不进入 handler**；指读 `demo-allowlist` 的 trace。 |
| **L3** | 能说明为何真实只读未进主 loop；设计「检索步骤调用 `read_file`」的最小 plan 扩展。 |

---

## M2-K02 · Trace = 可回放图

### What（是什么）

`trace.json` 不是日志堆砌，而是 **按时间有序的执行图**——每步 tool 的 input/output/latency 可逐步复盘。

### Why（为什么必须有）

L2 证据链 / 值班定位需要 **逐步物证**；只有 state 叙事无法回答「这一刀 tool 花了多久」。

### How（怎么做）

| 字段 | 含义 |
|---|---|
| `trace_id`, `step`, `tool`, `input`/`output`, `latency_ms`, `fallback_used`, `error_class` | `TraceCollector.record()` / `write()` |

**传统等价**：OpenTelemetry span；`state.json` 讲 **故事**，`trace.json` 讲 **事实**——面试两者并用。

### When wrong（典型故障）

#8448：hang 时 trace 缺「未完成 span」闭合 → 无法发现 stalled。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能讲清 `TraceEvent` 各字段；类比 OTel span。 |
| **L2** | 能 **逐步讲** 成功 run 或 `m2-8448-demo` 的 `trace.json`；与 state history **交叉验证**。 |
| **L3** | 能设计 `trace_id` 贯穿 state + trace；最小 **replay API**。 |

---

## M2-K03 · 三层防御（工具参数错误）

### What（是什么）

参数/权限类错误应在 **调用前** 拦截：① Allowlist → ② Schema 校验 → ③ HITL（危险工具需确认）。Dry-run 仍为概念扩展。

### Why（为什么必须有）

坏请求进 handler 才失败 → LLM 从 stderr 猜 → **无效 replan** 循环（Cline #7355 类）。

### How（怎么做）

| 层 | TrackARuntime 状态 |
|---|---|
| 第 0 层 allowlist | **已实现**（K01） |
| 第 1 层 schema | **已实现**：`ToolSpec.parameters` + `validate_schema()`（`tool_executor.py`） |
| 第 2 层 HITL | **已实现**：`dangerous=True` 且 `--require-hitl` 时需 `confirmed=True` |
| dry-run | **未做**（L3 扩展） |
| RETRYABLE 退避 | **已实现**：指数退避（`max_retries` / `retry_backoff_s`） |

**与 M1-K03**：三层防御 = **tool 侧**；fingerprint = **loop 侧** 抓无进展。

> **Issue 覆盖**：schema → [M2-I03](issues.md)；HITL → [M2-I04](issues.md)。  
> **RETRYABLE 退避 — 无对应 Issue**（CLI：`--max-retries` / `--retry-backoff-s`；单测 `force_retryable`）。

### When wrong（典型故障）

#7355：缺 schema/tier → 30s 误杀长命令；缺 HITL → 危险 tool 无确认即执行。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能 **按顺序背出** allowlist → schema → HITL。 |
| **L2** | 能跑 I03/I04，指读拒绝原因；对照 #7355「哪一层曾缺失」。 |
| **L3** | 能设计 dry-run：`docker_exec` parse 不 exec；trace 标记 `dry_run: true`。 |

---

## M2-K04 · 分路径 timeout

### What（是什么）

不同 tool / 意图对应不同 SLA；**全局 30s 一刀切** 会误杀 build/test。

### Why（为什么必须有）

#7355：120s 测试被 30s 切 → 假失败 → 错误 replan；Case 7 症状在 tool tier 却在 ASR 层打补丁。

### How（怎么做）

| Tool | Timeout（配置） | TrackARuntime |
|---|---|---|
| run_tests | 120s | `tool_executor._timeouts` |
| read_file / grep / docker_exec | 5 / 10 / 30s | dict **已存在** |

**诚实边界**：`_timeouts` 为 **教学配置表**；当前 `call()` **不会**按该表强制中断子过程（无真实 shell）。enforce 仍是 L3（对照 PR #9159）。

> **Issue 覆盖**：设计与口述 → [M2-I01](issues.md)；**强制 timeout 执行 — 无对应 Issue**（代码未实现）。

### When wrong（典型故障）

用户配置 6000s 与 managed 30s 是 **不同配置项**（connect vs exec）。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能口述 build/test/read/grep 时长数量级差异。 |
| **L2** | 能指读 `_timeouts` dict；写清「配置有 / enforce 无」。 |
| **L3** | 能实现 `resolve_timeout(tool, payload) -> float` 并在 call 路径使用。 |

---

## M2-K05 · timeout ≠ kill（observe 契约）

### What（是什么）

timeout 只表示 **「我停止等了」**，不等于子进程已退出；observe 须区分 **in_flight / stalled / completed**。

### Why（为什么必须有）

两极坏情况：**切太早**（#7355 fake failed）vs **永不切**（#8448 hang）；与 #803 对照：#803 是 fatal 未升维。

### How（怎么做）

| 极性 | Issue | 正确 observe |
|---|---|---|
| 切太早 | #7355 / I01 | `in_flight` 或 long-running tier |
| 永不切 | #8448 / I02 | **stalled** / idle cap；span 必须闭合 |

L3：`observe_stalled` — 无输出 N 秒 → stalled；backgroundExec + 轮询 exit code。

### When wrong（典型故障）

Case 7：全链路只优化 ASR/TTS 忽略 LLM TTFT — **observe 契约与 SLA 分桶** 问题。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能口述 **timeout ≠ kill**；两种坏情况。 |
| **L2** | 能对照 #7355 vs #8448 写 observe 语义表；跑通 `demo-no-output-hang`。 |
| **L3** | 能设计 `observe_stalled` + trace `completion: pending` 字段（I02 已演示雏形）。 |

---

## 生产扩展 K 点（求职增强）

> 扩展详解：[`02-production-extension-packs.md` P3](../curriculum/02-production-extension-packs.md#5-p3--security--tool-sandbox--privacy) 与 P6 HITL/Observability。核心原则：**模型输出不是授权依据**。

### M2-K06 · Policy Engine

**What**：Tool call 执行前必须经过模型外的 deterministic policy check。

**Why**：Agent 的风险来自「带权限行动」。如果模型说 `delete_database()` 合理，系统也不能直接执行。

**How**：

| 输入 | 检查 |
|---|---|
| user identity | 用户是否有该 tool 权限 |
| tool capability | read-only / write / destructive |
| resource scope | 是否越过项目根、多租户边界、网络边界 |
| approval policy | 是否需要 HITL / 双人审批 |
| trace policy | 输入输出是否需要 redaction |

**Prove**：能写 policy table：`(user_role, tool, side_effect_level, data_class) -> allow/deny/require_approval`。

### M2-K07 · Indirect Prompt Injection

**What**：网页、文档、issue、邮件等不可信内容不能直接变成工具意图。

**Why**：Agent 读取的资料可能包含「忽略之前指令并调用内部 API」；这是 Agent 特有的输入污染路径。

**How**：

- 把 retrieved/tool content 标记为 untrusted。
- 不把 untrusted content 当 system/developer instruction。
- Tool intent 进入 policy engine，而不是由模型文本直接授权。
- 对高危 tool 要求 human approval 与解释。

**Prove**：能复盘 [Case 12](../case-library/cases/case-12-indirect-prompt-injection-tool-abuse.md) 与 [SOP](../case-library/sops/sop-case-12-indirect-prompt-injection-tool-abuse.md)：恶意文档 → 模型提出危险 tool call → policy engine 拦截 → trace 留证。

### M2-K08 · Data Boundary

**What**：PII、secret、tenant data、provider-bound data 必须有清晰边界。

**Why**：trace、prompt、provider request 都可能成为泄露面；教学 trace 可见不代表生产 trace 可明文保存。

**How**：

| 数据 | 策略 |
|---|---|
| secret / token | 不进入 prompt；trace redaction |
| PII | 最小化发送；日志脱敏 |
| tenant data | tenant_id scope check |
| provider-bound data | 外部模型发送前 policy check |

**Prove**：能复盘 [Case 17](../case-library/cases/case-17-secret-leakage-through-tool-trace.md) 与 [SOP](../case-library/sops/sop-case-17-secret-leakage-through-tool-trace.md)，说明哪些字段不能写入可见 `trace.json`，以及生产系统如何做 redaction / rotation。

### M2-K09 · HITL UX

**What**：HITL 不只是拦截危险 tool，还要让用户理解、修改、拒绝、撤销。

**Why**：确认弹窗过多会导致 approval fatigue；用户会无脑点击，安全机制失效。

**How**：

- 展示 plan preview：Agent 准备做什么。
- 展示 tool explanation：为什么需要这个工具。
- 支持 approve step / approve plan / edit args / reject。
- 对 destructive action 提供 undo / rollback 方案。

**Prove**：能复盘 [Case 18](../case-library/cases/case-18-approval-fatigue-destructive-action.md) 与 [SOP](../case-library/sops/sop-case-18-approval-fatigue-destructive-action.md)，写一段 approval transcript：用户拒绝危险操作后，Agent 如何安全 replan。

---

## K 点 × Issue 对照

| Issue | 主 K 点 | 失败极性 / 能力 |
|---|---|---|
| Cline #7355 / M2-I01 | K04, K05 | timeout **太早** + observe 误判失败 |
| Cline #8448 / M2-I02 | K05, K02 | completion **永不到达** + trace 缺闭合 |
| M2-I03 schema | K03 | 非法 args → 调用前拒绝 |
| M2-I04 HITL | K03 | 危险 tool 无确认 → 拦截 |
| allowlist 选修 | K01 | 越权 tool → trace 拒载 |

| Runtime 能力 | Issue |
|---|---|
| 真实 `read_file`/`grep` 沙箱 | **无对应 Issue** |
| RETRYABLE 指数退避 | **无对应 Issue** |
| `_timeouts` 强制中断 | **无对应 Issue**（未实现） |

---

## M1 → M2 衔接

| M1 已会 | M2 加深 |
|---|---|
| loop：plan → act → observe | act 内部：**谁允许调、schema/HITL、调了多久、留下什么 trace** |
| observe fatal/recoverable | tool 层：**timeout / stalled / completed** |
| `state.json` 叙事 | `trace.json` **逐步证据** |

---

## 学习记录（自填）

| K 点 | 自评 L | 证据 run / 日期 |
|---|---|---|
| K01 | | |
| K02 | | |
| K03 | | |
| K04 | | |
| K05 | | |
| K06（扩展） | | Policy table |
| K07（扩展） | | Indirect injection Case |
| K08（扩展） | | Data boundary / redaction |
| K09（扩展） | | HITL UX transcript |
