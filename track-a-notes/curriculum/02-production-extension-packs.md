# Track A 生产扩展包 · Agent Development 求职补强

> **定位**：本文件补足 `00-knowledge-system.md` 中 M1–M5 的生产纵深。它不是新主模块，也不替代五条工程生命线；它回答「系统软件工程师要拿 Agent Development 岗位，还要把哪些生产能力挂回 M1–M5」。
>
> **阅读前置**：先读 [`00-knowledge-system.md`](00-knowledge-system.md) §2–§7，再读 [`01-course.md`](01-course.md) 第 1–6 课。

---

## 1. 为什么需要生产扩展包

M1–M5 已覆盖 Agent 系统的工程主干：

```text
M1 控制面   → 会不会停、会不会瞎转
M2 工具边界 → 会不会越权、trace 是否可信
M3 配置交付 → Prompt / 模型配置能否灰度发布
M4 质量门禁 → 行为质量是否可回归
M5 运维响应 → 线上坏了先看哪里、怎么止血
```

但真实 Agent Development 岗位常继续追问：

- 模型供应商 429 / timeout / invalid JSON 怎么处理？
- RAG 检索命中但答案错，怎么定位？
- Agent 读到恶意网页后要调用内部工具，谁拦？
- 1 万个任务同时跑，queue、worker、checkpoint、取消怎么设计？
- 长期记忆被污染，如何回滚？
- LLM-as-Judge 本身不可靠，怎么校准？
- Trace JSON 如何映射到 OpenTelemetry、dashboard、alert？

这些问题不应该拆成新的 M6 工程模块。更好的做法是新增 **Production Extension Packs（P1–P6）**，每个扩展包都映射回 M1–M5。

---

## 2. 扩展包总览

| 扩展包 | 求职追问 | 主归属 | 次归属 | 是否新增模块 |
|---|---|---|---|---|
| **P1 LLM Gateway + Cost + Rate Limit** | 真实模型 API 不稳定怎么办 | M3 | M1/M5 | 否 |
| **P2 RAG + Knowledge System** | 检索错还是生成错 | M4 | M1/M3/M5 | 否 |
| **P3 Security + Tool Sandbox + Privacy** | 模型带权限做错事怎么办 | M2 | M4/M5 | 否 |
| **P4 Runtime Scale + Memory + State** | 多任务、长任务、长期记忆怎么管 | M1 | M2/M4/M5 | 否 |
| **P5 Eval Reliability + Red Team** | Eval / Judge 本身可信么 | M4 | M3/M5 | 否 |
| **P6 Observability + SLO + Portfolio** | 生产环境怎么告警、复盘和展示 | M5 | M2/M3/M4 | 否 |

**结论**：当前不新增 M6 工程模块。M6 仍保留为作品集叙事层。只有当课程升级为完整 Agent 平台课程时，才考虑新增 `M0 Production Substrate`，承载模型、知识、权限、部署基础。

---

## 3. P1 · LLM Gateway + Cost + Rate Limit

### 3.1 并入哪些模块

| 模块 | 并入方式 |
|---|---|
| **M3** | 新增 `M3-K07 LLM Gateway`：provider adapter、streaming、structured output、fallback、rate limit |
| **M1** | Provider timeout / invalid tool call 进入 retryable / recoverable / fatal 分类 |
| **M5** | 新增 provider 监控：429、5xx、fallback_rate、cost_per_request、quota_exhausted |

### 3.2 必学知识

- Provider adapter interface：统一 OpenAI / Anthropic / local / mock 的调用契约。
- Streaming parser：处理半截 JSON、客户端取消、增量 token。
- Structured output validation：JSON mode、schema enforce、repair retry、fail closed。
- Tool calling compatibility：不同 provider 的 tool schema 差异。
- Rate limit：RPM、TPM、并发、tenant quota、backoff、fallback。
- Model fallback：降级模型、拒绝继续、灰度切换。
- Token accounting：prompt、completion、tool observation、memory 分账。
- Redaction：请求、响应、trace 中隐藏 PII / secret。

### 3.3 面试回答模板

