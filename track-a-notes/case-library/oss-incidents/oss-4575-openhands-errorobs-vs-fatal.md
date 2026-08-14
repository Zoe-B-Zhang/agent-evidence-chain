# OSS-4575 — Fatal 信号有了但 Controller 未停（ErrorObs vs Exception）

| 字段 | 值 |
|---|---|
| **ID** | oss-4575 |
| **标签** | agent, fatal, controller, error-classification |
| **关联模块** | M1 |
| **Case 库关联** | 与 [oss-803](oss-803-mini-swe-container-silent-loop.md) 对照：#803 是 observe 未升维；本 case 是 **断路器没跳** |
| **Issue / 阅读** | [OpenHands PR #4575](https://github.com/All-Hands-AI/OpenHands/pull/4575) · 前置 hotfix [#4573](https://github.com/OpenHands/OpenHands/pull/4573) |
| **对照 PR** | [#4575](https://github.com/All-Hands-AI/OpenHands/pull/4575)（根治）；[#4573](https://github.com/OpenHands/OpenHands/pull/4573)（controller fatal obs 处理顺序） |
| **TrackARuntime** | A/B 对照：<br>① `python cli.py run --task "fix test"`<br>② `python cli.py run --task "container death" --simulate-container-death 1` |
| **Day1–3 笔记** | [`module-01/module-01-day1.md`](../../module-01/module-01-day1.md) Issue 2 · [`module-01-day3.md`](../../module-01/module-01-day3.md) Issue 2 |
| **添加日期** | 2026-07 |

## 场景

SWE-Bench eval 中 eval-runtime 已 404（substrate 不可用）；或 recoverable 工具失败需 replan 的正常路径。

## 现象

- **B 侧（fatal）**：日志连续出现 `FatalErrorObservation`，但 agent 仍 dispatch STEP 3/4/5/6，空烧 API。
- **A 侧（recoverable）**：测试失败 → replan → 修改 command → 成功退出。

## 根因

- **不是**「没做错误分类」——OpenHands 曾有 `FatalErrorObservation` 类型。
- **是** **分类与终止策略脱节**：fatal 信号经 event stream 到达 controller，但 `#4573` 路径下 `report_error()` 把 **ErrorObservation**（recoverable）写回 stream → agent 当可恢复错误继续 step。
- **#4575 根治方向**：fatal 改 **raise Exception 短路**，不进 event stream；recoverable 仍走 ErrorObservation + replan。

## 系统等价物

工作流节点已标 `FAILED_FATAL`，executor 仍按 `RETRYABLE` 调度；或 Kafka poison pill 已标 FATAL，handler 仍走 retry 分支。

## TrackARuntime 证据

| 侧 | Run | 关键读数 |
|---|---|---|
| A recoverable → replan | `m1_m2/evidence/5fb33372/` | `success=true`；history `[retryable]`→`replan`→`[recoverable]`；trace command **变化** |
| B fatal 短路 | `m1_m2/evidence/7c3a04c8/` | `FatalAgentError`；无 round2 replan；trace `error_class: fatal` |

**同一 runtime、同一 controller**——错误分类不同 → 策略不同（M1-K05 + M1-K03）。

## 学习记录（自填）

- **Day3 与 PR #4573 / #4575 差距**：
- **M1 rubric 自评**：
