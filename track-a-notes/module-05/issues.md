# M5 精选 Issue（第 5 周 · 4 深 + 4 浅）

> 索引：[tutor/README.md](../tutor/README.md) · 知识工程点：[knowledge.md](knowledge.md)

| 深度 | Case | Issue / 材料 | Runtime 映射 |
|---|---|---|---|
| 深 | 2 蝴蝶 | M3 harness v2 | harness-report；建议兼看 metrics |
| 深 | 3 中间迷失 | LlamaIndex #9371 概念 | replan / context 策略（文档） |
| 深 | 6 注入 | [Cline PR #10467](https://github.com/cline/cline/pull/10467) 讨论 | allowlist / schema / HITL（M2） |
| 深 | 7 延迟 | M2 #7355 | trace latency_ms；metrics |
| 浅 | 1,4,5,8 | SOP 速读 | monitoring-layers 填一行 |
| 生产扩展 | [Case 10](../case-library/cases/case-10-provider-rate-limit-fallback.md) | [SOP](../case-library/sops/sop-case-10-provider-rate-limit-fallback.md) | provider 429 / quota / fallback 响应 |
| 生产扩展 | [Case 11](../case-library/cases/case-11-rag-stale-index-hallucination.md) | [SOP](../case-library/sops/sop-case-11-rag-stale-index-hallucination.md) | stale index / freshness / citation 响应 |
| 生产扩展 | [Case 12](../case-library/cases/case-12-indirect-prompt-injection-tool-abuse.md) | [SOP](../case-library/sops/sop-case-12-indirect-prompt-injection-tool-abuse.md) | security incident / tool policy 响应 |
| 生产扩展 | [Case 13](../case-library/cases/case-13-worker-death-checkpoint-resume.md) | [SOP](../case-library/sops/sop-case-13-worker-death-checkpoint-resume.md) | worker death / lease / checkpoint resume 响应 |
| 生产扩展 | [Case 14](../case-library/cases/case-14-memory-poisoning-version-rollback.md) | [SOP](../case-library/sops/sop-case-14-memory-poisoning-version-rollback.md) | memory poisoning / rollback 响应 |
| 生产扩展 | [Case 15](../case-library/cases/case-15-judge-bias-false-regression.md) | [SOP](../case-library/sops/sop-case-15-judge-bias-false-regression.md) | eval gate / judge calibration 响应 |
| 生产扩展 | [Case 16](../case-library/cases/case-16-observability-cardinality-alert-fatigue.md) | [SOP](../case-library/sops/sop-case-16-observability-cardinality-alert-fatigue.md) | telemetry cardinality / alert 响应 |
| 生产扩展 | [Case 17](../case-library/cases/case-17-secret-leakage-through-tool-trace.md) | [SOP](../case-library/sops/sop-case-17-secret-leakage-through-tool-trace.md) | secret leakage / redaction / rotation 响应 |
| 生产扩展 | [Case 18](../case-library/cases/case-18-approval-fatigue-destructive-action.md) | [SOP](../case-library/sops/sop-case-18-approval-fatigue-destructive-action.md) | approval fatigue / destructive action 响应 |

> **无对应 Issue**：`metrics-*.json` 专项演习、成本硬熔断、bad-case 自动写入 `scenarios.json`——见 [`knowledge.md`](knowledge.md) M5-K03 / K04 标注。

## 生产扩展 SOP 使用方式

| 练习目标 | 先读 | 复盘输出 |
|---|---|---|
| Provider / 成本 / 配额止血 | [sop-case-10](../case-library/sops/sop-case-10-provider-rate-limit-fallback.md) | 429 率、quota、fallback route、rollback 记录 |
| RAG stale index 排障 | [sop-case-11](../case-library/sops/sop-case-11-rag-stale-index-hallucination.md) | index freshness、citation support、stale scenario |
| 安全事件响应 | [sop-case-12](../case-library/sops/sop-case-12-indirect-prompt-injection-tool-abuse.md) | tool provenance、policy deny、approval audit |
| Worker death 恢复 | [sop-case-13](../case-library/sops/sop-case-13-worker-death-checkpoint-resume.md) | lease、checkpoint、idempotency、DLQ |
| Memory poisoning 回滚 | [sop-case-14](../case-library/sops/sop-case-14-memory-poisoning-version-rollback.md) | memory source、scope、version、rollback |
| Eval gate 误判 | [sop-case-15](../case-library/sops/sop-case-15-judge-bias-false-regression.md) | judge-human disagreement、rubric / dataset version |
| Observability 告警失效 | [sop-case-16](../case-library/sops/sop-case-16-observability-cardinality-alert-fatigue.md) | label cardinality、SLO dashboard、alert dedupe |
| Secret 泄露响应 | [sop-case-17](../case-library/sops/sop-case-17-secret-leakage-through-tool-trace.md) | secret detector、redaction、provider-bound policy、rotation |
| Approval fatigue 响应 | [sop-case-18](../case-library/sops/sop-case-18-approval-fatigue-destructive-action.md) | risk tier、approval transcript、dry-run、undo |
