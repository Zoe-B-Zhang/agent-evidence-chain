# Failure Taxonomy (TrackARuntime M4)

| Code | Category | Detection signal |
|---|---|---|
| RETRIEVAL_MISS | 检索/工具选错 | wrong file or geocode |
| PLAN_ERROR | 计划错误 | wrong steps in trace |
| PATCH_INVALID | 输出/补丁无效 | apply failed |
| TEST_ENV | 环境失败 | timeout, missing dep |
| OVER_EDIT | 过度修改 | diff too large |
| REQ_MISREAD | 需求理解错误 | eval assertion fail |
| GUARDRAIL_BLOCK | 护栏拦截 | formality < threshold |
| MODEL_TIMEOUT | 模型/路由超时 | circuit open |
| STALE_INDEX | 检索/索引过期 | doc_version lag, stale chunk cited |
| JUDGE_BIAS | 评测器偏差 | judge-human disagreement on regression gate |
