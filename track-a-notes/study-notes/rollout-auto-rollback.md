# 自动 Rollback 控制器（Rollout Auto-Rollback）

> **一句话**：Prompt/配置/模型路由的 **灰度发布** 不能只靠单次「感觉不行」——需要 **持久化状态机**：护栏 fail → 立刻切回 stable；连续 N 次 fail → **锁 candidate**；全量 promote 前还要 **eval gate**。  
> **在本体系里**：M3-K04 **L3** 设计题；L2 的 `run_harness()` 只做 **单次决策**，L3 的 `rollout_controller.py` + `harness --watch` 做 **跨 tick 控制器**。

---

## 1. 要解决什么问题

**L2（单次 harness）** 能在一份 `harness-report.json` 里写出 `action: rollback_to_v1`，但：

- 不会 **累计** 连续失败次数
- 不会 **锁定** 坏版本，防止运维反复推 v2
- 不会在 promote 前强制 **eval gate_pass**
- 没有 **traffic_log / alerts** 审计链

**L3** 要设计的是 **发布控制器**（与 Prompt 正式度等业务解耦），类比：

- 配置中心金丝雀 + 自动回滚脚本
- 特性开关：gray → promote / rollback
- 蓝绿发布中的 **fail-closed 熔断**

---

## 2. L3 设计要考虑哪些方面（与业务无关）

| 维度 | 要问什么 | 产出物 |
|---|---|---|
| **状态机** | 有哪些 phase？合法迁移？ | `stable → gray → promoted` 或 `→ locked` |
| **双版本** | 谁是 stable（已知好）？谁是 candidate（待验）？ | `active_version` / `candidate_version` |
| **护栏插件** | 每 tick 如何判断 pass/fail？ | 注入 `guardrail_check(candidate, gray) → {ok, …}` |
| **失败计数** | 单次 fail 就锁，还是连续 N 次？ | `fail_streak` + `fail_streak_limit`（防抖动） |
| **回滚动作** | fail 后 **立刻** 做什么？ | `apply_traffic(stable, gray=0)` |
| **锁定** | streak ≥ N 后如何防再推？ | `version_locked` + `locked_versions[]` |
| **Promote 门禁** | gray OK 是否等于全量？ | 还要 `eval_gate().gate_pass`（或 CI gate） |
| **持久化** | 进程重启后状态是否保留？ | `rollout-state.json` |
| **审计** | 谁、何时、为何 rollback？ | `alerts[]`、`traffic_log[]`、`history[]` |
| **告警** | 如何通知值班？ | 抽象 `alert(msg, payload)`（可 stub） |
| **幂等 / 重放** | demo 或演练如何重来？ | `--reset-rollout` |
| **与 L2 关系** | 单次 report 放哪？ | 每 tick 仍写 `harness-report.json` |

**原则**：业务只通过 **可替换函数** 进入控制器——正式度、长度、敏感词都是 `guardrail_check` 的一种实现；控制器本身不依赖 Case 2 文案。

---

## 3. 状态机（phase）

```text
                    guardrail OK + eval gate
         ┌────────────────────────────────────── promote
         │                                              │
         v                                              v
     [stable] ──gray tick OK──> [gray] ─────────────> [promoted]
         ^                         │
         │                         │ guardrail fail (streak < N)
         │                         v
         └──── auto_rollback ─────┘
         
     guardrail fail streak ≥ N  ──>  [locked]  (candidate 禁止再推)
```

| Phase | 含义 |
|---|---|
| **stable** | 全量走 `active_version`（stable）；candidate 未放量或已回滚 |
| **gray** | candidate 通过护栏，canary 流量 = `gray_percent`；stable 仍为 fallback |
| **locked** | candidate 连续 N 次护栏失败，版本被锁 |
| **promoted** | candidate 通过 gray + eval gate，全量切换 |

---

## 4. 通用伪码（业务无关）

### 4.1 状态结构

```text
STATE:
  phase ∈ {stable, gray, locked, promoted}
  active_version          # 当前线上主版本（stable）
  candidate_version       # 本 tick 待验版本
  gray_percent            # canary 流量比例 0–100
  fail_streak             # 连续护栏失败次数
  fail_streak_limit       # 默认 3
  locked_versions[]       # 已锁 candidate 列表
  alerts[]                #  append-only 告警审计
  traffic_log[]           # 每次 apply_traffic 记录
  history[]               # 每 tick 摘要
```

### 4.2 单 tick：`watch_tick(candidate, gray_percent, opts)`

