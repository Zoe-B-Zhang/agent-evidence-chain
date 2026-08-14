# M2 Day1 — 找茬

**日期**：________  
**知识工程点**：开始前读 [M2-K01–K05](knowledge.md)

> **导师读法**：Day1 只读 Issue 原文 + bot 评论，**不看 PR diff**。目标是把「用户现象 → 技术根因猜测 → 系统等价物」写清楚，为 Day2 开方和 Day3 对照 PR 打底。

## Issue 1（主修 · timeout 分桶）

- **链接**：[Cline #7355](https://github.com/cline/cline/issues/7355)（相关 [#8154](https://github.com/cline/cline/issues/8154)）
- **对应 K 点**：M2-K04, M2-K05
- **Day3 PR**：[Cline PR #9159](https://github.com/cline/cline/pull/9159)
- **现象**（只抄用户描述，不看 PR）：
  - 用户配置 terminal timeout 为 6000 秒，但执行 `sleep 120 && echo 'yes'` 时，Cline 在 **约 30 秒** 就判定命令 timeout，认为命令失败。
  - Agent 随后 **继续推理**，向用户报告「命令已 timeout，但仍在后台运行」——任务被标记完成，**实际结果未被 observe**。
  - 3.33.1 正常，3.34+ 回归；JetBrains / Void Editor 与 VS Code 均受影响。
  - 典型场景：单元测试、集成测试、build 等 **合法长命令** 被 30s 硬切，Agent 误判失败并重试或提前结束任务。
  - #8154 补充：即使用户或模型想 override，**非 YOLO 模式下** 30s 仍无法被覆盖。
- **我的根因猜测**：
  - PR #7171（2025-11）为 yolo / backgroundExec 引入 **DEFAULT_COMMAND_TIMEOUT_SECONDS = 30**；JetBrains 的 `StandaloneTerminalManager` 行为类似 backgroundExec，**继承了 30s 硬超时**。
  - 用户设置的 6000s 是 **shell integration timeout**（等终端连接），不是 **command execution timeout**——两个配置被混读。
  - 「LLM-judged timeout」依赖模型主动传 `timeout` 参数；非 YOLO 时模型 **无法指定**，长命令必死。
  - **M2-K05 核心**：timeout 在这里被当成 **observe 失败信号**（命令失败），但子进程 **仍在跑**——timeout ≠ kill，observe 层语义错了。
  - **M2-K04 核心**：所有命令共用 30s 一刀切，没有按 **build / test / read** 分 tier SLA。
- **系统等价物**（如：API Gateway 全局 30s vs 编译任务 10min）：
  - API Gateway 对所有下游统一 30s timeout → 编译/批处理服务 **永远被误判 504**，调用方却以为任务失败而 **重复提交**（与 Agent 重跑 test 同构）。
  - 只监控「请求是否返回」，不区分 **in-flight 长任务** vs **真正失败** → Case 7 的「全链路单一 timeout」。
  - 配置项命名歧义：`connect_timeout` 与 `read_timeout` 混在一个 UI 字段 → 用户调了 connect，execution 仍 30s。
- **是 timeout 设错还是 observe 语义错？**：
  - **两者都有**：30s 默认值对 long-running workload 不合理（M2-K04）；timeout 后 Agent 把 **仍在运行的进程** 当失败 observation 写回（M2-K05）。
  - 与 M1 #803 对照：#803 是 observe 未升维 fatal；#7355 是 **过早 timeout + 错误 observe 语义**（timeout 不等于 exit code）。

## Issue 2（主修 · observe 永不完成）

- **链接**：[Cline #8448](https://github.com/cline/cline/issues/8448)
- **对应 K 点**：M2-K05, M2-K02
- **现象**：
  - Cline gets stuck if it runs a command which produces no output.
  - 然后你需要两次切换计划/行动模式，然后输入这个提示继续：
    > Your command had no output.
    Then Cline will continue the task. But this is cumbersome if happens a lot.
  - `grep` 无匹配 → **零输出** → Cline **hang 永不完成**；切换 Plan/Act 或手动提示后才继续。
- **根因猜测**：
  - 当命令没有输出（比如找不到匹配的命令），VSCode 的 shell 集成 API 并不总是正确地表示完成，导致 Cline 无限期等待。
  - no related with LLM used 
- **系统等价物**：（Learner 自填）
  - 终端设置中set idle timeout 兜底，终止客户端的无限等待。
  - 通过其他方式，比如后**台执行**终端模式来绕过了VSCode的shell集成，避免集成导致状态不能正确表示。

> **导师提示（Issue 2 填空脚手架）**
>
> 1. **现象关键词**：`grep` 无匹配 → **零输出** → Cline **hang 永不完成**；切换 Plan/Act 或手动提示后才继续。
> 2. **根因方向**：VS Code shell integration 的 completion detection 在无输出时不触发 end signal（#4356 集群）；**不是模型问题**（多模型复现）。
> 3. **M2-K05**：这是 timeout 的 **反面**——不是「切太早」，而是 **observe 永远等不到 completion**；timeout ≠ kill 的另一半：缺少 **stalled / idle timeout** 兜底。
> 4. **系统等价物**：HTTP 长连接无 body 无 EOF，客户端 **无限 wait**；需要 idle timeout 或 heartbeat。
> 5. **Day1 写法**：对照 Issue 1 表格，写清「过早切 vs 永不切」两极，证明 **tool observe 需要分路径 SLA + stalled 检测**。

## 与 Case 7 的关联笔记

- Case 7：团队只优化 ASR/TTS，忽略 LLM TTFT → **瓶颈错位** + **全链路单一 timeout**。
- #7355：Cline 对 execute_command 用 **单一 30s managed timeout**，与 build/test 真实时长错位——同一类「SLA 未分桶」。
- **共同教训**：不能只有一个全局 timeout；需要 **per-tool / per-intent tier** + trace 里 **latency_ms 分 span 监控**（`TrackARuntime/trace.py`）。
- Issue 1 = **切太早**；Issue 2 = **切太晚/永不切** → 工具链 observe 需要 **上下界**（min wait + max stall）。

## 今日结论（Issue 1 示范）

- 我原先低估的点：
  - Tool timeout 不只是「数字调大」，而是 **observe 契约**：timeout 时应报告 `stalled`/`in_flight`，不能假装命令已失败或已完成。
  - Agent 产品里「配置项」常有多层（shell connect vs command exec），Day1 要先 **拆清配置语义** 再猜根因。
- **Issue 对照矩阵（建议记入笔记）**

  | **Issue** | **失败类型**   | **主缺陷层**                     | **修复方向**                              | **K 点**  |
  | --------- | ---------- | ---------------------------- | ------------------------------------- | -------- |
  | **#7355** | 长命令被 30s 切 | timeout tier 缺失 + observe 误判 | 分 tier + 保留 explicit override         | K04, K05 |
  | **#8448** | 无输出 hang   | completion detection 缺失      | idle/stalled timeout + backgroundExec | K05, K02 |


