# M5 Day3 — 对照校准

**日期**：________

> **导师读法**：M5 Day3 不做单一 PR 对照，而是 **跨模块校准**——Case 叙事 + M2/M3 已学 fix + 监控/映射是否一致。Issue 1 对照 M2 Day3 PR #9159 + Case 7 SOP 为完整示范。

## Issue 1（Case 7 ↔ M2 #7355 ↔ PR #9159）

- **对照物**：[M2 Day3 PR #9159 笔记](../module-02/module-02-day3.md) · [sop-case-07](sops/sop-case-07-latency-avalanche.md)
- **M5 SOP 与 M2 机制一致？** **部分一致（tier 同构；SOP 补监控与值班动作）**

  | 维度 | M5 Day2 SOP | M2 Day2/PR #9159 | 判定 |
  | --- | --- | --- | --- |
  | 根因 | 瓶颈错位 + 单一 timeout | 30s 一刀切 + long-running | ✅ 一致 |
  | fix | per-tool tier + resolve | 120s default + 300s heuristic | ✅ 同构 |
  | observe | 定位步查 trace 分 span | Day2 in_flight 语义 | M5 运维化 |
  | 监控 | 工具层 latency P95 | Case 7 分 span | ✅ M5 增值 |
  | PR 缺口 | idle/stalled 上界 | PR 未改 #8448 | ⚠️ 保留 M2 Issue 2 |

- **Day3 学到什么**：
  1. **M2 教 mechanism，M5 教「告警来了先点哪个文件」**——`trace.json` > 猜模型。
  2. PR #9159 验证 tier 方向；值班 SOP 仍需 **TTFT + tool tier 双监控**，防 Case 7 式错位。
  3. 复盘应更新 `monitoring-layers.md` 和 `project-mapping.md`，不是只更新 code。

### Industry PR 归类

| 维度 | 归类 |
| --- | --- |
| **主类** | **SLO**（分 span latency；全局 timeout 错位瓶颈） |
| **次类** | **OBS**（timeout 被当失败 observe；in_flight 语义） |
| **PR 类型** | M2 `fix` PR #9159（tier + unit test）+ M5 **SOP/监控表**（运维翻译层） |
| **同构 Case/OSS** | [Case 07](../case-library/cases/case-07-latency-avalanche.md)；Cline #7355 |
| **归类依据** | 故障首先暴露在 **性能/容量层**——优化 ASR 无效因瓶颈在 LLM/tool span |

### Design 考量

- **前期如何避免**：架构设计阶段画 **全链路 latency budget**（TTFT + per-tool P95 + total）——任一 span 无预算 = 测试集只测 happy path 短命令。Case 7 教训：**监控分层先于优化**，否则 patch 错位。
- **Flowchart 能否避免编码错误**：**能**。`resolve_timeout(tool, payload)` 决策树（Day2/M2）应在写 `ToolExecutor` 时对照——不会写死全局 30s。observe 语义图：timeout → **in_flight** vs **failed** 分支分开。
- **测试策略**：long-running scenario（run_tests >120s）+ unit test 三路径（default / explicit / heuristic）——PR #9159 已示范。
- **M5 增值**：SOP 把 mechanism 翻译成 **5min 观察 → 10min 隔离** 动作；`monitoring-layers.md` 填 **工具层 per-tool latencyMs P95** + **模型层 TTFT**。

## Issue 2（Case 2 ↔ M3 harness · 完整对照）

- **对照物**：M3 Day3 harness-report + [`sop-case-02`](sops/sop-case-02-prompt-butterfly.md)
- **与 Day2/M3 Day3 一致？** **高度一致（SOP 动作与 harness 字段 1:1 映射）**

  | 维度 | M5 Day2 SOP | M3 harness-report | 判定 |
  | --- | --- | --- | --- |
  | 隔离 | gray→0 或停 promote | `gray_percent: 10` 失败即 rollback | ✅ 一致 |
  | 回滚 | v1 全量 | `action: rollback_to_v1` | ✅ 一致 |
  | 监控 | formality_score | `formality_score: 0.0`；`guardrail_ok: false` | ✅ 一致 |
  | 定位 | v1/v2 yaml diff | v2 changelog + 低 formality_min | ✅ 一致 |
  | 证据 | harness-report.json | 同路径 | ✅ L2 |
  | 复盘 | changelog + eval 风格维 | M3-K02/K04 | ✅ 一致 |

- **Day3 学到什么**：
  1. M3 教 **Harness 机制**；M5 教 **值班第一反应**——formality 断崖 → 查 prompt version + gray，不是换模型。
  2. `project-mapping` Case 2 行：监控 **formality_score**；回滚 **prompts/v1**——与 M3 harness 同证据链。
  3. Case 2 与 Case 7 **对照**：前者 REL（配置发布），后者 SLO（latency）——告警类型不同，打开的文件不同（harness-report vs trace.json）。

> **导师提示**：Issue 2 填空完成后，在 `project-mapping.md` 填 Case 2 行，并与 Case 7 行并列——面试时能秒答「两类 Bad Case 各看什么证据」。

### Industry PR 归类

| 维度 | 归类 |
| --- | --- |
| **主类** | **REL**（Prompt 发布；灰度 + 护栏 + rollback） |
| **次类** | **MET**（满意度单 KPI 无 formality 护栏） |
| **PR 类型** | M3 本地 Harness 证据 + M5 SOP（无单一 OSS fix PR） |
| **同构 Case** | [Case 02](../case-library/cases/case-02-prompt-butterfly.md)；M3 module-03-day3 Issue 2 |
| **归类依据** | 故障首先暴露在 **交付/变更层**——M5 把 M3 mechanism 运维化 |

### Design 考量

- **前期如何避免**：Prompt 变更纳入 **发布 checklist**（changelog + gray + 护栏 KPI）——与 Case 7 的 latency budget 并列，写入 onboarding doc。缺 checklist = 生产测试集不含 rollback 路径。
- **Flowchart 能否避免编码错误**：**能**。M5 SOP 五步与 M3 `run_harness` pipeline 同序——值班 SOP 即 **runtime 设计图的运维视图**；写 harness 代码时对照 SOP，不会漏 `rollback_reason` 字段。
- **测试策略**：`python cli.py harness --prompt v2 --gray-percent 10` 为 smoke；故意破坏三条路径（Day2）作 regression。
- **跨模块**：M2 allowlist（入口）+ M3 formality（出口）+ M4 eval 风格 scenario = 完整 REL 证据链。

---

## 深 Case 速览（Day3 扩展阅读）

| Case | 对照物 | 与 TrackARuntime | Industry 主类 | Design 要点 |
|---|---|---|---|---|
| 3 中间迷失 | LlamaIndex #9371 | replan 读 summary 策略 | **CTX** | context 当稀缺资源路由；长 doc 先索引策略 |
| 6 注入 | Cline PR #10467 | allowlist | **SEC** | 多轮=有状态服务；session reset + least privilege |
| 7 延迟 | 本 Issue 1 | trace latency_ms | **SLO** | 分 span budget；勿全局 timeout |
| 9 配额（扩展） | M1 Issue 4 · [Case 9](../case-library/cases/case-09-token-burn-rate-limit-cascade.md) | state 轮次 + 429 率 | **CTL+SLO** | early fatal 先于 cost_limit；tenant 隔离 |

> **Case 6 与 M2-I02 直连**：完成 allowlist trace 后，在 project-mapping 填 Case 6 行——**同一证据链**。  
> **Case 9 与 M1-I04 直连**：M1 Day3 Issue 4 口述完成后，在 project-mapping 填 Case 9 行——**CTL 证据在 M1 run，SLO 证据在 429 监控**。

---

## 跨模块校准表

| 模块 | 考核句 | Issue 1 关联 | 证据文件 |
|---|---|---|---|
| M2 | Tool + Trace | #7355 tier | trace.json |
| M3 | Harness | Case 2 rollback | harness-report.json |
| M4 | Eval | gate + latency | evaluation-report.md |
| M5 | 值班思维 | Case 7 SOP | monitoring-layers.md |
| M1（扩展） | Agent 闭环 | Case 9 / I04 | state.json + 429 监控 |

## 扩展 · Case 9 校准（Learner 自填）

- **对照物**：M1 [`module-01-day3.md` Issue 4](../module-01/module-01-day3.md) · [SOP Case 9](../case-library/sops/sop-case-09-token-burn-rate-limit-cascade.md)
- **M5 SOP 与 M1 fix 一致？** （Learner 自填）
- **与 Case 7 对照**：Case 7 先看 `trace.json` latency；Case 9 先看 **run 轮次 + 429 率**——告警类型不同，打开的文件不同。

## 校准结论

- [ ] Issue 1 SOP 与 M2 #7355/PR #9159 逻辑一致 → M5-K01/K02 L2
- [ ] monitoring-layers 工具层+模型层已填 → M5-K03 L2
- [ ] project-mapping Case 7 行完成 → M5-K04 L2
- [ ] Issue 2 Case 2 SOP 完成 → M5-K01 L2
- [ ] **M2 Issue 2 Day1–3 已回填** → 跨模块闭环
- [ ] **M1 Issue 4 / Case 9** 可选：project-mapping Case 9 行 + SOP 映射段
- [ ] 需延长 → 指定补哪张表/哪个 Case

**Issue 1 示范判定**：M5 不是重复 M2，而是把 **同样根因** 翻译成 **值班语言 + 监控表**——面试时 M2 讲设计，M5 讲「我怎么处理线上告警」。

**写入 exit 的要点**：

- Bad Case 高级 fix = 监控 + 回滚 + eval，不是换模型。
- Case 7 = #7355 = 分 span + 分 tier——**全链路单一 timeout 必败**。
- Case 2 = M3 harness = **REL 类先看 harness-report**，不是 trace latency。
- 完成 M2 剩余 Issue 的 **最低标准**：Issue 2 Day1 现象 + Day2 allowlist trace 表 + Day3 trace 逐步讲解 5 event。
- 8 Case 浅读：各 1 句系统等价物 + SOP 速读即可；深 Case 2,3,6,7 必须 project-mapping 有行。
