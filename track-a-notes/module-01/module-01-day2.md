# M1 Day2 — 开方

**日期**：________

## Issue 1 工程化解法（#803 · 不换模型）

**方案一句话**：detect container dead → 升维为 fatal → raise FatalAgentError → controller interrupt → save trajectory


| 维度          | 我的方案                                                                                                                                                                                                                                          |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 终止条件        | `_docker_exec` 检测到容器不可达时返回 `error_class: fatal`；`LoopEngine.run()` 见 fatal 即 `raise FatalAgentError`；`cli.py` 捕获后 `abort_fatal` + `persist`，进程 exit 2。**fatal 优先于 max_rounds**，不在 dead substrate 上烧完剩余轮次。                                     |
| observe 检查点 | **Runtime 层**：`ToolExecutor._docker_exec` 检查 `_container_alive`（模拟 container_timeout 后 `--rm`）。**输出层**：stderr 含 dead marker（`No such container` / `is not running`）时附带 `error_class: fatal`，而非仅 `returncode: -1`。对应 M1-K02：observe 必须带错误语义层级。 |
| replan 触发条件 | 仅 **retryable**（round1 测试失败）或 **recoverable**（round2 测试通过路径）进入 replan；**fatal 不进入 replan policy**——controller 在 act 阶段短路，不再 `_make_plan` 下一轮。                                                                                                 |
| 最大轮次 / 熔断   | `max_rounds=3`、`step_limit=20` 作兜底熔断（M1-K04）；#803 场景下 fatal 应在 round 2 act 即停，不应依赖 step_limit 才退出。可选增强：round 开始前 proactive 检查 substrate health（PR #832 的 wall_time_limit 思路）。                                                                 |
| 监控指标        | `trace.json`：每次 tool call 的 `error_class` 字段；fatal run 最后一次 `docker_exec` 应为 `"fatal"`。`state.json`：`history` 最后一 phase 为 `done` + `FatalAgentError: ...`；`success: false` 且 `round` 未达 max_rounds。                                           |
| 回滚预案        | Substrate 已死 **无法 in-loop 补偿**；正确行为是 interrupt + 持久化 trajectory，由用户重启 session / 新容器后再跑。不做 blind retry。                                                                                                                                        |


**Runtime 任务（issues.md 绑定）**：

```powershell
python cli.py run --task "container death" --simulate-container-death 1
```

**预期证据**（L2）：

- CLI 打印 `Fatal: Error: No such container: container is not running`
- `m1_m2/evidence/<id>/trace.json` 含 `"error_class": "fatal"`
- `m1_m2/evidence/<id>/state.json` 的 `history` 无 round 3，末行含 `FatalAgentError`

**本次证据路径**：`TrackARuntime/m1_m2/evidence/7c3a04c8/state.json`、`TrackARuntime/m1_m2/evidence/7c3a04c8/trace.json`

## Issue 2 工程化解法

**方案一句话**：**retryable/recoverable → ErrorObs 路径 → replan 继续 loop；fatal → Exception 短路 → 不进 replan**（A/B 两条命令对照 #4575）


