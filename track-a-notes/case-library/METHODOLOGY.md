# 校准方法论 — 三日挑战与系统思维

> 将 AI 故障当作 **概率环境下的分布式系统异常** 来分析，而不是「模型魔法问题」。

## 三日校准法（每项能力 / 每个 OSS Issue 复用）

| 天 | 动作 | 产出 |
|---|---|---|
| **Day1 找茬** | 读 Issue/PR **只看现象**，写根因猜测 + **系统等价物** | `module-XX-day1.md` |
| **Day2 开方** | 设计 **不依赖换模型** 的工程解法 + 监控/回滚点 | `module-XX-day2.md` |
| **Day3 对照** | 读已 Merge 的 PR/设计，对比差距，更新认知 | `module-XX-day3.md` |
| Day4–7 | 在 **TrackARuntime** 上实现最小垂直切片 | 代码 + trace/eval |
| Day8 | 原理 + 自己的例子 + bad case 口述 | `module-XX-exit.md` |

**判据**：

- 你的 Day2 思路与最终 PR **逻辑一致** → 认知无大偏差，可进面试讨论。
- PR 更简洁 → 免费校准，更新笔记即可。

## 认知偏差消除（Case 库裸测）

对 [`cases/`](cases/) 中每个 Case 完成三步：

### 第一步：写「系统等价物」

把 AI 术语翻译成你熟悉的系统概念。示例：

| Case | 系统等价物 |
|---|---|
| 1 RAG 幻觉 | 分布式读只拿到半份数据却假装完整 |
| 4 时间穿越 | MVCC/版本失效，旧版本被误读 |
| 6 注入 | SQL 注入 + 会话状态污染 |
| 8 幸存者偏差 | 未分层随机的实验设计 |

### 第二步：画监控分层

见 [`../module-05/monitoring-layers.md`](../module-05/monitoring-layers.md)。每层至少填 **1 个可告警指标**。

### 第三步：故障演习

任选 1 Case，按 SOP 五段计时模拟值班（可只写时间线，不写代码）：

1. 观察（5 min）  
2. 隔离（10 min）  
3. 定位（30 min）  
4. 修复验证（1 h）  
5. 复盘（全天）

## 自我评估标尺（每个 Case 文末也有）

| 层级 | 典型反应 |
|---|---|
| **初级** | 换模型、改一句 Prompt、加「不知道就说不知道」 |
| **高级（目标）** | 改检索/交付/监控/回滚/实验设计；用 **固定 eval + 护栏指标** 证明修复 |

## 与 Track A 模块的关系

```
Case Library (what can go wrong)
    ↓ 口述 + SOP
Module 1–4 (Agent / Tool / Harness / Eval) ← TrackARuntime 证据
    ↓
Module 5 (映射 + 监控分层)
    ↓
Module 6 (portfolio + 面试)
```

RAG **非主轴**；Case 1/4 以概念 + eval 设计满足面试即可。
