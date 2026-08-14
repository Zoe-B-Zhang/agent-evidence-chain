# 模块 4 学习指南：Eval

> **导师补充**：知识工程点 [`M4-K01–K05`](knowledge.md) · 精选 Issue [`M4-I01–I03`](issues.md) · 评分 [`rubric.md`](rubric.md)

## 本模块在系统中的位置

| | |
|---|---|
| **生命线** | ④ **质量门禁** — 行为质量数据证明、merge block |
| **依赖** | M3（Harness 在线 vs Eval 离线互补） |
| **主证据** | `evaluation-report.md` / `.json` |
| **体系详述** | [`KNOWLEDGE-SYSTEM.md` §7 M4](../curriculum/00-knowledge-system.md) · [`COURSE.md` 第 4 课](../curriculum/01-course.md) |

## 原理（3 分钟版）

Eval = 固定任务集 + 自动执行 + 失败分类 + 回归门禁。

| 概念 | 系统等价 |
|---|---|
| Benchmark | 集成测试套件 |
| 失败 taxonomy | 错误码分类 |
| baseline auto | 动态门槛 / 历史校准 |
| 回归门禁 | CI block merge |

**诚实句**：TrackARuntime 的 `eval` 对 scenario 做 **`_simulate`**，不跑真实 Agent loop；`trace_eval` 模块存在但 **未写入** eval 报告（见 knowledge M4-K05）。

## OSS 阅读清单

1. **SWE-bench**：任务定义与 pass@k
2. **DeepEval**：metric 设计
3. **Ragas**：faithfulness（概念级）

## 三日校准（导师指定 Issue）

| 天 | 任务 | 链接 |
|---|---|---|
| Day1 主修 1 | loop 检测 metric 缺口 | [DeepEval #2643](https://github.com/confident-ai/deepeval/issues/2643) · [M4-I01](issues.md) |
| Day1 主修 2 | eval judge JSON 失败 | [DeepEval #929](https://github.com/confident-ai/deepeval/issues/929) |
| Day1 主修 3 | 检索对、答错 | [RAGFlow #9415](https://github.com/infiniflow/ragflow/issues/9415) · [M4-I02](issues.md) |
| Day2 | taxonomy + baseline auto | [M4-I03](issues.md) · [`TrackARuntime/m4/`](../../TrackARuntime/m4/) |

## 关联 Bad Case

- Case 1、4、8

## TrackARuntime（主线）

```powershell
cd TrackARuntime
python cli.py eval --baseline auto
# 对照 CI：python cli.py eval --baseline 0.45
```

见 [`TrackARuntime/README.md`](../../TrackARuntime/README.md)
