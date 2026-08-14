# OSS-9415 — RAGFlow 检索 OK 生成错

| 字段 | 值 |
|---|---|
| **ID** | oss-9415 |
| **主类** | **KNW** |
| **次类** | CTX, MET |
| **标签** | rag, retrieval, generation, inject |
| **关联模块** | M4 |
| **Case 库关联** | [Case 01](../cases/case-01-rag-surrender-hallucination.md)；[Case 03](../cases/case-03-context-lost-in-middle.md)；[Case 11](../cases/case-11-rag-stale-index-hallucination.md) |
| **Issue** | [RAGFlow #9415](https://github.com/infiniflow/ragflow/issues/9415) |
| **对照 PR** | workflow fix（#9238/#9315 类）；根因多在 prompt 注入链 |
| **TrackARuntime** | S11 `RETRIEVAL_MISS`；计划 **S23** `RETRIEVAL_OK_GEN_FAIL`（[BACKLOG](../BACKLOG.md)）；**S21** 已用于 [Case 11](../cases/case-11-rag-stale-index-hallucination.md) `STALE_INDEX` |
| **Day1–3 笔记** | [`module-04/module-04-day1.md`](../../module-04/module-04-day1.md) · [`day3`](../../module-04/module-04-day3.md) |
| **添加日期** | 2026-07 |

## 场景

RAG 聊天：UI 显示已检索到 target chunks，但答案错误/无关。

## 现象

检索面板与答案 **用户可见矛盾**——比纯 E2E fail 更易 debug，但单一 pass rate 会 false green。

## 根因

1. system prompt 缺 `{knowledge}` 或 workflow 未注入 chunks。
2. prompt+chunks 超 context 截断（Case 3 次类）。
3. workflow 改版漏接线。

## 系统等价物

DB 查询返回正确行，但 API handler 没用查询结果拼 response。

## Design 要点（Day3 提炼）

- 数据流图：chunks → inject 点 → LLM → answer；每 inject 点写 assert。
- 拆分 metric：RETRIEVAL_MISS vs RETRIEVAL_OK_GEN_FAIL。
- 线上双指标：retrieval hit + generation faithfulness。
- 扩展到 freshness：[Case 11](../cases/case-11-rag-stale-index-hallucination.md) 把“检索命中”继续拆成 citation support / doc_version / index freshness。

## TrackARuntime 证据

- S11 `RETRIEVAL_MISS` vs **计划 S23** `RETRIEVAL_OK_GEN_FAIL` 成对 scenario（S23 尚未实现，见 [BACKLOG](../BACKLOG.md)）
- **S21** 已绑定 Case 11 的 `STALE_INDEX`（freshness 子类型，与 #9415 的 generation 失败不同）
- eval `failure_distribution` 分列

## 学习记录（自填）

- **Day3 与 Issue 讨论差距**：
- **M4 rubric 自评**：
