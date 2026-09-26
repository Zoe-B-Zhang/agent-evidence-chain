# Agent 工程化证据链模板 · 从 OSS 事故到可复现物证

> Open source · offline reproducible · [MIT](LICENSE)  
> Repo: [agent-evidence-chain](https://github.com/Zoe-B-Zhang/agent-evidence-chain) · Learning spine: [track-a-notes/](track-a-notes/) · Optional mock self-check: [TrackARuntime/](TrackARuntime/) · [portfolio/](portfolio/) (templates & examples)  
> Display names / internal codenames (Residency v2, Track A, etc.): [STRUCTURE.md · naming](STRUCTURE.md#命名约定避免混读)

---

## English overview

**An incident-driven evidence-chain template for agent platform engineering interviews** — not a production agent runtime, not a framework crash course.

Reverse-engineer agent reliability from **real OSS incidents** → structured **Cases + SOPs** → five engineering lifelines (M1–M5) → **offline mock CLI artifacts** you can cite in a whiteboard or resume.


| You get                                                                               | This is **not**                                                           |
| ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| 18 incident Cases + formal SOPs (429, RAG stale index, secret leakage, HITL fatigue…) | A production agent platform or hosted service                             |
| Five lifelines: control plane, tool boundary, config rollout, eval gate, on-call SOP  | A "build an agent in 30 minutes" LangGraph/CrewAI tutorial                |
| Optional mock CLI → inspectable `state.json`, `trace.json`, harness & eval reports    | A substitute for real LLM providers, vector DBs, or alerting pipelines    |
| [Portfolio templates](portfolio/) — resume bullets, case studies, 5-min demo script   | Finished interview materials (you fill `portfolio/personal/`, gitignored) |


**How the evidence chain works**

```text
OSS incident / PR  →  Case + SOP  →  K-point + module exit  →  mock CLI artifact  →  interview claim
```

Every resume bullet must point to **code, a CLI command, an evidence file, or a Case** — see `[portfolio/examples/resume-snippet.example.md](portfolio/examples/resume-snippet.example.md)`. Personal drafts go in `[portfolio/personal/](portfolio/personal/README.md)` (not committed).

**What the mock runtime can demonstrate** (`TrackARuntime/`)

- Agent loop with persisted state + trace; allowlist, schema, HITL stub
- Harness: prompt versions, guardrails, gray rollout, rollback
- Eval: 22 scenarios, failure taxonomy, regression gate (`--baseline auto`)

**What it cannot do** (say this out loud in interviews)

- No live LLM provider, distributed queue, OTel backend, or vector index
- P1–P6 extension demos (`demo-llm-gateway`, `eval-rag`, …) are **documented + designed, not all implemented** — see [BACKLOG.md](track-a-notes/case-library/BACKLOG.md)
- M1–M5 depth lives in `[track-a-notes/](track-a-notes/)` (Chinese); English readers: start here, then use browser translate for curriculum

**30-second repro**

```bash
cd TrackARuntime
pip install -r requirements.txt
python cli.py eval --baseline auto
```

→ Full learning path (Chinese): [USAGE.md](USAGE.md) · Case index: [case-library/README.md](track-a-notes/case-library/README.md) · Layout: [STRUCTURE.md](STRUCTURE.md)

---



## 中文概要

**一句话**：OSS 事故 → Case/SOP → 五条生命线 → 离线 mock 物证；这是**可复现的面试证据链模板**，不是生产运行时。


| 你能得到什么                                                       | 这不是什么                           |
| ------------------------------------------------------------ | ------------------------------- |
| 五条工程生命线（M1–M5）+ 生产扩展 Case 10–18                              | 不是生产 Agent 平台                   |
| 18 个故障 Case + 正式 SOP（429、RAG stale、secret leakage…）          | 不是「30 分钟搭完就忘」的框架课               |
| 可选 mock CLI：`run` / `harness` / `eval` → 可指读的物证              | 不替代真实 LLM / 向量库 / 告警通道          |
| `[portfolio/](portfolio/)` 模板：简历 bullet、case study、5 分钟 demo | 不是替你写好的面试稿（成稿放 `personal/`，不提交） |


**证据链**：OSS/PR 事故 → Case + SOP → K 点与模块 Exit → mock 物证 → 面试 claim。简历每条须对齐代码、命令、evidence 或 Case，见 `[portfolio/examples/resume-snippet.example.md](portfolio/examples/resume-snippet.example.md)`。

**和常见 Agent 课差在哪？** 从 **observe 语义、灰度回滚、eval 门禁、值班 SOP** 切入，而不是从框架 API 切入。P1–P6 扩展 Runtime demo **尚在 BACKLOG**，文档中规划命令勿当作已存在 CLI。

**30 秒自证（可选 mock 自检）**：

```bash
cd TrackARuntime
pip install -r requirements.txt
python cli.py eval --baseline auto
```

→ 开始学习：[USAGE.md](USAGE.md) · Case 索引：[case-library/README.md](track-a-notes/case-library/README.md) · 目录分层：[STRUCTURE.md](STRUCTURE.md)

---



## 怎么用

**学习主轴** → [USAGE.md](USAGE.md)（学习路径、Case 与 curriculum 互链、模块 Exit）。


| 你还想…             | 去看                                                                                                                           |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| 仓库目录与分层（含可选自检模拟） | `[STRUCTURE.md](STRUCTURE.md)`                                                                                               |
| 学习主轴索引           | `[track-a-notes/README.md](track-a-notes/README.md)` · 首读 `[curriculum/00](track-a-notes/curriculum/00-knowledge-system.md)` |
| K 点详卡 / Prove    | `[track-a-notes/module-0X/knowledge.md](track-a-notes/module-01/knowledge.md)`                                               |
| K 点速查索引          | `[KNOWLEDGE-MAP.md](track-a-notes/KNOWLEDGE-MAP.md)`                                                                         |
| 分不清 M / K / P    | `USAGE.md` [§1.0](USAGE.md) · `KNOWLEDGE-MAP` [§2.5](track-a-notes/KNOWLEDGE-MAP.md)                                         |
| 改进待办             | `[track-a-notes/case-library/BACKLOG.md](track-a-notes/case-library/BACKLOG.md)`                                             |
| 贡献与 evidence 策略  | `[CONTRIBUTING.md](CONTRIBUTING.md)`                                                                                         |
| AI 编程助手约定        | `[AGENTS.md](AGENTS.md)`                                                                                                     |


---

> 下面是大纲；第一次来请先看 `[USAGE.md](USAGE.md)`。



## 五条生命线（一句话）


| 模块    | 考核句           | 主轴材料                                                                                       | 自检模拟（可选）             |
| ----- | ------------- | ------------------------------------------------------------------------------------------ | -------------------- |
| M1+M2 | 控制面可靠 + 工具可审计 | `[module-01](track-a-notes/module-01/)` · `[module-02](track-a-notes/module-02/)` · OSS 三联 | `run` / `demo-*`（可选） |
| M3    | 配置可灰度发布与回滚    | `[module-03](track-a-notes/module-03/)` · Case 02/08                                       | `harness`（可选）        |
| M4    | 行为质量有数据门禁     | `[module-04](track-a-notes/module-04/)` · Case 01/08                                       | `eval`（可选）           |
| M5    | 线上故障有 SOP 与映射 | `[module-05](track-a-notes/module-05/)` · Case + SOP                                       | 无独立 CLI              |




## 主轴 K 点覆盖（`track-a-notes`）

> **详卡真源**：各 `[module-XX/knowledge.md](track-a-notes/module-01/knowledge.md)` · **索引**：`KNOWLEDGE-MAP` [§5–§7](track-a-notes/KNOWLEDGE-MAP.md)  
> **图例（主轴列）**：该 K 在课程中的主要材料（PR 分析 / Case / SOP / 设计题）  
> **图例（自检列）**：可选 mock 自检是否已有对应模拟（与主轴覆盖**不是同一回事**；目录见 `[STRUCTURE.md](STRUCTURE.md)`）  
> **P1–P6**：主轴已有 Case 10–18；自检模拟 **均未实现**——计划 workflow：**先收集实际 PR case → 再编写模拟例子**（见 `[BACKLOG.md](track-a-notes/case-library/BACKLOG.md)`）。



### M1 · `[module-01](track-a-notes/module-01/)`


| K 点                  | 主轴材料                                                                                                                                                                                                                                  | 自检模拟（可选）                               |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| M1-K01 状态机           | `[knowledge](track-a-notes/module-01/knowledge.md)` · `01-course` [第 1 课](track-a-notes/curriculum/01-course.md)                                                                                                                      | **有** · `run` → `state.json`           |
| M1-K02 observe       | `issues` [I01–I02](track-a-notes/module-01/issues.md) · [oss-803](track-a-notes/case-library/oss-incidents/oss-803-mini-swe-container-silent-loop.md) · [Case 03](track-a-notes/case-library/cases/case-03-context-lost-in-middle.md) | **有** · `[retryable]` / `fatal`        |
| M1-K03 replan        | [oss-5099](track-a-notes/case-library/oss-incidents/oss-5099-langgraph-pseudo-replan-loop.md) · `--pseudo-replan` 对照                                                                                                                  | **有** · `--llm mock`                   |
| M1-K04 终止/checkpoint | I05 · [Case 13](track-a-notes/case-library/cases/case-13-worker-death-checkpoint-resume.md)                                                                                                                                           | **有** · checkpoint/resume              |
| M1-K05 fatal 分类      | [oss-4575](track-a-notes/case-library/oss-incidents/oss-4575-openhands-errorobs-vs-fatal.md) · A/B 口述                                                                                                                                 | **有** · `--simulate-container-death`   |
| M1-K06 fingerprint   | [oss-4579](track-a-notes/case-library/oss-incidents/oss-4579-openhands-stuck-loop-fatal.md) · I03A/B                                                                                                                                  | **有** · `stuck loop` / `pseudo replan` |
| M1-K07–K09 扩展        | **P4** · Case 13 / 14 / 18 · SOP                                                                                                                                                                                                      | **无**（设计题）                             |




### M2 · `[module-02](track-a-notes/module-02/)`


| K 点                 | 主轴材料                                                                                                                    | 自检模拟（可选）                          |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| M2-K01 allowlist    | `[issues](track-a-notes/module-02/issues.md)` · [Case 06](track-a-notes/case-library/cases/case-06-prompt-injection.md) | **有** · `demo-allowlist`          |
| M2-K02 trace        | I01/I02 · [Case 07](track-a-notes/case-library/cases/case-07-latency-avalanche.md)                                      | **有** · `trace.json` 指读           |
| M2-K03 schema/HITL  | I03/I04                                                                                                                 | **有** · `--require-hitl`          |
| M2-K04 timeout tier | oss-7355 · Case 07                                                                                                      | **部分** · `_timeouts` 可读，未 enforce |
| M2-K05 stalled      | oss-8448                                                                                                                | **有** · `demo-no-output-hang`     |
| M2-K06–K09 扩展       | **P3** · Case 12 / 17 / 18                                                                                              | **无**                             |




### M3 · `[module-03](track-a-notes/module-03/)`


| K 点              | 主轴材料                                                                                         | 自检模拟（可选）                             |
| ---------------- | -------------------------------------------------------------------------------------------- | ------------------------------------ |
| M3-K01 交付层       | `[knowledge](track-a-notes/module-03/knowledge.md)` · Case 02                                | **部分** · harness + metrics stub      |
| M3-K02 Prompt 版本 | Case 02 · prompts v1/v2                                                                      | **有** · `harness --prompt v2`        |
| M3-K03 护栏        | Case 02 / [08](track-a-notes/case-library/cases/case-08-survivorship-bias-eval.md)           | **有** · `guardrails` → report        |
| M3-K04 回滚        | `[rollout-auto-rollback](track-a-notes/study-notes/rollout-auto-rollback.md)`                | **有** · `rollback_to_v1` / `--watch` |
| M3-K05 灰度        | Case 08                                                                                      | **有** · `--gray-percent`             |
| M3-K06 re-ask    | oss-1491 · PR #1492                                                                          | **部分** · 概念级                         |
| M3-K07–K09 扩展    | **P1** · [Case 10](track-a-notes/case-library/cases/case-10-provider-rate-limit-fallback.md) | **无**（router/quota 仅 stub）           |




### M4 · `[module-04](track-a-notes/module-04/)`


| K 点                 | 主轴材料                                                               | 自检模拟（可选）                              |
| ------------------- | ------------------------------------------------------------------ | ------------------------------------- |
| M4-K01 任务集          | `[knowledge](track-a-notes/module-04/knowledge.md)` · SWE-bench 类比 | **有** · 22 scenarios                  |
| M4-K02 taxonomy     | Case 01/08 · failure taxonomy                                      | **有** · report 建议                     |
| M4-K03 回归门禁         | oss-929                                                            | **有** · `--baseline auto` / CI `0.45` |
| M4-K04 检索 vs 生成     | oss-9415                                                           | **有** · `category_split`              |
| M4-K05 trace metric | oss-2643                                                           | **部分** · `trace_eval` 未接 runner       |
| M4-K06–K09 扩展       | **P2/P5** · Case 11 / 15 / 12                                      | **部分** · S21/S22 stub only            |




### M5 · `[module-05](track-a-notes/module-05/)`


| K 点           | 主轴材料                                                                          | 自检模拟（可选）                     |
| ------------- | ----------------------------------------------------------------------------- | ---------------------------- |
| M5-K01 五步 SOP | `[sops/](track-a-notes/case-library/sops/)` · Case 2/3/6/7                    | **无**                        |
| M5-K02 系统等价   | Case 库 · `[project-mapping](track-a-notes/module-05/project-mapping.md)`      | **无**                        |
| M5-K03 监控分层   | `[monitoring-layers](track-a-notes/module-05/monitoring-layers.md)` · Case 07 | **部分** · `metrics-*.json` 旁路 |
| M5-K04 项目映射   | `[project-mapping.md](track-a-notes/module-05/project-mapping.md)`            | **无**                        |
| M5-K05–K07 扩展 | **P6/P1** · Case 16 / 10                                                      | **无**                        |




### P1–P6 扩展包


| Px  | 主轴（Case + `02` [机理](track-a-notes/curriculum/02-production-extension-packs.md)）                | 自检模拟（可选）                |
| --- | ---------------------------------------------------------------------------------------------- | ----------------------- |
| P1  | [Case 10](track-a-notes/case-library/cases/case-10-provider-rate-limit-fallback.md)            | **计划**（先 PR case → 后模拟） |
| P2  | [Case 11](track-a-notes/case-library/cases/case-11-rag-stale-index-hallucination.md)           | **计划**                  |
| P3  | Case 12 / 17                                                                                   | **计划**                  |
| P4  | Case 13 / 14                                                                                   | **计划**                  |
| P5  | [Case 15](track-a-notes/case-library/cases/case-15-judge-bias-false-regression.md)             | **计划**                  |
| P6  | [Case 16](track-a-notes/case-library/cases/case-16-observability-cardinality-alert-fatigue.md) | **计划**                  |


主轴学习栈与 Exit 自评见 `[USAGE.md](USAGE.md)`；可选自检命令与物证指读见 `[STRUCTURE.md](STRUCTURE.md)` · `USAGE.md` [§2.1](USAGE.md#21-证据文件怎么用m1m2-示例)。