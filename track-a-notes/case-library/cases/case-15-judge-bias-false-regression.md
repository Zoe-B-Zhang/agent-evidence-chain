# Case 15 — Judge bias 造成误判 regression

| 字段 | 值 |
|---|---|
| **ID** | case-15 |
| **主类** | **MET** |
| **次类** | REL |
| **标签** | judge, eval, calibration, dataset, regression |
| **关联模块** | M4 质量门禁、M3 发布 |
| **M5 深度** | 扩展（求职增强） |
| **SOP** | [sop-case-15](../sops/sop-case-15-judge-bias-false-regression.md) |
| **TrackARuntime** | `python cli.py eval --baseline auto` 含 **S22 judge-bias** 场景；`m4/judge.py` 默认 `DisabledJudge` |
| **OSS 对照** | [oss-929](../oss-incidents/oss-929-deepeval-judge-invalid-json.md) |
| **添加日期** | 2026-08-08 |
| **来源** | oss-929 eval 自身失败思路扩展 + 合成生产事故 |
| **当前状态** | 正式草稿（SOP 已落地；Runtime 可选） |
| **补强 K 点** | M4-K07 Judge Calibration；M4-K08 Dataset Lifecycle |
| **目标扩展包** | P5 Eval Reliability + Red Team |

## 场景

新版本 Agent 在人工抽样中明显更好，但 eval gate 显示 regression。调查发现 LLM-as-Judge 偏好短答案，惩罚了更完整但略长的回答。

## 现象

1. 人工抽样更好，但 eval gate 显示 regression。
2. Judge raw output 偏好短答案，惩罚更完整回答。
3. 发布被阻塞，团队争论是模型退化还是评测器坏了。

## 根因（非表面）

Eval 不是坏在被测 Agent，而是 **Judge rubric 与 human preference 未校准**。Gate 把 judge bias 当成真实 regression。

## 缺失的工程 invariant

Eval 系统本身也需要质量门禁；judge 输出必须与 human label 定期校准。

## 工程解法

- 建 calibration set。
- judge vs human label 一致性统计。
- 高风险变更使用 pairwise eval。
- judge invalid output fail closed。
- dataset / rubric 版本化。

## 系统等价物

CI 测试框架本身 flaky 或 biased：被测代码可能没坏，质检仪先坏了。

## 初级 vs 高级认知

**初级**：看到 eval regression 就回滚 candidate。

**高级（目标）**：先确认 judge / rubric / dataset 版本是否漂移，用 human label、pairwise eval 与 confidence interval 校准 gate。

## 对应 Issue / PR / 校准来源

| 来源 | 链接 | 现象 | 修复点 | 可抽象的工程规则 |
|---|---|---|---|---|
| OSS Issue | [oss-929](../oss-incidents/oss-929-deepeval-judge-invalid-json.md) | eval/judge 自身输出不可靠 | fail closed、结构化校验、校准集 | 质量门禁本身也需要被验证 |
| 合成生产事故 | 本 Case | judge 偏好短答案，误判 regression | human labels、pairwise eval、rubric version | gate 不能只看单一 pass rate |

## What / Why / How 抽取

| K 点 | What | Why | How | Prove |
|---|---|---|---|---|
| M4-K07 | Judge Calibration = LLM-as-Judge 与 human label 的一致性校准 | Judge bias 会误判 regression | calibration set + disagreement review + pairwise eval | Case 15 |
| M4-K08 | Dataset Lifecycle = eval 数据与 rubric 的版本治理 | 随意改 rubric 会污染 baseline | version + changelog + bad case 回流 | eval governance checklist |

## 监控与回滚

- **最先亮的监控层**：judge_human_disagreement_rate、judge_parse_error_rate、dataset/rubric version、pairwise win rate。
- **隔离 / 回滚**：暂停自动 promote；不因单次 judge regression 直接删除候选；先校准 judge/rubric，再决定 rollback / promote。

