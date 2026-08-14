# OSS 事故案例库（扩展）

> 与 [`tutor/README.md`](../tutor/README.md) 绑定，但 **独立成篇** 便于复用与追加。  
> 格式见 [`../cases/_TEMPLATE.md`](../cases/_TEMPLATE.md)；OSS 专用字段：**Issue 链接、Day1–3 笔记路径、Runtime 命令**。  
> **类别说明**见 [`../README.md`](../README.md#分类体系)（OBS / CTL 等）。

## 已收录

| ID | 标题 | **主类** | 模块 | 文件 |
|---|---|---|---|---|
| oss-803 | mini-swe-agent container silent loop | **OBS** | M1 | [oss-803-mini-swe-container-silent-loop.md](oss-803-mini-swe-container-silent-loop.md) |
| oss-4575 | OpenHands ErrorObs vs Fatal（#4573→#4575） | **CTL** | M1 | [oss-4575-openhands-errorobs-vs-fatal.md](oss-4575-openhands-errorobs-vs-fatal.md) |
| oss-4579 | OpenHands stuck loop → fatal | **CTL** | M1 | [oss-4579-openhands-stuck-loop-fatal.md](oss-4579-openhands-stuck-loop-fatal.md) |
| oss-5099 | LangGraph pseudo-replan / 假恢复 | **CTL** | M1 | [oss-5099-langgraph-pseudo-replan-loop.md](oss-5099-langgraph-pseudo-replan-loop.md) |
| oss-1491 | Guardrails re-ask 空 fail_results crash | **REL** | M3 | [oss-1491-guardrails-reask-index-crash.md](oss-1491-guardrails-reask-index-crash.md) |
| oss-2643 | DeepEval loop metric scaffold | **MET** | M4 | [oss-2643-deepeval-loop-metric-scaffold.md](oss-2643-deepeval-loop-metric-scaffold.md) |
| oss-929 | DeepEval judge invalid JSON | **MET** | M4 | [oss-929-deepeval-judge-invalid-json.md](oss-929-deepeval-judge-invalid-json.md) |
| oss-9415 | RAGFlow 检索 OK 生成错 | **KNW** | M4 | [oss-9415-ragflow-retrieval-ok-gen-fail.md](oss-9415-ragflow-retrieval-ok-gen-fail.md) |

> **M1 四 Issue 已全部收录**（对应 [`module-01/issues.md`](../../module-01/issues.md) I01–I03B）。  
> **M3–M4 主修 Issue** 已收录（#1491、#2643、#929、#9415）；M5 深 Case 见 [`cases/`](../cases/) + [`../sops/`](../sops/)。

## 待收录（有 runtime 落点才读）

见 tutor/README「刻意不读」列表；达标 L3 后再迁入本目录。

## 如何添加

完整流程（主线 Issue + Px Case 10–18 校准、PR 检查清单、认领表）见 **[`HOW-TO-ADD-OSS-CALIBRATION.md`](../HOW-TO-ADD-OSS-CALIBRATION.md)**。

速查：

1. 复制现有 `oss-*.md` 或按该文档 §4 建 `oss-XXXX-….md`。
2. 在本表登记一行。
3. 反链到 `cases/case-XX.md` 和/或 `module-XX/issues.md`。
4. 同步 [`../README.md`](../README.md) 与 [`KNOWLEDGE-MAP.md`](../../KNOWLEDGE-MAP.md)（若影响 Case 10–18）。