> 我不会把 LLM API 当稳定函数用。我会在 M3 放 LLM Gateway，统一 provider adapter、structured output、rate limit 和 fallback；在 M1 把 provider error 映射到 retryable/recoverable/fatal；在 M5 用 429、fallback_rate、cost_per_request 做告警与止血。

### 3.4 建议 Case / Runtime

- [Case 10](../case-library/cases/case-10-provider-rate-limit-fallback.md)：Provider 429 导致 fallback 失败；[SOP 已落地](../case-library/sops/sop-case-10-provider-rate-limit-fallback.md)。
- Runtime 可选：`demo-llm-gateway --failure rate_limit`。
- Evidence：provider error taxonomy、fallback decision、metrics cost/route。

---

## 4. P2 · RAG + Knowledge System

### 4.1 并入哪些模块

| 模块 | 并入方式 |
|---|---|
| **M4** | 新增 `M4-K06 RAG Eval`：retrieval / generation / citation 分层指标 |
| **M1** | observe 增加 retrieval_empty、low_confidence、citation_missing 等 branch 信号 |
| **M3** | top_k、threshold、rerank_enabled 作为配置发布面 |
| **M5** | RAG 事故 SOP：先看检索证据、索引版本、引用支持度 |

### 4.2 必学知识

- Ingestion：解析、清洗、去重、metadata。
- Chunking：固定长度、语义切分、标题层级、代码块保护。
- Embedding versioning：模型升级后的索引重建与效果对比。
- Hybrid search：keyword + vector。
- Rerank：cross-encoder、LLM rerank、规则 rerank。
- Threshold：top-k、score threshold、recall/precision trade-off。
- Citation verification：答案引用是否真的支持结论。
- Index freshness：避免 stale answer。
- Tenant isolation：多租户知识库边界。
- RAG eval：context recall、context precision、faithfulness。

### 4.3 面试回答模板

> 我会把 RAG 错误拆成检索、生成、引用三层，不直接说「embedding 不好」。M4 负责 RAG eval，M3 负责检索参数灰度，M1 observe 负责把 retrieval_empty / low_confidence 变成 replan 信号，M5 用 index version 和 citation 证据做事故定位。

### 4.4 建议 Case / Runtime

- [Case 11](../case-library/cases/case-11-rag-stale-index-hallucination.md)：RAG stale index 导致幻觉；[SOP 已落地](../case-library/sops/sop-case-11-rag-stale-index-hallucination.md)。
- Runtime 可选：`eval-rag --scenario stale-index`。
- Evidence：retrieved chunks、answer faithfulness、citation mismatch。

---

## 5. P3 · Security + Tool Sandbox + Privacy

### 5.1 并入哪些模块

| 模块 | 并入方式 |
|---|---|
| **M2** | 新增 `M2-K06 Policy Engine`、`M2-K07 Indirect Prompt Injection`、`M2-K08 Data Boundary` |
| **M4** | 增加 SEC scenario / red team eval |
| **M5** | 增加 secret leakage、tenant boundary、tool abuse 的事故路径 |

### 5.2 必学知识

- Capability-based permission：模型输出不是授权依据。
- Per-user authorization：同一 tool 对不同用户权限不同。
- Secret handling：secret 不进 prompt、不进可见 trace。
- Tool result provenance：tool output 来自哪里、是否可信。
- Command sandbox：filesystem、network、process、CPU/memory 限制。
- Write tool 分级：read-only、dry-run、write、destructive。
- Approval policy：哪些工具必须 HITL。
- Audit log：可审计、不可被模型伪造。
- Indirect prompt injection：网页/文档/issue 内容诱导 Agent 越权。

### 5.3 面试回答模板

> 我不会让模型决定权限。模型只能提出 tool intent，真正执行前必须经过 M2 policy engine：用户身份、tool capability、side_effect_level、data boundary 和 HITL 策略都在模型外确定性检查。

### 5.4 建议 Case / Runtime

