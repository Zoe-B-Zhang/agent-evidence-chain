# 五步 SOP（Incident Response SOP）

> **一句话**：线上 AI 故障值班时，用 **固定时间盒 + 固定动作顺序** 把 panic 变成可复现流程——**先止血、再定位、再验证、最后沉淀**；高级 fix 是改监控/回滚/eval，不是先换模型。  
> **在本体系里**：M2–M4 教 **机制设计**（Day2 开方）；M5 把同一根因翻译成 **值班语言**（本 SOP）。

---

## 1. 要解决什么问题

AI 系统故障常见 **初级反应**：

- 用户说「变慢了」→ 立刻换更大模型
- Prompt 改坏 → 再改一句 tone
- eval 掉了 → 调 temperature

这些动作 **无证据链、无时间盒、无回滚点**，往往错位优化（Case 7：ASR/TTS 打补丁，瓶颈其实在 LLM TTFT）。

**五步 SOP** 来自 [`case-library/METHODOLOGY.md`](../case-library/METHODOLOGY.md) 的「故障演习」与 M5 [`module-05-day2.md`](../module-05/module-05-day2.md) 的 **SOP 时间线**——把 on-call 拆成五段，每段有 **目标、禁止事项、产出物**。

---

## 2. 总览

| 阶段 | 时间盒 | 英文 | 核心目标 | 禁止 |
|---|---|---|---|---|
| **① 观察** | 5 min | Observe | 确认 **现象可复现** + 收集 **第一份证据** | 改生产配置、换模型 |
| **② 隔离** | 10 min | Contain | **缩小爆炸半径**，停止恶化 | 深度 debug、大重构 |
| **③ 定位** | 30 min | Diagnose | 找到 **根因层级**（哪 span / 哪层 / 哪版本） | 未定位就 permanent fix |
| **④ 修复验证** | 1 h | Fix & Verify | 最小 fix + **可重复验证** | 只凭感觉说「好了」 |
| **⑤ 复盘** | 全天 | Postmortem | 监控/eval/文档 **防再发** | 只写「人为失误」 |

**时间盒是下限也是上限**：

- 观察 **超过 5 min 仍无证据** → 先定「缺什么 log/trace」，不要猜。
- 隔离 **10 min 内必须有一个 rollback/feature flag/降级动作**。
- 定位 **30 min 仍不确定** → 升级：拉 design owner，或开 **分 span 对比实验**。
- 修复验证 **1 h 内要有 before/after 证据**（trace、harness-report、eval gate）。
- 复盘 **不必当晚写完**，但 **24h 内** 要更新 monitoring-layers / project-mapping。

---

## 3. 逐步详解

### ① 观察（Observe · 5 min）

**要回答的问题**

1. **谁** 受影响？（全量 / 灰度 10% / 单租户）
2. **什么** 指标异常？（延迟、错误率、满意度、formality、gate_pass）
3. **何时** 开始？（与 prompt 版本、模型路由、发布窗口对齐）
4. **第一份证据在哪？**（打开哪个文件）

**标准动作**

| 故障主类 | 先打开的文件 | 先看字段 |
|---|---|---|
| **SLO**（延迟/timeout） | `m1_m2/evidence/<id>/trace.json` | 按 tool 分 `latency_ms` P95 |
| **REL**（Prompt/发布） | `m3/evidence/harness-report.json` | `prompt_version`, `formality_score`, `action` |
| **CTL/OBS**（loop/hang） | `trace.json` | 重复 tool+args、fingerprint、completion pending |
| **MET**（eval 门禁） | `m4/evidence/evaluation-report.md` | `gate_pass`, `failure_distribution` |
| **KNW**（RAG 答错） | retrieval UI + eval scenario | hit vs faithfulness 是否分裂 |
| **SEC**（注入/越权） | `trace.json` | `fallback_used`, allowlist 拒绝 |

**产出物（5 min 结束时应能口述）**

> 「从 T0 起，灰度 v2 10% 用户 formality_score 断崖；证据：`harness-report.json` 中 `guardrail_ok: false`，`action: rollback_to_v1`。」

