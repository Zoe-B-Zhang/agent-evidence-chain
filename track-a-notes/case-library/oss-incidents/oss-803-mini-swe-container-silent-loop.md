# OSS-803 — Container 死后 Silent Loop

| 字段 | 值 |
|---|---|
| **ID** | oss-803 |
| **标签** | agent, fatal, observe, docker |
| **关联模块** | M1 |
| **Case 库关联** | 与 [Case 03](../cases/case-03-context-lost-in-middle.md)、[Case 06](../cases/case-06-prompt-injection.md) 同属 observe/终止类；扩展 [Case 09](../cases/case-09-token-burn-rate-limit-cascade.md)（空转烧 Token → 429） |
| **Issue** | [mini-swe-agent #803](https://github.com/SWE-agent/mini-swe-agent/issues/803) |
| **对照 PR** | [PR #807](https://github.com/SWE-agent/mini-swe-agent/pull/807) |
| **TrackARuntime** | `python cli.py run --task "container death" --simulate-container-death 1` |
| **Day1–3 笔记** | [`module-01/module-01-day1.md`](../../module-01/module-01-day1.md) 等 |
| **添加日期** | 2026-07 |

## 场景

Agent 在 Docker 容器内执行命令；容器已停止或不可达。

## 现象

Agent **继续 loop**：仍发 action、仍等 observation，长时间无进展（silent loop）。

## 根因（Day1 猜测，对照 PR 前）

Container 死亡被当作 **普通 recoverable observation**，未分类为 **fatal**；replan 在已死 substrate 上空转。

## 系统等价物

下游实例已注销，调用方仍按可重试错误无限 retry。

## TrackARuntime 证据

- Fatal 退出 + `trace.json` 含 `error_class: fatal`
- 对比：`run --task "fix test"` → recoverable → replan

## 学习记录（自填）

- **Day3 与 PR #807 差距**：
- **M1 rubric 自评**：
