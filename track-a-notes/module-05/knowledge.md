# M5 知识工程点 · Bad Case 系统思维

> **生命线**：⑤ **运维响应** · **模块考核句**：**「我会值班思维」**  
> **体系位置**：[`KNOWLEDGE-SYSTEM.md` §7 M5](../curriculum/00-knowledge-system.md) · **教案**：[`COURSE.md` 第 5 课](../curriculum/01-course.md)  
> 索引：[tutor/README.md](../tutor/README.md) · Case：[case-library/README.md](../case-library/README.md)

**本模块共 4 个核心 K 点**（M5-K01–K04），另有 3 个生产扩展 K 点（M5-K05–K07）用于求职增强。M5 是 **合成层**——把 M1–M4 证据串成故障响应叙事，不是第六块独立理论。

**深做 Case**：2, 3, 6, 7 · **浅读 Case**：1, 4, 5, 8

> **Issue 标注约定**：M5 以 Case 映射为主；新增 Runtime 证据文件若无独立 Issue，在下方标明。

---

## 速查表

| ID | 知识点 | What 摘要 | 主材料 | Issue / 覆盖 |
|---|---|---|---|---|
| M5-K01 | 五步 SOP | 观察→复盘 固定计时 | `case-library/sops/` | Case 表 |
| M5-K02 | 系统等价物 | AI→分布式语言 | Case 库 + day1 | Case 表 |
| M5-K03 | 监控分层 | 五层指标 + metrics | `monitoring-layers.md` | **metrics 无独立 Issue** |
| M5-K04 | 项目映射 | 现象→回滚 | `project-mapping.md` | Case 表 |
| M5-K05 | Observability（扩展） | trace / metrics / logs / alerts / SLO | OTel span 对照 | [Case 16](../case-library/cases/case-16-observability-cardinality-alert-fatigue.md) + [SOP](../case-library/sops/sop-case-16-observability-cardinality-alert-fatigue.md)；[Case 17](../case-library/cases/case-17-secret-leakage-through-tool-trace.md) + [SOP](../case-library/sops/sop-case-17-secret-leakage-through-tool-trace.md) |
| M5-K06 | Incident Feedback Loop（扩展） | bad case → eval/prompt/policy/runtime | postmortem 设计 | [Case 13](../case-library/cases/case-13-worker-death-checkpoint-resume.md) / [Case 14](../case-library/cases/case-14-memory-poisoning-version-rollback.md) / [Case 16](../case-library/cases/case-16-observability-cardinality-alert-fatigue.md) / [Case 18](../case-library/cases/case-18-approval-fatigue-destructive-action.md) |
| M5-K07 | Cost & Capacity Response（扩展） | 429 / quota / backlog / cost spike | SOP 设计 | [Case 10](../case-library/cases/case-10-provider-rate-limit-fallback.md) + [SOP](../case-library/sops/sop-case-10-provider-rate-limit-fallback.md) |

**面试 60s**：Bad Case 不是换模型，是 **改监控/回滚/实验设计**；证据链 = trace + harness-report + evaluation-report + **metrics-*.json**。

---

## M5-K01 · 五步 SOP

### What（是什么）

AI 故障响应用 **固定五段计时**：观察（5min）→ 隔离（10min）→ 定位（30min）→ 修复验证（1h）→ 复盘（全天）。

### Why（为什么必须有）

无 SOP → panic 式「改 Prompt / 换模型试试」→ 扩大事故、丢失证据。

### How（怎么做）

| 阶段 | 目标 | 应打开的 evidence |
|---|---|---|
| 观察 | 第一份证据 | trace / harness / eval |
| 隔离 | 止血 | rollback、gray→0、降级 |
| 定位 | 根因一句话 | 对应 M1–M4 K 点 |
| 修复验证 | 最小 diff + before/after | Runtime 命令 |
| 复盘 | 更新监控/eval/SOP | mapping 表 |

**Case 7 vs Case 2 第一步**：前者 `trace.json` latency；后者 `harness-report` formality。

深读：[`five-step-incident-sop.md`](../study-notes/five-step-incident-sop.md)

### When wrong（典型故障）

SOP 第一步换模型 → 掩盖根因、无法复盘。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能 **按顺序背出** 五步及建议时长。 |
| **L2** | 能选 Case 7（或 2），写 **带时间戳的模拟值班时间线**。 |
| **L3** | 能针对 TrackARuntime 定制 SOP：定位步必须打开 `trace.json` 分 span P95。 |

---

## M5-K02 · 系统等价物

### What（是什么）

