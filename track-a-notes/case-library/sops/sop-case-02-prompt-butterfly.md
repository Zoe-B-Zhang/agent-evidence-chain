# SOP Case 2：Prompt「蝴蝶效应」

> 案例叙事：[case-02](../../case-library/cases/case-02-prompt-butterfly.md)

## 现象

小改动 Prompt 后输出风格或满意度断崖下跌。

## 根因

语义偏移改变输出分布；无版本化、无 A/B、无护栏指标。

## 系统等价物

配置热更新无灰度、无回归测试。

## 故障响应 SOP

| 阶段 | 时间 | 动作 |
|---|---|---|
| 观察 | 5 min | 对比 Prompt diff、满意度分桶、输出样例 |
| 隔离 | 10 min | 灰度流量降至 0 或切回 v1 |
| 定位 | 30 min | 检查 eval 是否覆盖语义偏移维度 |
| 修复验证 | 1 h | 小流量 A/B + 风格向量/正式度评分 |
| 复盘 | 全天 | Prompt 变更必须带 changelog + 门禁 |

## 监控

- 模型层：风格/正式度分数
- 业务层：满意度、投诉关键词

## 回滚预案

`prompts/v1` 全量；废弃 v2 直至 eval 通过。

## 我的项目映射

见 `TrackARuntime`：`python cli.py harness --prompt v2 --gray-percent 10` → rollback_to_v1
