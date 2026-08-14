# M3 Day1 — 找茬

**日期**：________  
**知识工程点**：开始前读 [M3-K01–K06](knowledge.md)

> **导师读法**：Day1 只读 Issue 原文 + bot 评论，**不看 PR diff**。目标是把「用户现象 → 技术根因猜测 → 系统等价物」写清楚。Issue 1 为完整示范；Issue 2 留空供 Learner 按同结构填写（可参考 M2 Day1 Issue 2 脚手架）。

## Issue 1（主修 · re-ask 边界 crash）

- **链接**：[guardrails #1491](https://github.com/guardrails-ai/guardrails/issues/1491)
- **Day3 PR**：[PR #1492](https://github.com/guardrails-ai/guardrails/pull/1492)
- **对应 K 点**：M3-K06, M3-K01
- **现象**（只抄 Issue 描述，不看 PR）：
  - `sub_reasks_with_fixed_values` 在 `guardrails/actions/reask.py` 对 `FieldReAsk` 处理时 **IndexError: list index out of range**。
  - 触发条件：`FieldReAsk(incorrectValue="bad_value")` 且 **`fail_results` 默认为 None**（ReAsk 基类默认值）。
  - 第 572 行 `copy.fail_results or []` 把 None 变成 **空列表**，第 573 行立刻 `fail_results[0]` → crash。
  - 第 575 行 `if first_fail_result else None` 本可处理空列表，但 **写在索引之后，永远不可达**。
  - 任何产生 `FieldReAsk` 且未设 `fail_results`、再访问 `guard.history.last.fixed_output` 的路径都会触发。
  - 最小 repro 仅 3 行 Python，**无 LLM 调用**即可复现——纯 Harness 内部逻辑 bug。
- **我的根因猜测**：
  - **边界条件遗漏**：开发者假设 `fail_results` 非空，但默认值是 None/[]，与 M1 #803「未检查环境是否存活」同构——**默认值路径未测试**。
  - **防御性代码顺序错误**：guard 存在但 unreachable，属于 **off-by-one 式逻辑顺序 bug**（先索引后判断）。
  - **M3-K06 核心**：re-ask 是 Harness 内循环；无 max re-ask 上限时类似 silent loop，而此 bug 是 **循环辅助函数直接 crash**，交付层自身不可靠。
  - **M3-K01 核心**：Harness 层 bug 会导致 **整段 guard 流程中断**，比「LLM 输出不好」更严重——类 CI 门禁脚本空指针。
  - 与 guardrails #891 同类：`num_reasks=None` 未回落默认值——**Optional 参数与 default 语义不一致**。
- **系统等价物**（如：retry 回调在 empty queue 上 pop）：
  - 消息队列 consumer 对 **空 dead-letter 队列** 直接 `queue[0]`，重试逻辑写在 pop 之后 → 进程 crash，整条 pipeline 停服。
  - 或：Kubernetes readiness probe 回调假设 `status.details[0]` 存在，新 pod 无 details 时 **探针脚本崩溃** 而非返回 false。
  - 配置热更新 rollback 脚本在 **fail_results 为空** 时未 short-circuit，反而在 fix 阶段抛异常——**回滚路径本身不可信**（对照 M3-K04）。
- **是 re-ask 策略错还是边界防御错？**：
  - **主要是边界防御错**（M3-K06 L2）：不是 re-ask 次数太多，而是 **单次 re-ask 预处理就 crash**。
  - 深层启示：Harness 必须对 **空 fail_results / max re-ask 耗尽** 两条路径都有明确定义（return unchanged vs refrain）。
  - 与 M2 #8448 对照：#8448 是 observe **永不完成**；#1491 是 Harness **立即 crash**——都是「失败处理路径未闭合」。

## Issue 2（主修 · Case 2 + 本地实验）

- **OSS**：[guardrails Discussion #1454](https://github.com/guardrails-ai/guardrails/discussions/1454)
- **本地**：`TrackARuntime` 运行 `python cli.py harness --prompt v2 --gray-percent 10`
- **对应 K 点**：M3-K02–K05
- **现象**：（Learner 自填）
- **根因**：（Learner 自填）

> **导师提示（Issue 2 填空脚手架）**
>
> 1. **现象关键词**：满意度 92%→40%；输出「Amazing!!!」「awesome」——**小 Prompt 改动、大分布偏移**（Case 2）。
> 2. **根因方向**：v2 改 system tone + 降低 `style_formality_min: 0.4`；**无 changelog 门禁、无灰度护栏** 即全量（本地 mock 用 gray 10% 演示 rollback）。
> 3. **M3-K02/K03**：对照 `prompts/v1.yaml` vs `v2.yaml`；`formal_tone_score()` 如何判失败。
> 4. **系统等价物**：配置中心热更新无金丝雀；改一个 feature flag 全局生效 → 业务指标断崖。
> 5. **Day1 写法**：对照 Issue 1 表格，写清「Harness 自身 crash」vs「Prompt 变更无护栏」两类失败——证明 **交付层既要逻辑健壮，也要发布流程**。
> 6. **衔接 M2**：M2-I02 allowlist 是 **tool 入口拦截**；Case 2 是 **prompt 出口未拦截**——面试可串：入口 allowlist + 出口 formality guardrail。

## 与 M2 Issue 2 的关联笔记

- M2 Issue 2（#8448 + allowlist）Learner 仍需自填 Day1–3；M3 提供 **对照学习法**：
  - M2：**tool observe 两极**（切太早 #7355 / 永不切 #8448）→ trace 证据。
  - M3：**交付层两极**（Harness crash #1491 / Prompt 无护栏 Case 2）→ harness-report 证据。
- **共同教训**：失败路径必须 **可观测 + 可降级**——M2 `fallback_used`；M3 `rollback_to_v1`。
- 完成 M2-I02 时，可写一句：allowlist 拒绝若不进 trace，等价于 Harness 无 rollback 证据链。

## 今日结论（Issue 1 示范）

- 我原先低估的点：
  - Harness bug 不需要 LLM 即可 repro——**单元测试应覆盖 default/empty 路径**（PR #1492 补了 test）。
  - re-ask 不只是「问模型再来一次」，而是 **带 fail_results 的状态机**；空状态必须 first-class。
- **Issue 对照矩阵（建议记入笔记）**

  | **Issue** | **失败类型** | **主缺陷层** | **修复方向** | **K 点** |
  | --- | --- | --- | --- | --- |
  | **#1491** | re-ask 预处理 crash | 空 fail_results 未 guard | `fail_results[0] if fail_results else None` | K06, K01 |
  | **Case 2** | 风格断崖 | 无版本化/灰度/护栏 | v1/v2 + formality + rollback | K02–K05 |
