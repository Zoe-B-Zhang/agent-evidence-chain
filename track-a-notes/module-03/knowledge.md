# M3 知识工程点 · Harness

> **生命线**：③ **配置交付** · **模块考核句**：**「我会 Harness」**  
> **体系位置**：[`KNOWLEDGE-SYSTEM.md` §7 M3](../curriculum/00-knowledge-system.md) · **教案**：[`COURSE.md` 第 3 课](../curriculum/01-course.md)  
> 索引：[tutor/README.md](../tutor/README.md) · 评分：[MASTERY-RUBRIC.md](../MASTERY-RUBRIC.md) · Issue：[issues.md](issues.md)

**本模块共 6 个核心 K 点**（M3-K01–K06），另有 3 个生产扩展 K 点（M3-K07–K09）用于求职增强。

> **Issue 标注约定**：平台 stub 等若无 [`issues.md`](issues.md) 练习，用  
> `> **Issue 覆盖**：无对应 Issue — …`  
> 标明。

---

## 速查表

| ID | 知识点 | What 摘要 | Runtime 绑定 | Issue |
|---|---|---|---|---|
| M3-K01 | Harness = 交付层 | Prompt 发布 + 平台 stub | `pipeline.py`；router/token/cost | I02；**平台 stub 无独立 Issue** |
| M3-K02 | Prompt = 代码 | v1/v2 + changelog | `prompts/*.yaml` | I02 |
| M3-K03 | 护栏指标 | SLI vs SLO（formality） | `guardrails.py` | I02 |
| M3-K04 | 回滚 | rollback_to_v1 | `cli.py harness` | I02 |
| M3-K05 | 灰度 / Canary | gray_percent | `pipeline.run_harness()` | I02 |
| M3-K06 | re-ask 上限 | validator 循环熔断 | #1491 概念 | I01 |
| M3-K07 | LLM Gateway（扩展） | provider adapter / streaming / fallback | `model_router` 仅 stub；真实 gateway 未实现 | [Case 10](../case-library/cases/case-10-provider-rate-limit-fallback.md) + [SOP](../case-library/sops/sop-case-10-provider-rate-limit-fallback.md) |
| M3-K08 | Runtime Config Surface（扩展） | model/prompt/retrieval/policy/memory 统一发布 | 设计题 | P1/P2/P3/P4 |
| M3-K09 | Rate Limit & Quota Delivery（扩展） | RPM/TPM/tenant quota 作为护栏 | `rate_limiter` 仅教学 stub | [Case 10](../case-library/cases/case-10-provider-rate-limit-fallback.md) + [SOP](../case-library/sops/sop-case-10-provider-rate-limit-fallback.md) |

**面试 60s**：Harness 不是模型，是 **Prompt 的配置中心 + 金丝雀 + 熔断**；证据在 `harness-report.json` 的 `action: rollback_to_v1`。Router/cost 为 **loop 侧教学 stub**，与 harness 状态不共享。

---

## M3-K01 · Harness = 交付层

### What（是什么）

Harness 是 **AI 行为的交付与可靠性层**——版本化 Prompt、灰度、护栏、回滚——不是 Agent loop 本身。

### Why（为什么必须有）

与 Agent loop 混淆 → 靠 **换模型救火**；全局 Prompt 变更无版本/无灰度 → Case 2 类满意度断崖。

### How（怎么做）

| | Agent loop (M1) | Harness (M3) |
|---|---|---|
| 改什么 | 单 task plan/command | **全局** Prompt/模型配置 |
| 证据 | trace / metrics 单 run | harness-report **配置能否上线** |

**平台 stub（与 harness 并列、接入 loop plan）**：

| 模块 | 作用 | 诚实边界 |
|---|---|---|
| `model_router.py` | 简单/复杂任务 → 模型名 | 关键词启发式 |
| `token_counter.py` | 字符估算 token | 非 tokenizer |
| `cost_monitor.py` | token × 单价记账 | **无超限阻断** |
| `rate_limiter.py` | token bucket | 超限时换 fallback 模型名，非硬拒绝 |

Harness / run 均可写 metrics JSON，**两边不共享状态**。

> **Issue 覆盖**：**model_router / token / cost / rate_limiter — 无对应 Issue**（自行：`run --llm mock` 后读 `metrics-*.json` 的 route/token/cost）。灰度回滚仍走 [M3-I02](issues.md)。

**传统等价**：配置中心 + Git + Feature flag；网关路由 / 配额仪表盘（stub）。

### When wrong（典型故障）

无 Harness → 改一句 system tone 全量上线 → 分布级偏移；把 cost 记账误当成「已有成本熔断」。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能口述 Agent vs Harness 分工；类比配置中心。 |
| **L2** | 能跑 `harness --prompt v2 --gray-percent 10`，解读 `guardrail_ok`、`action`、`rollback_reason`；能指 metrics 中的估算字段。 |
| **L3** | 能设计 **rollout 状态机**：draft → gray → promote / rollback；能设计 cost 硬护栏接 loop。 |

