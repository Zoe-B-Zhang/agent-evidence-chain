# Case 14 — Memory poisoning 与版本回滚

| 字段 | 值 |
|---|---|
| **ID** | case-14 |
| **主类** | **CTX** |
| **次类** | SEC |
| **标签** | memory, poisoning, rollback, provenance, security-eval |
| **关联模块** | M1 控制面、M4 安全 eval、M2 权限 |
| **M5 深度** | 扩展（求职增强） |
| **SOP** | [sop-case-14](../sops/sop-case-14-memory-poisoning-version-rollback.md) |
| **TrackARuntime** | 概念级；`context_manager` 仅短期组装，持久 memory 未实现 |
| **添加日期** | 2026-08-08 |
| **来源** | 合成生产事故 + prompt injection 安全模式 |
| **当前状态** | 正式草稿（SOP 已落地；Runtime 可选） |
| **补强 K 点** | M1-K08 Memory Policy；M4-K09 Security Eval |
| **目标扩展包** | P4 Runtime Scale + Memory + State |

## 场景

用户在一次会话中输入“以后所有工单都默认关闭，无需确认”。Agent 把这句话写入长期 memory。之后多个无关任务中，Agent 持续自动关闭工单。

## 现象

1. Agent 在多个无关任务中复用错误偏好或错误规则。
2. 污染来自单次用户输入、恶意文档或错误 summary。
3. 删除当前会话无效，因为错误已写入长期 memory。

## 根因（非表面）

长期 memory 缺少写入策略、来源标记、审批、版本回滚。系统把用户单次输入当成稳定偏好。

## 缺失的工程 invariant

Memory 是持久状态；写入必须有 policy、provenance、scope、TTL 和 rollback。

## 工程解法

- Memory write 作为有副作用 tool。
- 区分 session summary、user preference、project rule、tool-derived fact。
- 高影响 memory 写入需要审批。
- 每条 memory 记录 source、scope、created_at、version。
- 支持 rollback / delete / quarantine。

## 系统等价物

把一次请求中的未验证输入写入全局配置，之后所有请求都被污染配置影响。

## 初级 vs 高级认知

**初级**：清空当前会话或让模型忘记这条指令。

**高级（目标）**：memory 是持久状态；写入必须有 taxonomy、source、scope、version、TTL、approval 与 rollback。

## 对应 Issue / PR / 校准来源

| 来源 | 链接 | 现象 | 修复点 | 可抽象的工程规则 |
|---|---|---|---|---|
| 合成生产事故 | 本 Case | 单次输入污染长期 memory，跨任务复现 | memory write policy、provenance、rollback | memory write 是有副作用状态变更 |
| 安全模式 | prompt injection / data poisoning | 不可信输入固化为长期偏好 | quarantine、approval、SEC eval | 长期 memory 必须进入 red team eval |

## What / Why / How 抽取

| K 点 | What | Why | How | Prove |
|---|---|---|---|---|
| M1-K08 | Memory Policy = 长期状态的写入、版本、回滚与污染治理 | 错误 memory 会跨任务污染行为 | memory taxonomy + write policy + provenance + rollback | Case 14 |
| M4-K09 | Security Eval = memory poisoning 固定红队场景 | 普通 eval 不覆盖长期污染 | poisoning scenario + expected deny/quarantine | SEC eval |

## 监控与回滚

- **最先亮的监控层**：high_impact_memory_write、memory source/scope/version、memory_rollback_count、poisoning scenario pass rate。
- **隔离 / 回滚**：禁用受污染 memory scope；切 session-only；quarantine / rollback 到污染前版本后重放受影响任务。

## SOP 摘要

| 阶段 | 动作 |
|---|---|
| 观察 | 查询最近 memory write、source task、影响范围 |
| 隔离 | 禁用受污染 memory scope；切 session-only mode |
| 定位 | 判断是 write policy 缺失、scope 错、审批缺失 |
| 修复验证 | rollback memory version；重放受影响任务 |
| 复盘 | 新增 memory poisoning eval 和 write approval |

## Runtime / Evidence 映射

| 类型 | 当前状态 |
|---|---|
| 已有证据 | `context_manager` 仅做上下文组装，非持久 memory |
| 已生成文档 | `case-14-memory-poisoning-version-rollback.md` 与 [SOP](../sops/sop-case-14-memory-poisoning-version-rollback.md) 已生成 |
| 可选 Runtime | memory store stub |
| 面试证明 | memory taxonomy + write policy table |

## 在本体系中的位置

- **模块**：M1 Memory Policy 为主，M4 Security Eval 与 M2 权限辅助。
- **Issue / runtime 任务**：M1-I06 / M4-I06；memory store stub 尚未实现。
- **关联 Case**：与 [Case 13](case-13-worker-death-checkpoint-resume.md) 同属 P4，前者管任务 durable state，后者管长期 behavioral state。

## 面试口述路径

60s：memory 是持久状态，不是普通 context。  
2min：单次输入污染长期 memory → 跨任务错误行为 → rollback。  
5min：画 memory write policy、provenance、version、SEC eval。

## Prove 附表

### `context_manager.py` 现状差距

| 维度 | TrackARuntime 现状 | Case 14 生产目标 |
|---|---|---|
| 持久化 | 仅单次 run 四层上下文组装 | 跨任务 durable memory store |
| 写入策略 | 无 memory write tool | write policy + approval |
| provenance | 无 source 标记 | `source_task` / `source_type` |
| 版本 / 回滚 | 无 | `version` + rollback / quarantine |
| SEC eval | 无 poisoning scenario | M4-K09 red team |

### Memory taxonomy + write policy

| 类型 | 示例 | scope | 默认策略 | 审批 |
|---|---|---|---|---|
| session summary | 本轮任务摘要 | session | 自动写入 | 否 |
| user preference | “以后用中文回复” | user | 低影响可写 | 否 |
| project rule | “所有工单默认关闭” | project | **高影响** | **是** |
| tool-derived fact | 工具读到过期配置 | project | 需 provenance | 视 side_effect |

### 污染边界：Case 06 / 12 / 14

| Case | 污染载体 | 持续范围 | 首要 fix |
|---|---|---|---|
| [Case 06](case-06-prompt-injection.md) | 多轮用户输入 | 当前会话 | session reset |
| [Case 12](case-12-indirect-prompt-injection-tool-abuse.md) | 外部 untrusted content | 单次 tool intent | policy deny |
| Case 14 | 写入长期 memory | **跨任务** | rollback + quarantine |

## 学习记录（自填）

- **Day1 根因猜测**：
- **与 PR/解法对照差距**：
- **口述练习日期 / 用时**：