- [Case 12](../case-library/cases/case-12-indirect-prompt-injection-tool-abuse.md)：Indirect Prompt Injection 诱导内部工具调用；[SOP 已落地](../case-library/sops/sop-case-12-indirect-prompt-injection-tool-abuse.md)。
- [Case 17](../case-library/cases/case-17-secret-leakage-through-tool-trace.md)：Secret 泄露进入 trace/provider；[SOP 已落地](../case-library/sops/sop-case-17-secret-leakage-through-tool-trace.md)。
- Runtime 可选：`demo-tool-policy --attack indirect-prompt-injection`。

---

## 6. P4 · Runtime Scale + Memory + State

### 6.1 并入哪些模块

| 模块 | 并入方式 |
|---|---|
| **M1** | 新增 `M1-K07 Runtime Scale`、`M1-K08 Memory Policy`、`M1-K09 Goal Change` |
| **M2** | Memory write 视为有副作用 tool，需要权限和 trace |
| **M4** | 长上下文 / memory poisoning scenario |
| **M5** | queue backlog、worker death、memory rollback SOP |

### 6.2 必学知识

- Job queue、worker pool、task lease。
- Cancellation：用户取消、超时取消、管理员 kill。
- Idempotency：重试不重复副作用。
- Checkpoint persistence：存储、恢复、版本兼容。
- Backpressure：队列积压时限流或拒绝。
- Dead letter queue：无法恢复任务进入人工处理。
- Memory taxonomy：session、long-term、project、user preference。
- Memory write policy：什么允许写、何时写、谁批准。
- Memory versioning / deletion / rollback。
- Memory poisoning：恶意输入污染长期状态。

### 6.3 面试回答模板

> 我会把单次 Agent loop 放进分布式任务系统：queue 接任务、worker 执行、lease 防止 worker 死亡丢任务、checkpoint 支持 resume、idempotency 防重复副作用。长期 memory 是持久状态，不是普通 context，写入要有 policy、provenance 和 rollback。

### 6.4 建议 Case / Runtime

- [Case 13](../case-library/cases/case-13-worker-death-checkpoint-resume.md)：Worker 死亡后 checkpoint resume；[SOP 已落地](../case-library/sops/sop-case-13-worker-death-checkpoint-resume.md)。
- [Case 14](../case-library/cases/case-14-memory-poisoning-version-rollback.md)：Memory poisoning 与版本回滚；[SOP 已落地](../case-library/sops/sop-case-14-memory-poisoning-version-rollback.md)。
- Runtime 可选：`demo-runtime-queue --simulate-worker-death`。

---

## 7. P5 · Eval Reliability + Red Team

### 7.1 并入哪些模块

| 模块 | 并入方式 |
|---|---|
| **M4** | 新增 `M4-K07 Judge Calibration`、`M4-K08 Dataset Lifecycle`、`M4-K09 Security / Red Team Eval` |
| **M3** | Prompt / model / retrieval 变更均需触发对应 eval 子集 |
| **M5** | postmortem 必须记录 bad case 是否进入 eval set |

### 7.2 必学知识

- Dataset construction：线上 bad case、人工构造、对抗样本、分层采样。
- Golden answer policy：谁标、标什么、何时更新。
- LLM-as-Judge calibration：judge 与 human label 一致性。
- Pairwise eval：A/B 两版本比较。
- Confidence interval：小样本波动不能误判回归。
- Statistical significance：退化是否显著。
- Red team eval：注入、越权、泄露、拒答。
- Regression triage：定位 prompt、retrieval、tool、model、memory。

### 7.3 面试回答模板

> Eval 不是只看 pass rate。我会维护 dataset lifecycle，用 human label 校准 judge，用 pairwise eval 比较变更，用 confidence interval 判断小样本波动，并把线上 bad case 回流到固定 scenario。

### 7.4 建议 Case / Runtime

- [Case 15](../case-library/cases/case-15-judge-bias-false-regression.md)：Judge bias 造成误判 regression；[SOP 已落地](../case-library/sops/sop-case-15-judge-bias-false-regression.md)。
- Runtime 可选：judge calibration stub。
- Evidence：human label 对照、judge disagreement、fail closed 策略。

---

## 8. P6 · Observability + SLO + Portfolio

### 8.1 并入哪些模块

