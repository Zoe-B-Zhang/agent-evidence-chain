# 模块 3 学习指南：Harness 思维

> **导师补充**：知识工程点 `[M3-K01–K06](knowledge.md)` · 精选 Issue `[M3-I01–I02](issues.md)` · 评分 `[rubric.md](rubric.md)`

## 本模块在系统中的位置

| | |
|---|---|
| **生命线** | ③ **配置交付** — Prompt/配置安全发布 |
| **依赖** | M2（理解单次 run trace 后再谈全局配置） |
| **主证据** | `harness-report.json` |
| **体系详述** | [`KNOWLEDGE-SYSTEM.md` §7 M3](../curriculum/00-knowledge-system.md) · [`COURSE.md` 第 3 课](../curriculum/01-course.md) |

## 原理（3 分钟版）

Harness = **AI 行为的交付与可靠性层**，不是模型本身。


| Harness 能力 | 系统等价       |
| ---------- | ---------- |
| Prompt 版本化 | 配置中心 + Git |
| A/B / 灰度   | 特性开关 + 金丝雀 |
| 护栏指标       | SLO 错误预算   |
| 回滚         | 蓝绿发布回退     |
| Fallback   | 熔断器 + 降级服务 |


### 术语注释（上表）


| 系统等价           | 英文                                                 | 含义                                                                                             | M3 / TrackARuntime 对应                                                                                                       |
| -------------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| 特性开关 + **金丝雀** | Feature flag · **Canary release**                  | 新版本先接 **小比例真实流量**，指标正常再放大；异常则只影响小部分并回滚（煤矿「金丝雀探毒」类比）                                            | `gray_percent=10`；`cli.py harness --prompt v2 --gray-percent 10`                                                            |
| **SLO** 错误预算   | **S**ervice **L**evel **O**bjective · error budget | **SLI**=实测指标（如 formality_score）；**SLO**=目标线（如 `style_formality_min`）；**错误预算**=允许失败额度，耗尽应停发布/回滚 | `guardrail_ok: false` → `rollback_to_v1`；连续 fail → `[rollout-state.json](../../TrackARuntime/m3/evidence/rollout-state.json)` lock |
| **蓝绿发布**回退     | **Blue-green deployment** · rollback               | **Blue**=当前线上版，**Green**=候选版；验证通过后一切换流量，出问题 **切回 Blue**（与金丝雀「渐进放量」不同，偏 0↔100% 切换）              | Blue=`v1.yaml`；Green=`v2.yaml`；回退=`action: rollback_to_v1` 或 `harness --watch`                                              |


> 深读：自动 rollback 状态机见 `[study-notes/rollout-auto-rollback.md](../study-notes/rollout-auto-rollback.md)`。

## OSS 阅读清单

1. **guardrails-ai/guardrails**：validator + re-ask loop
2. **System Guardian 蓝图**：`[case-library/supplements/system-guardian-blueprint.md](../case-library/supplements/system-guardian-blueprint.md)`
3. **LangSmith eval docs**：dataset + 版本对比

## 三日校准（导师指定 Issue）