```text
FUNCTION watch_tick(candidate, gray_percent, opts):
  stable ← STATE.active_version

  # --- 0. 前置：已锁则拒绝 ---
  IF candidate IN STATE.locked_versions:
    alert("candidate locked", {candidate})
    RETURN {tick: rejected}

  # --- 1. 护栏检查（插件，与业务解耦）---
  report ← guardrail_check(candidate, gray_percent)

  # --- 2. 失败路径：回滚 + 计数 + 可能锁定 ---
  IF NOT report.ok:
    STATE.fail_streak += 1
    apply_traffic(active=stable, gray=0, reason="auto_rollback")
    alert("guardrail fail", report)
    STATE.phase ← stable

    IF STATE.fail_streak >= STATE.fail_streak_limit:
      lock(candidate)                    # locked_versions += candidate
      STATE.phase ← locked
      alert("candidate locked after streak", {candidate, limit})

    RETURN {tick: rollback, fail_streak: STATE.fail_streak}

  # --- 3. 成功路径：重置 streak，保持 gray ---
  STATE.fail_streak ← 0
  STATE.phase ← gray
  apply_traffic(active=stable, gray=gray_percent, reason="canary_ok")

  # --- 4. 可选：promote（双门禁）---
  IF opts.promote_if_ready:
    IF NOT eval_gate().gate_pass:
      alert("promote blocked: eval gate fail")
      RETURN {tick: gray_ok, promote: blocked}

    apply_traffic(active=candidate, gray=100, reason="promote")
    STATE.phase ← promoted
    alert("promoted", {candidate})
    RETURN {tick: promoted}

  RETURN {tick: gray_ok}
END FUNCTION
```

### 4.3 插件接口（业务注入点）

```text
guardrail_check(version, gray) → { ok: bool, action, reason, metrics... }
eval_gate()                    → { gate_pass: bool, ... }
apply_traffic(active, gray, reason)   # 真实系统：LB / 配置中心 / feature flag
alert(message, payload)               # 真实系统：PagerDuty / Slack
```

---

## 5. L2 vs L3 对照

| | L2 `run_harness()` | L3 `watch_tick()` |
|---|---|---|
| 触发 | 手动跑一次 CLI | 定时/CI 每 tick 调用 `--watch` |
| 决策 | 单次 report 里 `rollback_to_v1` | 立刻 `apply_traffic` + 更新 state |
| 连续失败 | 不累计 | `fail_streak` → lock |
| Promote | 无 | 需 `eval gate_pass` |
| 证据 | `harness-report.json` | + `rollout-state.json` |

**面试一句**：L2 是 **质检报告**；L3 是 **带记忆的发布控制器**。

---

## 6. 在本项目里（TrackARuntime）

| 文件 | 作用 |
|---|---|
| [`rollout_controller.py`](../../TrackARuntime/m3/rollout_controller.py) | 上述伪码的 Python 实现 |
| [`pipeline.py`](../../TrackARuntime/m3/pipeline.py) | L2：`run_harness()` = 默认 `guardrail_check` 插件 |
| [`cli.py`](../../TrackARuntime/cli.py) | `harness --watch` / `--reset-rollout` |

### 命令（M3-K04 L3 证据）

```powershell
cd TrackARuntime

# Case 2：v2 连续 3 次护栏 fail → lock
python cli.py harness --reset-rollout
python cli.py harness --prompt v2 --gray-percent 10 --watch   # fail_streak=1
python cli.py harness --prompt v2 --gray-percent 10 --watch   # fail_streak=2
python cli.py harness --prompt v2 --gray-percent 10 --watch   # fail_streak=3, locked

# promote 路径：v1 gray OK + eval gate
# 默认 --eval-baseline 0.45，与 45.5% 成功率对齐，护栏通过后会 promote
python cli.py harness --reset-rollout
python cli.py harness --prompt v1 --gray-percent 10 --watch --promote-if-ready
```

### 证据文件

- `m3/evidence/rollout-state.json` — phase、fail_streak、locked_versions、traffic_log、alerts
- `m3/evidence/harness-report.json` — 当 tick 护栏快照

当前 `guardrail_check` 接 `run_harness()`（正式度是 M3 **一种** 护栏）；换成长度/敏感词只需换插件，控制器不变。

---

## 7. 与模块 / Case 的关系

| 关联 | 说明 |
|---|---|
| **M3-K04 L3** | 本笔记主对应点 |
| **M3-K03** | 护栏指标 = `guardrail_check` 插件内容 |
| **M3-K05** | `gray_percent` = 流量分桶 |
| **M4 eval** | `eval_gate()` = promote 第二门禁 |
| **Case 2** | v2 蝴蝶效应 → watch 演示 auto rollback |
| **Case 5 / 8** | 配置回滚、多指标共识 |

---

## 8. 口述模板（≤30s）

> 自动 rollback 不是单次 harness 报告里写 rollback，而是 **rollout 状态机**：每 tick 跑 guardrail_check；fail 立刻切回 stable 并累加 fail_streak；连续 N 次 fail 锁 candidate；promote 还要 eval gate。业务通过 guardrail_check / eval_gate 注入；控制器只管 phase、traffic_log 和 alerts。TrackARuntime 用 `harness --watch` 和 `rollout-state.json` 演示。

---

## 9. 学习记录（自填）

- **第一次跑通 `--watch` 三连 lock 日期**：
- **仍易混淆**：L2 report rollback vs L3 apply_traffic？
- **自己的 guardrail_check 插件设想**：

---

## 参考

- [module-03/knowledge.md](../module-03/knowledge.md) — M3-K04 L3
- [module-03/issues.md](../module-03/issues.md) — L3 扩展命令
- [Case 02](../case-library/cases/case-02-prompt-butterfly.md) — REL 类发布问题
- [five-step-incident-sop.md](five-step-incident-sop.md) — 隔离步 = `apply_traffic(stable, 0)`
