# Case 11 — RAG stale index 导致幻觉

| 字段 | 值 |
|---|---|
| **ID** | case-11 |
| **主类** | **KNW** |
| **次类** | MET |
| **标签** | rag, stale-index, citation, freshness, eval |
| **关联模块** | M4 质量门禁、M1 observe、M3 配置 |
| **M5 深度** | 扩展（求职增强） |
| **SOP** | [sop-case-11](../sops/sop-case-11-rag-stale-index-hallucination.md) |
| **TrackARuntime** | `python cli.py eval --baseline auto` 含 **S21 stale-index** 场景（`m4/scenarios.json`） |
| **OSS 对照** | [oss-9415](../oss-incidents/oss-9415-ragflow-retrieval-ok-gen-fail.md) |
| **添加日期** | 2026-08-08 |
| **来源** | 合成生产事故 + oss-9415 检索/生成拆分思路扩展 |
| **当前状态** | 正式草稿（SOP 已落地；Runtime 可选） |
| **补强 K 点** | M4-K06 RAG Eval；M4-K08 Dataset Lifecycle |
| **目标扩展包** | P2 RAG + Knowledge System |

## 场景

企业文档助手回答了一个已经过期的价格/政策。用户看到回答带引用，但引用来自旧版本文档；新文档已经上传，但索引未刷新或 retrieval filter 未按版本选择。

## 现象

1. 回答带引用，但引用来自旧版本文档。
2. 用户反馈与最新政策 / 价格 / API 行为不一致。
3. 检索看似命中、生成看似有据，业务结论仍错误。

## 根因（非表面）

不是“模型幻觉”这么简单，而是 **知识索引 freshness 与 citation verification 缺失**。检索层召回了旧证据，生成层基于旧证据给出看似可信答案。

## 缺失的工程 invariant

RAG 答案必须绑定 **文档版本、索引版本和引用支持度**；retrieval hit 不等于 answer correct。

## 工程解法

- 文档 ingestion 记录 `doc_version`、`indexed_at`、`source_updated_at`。
- retrieval filter 默认选最新有效版本。
- Eval 拆 retrieval / generation / citation。
- citation verifier 检查答案 claim 是否被引用段支持。
- stale index 进入 KNW/MET taxonomy。

## 系统等价物

缓存读取了旧版本配置，但响应仍带合法来源 ID；调用方因此把 stale cache 当成可信事实。

## 初级 vs 高级认知

**初级**：换 embedding、提高 top-k、让模型“引用来源”。

**高级（目标）**：把 RAG 失败拆成 retrieval / generation / citation / freshness 四层；每条 eval scenario 记录 doc_version 与 index_version。

## 对应 Issue / PR / 校准来源

| 来源 | 链接 | 现象 | 修复点 | 可抽象的工程规则 |
|---|---|---|---|---|
| OSS Issue | [oss-9415](../oss-incidents/oss-9415-ragflow-retrieval-ok-gen-fail.md) | 检索看似正确但生成仍失败 | 拆 retrieval 与 generation 指标 | RAG eval 不能只看最终答案 |
| 合成生产事故 | 本 Case | 引用来自旧索引，答案与最新事实不一致 | index freshness、doc_version、citation support | “有引用”不等于“引用支持最新结论” |

## What / Why / How 抽取

| K 点 | What | Why | How | Prove |
|---|---|---|---|---|
| M4-K06 | RAG Eval = retrieval/generation/citation 三层门禁 | 只看答案会误判模型问题；只看 chunk 会误判 RAG 正确 | context recall、faithfulness、citation support、freshness | Case 11；RAG split report |
| M4-K08 | Dataset Lifecycle = eval set 的采样、版本和 bad case 回流 | 文档版本变化会让旧 golden 失效 | scenario 带 doc_version/index_version；postmortem 回流 | stale-index scenario |

## 监控与回滚

- **最先亮的监控层**：retrieved doc_version / indexed_at、stale_chunk_rate、citation_support_rate、index_lag。
- **隔离 / 回滚**：启用 refuse-if-stale 或只返回引用；回滚到上一版新鲜索引或强制重建目标 collection。

