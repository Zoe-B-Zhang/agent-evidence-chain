# M4 Day1 — 找茬

**日期**：________  
**知识工程点**：开始前读 [M4-K01–K05](knowledge.md)

> **导师读法**：Day1 只读 Issue 原文，**不看 PR diff**。Issue 1 为完整示范；Issue 2、3 留空供 Learner 按同结构填写。

## Issue 1（主修 · loop 检测缺口）

- **链接**：[DeepEval #2643 AgentLoopDetectionMetric](https://github.com/confident-ai/deepeval/issues/2643)
- **对应 K 点**：M4-K05, M1-K06
- **现象**（只抄 Issue 描述）：
  - DeepEval 现有 agentic metric（`TaskCompletionMetric`、`StepEfficiencyMetric`、`PlanAdherenceMetric` 等）评估 **已完成 run 的质量**，但 **不检测 infinite loop / cyclical tool-call**。
  - 生产常见失败：同一 tool + 相同 args 重复 N 次；LLM reasoning 跨步高度相似；tool call 图出现环——**final output 可能仍「看起来完成了」**。
  - Issue 提议 `AgentLoopDetectionMetric`：**trace-only、无 reference** 的新 metric。
  - 三个 sub-signal：① tool+args hash 重复计数 ② reasoning stagnation（cosine/n-gram）③ call graph DFS 环检测。
  - 评分 0–1：1.0=线性进展，0.0=严重 loop；中间分需 `reason` 解释哪类 pattern。
  - 关联 PR #2782 仅为 **scaffold**，核心检测逻辑仍 open。
- **我的根因猜测**：
  - **eval 维度缺口**：业界习惯评「答对没有」，忽略 **过程是否空转**——与 M1 #4579 fingerprint 同构，但 DeepEval 未产品化。
  - **M4-K05 核心**：loop 是 **trace 级病理**，不能只看 final answer；需 hash(tool, args) 类信号。
  - **M1-K06 核心**：TrackARuntime 在线 `_check_fingerprint_loop()` 3 次相同 docker_exec → fatal；eval 侧应对标 **离线 loop detector**。
  - 与 M2 #8448 对照：hang = observe 永不完成；loop = **重复 act 有 observe 但无 progress**——eval 需两类 scenario。
- **系统等价物**：
  - 集成测试只 assert HTTP 200，不查 **retry 风暴** 或 **相同 SQL 执行 50 次**——压测通过但生产空转。
  - 或：CI 只看 merge commit message，不看 **build 是否在同一 step 循环 3 小时**（M1 #803 step_limit 延迟暴露）。
- **是 metric 设计错还是 Agent 实现错？**：
  - **主要是 eval 覆盖缺口**（M4-K05）：Agent 可能真 loop，但 eval 没测到。
  - Agent 侧 fix 仍需要 M1 fingerprint / M2 trace——eval 是 **发现问题的传感器**。

## Issue 2（主修 · eval 系统可靠性）

- **链接**：[DeepEval #929 invalid JSON](https://github.com/confident-ai/deepeval/issues/929)
- **对应 K 点**：M4-K03
- **现象**：（Learner 自填）
- **根因猜测**：（Learner 自填）

> **导师提示（Issue 2 填空脚手架）**
>
> 1. **现象关键词**：`ValueError: Evaluation LLM outputted an invalid JSON. Please use a better evaluation model.`
> 2. **根因方向 A**：judge LLM 输出被 **max_tokens 截断** → JSON 不完整。
> 3. **根因方向 B**：AzureOpenAI 未传 `model_name` → 框架 assume **不支持 structured output** → 畸形 JSON。
> 4. **根因方向 C**：开源小模型不遵守 JSON schema → 需 Instructor/outlines/lm-format-enforcer。
> 5. **M4-K03 核心**：eval 门禁若 judge 自身不可靠 → **gate_pass 无意义**（类比 M3 Harness crash #1491）。
> 6. **系统等价物**：CI 测试 runner 崩溃 → 全绿/全红都不可信。

## Issue 3（主修 · 检索对答错）

- **链接**：[RAGFlow #9415](https://github.com/infiniflow/ragflow/issues/9415)
- **对应 K 点**：M4-K04, Case 1
- **现象**：（Learner 自填）
- **根因猜测**：（Learner 自填）

> **导师提示（Issue 3 填空脚手架）**
>
> 1. **现象关键词**：UI 显示 **已检索到 target chunks**，但 chat 答案错误/无关。
> 2. **根因方向**：system prompt **缺 `{knowledge}` 变量**；或 prompt+chunks **超 context 被截断**；或 workflow 改版未正确注入（PR #9238/#9315）。
> 3. **M4-K04 核心**：必须 **拆分 metric**——retrieval hit rate vs generation faithfulness；不能只有一个 end-to-end pass rate。
> 4. **系统等价物**：DB 查询返回正确行，但 API handler **没用查询结果拼 response**——读路径 OK、写路径丢数据。
> 5. **与 M2 衔接**：检索层类似 tool 选错文件（S11 `RETRIEVAL_MISS`）；#9415 是 **RETRIEVAL_OK_GEN_FAIL** 新类。

## 与 M2 剩余 Issue 的关联笔记

- M2-I02（allowlist + #8448）在 eval 中应如何体现？
  - allowlist 拒绝 → trace `fallback_used: true` → scenario 可断言 `GUARDRAIL_BLOCK`。
  - #8448 hang → 无 completion → eval 应超时/标记 `TEST_ENV` 或 `OBSERVE_STALL`（L3 新码）。
- **共同教训**：M2 教 **在线 trace 证据**；M4 教 **离线批量断言**——同一 failure 应有两条证据链。

## 今日结论（Issue 1 示范）

- 我原先低估的点：
  - Agent eval 不能只看 **task completion**——#2643 说明 **过程 metric** 是独立维度。
  - M1 fingerprint 与 M4 loop metric **算法同构**，应能在面试中互证。
- **Issue 对照矩阵（建议记入笔记）**

  | **Issue** | **失败类型** | **主缺陷层** | **修复方向** | **K 点** |
  | --- | --- | --- | --- | --- |
  | **#2643** | loop 未检测 | eval metric 缺口 | AgentLoopDetectionMetric | K05, M1-K06 |
  | **#929** | eval judge 崩 | 门禁不可信 | structured output + schema | K03 |
  | **#9415** | 检索 OK 答错 | prompt/注入链 | 拆分 retrieval vs gen metric | K04 |
