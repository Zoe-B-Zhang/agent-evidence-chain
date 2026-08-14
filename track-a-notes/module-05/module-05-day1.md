# M5 Day1 — 找茬

**日期**：________  
**知识工程点**：开始前读 [M5-K01–K04](knowledge.md)

> **导师读法**：M5 Day1 复用 **三日校准法**——从 Bad Case 叙事或已学 OSS Issue 出发，写现象 + 根因 + 系统等价物。Issue 1 以 **Case 7 ↔ M2 #7355** 为完整示范（你在 M2 已练过 Issue 1，此处升维到值班视角）；Issue 2 留空（Case 2）。

## Issue 1（主修 · Case 7 延迟雪崩 ↔ M2 #7355）

- **链接**：[Case 7 叙事](../case-library/cases/case-07-latency-avalanche.md) · OSS：[Cline #7355](https://github.com/cline/cline/issues/7355)
- **对应 K 点**：M5-K02, M5-K03, M2-K04, M2-K05
- **现象**（Case + Issue 合并描述）：
  - **Case 7 业务现象**：语音/全链路产品部分请求 **稳定超时**，用户体验崩溃；团队忙于优化 ASR/TTS，指标仍不改善。
  - **#7355 工具层现象**：用户配置 6000s terminal timeout，但 `sleep 120` 类命令 **~30s 被切**；Agent 报 timeout 失败却 **任务标记完成**，子进程仍在跑。
  - 3.34+ 回归；build/test 等 **合法长命令** 被误杀；非 YOLO 无法 override 30s。
  - trace 上表现为：某 span **latency 顶满 timeout**，后续 span 仍继续——**瓶颈错位**。
- **我的根因猜测**：
  - **Case 7 根因**：全链路 SLA 优化 **错位**——瓶颈在 LLM TTFT 或某 tool，却在 ASR/TTS 打补丁（M5-K03 监控分层未分 span）。
  - **#7355 根因**：单一 30s managed timeout（M2-K04）+ timeout 被当 **失败 observe**（M2-K05）。
  - **合并模式**：**全局单一 timeout / 单一优化目标** 在 Agent 系统必然失败——需 per-tool / per-intent tier + 分 span 监控。
  - 配置语义混淆：shell connect timeout vs command exec timeout——用户调了前者，后者仍 30s。
- **系统等价物**：
  - 只优化 CDN 和前端，**数据库慢查询** P95 10s 未治理 → 全站超时（Case 7）。
  - API Gateway 全局 30s read timeout → 批处理服务永远 504（#7355）。
  - 监控只看 **总请求延迟**，不看 **分服务 span** → 优化无效（OpenTelemetry 经典坑）。
- **是性能不够还是观测/SLA 设计错？**：
  - **主要是 SLA 分桶 + observe 语义错**（M2-K04/K05），不是单纯「机器慢」。
  - 值班视角（M5-K01）：**定位步** 必须先分 span P95，再决定改 ASR 还是改 tool tier。

## Issue 2（主修 · Case 2 Prompt 蝴蝶 ↔ M3 harness）

- **链接**：[Case 2](../case-library/cases/case-02-prompt-butterfly.md)
- **本地证据**：`python cli.py harness --prompt v2 --gray-percent 10`
- **对应 K 点**：M5-K01, M5-K04, M3-K02–K04
- **现象**：（Learner 自填）
- **根因猜测**：（Learner 自填）

> **导师提示（Issue 2 填空脚手架）**
>
> 1. **现象**：满意度 92%→40%；输出过于热情夸张（Case 2）。
> 2. **根因**：Prompt 小改 → **分布级偏移**；无版本化/灰度/护栏（M3）。
> 3. **系统等价物**：配置热更新无金丝雀（M5-K02）。
> 4. **与 M2 衔接**：这不是 tool timeout 问题，是 **交付层** 问题——用 harness-report 作证据。
> 5. **SOP 预告（Day2）**：观察=对比 prompt diff；隔离=gray 降至 0；回滚=v1 全量。

## 浅读 Case 速记（1 句系统等价物 · Learner 可补）

| Case | 系统等价物（L1 目标） |
|---|---|
| 1 RAG 幻觉 | 读半份数据却假装完整 |
| 4 时间穿越 | MVCC/版本失效 |
| 5 灾难性遗忘 | 微调后通用能力 regression 无 eval |
| 8 幸存者偏差 | 未分层随机的 A/B |
| 9 配额雪崩（扩展） | 单 run retry 风暴打满共享 API 429 · 对照 M1 Issue 4 |

> **Case 9 练习**：M1 Day3 Issue 4 完成后，在 M5 填 [SOP](../case-library/sops/sop-case-09-token-burn-rate-limit-cascade.md) 与 `monitoring-layers` Case 9 行（Day2）。

## 与 M2 剩余 Issue 的关联（辅导核心）

**如何用 M5 思维完成 M2 Issue 2（#8448 + allowlist）**：

| M2 Issue 2 子问题 | M5 映射 | Day1 应写什么 |
|---|---|---|
| allowlist 拒绝 | Case 6 注入面 | 现象=disallow 工具；系统等价=API gateway 越权 |
| #8448 hang | observe 永不切（M2-K05 反面） | 现象=grep 零输出 hang；系统等价=HTTP 无 EOF 无限 wait |
| trace 证据 | M5-K04 项目映射 | 监控=allowlist拒绝率；证据=trace fallback_used |

- **建议动作**：回到 [`module-02/module-02-day1.md`](../module-02/module-02-day1.md) Issue 2，用 **本日 Issue 1 的表格格式** 补完空白。
- **对照矩阵**：

  | **Issue/Case** | **失败类型** | **最先亮的监控层** | **SOP 隔离动作** |
  | --- | --- | --- | --- |
  | **Case 7 / #7355** | 延迟/误 timeout | 工具层 latencyMs P95 | 长命令 tier / 禁用误杀路径 |
  | **Case 2** | 风格断崖 | 模型层 formality | rollback v1 |
  | **M2 #8448** | observe hang | 工具层 completion/idle | backgroundExec / idle timeout |
  | **M2 allowlist** | 越权调用 | 检索/工具层拒绝率 | 拒绝 + trace 留证 |
  | **Case 9 / M1-I04** | Token 空转 → 429 | 应用 cost + infra **429 率** | Kill run + tenant 暂停 dispatch |

## 扩展 · Issue 3（Case 9 · Day1 速记 · 可选）

- **链接**：[Case 9](../case-library/cases/case-09-token-burn-rate-limit-cascade.md) · 前置 [M1 Day3 Issue 4](../module-01/module-01-day3.md)
- **对应 K 点**：M5-K01, M5-K03；M1-K04（次）
- **现象（1 句）**：单 Agent silent loop 未停 → 共享 Org Key **429 全网**。
- **系统等价物**：（Learner 自填 · 提示：retry 风暴 / 连接池打满）
- **与 Case 7 差异**：Case 7 = **慢**（SLO）；Case 9 = **空转烧配额**（CTL 主，SLO 次）

## 今日结论（Issue 1 示范）

- 我原先低估的点：
  - Case 7 与 #7355 **同构**——都是「优化错位 + 单一 SLA」；M2 学 mechanism，M5 学 **值班分 span**。
  - Bad Case 的 **高级 fix** 不是换模型，是改监控分层 + 分路径 timeout（M5-K03 + M2-K04）。
- M2 Issue 1 已完成的认知，在 M5 应升级为：**若值班收到「长命令 timeout」告警，第一步看什么 trace 字段？** → `latency_ms` 按 tool 分桶。
