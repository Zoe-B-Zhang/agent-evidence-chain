# Case Library — AI Assistant 工程故障与校准案例库

> **发布版学习材料**：面向「无生产 AI 经验、用系统思维补证据」的学习者。  
> 随 Track A 体系演进 **持续追加** OSS 事故、runtime 证据与面试口述稿。

**新手上路**：先读根目录 [`USAGE.md`](../../USAGE.md)（怎么用）→ [`HOW-TO-ADD-OSS-CALIBRATION.md`](HOW-TO-ADD-OSS-CALIBRATION.md)（如何增补真实 Issue/PR）→ [`BACKLOG.md`](BACKLOG.md)（尚未完成什么）。

## 术语（缩写说明）

| 缩写 / 术语 | 含义 |
|---|---|
| **OSS** | **Open Source Software**（开源软件）。本库 `oss-incidents/` 指 GitHub 上 **真实 Issue / PR 事故**（如 mini-swe-agent #803），与虚构教学 Case 互补。 |
| **Case** | 本库 [`cases/`](cases/) 中编号 1–8 的 **合成/提炼场景**，侧重跨模块口述与 SOP；**Case 09** 已落地为扩展补充；**Case 10–18** 已对齐 [`_TEMPLATE.md`](cases/_TEMPLATE.md)（元数据 / 校准来源 / SOP 摘要 / 学习记录），SOP 已全部落地。 |
| **RAG** | Retrieval-Augmented Generation，检索增强生成。 |
| **A/B** | 对照实验：两版策略/模型/Prompt 分流比较。 |
| **SOP** | Standard Operating Procedure；[`sops/`](sops/) 中的故障演习步骤。 |
| **TrackARuntime** | 本体系最小 Agent 运行时；Case 的 **工程证据** 多指向其 `m1_m2/evidence/`（及 m3/m4 evidence）输出。 |
| **fatal / recoverable / retryable** | Agent 错误语义层级（M1-K05）：substrate 不可恢复 vs 可 in-loop replan vs 单步可重试。 |

---

## 怎么用

> **详细上手**：根目录 [`USAGE.md`](../../USAGE.md) · **待办清单**：[`BACKLOG.md`](BACKLOG.md)

1. **M1–M4**：按模块 GUIDE 做 OSS Issue 三日校准（见 [`METHODOLOGY.md`](METHODOLOGY.md)）。
2. **M5**：深读 4 Case + 浅读 4 Case（见下表「M5 深度」）。
3. **面试**：每个 Case 能口述「现象 → 根因 → 系统等价 → 监控 → 回滚」≤2 分钟。
4. **自填**：每个 Case 文件末尾有「学习记录」；SOP 见 [`sops/`](sops/)。

**阅读顺序建议**：先在本页找到 **类别** → 读该类「举一反三」→ 再打开具体 Case / OSS 文件。

---

## 分类体系

### 分类依据（Primary axis）

按 **故障首先暴露在哪个工程层级** 分类，而不是按产品场景（客服、律所、车载）或按模块编号。

```
用户可见现象
    ↓
[OBS]  observe 是否带正确语义？
[CTL]  控制面是否 enforce 终止 / replan / progress？
[CTX]  上下文 / 多轮状态是否被正确管理？
[KNW]  检索与知识版本是否可信？
[REL]  变更发布是否有灰度与回归？
[SEC]  信任边界是否被突破？
[SLO]  延迟与容量是否可观测、可降级？
[MET]  实验与 eval 是否避免偏差与单一 KPI？
```

同一 Case 可能 **跨类**（表中用「主 / 次」标注）；学习时以 **主类** 定 fix 层级，**次类** 定监控补位。

### 各类别：技术点 · 系统设计 · 问题切入 · 举一反三

#### OBS — Observe 与信号层级

| 维度 | 说明 |
|---|---|
| **技术点** | observation 带 `error_class`；retrieve 质量分数；substrate health；结构化 stderr |
| **系统设计** | 传感器层与业务层分离；fatal 必须在 observe/execute **升维**，不能交给 LLM 自行判断 |
| **问题切入** | 「这条 observation 是 log、recoverable 还是 fatal？」「读数是否带语义层级？」 |
| **举一反三** | 任何 tool 返回都应问：**失败类型** 是否已编码，而非只看 returncode / 自然语言 |

