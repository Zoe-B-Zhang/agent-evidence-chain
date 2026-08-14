# M3 Day2 — 开方

**日期**：________

> **导师读法**：Day2 在 Day1 根因基础上设计 **Harness 机制表 + Runtime 映射**。Issue 1 下方为完整示范；Issue 2 留空供 Learner 按同结构填写。

## Issue 1 工程化解法（#1491 · re-ask 边界）

**方案一句话**：re-ask 预处理对空 fail_results 安全 short-circuit → max re-ask counter 防无界循环 → 单元测试锁定 default 路径

| 机制 | 我的方案（Issue 1 示范） |
|---|---|
| re-ask 预处理 | `first_fail_result = fail_results[0] if fail_results else None`；空则 **return FieldReAsk unchanged**，不 crash（对齐 PR #1492） |
| max re-ask | Harness 层 `MAX_REASKS=3`（概念）；达上限 → `on_fail=refrain` 或 fallback template，**不再调用 LLM**（M3-K06 L3） |
| fail_results 契约 | Schema 层：`fail_results: Optional[List]` 默认 `[]` 而非 None；Pydantic validator 统一 coerce（M3-K03 第 1 层） |
| 可测试性 | 单测 `test_sub_reasks_with_fixed_values_none_fail_results`：无 fail_results 的 FieldReAsk **不 raise** |
| Trace / 审计 | re-ask 每次 increment 写入 harness history（guardrails 已有 `guard.history`）；空 fail_results 记 `reask_skipped: true` |

**re-ask 安全路径设计（M3-I01 Runtime 任务 · 文档层）**

```text
on_validation_fail(field)
├── fail_results empty?  → return unchanged ReAsk (不索引 [0])
├── reask_count >= MAX   → refrain / fixed_output fallback
└── else                 → sub_reasks_with_fixed_values + LLM re-ask
```

**Runtime 任务（issues.md 绑定）**：

```powershell
cd TrackARuntime
# 1. 阅读 Harness 交付链（对照 re-ask 应有上界）
#    m3/pipeline.py
#    m3/guardrails.py

# 2. 文档记录：max re-ask 应如何实现（可写在 day2 本表下方）
#    - counter 放 pipeline 还是 guardrails 层？
#    - 达上限时 action: rollback_to_v1 还是 refrain？
```

**预期证据**（L2 · 设计层）：

- 能口述 #1491 fix 一行 diff 的逻辑
- 能说明「为何 test 必须在 merge 前存在」——防止 default 再次变回 crash
- Day2 表格 = M3-K06 L2 证据

**与 TrackARuntime 映射（Issue 1）**

| 文件 | 现状 | Day2 应理解什么 |
|---|---|---|
| `guardrails.py` | 仅 formality 护栏 | 护栏失败 → 类似 re-ask 失败，应 **有界** 而非无限重试 |
| `pipeline.py` | v1/v2 + gray + rollback | `run_harness` 是 **交付决策点**；re-ask counter 应对标 `action` 字段 |
| `prompts/*.yaml` | 版本 + changelog | schema 默认值应 explicit，避免 None/[] 混用（#1491 同构） |

---

## Issue 2 工程化解法（Case 2 · Prompt 蝴蝶 · Learner 自填）

**方案一句话**：（一句概括 v2 灰度 + formality 护栏 + rollback）

| 组件 | 我的方案 |
|---|---|
| prompts/v1.yaml vs v2.yaml | |
| 变更日志 | |
| 灰度比例 | |
| 护栏指标（如风格正式度） | |
| 回滚触发条件 | |
| ModelAccessRouter（timeout/retry/circuit） | |

**Runtime 任务（issues.md M3-I02 绑定）**：

```powershell
cd TrackARuntime
python cli.py harness --prompt v2 --gray-percent 10
# 打开 m3/evidence/harness-report.json，对照下列字段填写 Issue 2 表格
```

> **导师提示（Issue 2 Day2 填空顺序）**
>
> 1. 先读 `v1.yaml` / `v2.yaml` diff + v2 `changelog` 行（M3-K02）。
> 2. 填 **护栏指标**：`style_formality_min` v1=0.7 vs v2=0.4；mock 输出为何 score=0.0（M3-K03）。
> 3. 填 **灰度 + 回滚**：gray 10% + `guardrail_ok: false` → `action: rollback_to_v1`（M3-K04/K05）。
> 4. **ModelAccessRouter 行**（可选 L3）：timeout/retry/circuit 类比 M2 tool tier——模型 API 也要有熔断，防止 re-ask 风暴拖垮上游。
> 5. **故意破坏实验**（见下方）：把 v2 的 `style_formality_min` 改到 0.9，观察是否仍 rollback——理解阈值与输出分布关系。

---

## 解法设计（总表 · 两日 Issue 合并视图）

| 机制 | Issue 1 (#1491) | Issue 2 (Case 2) |
|---|---|---|
| 版本/契约 | fail_results 默认 [] | prompt v1/v2 + changelog |
| 边界安全 | 空列表不索引 | formality 阈值 + mock 输出 |
| 有界循环 | max re-ask | gray_percent 限流 |
| 失败动作 | return unchanged | rollback_to_v1 |
| 证据 | unit test | harness-report.json |

## 故意破坏实验

- **Issue 1 示范**：若把 fix 行改回 `fail_results[0]`，单测应 fail——证明 test 是回归门禁。
- **Issue 2（Learner）**：如何将 v2 改坏以触发回滚：
  - 改 `MOCK_OUTPUTS["v2"]` 为更夸张文案；或
  - 把 v2 `style_formality_min` 提高到 0.95；或
  - 设 `gray-percent 0` 观察 promote 路径（对比 gray 失败）。

## harness-report 契约确认

见 [`TrackARuntime/m3/pipeline.py`](../../TrackARuntime/m3/pipeline.py)：

| 字段 | 含义 | Issue 1 类比 | Issue 2 示例 |
|---|---|---|---|
| `prompt_version` | 被测版本 | N/A | `"v2"` |
| `gray_percent` | 灰度比例 | N/A | `10` |
| `guardrail_ok` | 护栏是否通过 | re-ask 成功路径 | `false` |
| `formality_score` | 护栏分数 | N/A | `0.0` |
| `action` | 交付决策 | refrain 类比 | `"rollback_to_v1"` |
| `rollback_reason` | 回滚原因 | empty fail_results | `"guardrail_failed_during_gray"` |
