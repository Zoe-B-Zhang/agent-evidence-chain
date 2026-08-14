# M2 Day2 — 开方

**日期**：________

> **导师读法**：Day2 在 Day1 根因基础上设计 **机制表 + Runtime 映射**。Issue 1 下方为完整示范；Issue 2 留空供 Learner 按同结构填写。

## Issue 1 工程化解法（#7355 · timeout 分桶）

**方案一句话**：按 tool/command 分 tier timeout → trace 记录 latency + timeout 语义 → 超时时不伪造失败 observation，走降级或 explicit retry


| 机制          | 我的方案（Issue 1 示范）                                                                                                                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tool schema | `execute_command` 保留可选 `timeout_seconds`；schema 校验 **正整数 + 上限 cap**（如 3600）；未传则走 `resolve_timeout(tool, payload)` heuristic（M2-K03 第 1 层）                                                               |
| Allowlist   | 已有 `ToolExecutor.ALLOWLIST`；timeout tier **仅对 allowlist 内工具生效**；拒绝工具仍 `fallback_used: true` + fatal（M2-K01，Issue 2 主修）                                                                                  |
| 超时（按工具类型）   | 对齐 `tool_executor.py` 现有 `_timeouts` 差异并 **真正 enforce**：`read_file: 5s`、`grep: 10s`、`docker_exec: 30s`、`run_tests: 120s`；新增 **long-running tier: 300s**（pytest/npm/cargo/build 等 heuristic，对齐 PR #9159） |
| Trace 字段    | 每次 tool call 写 `latency_ms`；timeout 时 `output.error: "timeout"`、`fallback_used: true`、可选 `error_class: "timeout"`（非 fatal，除非 stall 超过 hard cap）；便于 Case 7 分 span P95                                    |
| 失败后降级       | **短超时**（read/grep）：快速 fallback → 换工具或提示用户。**长超时**（test/build）：timeout 后 **不宣称命令失败**；标记 `in_flight` 或延长 tier，避免 Agent 在 build 中途改文件（#7355 评论区真实痛点）                                                       |


**long-running tier 设计（M2-I01 Runtime 任务）**

```text
resolve_timeout(tool, payload) → seconds
├── explicit payload["timeout_seconds"]  → min(explicit, HARD_CAP)
├── tool == "run_tests"                  → 120.0
├── heuristic(payload) 匹配 build/test   → 300.0   # npm|pytest|cargo|docker build|make ...
└── default _timeouts[tool]              → 5~30s
```

**Heuristic 示例（L3 可扩展）**：

- 命令串匹配：`pytest|jest|vitest|npm (run )?test|cargo build|docker build|mvn|gradle`
- `run_tests` 工具恒走 120s；含上述 pattern 的 `docker_exec` payload 升到 300s

**Runtime 任务（issues.md 绑定）**：

```powershell
cd TrackARuntime
# 1. 阅读现有分桶（尚未 enforce，Day2 设计要点）
#    m1_m2/tool_executor.py → _timeouts dict

# 2. 对照 trace 字段契约
python cli.py run --task "fix failing test"
# 证据：m1_m2/evidence/<id>/trace.json → latency_ms, fallback_used, error_class
```

**预期证据**（L2 · 设计层，实现前也可写「应出现」）：

- `trace.json` 中 `run_tests` 事件 `latency_ms` 可高于 `read_file`（分桶可观测）
- timeout 事件：`fallback_used: true` 且 **不** 误标 `error_class: fatal`（与 M1 fatal 区分）
- Day2 表格 + heuristic 伪代码 = M2-K04 L2 证据（`module-02-day2.md` 本表）

**与 TrackARuntime 映射（Issue 1）**


| 文件                 | 现状                                           | Day2 应改什么                                                               |
| ------------------ | -------------------------------------------- | ----------------------------------------------------------------------- |
| `tool_executor.py` | `_timeouts` dict 存在，**call() 未 enforce**     | 在 `call()` 内用 `resolve_timeout()` + mock sleep/timeout 分支；长命令 tier 300s |
| `trace.py`         | `latency_ms`, `fallback_used`, `error_class` | timeout 时写入明确 `output` 结构，供 Case 7 分 span                               |
| `loop_engine.py`   | M1 replan 逻辑                                 | timeout 走 recoverable replan，**in_flight** 时不 replan 改文件                |
| `knowledge M2-K03` | 三层防御                                         | schema 校验 timeout 参数 → tier resolve → 超时降级                              |


