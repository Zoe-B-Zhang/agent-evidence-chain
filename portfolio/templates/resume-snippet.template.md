# 简历片段（TrackARuntime）

> **模板**：复制到 [`../personal/resume-snippet.md`](../personal/README.md) 后按你的经历改写。**`personal/` 已 gitignore，勿提交公开仓。**  
> 数字须本地重跑 CLI 填入；可参考 [`../examples/resume-snippet.example.md`](../examples/resume-snippet.example.md) 的写法与证据路径。

## Coding Agent / Agent 平台方向

- [ bullet：Agent loop + 工具边界 + 证据落盘 ]
- [ bullet：LLMClient / checkpoint ]
- [ bullet：路由 / token / cost ]
- [ bullet：golden eval + baseline gate ]
- [ bullet：CI / Docker 叙事 ]

## 可填数字（证据路径）

| 指标 | 证据路径 | 实测值（本地重跑） |
|---|---|---|
| Eval 成功率 | `TrackARuntime/m4/evidence/evaluation-report.json` | |
| P95 延迟 | 同上 `p95_latency_ms` | |
| Token / Cost | `TrackARuntime/m1_m2/evidence/metrics-<run_id>.json` | |
| Category split | evaluation-report | |
| Unittest | `python -m unittest discover tests` | |
