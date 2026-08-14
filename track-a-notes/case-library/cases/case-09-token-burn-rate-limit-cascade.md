# Case 09 — Token 空转引发「配额雪崩」

| 字段 | 值 |
|---|---|
| **ID** | case-09 |
| **主类** | **CTL** |
| **次类** | SLO |
| **标签** | cost, token, rate-limit, silent-loop, quota |
| **关联模块** | M1, M2, M5 |
| **补强 K 点** | M1-K06 fingerprint 无进展 loop；M1-K05 fatal interrupt；M5-K03 cost / quota 监控 |
| **M5 深度** | **浅**（扩展阅读，不进 M5 深读四 Case） |
| **SOP** | [sop-case-09](../sops/sop-case-09-token-burn-rate-limit-cascade.md) |
| **TrackARuntime** | `python cli.py run --task "container death" --simulate-container-death 1` · `python cli.py run --task "stuck loop" --always-fail-tests --max-rounds 5` |
| **OSS 对照** | [oss-803](../oss-incidents/oss-803-mini-swe-container-silent-loop.md) · [oss-4579](../oss-incidents/oss-4579-openhands-stuck-loop-fatal.md) |
| **添加日期** | 2026-07 |
| **来源** | 合成场景（#803 token 浪费 + 共享 API 配额 429 级联） |

## 场景

企业内多个 Agent 服务 **共用同一 LLM 供应商 Org 级 API Key**（共享 TPM/RPM 配额）。  
夜间批处理触发一个 **Coding Agent** 长跑任务；控制面未及时 fatal，单任务在 silent loop 中持续 dispatch LLM step。

## 现象

1. **单任务侧**：用户/运维看到任务「还在跑」，无明确失败；`state.json` 轮次持续增加，`trace.json` 事件堆积，**无业务进展**。
2. **平台侧**（约 10–20 min 后）：账单告警、**cost_per_request** 尖刺；随后 **全公司 Agent 接口 429**（Rate Limit Exceeded）。
3. **业务侧**：白天在线客服 Agent、文档助手 **集体不可用**——像基础设施「雪崩」，但根因是一个 **空转 loop** 烧穿共享配额。

## 根因（非表面）

| 层 | 根因 |
|---|---|
| **CTL（主）** | 与 oss-803 / oss-4579 同族：substrate 已死或 fingerprint 无进展，但 loop **未 early fatal**，仍在 dispatch LLM → **Token 空转**。 |
| **SLO（次）** | 仅有 **事后** `step_limit` / `cost_limit` 兜底，缺 **过程级** token 速率告警与 **租户/任务级配额隔离**；单 noisy neighbor 拖垮共享 RPM。 |
| **监控错位** | 团队盯「任务完成率」，未盯 **每 run 的 LLM call 数 / token 斜率** 与 **infra 层 429 率**。 |

**一句话**：不是「模型太贵」，而是 **控制面没停 + 配额没隔离** → 空转变成本事故，再升级为 **Rate Limit 雪崩**。

## 系统等价物

- 微服务 **重试风暴**：一个实例对 dead backend 无限 retry，打满共享连接池，拖垮全集群。
- API Gateway **无 per-tenant 限流**：单租户 burst 触发上游 429，所有租户受影响。
- 批 job **无 wall_time / budget**：跑满 scheduler slot 才被发现。

## 初级 vs 高级认知

**初级**：加 `cost_limit`、换更便宜模型、找 LLM 供应商升配额。

**高级（目标）**：

- **CTL**：observe 升维 fatal（#803）· dispatch 前 fingerprint fatal（#4579）· **Token 斜率** 超阈值 → meta fatal（不必等烧满 step_limit）。
- **SLO / 隔离**：per-run **token budget** + per-tenant **RPM 令牌桶**；429 时 **降级 + 熔断**，不无限 retry 同一 loop。
- **监控**：应用层 `cost_per_request` + `llm_calls_per_run`；基础设施层 **429 率 / quota_remaining**；告警 **先于** 账单。

## 监控与回滚

- **最先亮的监控层**：
  - **应用层**：单 run LLM 调用次数突增、`cost_per_request` P99。
  - **基础设施层**：API **429 率**、TPM/RPM 使用率 >80%。
  - **控制面**：`state.json` 多轮 `[retryable]→replan` 无 DONE；`trace.json` 相同 tool+args fingerprint（对照 `416be508`）。
- **隔离**：Kill 空转 run；对该 tenant **暂停 dispatch**；启用只读/缓存降级路径。
- **回滚**：恢复共享配额（等待窗口或切换 backup key）；修复 fatal/enforce 后 **重跑单任务**，不全量重启所有 Agent。

## 在本体系中的位置

| 模块 | 关联 |
|---|---|
| **M1** | M1-K04 多层终止（cost_limit 是 **兜底** 非首选）；M1-K06 fingerprint；#803 / #4579 Issue Day1–3 |
| **M2** | trace 事件数 / latency 可辅助估算 burn 速率 |
| **M5** | 五步 SOP 扩展阅读；与 Case 7（延迟雪崩）对比：**Case 7 = 慢**，**Case 9 = 空转烧配额** |
| **KNOWLEDGE-SYSTEM** | [`§3.4` 成本与资源水位盲区](../../curriculum/00-knowledge-system.md) 的补充 Case |

## 关联 Case / 区分轴

| 对比项 | Case 09：Token 空转配额雪崩 | [Case 10](case-10-provider-rate-limit-fallback.md)：Provider fallback 失败 |
|---|---|---|
| 首要根因层 | **CTL**：silent loop / fingerprint 未 early fatal | **SLO / REL**：LLM Gateway fallback 不感知 quota |
| 429 触发方式 | 单个 run 持续 dispatch LLM，烧穿共享 TPM/RPM | prompt/model 变更后 token 上升，fallback 共用 quota pool |
| 第一监控 | `llm_calls_per_run`、token 斜率、fingerprint 重复 | `provider_429_rate`、`fallback_rate`、quota_remaining |
| 首要 fix | dispatch 前 fatal、per-run token budget、tenant 隔离 | quota-aware fallback、backoff、gray rollback、tenant limiter |
| 面试一句话 | “控制面没停，空转把共享配额烧穿。” | “Gateway 降级策略错，把 provider 429 放大成平台事故。” |

## TrackARuntime 证据（口述用）

| Run | 命令 | 说明 |
|---|---|---|
| `7c3a04c8` 类 | `--simulate-container-death 1` | substrate 死后仍多轮 → token 空转（应对 early fatal） |
| `416be508` | `--always-fail-tests --max-rounds 5` | fingerprint ≥3 → **应** dispatch 前 fatal，避免烧满 5 轮 |

口述时强调：**若只靠 max_rounds=5 才停，5 轮 × 每轮 LLM call 已在生产级共享配额下造成连带 429**。

## 学习记录（自填）

- **M1 Day1 Issue 4 根因猜测**：[`module-01-day1.md`](../module-01/module-01-day1.md)
- **M1 Day2 Issue 4 token budget 方案**：
- **M1 Day3 Issue 4 校准 / 2min 口述**：
- **M5 Day2 监控行 + SOP 映射**：[SOP](../sops/sop-case-09-token-burn-rate-limit-cascade.md)
