# Project Mapping 示例（M5）

> **示例**：对应 `track-a-notes` 中 monitoring-layers / project-mapping 练习；展示如何把生产故障轴映射到 TrackARuntime 可运行证据。

| 生产问题 | 故障轴 | TrackARuntime 等价物 | 证据命令 |
|---|---|---|---|
| Agent 死循环烧 token | CTL | fingerprint ≥3 → FatalAgentError | `run --always-fail-tests --pseudo-replan` |
| 容器已死后仍发命令 | CTL/OBS | `--simulate-container-death` | `run --simulate-container-death 1`（exit 2） |
| 工具越权 / 危险 shell | SEC | allowlist + HITL `confirmed` | `demo-allowlist --tool rm_rf`；`run --require-hitl` |
| grep 无输出挂起 | OBS | observe_stalled | `demo-no-output-hang --idle-timeout 1` |
| Prompt 灰度翻车 | SLO | harness gray + rollback | `harness --prompt v2 --gray-percent 10` |
| 回归质量下降 | MET | eval gate + baseline auto | `eval --baseline auto` |
| 成本不可见 | SLO/MET | token/cost metrics | `run` → `metrics-*.json` |
| 模型超时/降级 | REL | model_router + rate_limiter | 见 metrics 中 `route_tier` / `rate_limited` |

## 面试口述模板

「线上出现 X → 我在 Runtime 用 Y 命令复现 → 从 Z 证据字段证明根因在控制面/边界/门禁，而不是换模型。」
