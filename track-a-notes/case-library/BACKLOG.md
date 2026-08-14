# Case Library / 生产扩展 — 尚未完成工作清单

> 本文档是**改进待办真源**：新贡献者请先读根目录 [`USAGE.md`](../../USAGE.md) 了解如何用，再从这里认领任务。  
> 已完成的一致性清扫见文末「2026-08-09 清扫记录」。

---

## 优先级说明

| 级别 | 含义 |
|---|---|
| **P0** | 阻塞一致性或误导学习者；应优先修 |
| **P1** | 增强 Prove / 面试价值；有明确落点 |
| **P2** | 体验优化或扩展阅读材料更新 |

---

## P0 — 已知缺口（影响「能证明」）

### Runtime：规划 CLI 尚未实现

以下命令在 Case / 计划中出现过，**`TrackARuntime/cli.py` 中不存在**（见 `AGENTS.md`）：

| 规划命令 | 关联 Case | 状态 |
|---|---|---|
| `demo-llm-gateway --failure rate_limit` | Case 10 | 未实现 |
| `eval-rag --scenario stale-index` | Case 11 | 未实现（**S21 已在 `scenarios.json` 落地**） |
| `demo-tool-policy --attack indirect-prompt-injection` | Case 12 | 未实现 |
| `demo-runtime-queue --simulate-worker-death` | Case 13 | 未实现 |
| memory store stub | Case 14 | 未实现 |
| judge calibration stub（启用 Judge + 校准集） | Case 15 | 未实现（`judge.py` 默认 `DisabledJudge`） |
| `demo-observability --export otel-json` | Case 16 | 未实现 |
| redaction check demo | Case 17 | 未实现 |
| approval transcript demo | Case 18 | 未实现 |

**最小改进建议**：每 Wave 选 1 个 demo，优先 Wave 1（Gateway stub / policy deny mock / 已有 eval 场景增强）。

### M4：S23 `RETRIEVAL_OK_GEN_FAIL`（oss-9415）未落地

| 项 | 现状 |
|---|---|
| **S21** | 已用于 **Case 11** → `STALE_INDEX`（stale index） |
| **S23**（计划） | 预留给 **oss-9415** → `RETRIEVAL_OK_GEN_FAIL`（检索 OK、生成错） |
| `failure_taxonomy.md` | 有 `STALE_INDEX`、`JUDGE_BIAS`；**无** `RETRIEVAL_OK_GEN_FAIL` |

**改进任务**：

1. 在 `scenarios.json` 增加 **S23**（`RETRIEVAL_OK_GEN_FAIL`，`category: generation` 或 `mixed`）。
2. 在 `failure_taxonomy.md` 增加对应行。
3. 更新 `oss-9415` 与 `module-04-day2/day3` 学习者笔记中的 scenario 示例。
4. 跑 `eval` 更新 `evaluation-report` 与 CI baseline（若新增 fail 场景需重算通过率）。

### M4：`trace_eval` 未接入 `run_eval` 主路径

- 库代码存在：`m4/trace_eval.py`
- `runner.run_eval` **未调用** → evaluation-report 无 loop 类指标  
- 见 `module-04/issues.md` M4-I01 L3

### 测试：`test_tool_executor` 失败

- `python -m unittest discover tests` 当前 **42 tests，1 error**（`test_read_file_returns_mock_content` KeyError）
- 简历片段示例 — 需重跑后更新 [`portfolio/examples/resume-snippet.example.md`](../../portfolio/examples/resume-snippet.example.md)（个人版在 `portfolio/personal/`）

---

## P1 — Case / SOP 内容增强

| 任务 | 说明 | 状态 |
|---|---|---|
| SOP「我的项目映射」示例 | `sops/sop-case-10` … `18` 的填写区均为空白，可加 1 条示例 | 待办 |
| Case 13 结构 | Prove 附表与口述路径顺序可与其他 Case 统一 | ✅ 2026-08-09 删除重复 Prove |
| Case 14 结构 | Prove 附表目前在「面试口述路径」之后，可前移 | 待办 |
| 根目录 `portfolio/README.md` | 链到 demo-script §4 + Case 10–18 | ✅ |
| `resume-snippet.md` | 22 场景 / 45.5% / baseline 0.45 | ✅ |

---

## P2 — 文档与导出物（低优先级）

| 任务 | 说明 | 状态 |
|---|---|---|
| `curriculum/sysknowledge.html`、`map.html`、`map/pdf` | 导出快照仍写 CI `baseline 0.5`；改源 Markdown 后重新导出 | 待办 |
| `module-04/module-04-day2.md` 历史填空 | 已加 2026-08 勘误（S21/S23、22 场景、0.45） | ✅ |
| `case-library/supplements/portfolio-evidence-standards.md` | 22 场景 + 真源链接 | ✅ |
| `track-a-notes/portfolio/` | 已合并入根 `portfolio/`；删除重复 `demo-script` | ✅ 2026-08-10 |

---

## 可选 Runtime 扩展路线图（建议顺序）

```text
Wave 1 证明链
  1. S23 RETRIEVAL_OK_GEN_FAIL（补 oss-9415 闭环）
  2. rate_limiter / model_router 与 Case 10 metrics 字段联动
  3. tool policy deny mock（Case 12）

Wave 2 证明链
  4. checkpoint + lease 教学扩展（Case 13）
  5. memory store stub（Case 14）

Wave 3 证明链
  6. trace redaction 示例（Case 17）
  7. approval transcript JSON 字段（Case 18）
```

---

## 2026-08-09 一致性清扫记录（已完成）

| 项 | 处理 |
|---|---|
| S21 语义 | 定为 `STALE_INDEX` / Case 11；oss-9415 改为指向 S23 计划 |
| Eval 数字 | 22 场景、10 pass、45.5%、CI baseline **0.45** → 真源见 `TrackARuntime/README.md` |
| `failure_taxonomy.md` | 增加 `STALE_INDEX`、`JUDGE_BIAS` |
| `scenarios.json` | S21、S22 落地 |
| `tests/test_runner.py`、`.github/workflows/ci.yml` | 对齐 22 场景与 baseline 0.45 |
| `portfolio/demo-script.md` | 22 场景 + P1 扩展 §4 |
| `TrackARuntime/README.md` | 新增 M4 Eval 数字真源节 |
| `KNOWLEDGE-MAP.md`、`curriculum/00`、`01-course`、`module-04/*` | baseline **0.45**、22 场景、S21/S23 语义 |
| `portfolio/examples/resume-snippet.example.md`、`portfolio/README.md` | 22 场景 / 0.45 |
| `case-08`、sop-case-08 | baseline 0.45 |
| 本库 | 使用指引迁至根目录 [`USAGE.md`](../../USAGE.md)；本目录保留 `BACKLOG.md` |

---

## 如何贡献一条改进

1. 从本文件 **P0/P1** 认领一项。  
2. 若改 `scenarios.json` / taxonomy / CI baseline，**同步** `TrackARuntime/README.md` Eval 真源表。  
3. 若改 Case 行为，同步 Case 文件 + SOP +（如需要）`module-XX/issues.md`。  
4. 跑 `python -m unittest discover tests` 与 `python cli.py eval --baseline 0.45`。  
5. 在本文件对应条目打勾或移到「清扫记录」。