**本类 Case**：Case 03（次：CTX）、oss-803

---

#### CTL — Control 与控制面

| 维度 | 说明 |
|---|---|
| **技术点** | Agent loop 状态机；Exception 短路 vs ErrorObs replan；fingerprint / stuck detector；dispatch 前门禁 |
| **系统设计** | **策略表与执行器一致**：分类定了，controller 必须 enforce；meta 层 override replan policy |
| **问题切入** | 「信号到了，断路器跳了吗？」「replan 后 action 变了吗？」「检测在 dispatch 前还是后？」 |
| **举一反三** | silent loop 三类根因常落在此类或 OBS：**没升维**（#803）· **没 enforce**（#4575）· **无 progress**（#4579/#5099） |

**本类 Case**：oss-4575、oss-4579、oss-5099；Case 06（次：SEC，session reset）；[Case 09](cases/case-09-token-burn-rate-limit-cascade.md)（扩展 · Token 空转，次 SLO）；[Case 13](cases/case-13-worker-death-checkpoint-resume.md)（worker death）

---

#### CTX — Context 与记忆

| 维度 | 说明 |
|---|---|
| **技术点** | context window 分配；摘要树 / 分层检索；多轮 history 压缩；attention 中间弱化 |
| **系统设计** | 把 context 当 **稀缺资源** 路由，而非「窗口够大就全塞」 |
| **问题切入** | 「关键证据在哪个 chunk / 哪一轮？」「是否 observe 到检索不充分再 replan？」 |
| **举一反三** | 长文档、长会话：先问 **索引策略**，再问模型大小 |

**本类 Case**：Case 03（主）；Case 06（次：多轮污染）；[Case 14](cases/case-14-memory-poisoning-version-rollback.md)（memory poisoning）

---

#### KNW — 检索与知识

| 维度 | 说明 |
|---|---|
| **技术点** | chunk 切分；Top-K 与相似度；置信度门控；文档版本 / 时效标签 |
| **系统设计** | 检索层与生成层 **职责拆分**；缺证据时 **拒答** 优于幻觉补全 |
| **问题切入** | 「答案在库里吗？」「检索分够吗？」「是否召回冲突版本？」 |
| **举一反三** | 具体数字「看似有据」→ 先查 retrieval trace，再查 generation |

**本类 Case**：Case 01、Case 04；[Case 11](cases/case-11-rag-stale-index-hallucination.md)（RAG stale index）

---

#### REL — 交付与变更

| 维度 | 说明 |
|---|---|
| **技术点** | Prompt 版本化；灰度发布；护栏指标；模型/router 回滚；changelog |
| **系统设计** | 把 Prompt / 模型当 **配置发布**，不是「改一行就上生产」 |
| **问题切入** | 「何时改的？有无灰度？回归集覆盖吗？」 |
| **举一反三** | 线上行为漂移：先 diff **配置与模型版本**，再 diff 代码 |

**本类 Case**：Case 02、Case 05；[Case 10](cases/case-10-provider-rate-limit-fallback.md)（provider fallback，次 SLO）

---

#### SEC — 安全与信任边界

| 维度 | 说明 |
|---|---|
| **技术点** | System Prompt 锁定；tool allowlist；输入/输出 classifier；session 边界 |
| **系统设计** | 用户输入 **不可信**；长会话需 detect 漂移并 **reset** |
| **问题切入** | 「攻击面在哪一轮进入？」「tool 是否 least privilege？」 |
| **举一反三** | 多轮 Agent = 有状态服务；等价于会话固定 + 注入防护 |

**本类 Case**：Case 06（主）；[Case 12](cases/case-12-indirect-prompt-injection-tool-abuse.md) / [Case 17](cases/case-17-secret-leakage-through-tool-trace.md) / [Case 18](cases/case-18-approval-fatigue-destructive-action.md)（tool abuse / secret leakage / approval fatigue）