把 AI 术语翻译成 **分布式系统/运维语言**——让非 LLM 背景面试官听懂根因。

### Why（为什么必须有）

纯 AI  jargon → 无法证明 **工程化思维**；跨 Case 模式归纳才能举一反三。

### How（怎么做）

| Case | 系统等价物（1 句） |
|---|---|
| Case 1 | 分布式读半份数据假装完整 |
| Case 6 | SQL 注入 + 会话污染 |
| Case 7 | 只优化前后端、DB 瓶颈未治理 |
| Case 8 | 未分层随机实验 |

**跨模块模式**：#7355 切太早 vs #8448 永不切 = timeout 两极（M2-K05）；Case 2 vs #1491 = 无护栏 vs Harness crash。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 每深 Case 能讲 **1 句** 系统等价物。 |
| **L2** | 能在白板画 **Case → 系统等价物 → 监控层** 三列。 |
| **L3** | 能归纳 **跨 Case 模式** 并链到 M1–M4 K 点。 |

---

## M5-K03 · 监控分层

### What（是什么）

告警必须 **分层**：业务 → 应用 → 检索/工具 → 模型 → 基础设施。

### Why（为什么必须有）

在错误层打补丁 → Case 7：ASR/TTS 优化无效，瓶颈在 **LLM TTFT / tool tier**。

### How（怎么做）

| 层 | Case 7 示例指标 | TrackARuntime 证据 |
|---|---|---|
| 模型 | TTFT P95 | （mock）`metrics` token/cost 估算 |
| 工具 | per-tool `latency_ms` P95 | `trace.json` |
| 应用 | harness `formality_score` | `harness-report.json` |
| 业务 | 任务成功率 | `evaluation-report` `gate_pass` |
| 成本水位 | cost_per_request | `metrics-*.json`（**只记账，无告警通道**） |

**Runtime 指标**：`trace.json` latency_ms、`harness-report.json` guardrail、evaluation-report gate_pass、`metrics-<run_id>.json`。

> **Issue 覆盖**：**`metrics-*.json` 值班精读 — 无对应 Issue**（建议并入 Case 2/7 演习：观察步多打开 metrics）。**自动告警 / bad-case→scenario 回流 — 无对应 Issue**（且无代码）。

填表：[`monitoring-layers.md`](monitoring-layers.md)

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能画 **五层** mermaid。 |
| **L2** | 能填 **每层 1 指标 + 阈值 + 告警动作**；能指出 metrics 文件路径。 |
| **L3** | 能说明 Case 7 为何 ASR 优化无效；应先亮哪两层；能设计「成本超阈人工停」流程。 |

---

## M5-K04 · 项目映射

### What（是什么）

每个 Case 映射到 **你的主项目**——「若我的系统出现类似现象，看哪里、回滚什么」。

### Why（为什么必须有）

Case 与己项目脱节 → 面试 **无自己的例子**；Track A Exit 要求指向 runtime 证据。

### How（怎么做）

每行四列：**现象 | 监控红灯 | 证据路径 | 回滚动作**

| Case | 模块证据 | 回滚动作示例 |
|---|---|---|
| 2 蝴蝶 | harness-report + metrics | gray→0, rollback_to_v1 |
| 7 延迟 | trace latency_ms + metrics | 调 `_timeouts` tier（设计） |
| 6 注入 | allowlist / schema / HITL | 收紧 allowlist + 拒载率告警 |
| 9 配额 | fingerprint fatal + cost 叙事 | early fatal；**无自动 cost 熔断** |

> **Issue 覆盖**：映射练习走 Case 表 / [`issues.md`](issues.md)。**成本异常→硬停 — 无对应 Issue**（代码仅记账）。

填表：[`project-mapping.md`](project-mapping.md) · Spine：TrackARuntime

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能填 **4 行**（深 Case 2,3,6,7 各 ≥1）。 |
| **L2** | 每行四列完整。 |
| **L3** | 8 Case 全覆盖；Case 7 绑定 `_timeouts` + PR #9159 同构；Case 9 说明「有 metrics 无熔断」。 |

---

## 生产扩展 K 点（求职增强）

