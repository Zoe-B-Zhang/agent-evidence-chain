# M2 精选 Issue（第 2 周）

> 索引：[tutor/README.md](../tutor/README.md) · 知识工程点：[knowledge.md](knowledge.md)

## 三层分工

| 层 | 放在哪 | Learner 做什么 |
|---|---|---|
| **L2 · 跑** | **本文件 Runtime 命令** | 复制命令 → 看 **该 Issue 专用** `trace.json` |
| **L2 · 写** | **`module-02-day2.md`** | 机制表 + TraceEvent 释义（引用本次 trace） |
| **L3** | 本文件 L3 扩展 | 改 runtime 后再跑同一命令复验 |

---

## 命令 ↔ Issue（一条命令只验一个 Issue）

在 `TrackARuntime/` 下执行。

| Issue | 命令 | trace / 结果 | 必须看到 |
|---|---|---|---|
| **I01 #7355** | `python cli.py run --task "fix failing test"` + 读 `_timeouts` | `m1_m2/evidence/<run_id>/trace.json` | `docker_exec`、`run_tests`；Day2 写 tier 设计 |
| **I02 #8448** | **`python cli.py demo-no-output-hang`** | **`m1_m2/evidence/m2-8448-demo/trace.json`** | Event1 `pending`；Event2 `stalled` |
| **I03 schema** | 见下方 I03（单测或非法参数调用） | 测试输出 / 拒绝 error | schema 校验失败信息 |
| **I04 HITL** | `python cli.py run --task "hitl" --require-hitl` | CLI Fatal / trace | HITL / 未确认拒绝 |
| **I05 Case 12** | 阅读 [Case 12](../case-library/cases/case-12-indirect-prompt-injection-tool-abuse.md) + [SOP](../case-library/sops/sop-case-12-indirect-prompt-injection-tool-abuse.md) | policy 决策设计 | untrusted content 不能直接授权 tool call |
| **I06 Case 17** | 阅读 [Case 17](../case-library/cases/case-17-secret-leakage-through-tool-trace.md) + [SOP](../case-library/sops/sop-case-17-secret-leakage-through-tool-trace.md) | data boundary 设计 | secret 不进 prompt / provider / trace |
| **I07 Case 18** | 阅读 [Case 18](../case-library/cases/case-18-approval-fatigue-destructive-action.md) + [SOP](../case-library/sops/sop-case-18-approval-fatigue-destructive-action.md) | HITL UX 设计 | approval fatigue 需要分级与撤销 |

> **I02 不是** `fix failing test`，也**不是** allowlist。

---

## M2-I01 主修 — timeout 分桶（#7355）

