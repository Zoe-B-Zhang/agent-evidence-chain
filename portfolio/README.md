# Portfolio — M6 面试材料（模板 + 示例）

> **English**: Interview packaging for the [evidence-chain template](../README.md#english-overview). Public repo ships **neutral templates & examples**; your first-person drafts go in [`personal/`](personal/README.md) (gitignored). Every claim must trace to a CLI command, evidence file, or Case.

完成 M1–M5 后，用本目录包装求职叙事。核心叙事先证明 **五条工程生命线**，再用 [`02-production-extension-packs`](../track-a-notes/curriculum/02-production-extension-packs.md) 的 **P1–P6** 回答生产追问。

**公开仓策略**：本目录只放 **通用模板** 与 **中性示例**（第三人称、可复现 CLI 数字）。**第一人称成稿** 复制到 [`personal/`](personal/README.md) 填写，**勿提交** 到 GitHub。

使用指引：[`USAGE.md`](../USAGE.md) · Case 正文：[`case-library/cases/`](../track-a-notes/case-library/cases/) · 面试 drill：[`interview/DRILLS.md`](../track-a-notes/interview/DRILLS.md)

## 目录结构

| 路径 | 用途 | 是否提交公开仓 |
|---|---|---|
| [`demo-script.md`](demo-script.md) | 5 分钟口述 Demo（含 §4 P1 扩展） | ✅ |
| [`templates/`](templates/) | 空模板：case study · postmortem · LinkedIn · 简历 | ✅ |
| [`examples/`](examples/) | 填好结构的 **示例**（非作者真实简历） | ✅ |
| [`personal/`](personal/README.md) | **你的成稿**（gitignore） | ❌ |

## 快速入口

| 文件 | 用途 |
|---|---|
| [demo-script.md](demo-script.md) | 5 分钟 Demo 脚本 |
| [templates/resume-snippet.template.md](templates/resume-snippet.template.md) | 简历 bullet 模板 → 复制到 `personal/` |
| [examples/resume-snippet.example.md](examples/resume-snippet.example.md) | 简历 bullet 示例（第三人称 + 物证数字） |
| [examples/project-mapping-example.md](examples/project-mapping-example.md) | M5 project-mapping 填写示例 |
| [examples/README-snippet.example.md](examples/README-snippet.example.md) | Can / Cannot / Eval 三段示例 |
| [templates/case-study-01.template.md](templates/case-study-01.template.md) | Happy path + trace |
| [templates/case-study-02.template.md](templates/case-study-02.template.md) | 反馈闭环 / 自愈循环 |
| [templates/case-study-03.template.md](templates/case-study-03.template.md) | 故意失败 + fallback + 回滚 |
| [templates/postmortem.template.md](templates/postmortem.template.md) | 最严重失败复盘 |
| [templates/linkedin-project-paragraph.template.md](templates/linkedin-project-paragraph.template.md) | LinkedIn / 简历项目段落 |

## 个人成稿 workflow

```text
1. cp templates/case-study-01.template.md → personal/case-study-01.md
2. 本地跑 CLI，从 TrackARuntime/*/evidence/ 抄 run_id 与数字
3. 参考 examples/ 的写法；改第一人称、目标 JD
4. git status 确认 personal/ 下文件未被 staged
```

## M6 Exit（知识工程点）

> 评分：[MASTERY-RUBRIC.md](../track-a-notes/MASTERY-RUBRIC.md) · 交付物 = **`personal/` 成稿** + [`DRILLS.md`](../track-a-notes/interview/DRILLS.md) 计时通过（personal 不提交公开仓）。

| ID | 知识点 | L1 | L2 | L3 |
|---|---|---|---|---|
| M6-K01 | 证据链 | 背结构 | case study 成稿 | 5min demo 计时 |
| M6-K02 | STAR + metric | 模板 | 含数字复盘 | 模拟面试 PASS |
| M6-K03 | Can/Cannot/Eval | README 三段 | 简历段 | LinkedIn 定稿 |

**面试就绪线**：M1–M4 均 Exit + `personal/` 三份 case study + demo 一次计时通过。

## 生产扩展 Case（P1–P6）

| 材料方向 | Case / SOP | 可讲重点 |
|---|---|---|
| LLM Gateway / 配额 | [Case 10](../track-a-notes/case-library/cases/case-10-provider-rate-limit-fallback.md) · [SOP](../track-a-notes/case-library/sops/sop-case-10-provider-rate-limit-fallback.md) | 429、quota-aware fallback、灰度 |
| RAG Eval / 新鲜度 | [Case 11](../track-a-notes/case-library/cases/case-11-rag-stale-index-hallucination.md) · [SOP](../track-a-notes/case-library/sops/sop-case-11-rag-stale-index-hallucination.md) | retrieval / generation / citation |
| Tool Policy / 安全 | [Case 12](../track-a-notes/case-library/cases/case-12-indirect-prompt-injection-tool-abuse.md) · [SOP](../track-a-notes/case-library/sops/sop-case-12-indirect-prompt-injection-tool-abuse.md) | policy、red team |
| Runtime Scale | [Case 13](../track-a-notes/case-library/cases/case-13-worker-death-checkpoint-resume.md) · [SOP](../track-a-notes/case-library/sops/sop-case-13-worker-death-checkpoint-resume.md) | checkpoint、lease、idempotency |
| Memory Policy | [Case 14](../track-a-notes/case-library/cases/case-14-memory-poisoning-version-rollback.md) · [SOP](../track-a-notes/case-library/sops/sop-case-14-memory-poisoning-version-rollback.md) | provenance、rollback |
| Judge Calibration | [Case 15](../track-a-notes/case-library/cases/case-15-judge-bias-false-regression.md) · [SOP](../track-a-notes/case-library/sops/sop-case-15-judge-bias-false-regression.md) | judge-human disagreement |
| Observability | [Case 16](../track-a-notes/case-library/cases/case-16-observability-cardinality-alert-fatigue.md) · [SOP](../track-a-notes/case-library/sops/sop-case-16-observability-cardinality-alert-fatigue.md) | cardinality、SLO |
| Secret / 数据边界 | [Case 17](../track-a-notes/case-library/cases/case-17-secret-leakage-through-tool-trace.md) · [SOP](../track-a-notes/case-library/sops/sop-case-17-secret-leakage-through-tool-trace.md) | redaction |
| HITL UX | [Case 18](../track-a-notes/case-library/cases/case-18-approval-fatigue-destructive-action.md) · [SOP](../track-a-notes/case-library/sops/sop-case-18-approval-fatigue-destructive-action.md) | approval fatigue |

口述串联见 [demo-script.md](demo-script.md) **§4**（Case 10/11/12/15，60s）。

## 求职增强材料（规划 · 建议放 personal/）

| 文件（personal/ 内） | 用途 | 绑定扩展包 |
|---|---|---|
| `agent-platform-architecture.md` | M1–M5 + Gateway / RAG / Policy / Runtime / Observability 一页架构 | P1–P6 |
| `agent-engineering-demo-script.md` | 3/10/30 分钟演示；已实现 vs 设计题 | P6 |
| `agent-eval-safety-report.md` | Eval、RAG split、Judge、SEC red team 求职版报告 | P2/P3/P5 |
| `agent-reliability-case-study.md` | Case 10–18 中选 2–3 个事故复盘 | P1/P3/P4/P6 |

## 证据来源（可选自检模拟）

路径与命令见 [`STRUCTURE.md`](../STRUCTURE.md)。口述时可引用：

- Agent replan: `m1_m2/evidence/<run_id>/state.json`
- Trace: `m1_m2/evidence/<run_id>/trace.json`
- Harness: `m3/evidence/harness-report.json`
- Eval: `m4/evidence/evaluation-report.md`（数字真源见 STRUCTURE 所链自检文档）

## 生产扩展证据边界

- **可声称**：主轴 M1–M5 材料 + 可选自检物证已覆盖教学证据链；能设计 Gateway / RAG Eval / Policy / Runtime Scale / Observability 扩展路径。
- **不应声称**：已接真实 LLM Provider、向量库、分布式 queue、OTel 后端或自动告警通道。
- 每个简历 claim 须指向：代码、命令、evidence、Case 或 **`personal/` 成稿**。

M6 若扩展 TravelRouteMemo / System Guardian，在 `personal/` case study 中补充第二套路径，**不替代**上述主轴与自检物证。