**常见错误**

- 没看 trace 就换模型（Case 7）
- 把 harness crash 当 LLM 质量问题（M3 #1491）
- 把 judge 崩了当 task fail（M4 #929）

---

### ② 隔离（Contain · 10 min）

**目标**：在 **不搞清楚根因** 的前提下，让系统 **不再更坏**。

**手段优先级**（从高到低）

1. **回滚配置**：prompt v1、tier 表、gray→0
2. **降级路径**：关联网/重工具、换轻量模型、短答模式
3. **熔断**：ModelAccessRouter circuit open、拒绝新 session
4. **扩容量**：仅当明确是容量问题且已有 autoscaling

**按主类的典型隔离动作**

| 主类 | 隔离动作 | TrackARuntime 示例 |
|---|---|---|
| **SLO** | 慢 tool 升 long-running tier；或临时禁用误杀路径 | `tool_executor._timeouts` |
| **REL** | `gray-percent 0`；全量 v1 | `cli.py harness --prompt v2 --gray-percent 0` |
| **CTL** | 达 fingerprint 阈值 → fatal 停 loop | M1 meta fingerprint |
| **SEC** | 收紧 allowlist；session reset | M2 disallow + trace |
| **MET** | judge fail closed → block promote | `gate_pass: false` 阻止合并 |

**产出物**

- 一条 **已执行的隔离命令或配置变更**（可回滚）
- 告警曲线 **斜率变平** 或错误 **不再扩散** 的截图/时间点

**禁止**

- 10 min 内做 permanent code fix（除非 one-line hotfix 且已有单测）
- 隔离动作 **不可审计**（无 changelog、无 rollback_reason）

---

### ③ 定位（Diagnose · 30 min）

**目标**：把现象映射到 **case-library 主类 + 具体组件**，排除「猜错层」。

**定位漏斗**（自上而下）

```text
用户可见现象
  → 哪一层监控先红？（业务 / 应用 / 工具 / 模型 / 基础设施）
    → 哪 span / 哪版本 / 哪 scenario？
      → 与哪个 OSS Issue / Case 同构？
        → 根因一句话（机制，不是「模型笨」）
```

**分模块定位清单**

| 模块 | 定位问题 | 对照 Issue/Case |
|---|---|---|
| M1 Agent | loop 还是 fatal？replan 有 progress 吗？ | oss-803/4579/5099 |
| M2 Tool | timeout 切太早还是 hang 永不切？ | #7355 vs #8448 |
| M3 Harness | 交付脚本 crash 还是 Prompt 无护栏？ | #1491 vs Case 2 |
| M4 Eval | 被测系统错还是 judge/ metric 错？ | #929 vs #9415 |
| M5 值班 | 打开的文件是否与主类一致？ | monitoring-layers |

**Case 7 vs Case 2 定位对照**（面试高频）

| | Case 7 延迟 | Case 2 蝴蝶 |
|---|---|---|
| 先开文件 | `trace.json` | `harness-report.json` |
| 关键指标 | per-tool `latency_ms` | `formality_score` |
| 根因层 | SLO · tool/model span | REL · prompt 发布 |
| 误杀式 fix | 换 ASR/前端 | 换 LLM 模型 |

**产出物**

- **根因一句话** + **系统等价物**（Day1 格式）
- 标注 **主类/次类**（见 [`case-library/README.md`](../case-library/README.md)）

---

### ④ 修复验证（Fix & Verify · 1 h）

**目标**：**最小 diff** 修复 + **可重复** 的 before/after 证据。

**Fix 原则**（与 Day2 开方一致）

| 层级 | 优先 fix | 避免 |
|---|---|---|
| 边界 bug | 一行 guard + 单测 | 大重构 |
| timeout | per-tool tier + 纯函数 policy | 全局改成 6000s |
| Prompt 漂移 | 版本化 + 护栏 + gray rollback | 手工改 tone |
| eval 缺口 | taxonomy + scenario + gate | 只加「请认真回答」 |
| loop | fingerprint / loop metric | 盲目提高 max_rounds |

