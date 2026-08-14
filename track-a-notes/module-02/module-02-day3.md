# M2 Day3 — 对照 PR

**日期**：________

> **导师读法**：Day3 打开 PR diff，填「一致？学到什么」。Issue 1 对照 PR #9159 为完整示范；Issue 2 无指定 merged PR，以 Issue 原文 + Runtime trace 为 L2 对照物。

## Issue 1（#7355 ↔ PR #9159）

- **PR 链接**：[Cline PR #9159](https://github.com/cline/cline/pull/9159) — `fix(terminal): tune execute_command timeout strategy for long-running tasks`
- **实际改法摘要**：
  1. Managed mode 默认 timeout **30s → 120s**（PR 讨论中曾短暂改回 30s，最终合并版以 tier 策略为准）。
  2. 新增 **long-running tier = 300s**，通过 `isLikelyLongRunningCommand()` 正则/heuristic 识别（npm/pytest/cargo/docker build/make/torchrun 等）。
  3. 抽取 `resolveCommandTimeoutSeconds()` 纯函数；**explicit timeout 参数优先**，非 managed 路径仍返回 `undefined`。
  4. 新增单元测试 `ExecuteCommandToolHandler.timeout.test.ts` 覆盖 default / explicit / long-running 三路径。
  5. **未解决**（PR 后评论仍 open）：JetBrains 仍 inherit backgroundExec 30s 路径的用户体验；**无「无限等待直到结束」**选项；5–10 分钟 build 仍可能不够。
- **与我 Day2 一致？** **部分一致（tier 思路同构，observe 语义与平台覆盖有差）**

  | 维度                | Day2 方案                          | PR #9159                                     | 判定              |
  | ----------------- | -------------------------------- | -------------------------------------------- | --------------- |
  | 根因定位              | 30s 一刀切 + long-running 错位        | 同：TerminalBench 上 premature timeout          | ✅ 一致            |
  | 分 tier            | `_timeouts` + 300s heuristic     | 120s default + 300s long-running             | ✅ 同构            |
  | explicit override | schema 校验 + 优先 explicit          | 保留 LLM `timeout` 参数                          | ✅ 一致            |
  | 可测试性              | `resolve_timeout()` 纯函数          | `resolveCommandTimeoutSeconds()` + unit test | ✅ 一致            |
  | observe 语义        | timeout ≠ 失败；in_flight 标记        | PR 主要 **延长等待**，未改 Agent 对 in-flight 的叙述      | ⚠️ Day2 更完整     |
  | 平台覆盖              | 不限 JetBrains/VS Code             | 仅 yolo + backgroundExec managed mode         | ⚠️ PR 范围更窄      |
  | 配置混淆              | 区分 shell connect vs command exec | PR 未改 UI/配置命名                                | Day2 指出根因，PR 未修 |

- **PR 更优之处**（相对 Day2 纸面方案）：
  - **真实 regex 列表**覆盖 package manager / test runner / ML training 等，比 Day2 伪代码更落地。
  - **单元测试**锁定行为，防止 default 再次悄悄变回 30s。
  - **TerminalBench 驱动**：用 benchmark 失败反推 timeout 策略，而非拍脑袋全局值。
- **PR 未覆盖、Day2 应保留的认知**：
  - #7355 用户要的是 **「等到命令真正结束」**；tier 延长只是缓解，不是「timeout 哲学」的终局答案（0xfk0 评论：hardcoded timeout 对 shell 本身是 nonsense）。
  - **M2-K05**：#8448 hang 证明还需要 **stalled/idle** 上界——PR #9159 只解决「切太早」，不解决「永不切」。
- **更新后的认知**：
  - Day1「30s 一刀切 + 配置语义混淆」仍然成立；Day3 补充：**业界 fix 首选 heuristic tier + 可测 policy 函数**，不是简单把 30 改成 6000。
  - TrackARuntime `_timeouts` 与 PR #9159 **设计同构**；L3 是实现 `resolve_timeout()` 并写入 trace。
  - Case 7 口述可挂：ASR/TTS 优化无效，因为 **LLM TTFT / tool tier** 才是 P95 瓶颈——与 #7355 「test/build tier」同构。

## Issue 2（#8448 ↔ #4356 / PR #10181）

- **对照物**：[Cline #8448](https://github.com/cline/cline/issues/8448) · [#4356 终端 completion 集群](https://github.com/cline/cline/issues/4356) · 后续 [PR #10181](https://github.com/cline/cline/pull/10181)（idle timeout）
- **TrackARuntime 证据**：`python cli.py demo-no-output-hang` → `m1_m2/evidence/m2-8448-demo/trace.json`
- **实际改法摘要（Cline 侧）**：
  1. `grep` 无匹配 → 零 stdout → VS Code shell integration **不发 completion** → Cline 无限 wait。
  2. 官方 workaround：**Background Exec**（child_process，绕过 integration）。
  3. PR #10181 方向：`onDidEndTerminalShellExecution` + **idle timeout** 闭合 observe。
- **与我 Day2 一致？** **一致（主链路同构）**

  | 维度    | Day2 方案                           | Cline / OSS                                        | 判定             |
  | ----- | --------------------------------- | -------------------------------------------------- | -------------- |
  | 根因    | completion detection 在无输出时失效      | #8448 + #4356 同族                                   | ✅              |
  | 失败极性  | 永不切（#8448）vs 切太早（#7355）           | 同                                                  | ✅              |
  | 修复    | `observe_stalled` + idle cap      | backgroundExec / idle timeout                      | ✅ 同构           |
  | Trace | `completion: pending` → `stalled` | 真实 Cline hang 时 **无 trace**；runtime 用两条 event 显式对比 | ⚠️ runtime 更可教 |

- **更新后的认知**：
  - Issue 2 **不是 allowlist**；K01 可用 `demo-allowlist` 选修，与 I02 无关。
  - #8448 证明 timeout 策略必须 **双向**：tier 下界 + stalled 上界。
  - `fallback_used: true` 在 stalled 路径表示 **observe 降级闭合**，不是 allowlist 拒绝。

---

## Issue 对照表


| Issue                | PR / 对照物                          | 一致？       | 学到什么                                               |
| -------------------- | --------------------------------- | --------- | -------------------------------------------------- |
| **#7355** timeout 分桶 | PR #9159                          | 部分一致      | tier + heuristic + 纯函数 policy；延长不等于 observe 语义 fix |
| **#8448** hang       | #4356 + backgroundExec workaround | Learner 填 | timeout 两极：切太早 vs 永不切；需要 stalled 上界                |
| **M2-I02** allowlist | `ToolExecutor.call()` + trace     | Learner 填 | 副作用工具必须 allowlist + trace 留证                       |


## 校准结论

- [x] Issue 1 思路与 PR #9159 tier 策略一致 → M2-K04 L2
- [x] Issue 1 能口述 timeout ≠ kill（#7355 vs #8448 两极）→ M2-K05 L2
- [x] Issue 2 trace 逐步讲解完成 → M2-K02 L2
- [x] Issue 2 allowlist 拒绝 `fallback_used: true` 已验证 → M2-K01 L2
- [ ] 被 PR 打败 → 记录差距，延长 2 天再练

**Issue 1 示范判定**：PR #9159 验证了 Day2 **分 tier + resolve 函数 + 测试** 方向；Day2 额外的 **in_flight observe 语义** 与 **配置项拆分** 仍是 open problem——这不算「被打败」，而是 L3 扩展空间。

**写入 GUIDE 或 exit 的要点**：

- Tool = RPC：**allowlist** 防副作用；**timeout tier** 防 SLA 错位；**trace** 是面试证据链。
- #7355 ↔ Case 7：全局 timeout 优化错位瓶颈；要 **per-tool latency_ms** 分 span。
- #7355 vs #8448：**同一 observe 层的两极**——Policy 必须同时有 default tier、explicit override、idle/stalled cap。
- 三层防御（M2-K03）：schema 校验 → tier/dry-run → 超时降级或人工确认。