> 扩展详解：[`02-production-extension-packs.md` P6](../curriculum/02-production-extension-packs.md#8-p6--observability--slo--portfolio)。核心原则：本地 evidence 是生产观测的教学缩影，不等于已有告警平台。

### M5-K05 · Observability

**What**：把 Agent run、LLM call、tool call、retrieval call 映射为 trace / metrics / logs / alerts / SLO。

**Why**：事故响应不能只靠人工打开 JSON；生产系统需要 dashboard、alert、SLO 和可采样 trace。

**How**：

| 观测对象 | 教学证据 | 生产对照 |
|---|---|---|
| Agent run | `state.json` | workflow span / run log |
| Tool call | `trace.json` | OTel span |
| Token/cost | `metrics-*.json` | cost dashboard |
| Config rollout | `harness-report.json` | release dashboard |
| Eval regression | `evaluation-report` | quality gate dashboard |

**Prove**：能复盘 [Case 16](../case-library/cases/case-16-observability-cardinality-alert-fatigue.md) / [Case 17](../case-library/cases/case-17-secret-leakage-through-tool-trace.md) 与对应 SOP，并把一次 `trace.json` 字段映射为 OTel span：trace_id、span_id、tool、latency、status、error_class、redacted attributes。

### M5-K06 · Incident Feedback Loop

**What**：每次 bad case 复盘后，必须决定回流到 eval、prompt、policy、runtime 还是 SOP。

**Why**：只修当前事故不沉淀，下一次会以同类方式复发。Agent 系统改进依赖 bad case 飞轮。

**How**：

| 根因 | 回流目标 |
|---|---|
| prompt 分布偏移 | M3 prompt changelog / harness guardrail |
| retrieval miss | M4 RAG scenario |
| unsafe tool intent | M2 policy engine / SEC eval |
| loop 无进展 | M1 fingerprint / trace metric |
| judge 误判 | M4 calibration set |
| alert noise | M5 dashboard / threshold |

**Prove**：postmortem 末尾必须有「新增/更新了哪个 scenario、policy、guardrail、SOP」；能用 [Case 13](../case-library/cases/case-13-worker-death-checkpoint-resume.md) / [Case 14](../case-library/cases/case-14-memory-poisoning-version-rollback.md) / [Case 16](../case-library/cases/case-16-observability-cardinality-alert-fatigue.md) / [Case 18](../case-library/cases/case-18-approval-fatigue-destructive-action.md) 说明 runtime、memory、observability、HITL UX 四类事故如何回流。

### M5-K07 · Cost & Capacity Response

**What**：429、quota_exhausted、queue backlog、cost spike 是运维事故，需要固定止血动作。

**Why**：Agent loop / replan / memory / RAG 都可能放大 token 与并发成本；盲目 retry 会造成雪崩。

**How**：

- 观察：429 rate、fallback_rate、cost_per_request、queue_depth、P95 latency。
- 隔离：降低 gray、暂停候选 prompt、限流 tenant、切低成本模型。
- 定位：是 loop 空转、RAG 变长、model route 改变，还是 provider 限额变化。
- 修复：加 hard budget、优化 retrieval、收紧 max_rounds、调整 quota。
- 复盘：新增 cost/capacity scenario 与 alert。

**Prove**：能复盘 [Case 09](../case-library/cases/case-09-token-burn-rate-limit-cascade.md) / [Case 10](../case-library/cases/case-10-provider-rate-limit-fallback.md) 与 [SOP](../case-library/sops/sop-case-10-provider-rate-limit-fallback.md)：从 token burn 到 rate limit cascade 的完整 SOP。

---

## Case × 模块 × Issue 对照（深做 4 例）

| Case | 模块证据 | OSS / Issue | 主 K 点 |
|---|---|---|---|
| 2 蝴蝶 | harness-report | M3 v2 gray | M5-K01/K03/K04 |
| 3 中间迷失 | replan 策略 | LlamaIndex #9371 | M5-K02 |
| 6 注入 | allowlist | Cline PR #10467 | M2-K01, M5-K03 |
| 7 延迟 | trace latency_ms | M2 #7355 | M2-K04/K05, M5-K03 |

---

## M4 → M5 衔接

| M4 已会 | M5 加深 |
|---|---|
| failure taxonomy 离线分类 | SOP 在线响应时间线 |
| gate_pass 门禁 | 告警 + 隔离 + 回滚动作 |
| loop metric 设计 | Case 7 分 span 定位瓶颈 |

**辅导提示**：用 M5 **五步 SOP 模板** 重走 M2 Issue Day1–3，补齐 Learner 自填部分。

---

## 学习记录（自填）

| K 点 | 自评 L | 证据 / 日期 |
|---|---|---|
| K01 | | SOP 时间线 Case ___ |
| K02 | | 白板映射 |
| K03 | | monitoring-layers 填完 |
| K04 | | project-mapping ≥4 行 |
| K05（扩展） | | OTel span 对照 |
| K06（扩展） | | incident → eval/policy 回流 |
| K07（扩展） | | cost/capacity SOP |