---

## M3-K02 · Prompt = 代码

### What（是什么）

Prompt 变更应像代码一样 **版本化、带 changelog、可 diff**。

### Why（为什么必须有）

「改一句 warm」引发 **输出分布整体偏移**（蝴蝶效应）——代码没 crash，业务指标崩（Case 2）。

### How（怎么做）

| | TrackARuntime |
|---|---|
| 版本文件 | `prompts/v1.yaml`、`v2.yaml` |
| 关键字段 | temperature / system / style_formality_min |
| 加载 | `load_prompt()` |

**与 M1-K03**：replan 改 **command**；Harness 改 **system prompt**——策略变更必须可观测。

### When wrong（典型故障）

无 changelog、无 diff review → 无意引入 hype tone。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能指 v1 vs v2 差异；知各字段管什么。 |
| **L2** | 能讲 v2 changelog → mock 正式度跌破 → rollback。 |
| **L3** | 能设计 **prompt diff CI 门禁**：YAML 变更必须带 changelog。 |

---

## M3-K03 · 护栏指标

### What（是什么）

上线前用 **可量化护栏**（如正式度）代替「感觉还行」——SLI 实测 vs SLO 目标线。

### Why（为什么必须有）

无护栏 → 人工事后发现满意度崩盘；单指标可被 gaming（Case 8 → 需多指标）。

### How（怎么做）

| | 说明 |
|---|---|
| SLI | `formal_tone_score()`：感叹号、hype 词扣分 |
| SLO | `style_formality_min` 阈值 |
| 失败 | `guardrail_ok: false` → rollback |
| 非本护栏 | **成本不在此熔断**（`CostMonitor` 只记账） |

> **Issue 覆盖**：formality 护栏 → [M3-I02](issues.md)。**成本 SLI/硬护栏 — 无对应 Issue**。

### When wrong（典型故障）

v2 mock 输出极端 → `formality_score: 0.0` → 应触发 rollback 而非 promote。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能口述 formality 逻辑与阈值含义。 |
| **L2** | 能指 report 中 formality 失败字段；能区分「语气护栏」vs「成本仪表」。 |
| **L3** | 能设计 **多指标 dashboard**：正式度 + 长度 + 敏感词 + 可选 cost。 |

**与 M4-K02**：护栏 = **在线 SLO**；taxonomy = **离线 eval 分类**。

---

## M3-K04 · 回滚

### What（是什么）

灰度失败必须 **自动回滚到已知好版本**（v1）——配置 revert，不是 git revert 代码。

### Why（为什么必须有）

坏 Prompt 全量扩散 → 比 code crash 更难察觉（无异常栈）。

### How（怎么做）

| Level | TrackARuntime |
|---|---|
| L2 | `run_harness()` → `action: rollback_to_v1`、`rollback_reason: guardrail_failed_during_gray` |
| L3 | [`rollout_controller.py`](../../TrackARuntime/m3/rollout_controller.py)、`harness --watch`、[`rollout-auto-rollback.md`](../study-notes/rollout-auto-rollback.md) |

**传统等价**：Blue-green rollback — 切回 Blue（v1）。

### When wrong（典型故障）

gray 失败但未 rollback → 坏配置继续放量。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能口述 `rollback_to_v1` 含义。 |
| **L2** | 能复现 v2 gray 失败 → rollback 报告。 |
| **L3** | 能设计连续 N 次 gray 失败 → lock v2 + eval gate promote。 |

---

## M3-K05 · 灰度 / A/B

### What（是什么）

Prompt 变更应 **小流量验证**（gray_percent），通过护栏后再 promote——Canary release。

### Why（为什么必须有）

大 bang 发布 → Case 2 类全量事故；A/B 需多指标防幸存者偏差（Case 8）。

### How（怎么做）

| | TrackARuntime |
|---|---|
| gray | `gray_percent=10` — mock 简化为单次报告语义 |
| promote L3 | gray OK → 50% → 100%；每步 harness + eval 双门禁 |

**与 M2-K04**：M2 分 **tool timeout tier**；M3 分 **流量 tier**。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能口述 gray_percent 含义；Canary vs Blue-green 区别。 |
| **L2** | 能解释 gray 期间失败如何保护全量。 |
| **L3** | 能设计 **promote 状态机** + 双门禁。 |

---

## M3-K06 · re-ask 上限

### What（是什么）

Validator 失败后的 **re-ask 循环必须有上界与边界安全**——Harness 内循环，非 Agent act 循环。

### Why（为什么必须有）

无界 re-ask = 在线 silent loop；#1491：空 `fail_results` → IndexError（guard 写在 crash **之后**）。

### How（怎么做）

