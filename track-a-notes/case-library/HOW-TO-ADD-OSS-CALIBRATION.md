# 如何增补 OSS 校准来源（真实 Issue / PR 链接）

> **定位**：本仓库最喜欢的学习材料，是把 **理论（K 点 / Case）** 与 **真实工程现场（GitHub Issue / PR）** 用链接钉在一起，再用三日校准检验理解是否正确。  
> **方法论**：[`METHODOLOGY.md`](METHODOLOGY.md) · **Case 模板**：[`cases/_TEMPLATE.md`](cases/_TEMPLATE.md) · **改进待办**：[`BACKLOG.md`](BACKLOG.md)

---

## 1. 材料分层（不要只加一条外链）

```text
GitHub Issue / PR（外链真源）
    ↓
oss-incidents/oss-XXXX-标题.md     ← 可复用短文（全库索引）
    ↓
module-XX/issues.md                ← 主修选材：K 点 + 自检任务 + 证据（主线 M1–M5）
module-XX-day1/2/3.md              ← 学习者笔记（Day1 只抄现象、先猜根因）
    ↓
cases/case-XX.md + sops/           ← 正式 Case + SOP（含 Px Case 10–18）
    ↓
KNOWLEDGE-MAP.md                   ← 反查索引
```

**反模式**：只在 `module-01-day1.md` 加一行链接、不写 `oss-incidents/` — 其他模块与 Case 无法复用。

---

## 2. 两条贡献路径

### 路径 A · 主线模块（M1–M5）

