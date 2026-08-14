# Study Notes — 补充概念笔记

> **定位**：`module-XX-day*.md` 与 `case-library/` 之外的 **概念深读**；面试口述、Exit 口述稿中引用的术语，可在此展开。  
> **不替代**：模块 GUIDE、Issue 三日校准、TrackARuntime 证据。

## 怎么用

1. Exit / drill 里遇到缩写或跨域类比（如 Saga、MVCC）→ 来此查 **定义 + 本体系映射**。
2. 每篇笔记末尾有 **「在本项目里」** 一节，连到 TrackARuntime 或 M1–M4 模块。
3. 自填区可记自己的例子或卡壳点。

## 索引


| 文件                                                     | 主题                             | 关联模块                     |
| ------------------------------------------------------ | ------------------------------ | ------------------------ |
| [saga-compensation.md](saga-compensation.md)           | Saga 补偿模式                      | M1（replan）、GUIDE 系统等价物   |
| [five-step-incident-sop.md](five-step-incident-sop.md) | 五步故障响应 SOP（观察→复盘）              | M5（值班）、METHODOLOGY 故障演习  |
| [rollout-auto-rollback.md](rollout-auto-rollback.md)   | 自动 rollback 控制器（L3 状态机 + 通用伪码） | M3-K04、`harness --watch` |


## 如何追加

1. 新建 `主题-简短英文名.md`（小写 + 连字符）。
2. 在本表登记一行。
3. 若在 `module-XX-exit.md` 中引用，用相对链接 `[Saga 补偿](../study-notes/saga-compensation.md)`。