## SOP 摘要

| 阶段 | 动作 |
|---|---|
| 观察 | 比较 gate result、human sample、judge raw output |
| 隔离 | 暂停自动 promote；切人工 review |
| 定位 | 判断 judge bias、rubric drift、dataset stale、格式错误 |
| 修复验证 | 更新 calibration set；重跑 pairwise eval |
| 复盘 | 记录 judge disagreement，更新 M4 taxonomy |

## Runtime / Evidence 映射

| 类型 | 当前状态 |
|---|---|
| 已有证据 | M4 baseline / judge stub；oss-929 可对照 eval 自身失败 |
| 已有 Runtime | `scenarios.json` S22（`JUDGE_BIAS`）；`python cli.py eval --baseline auto` |
| 面试证明 | judge vs human disagreement table |

## 在本体系中的位置

- **模块**：M4 Judge Calibration 与 Dataset Lifecycle 为主，M3 发布门禁辅助。
- **Issue / runtime 任务**：M4-I05；judge calibration stub 尚未实现。
- **事故来源**：[oss-929](../oss-incidents/oss-929-deepeval-judge-invalid-json.md) 提供 eval 自身失败校准。

## 关联 OSS / Case 区分轴

| 对比项 | [oss-929](../oss-incidents/oss-929-deepeval-judge-invalid-json.md) | Case 15 |
|---|---|---|
| 失败子类型 | judge 输出 **invalid JSON** / 解析失败 | judge **bias**（偏好短答案） |
| 症状 | gate 因格式错误 fail closed | gate 显示 regression，人工抽样更好 |
| 第一信号 | `judge_parse_error_rate` 升高 | `judge_human_disagreement_rate` 升高 |
| 首要 fix | structured output + fail closed | calibration set + pairwise eval |
| 面试一句话 | “评测器坏了，输出都解析不了。” | “评测器没坏透，但判错了。” |

## Prove 附表：judge vs human disagreement

| 样本 | Agent 回答摘要 | Judge 判定 | Human 标注 | 分歧原因 |
|---|---|---|---|---|
| A | 三句完整解释（120 tokens） | fail / score 0.4 | pass | judge 惩罚长度 |
| B | 单词 "yes"（4 tokens） | pass / score 0.9 | fail | judge 奖励过短 |
| C | 带引用段落（80 tokens） | fail / score 0.5 | pass | rubric 未奖励 citation |

## Prove 附表：TrackARuntime eval 路径

```powershell
cd TrackARuntime
python cli.py eval --baseline auto
```

| 组件 | 路径 | Case 15 用途 |
|---|---|---|
| golden scenarios | `m4/scenarios.json` S22（`JUDGE_BIAS`） | 固定 judge 误判 regression 样本 |
| judge stub | `m4/judge.py` → `DisabledJudge` | 默认关闭；生产需 calibration |
| eval 报告 | `m4/evidence/evaluation-report.json` | 看 `failure_distribution.JUDGE_BIAS` |
| taxonomy | `m4/failure_taxonomy.md` | remediation 建议来源 |
| baseline | `m4/baseline.py` `--baseline auto` | 避免随意改 golden 污染 gate |

## 面试口述路径

60s：Eval gate 也需要被评测。  
2min：judge 偏好短答案 → false regression → calibration set 修正。  
5min：画 dataset lifecycle、judge calibration、pairwise eval。

## Prove 附表：judge-bias eval scenario（S22）

已落地到 `TrackARuntime/m4/scenarios.json`：

```json
{
  "id": "S22",
  "task": "eval gate shows regression but human sample prefers candidate",
  "expect": "fail",
  "failure_code": "JUDGE_BIAS",
  "category": "mixed",
  "rubric_version": "v1-short-answer-bias",
  "case_ref": "case-15"
}
```

## 学习记录（自填）

- **Day1 根因猜测**：
- **与 PR/解法对照差距**：
- **口述练习日期 / 用时**：