**验证清单**

- [ ] repro 步骤可 **第三方复现**（命令 + 输入）
- [ ] fix 后 **同一 repro 通过**
- [ ] **回归**：相关 scenario / 单测仍绿
- [ ] 证据文件已更新（新 trace、新 harness-report、新 eval report）
- [ ] 若 PR 对照：与 Day2 方案 **逻辑一致** 或记录差距

**TrackARuntime 验证命令示例**

```powershell
cd TrackARuntime
# SLO
python cli.py run --task "fix failing test"
# REL
python cli.py harness --prompt v2 --gray-percent 10
# MET
python cli.py eval
```

**产出物**

- fix PR 或配置 diff（小）
- before/after 证据 **并排** 可展示

---

### ⑤ 复盘（Postmortem · 全天）

**目标**：让同类故障 **更贵、更早、更窄**——不是追责，是 **改系统**。

**复盘四件套**

| 产出 | 写在哪 | 内容 |
|---|---|---|
| **监控补位** | [`monitoring-layers.md`](../module-05/monitoring-layers.md) | 哪层缺指标？阈值？告警动作？ |
| **项目映射** | [`project-mapping.md`](../module-05/project-mapping.md) | 现象 → 红灯 → 证据 → 回滚 |
| **eval/scenario** | `failure_taxonomy.md` / `scenarios.json` | 新 failure code 或 S21 类场景 |
| **SOP 更新** | `case-library/sops/sop-case-*.md` | 本次哪步超时/哪步有效 |

**复盘模板（5 段）**

1. **时间线**：T0 告警 → T+5 观察 → T+15 隔离 → …
2. **根因**：机制层一句话 + 主类
3. **为何未提前发现**：eval 缺 scenario？default 路径无单测？无 gray？
4. **行动项**：监控 / eval / harness / 文档（每项 owner + 截止日期）
5. **与 Case/OSS 对照**：同构哪条，下次第一步打开什么

**禁止**

- 只写「下次注意」无 **系统改动**
- 只 blame 运营改 Prompt 无 **changelog 门禁**

---

## 4. 与 M2–M5 模块的分工

```text
Day1 找茬    →  定位阶段的问题框架（根因猜测 + 系统等价物）
Day2 开方    →  修复验证阶段的 mechanism 表（tier、guard、taxonomy）
Day3 对照 PR →  验证 fix 是否与业界同构
M5 五步 SOP  →  告警来了「先做什么、打开哪个文件」
```

| 模块 | 你学会的设计语言 | M5 SOP 运维翻译 |
|---|---|---|
| M2 | `resolve_timeout(tool)` | 观察：trace 分 span P95 |
| M3 | harness gray + rollback | 隔离：gray→0；证据：harness-report |
| M4 | gate_pass + taxonomy | 复盘：加 scenario / judge health |
| M5 | monitoring-layers | 复盘：填表 + Case 映射行 |

**面试分工**

- **M2–M4 面**：「我会怎么 **设计** tier / harness / eval」
- **M5 面**：「告警来了我 **第一步点哪个文件**、10 min 内如何隔离」

---

## 5. 两个完整 walkthrough

### 5.1 Case 7 · 延迟雪崩（SLO 主类）

| 阶段 | 动作 |
|---|---|
| 观察 5 min | 打开 fail run 的 `trace.json`；算 read_file / run_tests / docker_exec 的 `latency_ms` P95 |
| 隔离 10 min | 对 P95 最高 tool 降级：缓存/短答；长命令切 300s tier |
| 定位 30 min | 确认瓶颈在 **tool tier** 非 loop 总时长；对照 #7355：30s 误杀 |
| 修复验证 1 h | 文档化 `resolve_timeout(tool, payload)`；跑 long test scenario；trace 显示 run_tests 可 >120s |
| 复盘 全天 | monitoring-layers 填 **工具层 per-tool latencyMs** + **模型层 TTFT**；eval 加 latency regression |

