# Case 18 — Approval fatigue 导致危险操作被批准

| 字段 | 值 |
|---|---|
| **ID** | case-18 |
| **主类** | **SEC** |
| **次类** | CTL |
| **标签** | hitl, approval, destructive-action, ux, goal-change |
| **关联模块** | M2 工具边界、M5 运维、M1 goal change |
| **M5 深度** | 扩展（求职增强） |
| **SOP** | [sop-case-18](../sops/sop-case-18-approval-fatigue-destructive-action.md) |
| **TrackARuntime** | `--require-hitl` 已有机制；approval transcript / undo 为概念级 |
| **添加日期** | 2026-08-08 |
| **来源** | 合成生产事故 + HITL 产品设计模式 |
| **当前状态** | 正式草稿（SOP 已落地；Runtime 可选） |
| **补强 K 点** | M2-K09 HITL UX；M5-K06 Incident Feedback Loop；M1-K09 Goal Change |
| **目标扩展包** | P3 Security + P6 Observability |

## 场景

Agent 助手在完成复杂任务时，每一步都弹 approval。用户为了推进流程连续点击 approve，最终批准了一个 destructive tool call，删除了生产配置。

## 现象

1. 低风险与高风险确认混在同一确认流中。
2. 用户形成连点 approve 习惯，危险操作没有额外解释或 diff preview。
3. 事故后无法从 approval transcript 还原用户当时看到了什么、是否理解影响范围。

## 根因（非表面）

HITL 被当成“弹确认框”，没有风险分级、上下文解释、可撤销设计和 approval budget。安全机制被 UX 反噬。

## 缺失的工程 invariant

HITL 必须按风险分级触发，并让用户理解后果；高危操作需要可撤销或额外审批。

## 工程解法

- Approval granularity：approve plan / step / tool / diff。
- Risk-based prompts：只对高风险操作打断。
- Tool explanation：说明为什么需要、影响范围、回滚方式。
- Destructive action 需要 dry-run / diff preview / undo。
- 记录 approval transcript。
- 用户 reject / edit 后，控制面进入 `replan_requested`，不得继续旧 plan。

## 系统等价物

安全系统把所有操作都弹同样的确认框，最终用户忽略真正危险的 root 权限操作。

## 初级 vs 高级认知

**初级**：给危险工具多弹几次确认框。

**高级（目标）**：HITL 是风险分级审批流；高危操作需要 diff preview、dry-run、undo、approval transcript，reject/edit 要触发 M1 replan。

## 对应 Issue / PR / 校准来源

| 来源 | 链接 | 现象 | 修复点 | 可抽象的工程规则 |
|---|---|---|---|---|
| HITL 产品设计模式 | 本 Case | 低风险与高风险确认混在一起，用户无脑 approve | risk tier、approval budget、undo | 更多弹窗不等于更安全 |
| TrackARuntime 教学机制 | `python cli.py run --task "hitl check" --require-hitl` | 已有 dangerous tool 拦截 stub | 扩展 approval transcript / dry-run / reject replan | HITL 机制要和 UX、审计、控制面联动 |

## What / Why / How 抽取

| K 点 | What | Why | How | Prove |
|---|---|---|---|---|
| M2-K09 | HITL UX = 风险分级、解释、可撤销的人机审批流 | 无脑确认会让安全机制失效 | risk tier + explanation + approve/edit/reject + undo | Case 18 |
| M1-K09 | Goal Change = 用户拒绝/修改后控制面重规划 | reject 后不能继续旧 plan | approval_reject → replan_requested | transcript |
| M5-K06 | Incident Feedback Loop = 事故后更新 approval policy | 只恢复数据不改审批会复发 | postmortem → policy/rule update | SOP |

## 监控与回滚

- **最先亮的监控层**：approval count per run、approval burst、destructive approval rate、reject/edit rate、approval transcript completeness。
- **隔离 / 回滚**：禁用 destructive tool 或强制 dry-run；恢复已破坏配置；收紧 risk tier 后再恢复自动审批流。

## SOP 摘要

| 阶段 | 动作 |
|---|---|
| 观察 | 查看 approval transcript、tool risk tier、用户点击路径 |
| 隔离 | 禁用 destructive tool；启用 dry-run only |
| 定位 | 判断是确认过多、解释不足、缺 undo、risk tier 错 |
| 修复验证 | 更新 approval policy；回放同任务看是否 require edit/reject |
| 复盘 | 加 approval fatigue scenario 和 UX checklist |

## Runtime / Evidence 映射

| 类型 | 当前状态 |
|---|---|
| 已有证据 | M2 HITL 已有机制；UX 设计未覆盖 |
| 已生成文档 | `case-18-approval-fatigue-destructive-action.md` 与 [SOP](../sops/sop-case-18-approval-fatigue-destructive-action.md) 已生成 |
| 可选 Runtime | approval transcript demo |
| 面试证明 | HITL risk tier table |

## 在本体系中的位置

- **模块**：M2 HITL UX 为主，M1 Goal Change 与 M5 incident feedback 辅助。
- **Issue / runtime 任务**：M2-I07；approval transcript demo 尚未实现。
- **关联 Case**：与 [Case 12](case-12-indirect-prompt-injection-tool-abuse.md) 同属 tool safety，Case 12 管外部注入，Case 18 管 human approval 失效。

## 面试口述路径

60s：HITL 不是弹框，而是风险分级审批流。  
2min：确认疲劳 → 危险操作被批准 → dry-run/diff/undo/risk tier 修复。  
5min：画 plan preview、tool explanation、approve/edit/reject、M1 replan。

## Prove 附表：HITL 现状 vs 目标

| 能力 | TrackARuntime 现状（`--require-hitl`） | Case 18 目标 |
|---|---|---|
| dangerous tool 拦截 | ✅ 需 `confirmed=True` | ✅ |
| risk tier 分级 | ❌ 所有 dangerous 同级 | low / medium / high / destructive |
| diff / dry-run preview | ❌ | destructive 必须 preview |
| approval transcript | ❌ | 记录用户看到的解释与点击路径 |
| reject → replan | ❌ | `approval_reject` → `replan_requested`（M1-K09） |
| undo | ❌ | 高危操作可撤销窗口 |

## Prove 附表：approval transcript 示例

```text
Run r-8f2a | Task: deploy config fix
[1] read_file config.yaml        → auto-approved (risk: low)
[2] run_tests                    → auto-approved (risk: low)
[3] docker_exec rm -rf /prod/... → PROMPT: "Delete prod config?"
    User: APPROVE (3.2s after [2], burst approve pattern)
[4] RESULT: destructive action executed — incident opened
```

复盘：步骤 3 应与 1–2 **不同风险 tier**；应展示 diff + 要求输入 `DELETE` 确认或 dry-run。

## Prove 附表：HITL risk tier table

| tier | 示例 tool | 打断方式 | 用户动作 |
|---|---|---|---|
| low | `read_file`, `grep` | 无 | — |
| medium | `run_tests` | 可选 batch approve | approve plan |
| high | `docker_exec`（非 prod） | 逐步确认 + 解释 | approve / edit |
| destructive | 删配置、写 prod | diff + dry-run + 二次确认 | approve + undo 窗口 |

**现有命令**：`python cli.py run --task "deploy fix" --require-hitl`（仅演示 `confirmed` 门禁，不含 tier/transcript）。

## 学习记录（自填）

- **Day1 根因猜测**：
- **与 PR/解法对照差距**：
- **口述练习日期 / 用时**：


