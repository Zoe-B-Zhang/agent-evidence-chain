# M1 Mastery Rubric

> 完整版：[MASTERY-RUBRIC.md](../MASTERY-RUBRIC.md) · 知识工程点：[knowledge.md](knowledge.md)

## M1 核心 K 点（模块 Exit 填此表）

| K 点 | 0 | 1 | 2 | 3 | 自评 | 证据路径 / 日期 |
|---|---|---|---|---|---|---|
| M1-K01 | | | ● | | **2** | `m1_m2/evidence/5fb33372/state.json`：history 含 parse_intent→plan→act→observe→replan→done；round/phase 可指读 · Day1–3 · 2026-07-05 |
| M1-K02 | | | | ● | **3** | history 含 `[retryable]`/`[recoverable]`；`trace.json` 含 `error_class`；已实现 `ErrorClass` + `_observe_tests` · `5fb33372` / `7c3a04c8` · 2026-07-05 |
| M1-K03 | | | ● | | **2** | `5fb33372` round2 plan 引用 observation；`6363ddfb` vs `5fb33372` 对照 replan≠blind retry · module-01-day2 Issue 3B · 2026-07-05 |
| M1-K05 | | | | ● | **3** | A/B：`5fb33372` recoverable→replan vs `7c3a04c8` fatal 短路；`errors.py` + `tool_executor._docker_exec`；Day3 对照 #4573/#4575 · 2026-07-05 |
| M1-K06 | | | | ● | **3** | `416be508` / `6363ddfb`：3 次相同 `docker_exec` → FatalAgentError；`loop_engine._check_fingerprint_loop` · 2026-07-05 |

**M1 平均分**：**2.6** / **≥1 个 3 分**：**是**（K02、K05、K06 = 3）

### 自评说明（简要）

| K 点 | 为何此分 |
|---|---|
| K01 | L2：能从 `state.json` 指读状态机各 phase；未单独设计 FSM 扩展点文档 → 未报 3 |
| K02 | L3：`ErrorClass` enum、`trace.error_class`、observe 行带语义标签均已实现并可演示 |
| K03 | L2：真 replan（plan 变 + 成功）与假 replan（`--pseudo-replan`）均有 runtime 证据；未写独立 policy 表文件 → 未报 3 |
| K05 | L3：`FatalAgentError` + fatal/recoverable/retryable 三分 + A/B 两条 run 对照 #803/#4575 家族 |
| K06 | L3：fingerprint 累计达阈值 fatal，对齐 #4579/#5099；act 前门禁在 `loop_engine.py` |

**L2 最低证据**：

- [x] `cli.py run --task "fix test"` → success + state.json — `TrackARuntime/m1_m2/evidence/5fb33372/state.json`（`success: true`, `round: 2`）
- [x] `cli.py run --simulate-container-death 1` → Fatal + trace — `TrackARuntime/m1_m2/evidence/7c3a04c8/`（history 末行 FatalAgentError；`trace.json` 含 `"error_class": "fatal"`）

**补充证据（Issue 3，非 Exit 必需但支撑 K03/K06）**：

- [x] stuck loop — `m1_m2/evidence/416be508/`
- [x] pseudo-replan — `m1_m2/evidence/6363ddfb/`
