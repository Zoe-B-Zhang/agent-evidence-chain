# 简历片段示例（TrackARuntime · 第三人称 / 可复现数字）

> **示例**：展示如何把 **CLI 物证** 写成简历 bullet；fork 者请复制到 [`../personal/`](../personal/README.md) 后改为第一人称。**非作者真实简历。**

数字来自 2026-08-09 本地证据重跑（可复现）。Eval 数字真源：[`TrackARuntime/README.md`](../../TrackARuntime/README.md)。

## Coding Agent / Agent 平台方向（示例 bullet）

- TrackARuntime 提供可离线复现的 Agent 运行时（plan→act→observe→replan），含工具 allowlist、JSON Schema 校验、指数退避重试与危险操作 HITL 存根；证据落盘为 `state.json` + `trace.json`。
- 可插拔 `LLMClient`（默认 Mock）与 checkpoint/resume；只读沙箱 `read_file`/`grep` 读取仓库文件。
- 模型路由 + token/cost 估算 + rate-limit 降级 stub；示例 run `426ee936`：input **190** / output **40** tokens，估算成本 **$0.000027**，路由 `mock-small`（simple）。
- **22** 场景 golden eval：动态 baseline 校准、taxonomy 修复建议、检索 vs 生成拆分；成功率 **45.5%（10/22）**，gate PASS @ CI baseline **0.45**，P95 **5 ms**。
- Dockerfile + GitHub Actions 串联 `unittest` → `harness` → `eval`。

## 可填数字（证据路径）

| 指标 | 证据路径 | 实测值（2026-08-09） |
|---|---|---|
| Eval 成功率 | `m4/evidence/evaluation-report.json` | 45.5%（10/22）gate PASS @ 0.45 |
| P95 延迟 | 同上 `p95_latency_ms` | 5 ms |
| Token / Cost | `m1_m2/evidence/metrics-426ee936.json` | 190+40 tok，$2.7e-05 |
| Category split | evaluation-report | 见 report `category_split` |
| Unittest | `python -m unittest discover tests` | 本地重跑后填入 personal 版 |