| 模块 | 并入方式 |
|---|---|
| **M5** | 新增 `M5-K05 Observability`、`M5-K06 Incident Feedback Loop`、`M5-K07 Cost & Capacity Response` |
| **M2** | `trace.json` 映射到 OTel span |
| **M3** | cost / rate / fallback dashboard |
| **M4** | eval regression dashboard 与发布门禁 |
| **Portfolio** | 架构图、demo script、incident report、eval/safety report |

### 8.2 必学知识

- OTel span model：Agent run、LLM call、tool call、retrieval call。
- Structured logs：run_id、tenant_id、model、tool、phase、error_code。
- Metrics cardinality：避免高基数字段炸 dashboard。
- Dashboard：latency、error、cost、quality、tool failure、retrieval empty。
- Alert rule：何时告警、给谁、如何去重。
- SLO / error budget：成功率、延迟、成本、安全。
- Trace sampling：高流量下如何采样。
- Redaction：日志和 trace 中 PII / secret 处理。
- Incident timeline：告警→止血→修复→复盘。

### 8.3 面试回答模板

> 我会把本地 `trace.json` 看作 OTel span 的教学版本：每个 Agent run、LLM call、tool call、retrieval call 都有 run_id、latency、error_class 和 redaction policy。M5 的 SOP 从 alert 进入 trace，再回流到 M4 eval 和 M3 发布策略。

### 8.4 建议 Case / Runtime

- [Case 16](../case-library/cases/case-16-observability-cardinality-alert-fatigue.md)：高基数 metrics 导致告警失效；[SOP 已落地](../case-library/sops/sop-case-16-observability-cardinality-alert-fatigue.md)。
- [Case 18](../case-library/cases/case-18-approval-fatigue-destructive-action.md)：Approval fatigue 导致危险操作被批准；[SOP 已落地](../case-library/sops/sop-case-18-approval-fatigue-destructive-action.md)。
- Runtime 可选：`demo-observability --export otel-json`。

---

## 9. 新增 K 点索引

| 模块 | 新增 K 点 | 证明方式 |
|---|---|---|
| **M1** | K07 Runtime Scale；K08 Memory Policy；K09 Goal Change | [Case 13](../case-library/cases/case-13-worker-death-checkpoint-resume.md) + [SOP](../case-library/sops/sop-case-13-worker-death-checkpoint-resume.md)；[Case 14](../case-library/cases/case-14-memory-poisoning-version-rollback.md) + [SOP](../case-library/sops/sop-case-14-memory-poisoning-version-rollback.md)；Runtime 可选 |
| **M2** | K06 Policy Engine；K07 Indirect Prompt Injection；K08 Data Boundary；K09 HITL UX | [Case 12](../case-library/cases/case-12-indirect-prompt-injection-tool-abuse.md) + [SOP](../case-library/sops/sop-case-12-indirect-prompt-injection-tool-abuse.md)；[Case 17](../case-library/cases/case-17-secret-leakage-through-tool-trace.md) + [SOP](../case-library/sops/sop-case-17-secret-leakage-through-tool-trace.md)；[Case 18](../case-library/cases/case-18-approval-fatigue-destructive-action.md) + [SOP](../case-library/sops/sop-case-18-approval-fatigue-destructive-action.md)；policy table |
| **M3** | K07 LLM Gateway；K08 Runtime Config Surface；K09 Rate Limit & Quota Delivery | [Case 10](../case-library/cases/case-10-provider-rate-limit-fallback.md) + [SOP](../case-library/sops/sop-case-10-provider-rate-limit-fallback.md)；provider taxonomy |
| **M4** | K06 RAG Eval；K07 Judge Calibration；K08 Dataset Lifecycle；K09 Security / Red Team Eval | [Case 11](../case-library/cases/case-11-rag-stale-index-hallucination.md) + [SOP](../case-library/sops/sop-case-11-rag-stale-index-hallucination.md)；[Case 15](../case-library/cases/case-15-judge-bias-false-regression.md) + [SOP](../case-library/sops/sop-case-15-judge-bias-false-regression.md)；[Case 14](../case-library/cases/case-14-memory-poisoning-version-rollback.md) + [SOP](../case-library/sops/sop-case-14-memory-poisoning-version-rollback.md)；eval report 扩展 |
| **M5** | K05 Observability；K06 Incident Feedback Loop；K07 Cost & Capacity Response | [Case 10](../case-library/cases/case-10-provider-rate-limit-fallback.md) + [SOP](../case-library/sops/sop-case-10-provider-rate-limit-fallback.md)；[Case 13](../case-library/cases/case-13-worker-death-checkpoint-resume.md) + [SOP](../case-library/sops/sop-case-13-worker-death-checkpoint-resume.md)；[Case 16](../case-library/cases/case-16-observability-cardinality-alert-fatigue.md) + [SOP](../case-library/sops/sop-case-16-observability-cardinality-alert-fatigue.md)；[Case 17](../case-library/cases/case-17-secret-leakage-through-tool-trace.md) + [SOP](../case-library/sops/sop-case-17-secret-leakage-through-tool-trace.md)；[Case 18](../case-library/cases/case-18-approval-fatigue-destructive-action.md) + [SOP](../case-library/sops/sop-case-18-approval-fatigue-destructive-action.md)；SOP + dashboard 草图 |

