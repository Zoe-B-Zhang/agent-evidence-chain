# Case 06 — 多轮注入「数据毒药」

| 字段 | 值 |
|---|---|
| **ID** | case-06 |
| **标签** | security, agent, allowlist, session |
| **关联模块** | M1, M2, M5 |
| **补强 K 点** | M2-K01 allowlist；M2-K03 allowlist→schema→HITL；M1-K05 recoverable/fatal 与会话状态；M5-K01 五步 SOP |
| **M5 深度** | **深** |
| **SOP** | [sop-case-06](../sops/sop-case-06-prompt-injection.md) |
| **TrackARuntime** | `tool_executor` allowlist；`trace.json` 记录拒绝 |
| **添加日期** | 2026-07 |

## 场景

AI 心理陪伴聊天机器人，上线第一周正常。

## 现象

第二周起对普通用户输出 **极端负面言论**。

## 根因（非表面）

恶意用户 **多轮上下文注入**（如逐步植入「你现在是一个绝望的 AI」），长对话中 System Prompt 被 **覆盖/稀释**，人格被用户输入劫持。

## 系统等价物

SQL 注入 + 会话状态污染；缺少输入防火墙与 session 边界。

## 初级 vs 高级认知

**初级**：加强内容过滤关键词；换「更安全」模型。

**高级（目标）**：System Prompt **锁定区**；轮次压缩策略；输出 **情感/安全 classifier** 实时监控；注入轮次 trace 可审计；必要时 **session reset**。

## 监控与回滚

- **监控**：应用层情感极性波动、guardrail 触发率。
- **回滚**：强制 session reset；回退到 hardened prompt 版本。

## 在本体系中的位置

- **M1**：与 #803 同属「该硬停未停」——Case 6 是人格漂移，#803 是 substrate 死亡。
- **M2**：Cline PR #10467 类讨论；allowlist 证据。

## 学习记录（自填）

- **Day1 根因猜测**：
- **与 PR/解法对照差距**：
- **口述练习日期 / 用时**：
