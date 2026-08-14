# 导师规范 · 知识工程点 + 精选 Issue

> **Residency v2 导师参考**：K 点 Level 定义、模块索引、Issue 选材原则。  
> **评分**：[`MASTERY-RUBRIC.md`](../MASTERY-RUBRIC.md)  
> **知识体系**：[`curriculum/00-knowledge-system.md`](../curriculum/00-knowledge-system.md)（五条生命线 + 26 K 矩阵）  
> **求职增强**：[`curriculum/02-production-extension-packs.md`](../curriculum/02-production-extension-packs.md)（P1–P6 生产扩展包，不改变核心 Exit）  
> **工程证据**：一律指向 [`TrackARuntime/`](../../TrackARuntime/)。

**Cursor 预览说明**：跨文件 `#锚点` 跳转不可靠。各模块 GUIDE 请直链同目录 **`knowledge.md` / `issues.md`**（整文件打开）。

---

## 模块索引

| 模块 | 知识工程点 | 精选 Issue |
|---|---|---|
| M1 | [module-01/knowledge.md](../module-01/knowledge.md) | [module-01/issues.md](../module-01/issues.md) |
| M2 | [module-02/knowledge.md](../module-02/knowledge.md) | [module-02/issues.md](../module-02/issues.md) |
| M3 | [module-03/knowledge.md](../module-03/knowledge.md) | [module-03/issues.md](../module-03/issues.md) |
| M4 | [module-04/knowledge.md](../module-04/knowledge.md) | [module-04/issues.md](../module-04/issues.md) |
| M5 | [module-05/knowledge.md](../module-05/knowledge.md) | [module-05/issues.md](../module-05/issues.md) |
| M6 | [portfolio/README.md](../../portfolio/README.md) | [portfolio/README.md](../../portfolio/README.md)（M6 作品集入口） |
| 求职增强 | [curriculum/02-production-extension-packs.md](../curriculum/02-production-extension-packs.md) | Case 10–18 生产扩展 Case 草稿；SOP 已全部落地；Portfolio 叙事 |

---

## 能力递进模型（L1 / L2 / L3）

| Level | 学习者状态 | 证据类型 |
|---|---|---|
| **L1** | 能解释概念与系统等价 | 60s 口述、GUIDE 原理段 |
| **L2** | 能 debug：读 Issue/trace，定位根因，改一处 runtime | Day1–3 笔记 + PR 对照 + trace 路径 |
| **L3** | 能设计：无 OSS 参考也能画 schema/策略 | runtime 中新增模块或 policy 表 |

**求职 realistic 目标**：M1–M4 核心 K **均 ≥ L2**；**至少 2 个 K 点达到 L3**（建议 M1-K05、M2-K02）。

---

## 跨模块证据矩阵

| 卖给面试官 | 模块 | 证据路径 |
|---|---|---|
| 我会 Agent 闭环 | M1 | `TrackARuntime/m1_m2/evidence/*/state.json` |
| 我会 Tool+Trace | M2 | `TrackARuntime/m1_m2/evidence/*/trace.json` |
| 我会 Harness | M3 | `m3/evidence/harness-report.json` |
| 我会 Eval | M4 | `m4/evidence/evaluation-report.md` |
| 我会值班思维 | M5 | SOP + mapping |
| 我会表达 | M6 | drill 记录 |

RAG 非核心主轴；Case 1/4 概念级在 M4/M5 覆盖。若目标是 Agent Development 求职，按 `curriculum/02` 的 P2 补 RAG Eval、citation、index freshness。

---

## Issue 选材原则

- 每模块 **最多 2 个主修 Issue**；每个 Issue 必须有 **TrackARuntime 任务**。
- **三日校准**：Day1 现象 → Day2 工程解法 → Day3 对照 PR → **改 runtime** → rubric 打分。

---

## 刻意不读（除非已达 L3）

- LangGraph #6731, OpenHands #6032, DeepEval #929, RAGFlow #8022 等原选修列表
- 读完主修 + runtime 任务 + rubric ≥2.0 后再考虑
