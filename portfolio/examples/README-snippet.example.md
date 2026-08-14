# README Snippet 示例（Can / Cannot / Eval）

> **示例**：复制到个人作品集仓库 README 或 [`../personal/`](../personal/README.md) 后按需改写。  
> **English**: Use this block on GitHub or in a personal repo README — it states scope honestly so reviewers do not mistake the mock runtime for production.

## What this assistant can do

- Plan–act–observe–replan agent loop with persisted `state.json` / trace
- Tool execution with allowlist, per-tool timeout, structured `TraceEvent`
- Harness: prompt versions, formality guardrails, gray release simulation, rollback
- Eval: 22-scenario benchmark, failure taxonomy, regression gate

## What it cannot do

- Not a production agent platform or hosted service
- Not a general-purpose autonomous software engineer
- Not a production RAG / document QA platform (RAG covered at interview concept level only; P2 extension demos mostly planned — see [BACKLOG](../../track-a-notes/case-library/BACKLOG.md))
- Not fine-tuning or training foundation models
- No live LLM provider, vector DB, distributed queue, or OTel/alerting backend

## How it is evaluated

```bash
cd TrackARuntime && python cli.py eval --baseline auto
```

See `TrackARuntime/m4/evidence/evaluation-report.md` for success rate, failure distribution, P95 latency.

## Where it fails (honest)

| Failure code | Meaning |
|---|---|
| GUARDRAIL_BLOCK | Output failed deterministic validators |
| STALE_INDEX | Stale retrieval index cited |
| JUDGE_BIAS | Judge-human disagreement on regression gate |
| RETRIEVAL_MISS | Wrong tool/file selected |
| PLAN_ERROR | Plan without sufficient observation |

Full taxonomy: `TrackARuntime/m4/failure_taxonomy.md`

## Architecture

See [`track-a-notes/README.md`](../../track-a-notes/README.md) and [`USAGE.md`](../../USAGE.md).
