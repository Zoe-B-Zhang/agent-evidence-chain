# Case 07 — 全链路「延迟雪崩」

| 字段 | 值 |
|---|---|
| **ID** | case-07 |
| **标签** | trace, timeout, sla, tool-chain |
| **关联模块** | M2, M5 |
| **补强 K 点** | M2-K02 trace 分 span；M2-K04/K05 timeout 两极；M5-K01 五步 SOP；M5-K03 监控五层 + metrics |
| **M5 深度** | **深** |
| **SOP** | [sop-case-07](../sops/sop-case-07-latency-avalanche.md) |
| **TrackARuntime** | `m1_m2/tool_executor.py` 分工具 timeout；`trace.json` 的 `latencyMs` |
| **添加日期** | 2026-07 |

## 场景

车载语音助手，要求语音输入→理解→行动→输出 **全链路 <1.5s**。

## 现象

约 80% 正常，**20% 超时**（尤其需联网搜索时），用户感知「车机卡顿」。

## 根因（非表面）

团队优化 ASR/TTS，却忽略 **LLM TTFT**（首 token 延迟）。长生成时 TTFT 可达 800ms，叠加网络抖动即超时——**瓶颈错位**。

## 系统等价物

只优化前后端，数据库/核心服务 SLA 未治理；全链路用单一 timeout。

## 初级 vs 高级认知

**初级**：全局加大 timeout；换更快模型。

**高级（目标）**：按意图/工具 **分路径 timeout**；分 span 监控 P95（ASR/LLM/TTS/工具）；流式首 token + 降级路径；Cline #7355 类分 tier。

## 监控与回滚

- **监控**：模型层 TTFT P50/P95；工具层 per-tool `latencyMs`。
- **回滚**：关闭重工具/联网路径；切轻量模型。

## 在本体系中的位置

- **M2 核心**；module-02 exit 口述 Case 7 + 工具三层防御。

## 学习记录（自填）

- **Day1 根因猜测**：
- **与 PR/解法对照差距**：
- **口述练习日期 / 用时**：
