# M4 知识工程点 · Eval

> **生命线**：④ **质量门禁** · **模块考核句**：**「我会 Eval」**  
> **体系位置**：[`KNOWLEDGE-SYSTEM.md` §7 M4](../curriculum/00-knowledge-system.md) · **教案**：[`COURSE.md` 第 4 课](../curriculum/01-course.md)  
> 索引：[tutor/README.md](../tutor/README.md) · 评分：[MASTERY-RUBRIC.md](../MASTERY-RUBRIC.md) · Issue：[issues.md](issues.md)

**本模块共 5 个核心 K 点**（M4-K01–K05），另有 4 个生产扩展 K 点（M4-K06–K09）用于求职增强。

> **Issue 标注约定**：Runtime 能力若在 [`issues.md`](issues.md) **无对应练习**，用  
> `> **Issue 覆盖**：无对应 Issue — …`  
> 标明。

---

## 速查表

| ID | 知识点 | What 摘要 | Runtime 绑定 | Issue |
|---|---|---|---|---|
| M4-K01 | Eval = 固定任务集 | scenarios + `_simulate` | `scenarios.json`（含 `category`/`version`） | 必跑 eval；**golden 校验无独立 Issue** |
| M4-K02 | failure taxonomy | 失败分类 + remediation | `failure_taxonomy.md` → report 建议 | I 扩展；taxonomy 建议见 I03 |
| M4-K03 | 回归门禁 | gate_pass + baseline | `baseline.py`；`--baseline auto` | I03 |
| M4-K04 | 检索 vs 生成 | category_split | report `category_split` | I02 |
| M4-K05 | trace-based metric | `trace_eval` 库 | **未接入** `run_eval` | I01（缺口仍在） |
| M4-K06 | RAG Eval（扩展） | retrieval / generation / citation 分层 | 设计题；Runtime 未实现真实 RAG | [Case 11](../case-library/cases/case-11-rag-stale-index-hallucination.md) + [SOP](../case-library/sops/sop-case-11-rag-stale-index-hallucination.md) |
| M4-K07 | Judge Calibration（扩展） | LLM-as-Judge 与 human label 对齐 | `judge.py` 仅 stub | [Case 15](../case-library/cases/case-15-judge-bias-false-regression.md) + [SOP](../case-library/sops/sop-case-15-judge-bias-false-regression.md) |
| M4-K08 | Dataset Lifecycle（扩展） | 采样、版本、bad case 回流 | 设计题 | [Case 11](../case-library/cases/case-11-rag-stale-index-hallucination.md) + [SOP](../case-library/sops/sop-case-11-rag-stale-index-hallucination.md) / [Case 15](../case-library/cases/case-15-judge-bias-false-regression.md) + [SOP](../case-library/sops/sop-case-15-judge-bias-false-regression.md) |
| M4-K09 | Security / Red Team Eval（扩展） | 注入、越权、泄露、拒答 | SEC scenario 设计 | [Case 12](../case-library/cases/case-12-indirect-prompt-injection-tool-abuse.md) + [SOP](../case-library/sops/sop-case-12-indirect-prompt-injection-tool-abuse.md) / [Case 14](../case-library/cases/case-14-memory-poisoning-version-rollback.md) + [SOP](../case-library/sops/sop-case-14-memory-poisoning-version-rollback.md) / [Case 17](../case-library/cases/case-17-secret-leakage-through-tool-trace.md) |

**面试 60s**：Eval = **集成测试套件 + 错误码分类 + CI 门禁**；当前 golden **不跑真实 LoopEngine**（`_simulate`）；`trace_eval` 有模块但未进报告主路径。

---

## M4-K01 · Eval = 固定任务集

### What（是什么）

Eval 用 **固定、可重复的 scenarios** 测 Agent——SWE-bench 式的 **任务集 + 自动执行**，非手工试几个 prompt。

### Why（为什么必须有）

