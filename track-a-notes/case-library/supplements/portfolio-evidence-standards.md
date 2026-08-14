# 作品集证据标准（HR / 终面视角）

> 提炼自求职校准对话，供 M6 portfolio 与 LinkedIn 段落使用。  
> **工程证据**仍以 TrackARuntime + case-library 口述为主。

## 进终面需要证明的三件事

1. **模糊需求 → 可用 AI assistant**（有场景、用户、工具边界，不是 Chat wrapper）
2. **能处理不确定性与失败**（主动讲 bad case、修复、监控、回滚）
3. **demo → 可交付**（eval、日志、权限、成本控制——哪怕用户是「内部 10 人」）

## 强项目长什么样

| 维度 | 加分证据 |
|---|---|
| 类型 | 知识库助手 / 代码库 assistant / 业务流程 agent / 多工具 workflow（有安全边界） |
| 使用 | 真实用户或明确内部试点（10+ 人也可） |
| 指标 | 准确率、采纳率、响应时间、成本、节省时间——**带数字** |
| 失败 | 幻觉、工具参数错、上下文过长、召回不准等 **至少 3 类** + 修复 |
| 工程质量 | trace、eval 集、回归门禁、回滚、Can/Cannot/Eval 三段 |

## 面试回答：满意 vs 不满意

**满意**：有场景 + 工具 + 演进路径（如先 RAG 再加 tool use 再 workflow）；知悉 **为何** 选模型/框架；能报失败分类与修复。

**不满意**：「ChatGPT wrapper」「只会 LangChain」「hyper-speed / bulletproof」无实例。

## 无商业用户时的可信项目（本体系路径）

**TrackARuntime** = anchor project：

- 固定 **22** 场景 eval + failure taxonomy（数字真源：[`TrackARuntime/README.md`](../../TrackARuntime/README.md)）
- harness 回滚演示
- trace 全链路
- 3 case study + 1 postmortem + 5min demo

可选 M6 扩展叙事见 [`system-guardian-blueprint.md`](system-guardian-blueprint.md)（**不替代** runtime）。

## 简历一句话方向

把「用 Cursor 做 AI」改成 **交付链路工程**：

> 专注于 AI 应用交付（Harness/MLOps 实践）：Prompt 版本、RAG/Agent 可观测性、固定 eval 与回滚；用 Cursor 辅助编码 + 人工 review 的增量开发。

## 学习记录（自填）

- **我的 TrackARuntime 数字**：
- **三条失败 + 修复**：
- **LinkedIn 段落定稿日期**：