| 天         | 任务                 | 链接                                                                                            |
| --------- | ------------------ | --------------------------------------------------------------------------------------------- |
| Day1 主修 1 | re-ask 边界 crash    | [guardrails #1491](https://github.com/guardrails-ai/guardrails/issues/1491)                   |
| Day1 主修 2 | Case 2 + re-ask 架构 | [Discussion #1454](https://github.com/guardrails-ai/guardrails/discussions/1454) + 本地 v2 demo |
| Day3 对照   | fail_results guard | [PR #1492](https://github.com/guardrails-ai/guardrails/pull/1492)                             |


## 关联 Bad Case

- Case 2：Prompt 蝴蝶效应
- Case 5：模型/配置回滚
- Case 8：A/B 幸存者偏差

## TrackARuntime（主线）

```powershell
cd TrackARuntime
python cli.py harness --prompt v2 --gray-percent 10
python cli.py harness --prompt v1 --gray-percent 0
# 平台 stub 数字：先 run 再看 metrics
python cli.py run --task "fix failing test" --llm mock
# → m1_m2/evidence/<run_id>/metrics-<run_id>.json
```

平台 stub（router/token/cost）**无独立 Issue**，见 [`knowledge.md`](knowledge.md) M3-K01 标注。

见 `[m3/](../../TrackARuntime/m3/)`

## Others

### **1. 「金丝雀」指什么？**

**英文**：**Canary release / Canary deployment**（金丝雀发布）

**含义**：新版本 **先接一小部分真实流量**，指标正常再逐步放大；有问题则只影响这小部分，再回滚。

名字来自煤矿里 **用金丝雀探测毒气**——先让 Canary 探路，死了就说明环境有问题。


| **传统系统**      | **M3 Harness 对应**                        |
| ------------- | ---------------------------------------- |
| 新版本服务先接 5% 用户 | `gray_percent=10`：10% 流量走 `prompt v2`    |
| 特性开关控制谁看到新版本  | Prompt 版本 + 灰度比例                         |
| 指标变差就停扩量      | `guardrail_ok: false` → `rollback_to_v1` |


GUIDE 里 **「A/B / 灰度 → 特性开关 + 金丝雀」** 想表达：

- **特性开关（Feature flag）**：控制「谁用 v1 / 谁用 v2」
- **金丝雀**：不是一次全量，而是 **小流量试跑 + 观察护栏**

和 **A/B 实验** 的关系：A/B 偏 **对比两版谁更好**；金丝雀偏 **先小流量保安全**。Case 8 提醒 A/B 还要看多指标，不能只看单一 KPI。

本地命令：

python [cli.py](http://cli.py) harness --prompt v2 --gray-percent 10

就是 **金丝雀** 的简化 mock：10% 灰度 + 护栏失败则回滚。

---

### **2. SLO 是什么？「错误预算」呢？**

**SLO** = **Service Level Objective**（**服务等级目标**）

表示：**对用户/业务承诺的服务质量下限**，通常是可量化指标，例如：

- 99.9% 请求在 500ms 内完成
- 正式度 score ≥ 0.7 的回复占比 ≥ 95%
- eval `gate_pass` 成功率 ≥ 50%

相关术语（面试常一起出现）：


| **缩写**  | **英文**                  | **含义**                                |
| ------- | ----------------------- | ------------------------------------- |
| **SLI** | Service Level Indicator | **实际测量的指标**（如 P95 延迟、formality_score） |
| **SLO** | Service Level Objective | **目标线**（如 formality ≥ 0.7）            |
| **SLA** | Service Level Agreement | **对外合同**（违约要赔偿；SLO 是内部目标，通常比 SLA 严）   |


**错误预算（Error budget）**：SLO 允许的那部分「失败额度」。

例：SLO 是「99.9% 可用」→ 每月约 **0.1%** 可以失败；预算用完就应 **停发布、回滚、修问题**，而不是继续推 v2。

GUIDE 里 **「护栏指标 → SLO 错误预算」** 在 M3 的映射是：


| **抽象**      | **M3 实例**                                |
| ----------- | ---------------------------------------- |
| SLI         | `formality_score`、长度、敏感词命中率              |
| SLO         | `style_formality_min: 0.7`               |
| 跌破 SLO      | `guardrail_ok: false`                    |
| 错误预算耗尽 / 熔断 | 连续 fail → `rollout-state.json` 里 lock v2 |


护栏不是「感觉 v2 不好」，而是 **用 SLO 式阈值做自动门禁**；超预算就 rollback（见 M3-K03 dashboard）。

---

### **3. 什么是蓝绿发布？英文怎么说？**

**中文**：蓝绿发布  
**英文**：**Blue-green deployment**（也写作 blue/green release）

**做法**：同时维护两套 **完整环境**：


| **环境**       | **角色**                           |
| ------------ | -------------------------------- |
| **Blue（蓝）**  | 当前线上、接 **100% 流量**               |
| **Green（绿）** | 新版本、先 **不接流量或接很少**，验证通过后 **一切换** |


切换通常是 **改路由/负载均衡**，秒级切流量；出问题再 **切回 Blue** → 即 **蓝绿回退（blue-green rollback）**。

和金丝雀的区别：


|      | **金丝雀 Canary**          | **蓝绿 Blue-green** |
| ---- | ----------------------- | ----------------- |
| 流量切换 | **渐进**（1% → 10% → 100%） | **一次性** 0%↔100%   |
| 环境   | 常共用一套，靠开关分流量            | **两套并行**          |
| 回滚   | 减流量 / 关开关               | **指回 Blue**       |


GUIDE 里 **「回滚 → 蓝绿发布回退」** 在 M3 的 **思想对应**（不是真有两套 K8s）：


| **蓝绿概念**    | **TrackARuntime**                                                  |
| ----------- | ------------------------------------------------------------------ |
| Blue = 稳定版  | `prompts/v1.yaml`，`active_version: v1`                             |
| Green = 候选版 | `prompts/v2.yaml`                                                  |
| 切 Green     | promote / 提高 gray                                                  |
| 回退 Blue     | `action: rollback_to_v1` 或 `--watch` 里 `apply_traffic(v1, gray=0)` |


Harness 的 rollback 是 **配置 revert（回到 v1）**，不是 `git revert` 代码；和蓝绿 **「切回已知好版本」** 同构。

---

### **对照表（背 GUIDE 一行时用）**


| **GUIDE 行** | **英文关键词**                | **M3 一句话**                              |
| ----------- | ------------------------ | --------------------------------------- |
| A/B / 灰度    | Feature flag, **Canary** | `gray_percent` 小流量试 v2                  |
| 护栏指标        | **SLO**, error budget    | formality 阈值；跌破就 rollback               |
| 回滚          | **Blue-green rollback**  | 从 v2 切回 v1                              |
| Fallback    | Circuit breaker          | 护栏 fail / lock candidate（见 rollout 控制器） |