## SOP 摘要

| 阶段 | 动作 |
|---|---|
| 观察 | 打开 retrieval trace：chunk id、doc_version、indexed_at、citation |
| 隔离 | 对高风险答案启用 refuse-if-stale；临时切人工审核 |
| 定位 | 区分 ingestion 未跑、索引未刷新、filter 错、citation 不支持 |
| 修复验证 | 重建索引；跑 RAG eval；检查 citation support |
| 复盘 | 新增 stale index scenario，加入 M4 RAG Eval |

## Runtime / Evidence 映射

| 类型 | 当前状态 |
|---|---|
| 已有证据 | M4-K04 已有 retrieval vs generation 概念；oss-9415 可对照 |
| 已生成文档 | `case-11-rag-stale-index-hallucination.md` 与 [SOP](../sops/sop-case-11-rag-stale-index-hallucination.md) 已生成 |
| 已有 Runtime | `scenarios.json` S21（`STALE_INDEX`）；`python cli.py eval --baseline auto` |
| 面试证明 | RAG failure triage table |

## 在本体系中的位置

- **模块**：M4 RAG Eval 为主，M1 observe 与 M3 检索配置发布辅助。
- **Issue / runtime 任务**：M4-I04；**S21** 已落地于 `scenarios.json`（`STALE_INDEX`）；跑 `python cli.py eval --baseline auto` 验证
- **事故来源**：[oss-9415](../oss-incidents/oss-9415-ragflow-retrieval-ok-gen-fail.md) 提供 retrieval/generation 拆分校准。

## 关联 Case / OSS 区分轴

| 对比项 | [oss-9415](../oss-incidents/oss-9415-ragflow-retrieval-ok-gen-fail.md)：检索 OK 生成错 | Case 11：stale index 旧证据被引用 |
|---|---|---|
| 失败子类型 | generation / faithfulness | freshness / citation / index version |
| 检索层 | chunk 命中但不足以支撑答案 | 命中的是**旧版本** chunk |
| 第一信号 | retrieval score 正常、答案仍错 | `doc_version` / `indexed_at` 滞后 |
| 首要 fix | 拆 generation eval、加 faithfulness | index refresh、version filter、citation verifier |
| 面试一句话 | “召回到了，但生成没守住。” | “引用看起来合法，但索引已经过期。” |

## Prove 附表：RAG failure triage

| 用户症状 | 先查层 | 关键信号 | 常见根因 | 下一步 |
|---|---|---|---|---|
| 答案与最新政策不符 | retrieval trace | `doc_version`、`indexed_at` | 索引未刷新 / filter 错版本 | 重建索引 + stale scenario |
| 有引用但结论错 | citation | claim 是否被 chunk 支持 | citation verifier 缺失 | 加 citation support eval |
| 检索分高但答案胡编 | generation | chunk 内容 vs 最终 claim | 过度补全 / 幻觉 | faithfulness gate |
| 完全找不到相关内容 | retrieval | recall@k、相似度分布 | chunk 切分 / embedding | 调 ingestion，不是换大模型 |

## Prove 附表：stale-index eval scenario 草案

已落地到 `TrackARuntime/m4/scenarios.json`（**S21**）：

```json
{
  "id": "S21",
  "task": "answer pricing policy from knowledge base",
  "expect": "fail",
  "failure_code": "STALE_INDEX",
  "category": "retrieval",
  "doc_version": "v1",
  "index_version": "2026-08-01",
  "source_updated_at": "2026-08-07",
  "case_ref": "case-11"
}
```

验证：`cd TrackARuntime && python cli.py eval --baseline auto` → 在 `m4/evidence/evaluation-report.json` 中可见 `STALE_INDEX` 失败分布。

## 面试口述路径

60s：RAG 错误要拆 retrieval、generation、citation、freshness。  
2min：旧文档被引用不是模型幻觉，而是索引版本和 citation verification 缺失。  
5min：画 ingestion → index → retrieval → rerank → citation verifier → eval 的链路。

## 学习记录（自填）

- **Day1 根因猜测**：
- **与 PR/解法对照差距**：
- **口述练习日期 / 用时**：


