# SOP Case 11：RAG stale index 导致幻觉

> 案例叙事：[case-11](../cases/case-11-rag-stale-index-hallucination.md)  
> **定位**：生产扩展 Case（求职增强）；主练 P2 RAG Eval + M4 检索/生成/引用分层。

## 现象

- Agent 回答带引用，但引用来自旧版本文档。
- 用户反馈答案与最新政策 / 价格 / API 行为不一致。
- 检索看似命中，生成也看似有据，但业务结论错误。

## 根因

1. **KNW**：索引 freshness 缺失，retrieval filter 未按最新有效版本约束。
2. **MET**：eval 只看答案正确率，未拆 retrieval / generation / citation / freshness。
3. **M5**：事故复盘未把 stale index bad case 回流到固定 RAG scenario。

## 系统等价物

缓存读取了旧版本配置，但响应仍带合法来源 ID，导致调用方把 **stale cache** 当成可信数据。

## 故障响应 SOP

| 阶段 | 时间 | 动作 |
|---|---|---|
| 观察 | 5 min | 打开 retrieval trace：chunk id、doc_version、indexed_at、source_updated_at、citation |
| 隔离 | 10 min | 对高风险答案启用 `refuse_if_stale`；临时切人工审核或只返回引用不生成结论 |
| 定位 | 30 min | 区分 ingestion 未跑、索引未刷新、filter 错、rerank 错、citation 不支持 |
| 修复验证 | 1 h | 重建索引；跑 RAG eval；检查 context recall / faithfulness / citation support |
| 复盘 | 全天 | 新增 stale index scenario；更新 index freshness dashboard 与 reindex runbook |

## 监控

| 层 | 指标 |
|---|---|
| Ingestion | `documents_pending_index`、`index_lag_seconds` |
| Retrieval | `retrieved_doc_version`、`stale_chunk_rate` |
| Generation | `citation_support_rate`、`faithfulness_score` |
| Eval | stale-index scenario pass rate、RAG split report |

## 回滚预案

1. 回滚到上一版已知新鲜索引，或强制重建目标 collection。
2. 对 stale collection 启用 refusal / manual review。
3. 修复 filter 与 metadata 后再恢复自动生成。

## 我的项目映射

（填写：文档版本字段、索引刷新路径、retrieval trace、Case 11 eval scenario）
