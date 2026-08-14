# SOP Case 15：Judge bias 造成误判 regression

> 案例叙事：[case-15](../cases/case-15-judge-bias-false-regression.md)  
> **定位**：生产扩展 Case（求职增强）；主练 P5 Eval Reliability + M4 Judge Calibration。

## 现象

- 新版本 Agent 人工抽样更好，但 eval gate 显示 regression。
- Judge raw output 偏好短答案，惩罚更完整但略长的回答。
- 版本发布被阻塞，团队争论是模型退化还是评测器坏了。

## 根因

1. **MET**：LLM-as-Judge 未与 human label 校准。
2. **REL**：Eval rubric / dataset 变更未版本化，baseline 与 judge 行为漂移。
3. **M4**：gate 只看 pass rate，没有区分真实 regression 与 judge false negative。

## 系统等价物

等价于 CI 测试框架本身有 flaky / biased test：被测代码可能没坏，质检仪先坏了。

## 故障响应 SOP

| 阶段 | 时间 | 动作 |
|---|---|---|
| 观察 | 5 min | 对比 gate result、human sample、judge raw output、dataset/rubric version |
| 隔离 | 10 min | 暂停自动 promote；切人工 review；保留候选版本不立即 rollback |
| 定位 | 30 min | 判断 judge bias、rubric drift、dataset stale、invalid JSON、样本波动 |
| 修复验证 | 1 h | 建 calibration set；重跑 pairwise eval；统计 judge-human disagreement |
| 复盘 | 全天 | 更新 Judge rubric、dataset changelog、CI gate fail-closed 策略 |

## 监控

| 层 | 指标 |
|---|---|
| Eval | `judge_parse_error_rate`、`judge_human_disagreement_rate` |
| Dataset | dataset version、rubric version、sample bucket |
| Gate | pass rate、confidence interval、pairwise win rate |
| Release | candidate blocked reason、manual override reason |

## 回滚预案

1. 不因单次 judge regression 直接删除候选版本。
2. 若 judge 输出格式异常，gate fail closed，先修评测器。
3. 若 judge-human disagreement 高，转人工抽样 + pairwise eval。
4. 校准后重跑 gate，再决定 rollback / promote。

## 我的项目映射

（填写：calibration set、human labels、judge raw output、dataset/rubric version）