手工试 → 不可重复、不可回归；无法证明 merge 前 **全任务集** 质量。

### How（怎么做）

| | TrackARuntime |
|---|---|
| scenario 结构 | `{id, task, expect, failure_code?, category?, …}` + 文件 `version` |
| 执行 | `runner._simulate()` 按 `expect` 造结果——**不驱动 `LoopEngine`** |
| 校验 | `golden_dataset.py`（结构检查） |
| 产出 | `evaluation-report.md/.json`：success_rate、Top failure、P95、`category_split` |

**与 M3**：Harness 证 **单次配置变更**；Eval 证 **全任务集回归**。

> **Issue 覆盖**：**`golden_dataset` / scenarios `version` — 无对应 Issue**（读 `m4/golden_dataset.py` + `scenarios.json` 头）。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能口述 scenario 结构与 expect 含义。 |
| **L2** | 能跑 `cli.py eval --baseline auto`，读 report 各字段；能说明「模拟 outcome ≠ 真跑 Agent」。 |
| **L3** | 能设计新 scenario 绑定 failure_code + category。 |

---

## M4-K02 · failure taxonomy

### What（是什么）

失败必须 **分类编码**（taxonomy）——类比 HTTP 5xx 不分子类则无法定向 fix；报告可附 **remediation 建议**（解析 taxonomy 文档）。

### Why（为什么必须有）

仅 pass/fail% → 无法回答「该改检索还是改 plan」；Case 8 提醒分桶统计防幸存者偏差。

### How（怎么做）

| 类（示例） | 检测信号 |
|---|---|
| RETRIEVAL_MISS、PLAN_ERROR、PATCH_INVALID、TEST_ENV、OVER_EDIT、REQ_MISREAD | `failure_taxonomy.md` + runner `failure_code` + `remediation_advice` |

**与 M1-K05**：M1 在线 error_class；M4 离线 failure_code——应可对齐映射。

> **Issue 覆盖**：Top failure 分布 → 随 eval 必跑；**remediation 字段精读 — 见 [M4-I03](issues.md)**。

### When wrong（典型故障）

所有失败归为一类 → 团队争论改 RAG 还是改 plan 无数据支撑。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能列举 6+ 类。 |
| **L2** | 能报一次 eval 的 **Top3 failure** 及对应 remediation（若有）。 |
| **L3** | 能新增 `RETRIEVAL_OK_GEN_FAIL` 等并写入 taxonomy + scenarios。 |

---

## M4-K03 · 回归门禁

### What（是什么）

`gate_pass = success_rate >= baseline` 是 **能否 merge 的客观判据**；baseline 可固定数值或 **`auto`（历史报告校准）**。

### Why（为什么必须有）

merge 靠感觉 → 线上 regression；**eval 系统自身坏了**（#929）→ gate_pass 无意义。

### How（怎么做）

| | TrackARuntime |
|---|---|
| 固定 baseline | `--baseline 0.45`（**CI 当前用法**，见 [`TrackARuntime/README.md`](../../TrackARuntime/README.md)） |
| 自动校准 | `--baseline auto` → `baseline.py` / report `baseline_meta` |
| gate | `runner.run_eval` → `gate_pass` |
| Judge | `judge.py` 默认关闭；开启时轨迹常为空（教学 stub） |

**与 M3-K04**：Harness rollback = **在线**；eval gate = **离线 merge 前**——双门禁。

> **Issue 覆盖**：`--baseline auto` → [M4-I03](issues.md)。

### When wrong（典型故障）

DeepEval #929：eval judge 输出畸形 JSON → 门禁失灵 → **fail closed**。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能口述 baseline 与 gate_pass 含义。 |
| **L2** | 能区分固定 0.5 vs auto；能读 `baseline_meta`；能区分 **真实 regression** vs **eval 坏了**。 |
| **L3** | 能设计 CI：`gate_pass false` → block merge；讨论 CI 是否应改用 `auto`。 |