| 维度          | 我的方案                                                                                                                                                                                            |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 终止条件        | recoverable 路径（本次）：round2 observe 通过 → success=true → done，cli exit 0。fatal 路径（B 侧）：error_class==fatal → FatalAgentError → exit 2。不是「同样错误烧完轮次」——本次 round2 已成功退出                                 |
| observe 检查点 | `_observe_tests`：exit_code=0 → recoverable；≠0 → retryable；tool 返回 fatal → fatal。分类写在 **state history 的** `[retryable]` **/** `[recoverable]`，对应 M1-K02 + M1-K05。                                |
| replan 触发条件 | 仅 `ok=false` 且 `round < max_rounds` 时进入 replan（`5fb33372` history 第 5 行）。round2 plan **引用** observation（history 第 6 行 vs trace event 3）。**fatal 不触发 replan**（B 侧 round2 无 replan phase）。M1-K03。 |
| 最大轮次 / 熔断   | A 侧：round2 成功即退出，未触达 `max_rounds=3`（M1-K04 兜底未触发）。B 侧：fatal 在 round2 act 短路，同样未烧满轮次。与 #4575 一致：**分类决定走 replan 还是 Exception 短路**，而非仅靠 max_rounds 兜底。                                             |
| 监控指标        | A 侧：`success=true`；history 含 `replan`；trace 无 `error_class: fatal`。B 侧：`success=false`；history 以 `FatalAgentError` 结束。两条 run 对比即 M1-K05 L2 证据。                                                  |
| 回滚预案        | recoverable：in-loop replan 补偿（本次即成功范例）。fatal：interrupt + persist，用户重启 session（B 侧）。                                                                                                             |


**Runtime 任务（issues.md 绑定）**：

```powershell
# A 侧（本次）
python cli.py run --task "fix test"
# 证据：TrackARuntime/m1_m2/evidence/5fb33372/

# B 侧（Issue 1 同命令，Issue 2 对照必需）
python cli.py run --task "container death" --simulate-container-death 1
# 证据：TrackARuntime/m1_m2/evidence/7c3a04c8/
```

**预期证据**（L2）：

- A 侧：`success=true`；history 含 `[retryable]` → `replan` → `[recoverable]` → `Task completed`
- B 侧：history 无 round2 replan；末行 `FatalAgentError`；trace 含 `"error_class": "fatal"`
- 对照：同一 runtime、同一 controller，**错误分类不同 → 策略不同**（对齐 #4575 ErrorObs vs Exception 短路）

**与 TrackARuntime 映射（Issue 2）**


| **文件**                       | **Issue 2 相关逻辑**                                  |
| ---------------------------- | ------------------------------------------------- |
| `loop_engine._observe_tests` | retryable / recoverable / fatal 三分                |
| `loop_engine.run` 124–133    | recoverable 失败 → replan；fatal → 110–114 raise     |
| `loop_engine._make_plan`     | round2 引用 observation（M1-K03）                     |
| `cli.cmd_run`                | 仅 fatal 走 except；recoverable 走正常 persist exit 0/1 |


## Issue 3A 工程化解法（#4579 · stuck loop）

**方案一句话**：跨轮无进展 → meta 层 `_check_fingerprint_loop` override replan → FatalAgentError（不把 loop 再 dispatch 给 agent）


| 维度          | 我的方案                                                                                                                                                                                                |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 终止条件        | 相同 `docker_exec` args 累计 ≥3 次 → `_check_fingerprint_loop` raise `FatalAgentError`；发生在 **round 4 plan 后、act 前**（`416be508` 无 round4 `act`）。**fingerprint 优先于 max_rounds=5**。cli exit 2 + persist。    |
| observe 检查点 | **单步层（M1-K02）**：每轮 `_observe_tests` → `[retryable]`（测试始终失败）。**meta 层（M1-K06）**：`_check_fingerprint_loop` 对 `(tool, command)` 做 hash 累计——trace **不**逐步写 loop，达阈值才 Fatal。                             |
| replan 触发条件 | **单步 replan（M1-K03）**：`ok=false` 且 `round < max_rounds` → round1–3 仍 `replan`（replan policy 放行）。**meta override**：第 3 次相同 args 时 **禁止**再 act，不再 `_make_plan` 下一轮。对齐 #4579：已知 stuck 后不浪费一轮 dispatch。 |
| 最大轮次 / 熔断   | `max_rounds=5` 作兜底；本 run `round=4` 即 fatal 退出，未烧满 5 轮。若无 fingerprint，会空转到 max_rounds → `Max rounds exceeded`（#4579 要避免的路径）。                                                                         |
| 监控指标        | `state.json`：`success=false`；round1–3 每轮 `[retryable]`→`replan`；末行 `FatalAgentError: Loop fingerprint detected...`。`trace.json`：event 3 与 5 的 `docker_exec.input.command` **完全相同**（跨轮 loop 证据）。     |
| 回滚预案        | stuck 态 **in-loop 无法补偿**；fatal interrupt + 用户改策略/换 prompt 后重启 session。不做 blind retry 到 max_rounds。                                                                                                  |


**Runtime 任务（issues.md 绑定）**：

```powershell
python cli.py run --task "stuck loop" --always-fail-tests --max-rounds 5
```

> `**--task` 仅标签**；行为由 `--always-fail-tests` + `--max-rounds 5` 驱动。详见 [issues.md](issues.md)「task vs flag」。

**预期证据**（L2）：

- CLI：`Fatal: Loop fingerprint detected: docker_exec called 3x with identical args`
- `state.json`：`round=4`；history 末行 FatalAgentError；**无** round4 `act`
- `trace.json`：round2+ 的 `docker_exec.command` 重复（与 `5fb33372` 对比：那边 command **变**且测试通过）

**本次证据路径**：`TrackARuntime/m1_m2/evidence/416be508/state.json`、`TrackARuntime/m1_m2/evidence/416be508/trace.json`

**与 TrackARuntime 映射（Issue 3A）**


| 文件                                    | Issue 3A 相关逻辑                                                  |
| ------------------------------------- | -------------------------------------------------------------- |
| `loop_engine._check_fingerprint_loop` | meta 层；act 前门禁；≥3 相同 args → Fatal                              |
| `loop_engine._make_plan`              | round≥2 引用 observation（形态像真 replan，但 observation 不变 → plan 稳定） |
| `tool_executor._run_tests`            | `--always-fail-tests` → 始终 `[retryable]`                       |
| `LoopConfig.always_fail_tests`        | flag 传入 ToolExecutor                                           |
| `cli.cmd_run`                         | 同 Issue 1：FatalAgentError → abort_fatal → persist              |


---

## Issue 3B 工程化解法（#5099 · pseudo-replan）

**方案一句话**：observe 为 `[retryable]` 且 replan 在走，但 plan/command 冻结不变 → fingerprint 判定假恢复 → fatal


| 维度          | 我的方案                                                                                                                                                                                       |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 终止条件        | 同 3A 机制：`_check_fingerprint_loop` 在第 3 次相同 `docker_exec` args 时 Fatal。`6363ddfb` round4 无 `act`，cli exit 2。                                                                                |
| observe 检查点 | **单步层（M1-K02）**：每轮 `[retryable]`——分类**正确**，不是 #803 式 observe 缺失。**问题在进展**：`--pseudo-replan` 使 round≥2 plan **冻结**为 `Let me fix the parameter name...`，tool args 无变化。                       |
| replan 触发条件 | replan policy 仍放行（history 有 `replan`）——这是 #5099 陷阱：**replan 发生了，但无 state/action 变化**。M1-K03：replan ≠ blind retry。meta 层 fingerprint 作 progress 门禁。                                         |
| 最大轮次 / 熔断   | 同 3A：`max_rounds=5` 兜底；fingerprint 在 round4 抢先终止。                                                                                                                                          |
| 监控指标        | **对照 Issue 2 A 侧**（`5fb33372`）：trace event1 vs 3 command **不同** + 测试通过 = 真 replan。**本 run**：trace event3/5 command 均为 `Let me fix the parameter name...`；history 多轮 `[retryable]` 后 fatal。 |
| 回滚预案        | 假恢复无法 in-loop 修复；fatal 后需换 tool 参数策略或人工介入，而非继续相同 tool call。                                                                                                                                |


**Runtime 任务（issues.md 绑定）**：

```powershell
python cli.py run --task "pseudo replan" --always-fail-tests --pseudo-replan --max-rounds 5
```

> 3B 比 3A **多 `--pseudo-replan`**；task 名仍仅为标签。

**预期证据**（L2）：

- 同 3A：FatalAgentError fingerprint 消息；round4 无 `act`
- **3B 特有**：`state.json` plan/history round2+ 均为 `Let me fix the parameter name — use indexPattern not index_pattern`
- **对照**：`m1_m2/evidence/5fb33372/trace.json` round2 command **变了**且 success=true

**本次证据路径**：`TrackARuntime/m1_m2/evidence/6363ddfb/state.json`、`TrackARuntime/m1_m2/evidence/6363ddfb/trace.json`

**与 TrackARuntime 映射（Issue 3B）**


| 文件                                    | Issue 3B 相关逻辑                                               |
| ------------------------------------- | ----------------------------------------------------------- |
| `loop_engine._make_plan`              | `pseudo_replan=True` → round≥2 返回 `_PSEUDO_REPLAN_PLAN`（冻结） |
| `loop_engine._check_fingerprint_loop` | 同 3A；机制相同，叙事侧重「retryable 仍可无进展」                             |
| `tool_executor._run_tests`            | `--always-fail-tests`                                       |
| `LoopConfig.pseudo_replan`            | 3B 专用 flag                                                  |


---

## 与 TrackARuntime 的映射（Issue 1）


| 文件                 | 已实现内容                                                                               | 对应 Day2 哪一行     |
| ------------------ | ----------------------------------------------------------------------------------- | --------------- |
| `tool_executor.py` | `kill_container()` 模拟 timeout；`_docker_exec` 返回 dead marker + `error_class: fatal`  | observe 检查点     |
| `loop_engine.py`   | round > N 时 `kill_container()`；act 后 `error_class==fatal` → `raise FatalAgentError` | 终止条件            |
| `errors.py`        | `ErrorClass.FATAL`、`FatalAgentError`                                                | M1-K05 错误分类     |
| `cli.py`           | `except FatalAgentError` → `abort_fatal` → `persist` → exit 2                       | save trajectory |
| `trace.py`         | `TraceEvent.error_class` 写入 trace.json                                              | 监控指标            |


- **将在 `loop_engine.py` 或相关模块改什么（L3 可选）**：
  - `tool_executor.py`：将 dead marker 抽成 configurable 列表（对齐 PR #807 的 `_CONTAINER_DEAD_MARKERS`）
  - `LoopConfig`：可选 `wall_time_limit` / 每 round 开始前 substrate health check
- **为什么这样改**：
  - Day1 根因是 observe 未升维 fatal；L2 基线已在 tool + controller 两层闭合
  - L3 扩展对齐 PR #807 的可配置 marker 与 proactive 超时，而非改 loop 主结构

---

## Issue 4 工程化响应（Case 9 · Token 配额雪崩 · Learner 自填）

> **前置**：Issue 1–3B 方案已写；本 Issue 把 **同一 silent loop** 加上 **成本/配额层** 监控与熔断。

**方案一句话**：（early fatal 不变 + per-run token budget 告警 + 429 隔离）

| 维度 | 我的方案（Learner 自填 · 导师脚手架） |
|---|---|
| 终止条件 | **首选**：Issue 1/3A 的 early fatal（不变）。**兜底**：M1-K04 `cost_limit` / `step_limit`（#803 原文路径——仅延迟暴露） |
| observe / meta | 同 Issue 1/3A；另加 **token 斜率**：N 分钟内 LLM call 数超阈值 → meta fatal（不必等 fingerprint 第 3 次） |
| 监控指标 | `llm_calls_per_run`；`trace.json` **event 条数**；应用层 `cost_per_request`；infra **429 率** |
| 隔离 / 回滚 | Kill 空转 run_id；tenant 暂停 dispatch；429 时 **停止 retry 同一 loop**，等 RPM 窗口 |

**Runtime 对照（口述，不必新命令）**：

```powershell
# 若 #803 未 fatal， hypothetically 会烧满 step_limit —— 对照 Issue 1 的 7c3a04c8（已 early fatal）
python cli.py run --task "container death" --simulate-container-death 1
python cli.py run --task "stuck loop" --always-fail-tests --max-rounds 5
```

> **导师提示**：Day2 写清 **cost_limit 是最后一道门，不是第一 fix**；第一 fix 仍是 Issue 1/3A 的 fatal / fingerprint。参考 [SOP Case 9](../case-library/sops/sop-case-09-token-burn-rate-limit-cascade.md)。

