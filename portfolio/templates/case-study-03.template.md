# Case Study 03 — 故意注入失败 + Fallback + 回滚

> **模板**：复制到 [`../personal/case-study-03.md`](../personal/README.md) 后填写。**`personal/` 已 gitignore，勿提交公开仓。**

## 注入方式

- [ ] Prompt v2 风格漂移（Case 2）
- [ ] 工具 allowlist 拒绝（Case 6）
- [ ] 模型/router 熔断（Case 7）
- [ ] Eval 门禁失败（Case 8）

## 时间线

| 时间 | 事件 | 系统反应 |
|---|---|---|
| T0 | 灰度 v2 / 危险 tool / ... | |
| T1 | 护栏触发 | |
| T2 | 回滚 / fallback | |
| T3 | 验证恢复 | |

## 证据文件

- harness-report.json（v2 rollback）：`TrackARuntime/m3/evidence/harness-report.json`
- trace.json（allowlist 拒绝 / timeout）：`TrackARuntime/m1_m2/evidence/<run_id>/trace.json`

## 三类失败（招聘方最爱听）

1. **类型**：根因 — 修复
2. **类型**：根因 — 修复
3. **类型**：根因 — 修复

## 面试口述稿

（2 分钟：我们如何让失败可观测、可回滚）
