# SOP Case 18：Approval fatigue 导致危险操作被批准

> 案例叙事：[case-18](../cases/case-18-approval-fatigue-destructive-action.md)  
> **定位**：生产扩展 Case（求职增强）；主练 P3 HITL UX + P6 incident feedback。

## 现象

- Agent 每一步都要求确认，用户形成连续 approve 习惯。
- 高危 destructive tool call 混在低风险确认流中被批准。
- 事故后难以解释用户批准时看到了什么、是否理解影响范围。

## 根因

1. **SEC**：HITL 被简化成弹窗，没有 risk tier、tool explanation、diff preview。
2. **CTL**：用户 reject/edit 后控制面没有明确 replan 状态。
3. **M5**：缺少 approval transcript 与 approval fatigue 复盘路径。

## 系统等价物

等价于安全系统把所有操作都弹同样的确认框，最终用户忽略真正危险的 root 权限操作。

## 故障响应 SOP

| 阶段 | 时间 | 动作 |
|---|---|---|
| 观察 | 5 min | 查看 approval transcript、tool risk tier、确认频率、用户点击路径、destructive diff |
| 隔离 | 10 min | 禁用 destructive tool；切 dry-run only；要求二次审批或管理员确认 |
| 定位 | 30 min | 判断确认过多、解释不足、risk tier 错、缺 undo、reject 后未 replan |
| 修复验证 | 1 h | 更新 approval policy；回放同任务确认是否变成 edit/reject/dry-run |
| 复盘 | 全天 | 新增 approval fatigue scenario、UX checklist、undo/rollback 证据要求 |

## 监控

| 层 | 指标 |
|---|---|
| HITL | approval count per run、approval burst、reject/edit rate |
| Tool Risk | destructive approval rate、dry-run coverage |
| Control Plane | approval_reject → replan count |
| Audit | approval transcript completeness、rollback token present |

## 回滚预案

1. 暂停 destructive tool，或强制 dry-run + diff preview。
2. 对已执行破坏性操作执行 rollback / restore。
3. 收紧 risk tier：低风险批量确认，高风险单独解释和二次审批。
4. 恢复前必须保留 approval transcript 与 undo 路径。

## 我的项目映射

（填写：risk tier 表、approval transcript 示例、dry-run/diff/undo 设计）
