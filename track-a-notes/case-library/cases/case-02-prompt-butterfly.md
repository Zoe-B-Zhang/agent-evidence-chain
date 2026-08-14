# Case 02 — Prompt「蝴蝶效应」

| 字段 | 值 |
|---|---|
| **ID** | case-02 |
| **标签** | harness, prompt, guardrail, ab-test |
| **关联模块** | M3, M5 |
| **补强 K 点** | M3-K02 Prompt 版本化；M3-K03 formality 护栏；M3-K04 rollback；M5-K01 五步 SOP；M5-K04 project-mapping |
| **M5 深度** | **深** |
| **SOP** | [sop-case-02](../sops/sop-case-02-prompt-butterfly.md) |
| **TrackARuntime** | `python cli.py harness --prompt v2 --gray-percent 10` → `rollback_to_v1` |
| **添加日期** | 2026-07 |

## 场景

跨境电商客服邮件自动回复。上周满意度 92%，本周跌至 40%。

## 现象

回复变得「过于热情、用词夸张」，像微商话术。

## 根因（非表面）

产品经理在 System Prompt 增加一句 “You are a warm and enthusiastic assistant”。在 temperature 不变时，**语义偏移**改变输出分布熵，整体风格从「中性专业」滑向「过度营销」——小改动、大分布变化（蝴蝶效应）。

## 系统等价物

配置热更新无灰度、无回归测试；生产直接改全局配置项。

## 初级 vs 高级认知

**初级**：删掉 “warm”，改回旧 Prompt。

**高级（目标）**：Prompt **版本化** + changelog；灰度 + **护栏指标**（正式度/风格向量）；eval 集覆盖语义偏移维度；全量前多指标共识（见 Case 8）。

## 监控与回滚

- **监控**：模型层 formality_score；业务层满意度、投诉关键词。
- **回滚**：`prompts/v1` 全量；v2 废弃直至 eval 通过。

## 在本体系中的位置

- **M3 核心**：Harness 叙事主案例；M3-I02 runtime 任务。
- **M5 深做**：project-mapping + harness-report 证据。

## 学习记录（自填）

- **Day1 根因猜测**：
- **与 PR/解法对照差距**：
- **口述练习日期 / 用时**：