---

#### SLO — 性能与容量

| 维度 | 说明 |
|---|---|
| **技术点** | 分 span latency；TTFT；分工具 timeout；降级路径 |
| **系统设计** | 全链路 SLA = 各段 SLA 之和；瓶颈在 **最慢 span** |
| **问题切入** | 「P95 卡在哪一段？」「是否全局 timeout 掩盖局部慢？」 |
| **举一反三** | 「整体变慢」→ 打开 trace  waterfall，不要先换模型 |

**本类 Case**：Case 07；[Case 09](cases/case-09-token-burn-rate-limit-cascade.md)（扩展 · 429 配额雪崩，次 CTL）；[Case 10](cases/case-10-provider-rate-limit-fallback.md) / [Case 16](cases/case-16-observability-cardinality-alert-fatigue.md)（provider 429 / observability）

---

#### MET — 度量与实验

| 维度 | 说明 |
|---|---|
| **技术点** | 分层随机；护栏 KPI；eval 子集分桶；baseline 门禁 |
| **系统设计** | 实验平台要防 **幸存者偏差**；上线决策看 **多指标** |
| **问题切入** | 「样本是否随机？」「全量后长期指标如何？」 |
| **举一反三** | A/B 赢了的 variant，问 **谁没进实验**（Case 8） |

**本类 Case**：Case 08；Case 02（次：多指标共识）；[Case 15](cases/case-15-judge-bias-false-regression.md) / [Case 16](cases/case-16-observability-cardinality-alert-fatigue.md)（judge bias / metrics cardinality）

---

### 类别 × 模块速查

| 类别 | 主要模块 | 代表 K 点（M1 示例） |
|---|---|---|
| OBS | M1, M4 | K02 |
| CTL | M1 | K03, K05, K06 |
| CTX | M1, M4 | K02, replan |
| KNW | M4 | eval / retrieval |
| REL | M3 | harness |
| SEC | M1, M2 | allowlist, trace |
| SLO | M2 | latency, timeout |
| MET | M3, M4 | eval 门禁 |

---

## 核心 Case（1–8）

> **关于标题**：表中「现象昵称」（如「投降式幻觉」）便于记忆 **用户可见症状**，**不等于** 类别名。准确类别见 **主类** 列；完整分类逻辑见上一节。

| ID | 现象昵称 | **主类** | 模块 | M5 | SOP | TrackARuntime |
|---|---|---|---|---|---|---|
| [case-01](cases/case-01-rag-surrender-hallucination.md) | RAG「投降式幻觉」 | **KNW** | M4 | 浅 | [SOP](sops/sop-case-01-rag-surrender-hallucination.md) | 概念级 |
| [case-02](cases/case-02-prompt-butterfly.md) | Prompt「蝴蝶效应」 | **REL** | M3 | **深** | [SOP](sops/sop-case-02-prompt-butterfly.md) | `cli.py harness` |
| [case-03](cases/case-03-context-lost-in-middle.md) | 上下文「中间迷失」 | **CTX** | M1 | **深** | [SOP](sops/sop-case-03-context-lost-in-middle.md) | replan 策略（文档） |
| [case-04](cases/case-04-data-time-travel.md) | 数据「时间穿越」 | **KNW** | M4 | 浅 | [SOP](sops/sop-case-04-data-time-travel.md) | eval 场景设计 |
| [case-05](cases/case-05-catastrophic-forgetting.md) | 微调「灾难性遗忘」 | **REL** | M3 | 浅 | [SOP](sops/sop-case-05-catastrophic-forgetting.md) | 模型/router 回滚 |
| [case-06](cases/case-06-prompt-injection.md) | 多轮注入「数据毒药」 | **SEC** | M1,M2 | **深** | [SOP](sops/sop-case-06-prompt-injection.md) | allowlist + trace |
| [case-07](cases/case-07-latency-avalanche.md) | 全链路「延迟雪崩」 | **SLO** | M2 | **深** | [SOP](sops/sop-case-07-latency-avalanche.md) | `trace.json` latency |
| [case-08](cases/case-08-ab-survivorship-bias.md) | A/B「幸存者偏差」 | **MET** | M3,M4 | 浅 | [SOP](sops/sop-case-08-ab-survivorship-bias.md) | `cli.py eval` 门禁 |

