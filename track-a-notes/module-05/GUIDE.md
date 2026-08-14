# 模块 5 学习指南：Bad Case 系统思维

> **导师补充**：知识工程点 [`M5-K01–K04`](knowledge.md) · 按 Case 选 Issue [`M5 映射表`](issues.md)

## 本模块在系统中的位置

| | |
|---|---|
| **生命线** | ⑤ **运维响应** — 告警、SOP、监控分层 |
| **依赖** | M1–M4（合成层，指向各证据文件） |
| **主证据** | `monitoring-layers.md` · `project-mapping.md` |
| **体系详述** | [`KNOWLEDGE-SYSTEM.md` §7 M5](../curriculum/00-knowledge-system.md) · [`COURSE.md` 第 5 课](../curriculum/01-course.md) |

材料来源：[`case-library/README.md`](../case-library/README.md) Case 1–8 · 扩展 [Case 09](../case-library/cases/case-09-token-burn-rate-limit-cascade.md)（SOP：[`case-library/sops/`](../case-library/sops/sop-case-09-token-burn-rate-limit-cascade.md)）· 方法论 [`METHODOLOGY.md`](../case-library/METHODOLOGY.md)

## 三日校准（导师指定 Case）

| 天 | 任务 | 材料 |
|---|---|---|
| Day1 主修 1 | Case 7 延迟 ↔ M2 #7355 | [`module-05-day1.md`](module-05-day1.md) |
| Day1 主修 2 | Case 2 蝴蝶 ↔ M3 harness | 同上 |
| Day1 扩展 | Case 9 浅读速记（可与 M1 Issue 4 Day1 并行） | 同上 · Issue 3 块 |
| Day2 | 五步 SOP + 监控分层 + **Case 9 监控行**（前置 M1 Day2 Issue 4） | [`module-05-day2.md`](module-05-day2.md) |
| Day3 | 跨模块校准 + Case 9 对照（前置 M1 Day3 Issue 4） | [`module-05-day3.md`](module-05-day3.md) |

## 任务

1. 阅读 [`case-library/sops/`](../case-library/sops/) 下 **8 份核心** 故障 SOP；扩展 Case 9 见 [`sop-case-09`](../case-library/sops/sop-case-09-token-burn-rate-limit-cascade.md)（M1 Day3 Issue 4 后填写）
2. 完成 [`monitoring-layers.md`](monitoring-layers.md) 白板图（**加上** `metrics-*.json` 一行）
3. 填写 [`project-mapping.md`](project-mapping.md)（至少 4 个 Case 与主项目关联）

## 每周故障演习

任选 1 Case，按 SOP 五步模拟值班（不写代码，写时间线）。观察步建议同时打开：`trace` / `harness-report` / `evaluation-report` / **`metrics-*.json`**。

`metrics` 精读与自动告警 **无独立 Issue**（见 [`knowledge.md`](knowledge.md) M5-K03）。

## Exit

见 [`module-05-exit.md`](module-05-exit.md)
