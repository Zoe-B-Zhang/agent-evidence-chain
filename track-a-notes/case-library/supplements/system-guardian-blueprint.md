# System Guardian — M6 可选项目蓝图

> **非 M1–M5 主线。** TrackARuntime 仍是唯一 anchor；本蓝图用于作品集 **第二叙事** 或面试 system design。

## 定位

**AI 生成代码的架构守门员**：LLM 生成 → **确定性 guardrail**（AST/schema）→ 失败则 feed error → 最多 N 轮自愈。

## 五步构建

| 步 | 内容 |
|---|---|
| 1 架构 Schema | JSON Schema / Pydantic 定义「合格代码」（日志、函数长度、禁库等） |
| 2 Agent 链 | 用户请求 → LLM 生成模块 |
| 3 Guardrail | AST/ESLint 等 **确定性** 校验 |
| 4 自愈 Loop | 失败 → 错误写回 prompt → 重试（≤3 轮） |
| 5 可观测 | trace：Attempt 1 fail → Attempt 2 pass |

## 为何有竞争力（对系统架构背景）

- 证明 **用架构知识约束 AI 输出**，不是纯 Prompt 玩家
- 覆盖 Agent + Tool + Harness + Eval 面试话题
- 与 TrackARuntime 叙事互补：runtime = 通用 agent 工程；Guardian = 垂直场景

## 可参考 OSS

| 项目 | 学什么 |
|---|---|
| [guardrails-ai/guardrails](https://github.com/guardrails-ai/guardrails) | validator + re-ask |
| [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) | agent loop + 沙箱执行 |
| [Pydantic Logfire](https://github.com/pydantic/logfire) / [TruLens](https://github.com/truera/trulens) | step 级 observability |

## 与 Case Library 的关联

- Case 2 → Prompt/护栏
- Case 6 → 注入与边界
- M3 harness 演示可复用到「prompt/规则版本回滚」

## 学习记录（自填）

- **是否采用为 M6 叙事**：是 / 否
- **与 TrackARuntime 分工**：
