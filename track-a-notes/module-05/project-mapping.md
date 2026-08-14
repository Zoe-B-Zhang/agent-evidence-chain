# Case 与主项目映射

**主 Spine**：TrackARuntime（M6 可选叙事扩展：TravelRouteMemo / System Guardian）

至少完成 4 行。

| Case | 若我的系统出现类似现象 | 监控哪里亮红灯 | 我的 trace/eval 证据路径 | 回滚动作 |
|---|---|---|---|---|
| 1 RAG 幻觉 | | | | |
| 2 Prompt 漂移 | 例：v2 prompt 正式度下降 | formality_score | TrackARuntime/m3/evidence/harness-report.json | 回滚 prompts/v1 |
| 3 中间迷失 | | | | |
| 4 时间穿越 | | | | |
| 5 灾难性遗忘 | | | | |
| 6 注入攻击 | | | | |
| 7 延迟雪崩 | tool 超时堆积 | latencyMs P95 | TrackARuntime/m1_m2/evidence/<id>/trace.json | 降级 fallback |
| 8 幸存者偏差 | eval 子集偏差 | gate_pass 分桶 | TrackARuntime/m4/evidence/evaluation-report.md | 暂停全量 |

## 口述练习记录

- **Case ___ + ___**：练习日期 ___，用时 ___ 分钟，自评 ___/5
