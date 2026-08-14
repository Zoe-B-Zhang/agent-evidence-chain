# M1 Day3 — 对照 PR

**日期**：________

## Issue 1（#803 ↔ PR #807）

- **PR 链接**：[mini-swe-agent PR #807](https://github.com/SWE-agent/mini-swe-agent/pull/807)
- **实际改法摘要**：
  1. 新增 `ContainerNotRunning` 异常，继承已有 `InterruptAgentFlow`（与 `LimitsExceeded`、`Submitted` 同级）。
  2. 在 `execute()` **两条路径**检测 dead marker：
    - subprocess 正常返回但 returncode≠0 且 stdout 含 marker → raise
    - except 块中 exception message 含 marker → raise
  3. Marker 列表：`"No such container"`、`"is not running"`、`"no such container"`（大小写兼容）。
  4. Agent `run()` 已有对 `InterruptAgentFlow` 的处理：记录 exit message → `finally: save()` 保存 trajectory → 停止 loop。
  5. 附带单元测试 + 真实 Docker 的 integration test（container_timeout 到期场景）。
  6. 相关增强：PR #832 增加 `wall_time_limit_seconds`，在容器 timeout **之前** proactive 停止 agent（预防性熔断，非 #807 核心但同属 #803 家族）。
- **与我 Day2 一致？** **部分一致（主链路同构，实现层与防御深度有差）**

  | 维度          | Day2 方案                                   | PR #807                                      | 判定                 |
  | ----------- | ----------------------------------------- | -------------------------------------------- | ------------------ |
  | 根因定位        | observe 未升维 fatal，substrate 死仍 replan     | 同：execute 把 dead 当普通 observation             | ✅ 一致               |
  | 检测点         | `_docker_exec` + dead marker              | `execute()` return path + except path        | ✅ 一致               |
  | 中断机制        | `FatalAgentError` → controller 跳出 loop    | `ContainerNotRunning` → `InterruptAgentFlow` | ✅ 同构（Exception 短路） |
  | 轨迹保存        | fatal 后 `persist` trace + state           | `finally: save()` trajectory                 | ✅ 一致               |
  | 检测位置        | tool 返回 fatal class → loop_engine 再 raise | execute 内直接 raise                            | ⚠️ 层略不同，效果相同       |
  | dead marker | 硬编码一条 stderr 字符串                          | 可配置 tuple，覆盖大小写                              | PR 更完整             |
  | 预防性熔断       | Day2 仅提及可选                                | PR #832 wall_time_limit 已合并                  | PR 更前瞻             |
  | 测试          | 本地跑 cli + 看 `m1_m2/evidence/*/*.json`                   | 单元 + Docker integration test                 | PR 更严谨             |

- **PR 更优之处**（相对 TrackARuntime L2 基线）：
  - **复用已有中断体系**：`ContainerNotRunning ⊂ InterruptAgentFlow`，不另造 event stream 分支（与 #4575 教训同方向）。
  - **双路径检测**：returncode 路径和 exception 路径都覆盖，避免漏网。
  - **Marker 可配置 + 大小写**：L3 扩展方向明确。
  - **真实 Docker integration test**：验证 container_timeout 真实到期，而非仅 mock flag。
  - **预防 + 兜底**：#832 wall_time_limit 在 substrate 死之前停 agent，减少「先死再检」窗口。
- **更新后的认知**：
  - Day1「主要是 observe 问题」仍然成立；Day3 补充：**fix 的正确形态是 observe 层 detect + 现有 interrupt 体系 raise**，不是加新的 observation 类型让 model 自己决定。
  - TrackARuntime 的 L2 基线与 PR #807 **行为等价**（fatal → stop → save），差距在工程完整度（marker 配置、双路径、集成测试、proactive limit）。
  - #803 的 silent loop 本质是 **缺少 substrate-level fatal 信号**；step_limit / cost_limit 只是延迟暴露，不是修复。

## Issue 2

- **PR 链接**：[OpenHands PR #4573](https://github.com/OpenHands/OpenHands/pull/4573) — `fix(controllor): make agent controller stops when encounter fatal observation`
- **实际改法摘要**：
  1. **现象**：SWE-Bench eval 中 eval-runtime 404（substrate 已死），runtime 已产出 `FatalErrorObservation`，但 controller 仍继续 dispatch STEP 3/4/5/6，空烧 API。
  2. **根因**：`_handle_observation` 收到 `FatalErrorObservation` 时先调 `report_error()` → 向 event stream 追加 `ErrorObservation`（recoverable 通道）→ CodeAct agent 把所有 error obs 一视同仁喂给 LLM → 触发下一轮 action；`set_agent_state_to(ERROR)` 虽在后面执行，但 loop 已被新 ErrorObs 续命。（event stream handler 在处理 fatal 时又往 stream 里写 recoverable 事件，形成反馈环。）
  3. **修复**（`agent_controller.py` `_handle_observation`，仅 6 行 diff）：
    - **去掉** `report_error()` 调用（不再向 stream 追加 ErrorObservation）。
    - **直接** `self.state.last_error = f'There was a fatal error...'`（eval 报告用）。
    - merge metrics → `await self.set_agent_state_to(AgentState.ERROR)`。
  4. **验证**：新增 `test_run_controller_with_fatal_error`——mock runtime 返回 `FatalErrorObservation` 后，断言 `iteration==1`、`agent_state==STOPPED`、`last_error` 含 fatal 文案、event stream 不再增长。
  5. **后续演进**：review 指出这是 hotfix；#4575 进一步把 fatal 改 **raise Exception 短路**，彻底不进 event stream（与 #807 的 Exception 短路同构）。
- **与 Day2 一致？** **部分一致（根因与策略表正确，Day2 对标 #4575 根治、#4573 仅为 controller hotfix）**

  | 维度        | Day2 方案                                    | PR #4573                                                   | 判定              |
  | --------- | ------------------------------------------ | ---------------------------------------------------------- | --------------- |
  | 根因定位      | fatal → Exception 短路；recoverable → replan  | 同：fatal 信号有，但 controller 未 enforce stop                    | ✅ 一致            |
  | 错误分类      | retryable / recoverable / fatal 三分（M1-K05） | FatalErrorObservation 已存在，被 report_error 误走 recoverable 通道 | ✅ 一致            |
  | 中断机制      | `FatalAgentError` → cli except 短路          | `set_agent_state_to(ERROR)`，不经 report_error                | ✅ 同构（stop loop） |
  | replan 策略 | fatal 不触发 replan（M1-K03）                   | 去掉 ErrorObs 回流，loop 不再续命                                   | ✅ 一致            |
  | 修复深度      | 对标 #4575：fatal 改 raise Exception           | #4573：controller 层改处理顺序（hotfix）                            | ⚠️ Day2 更前瞻     |
  | 证据        | A/B：`5fb33372` vs `7c3a04c8`               | eval 404 + unit test                                       | ✅ 行为等价          |


## Issue 3A（stuck loop ↔ PR #4579）

- **PR 链接**：[OpenHands PR #4579](https://github.com/OpenHands/OpenHands/pull/4579) — `fix(controller): stop when run into loop`
- **实际改法摘要**：
  1. **现象**：Agent 陷入 action-observation 重复模式（如连续相同 `ls`）；`_stuck_detector` / `_is_stuck()` 已能识别 loop，但 controller 仍 dispatch 后续 LLM step，空烧 token 后才报错（#4573 review 中 xingyaoww 附的截图场景）。
  2. **根因**（`agent_controller.py` `_step()`，#4573 同族 + 时机错误）：
     - **时机**：旧代码 `_is_stuck()` 在 `agent.step()` **之后**（action 已写入 event stream）才检测。
     - **通道**：stuck 时走 `report_error('Agent got stuck in a loop')` → 追加 **ErrorObservation**（recoverable）→ loop 可续命。
  3. **修复**（+88/-6 行，2 文件）：
     - 把 `_is_stuck()` **前移**到 `_step()` 内、`agent.step()` **之前**（pending action 检查之后）。
     - stuck 时 **`event_stream.add_event(FatalErrorObservation('Agent got stuck in a loop'))`** 然后 `return`——不再 `report_error`，复用 #4573 修好的 fatal obs → `AgentState.ERROR` → stop 路径。
     - PR 描述：**不把 stuck 错误扔给 agent replan**，而是 throw fatal 停 controller。
  4. **验证**：新增 `test_run_controller_stop_with_stuck`——mock agent 反复返回 `CmdRunAction('ls')` + runtime 返回 ErrorObservation 触发 loop；断言 `iteration==4`、`agent_state==STOPPED`、events 含 4 对重复 action/obs、末行 `last_error` 含 stuck 文案。
  5. **与 #4573 / #4575 关系**：#4579 依赖 #4573 的 fatal obs 处理；#4575 进一步把 fatal 改 Exception 短路（同 #807 方向）。
- **与 Day2 一致？** **部分一致（目标同构，检测机制不同）**

  | 维度 | Day2 方案 | PR #4579 | 判定 |
  | --- | --- | --- | --- |
  | 根因定位 | 跨轮无进展，replan 等于 blind retry | stuck 已 detect，但 dispatch 后才拦 + recoverable 通道 | ✅ 一致 |
  | 检测层 | meta 层 `_check_fingerprint_loop`（tool+args hash） | controller 内置 `_stuck_detector.is_stuck()` | ⚠️ 机制不同 |
  | 检测时机 | round4 plan 后、**act 前** | `_step()` 内、**agent.step 前** | ✅ 一致（dispatch 前拦截） |
  | 中断机制 | `FatalAgentError` raise | `FatalErrorObservation` → #4573 fatal 路径 | ✅ 同构（fatal 短路） |
  | replan 策略 | meta override replan（M1-K03） | 不把 loop 再给 agent | ✅ 一致 |
  | 证据 | `m1_m2/evidence/416be508/` | unit test + #4573 讨论截图 | ✅ 行为等价 |

- **PR 更优之处**（相对 TrackARuntime L2）：
  - **dispatch 前拦截**：与 Day2 act 前 fingerprint 门禁同目标，OpenHands 复用已有 `_is_stuck()` 而非新造 meta 层。
  - **fatal 通道统一**：stuck 走 `FatalErrorObservation`，与 substrate fatal（#4573）同终止路径。
- **更新后的认知**：
  - #4579 是 **第三类 silent loop**：环境可能正常，但 **行为无进展** → replan 不应继续（M1-K06）。
  - Day2 fingerprint 比 PR `_stuck_detector` 更通用（progress 门禁）；#4579 证明 **检测时机 + 终止通道** 与检测算法同等重要。

## Issue 3B（pseudo-replan ↔ Issue #5099）

- **Issue 链接**：[LangGraph #5099](https://github.com/langchain-ai/langgraph/issues/5099) — `The agent via (create_react_agent) is looping and not able to complete the task`
- **对照 PR**：课程 **未指定** Day3 merged PR。#5099 已被 maintainer 以「新版本无法复现」关闭；相关但未合并：[langgraph PR #6889](https://github.com/langchain-ai/langgraph/pull/6889)（检测相同 tool call 循环，已 close）。**L2 证明靠 Day2 TrackARuntime + `m1_m2/evidence/6363ddfb/`，非 PR diff。**
- **Issue 实际现象摘要**（#5099 原文）：
  1. `create_react_agent` + Elastic MCP `list_indices`：ToolMessage 报 `indexPattern` Required，agent 用了 `index_pattern`。
  2. Agent 文本：「Let me fix that by using the correct parameter name」——但 **下一轮 args 仍是 `index_pattern: '*'`**。
  3. 重复至 `recursion_limit`；同一 MCP 在 Claude Code / pydanticAI 可正常工作。
- **根因**（M1 视角，非 #5165）：
  1. **单步 observe 正确**：ToolMessage 是 recoverable error（`Please fix your mistakes`）——不是 #803 式 observe 缺失。
  2. **replan 路径在走**：agent 进入下一轮——不是 #4575 式 controller 漏停。
  3. **无 progress**：`(tool, args)` fingerprint 不变 → **假恢复 / pseudo-replan**（M1-K03：replan ≠ blind retry）。
  4. **缺 meta 层门禁**：无 fingerprint / loop detector 在 N 次相同 pattern 后 escalate fatal（M1-K06）。
- **TrackARuntime Day2 改法**（模拟 #5099）：
  1. `--pseudo-replan`：`loop_engine._make_plan` round≥2 冻结 plan 为 `Let me fix the parameter name...`。
  2. `_check_fingerprint_loop`：相同 `(tool, command)` ≥3 次 → `FatalAgentError`（与 3A 同机制，叙事侧重「retryable 仍可无进展」）。
  3. 命令：`python cli.py run --task "pseudo replan" --always-fail-tests --pseudo-replan --max-rounds 5`
- **验证**（`m1_m2/evidence/6363ddfb/`）：
  - CLI：`Fatal: Loop fingerprint detected: docker_exec called 3x with identical args`
  - `state.json`：round1–3 每轮 `[retryable]`→`replan`；round4 无 `act`；末行 FatalAgentError
  - `trace.json`：round2+ 的 `docker_exec.input.command` **均为** `Let me fix the parameter name...`
  - **对照** `m1_m2/evidence/5fb33372/`：trace event1 vs 3 command **不同** + 测试通过 = 真 replan
- **与 Day2 一致？** **一致（Issue 无 merged PR，Day2 runtime 即 L2 对照物）**

  | 维度 | Day2 方案 | #5099 Issue | 判定 |
  | --- | --- | --- | --- |
  | 根因定位 | replan 无 state/action 变化 | LLM 声称 fix 但 args 不变 | ✅ 一致 |
  | observe | `[retryable]` 分类正确 | ToolMessage recoverable error | ✅ 一致 |
  | 缺陷层 | meta 层缺 progress 门禁 | 无 loop/fingerprint escalate | ✅ 一致 |
  | fix 方向 | fingerprint → fatal | 社区未 merged fix；TrackARuntime 已模拟 | ✅ Day2 闭合 |
  | 与 3A 差异 | `--pseudo-replan` 冻结 plan | observation 不变但 LLM 也不改 args | 叙事不同，机制同 |

- **更新后的认知**：
  - #5099 与 #5165 **不是同一 issue**：#5165 是 `astream_events` streaming 层参数 schema bug；#5099 是 **replan 假恢复**。
  - 第三类 loop 的 fix 形态：**meta 层 fingerprint override replan**，不是改 observe 分类、也不是 controller fatal 通道（除非 fingerprint 达阈值后 escalate）。

## Issue 4（Case 9 · 平台后果校准 · Learner 自填）

- **对照物**：[Case 9](../case-library/cases/case-09-token-burn-rate-limit-cascade.md) · [SOP](../case-library/sops/sop-case-09-token-burn-rate-limit-cascade.md)
- **与 Issue 1–3 一致？** （Learner 自填）

  | 维度 | Issue 1/3A fix | Case 9 平台层 | 判定 |
  | --- | --- | --- | --- |
  | 根因 | silent loop 未停 | 同族 + 共享配额无隔离 | |
  | CTL fix | fatal / fingerprint | 同左（**必须先做**） | |
  | SLO fix | （Issue 1–3 未写） | per-run budget · 429 监控 · tenant 隔离 | |
  | 监控 | trace error_class | + llm_calls/run · 429 率 | |

- **Day3 学到什么**（Learner 自填 · 导师脚手架）：
  1. **step_limit / cost_limit 只是延迟暴露**（#803 原文）——不能替代 early fatal。
  2. 生产上 silent loop 的损害 = **Token × 共享 Key** → Case 9 的 429 雪崩。
  3. 口述链：**Issue 1 传感器错** 或 **Issue 3A 无进展** → 若未 fatal → Case 9 平台后果。

> **练习**：用 2 分钟口述「现象 → CTL 根因 → SLO 次因 → 监控 → 隔离」；可填 SOP「我的项目映射」段。

## 校准结论

- [x] Issue 1 思路与 PR #807 主链路一致 → 认知达标（L2）
- [x] Issue 2 根因（分类与终止策略脱节 / 断路器没跳）与 PR #4573 一致 → 认知达标（L2）；Day2 对标 #4575 根治方向正确，#4573 仅为前置 hotfix
- [x] Issue 3A 主链路与 PR #4579 一致（dispatch 前拦截 + fatal 通道）→ 认知达标（L2）
- [x] Issue 3B 根因与 #5099 + Day2 runtime 一致（假恢复 / fingerprint 门禁）→ 认知达标（L2）；无 merged OSS PR，以 TrackARuntime 为对照物
- [ ] Issue 4 Case 9 平台后果口述完成（可选 L2+） → M1-K04 与 M5 监控衔接
- [ ] 被 PR 打败 → 记录差距，延长 2 天再练

**Issue 1–3 综合判定**：L2 达标。三类 silent loop 分层清晰：

| 类型 | 代表 | 缺陷层 | fix 形态 |
| --- | --- | --- | --- |
| 传感器错 | #803 / #807 | observe 未升维 fatal | execute detect + raise |
| 断路器没跳 | #4573 → #4575 | controller 未 enforce | fatal 不进 recoverable 通道 |
| 无进展空转 | #4579 / #5099 | replan 无 progress | meta fingerprint → fatal（dispatch/act 前拦截） |

- **写入 GUIDE 或 exit 的要点**：
  - Fatal substrate 错误必须在 **observe/execute 层升维** 并 **Exception 短路 loop**；不能当 recoverable observation 继续烧 API。
  - **#4573 教训**：event stream handler 处理 fatal 时，`report_error()` 会把 ErrorObservation 写回 stream → agent 当 recoverable 继续 step。
  - **#4579 教训**：stuck detect 必须在 **dispatch 前**，且走 fatal 通道，不能把 loop 再给 agent。
  - **#5099 教训**：replan ≠ blind retry；须 **action/progress 变化**，否则 meta 层 fingerprint 应 override replan。
  - 证据：`m1_m2/evidence/416be508/`（3A stuck）、`m1_m2/evidence/6363ddfb/`（3B pseudo-replan）vs `m1_m2/evidence/5fb33372/`（真 replan 对照）。

