# M1 Day1 — 找茬

**日期**：________  
**知识工程点**：开始前读 [M1-K01–K06](knowledge.md)

## Issue 1（主修 · 导师指定）

- **链接**：[mini-swe-agent #803](https://github.com/SWE-agent/mini-swe-agent/issues/803)
- **对应 K 点**：M1-K02, M1-K05
- **现象**（只抄用户描述，不看 PR）：
  - Agent 在 Docker 容器里跑命令；容器已经挂掉或不再运行。
  - 后续 step 里 agent 仍在继续 loop：还在发 action、还在等 observation，像什么都没发生。
  - 用户侧看到长时间无进展、无明确失败退出，像 **silent loop / 空转**。
  - 日志里可能出现 container not running / 类似错误，但 **loop 没有立刻 Fatal 终止**。
  - container_timeout到期会导致无声故障循环，而不是干净的代理退出

 #803：漏洞描述-当 Docker 容器在 container_timeout 后退出（以睡眠实现），代理进程继续运行，浪费 API 调用，直到 step_limit 或 cost_limit 调用耗尽。

- **我的根因猜测**：
  - 原文：container_timeout通过以睡眠启动容器实现。一旦睡眠结束，容器就会停止并取出（--rm）。后续的docker执行调用失败，但execute（）捕获异常并作为正常观察返回（returncode=-1，exception_info集合），未重新出现。模型能看到错误输出，但无法知道容器是否消失，因此会不断下达命令直到达到极限。
  - 容器死亡被当成 **普通 tool 失败 observation** 写回状态机，而不是 **不可恢复的 fatal 态**。
  - observe 阶段只记录「命令 stderr 里一行错误」，**没有检查 execution environment 是否仍存活**。
  - replan 逻辑看到「失败了」就 retry / 再 plan，但 **前提（容器存在）已不成立**，retry 无意义。
  - 可能缺少：**错误分类**（recoverable vs fatal）+ **Fatal 时 interrupt loop 并 persist trace**。
- **系统等价物**（如：工作流无终止条件 → 死循环）：
  - 下游微服务实例已注销，调用方仍按「可重试超时错误」做 retry → **对 dead backend 无限重试**。
  - 或：工作流引擎任务节点依赖的 worker 进程已死，但调度器仍派发同名 task，**没有 health check 门禁**。
  - 不是「业务逻辑 replan 条件写错」，而是 **observe 没识别环境级 fatal**。
  - 影响
    - 在基准测试中，在step_limit=500的条件下，容器在第200步失效的任务将继续执行300步，消耗约300个不必要的API调用及相关成本。
    - 轨迹从未被正确保存，且没有合适的退出状态。
- **是 observe 缺失还是 replan 条件未定义？**：
  - **主要是 observe / 错误分类问题**（M1-K02 + M1-K05）。
  - observe 应回答：「这次 failure 是 tool 参数错（可 replan），还是 execution substrate 已死（必须 Fatal）？」
  - 当前行为像把 **fatal 误判为 recoverable**，导致 replan 继续空转。
  - **不是**典型的「replan 条件未定义」（那种是 observe 正常但策略表缺分支）；这里是 **observe 信号层级错了**。

## Issue 2（主修 · 导师指定）

- **链接**：[OpenHands PR #4575 error handling](https://github.com/All-Hands-AI/OpenHands/pull/4575)
- **对应 K 点**：M1-K05, M1-K03
- **现象**：SWE-Bench eval 中 runtime 404，日志连续出现 FatalErrorObservation，但 agent 仍 dispatch 后续 action。
  - 有几个 FatalErrorObservation 并没有真正阻止代理控制器
  - 两类错误处理，会有不同的恢复途径
    - 由于代理愚蠢引发的错误称为ErrorObservations
      - 这些问题，客服可以通过反馈自动恢复
    - 由致命环境问题引起的错误为例外
      - 这些装置终止了智能体循环
      - 用户必须采取某些操作才能继续
      - 需要一些管道处理才能把它们送回用户手中，但运行时和agent_controller都运行得很好
- **我的根因猜测**：
  - #4575 要回答的是：**为什么有了 Fatal 类型，loop 仍会空转？**
  - OpenHands 曾用 FatalErrorObservation 区分 fatal，但它仍走 event stream；controller 在部分路径（#4573：eval runtime 404）未把 fatal obs 转为agent_state=ERROR / stop loop。
  - 根因不是「没分类」，而是 **分类与终止策略脱节**：fatal 信号有了，interrupt 未在 controller 层硬保证。
  - PR #4575 重构：fatal 改 raise Exception（不进 stream），recoverable 仍用 ErrorObservation + replan。
  - 对应 M1-K05（错误分类）+ M1-K03（fatal 不应进入 replan policy）。
- **系统等价物**：
  - 工作流引擎已标记节点 FAILED_FATAL，但 executor 仍按 RETRYABLE 调度 → **策略表与执行器不一致**。
  - 对比 #803：#803 是传感器读数层级错了；#4575 是读数对了但 **断路器没跳**。
  - TrackARuntime 对照： `fix test` → recoverable → replan`container death` → FatalAgentError → 不进 round2。
  - 与issue 1 的比较：**#803 与 #4575 的对照**

    |                | **#803 (mini-swe-agent)**         | **#4575 (OpenHands)**                                 |
    | -------------- | --------------------------------- | ----------------------------------------------------- |
    | **Fatal 如何表达** | 当普通 observation 返回（returncode=-1） | 曾有独立 `FatalErrorObservation` 类型                       |
    | **主要缺陷**       | observe **未升维**为 fatal            | observe **已升维**，但 controller **未稳定 interrupt**        |
    | **修复方向**       | 检测 substrate 死亡 → raise Fatal     | 去掉 FatalObs，fatal 改走 **Exception 短路**，不进 event stream |

    系统等价物应体现 **「信号到了但断路器没跳」**
  - Runtime pod 已 404，但调度器仍按「普通 tool 失败」继续派发 step——  
  Kafka consumer 收到 poison pill 已标记 `FATAL`，但 handler 仍走 retry 分支，因为 **interrupt 逻辑只在**  `main.py` / `cli.py`**检查、cli 路径漏了**（#4573 评论里提到的 multi-entry 不一致）。
- - **是 observe 缺失还是 replan 条件未定义？**：
  - **主要是 controller 终止策略未硬绑定**（M1-K05），辅以 **fatal 不应进入 replan**（M1-K03）。
  - observe 已产出 fatal 信号；replan 策略表也不是空白——问题是 fatal 仍走 observation 通道，controller 未统一 interrupt。
  - 修复本质：fatal 改 Exception 短路，recoverable 才进 replan policy。

## Issue 3A（补充 · loop fatal）

- **链接**：[OpenHands PR #4579](https://github.com/All-Hands-AI/OpenHands/pull/4579)
- **对应 K 点**：M1-K03, M1-K06, M1-K05
- **现象**：
  - Agent 陷入 action-observation 重复模式（如连续 ls、连续相同 tool call）
  - Stuck detector 已识别 loop，但 controller 仍可能再发一轮 LLM 请求
  - 浪费 token，用户看到长时间空转后才报错
- **我的根因猜测**：
  - Loop 错误走 ErrorObservation → agent 侧 replan，但 **状态无实质变化**，replan 等于 blind retry
  - 缺少 meta 层：stuck detector 结论应 **override replan policy**，直接 fatal interrupt
  - PR #4579：不把 loop 错误给 agent，throw fatal 停 controller
- **系统等价物**：
  - API 网关已检测到客户端重试风暴，仍把请求转发给后端 → 应在 edge 拒载
- **与 #803 / #4575 的差异**：
  - #803：环境死了，observe 当 recoverable
  - #4575：fatal 有类型，controller 没停
  - #4579：**环境可能正常，但行为无进展** → replan 不应再发生

## Issue 3B（补充 · pseudo-replan）

- **链接**：[LangGraph #5099](https://github.com/langchain-ai/langgraph/issues/5099)
- **对应 K 点**：M1-K03, M1-K02, M1-K06
- **现象**：
  - Tool 返回 recoverable 错误（参数名 index_pattern vs indexPattern）
  - Agent 文本声称「Let me fix the parameter name」
  - 后续多轮 tool call 参数完全相同 → 无限 loop 直到 recursion_limit
- **我的根因猜测**：
  - Observe 层级正确（recoverable ErrorObs），replan 路径也在走
  - 但 replan 未产生 **可观测的状态变化**（tool+args fingerprint 不变）
  - 缺 M1-K06：应用 fingerprint 判定「假恢复」，N 次相同 pattern 后 escalate（fatal 或换策略）
- **系统等价物**：
  - CI 失败日志说「fixing flaky test」，但 diff 为空仍重跑 → 不是 replan，是空转 retry
- **与 #803 / #4575 的差异**：
  - 不是 fatal 分类错，也不是 controller 漏停
  - 是 **recoverable 路径上 replan 无效** → 需要 progress / fingerprint 门禁

## 今日结论

- 我原先低估的点：
  - Agent loop 的难点不只在 plan/replan，而在 **observe 是否带错误语义层级**（log / recoverable / fatal）。
  - 「有 max_rounds」不等于安全：对 fatal 态 retry 是在 **浪费轮次做空转**，用户感知仍是 silent loop。
- 与 Case 3 / Case 6 的关联：
  - **Case 3**：也是 observe 不足——没 observe「检索/上下文质量不够」就硬生成；#803 是 observe 没识别「执行环境已死」。都是 **observe 信号不够结构化**。
  - **Case 6**：多轮后 system 被污染；#803 是  **substrate 死亡仍继续轮次**。共同点：状态机缺少 **硬终止 / reset 条件**。
- **Issue 对照矩阵（建议记入笔记）**

  | **Issue** | **失败类型** | **主缺陷层**                 | **修复方向**                  | **K 点**  |
  | --------- | -------- | ------------------------ | ------------------------- | -------- |
  | **#803**  | 环境死亡     | observe 未升维 fatal        | detect dead → raise Fatal | K02, K05 |
  | **#4575** | 环境 fatal | controller 未 enforce     | fatal → Exception 短路      | K05, K03 |
  | **#4579** | 行为 loop  | replan policy 未 override | stuck → fatal，不给 agent    | K03, K06 |
  | **#5099** | 假恢复      | replan 无状态变化             | fingerprint → escalate    | K03, K06 |

- **平台后果（扩展 · Case 9）**：上表任一子类型若 **未 early fatal**，在生产共享 API Key 下可演变为 **Token 空转 → 全平台 429**——见 [Issue 4 / Case 9](../case-library/cases/case-09-token-burn-rate-limit-cascade.md)（Day3 扩展）。

## 扩展 · Issue 4（Case 9 · Day1 找茬 · Learner 自填）

> **前置**：Issue 1–3B 写完后做；把 silent loop 从「单 run 空转」升维到 **平台配额事故**。

- **链接**：[Case 9](../case-library/cases/case-09-token-burn-rate-limit-cascade.md) · 对照 [oss-803](../case-library/oss-incidents/oss-803-mini-swe-container-silent-loop.md) / [oss-4579](../case-library/oss-incidents/oss-4579-openhands-stuck-loop-fatal.md)
- **对应 K 点**：M1-K04, M1-K06
- **现象**（Learner 自填 · 导师脚手架）：
  1. 夜间批处理 Agent「还在跑」，无 DONE；`state.json` 轮次涨、`trace.json` 事件堆叠。
  2. 约 15 min 后：`cost_per_request` 尖刺 → **全公司 LLM API 429** → 白天客服 Agent 集体挂。
  3. #803 原文：container 死后仍 loop，**浪费 API 直至 step/cost limit**——Case 9 问：**若 Org 共享 Key，损害范围多大？**
- **我的根因猜测**：（Learner 自填）
- **系统等价物**：（Learner 自填 · 提示：retry 风暴 · 共享连接池 · 无 per-tenant 限流）

> **导师提示**：Day1 不要只写「加 cost_limit」——那是 **兜底**；主因仍是 **CTL 未 early fatal**（与 Issue 1/3A 同族）。

    