---

## Issue 2 工程化解法（#8448 · 无输出 hang）

**方案一句话**：grep 零输出 → shell integration 不发 completion → observe 用 **idle/stalled timeout** 闭合 span，trace 写明 `pending` vs `stalled`，不误当成功或无限 wait

| 机制 | 我的方案 |
|---|---|
| Tool schema | `grep` payload 可带 `observe_stalled: true`、`idle_timeout_s`（默认对齐 `_timeouts["grep"]` = 10s） |
| Allowlist | `grep` 在 allowlist 内；#8448 缺陷不在越权，在 **observe 契约** |
| 超时（按工具类型） | **idle/stalled 上界**：无输出 N 秒仍无 completion signal → `completion: stalled`（M2-K05）；与 #7355 的 tier **下界** 成对 |
| Trace 字段 | `output.completion`: `pending`（bug，span 不闭合）→ `stalled`（fix）；`error_class: stalled`；fix 路径 `fallback_used: true` |
| 失败后降级 | stalled 后提示用户 / 切 backgroundExec；**不** infinite wait；**不** 伪造 grep 成功 |

**Runtime 任务**（[`issues.md`](issues.md) M2-I02）：

```powershell
cd TrackARuntime
python cli.py demo-no-output-hang
# → m1_m2/evidence/m2-8448-demo/trace.json（固定目录，可重复跑覆盖）
```

**预期证据**（`m1_m2/evidence/m2-8448-demo/trace.json`）：

| Event | 模拟 | `completion` | `fallback_used` | `error_class` |
|---|---|---|---|---|
| 1 | #8448 bug：无 completion signal | `pending` | `false` | `null` |
| 2 | fix：`observe_stalled` | `stalled` | `true` | `stalled` |

**本次证据路径**：`TrackARuntime/m1_m2/evidence/m2-8448-demo/trace.json`、`state.json`

**与 TrackARuntime 映射（Issue 2）**

| 文件 | 已实现 |
|---|---|
| `tool_executor._grep_no_output_hang` | pattern `ABCDEFGH0193746458`（#8448 原文复现串） |
| `cli.demo-no-output-hang` | 一次跑 A/B 两条 event 写入同一 trace |
| `errors.ErrorClass.STALLED` | stalled 与 fatal / retryable 区分 |

**与 Cline workaround 对照**：官方建议 Background Exec 绕过 shell integration → 等价于换 observe 通道，不是改 LLM。

---

## 解法设计（总表 · 两日 Issue 合并视图）


| 机制 | Issue 1 (#7355) | Issue 2 (#8448) |
|---|---|---|
| Tool schema | timeout 参数校验 | `observe_stalled` + `idle_timeout_s` |
| Allowlist | tier 仅作用于 allowlist 内 | 非主缺陷（grep 已 allowlist） |
| 超时（按工具类型） | 分 tier 下界（防切太早） | idle/stalled 上界（防永不切） |
| Trace 字段 | `latency_ms` 分桶 | `output.completion` pending → stalled |
| 失败后降级 | in_flight 不误判失败 | stalled → 提示 / backgroundExec |


## TraceEvent 契约确认

见 `[TrackARuntime/m1_m2/trace.py](../../TrackARuntime/m1_m2/trace.py)`：


| 字段 | 含义 | Issue 1 示例 | Issue 2 示例（`m2-8448-demo/trace.json`） |
|---|---|---|---|
| `step` | loop 阶段 | `act` | `act` |
| `tool` | 工具名 | `run_tests` | `grep` |
| `input` | payload | `{"round": 0}` | Event2：`observe_stalled: true`, `pattern: ABCDEFGH...` |
| `output` | 返回 | `{"exit_code": 1}` | Event1：`completion: pending` · Event2：`completion: stalled` |
| `latency_ms` | 耗时 | mock `0` | `0` |
| `fallback_used` | 降级/拒绝 | 正常 `false` | Event1 `false`（仍 hang）· Event2 `true`（stalled 闭合） |
| `error_class` | 错误语义 | 常为 `null` | Event2：`stalled` |