| | 说明 |
|---|---|
| re-ask | 校验失败 → 带错误信息再问 LLM |
| 上界 | max_reasks + counter |
| 边界 | 空 fail_results 安全返回 unchanged |

**与 M1-K06**：M1 fingerprint 抓 **loop 无进展**；M3-K06 抓 **validator re-ask**。

### When wrong（典型故障）

guardrails #1491 → PR #1492 fix 方向。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能口述 re-ask 与 max_reasks。 |
| **L2** | 能对照 #1491 IndexError 根因。 |
| **L3** | 能设计 re-ask counter + 空 fail_results guard。 |

---

## 生产扩展 K 点（求职增强）

> 扩展详解：[`02-production-extension-packs.md` P1](../curriculum/02-production-extension-packs.md#3-p1--llm-gateway--cost--rate-limit)。本节把原有平台 stub 升级为生产 LLM Gateway 的设计语言；不表示 TrackARuntime 已接真实 provider。

### M3-K07 · LLM Gateway

**What**：LLM Gateway 是模型供应商适配与故障隔离层，统一 provider adapter、streaming、structured output、tool calling、fallback。

**Why**：真实 LLM API 不是稳定函数，会出现 429、5xx、timeout、context overflow、invalid JSON、invalid tool call。

**How**：

| 能力 | 设计要点 |
|---|---|
| Provider adapter | OpenAI / Anthropic / local / mock 统一接口 |
| Streaming parser | 半截 JSON、客户端 cancel、partial token |
| Structured output | schema validation、repair retry、fail closed |
| Tool calling | provider schema 差异归一化 |
| Fallback | 按错误类型降级、拒绝或重试 |
| Redaction | request/response/trace 隐藏敏感数据 |

**Prove**：能画 `client → LLM Gateway → provider`，并说明 429、timeout、invalid JSON 分别进入 M1 什么 error_class。

### M3-K08 · Runtime Config Surface

**What**：生产 Agent 的配置面不只有 prompt，还包括 model、retrieval、tool policy、memory policy、rate limit。

**Why**：任一配置变化都可能造成行为分布抖动；只管 prompt 会漏掉 RAG 参数、权限策略、模型路由变化。

**How**：

| 配置 | 应走的门禁 |
|---|---|
| prompt | changelog + harness + eval |
| model route | fallback/cost/latency guard |
| retrieval top_k / threshold | RAG eval split |
| tool policy | SEC scenario + HITL review |
| memory policy | long-context / poisoning scenario |

**Prove**：能写一张配置发布 checklist，说明每类配置走 M3 还是 M4，回滚看哪个证据。

### M3-K09 · Rate Limit & Quota Delivery

**What**：RPM、TPM、并发、tenant quota 是发布护栏，不只是运行时异常。

**Why**：一次 prompt 或 loop 改动可能让 token 使用暴涨，引发 429 雪崩和全线降级。

**How**：

- 发布前用估算 token/cost 做预算。
- 灰度期间监控 429、quota_exhausted、fallback_rate。
- quota 超限时优先降级/限流，不盲目重试。
- M5 SOP 要能止血：降低 gray、暂停候选版本、切 fallback、限制 tenant。

**Prove**：能复盘 [Case 10](../case-library/cases/case-10-provider-rate-limit-fallback.md) / [SOP](../case-library/sops/sop-case-10-provider-rate-limit-fallback.md) 与 [Case 09](../case-library/cases/case-09-token-burn-rate-limit-cascade.md)：空转或配置变更如何导致成本与 rate limit 级联。

---

## K 点 × Issue 对照

| Issue | 主 K 点 | 失败极性 |
|---|---|---|
| guardrails #1491 / M3-I01 | K06, K01 | re-ask **边界 crash** |
| Case 2 + v2 harness / M3-I02 | K02–K05 | Prompt 变更 **无灰度/无护栏** |

| Runtime 能力 | Issue |
|---|---|
| `model_router` / `token_counter` / `cost_monitor` / `rate_limiter` | **无对应 Issue** |
| harness/run `metrics-*.json` | **无对应 Issue** |
| 成本硬熔断 | **无对应 Issue**（未实现） |

---

## M2 → M3 衔接

| M2 已会 | M3 加深 |
|---|---|
| trace 逐步证据 | harness-report **配置变更证据** |
| timeout tier 分桶 | gray_percent **流量分桶** |
| allowlist 防副作用 | 护栏指标防 **语义副作用** |

面试串讲：**「入口拦 rm_rf，出口拦 Amazing!!!」**

---

## 学习记录（自填）

| K 点 | 自评 L | 证据 run / 日期 |
|---|---|---|
| K01 | | |
| K02 | | |
| K03 | | |
| K04 | | harness v2 → rollback |
| K05 | | |
| K06 | | #1491 笔记 |
| K07（扩展） | | LLM Gateway taxonomy |
| K08（扩展） | | Runtime config checklist |
| K09（扩展） | | Rate limit / quota SOP |
