# M4 Day3 — 对照 PR

**日期**：________

> **导师读法**：Day3 对照 PR / 本地 eval 报告。Issue 1 对照 PR #2782 scaffold 为完整示范；Issue 2、3 以 Issue 讨论 + 本地 eval 为对照物。

## Issue 1（#2643 ↔ PR #2782）

- **PR 链接**：[DeepEval PR #2782](https://github.com/confident-ai/deepeval/pull/2782) — `feat: add AgentLoopDetectionMetric scaffold`
- **实际改法摘要**：
  1. 新增 metric **结构/schema/test scaffolding**，非完整 loop 检测逻辑。
  2. 计划 follow-up：repeated tool-call、identical args fingerprint、loop severity scoring、reasoning stagnation。
  3. 动机明确引用 #2643：DeepEval 评 completion/quality，**缺 dedicated loop metric**。
  4. **未实现**：hash(tool, args) 计数与 M1 fingerprint 等价的 deterministic 检测——仍是 open。
- **与我 Day2 一致？** **方向一致（scaffold 阶段；Day2 fingerprint 方案是 follow-up 内容）**

  | 维度 | Day2 方案 | PR #2782 | 判定 |
  | --- | --- | --- | --- |
  | 根因定位 | eval 缺 loop 类 | 同 #2643 | ✅ 一致 |
  | 第一版交付 | stub + taxonomy | scaffold only | ✅ 同阶段 |
  | tool+args hash | Day2 伪代码 | planned follow-up | ⚠️ 待实现 |
  | reasoning 相似度 | Day2 提及 | planned | ⚠️ 待实现 |
  | 与 M1 对齐 | fingerprint 同构 | PR 未绑 M1 | Day2 补充价值 |

- **PR 更优之处**：
  - **产品化路径清晰**：schema → test → trace integration 分步，符合大库贡献规范。
  - 挂在 DeepEval agentic trace API 上，**与 TaskCompletion 等并列**。
- **PR 未覆盖、Day2 应保留的认知**：
  - TrackARuntime M1 **在线 fingerprint 已是 working reference**——面试可说「我们 runtime 先做了，eval metric 应对齐」。
  - M2 trace `latency_ms` 分 span 可辅助 loop 检测（Case 7）——不单靠 args 重复。
- **更新后的认知**：
  - #2643 说明 **过程 eval** 是 Agent 赛道刚需；scaffold PR 证明「先占坑再迭代」。
  - 完成 M2-I02 后：allowlist 拒绝应进 eval scenario，与 loop metric **并列** failure 分布。

### Industry PR 归类

| 维度 | 归类 |
| --- | --- |
| **主类** | **MET**（eval 维度缺口；过程 metric 未产品化） |
| **次类** | **CTL**（loop 是在线控制面 pathology 的离线镜像） |
| **PR 类型** | `feat` scaffold — 占坑 + schema/test，检测逻辑 follow-up |
| **同构 OSS/Case** | [oss-4579](../case-library/oss-incidents/oss-4579-openhands-stuck-loop-fatal.md)、[oss-5099](../case-library/oss-incidents/oss-5099-langgraph-pseudo-replan-loop.md)；M1 fingerprint |
| **归类依据** | 故障首先暴露在 **度量层**——Agent 可能真 loop，但 eval 没传感器发现 |

### Design 考量

- **前期如何避免**：eval taxonomy 设计阶段就列 **过程类 failure code**（LOOP_DETECTED、OBSERVE_STALL），与 outcome 类并列——不能等生产踩坑再加 metric。Day2 flowchart：`trace events → loop_detection() → failure_code → gate_pass`。
- **Flowchart 能否避免编码错误**：**能，针对算法对齐**。在线 M1 `_check_fingerprint_loop()` 与离线 `loop_detection()` 应共用同一 **hash(tool,args) 伪代码**（Day2 已写）——写实现时对照图，避免 online/offline 两套逻辑 drift。
- **测试策略**：scaffold PR 已含 test scaffolding；L3 应加 scenario expect fail（如 **LOOP_DETECTED** 类），用 M1 run `416be508` trace 作 golden file。
- **与 M2 衔接**：#8448 hang 与 loop 是 eval 两类 scenario——前者 `OBSERVE_STALL`，后者 `LOOP_DETECTED`；不能只评 final answer。

## Issue 2（#929 · eval judge 可靠性）

- **对照物**：[DeepEval #929](https://github.com/confident-ai/deepeval/issues/929) 讨论串
- **实际根因摘要**：
  1. JSON 被 max_tokens 截断 → 不完整 JSON。
  2. AzureOpenAI 缺 `model_name` → 框架 assume **不支持 structured output** → 走自由文本解析。
  3. 小模型不遵守 JSON schema → 需 Instructor/outlines/lm-format-enforcer 强制 schema。
- **与 Day2 一致？** **高度一致（EVAL_JUDGE_FAIL 三类根因全覆盖）**

  | 维度 | Day2 方案 | #929 讨论 | 判定 |
  | --- | --- | --- | --- |
  | 根因 | judge 不可靠 | 截断 / model_name / schema | ✅ 一致 |
  | 门禁影响 | gate 不可信 | 全量 invalid JSON → gate 无意义 | ✅ 一致 |
  | fix | structured output + schema enforce | model_name + schema generate + outlines | ✅ 一致 |
  | fail closed | judge fail → block merge | 同：不能 skip judge 报错 | ✅ 一致 |
  | 与 M3 同构 | Harness crash #1491 | eval 自身 crash = 门禁脚本不可信 | ✅ 跨模块 |

- **PR 更优之处**（社区讨论侧）：
  - 根因 **三分法** 清晰——Learner 可按 checklist 排查 judge 失败，不是笼统「换大模型」。
  - Azure 路径 `model_name` 是 **配置契约** 问题，与 Agent tool schema 校验同构（M2-K03）。
- **PR 未覆盖、Day2 应保留的认知**：
  - judge 输出应 **结构化 + 限长 + retry with backoff**——单次畸形 JSON 不应 silent pass。
  - eval 报告应单独列 `EVAL_JUDGE_FAIL` 计数，与 task fail 分开——否则 failure_distribution 误导。
- **更新后的认知**：
  - #929 教 **「门禁自身要可靠」**——类比 M3 #1491：不是被测系统错，是 **质检仪坏了**。
  - gate_pass 前提：judge pass rate 本身也要 baseline（meta-eval，L3）。

> **导师提示**：Issue 2 无单一 merged PR 对照——以 Issue 讨论 + Day2 taxonomy 行为准。Learner 应在 `failure_taxonomy.md` 确认 `EVAL_JUDGE_FAIL` 行已填。

### Industry PR 归类

| 维度 | 归类 |
| --- | --- |
| **主类** | **MET**（eval 门禁 / judge 自身可靠性） |
| **次类** | **REL**（交付层 CI gate 脚本不可信，同 #1491） |
| **PR 类型** | Issue 讨论 + 社区 workaround（structured output 库）——非单一 fix PR |
| **同构 OSS** | [oss-1491](../case-library/oss-incidents/oss-1491-guardrails-reask-index-crash.md)（Harness/eval 脚本 crash）；M3 #1491 |
| **归类依据** | 故障首先暴露在 **度量/门禁层**——被测 Agent 可能正常，但 **gate 结论不可信** |

### Design 考量

- **前期如何避免**：eval pipeline 设计时把 **judge 当一等公民**——单独 health check scenario（expect judge 输出 valid schema）；max_tokens、model_name、schema enforce 写进 **eval 配置契约表**，与 Agent tool schema 同级。
- **Flowchart 能否避免编码错误**：**能**。`judge_llm()` 流程应是：选 model → **structured output 分支** → parse → **fail closed**；缺 `model_name` 的分支应在图上标红「禁止走 free-text parse」——编码时不会漏 Azure 路径。
- **测试策略**：三类根因各一个 unit test——截断 JSON、无 model_name、小模型 schema 违例；任一 fail 则 `gate_pass: false`（不能 skip）。
- **meta-eval（L3）**：定期跑「judge 评 gold 样本」——judge 自身 precision 也要 baseline。

## Issue 3（#9415 · 检索对生成）

- **对照物**：[RAGFlow #9415](https://github.com/infiniflow/ragflow/issues/9415)
- **实际根因摘要**（Dosu / 讨论）：
  1. UI 显示 **已检索到 target chunks**，但 chat 答案错误/无关。
  2. system prompt **缺 `{knowledge}` 变量** 或 workflow 改版未正确注入 chunks。
  3. prompt + chunks **超 context 被截断**，关键 evidence 在 middle 丢失（衔接 Case 3）。
- **与 Day2 一致？** **高度一致（RETRIEVAL_OK_GEN_FAIL 拆分 metric）**

  | 维度 | Day2 方案 | #9415 | 判定 |
  | --- | --- | --- | --- |
  | 拆分 metric | RETRIEVAL_OK_GEN_FAIL | 检索 UI 有、答案错 | ✅ 一致 |
  | 根因 | prompt 缺 {knowledge} / overflow | 同 Dosu 分析 | ✅ 一致 |
  | 与 S11 对比 | RETRIEVAL_MISS vs OK_GEN_FAIL | 检索层对 vs 生成层错 | ✅ 一致 |
  | scenario | **S23** 计划（S21 已用于 STALE_INDEX） | Learner 应添加 S23 expect fail | ⚠️ L3 待实现 |
  | Case 1 关联 | 投降式幻觉 | 有 chunks 仍胡答 = 更隐蔽 | ✅ 次类 KNW |

- **PR 更优之处**（Issue 侧）：
  - **用户可见矛盾**（检索面板 vs 答案）是最好 debug 信号——比纯 end-to-end fail 更易定位层。
  - workflow PR #9238/#9315 说明 **注入链** 是独立组件——改 UI 不等于改 prompt 模板。
- **PR 未覆盖、Day2 应保留的认知**：
  - 仅看 retrieval hit rate 会 **false green**——必须加 generation faithfulness assert（cite chunk id / 关键词覆盖）。
  - eval 应 **分桶报告**：retrieval pass + generation fail 单独计数。
- **更新后的认知**：
  - #9415 = **DB 查对了但 handler 没用结果**——与 S11「没查到」正交，taxonomy 必须两码。
  - M4 教 **拆分 metric**；M3 教 **护栏**——RAG 答案风格/formality 也可作 generation 层护栏（跨模块）。

> **导师提示**：Issue 3 建议在 `scenarios.json` 加 **S23**（`RETRIEVAL_OK_GEN_FAIL`）；跑 `python cli.py eval` 确认 failure_distribution 能区分 RETRIEVAL_MISS vs RETRIEVAL_OK_GEN_FAIL。对照 **S21** `STALE_INDEX`（Case 11）理解 freshness 子类型。

### Industry PR 归类

| 维度 | 归类 |
| --- | --- |
| **主类** | **KNW**（检索与生成职责拆分；注入链断裂） |
| **次类** | **CTX**（context overflow / middle 丢失）；**MET**（单一 E2E pass rate 掩盖） |
| **PR 类型** | Issue + workflow fix PR（#9238/#9315 类）——根因多在 **prompt 模板/注入** 非 embedding |
| **同构 Case** | [Case 01](../case-library/cases/case-01-rag-surrender-hallucination.md)；[Case 03](../case-library/cases/case-03-context-lost-in-middle.md)（overflow 次类） |
| **归类依据** | 故障首先暴露在 **知识链路**——retrieve 成功但 **generate 未消费** evidence |

### Design 考量

- **前期如何避免**：RAG pipeline 设计时画 **数据流图**：chunks → **inject 点**（system/user/template）→ LLM → answer。每个 inject 点写 **assert**（eval：answer 必须含 chunk 关键词或 citation id）。缺 inject 点在图上标为 **单点故障**。
- **Flowchart 能否避免编码错误**：**能，针对 workflow 改版**。新版 workflow 若改节点顺序，对照 flowchart 检查 `{knowledge}` 是否仍绑定——#9415 常是 **改版漏接线** 而非模型能力问题。
- **测试策略**：**S23** expect fail + S11 `RETRIEVAL_MISS` 成对——Learner 应能解释两 scenario 断言差异。eval report 的 failure_distribution 必须 **分列** 两类。
- **监控补位**：线上看 retrieval hit + answer faithfulness **双指标**；仅 hit 高、faithfulness 低 → 告警 generation 层，不是加 embedding。

---

## Issue 对照表

| Issue | PR / 对照物 | 一致？ | 学到什么 |
|---|---|---|---|
| **#2643** loop metric | PR #2782 scaffold | 方向一致 | 过程 eval；与 M1 fingerprint 对齐；MET+CTL |
| **#929** judge JSON | Issue 讨论 | 高度一致 | 门禁自身要可靠；fail closed |
| **#9415** 检索 OK 答错 | Issue + taxonomy | 高度一致 | 拆分 retrieval vs generation；**S23**（计划） |
| **M2-I02** allowlist | trace + GUARDRAIL_BLOCK | 设计一致 | 在线 trace → 离线 scenario |

## 校准结论

- [ ] Issue 1 思路与 #2643/PR #2782 一致 → M4-K05 L2
- [ ] Issue 1 能指 M1 fingerprint 同构证据 run → M1-K06 复习
- [ ] Issue 2 #929 根因与 Day2 EVAL_JUDGE_FAIL 一致 → M4-K03 L2
- [ ] Issue 3 #9415 与 RETRIEVAL_OK_GEN_FAIL 一致 → M4-K04 L2
- [ ] `python cli.py eval` 报告解读完成 → M4-K01/K02 L2
- [ ] 被 PR 打败 → 记录差距，延长 2 天再练

**Issue 1 示范判定**：PR #2782 仅 scaffold；Day2 **fingerprint 伪代码** 是合理 L3 next step——不算被打败。

**写入 GUIDE 或 exit 的要点**：

- Eval = 固定 scenarios + taxonomy + **gate_pass**。
- Loop 类失败必须 **trace metric**（#2643），不能只看 final output。
- #9415 教 **拆分 metric**——检索 hit ≠ 答案对。
- #929 教 **门禁自身要可靠**——类比 M3 #1491 Harness crash。
- **辅导 M2 剩余 Issue**：M2-I02 trace 讲解完成后，在 eval taxonomy 加 `GUARDRAIL_BLOCK` / `OBSERVE_STALL` 两行，形成闭环。
