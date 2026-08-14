# OSS-4579 — Stuck Loop 检测到了但仍 Dispatch（无进展空转）

| 字段 | 值 |
|---|---|
| **ID** | oss-4579 |
| **标签** | agent, loop, meta-observe, fatal |
| **关联模块** | M1 |
| **Case 库关联** | 与 [oss-803](oss-803-mini-swe-container-silent-loop.md)、[oss-4575](oss-4575-openhands-errorobs-vs-fatal.md) 同属 silent loop 家族；本 case **环境可正常，但跨轮无进展**；扩展 [Case 09](../cases/case-09-token-burn-rate-limit-cascade.md) |
| **Issue / 阅读** | [OpenHands PR #4579](https://github.com/OpenHands/OpenHands/pull/4579) |
| **对照 PR** | [#4579](https://github.com/OpenHands/OpenHands/pull/4579) — `fix(controller): stop when run into loop` |
| **TrackARuntime** | `python cli.py run --task "stuck loop" --always-fail-tests --max-rounds 5` |
| **Day1–3 笔记** | [`module-01/module-01-day1.md`](../../module-01/module-01-day1.md) Issue 3A · [`module-01-day2.md`](../../module-01/module-01-day2.md) · [`module-01-day3.md`](../../module-01/module-01-day3.md) Issue 3A |
| **添加日期** | 2026-07 |

## 场景

Agent 陷入 action-observation 重复模式（如连续相同 `ls`、相同 tool args）；substrate 仍可用，单步 observe 为 retryable。

## 现象

- `_stuck_detector` / `_is_stuck()` 已能识别 loop。
- Controller 仍 dispatch 后续 LLM step，浪费 token，长时间空转后才报错。
- 用户侧感知：silent loop（与 #803 表面相似，根因层不同）。

## 根因

1. **时机**：旧代码 `_is_stuck()` 在 `agent.step()` **之后**才检测——action 已发出。
2. **通道**：stuck 时走 `report_error()` → **ErrorObservation**（recoverable），与 #4573 同族，loop 可续命。
3. **#4579 修复**：`_is_stuck()` **前移**到 dispatch 前；stuck 时 emit `FatalErrorObservation` 并 return——**不把 loop 再给 agent replan**。

## 系统等价物

API 网关已检测到客户端重试风暴（相同请求 fingerprint），仍转发给后端 → 应在 edge 拒载，而非让后端再试一轮。

## TrackARuntime 证据

- **Run**：`m1_m2/evidence/416be508/`
- CLI：`Fatal: Loop fingerprint detected: docker_exec called 3x with identical args`
- `state.json`：`round=4`；round1–3 每轮 `[retryable]`→`replan`；**无** round4 `act`
- `trace.json`：event 3 与 5 的 `docker_exec.input.command` **完全相同**
- **对照真 replan**：`m1_m2/evidence/5fb33372/` trace command **变化** + 测试通过

## 学习记录（自填）

- **Day3 与 PR #4579 差距**（Day2 fingerprint vs OpenHands `_stuck_detector`）：
- **M1 rubric 自评**：