### 按类别浏览（核心 Case）

| 类别 | Case |
|---|---|
| OBS | （核心 Case 无独占；见 OSS-803，与 Case 03 的 observe 维度关联） |
| CTL | （核心 Case 无独占；见 OSS-4575/4579/5099）· [Case 09](cases/case-09-token-burn-rate-limit-cascade.md) |
| CTX | 03 |
| KNW | 01, 04 |
| REL | 02, 05 |
| SEC | 06 |
| SLO | 07 · [Case 09](cases/case-09-token-burn-rate-limit-cascade.md)（429 次） |
| MET | 08 |

---

## 扩展 Case（Supplement · 9+）

> 补 [`KNOWLEDGE-SYSTEM.md` §3.4](../curriculum/00-knowledge-system.md) 盲区；**M5 浅读 / 面试扩展**，不改变核心 1–8 的深读安排。

| ID | 现象昵称 | **主类** | 次类 | 模块 | M5 | SOP | TrackARuntime / OSS |
|---|---|---|---|---|---|---|---|
| [case-09](cases/case-09-token-burn-rate-limit-cascade.md) | Token 空转「配额雪崩」 | **CTL** | SLO | M1,M5 | 浅 | [SOP](sops/sop-case-09-token-burn-rate-limit-cascade.md) | oss-803 + oss-4579；`cli.py run` 对照 run |
| [case-10](cases/case-10-provider-rate-limit-fallback.md) | Provider 429「fallback 失败」 | **SLO** | REL | M3,M5 | 扩展 | [SOP](sops/sop-case-10-provider-rate-limit-fallback.md) | P1 LLM Gateway；provider taxonomy |
| [case-11](cases/case-11-rag-stale-index-hallucination.md) | RAG「旧索引幻觉」 | **KNW** | MET | M4,M5 | 扩展 | [SOP](sops/sop-case-11-rag-stale-index-hallucination.md) | P2 RAG Eval；citation / freshness |
| [case-12](cases/case-12-indirect-prompt-injection-tool-abuse.md) | 间接注入「越权工具」 | **SEC** | CTL | M2,M4 | 扩展 | [SOP](sops/sop-case-12-indirect-prompt-injection-tool-abuse.md) | P3 Policy Engine |
| [case-13](cases/case-13-worker-death-checkpoint-resume.md) | Worker 死亡「checkpoint resume」 | **CTL** | SLO | M1,M5 | 扩展 | [SOP](sops/sop-case-13-worker-death-checkpoint-resume.md) | P4 Runtime Scale |
| [case-14](cases/case-14-memory-poisoning-version-rollback.md) | Memory「污染与回滚」 | **CTX** | SEC | M1,M4 | 扩展 | [SOP](sops/sop-case-14-memory-poisoning-version-rollback.md) | P4 Memory Policy |
| [case-15](cases/case-15-judge-bias-false-regression.md) | Judge「误判 regression」 | **MET** | REL | M4 | 扩展 | [SOP](sops/sop-case-15-judge-bias-false-regression.md) | P5 Judge Calibration |
| [case-16](cases/case-16-observability-cardinality-alert-fatigue.md) | Observability「高基数告警失效」 | **MET** | SLO | M5 | 扩展 | [SOP](sops/sop-case-16-observability-cardinality-alert-fatigue.md) | P6 Observability |
| [case-17](cases/case-17-secret-leakage-through-tool-trace.md) | Secret「进入 trace/provider」 | **SEC** | SLO | M2,M5 | 扩展 | [SOP](sops/sop-case-17-secret-leakage-through-tool-trace.md) | P3 Data Boundary |
| [case-18](cases/case-18-approval-fatigue-destructive-action.md) | HITL「确认疲劳」 | **SEC** | CTL | M2,M5 | 扩展 | [SOP](sops/sop-case-18-approval-fatigue-destructive-action.md) | P3/P6 HITL UX |

