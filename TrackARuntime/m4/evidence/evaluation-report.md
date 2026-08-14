# Evaluation Report

- Dataset version: 1
- Success: 10/22 (45.5%)
- Gate (45%): **PASS**
- Baseline source: explicit
- P95 latency: 5 ms

## Category split (retrieval vs generation)

- generation: 8/13 (61.5%)
- mixed: 0/4 (0.0%)
- retrieval: 2/5 (40.0%)

## Failure distribution + remediation

- GUARDRAIL_BLOCK: 3 — [护栏拦截] 检测信号：formality < threshold → 按该轴排查并加回归场景。
- JUDGE_BIAS: 1 — [评测器偏差] 检测信号：judge-human disagreement on regression gate → 按该轴排查并加回归场景。
- MODEL_TIMEOUT: 1 — [模型/路由超时] 检测信号：circuit open → 按该轴排查并加回归场景。
- OVER_EDIT: 1 — [过度修改] 检测信号：diff too large → 按该轴排查并加回归场景。
- PATCH_INVALID: 1 — [输出/补丁无效] 检测信号：apply failed → 按该轴排查并加回归场景。
- PLAN_ERROR: 1 — [计划错误] 检测信号：wrong steps in trace → 按该轴排查并加回归场景。
- REQ_MISREAD: 1 — [需求理解错误] 检测信号：eval assertion fail → 按该轴排查并加回归场景。
- RETRIEVAL_MISS: 1 — [检索/工具选错] 检测信号：wrong file or geocode → 按该轴排查并加回归场景。
- STALE_INDEX: 1 — [检索/索引过期] 检测信号：doc_version lag, stale chunk cited → 按该轴排查并加回归场景。
- TEST_ENV: 1 — [环境失败] 检测信号：timeout, missing dep → 按该轴排查并加回归场景。