| 项 | 内容 |
|---|---|
| Issue | [Cline #7355](https://github.com/cline/cline/issues/7355) |
| Day3 PR | [PR #9159](https://github.com/cline/cline/pull/9159) |
| K 点 | M2-K04, M2-K05（过早切） |
| **L2 命令** | 读 `tool_executor._timeouts` + `python cli.py run --task "fix failing test"` |
| **Day2 交付** | Issue 1 机制表「超时」行 + long-running tier 设计；注明 **配置有、call 路径未 enforce** |
| **L2 Pass** | 能指读四个 tool 秒数；能讲 loop trace ≥3 条 event |
| **L3 扩展** | `resolve_timeout()` + enforce |

---

## M2-I02 主修 — 无输出 hang（#8448）

| 项 | 内容 |
|---|---|
| Issue | [Cline #8448](https://github.com/cline/cline/issues/8448) |
| K 点 | M2-K05（永不切）、M2-K02（trace 证据） |
| **L2 命令** | **`python cli.py demo-no-output-hang`** |
| **代码路径** | `cli.cmd_demo_no_output_hang` → hang 演示路径 |
| **Day2 交付** | 机制表 + TraceEvent 契约表 **引用 `m2-8448-demo/trace.json`** |
| **L2 Pass** | Event1：`completion: pending` · Event2：`completion: stalled` |
| **L3 扩展** | 对齐 Cline backgroundExec / idle timeout |

```powershell
cd TrackARuntime
python cli.py demo-no-output-hang
Select-String -Path m1_m2/evidence/m2-8448-demo/trace.json -Pattern "pending|stalled"
```

**对照 Issue 1**：#7355 = 切太早；#8448 = 永不切 → observe 需要 **tier 下界 + idle/stalled 上界**。

---

## M2-I03 扩展 — Schema 校验拒绝

| 项 | 内容 |
|---|---|
| 类型 | Runtime 能力练习（非单一 OSS Issue） |
| K 点 | M2-K03 |
| **L2 命令** | `python -m unittest tests.test_tool_executor -v`（关注 schema 相关用例）；或阅读 `validate_schema` + 故意缺必填字段调用 |
| **L2 Pass** | 能说明非法 args **不进 handler**；指出 `ToolSpec.parameters` 位置 |
| **L3 扩展** | 为某 tool 增加 enum/pattern 约束并补单测 |

---

## M2-I04 扩展 — HITL 拦截危险工具

| 项 | 内容 |
|---|---|
| 类型 | Runtime 能力练习 |
| K 点 | M2-K03 |
| **L2 命令** | `python cli.py run --task "hitl check" --require-hitl` |
| **预期** | `docker_exec`（`dangerous`）因缺少 `confirmed=True` 被拦截（Fatal / 拒绝路径） |
| **L2 Pass** | 口述 HITL 与 allowlist 差异：白名单内仍可能需确认 |
| **L3 扩展** | 交互式确认回调（当前仅为 `confirmed` 标志 stub） |

---

## M2-I05 生产扩展 — 间接 Prompt Injection 越权工具调用

| 项 | 内容 |
|---|---|
| Case | [Case 12](../case-library/cases/case-12-indirect-prompt-injection-tool-abuse.md) |
| SOP | [sop-case-12](../case-library/sops/sop-case-12-indirect-prompt-injection-tool-abuse.md) |
| K 点 | M2-K06, M2-K07, M4-K09 |
| **学习任务** | 把外部网页 / 文档 / issue 内容标为 `untrusted content`，说明它为什么不能直接授权 tool call |
| **L2 Pass** | 能口述 allowlist、schema、HITL 与 policy engine 的分工：白名单解决“能不能调用”，policy 解决“此刻是否被授权调用” |
| **L3 扩展** | 为 tool call 增加 source provenance 与 policy decision 记录；把 Case 12 加入 security eval |

---

## M2-I06 生产扩展 — Secret 泄露进入 trace/provider

| 项 | 内容 |
|---|---|
| Case | [Case 17](../case-library/cases/case-17-secret-leakage-through-tool-trace.md) |
| SOP | [sop-case-17](../case-library/sops/sop-case-17-secret-leakage-through-tool-trace.md) |
| K 点 | M2-K08, M5-K05 |
| **学习任务** | 设计 data classification：secret、PII、tenant data、provider-bound data；定义哪些字段不能进入 trace/provider |
| **L2 Pass** | 能解释 trace 也是泄露面；secret detector、redaction、provider-bound policy 分别拦哪一层 |
| **L3 扩展** | 为 `TraceEvent` 增加 redacted attribute policy；为 tool output 增加 data_class 标记 |

---

## M2-I07 生产扩展 — Approval fatigue 与破坏性动作

| 项 | 内容 |
|---|---|
| Case | [Case 18](../case-library/cases/case-18-approval-fatigue-destructive-action.md) |
| SOP | [sop-case-18](../case-library/sops/sop-case-18-approval-fatigue-destructive-action.md) |
| K 点 | M2-K06, M2-K09, M5-K06 |
| **学习任务** | 区分低风险确认、高风险确认、不可自动确认动作，设计 approval granularity |
| **L2 Pass** | 能解释为什么“更多确认弹窗”不等于更安全：确认疲劳会降低真正危险动作的拦截率 |
| **L3 扩展** | 为 destructive tool 增加 dry-run、diff preview、undo / rollback 证据 |

---

## 选修（非主修 Issue）

| 场景 | 命令 | 用途 |
|---|---|---|
| M2-K01 allowlist | `python cli.py demo-allowlist --tool rm_rf` | 越权拒载 |
| 真实只读工具 | 读 `tests/test_tool_executor.py` / 自建临时文件调用 | **无独立 Issue**（见 knowledge 标注） |

---

**主修仍为 I01–I02**；I03–I04 为 Phase B 后边界补强练习；I05–I07 为生产扩展 Case，用于面试追问 Tool Policy / Data Boundary / HITL UX。
