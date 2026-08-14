# M5 Day2 — 开方

**日期**：________

> **导师读法**：Day2 设计 **SOP 时间线 + 监控分层 + 项目映射**。Issue 1（Case 7）为完整示范；Issue 2（Case 2）留空供 Learner 填写。

## Issue 1 工程化响应（Case 7 · 延迟雪崩 ↔ #7355）

**方案一句话**：分 span 监控定位真实瓶颈 → per-tool timeout tier → 超时 observe 不伪造失败 → 慢路径降级

### 五步 SOP 时间线（Issue 1 示范）

| 阶段 | 时间 | 动作 | TrackARuntime 证据 |
|---|---|---|---|
| **观察** | 5 min | 打开最近 fail run 的 `trace.json`，按 tool 算 **latency_ms P95**；对比 read_file vs run_tests vs docker_exec | `m1_m2/evidence/<id>/trace.json` |
| **隔离** | 10 min | 对 P95 最高的 tool 路径 **降级**：短答/缓存/禁用联网；长命令切 long-running tier | `tool_executor._timeouts` |
| **定位** | 30 min | 确认瓶颈在 **tool tier** 而非 loop 总时长；对照 #7355：30s 误杀 vs 用户要 6000s | M2 day2 heuristic 表 |
| **修复验证** | 1 h | 实现/文档化 `resolve_timeout(tool, payload)`；跑 `run_tests` scenario；trace 中 latency 可高于 read | PR #9159 同构 |
| **复盘** | 全天 | monitoring-layers 填 **工具层 per-tool latencyMs** + **模型层 TTFT**；eval gate 加 latency regression | `evaluation-report.md` |

### 监控分层填表（Case 7 示范）

| 层 | 指标 | 阈值 | 告警动作 |
|---|---|---|---|
| 业务 | 任务完成率 | 较基线 -10% | 值班通知 |
| 应用 | fallback 率 | >5% | 查 trace error_class |
| 检索/工具 | **per-tool latencyMs P95** | run_tests >120s | 升 tier / 勿误杀 |
| 模型 | TTFT P95 | >3s | 换路由/小模型 |
| 基础设施 | API 错误率 | >1% | 熔断 |

### 项目映射行（Case 7 示范）

| Case | 若我的系统出现类似现象 | 监控哪里亮红灯 | trace/eval 证据 | 回滚动作 |
|---|---|---|---|---|
| 7 延迟 | 长 test 被 30s 切 | 工具层 run_tests latency P95 | `trace.json` latency_ms | 回退 tier 表 / 禁用 30s 硬切 |

**与 M2 Day2 对照**：M2 写了 mechanism 表；M5 写 **值班动作表**——同一 fix，两种证据（设计 vs 运维）。

---

## Issue 2 工程化响应（Case 2 · Learner 自填）

**方案一句话**：（Prompt 版本化 + gray + formality 护栏 + rollback）

### 五步 SOP 时间线

| 阶段 | 时间 | 动作 |
|---|---|---|
| 观察 | 5 min | |
| 隔离 | 10 min | |
| 定位 | 30 min | |
| 修复验证 | 1 h | |
| 复盘 | 全天 | |

> **导师提示（Issue 2 Day2 填空顺序）**
>
> 1. **观察**：对比 v1/v2 yaml diff + harness-report `formality_score`。
> 2. **隔离**：`gray-percent 0` 或停 v2 promote。
> 3. **定位**：Case 2 根因=语义偏移，非模型换版。
> 4. **修复验证**：`python cli.py harness --prompt v2 --gray-percent 10` 仍应 rollback。
> 5. **复盘**：prompt 变更必须 changelog + eval 覆盖风格维度。
>
> 参考 [`sops/sop-case-02-prompt-butterfly.md`](sops/sop-case-02-prompt-butterfly.md)。

### 项目映射行（Case 2 · Learner 填）

| Case | 现象 | 监控 | 证据 | 回滚 |
|---|---|---|---|---|
| 2 蝴蝶 | | formality_score | harness-report.json | prompts/v1 |

---

## 辅导：用 Day2 模板完成 M2 Issue 2

**M2 Issue 2 Day2 机制表 ↔ M5 SOP 映射**：

| M2 Day2 机制 | M5 隔离/定位动作 |
|---|---|
| Allowlist 拒绝 | 观察：跑 disallow 工具；证据：trace `fallback_used: true` |
| idle/stalled timeout | 定位：#8448 completion 缺失；监控：工具层 idle 超 60s |
| Trace 字段 | 修复验证：逐步讲 5 个 trace event（M2-K02 L2） |

**建议 Learner 现在完成**：
1. 打开 [`module-02/module-02-day2.md`](../module-02/module-02-day2.md) Issue 2 空白表。
2. 按上表 + M5 Issue 1 SOP 格式填写。
3. 跑 `python cli.py run --task "fix failing test"` 找 allowlist 相关 trace（或扩展触发 disallow）。

## monitoring-layers.md 任务

- 至少再填 **3 行**（Case 2/6/7 以外任选）。
- Case 6 建议：应用层 **guardrail 触发率** + 检索层 **allowlist 拒绝率**。
- **Case 9（扩展）**：应用层 `llm_calls_per_run` / `cost_per_request`；基础设施层 **429 率**（对照 [SOP](../case-library/sops/sop-case-09-token-burn-rate-limit-cascade.md)）。

### Case 9 监控填表示范（扩展 · Learner 可改）

| 层 | 指标 | 阈值 | 告警动作 |
|---|---|---|---|
| 应用 | `llm_calls_per_run` | >基线 3× | Kill 空转 run |
| 应用 | `cost_per_request` P99 | 较基线 +50% | 值班通知 |
| 基础设施 | API **429 率** | >1% | tenant 暂停 + 降级 |

### Case 9 项目映射行（扩展 · Learner 填）

| Case | 现象 | 监控 | 证据 | 回滚 |
|---|---|---|---|---|
| 9 配额雪崩 | 单 run 空转 + 全网 429 | 429 率 + llm_calls/run | `state.json` 轮次 + trace 条数 | Kill run · 等 RPM 窗口 |

> **前置**：完成 [M1 Day2 Issue 4](../module-01/module-01-day2.md) 后再填；SOP 主文件在 [`case-library/sops/`](../case-library/sops/sop-case-09-token-burn-rate-limit-cascade.md)。

## 解法总表

| 维度 | Issue 1 (Case 7) | Issue 2 (Case 2) | M2 Issue 2 |
|---|---|---|---|
| SOP 核心 | 分 span 定位 | prompt diff + rollback | trace + idle timeout |
| 监控层 | 工具/模型 | 模型/业务 | 工具 |
| 证据 | trace.json | harness-report | trace.json |
| 回滚 | tier 表 | v1 prompt | 无副作用拒绝 |