详见 [`sops/sop-case-07-latency-avalanche.md`](../case-library/sops/sop-case-07-latency-avalanche.md)。

### 5.2 Case 2 · Prompt 蝴蝶（REL 主类）

| 阶段 | 动作 |
|---|---|
| 观察 5 min | 对比 `prompts/v1.yaml` vs `v2.yaml`；读 harness-report `formality_score: 0.0` |
| 隔离 10 min | `gray-percent 0` 或停 v2 promote；全量 v1 |
| 定位 30 min | 根因=**语义分布偏移**，非换模型；v2 降 formality_min 仍挡不住 mock 极端文案 |
| 修复验证 1 h | `python cli.py harness --prompt v2 --gray-percent 10` 仍应 `rollback_to_v1`；故意破坏实验三条路径 |
| 复盘 全天 | Prompt RFC：changelog + gray + 护栏 KPI；eval 加风格维度 scenario |

详见 [`sops/sop-case-02-prompt-butterfly.md`](../case-library/sops/sop-case-02-prompt-butterfly.md)。

---

## 6. 与三日校准法的关系

| 三日校准 | 五步 SOP |
|---|---|
| Day1 现象 + 根因猜测 | 定位阶段输入 |
| Day2 mechanism 表 | 修复验证阶段设计稿 |
| Day3 PR 对照 | 修复验证「与业界一致？」 |
| Case 库裸测第三步 | **整段 SOP 计时演习**（可只写时间线） |

Learner 可先 **纸上跑 SOP**（不写代码），再填 `module-05-day2` 的空白表——与导师 Case 7 示范同结构。

---

## 7. 口述模板

### 7.1 30 秒版（面试：「线上 AI 变慢你怎么查？」）

> 我先 **5 分钟看证据**：打开最近 fail 的 trace，按 tool 看 latency P95，不会先换模型。 **10 分钟隔离**：对最慢 span 降级或调 tier，缩小影响面。 **30 分钟定位**：确认是 SLO 层 tool 误杀还是模型 TTFT，对照我们 Case 7。 **1 小时**做最小 fix 并用同一 repro 验证。 **复盘**更新监控分层和 eval regression，避免下次再错位优化。

### 7.2 2 分钟版（含 REL 与 SLO 对比）

> SOP 五步时间盒：观察、隔离、定位、修复验证、复盘。关键不是背步骤，是 **每步有产出物**。SLO 类先 trace 分 span；REL 类先 harness-report 看版本和护栏。高级 fix 是监控、回滚、eval 门禁，不是换模型。M2 我设计 tier 函数；M5 我告警来了先点 trace.json 哪几个字段——设计和值班是同一根因两种语言。

---

## 8. 常见混淆

| 混淆 | 澄清 |
|---|---|
| 隔离 vs 修复 | 隔离=止血（可回滚配置）；修复=改机制（PR） |
| 观察 vs 定位 | 观察=收集现象+证据；定位=解释机制+主类 |
| M5 SOP vs M2 Day2 | 同 fix；M2 写函数，M5 写值班动作表 |
| 复盘 vs Day3 | Day3=与 OSS PR 对照认知；复盘=改监控/eval 防再发 |
| 换模型 | 通常是 **观察/定位阶段禁止项** |

---

## 9. 学习记录（自填）

- **第一次完整纸面演习 Case**：
- **哪一步最容易超时**（观察/隔离/定位/验证/复盘）：
- **自己项目的第一步证据文件**：

---

## 参考

- [case-library/METHODOLOGY.md](../case-library/METHODOLOGY.md) — 故障演习第三步
- [module-05/module-05-day2.md](../module-05/module-05-day2.md) — Case 7 示范时间线
- [module-05/module-05-day3.md](../module-05/module-05-day3.md) — M2 mechanism ↔ M5 运维对照
- [module-05/monitoring-layers.md](../module-05/monitoring-layers.md) — 复盘填表
- [case-library/sops/](../case-library/sops/) — 各 Case 故障响应 SOP
