# M1 精选 Issue（第 1 周）

> 索引：[tutor/README.md](../tutor/README.md) · 知识工程点：[knowledge.md](knowledge.md)

## M1-I01 主修 — silent loop（#803）

| 项 | 内容 |
|---|---|
| Issue | [mini-swe-agent #803](https://github.com/SWE-agent/mini-swe-agent/issues/803) · [案例库全文](../case-library/oss-incidents/oss-803-mini-swe-container-silent-loop.md) |
| Day3 PR | [PR #807](https://github.com/SWE-agent/mini-swe-agent/pull/807) |
| K 点 | M1-K02, M1-K05, M1-K04 |
| **Runtime 任务** | `python cli.py run --task "container death" --simulate-container-death 1` → 必须 Fatal + `trace.json` 含 `error_class: fatal` |
| **L2 证明** | Day2 写：detect dead container → raise FatalAgentError；Day3 对照 PR #807 |
| **L3 扩展** | 在 `tool_executor.py` 增加 dead marker 列表 configurable |
| **证据示例** | `m1_m2/evidence/7c3a04c8/` |

## M1-I02 主修 — ErrorObs vs Fatal（#4575）

| 项 | 内容 |
|---|---|
| 阅读 | [OpenHands PR #4575](https://github.com/All-Hands-AI/OpenHands/pull/4575) · 前置 [#4573](https://github.com/All-Hands-AI/OpenHands/pull/4573) · [案例库全文](../case-library/oss-incidents/oss-4575-openhands-errorobs-vs-fatal.md) |
| Day3 PR | [OpenHands PR #4575](https://github.com/All-Hands-AI/OpenHands/pull/4575) |
| K 点 | M1-K05, M1-K03 |
| **Runtime 任务** | **A/B 对照**（两条命令，同一 runtime）：<br>① `python cli.py run --task "fix test"`<br>② `python cli.py run --task "container death" --simulate-container-death 1` |
| **L2 证明** | 写错误分类表：recoverable / retryable / fatal 各举 runtime 一例；对比两份 `state.json` 的 history 末段 |
| **证据示例** | A 侧：`m1_m2/evidence/5fb33372/` · B 侧：`m1_m2/evidence/7c3a04c8/` |

## M1-I03A 补充 — stuck loop → fatal（#4579）

| 项 | 内容 |
|---|---|
| 阅读 | [OpenHands PR #4579](https://github.com/All-Hands-AI/OpenHands/pull/4579) · Day1 笔记 [Issue 3A](module-01-day1.md) · [案例库全文](../case-library/oss-incidents/oss-4579-openhands-stuck-loop-fatal.md) |
| Day3 PR | [OpenHands PR #4579](https://github.com/All-Hands-AI/OpenHands/pull/4579) |
| K 点 | M1-K03, M1-K06, M1-K05 |
| **与 I01/I02 差异** | 环境正常，但 **跨轮无进展**（相同 `docker_exec` args 重复）；**meta 层** fingerprint 应 override replan，round4 前 fatal |
| **Runtime 任务** | `python cli.py run --task "stuck loop" --always-fail-tests --max-rounds 5` |
| **L2 证明** | Day2 写 meta-observe → override replan → FatalAgentError；Day3 对照 PR #4579 |
| **证据示例** | `m1_m2/evidence/416be508/` |
| **预期证据** | CLI：`Fatal: Loop fingerprint detected...`；`round=4` 且无 round4 `act`；trace event 3/5 `command` 相同 |

## M1-I03B 补充 — pseudo-replan / 假恢复（#5099）

| 项 | 内容 |
|---|---|
| 阅读 | [LangGraph #5099](https://github.com/langchain-ai/langgraph/issues/5099) · Day1 笔记 [Issue 3B](module-01-day1.md) · [案例库全文](../case-library/oss-incidents/oss-5099-langgraph-pseudo-replan-loop.md) |
| K 点 | M1-K03, M1-K02, M1-K06 |
| **与 I01/I02/I03A 差异** | 单步 observe 为 `[retryable]` 无误，replan 也在走，但 **`--pseudo-replan` 冻结 plan** → args 不变；对比 `5fb33372`（command 变且成功） |
| **Runtime 任务** | `python cli.py run --task "pseudo replan" --always-fail-tests --pseudo-replan --max-rounds 5` |
| **L2 证明** | Day2 写：replan ≠ blind retry，须 action 变化；fingerprint 抓假恢复 |
| **证据示例** | `m1_m2/evidence/6363ddfb/` |
| **预期证据** | 同 3A fatal 消息；trace round2+ `command` 均为 `Let me fix the parameter name...`；history 多轮 `[retryable]` |

## M1-I04 扩展 — Token 空转 → 配额雪崩（Case 9）

| 项 | 内容 |
|---|---|
| 阅读 | [Case 9 叙事](../case-library/cases/case-09-token-burn-rate-limit-cascade.md) · [SOP](../case-library/sops/sop-case-09-token-burn-rate-limit-cascade.md) |
| 前置 | 完成 I01–I03B 三联 silent loop 后再做 |
| K 点 | M1-K04, M1-K06；次 M5-K03 |
| **与 I01/I03A 关系** | #803 / #4579 **未 early fatal** 时，单 run 持续 dispatch → **Token 空转**；共享 Org Key 下升级为 **429 雪崩**（平台后果层） |
| **Runtime 任务** | 复跑 I01 + I03A 命令，口述：若 `max_rounds=5` 才停，5 轮 × 每轮 LLM call 在生产配额下的代价 |
| **L2 证明** | Day1 写平台现象 + 系统等价物；Day2 补 token budget 监控；Day3 串讲 I01–I03 → Case 9 |
| **练习文件** | [`module-01-day1.md`](module-01-day1.md) Issue 4 · [`module-01-day2.md`](module-01-day2.md) Issue 4 · [`module-01-day3.md`](module-01-day3.md) Issue 4 |

## M1-I05 扩展 — Checkpoint / Resume

| 项 | 内容 |
|---|---|
| 类型 | Runtime 能力练习 + 生产扩展 Case |
| Case | [Case 13](../case-library/cases/case-13-worker-death-checkpoint-resume.md) · [SOP](../case-library/sops/sop-case-13-worker-death-checkpoint-resume.md) |
| K 点 | M1-K04, M1-K07 |
| **Runtime 任务** | `python cli.py run --task "ckpt" --llm mock --checkpoint-dir m1_m2/evidence/checkpoints` → 中断后 `--resume-from <checkpoint.json>`（**再传** `--llm mock`） |
| **L2 证明** | 对照 checkpoint 与 resume 后 `state.json` 的 `round` / history 连续性；说明为何 `llm_client` 不在 checkpoint 内 |
| **L3 扩展** | 设计 queue / worker / lease / idempotency，把单机 checkpoint 升级为生产 resume contract |

## M1-I06 生产扩展 — Memory poisoning 与版本回滚

| 项 | 内容 |
|---|---|
| Case | [Case 14](../case-library/cases/case-14-memory-poisoning-version-rollback.md) |
| SOP | [sop-case-14](../case-library/sops/sop-case-14-memory-poisoning-version-rollback.md) |
| K 点 | M1-K08, M4-K09 |
| **学习任务** | 画 memory taxonomy：session summary、user preference、project rule、tool-derived fact；标注哪些允许持久化 |
| **L2 证明** | 能说明 memory 是持久状态，不是普通 context；写入必须有 source、scope、version、rollback |
| **L3 扩展** | 为 memory write 增加 policy stub、provenance 字段和 rollback 记录 |

> **无对应 Issue 的能力**（仅 knowledge 标注）：`--llm mock`、四层 `context_manager`、`metrics-*.json`、cost 硬限额。

---

## `--task` vs flag（必读）

**`--task "..."` 仅为 run 标签**（写入 `state.json` 的 `task` 字段），**不改变 loop 逻辑**。行为由 **flag** 决定：

| 想验证的场景 | 有效参数 | `--task` 是否决定行为 |
|---|---|---|
| #803 container 死 | `--simulate-container-death 1` | ❌ task 仅标签 |
| #4575 recoverable | （无额外 flag，默认 mock） | ❌ |
| #4579 stuck loop | `--always-fail-tests --max-rounds 5` | ❌ |
| #5099 pseudo-replan | 上列 **+ `--pseudo-replan`** | ❌ |

> 若只改 task 名而不加 flag，3A/3B **不会**与 Issue 2 不同。

---

## meta 层：如何从 trace/state 读 Issue 3

trace **不会**在每轮 act 写 `loop detected`。meta 层（`_check_fingerprint_loop`）在 controller 内部累计 `(tool, args)` hash，**达 3 次才 Fatal**。

| 读什么 | 在哪里 | Issue 3 含义 |
|---|---|---|
| 单步失败 | history `[retryable]` | 单步 observe（M1-K02）→ replan 仍放行 |
| 跨轮重复 | trace 多个 `docker_exec` 的 `input.command` **相同** | meta 层眼中的 loop（M1-K06） |
| 最终截断 | history 末行 `FatalAgentError: Loop fingerprint...`；**无** round4 `act` | meta override replan（对齐 #4579） |
| 真 replan 对照 | `m1_m2/evidence/5fb33372/` trace event1 vs 3 **command 不同** + 测试通过 | 有进展，不触发 fingerprint |

---

## Issue 对照速查

在 `TrackARuntime/` 目录执行：

| ID | OSS | Runtime 命令 | 关键证据 |
|---|---|---|---|
| I01 | #803 | `python cli.py run --task "container death" --simulate-container-death 1` | trace `error_class: fatal` |
| I02 | #4575 | `python cli.py run --task "fix test"` **+** 上条 | A: success / B: FatalAgentError |
| I03A | #4579 | `python cli.py run --task "stuck loop" --always-fail-tests --max-rounds 5` | trace command 重复；fingerprint fatal |
| I03B | #5099 | `python cli.py run --task "pseudo replan" --always-fail-tests --pseudo-replan --max-rounds 5` | plan 冻结；vs `5fb33372` command 变 |
| I05 | checkpoint + [Case 13](../case-library/cases/case-13-worker-death-checkpoint-resume.md) | `--checkpoint-dir` … → `--resume-from`（加 `--llm mock`） | round 连续；llm 需重注；生产化需 lease / idempotency |
| I06 | [Case 14](../case-library/cases/case-14-memory-poisoning-version-rollback.md) | 文档设计 | memory write policy、provenance、version rollback |

**CLI flag 说明**：

| Flag | 代码位置 | 作用 |
|---|---|---|
| `--always-fail-tests` | `tool_executor._run_tests` | 测试始终失败 → observation 不变 → 易触发相同 replan plan |
| `--pseudo-replan` | `loop_engine._make_plan` | round≥2 冻结 plan 为 `Let me fix the parameter name...`（#5099） |
| `--max-rounds 5` | `LoopConfig.max_rounds` | 默认 3 轮不够 fingerprint 累计到 3 次 |
| `--llm mock` | `cli.py` → `MockLLMClient` | 可插拔 plan（无独立 Issue） |
| `--checkpoint-dir` / `--resume-from` | `loop_engine` | I05 |
| `--require-hitl` | `ToolExecutor` | 见 M2-I04 |