适合能挂到 `module-XX/issues.md` 的**主修或补充 Issue**（范例：[`module-01-day1.md`  Issue 1 链接](https://github.com/SWE-agent/mini-swe-agent/issues/803) → [`oss-803`](oss-incidents/oss-803-mini-swe-container-silent-loop.md)）。

| 步骤 | 动作 | 文件 |
|---|---|---|
| A1 | 确认 Issue/PR 能映射到 **K 点**，且有自检任务或设计题落点 | — |
| A2 | 新建 `oss-XXXX-….md`（见 §4 字段） | `oss-incidents/` |
| A3 | 登记索引 | `oss-incidents/README.md` |
| A4 | 写入模块选材表 | `module-XX/issues.md` |
| A5 | （学习者自填）Day1 只抄现象 + 根因猜测 | `module-XX-day1.md` 等 |
| A6 | 同步 K 点索引 | `KNOWLEDGE-MAP.md`；若动核心 K 点另改 `module-XX/knowledge.md` |

**准入**（见 [`tutor/README.md`](../tutor/README.md)）：主修 Issue 需有 **Runtime 任务** 或明确的 **设计题**；否则标为扩展阅读，不进主修表。

### 路径 B · Px 扩展包 Case（10–18 及以后）

Px Case 多为「合成叙事 + OSS 校准」。社区贡献默认走 **校准模式**：**不重写** Case 主故事，只补真实锚点。

| 步骤 | 动作 | 文件 |
|---|---|---|
| B1 | 在 [`02-production-extension-packs.md`](../curriculum/02-production-extension-packs.md) 确认 **Px** 与目标 Case | — |
| B2 | 找 1–2 个真实 Issue/PR（**优先已 merge PR**，便于 Day3 对照） | — |
| B3 | 新建 `oss-XXXX-….md` | `oss-incidents/` |
| B4 | Case 元数据加 `OSS 对照`；`来源` 改为「合成 + oss-XXXX 校准」 | `cases/case-XX.md` |
| B5 | 在「对应 Issue / PR / 校准来源」表加一行 | 同上（见 Case 11 / 15 范例） |
| B6 | 更新 Case 库索引 | `case-library/README.md` |
| B7 | 同步 K 点 / Px 反查 | `KNOWLEDGE-MAP.md` §7 |
| B8 | （可选）补 SOP 校准段；认领 Runtime demo | `sops/` · [`BACKLOG.md`](BACKLOG.md) |

**好范例**：[`case-11`](cases/case-11-rag-stale-index-hallucination.md)（`oss-9415`）、[`case-15`](cases/case-15-judge-bias-false-regression.md)（`oss-929`）。

---

## 3. Case 10–18 · OSS 校准状态（欢迎认领）

| Case | Px | 当前 `来源` 摘要 | OSS 对照 | 认领建议 |
|---|---|---|---|---|
| [10](cases/case-10-provider-rate-limit-fallback.md) | P1 | 合成 + provider 文档 + **未来 OSS** | ⬜ 待补 | LLM Gateway / 429 / quota pool 相关 Issue |
| [11](cases/case-11-rag-stale-index-hallucination.md) | P2 | 合成 + oss-9415 扩展 | ✅ [oss-9415](oss-incidents/oss-9415-ragflow-retrieval-ok-gen-fail.md) | 可再补 stale-index / citation 类 Issue |
| [12](cases/case-12-indirect-prompt-injection-tool-abuse.md) | P3 | 安全规范 + 合成 + **未来 OSS** | ⬜ 待补 | 间接注入 / tool abuse 真实 PR |
| [13](cases/case-13-worker-death-checkpoint-resume.md) | P4 | 合成 + 分布式模式 | ⬜ 待补 | worker lease / checkpoint 类 Agent runtime Issue |
| [14](cases/case-14-memory-poisoning-version-rollback.md) | P4 | 合成 + 注入模式 | ⬜ 待补 | memory 版本 / preference 污染 Issue |
| [15](cases/case-15-judge-bias-false-regression.md) | P5 | oss-929 扩展 + 合成 | ✅ [oss-929](oss-incidents/oss-929-deepeval-judge-invalid-json.md) | 可再补 judge calibration 类 Issue |
| [16](cases/case-16-observability-cardinality-alert-fatigue.md) | P6 | 合成 + observability 模式 | ⬜ 待补 | OTel cardinality / alert fatigue 案例 |
| [17](cases/case-17-secret-leakage-through-tool-trace.md) | P3 | 安全规范 + 合成 | ⬜ 待补 | secret redaction / trace 泄露 Issue |
| [18](cases/case-18-approval-fatigue-destructive-action.md) | P3/P6 | 合成 + HITL 模式 | ⬜ 待补 | approval fatigue / destructive action UX |

认领后请在 PR 中 @ 更新本表（将 ⬜ 改为 ✅ 并链到 `oss-XXXX`）。

---

## 4. `oss-incidents/oss-XXXX.md` 最小字段

复制现有 [`oss-803`](oss-incidents/oss-803-mini-swe-container-silent-loop.md) 改元数据即可：

| 字段 | 必填 | 说明 |
|---|---|---|
| **ID** | ✅ | `oss-` + 短号（勿与已有冲突） |
| **标签** | ✅ | agent / gateway / rag / sec … |
| **关联模块** | ✅ | M1–M5 主归属 |
| **Case 库关联** | 推荐 | 链到 `case-XX` 或相关 Case |
| **Issue** | ✅ | GitHub Issue URL |
| **对照 PR** | 推荐 | 已 merge PR（Day3 对照用） |
| **自检命令** | 若有 | 见 [`STRUCTURE.md`](../../STRUCTURE.md)；**无则写「设计题」**，勿伪造 CLI |
| **Day1–3 笔记** | 主线 Issue 时 | 链到 `module-XX-dayN.md` |
| **添加日期** | ✅ | YYYY-MM-DD |

正文至少含：**场景 · 现象 · 根因（Day1 猜测框）· 系统等价物 · 工程规则一句**。

---

## 5. 质量门槛（PR 必过）

对齐 [`METHODOLOGY.md`](METHODOLOGY.md) 三日校准法：

1. **Day1 可读**：不打开 PR 也能从 Issue 读懂现象。  
2. **K 点可映射**：写明补强 `Mx-Kyy` 或目标 **Px**。  
3. **系统等价物**：一句翻译成传统系统概念（如 #803 → dead backend 仍无限 retry）。  
4. **Day3 可对照**：优先有 merge PR 或官方 RFC/文档。  
5. **Prove 可口述**：关联 Case 的 60s / 2min 路径能引用该链接。  
6. **诚实边界**：[`BACKLOG.md`](BACKLOG.md) 中未实现的 demo **不得**写成已存在。

---

## 6. PR 检查清单（复制到 PR 描述）

```markdown
- [ ] 新增 `oss-incidents/oss-XXXX-….md`，元数据完整
- [ ] 更新 `oss-incidents/README.md` 索引表
- [ ] 至少一处反链：`cases/case-XX.md` 和/或 `module-XX/issues.md`
- [ ] Case 元数据：`OSS 对照` +「对应 Issue / PR / 校准来源」表已更新
- [ ] `case-library/README.md` / `KNOWLEDGE-MAP.md` 已同步（若影响 Case 10–18 或 K 点）
- [ ] 未伪造自检 CLI；设计题已在 BACKLOG 或 Case 中标明
- [ ] 本文件 §3 认领表已更新（Px Case 校准时）
```

---

## 7. 两种增补模式（选对再动笔）

| 模式 | 何时用 | 改动范围 |
|---|---|---|
| **校准模式**（默认） | Case 10–18 叙事已够用，缺真实锚点 | 只加 `oss-XXX` + Case 校准表；**不改**主叙事 |
| **升格模式** | OSS 事故比合成场景更典型 | 以 OSS 重写现象/根因；需同步 SOP； Maintainer 评审 |

---

## 8. 相关链接

| 文档 | 用途 |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | 三日校准法 |
| [`cases/_TEMPLATE.md`](cases/_TEMPLATE.md) | 正式 Case 结构 |
| [`oss-incidents/README.md`](oss-incidents/README.md) | 已收录 OSS 索引 |
| [`BACKLOG.md`](BACKLOG.md) | Runtime / 场景待办 |
| [`02-production-extension-packs.md`](../curriculum/02-production-extension-packs.md) | P1–P6 机理 |
| [`CONTRIBUTING.md`](../../CONTRIBUTING.md) | 仓库级贡献约定 |