这些新增 K 点属于 **生产扩展 K**，不是原 26 个核心 K 的替代。Exit 可分两层：

- **核心 Exit**：仍按 26 K 点与 TrackARuntime 现有命令考核。
- **求职增强 Exit**：至少能从 P1–P6 中各讲 1 个 Case，并能说明真实生产系统如何扩展。

---

## 10. 推荐学习与实施顺序

1. **P3 Security**：最能体现系统软件工程师优势，先补 policy / sandbox / injection。
2. **P1 LLM Gateway**：真实模型 API 是 Agent runtime 的外部依赖，面试高频。
3. **P2 RAG**：企业 Agent 常见落地场景，补检索与生成分层。
4. **P4 Runtime Scale**：从单 run 过渡到 queue / worker / checkpoint。
5. **P5 Eval Reliability**：把 eval 从「有门禁」提升到「门禁可信」。
6. **P6 Observability**：把本地证据链升级成生产运维叙事。

---

## 11. Capstone 证明要求

完成生产扩展后，应能完成以下 30 分钟面试串讲：

1. **架构**：M1–M5 五条生命线如何包住 Agent 系统。
2. **模型层**：LLM Gateway 如何处理 provider failure、fallback、cost。
3. **知识层**：RAG 失败如何拆 retrieval / generation / citation。
4. **安全层**：工具执行为什么必须 policy engine，而不是相信模型输出。
5. **运行层**：queue / worker / checkpoint / idempotency 如何支撑多任务。
6. **质量层**：eval set、judge calibration、red team 如何防 regression。
7. **运维层**：OTel-style trace、dashboard、alert、SLO 如何进入 SOP。
8. **作品集**：每个 claim 对应代码、命令、证据、Case 或设计文档。

---

## 12. 诚实边界

当前 TrackARuntime 仍是教学型最小验证系统：

- 不接真实 LLM Provider。
- 不含向量数据库或真实 RAG pipeline。
- 不执行真实 shell 副作用。
- `CostMonitor` 只记账，不做硬熔断。
- `trace_eval.py` 有库但未进 runner 主路径。
- M5 无真实告警通道。

生产扩展包的作用是让这些边界变成 **可解释、可规划、可面试的扩展路径**，而不是把未实现能力包装成已上线能力。

---

## 变更记录

| 日期 | 变更 |
|---|---|
| 2026-08-07 | 初版：新增 P1–P6 生产扩展包，映射 M1–M5 与求职增强 Exit |
| 2026-08-08 | Wave 1 Case 10/11/12/15 SOP 已落地，并接入新增 K 点证明方式 |
| 2026-08-08 | Wave 2 Case 13/14/16 SOP 已落地，并接入 P4/P6 与 M1/M4/M5 证明方式 |
| 2026-08-08 | Wave 3 Case 17/18 SOP 已落地；Case 10–18 生产扩展 Case SOP 全部完成 |