---

## M4-K04 · 检索 vs 生成

### What（是什么）

RAG/Agent 失败可能是 **检索错** 或 **生成对但没用检索**——须 **拆分 metric**。

### Why（为什么必须有）

#9415：检索到 target chunks 但 LLM 答非所问 → 误判为 embedding/RAG 问题，实为 **注入链/overflow**。

### How（怎么做）

| | 说明 |
|---|---|
| 概念 | retrieval hit ≠ answer correct |
| Runtime | scenarios `category` → report **`category_split`**（retrieval vs generation 等） |
| scenario 扩展 | S11 `RETRIEVAL_MISS`；**S23** 计划 `RETRIEVAL_OK_GEN_FAIL`（I02；S21 已用于 `STALE_INDEX`） |

**与 M2-K02**：trace 逐步讲 tool 链；M4 讲 **eval 断言检索层 vs 生成层**。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能口述 retrieval hit ≠ answer correct。 |
| **L2** | 能指读 report `category_split`；对照 #9415。 |
| **L3** | 能设计 scenario + metric 拆分（I02）。 |

---

## M4-K05 · trace-based metric

### What（是什么）

Agent 可能在 trace 里 **空转 loop** 而 final output 看起来「完成了」——需 **trace-only metric**。

### Why（为什么必须有）

#2643：DeepEval 现有 metric 评 **质量**，缺 **loop 检测**；与 M1 fingerprint **同构**。

### How（怎么做）

| | 说明 |
|---|---|
| 三类 loop 信号 | tool+args 重复、reasoning 停滞、call graph 环 |
| 在线版 | M1 `_check_fingerprint_loop()` → fatal |
| 离线库 | `m4/trace_eval.py` + `tests/test_trace_eval.py` **已存在** |
| 主路径 | **`runner.run_eval` 未 import/调用 `trace_eval`**；Judge 即使 `--enable-judge` 也常传 `trajectory=[]` |

> **Issue 覆盖**：缺口认知 → [M4-I01](issues.md)。**把 `trace_eval` 接到 runner — 无对应 Issue**（L3 作业）。

### When wrong（典型故障）

eval 只看 final output → silent loop 通过门禁；或「有 trace_eval 模块」被误当成「报告已含轨迹指标」。

### Prove（L1 / L2 / L3）

| Level | 你要达到的状态 |
|---|---|
| **L1** | 能口述三类 loop 信号。 |
| **L2** | 能对照 #2643 与 M1-K06；能说明 eval 报告 **为何没有** trace 指标。 |
| **L3** | 能把 `trace_eval` 接入 `run_eval` 并写入 report。 |

---

## 生产扩展 K 点（求职增强）

> 扩展详解：[`02-production-extension-packs.md` P2/P5](../curriculum/02-production-extension-packs.md)。核心原则：Eval 不只是 pass rate，还要证明数据集、Judge 和分层指标可信。

### M4-K06 · RAG Eval

**What**：RAG 评测必须拆成 retrieval、generation、citation 三层。

**Why**：检索命中不代表答案正确；答案正确也不代表引用支持结论。#9415 已说明「chunks 对、答案错」不能简单归因 embedding。

**How**：

| 指标 | 回答的问题 |
|---|---|
| context recall | 应该出现的证据是否被检索到 |
| context precision | 检索内容是否噪声过多 |
| answer correctness | 生成答案是否满足任务 |
| faithfulness | 答案是否被上下文支持 |
| citation support | 引用是否真的支撑结论 |

**Prove**：能给一个坏回答分类：retrieval miss、retrieval ok generation fail、citation mismatch、stale index。

### M4-K07 · Judge Calibration

**What**：LLM-as-Judge 需要与 human label 校准，不能默认可信。

**Why**：#929 类问题说明 eval 系统本身也会坏；judge 偏见、格式错误、小样本波动都会误导 gate。

**How**：