**何时读**：Case 09 在 **M1 Day3 扩展 Issue 4**（三联 silent loop 完成后）→ **M5 Day2** 填监控行 → Exit 前口述；与 Case 7（慢）对照。Case 10–18 在核心 Exit 后配合 [`02-production-extension-packs.md`](../curriculum/02-production-extension-packs.md) 做求职增强，不计入 M5 深读四 Case；已对齐 `_TEMPLATE.md`，SOP 已全部落地（Runtime demo 仍为可选下一阶段）。

---

## OSS 扩展案例（`oss-incidents/`）

> 与 [`module-01/issues.md`](../module-01/issues.md) 绑定的 **开源真实事故**；格式与 `cases/` 相同，多 **Issue / PR / Runtime 命令** 字段。  
> 详见 [`oss-incidents/README.md`](oss-incidents/README.md)。

| ID | 标题 | **主类** | OSS 链接 | TrackARuntime 命令 |
|---|---|---|---|---|
| [oss-803](oss-incidents/oss-803-mini-swe-container-silent-loop.md) | Container 死后 silent loop | **OBS** | [#803](https://github.com/SWE-agent/mini-swe-agent/issues/803) · [PR #807](https://github.com/SWE-agent/mini-swe-agent/pull/807) | `--simulate-container-death 1` |
| [oss-4575](oss-incidents/oss-4575-openhands-errorobs-vs-fatal.md) | Fatal 有类型但 controller 未停 | **CTL** | [PR #4575](https://github.com/All-Hands-AI/OpenHands/pull/4575) · [#4573](https://github.com/OpenHands/OpenHands/pull/4573) | A/B：`fix test` vs container death |
| [oss-4579](oss-incidents/oss-4579-openhands-stuck-loop-fatal.md) | Stuck 检测到仍 dispatch | **CTL** | [PR #4579](https://github.com/OpenHands/OpenHands/pull/4579) | `--always-fail-tests --max-rounds 5` |
| [oss-5099](oss-incidents/oss-5099-langgraph-pseudo-replan-loop.md) | Replan 在走但 args 不变 | **CTL** | [#5099](https://github.com/langchain-ai/langgraph/issues/5099) | 上列 + `--pseudo-replan` |
| [oss-1491](oss-incidents/oss-1491-guardrails-reask-index-crash.md) | Re-ask 空 fail_results crash | **REL** | [#1491](https://github.com/guardrails-ai/guardrails/issues/1491) · [PR #1492](https://github.com/guardrails-ai/guardrails/pull/1492) | 阅读 `harness/guardrails.py` |
| [oss-2643](oss-incidents/oss-2643-deepeval-loop-metric-scaffold.md) | Eval 缺 loop metric | **MET** | [#2643](https://github.com/confident-ai/deepeval/issues/2643) · [PR #2782](https://github.com/confident-ai/deepeval/pull/2782) | `eval/runner.py` stub |
| [oss-929](oss-incidents/oss-929-deepeval-judge-invalid-json.md) | Eval judge 畸形 JSON | **MET** | [#929](https://github.com/confident-ai/deepeval/issues/929) | `python cli.py eval` |
| [oss-9415](oss-incidents/oss-9415-ragflow-retrieval-ok-gen-fail.md) | 检索 OK 答案错 | **KNW** | [#9415](https://github.com/infiniflow/ragflow/issues/9415) | 计划 **S23** `RETRIEVAL_OK_GEN_FAIL`（见 [BACKLOG](BACKLOG.md)）；对照 [Case 11](cases/case-11-rag-stale-index-hallucination.md)（**S21** `STALE_INDEX`） |

### M1 silent loop 三联对照（CTL + OBS）

| 子类型 | OSS | 缺陷层 | 一句话 fix |
|---|---|---|---|
| 传感器错 | oss-803 | OBS | substrate 死 → observe 升维 fatal → raise |
| 断路器没跳 | oss-4575 | CTL | fatal 不进 recoverable 通道 → Exception 短路 |
| 无进展空转 | oss-4579 / oss-5099 | CTL | meta fingerprint → dispatch 前 fatal |

**平台级后果（扩展）**：上述任一子类型若未及时 fatal，单 run 可持续 dispatch LLM → 见 [Case 09](cases/case-09-token-burn-rate-limit-cascade.md)（Token 空转 → 共享 429）。

### 按类别浏览（OSS + 关联核心 Case）

| 类别 | OSS | 关联核心 Case |
|---|---|---|
| **OBS** | oss-803 | Case 03（observe 检索质量） |
| **CTL** | oss-4575, oss-4579, oss-5099 | Case 06（session reset）· [Case 09](cases/case-09-token-burn-rate-limit-cascade.md) |
| **CTX** | — | Case 03, Case 06；oss-9415（次） |
| **KNW** | oss-9415 | Case 01, Case 04 |
| **REL** | oss-1491 | Case 02, Case 05 |
| **SEC** | — | Case 06 |
| **SLO** | — | Case 07 · [Case 09](cases/case-09-token-burn-rate-limit-cascade.md) |
| **MET** | oss-2643, oss-929 | Case 08 |

---

## 其他扩展材料

| 类型 | 目录 | 说明 |
|---|---|---|
| Case SOP | [`sops/`](sops/) | Case 1–9+ 值班 SOP，与 `cases/` 同库（见下节 **SOP 放哪**） |
| 补充材料 | [`supplements/`](supplements/) | 作品集证据标准、M6 System Guardian 蓝图等（非 Case 叙事） |

### SOP 放哪？

| 类型 | 位置 | 原因 |
|---|---|---|
| **全部 Case SOP（1–9+）** | [`sops/`](sops/) | 叙事 + SOP **同库**；M5 Day2 与 `monitoring-layers.md`、`project-mapping.md` 同步填写 |

> 核心 Case 1–8 与扩展 Case 9+ 的 SOP 均在 `case-library/sops/`。

---

## 配套文档

| 文档 | 用途 |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | 三日校准法、认知偏差消除、监控分层 |
| [`supplements/portfolio-evidence-standards.md`](supplements/portfolio-evidence-standards.md) | 什么算「能进终面的项目证据」 |
| [`supplements/system-guardian-blueprint.md`](supplements/system-guardian-blueprint.md) | M6 可选叙事：架构守门 Agent |
| [`../module-05/monitoring-layers.md`](../module-05/monitoring-layers.md) | 监控分层白板（与 Case 映射） |

---

## 如何追加新 Case

1. 确定 **主类**（OBS / CTL / CTX / KNW / REL / SEC / SLO / MET）。
2. 在 `cases/` 或 `oss-incidents/` 新建文件；复制 [`cases/_TEMPLATE.md`](cases/_TEMPLATE.md) 或现有 `oss-*.md`。
3. 元数据表增加 **`主类` / `次类`** 字段（可选，与 README 一致）。
4. 更新 **本 README** 索引表与 [`oss-incidents/README.md`](oss-incidents/README.md)（若适用）。
5. 若有 SOP，在 `case-library/sops/` 增文件并与 `cases/` 互链。

---

## 变更记录

| 日期 | 变更 |
|---|---|
| 2026-07 | 自 `_archive/inference-sources/ds_chat.md` 提炼 Case 1–8；建立 case-library 结构 |
| 2026-07 | `oss-incidents/` 补全 M1 四 Issue（#803、#4575、#4579、#5099） |
| 2026-07 | README 增加八类分类体系、术语表、OSS 归入类别、核心 Case 主类标注 |
| 2026-07 | Case 09 SOP 迁至 `case-library/sops/`；M1/M5 Day1–3 练习接入 |
| 2026-07 | 扩展 Case 09：Token 空转 / 配额雪崩（CTL+SLO）；SOP + KNOWLEDGE-SYSTEM §3.4 落地 |
| 2026-07 | M3–M4 OSS 扩展：oss-1491、oss-2643、oss-929、oss-9415；module-03/04/05 day3 补 Industry PR 归类 + Design 考量 |
