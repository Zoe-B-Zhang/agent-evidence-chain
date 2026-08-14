# M3 Day3 — 对照 PR

**日期**：________

> **导师读法**：Day3 打开 PR diff，填「一致？学到什么」。Issue 1 对照 PR #1492 为完整示范；Issue 2 以本地 harness-report 为 L2 对照物。

## Issue 1（#1491 ↔ PR #1492）

- **PR 链接**：[guardrails PR #1492](https://github.com/guardrails-ai/guardrails/pull/1492) — `fix(reask): guard against IndexError when FieldReAsk.fail_results is None`
- **实际改法摘要**：
  1. 第 573 行从 `first_fail_result = fail_results[0]` 改为 `first_fail_result = fail_results[0] if fail_results else None`。
  2. 原有第 575 行 `if first_fail_result` 分支 **变为可达**，空列表时 return FieldReAsk unchanged。
  3. 新增单测 `test_sub_reasks_with_fixed_values_none_fail_results`。
  4. **未改**：max re-ask 全局策略、fail_results 默认值从 None 改为 [] 的 schema 层修复——仍是 L3 扩展空间。
- **与我 Day2 一致？** **高度一致（一行 guard + 单测；max re-ask 为 Day2 L3 扩展）**

  | 维度 | Day2 方案 | PR #1492 | 判定 |
  | --- | --- | --- | --- |
  | 根因定位 | 空 fail_results 索引 crash | 同：unreachable guard | ✅ 一致 |
  | 修复 | 索引前 short-circuit | `if fail_results else None` | ✅ 一致 |
  | 可测试性 | 单测覆盖 default 路径 | 新增 unit test | ✅ 一致 |
  | max re-ask | Day2 设计 counter | PR 未涉及 | Day2 L3 保留 |
  | schema 默认值 | Optional → [] coerce | PR 未改 Pydantic default | Day2 L3 保留 |

- **PR 更优之处**（相对 Day2 纸面方案）：
  - **最小 diff**：一行修复 + 测试，符合「边界 bug 不需大重构」。
  - **Fixes #1491** 闭环，repro 与 test case 1:1 对应。
- **PR 未覆盖、Day2 应保留的认知**：
  - **M3-K06 L3**：max re-ask 仍可能无界——#1491 只是 crash，不是 loop。
  - **M3-K01**：Harness 层应有 **health check**——类似 M2 trace 必须记录 re-ask 次数。
- **更新后的认知**：
  - Day1「guard 顺序错误」仍然成立；Day3 补充：**先写 test 再 merge** 是 Harness 交付层的基本功。
  - 与 M2 #7355 对照：#7355 用 **heuristic tier** 缓解；#1491 用 **一行 guard** 修复——复杂度与 bug 类型匹配。

### Industry PR 归类

| 维度 | 归类 |
| --- | --- |
| **主类** | **REL**（Harness 交付层逻辑 crash，回滚/重试路径不可信） |
| **次类** | **CTL**（re-ask 预处理是 Harness 内循环的一跳；空状态未闭合） |
| **PR 类型** | `fix` — 边界 guard + 回归单测，非 feature/scaffold |
| **同构 OSS** | [oss-803](../case-library/oss-incidents/oss-803-mini-swe-container-silent-loop.md)（默认路径未处理）；M2 #7355 PR #9159（单测锁定 default tier） |
| **归类依据** | 故障首先暴露在 **交付/门禁脚本自身**，而非 LLM 输出质量——与 Case 2（REL·发布流程）互补：#1491 是「门禁脚本空指针」，Case 2 是「门禁指标未设」 |

### Design 考量

- **前期如何避免**：Day1 根因「默认值路径未测试」说明 **测试集在 design 阶段就不完整**。设计 re-ask 状态机时，应把 **None / [] / 有值** 三条路径写进契约表（Day2 flowchart），并在 PR 描述里列「必测路径」——merge 前缺任一条则 gate fail。
- **Flowchart 能否避免编码错误**：**能，针对顺序类 bug**。Day2 的 `on_validation_fail` 分支图若贴在 IDE 旁写代码，会强制「先判 empty → 再索引」，不会写出「先 `[0]` 再 if」——#1491 本质是 **执行顺序与图不一致**。
- **测试策略**：最小 repro 3 行、无 LLM → **必须 unit test**，不能靠 integration。PR #1492 的 test 名直接绑定现象（`none_fail_results`），便于 regression grep。
- **L3 设计补位**：schema 层 `fail_results` 默认 `[]` + validator coerce（消除 None/[] 混用）；max re-ask counter + harness history——PR 未做，但 interview 可说「fix 止血，counter 防 loop」。

## Issue 2（Case 2 · 本地 harness 对照）

- **对照物**：`python cli.py harness --prompt v2 --gray-percent 10` → `m3/evidence/harness-report.json`
- **实际现象摘要**：
  1. v2 mock 输出含 `Amazing!!!` / `awesome` → `formality_score: 0.0`。
  2. `guardrail_ok: false` → `action: rollback_to_v1`。
  3. `rollback_reason: guardrail_failed_during_gray`——**灰度期间护栏失败即回滚**。
- **与 Day2 一致？** **高度一致（版本化 + 护栏 + 灰度回滚链完整）**

  | 维度 | Day2 方案 | harness-report | 判定 |
  | --- | --- | --- | --- |
  | Prompt 版本化 | v1/v2 yaml + changelog | `prompt_version: v2`；v2 有 changelog 行 | ✅ 一致 |
  | 护栏 | formality_min 阈值 | v2 `style_formality_min: 0.4`；score=0.0 < 0.4 | ✅ 一致 |
  | 灰度 | gray 10% 限流 | `gray_percent: 10` | ✅ 一致 |
  | 回滚 | guardrail fail → rollback_to_v1 | `action: rollback_to_v1` | ✅ 一致 |
  | 回滚原因 | 灰度期护栏失败 | `rollback_reason: guardrail_failed_during_gray` | ✅ 一致 |
  | K 点 | M3-K02–K05 | 全链字段可审计 | ✅ L2 证据 |

- **PR 更优之处**（相对「无 Harness 直接改 Prompt 上生产」）：
  - **可复现**：mock 输出 + 确定性 score，不依赖 LLM 随机性——Learner 可反复跑 cli 验证。
  - **决策结构化**：`action` / `rollback_reason` 字段 = 面试证据链，不是「感觉 v2 不好」。
- **PR 未覆盖、Day2 应保留的认知**：
  - v2 把 `style_formality_min` 降到 0.4，但 **tone 改动 + 低阈值** 仍挡不住 mock 极端文案——说明护栏要绑 **输出分布**，不能只绑 Prompt 意图（M3-K03 L3）。
  - **ModelAccessRouter**（timeout/retry/circuit）PR 未模拟——re-ask 风暴拖垮上游仍是 open（衔接 Issue 1 max re-ask）。
- **更新后的认知**：
  - Case 2 与 #1491 **互补**：#1491 = Harness **逻辑** crash；Case 2 = Harness **流程** 缺护栏时的小改动大偏移。
  - M2 allowlist = tool **入口**；formality = prompt **出口**——Day3 应能串讲「双护栏」。

> **导师提示**：Issue 2 的 L2 证据 = **复制 harness-report.json 关键字段 + 口述 Case 2 蝴蝶效应**，不必等 OSS merged PR。Discussion #1454 补充 re-ask 架构背景即可。

### Industry PR 归类

| 维度 | 归类 |
| --- | --- |
| **主类** | **REL**（Prompt 当配置发布；缺灰度/护栏/回滚） |
| **次类** | **MET**（满意度断崖 = 单 KPI 无护栏维度；formality 是多指标之一） |
| **PR 类型** | 本地 **Harness 对照物**（非 OSS merged PR）；行业等价 = 配置中心金丝雀 + 自动 rollback |
| **同构 Case/OSS** | [Case 02](../case-library/cases/case-02-prompt-butterfly.md)；[Case 08](../case-library/cases/case-08-ab-survivorship-bias.md)（次：只看满意度不看 formality） |
| **归类依据** | 故障首先暴露在 **变更发布层**——代码没 crash，但 **行为分布** 断崖 |

### Design 考量

- **前期如何避免**：Prompt 变更走 **RFC 三件套**——(1) v1/v2 diff + changelog；(2) 灰度比例与 promote 条件；(3) **护栏 KPI 基线**（formality、长度、禁词）在 merge 前跑 harness。缺任一项 = 测试集只覆盖「happy path promote」，不覆盖「灰度失败 rollback」。
- **Flowchart 能否避免编码错误**：**能，针对 pipeline 顺序**。`run_harness` 逻辑应是：load prompt → generate → **check guardrail** → **if gray && fail → rollback** → else promote。写代码时对照 flowchart，不会先 promote 再检护栏。
- **测试策略**：故意破坏实验（Day2）——改 mock 文案 / 提高 `style_formality_min` / `gray-percent 0` 三条路径各跑一次，harness-report 字段应可预测。
- **与 M2 衔接设计**：入口 allowlist + 出口 formality = **完整交付面**；eval 侧应加风格维度 scenario（M4 延伸），不能只测 task completion。

---

## Issue 对照表

| Issue | PR / 对照物 | 一致？ | 学到什么 |
|---|---|---|---|
| **#1491** re-ask crash | PR #1492 | 高度一致 | 边界路径必须单测；最小 guard diff；flowchart 防顺序 bug |
| **Case 2** Prompt 漂移 | harness-report.json | 高度一致 | 版本化 + 护栏 + gray rollback；REL 类发布流程 |
| **M2-I02** allowlist | trace.json（跨模块） | 设计一致 | 入口拦截 + 出口护栏 = 完整交付 |

## 校准结论

- [ ] Issue 1 思路与 PR #1492 一致 → M3-K06 L2
- [ ] Issue 1 能口述 Harness vs Agent loop 区分 → M3-K01 L2
- [ ] Issue 2 harness-report 逐步讲解完成 → M3-K03/K04 L2
- [ ] Issue 2 能讲 v1/v2 changelog → M3-K02 L2
- [ ] 被 PR 打败 → 记录差距，延长 2 天再练

**Issue 1 示范判定**：PR #1492 验证 Day2 **索引前 guard + 单测**；Day2 的 **max re-ask counter** 仍是 open problem——不算被打败，是 L3 扩展。

**写入 GUIDE 或 exit 的要点**：

- Harness = 交付层：**Prompt 版本化** + **灰度** + **护栏** + **回滚**。
- #1491 ↔ M1 #803：都是 **默认路径/边界未处理**——Harness 也要 fatal short-circuit。
- Case 2 ↔ M2 allowlist：tool 入口 + prompt 出口 **双护栏**。
- **辅导 M2 剩余 Issue**：完成 M2-I02 后，用 M3 话术串讲：「allowlist 拒绝写 trace」= 交付证据链的一环。
