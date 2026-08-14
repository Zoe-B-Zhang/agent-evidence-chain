# Demo Script（约 5 分钟）

## 0. 开场（30s）

「TrackARuntime 是一个教学向的 Agent 工程骨架，覆盖控制面、工具边界、配置交付、质量门禁四条代码生命线。下面用三条命令证明它可复现。」

## 1. Agent Loop + Trace（90s）

```powershell
cd TrackARuntime
python cli.py run --task "fix failing test" --llm mock
```

口述要点：
1. Round1 失败 → Round2 replan 成功。
2. 打开 `m1_m2/evidence/<run_id>/state.json` 指 Phase 历史。
3. 打开 `trace.json` 指 allowlist 工具与 latency。
4. 指 `metrics-*.json` 的 token/cost 估算。

可选加戏：

```powershell
python cli.py run --task "container death" --simulate-container-death 1
```

说明 FatalAgentError + 退出码 2（Issue #803 类故障注入）。

## 2. Harness 灰度回滚（60s）

```powershell
python cli.py harness --prompt v2 --gray-percent 10
python cli.py harness --prompt v1 --gray-percent 0
```

口述：v2 formality 不过 → rollback；v1 通过。强调「配置交付」而非只改 Prompt。

## 3. Eval Gate（60s）

```powershell
python cli.py eval --baseline auto
```

口述：22 场景（含 S21 stale-index、S22 judge-bias）、taxonomy 修复建议、retrieval/generation 拆分。本地演示用 `--baseline auto`；**CI 门禁**用 `--baseline 0.45`（见 [`TrackARuntime/README.md`](../TrackARuntime/README.md)）。

## 4. P1 扩展包口述（60s · 求职增强）

不跑新命令，用已有 evidence 串 Case 10 / 11 / 12 / 15：

| Case | 一句话 | 指向证据 |
|---|---|---|
| [Case 10](../track-a-notes/case-library/cases/case-10-provider-rate-limit-fallback.md) | 429 不是 blind retry，要 quota-aware fallback | `metrics-*.json` + harness 灰度 |
| [Case 11](../track-a-notes/case-library/cases/case-11-rag-stale-index-hallucination.md) | RAG 要拆 freshness / citation，不是换大模型 | eval 报告里 `STALE_INDEX`（S21） |
| [Case 12](../track-a-notes/case-library/cases/case-12-indirect-prompt-injection-tool-abuse.md) | 模型输出不是授权，tool 要过 policy | `demo-allowlist` + policy 表 |
| [Case 15](../track-a-notes/case-library/cases/case-15-judge-bias-false-regression.md) | eval gate 本身要被校准 | eval 报告里 `JUDGE_BIAS`（S22） |

## 5. 收尾（30s）

「CI 与 Docker 复现同一路径：`unittest` → `harness` → `eval`。和 Cursor/Claude Code 的差距在真实模型与写工具，但控制面与门禁机制是可迁移的。」
