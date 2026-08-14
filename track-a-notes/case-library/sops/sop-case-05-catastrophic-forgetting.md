# SOP Case 5：微调「灾难性遗忘」

> 案例叙事：[case-05](../../case-library/cases/case-05-catastrophic-forgetting.md)

## 现象

专项能力提升，通用能力显著下降。

## 根因

微调数据分布单一；评估集缺通用能力项。

## 系统等价物

专项优化压垮共享模块。

## 故障响应 SOP

| 阶段 | 时间 | 动作 |
|---|---|---|
| 观察 | 5 min | 对比专项 vs 通用 eval |
| 隔离 | 10 min | 停止新模型全量 |
| 定位 | 30 min | 检查训练集构成与 eval 覆盖 |
| 修复验证 | 1 h | 回滚基座；混合数据重训（若岗位需要） |
| 复盘 | 全天 | 部署门禁：通用能力阈值 |

## 监控

- 模型层：多任务 eval dashboard

## 回滚预案

上一版基座/adapter 立即切回。

## 我的项目映射

概念级：Prompt/模型路由切换（见 ModelAccessRouter）
