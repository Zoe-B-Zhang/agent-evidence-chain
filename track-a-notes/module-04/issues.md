# M4 精选 Issue（第 4 周）

> 索引：[tutor/README.md](../tutor/README.md) · 知识工程点：[knowledge.md](knowledge.md)

## M4-I01 主修 — loop metric 缺口（#2643）

| 项 | 内容 |
|---|---|
| Issue | [DeepEval #2643](https://github.com/confident-ai/deepeval/issues/2643) |
| K 点 | M4-K05, M1-K06 |
| **Runtime 任务** | 阅读 `m4/trace_eval.py` + `tests/test_trace_eval.py`；确认 **`runner.run_eval` 未调用**；在 Day2 笔记写「库有 / 主路径无」 |
| **L2 Pass** | 能说明为何 evaluation-report **没有** trace loop 指标 |
| **L3** | 将 `trace_eval` 接入 `run_eval`（**无独立 Issue 编号**，见 knowledge 标注） |

## M4-I02 主修 — 检索对、答错（#9415）

| 项 | 内容 |
|---|---|
| Issue | [RAGFlow #9415](https://github.com/infiniflow/ragflow/issues/9415) |
| K 点 | M4-K04 |
| **Runtime 任务** | 跑 `eval --baseline auto`，指读 report `category_split`；可选在 `scenarios.json` 增加 **S23** `RETRIEVAL_OK_GEN_FAIL` 场景 |
| **L2 Pass** | 能口述 retrieval vs generation 分桶含义 |

## M4-I03 扩展 — baseline auto + taxonomy remediation

| 项 | 内容 |
|---|---|
| 类型 | Runtime 能力练习 |
| K 点 | M4-K03, M4-K02 |
| **Runtime 任务** | `python cli.py eval --baseline auto` → 读 `baseline_meta`、失败条目的 remediation/taxonomy 建议字段 |
| **L2 Pass** | 能对比 `--baseline 0.45`（CI）与 `auto` 的差异与过拟合风险 |
| **对照** | `.github/workflows/ci.yml` 固定 **0.45**（22 场景） |

## M4-I04 生产扩展 — RAG stale index hallucination

| 项 | 内容 |
|---|---|
| Case | [Case 11](../case-library/cases/case-11-rag-stale-index-hallucination.md) |
| SOP | [sop-case-11](../case-library/sops/sop-case-11-rag-stale-index-hallucination.md) |
| K 点 | M4-K06, M4-K08 |
| **Runtime 任务** | 在 `scenarios.json` 设计 stale-index 场景；报告中拆 retrieval / generation / citation / freshness |
| **L2 Pass** | 能说明“检索命中”不等于“答案可用”；必须验证 doc version 与 citation support |
| **L3 扩展** | 为 `evaluation-report.json` 增加 RAG split 指标与 stale chunk 分类 |

## M4-I05 生产扩展 — Judge bias false regression

| 项 | 内容 |
|---|---|
| Case | [Case 15](../case-library/cases/case-15-judge-bias-false-regression.md) |
| SOP | [sop-case-15](../case-library/sops/sop-case-15-judge-bias-false-regression.md) |
| K 点 | M4-K07, M4-K08 |
| **Runtime 任务** | 设计 calibration set：human label、judge raw output、rubric version、dataset version |
| **L2 Pass** | 能区分真实 regression 与 judge false negative；能解释为什么 gate 需要 confidence / pairwise 证据 |
| **L3 扩展** | 增加 judge-human disagreement 统计与 gate fail-closed 策略 |

## M4-I06 生产扩展 — Memory poisoning red team eval

| 项 | 内容 |
|---|---|
| Case | [Case 14](../case-library/cases/case-14-memory-poisoning-version-rollback.md) |
| SOP | [sop-case-14](../case-library/sops/sop-case-14-memory-poisoning-version-rollback.md) |
| K 点 | M1-K08, M4-K09 |
| **Runtime 任务** | 设计 memory poisoning scenario：恶意输入尝试写长期 memory，期望 deny / quarantine / approval |
| **L2 Pass** | 能解释为什么普通单轮 eval 不覆盖长期状态污染；必须把 memory write 当副作用验证 |
| **L3 扩展** | 将 memory poisoning 加入 SEC red team eval，并记录 rollback evidence |

**Eval 必跑**：`python cli.py eval --baseline auto` → 填 rubric M4 行

> **无对应 Issue**：`golden_dataset` 结构校验、Judge 真轨迹、`trace_eval`→runner 接线（L3）——见 [`knowledge.md`](knowledge.md) 标注。Case 11 / 15 / 14 用于把 RAG Eval、Judge Calibration 与 Security Eval 升级为 Case-backed 生产追问。