- 固定一批 human-labeled calibration set。
- 比较 judge vs human 的一致率与 disagreement。
- 对高风险维度使用 pairwise eval 或人工复核。
- judge 输出必须 structured，解析失败 fail closed。

**Prove**：能说明 judge disagreement 时如何处理：不直接 promote，先人工抽样和修正 rubric。

### M4-K08 · Eval Dataset Lifecycle

**What**：Eval set 是持续演进资产，需采样、版本、变更审查、bad case 回流。

**Why**：固定数据集会陈旧；只收线上成功样本会有幸存者偏差；随意改 golden answer 会污染 baseline。

**How**：

| 阶段 | 要求 |
|---|---|
| collect | 线上 bad case、人工构造、对抗样本 |
| label | golden answer / failure_code / category |
| version | dataset version + changelog |
| gate | baseline 对齐版本 |
| recycle | postmortem 决定是否入集 |

**Prove**：能把一次 M5 incident 写成 M4 scenario：task、expect、failure_code、category、why added；能用 [Case 11](../case-library/cases/case-11-rag-stale-index-hallucination.md) 说明 `doc_version/index_version` 如何进入 scenario，用 [Case 15](../case-library/cases/case-15-judge-bias-false-regression.md) 说明 rubric / judge version 如何进入 dataset changelog。

### M4-K09 · Security / Red Team Eval

**What**：安全 eval 专测 prompt injection、越权工具、secret 泄露、拒答边界。

**Why**：普通功能 eval 很难覆盖恶意输入；Agent 连接工具后，安全 regression 是发布 blocker。

**How**：

- SEC scenario 固定化：indirect injection、tenant escape、secret exfiltration、unsafe tool call。
- 与 M2 policy engine 联动：预期结果通常是 deny / require approval。
- 与 M5 incident 联动：安全事故进入 red team suite。

**Prove**：能复盘 [Case 12](../case-library/cases/case-12-indirect-prompt-injection-tool-abuse.md) / [Case 14](../case-library/cases/case-14-memory-poisoning-version-rollback.md)，设计红队 scenario，并说明应该由 M2 哪层拦截、M4 如何判定通过。

---

## K 点 × Issue 对照

| Issue | 主 K 点 | 失败极性 / 能力 |
|---|---|---|
| DeepEval #2643 / M4-I01 | K05, M1-K06 | eval **缺 loop 类 metric**（库有、主路径未接） |
| DeepEval #929 | K03 | eval judge **invalid JSON** |
| RAGFlow #9415 / M4-I02 | K04 | **检索 OK、生成 FAIL** 未拆分 |
| M4-I03 baseline auto | K03, K02 | 历史校准 + remediation 精读 |
| M4-I06 / Case 14 | K09, M1-K08 | memory poisoning 进入 red team eval |

| Runtime 能力 | Issue |
|---|---|
| `golden_dataset` / scenarios `version` | **无对应 Issue** |
| `trace_eval` → runner 接线 | **无对应 Issue**（L3） |
| `--enable-judge` 真轨迹 | **无对应 Issue**（且 trajectory 常空） |

---

## M3 → M4 衔接

| M3 已会 | M4 加深 |
|---|---|
| harness 护栏指标 | eval failure taxonomy + remediation |
| rollback_to_v1 | gate_pass false block merge |
| gray 小流量 | 固定 20 scenarios 全量回归（模拟 outcome） |

---

## 学习记录（自填）

| K 点 | 自评 L | 证据 run / 日期 |
|---|---|---|
| K01 | | evaluation-report.md |
| K02 | | Top3 failure + remediation |
| K03 | | gate_pass / baseline_meta |
| K04 | | category_split / #9415 |
| K05 | | trace_eval 未接线说明 |
| K06（扩展） | | RAG eval split |
| K07（扩展） | | Judge calibration |
| K08（扩展） | | Dataset lifecycle |
| K09（扩展） | | SEC / red team scenario |
