# M4 Day2 — 开方

**日期**：________

> **导师读法**：Day2 设计 **failure taxonomy + scenarios + loop metric stub**。Issue 1 下方为完整示范；Issue 2、3 在总表中对照填写。

## Issue 1 工程化解法（#2643 · loop detection metric）

**方案一句话**：trace-only loop metric = tool+args fingerprint 计数 + reasoning 相似度 + 环检测 → 写入 eval report failure 分布

| 机制 | 我的方案（Issue 1 示范） |
|---|---|
| Tool 重复检测 | hash(tool_name, serialized_args) → count；≥3 次 → `LOOP_TOOL_REPEAT`，score→0（对齐 M1-K06） |
| Reasoning 停滞 | 滑动窗口 cosine ≥0.85 跨 3 step → `LOOP_REASON_STAGNATION`（#2643 sub-signal 2） |
| Call graph 环 | tool 调用 DAG DFS 环 → `LOOP_GRAPH_CYCLE`（L3） |
| Eval 集成 | 在 `runner.py` stub `loop_detection(trace)`；失败时 `failure_code: LOOP_DETECTED` |
| 与在线联动 | 在线 `_check_fingerprint_loop()` fatal；离线 metric **同算法、不同动作**（gate fail vs interrupt） |

**loop_detection stub 设计（M4-I01 Runtime 任务）**

```python
# m4/runner.py — 文档/注释层 stub（L3 可实现）
def loop_detection(events: list) -> tuple[bool, str]:
    """Return (is_loop, reason). Hash (tool, args) like M1 fingerprint."""
    counts: dict[str, int] = {}
    for e in events:
        key = f"{e.get('tool')}:{json.dumps(e.get('input'), sort_keys=True)}"
        counts[key] = counts.get(key, 0) + 1
        if counts[key] >= 3:
            return True, f"tool+args repeated {counts[key]}x: {key[:80]}"
    return False, "ok"
```

**Runtime 任务（issues.md 绑定）**：

```powershell
cd TrackARuntime
# 1. 阅读 failure taxonomy + scenarios
#    m4/failure_taxonomy.md
#    m4/scenarios.json

# 2. 在 runner.py 添加 loop_detection 注释/stub（M4-I01）

# 3. 跑 eval 基线
python cli.py eval
# 证据：m4/evidence/evaluation-report.md → failure_distribution, gate_pass
```

**预期证据**（L2 · 设计层）：

- taxonomy 新增 `LOOP_DETECTED` 或复用 `PLAN_ERROR` 子类说明
- 能对照 M1 run `416be508` trace：相同 `docker_exec.input.command` 出现 3 次
- Day2 stub 伪代码 = M4-K05 L2 证据

**与 TrackARuntime 映射（Issue 1）**

| 文件 | 现状 | Day2 应改什么 |
|---|---|---|
| `m4/runner.py` | 模拟 pass/fail | 注释/stub `loop_detection`；未来读 trace.json |
| `failure_taxonomy.md` | 8 类 | 补充 `LOOP_DETECTED` 检测信号 |
| `scenarios.json` | S09–S18 fail 类 | **S21** 已用于 `STALE_INDEX`（Case 11）；**S23** 计划给 `RETRIEVAL_OK_GEN_FAIL`（#9415，见 [BACKLOG](../case-library/BACKLOG.md)） |
| M1 `loop_engine.py` | 在线 fingerprint | 算法对齐，面试互证 |

---

## 失败分类表（至少 6 类 · Issue 2/3 补充）

见 [`TrackARuntime/m4/failure_taxonomy.md`](../../TrackARuntime/m4/failure_taxonomy.md)，补充项目特有类别：

| 代码 | 描述 | 检测信号 | 对应 Issue |
|---|---|---|---|
| LOOP_DETECTED | Agent trace 空转 loop | 同 tool+args ≥3 次 | #2643, M1-K06 |
| EVAL_JUDGE_FAIL | eval 自身 judge 失败 | invalid JSON / schema 解析错 | #929, M4-K03 |
| RETRIEVAL_OK_GEN_FAIL | 检索命中但生成未用 | chunks 对 + answer 断言 fail | #9415, M4-K04 |
| OBSERVE_STALL | tool observe 永不完成 | 无 end span / idle timeout | M2 #8448 |
| GUARDRAIL_BLOCK | allowlist/护栏拦截 | trace fallback_used | M2-I02 |
| （原有 8 类） | 见 taxonomy 文件 | | |

## 22 场景设计要点

- 场景文件：[`TrackARuntime/m4/scenarios.json`](../../TrackARuntime/m4/scenarios.json)
- 门禁基线成功率：**45.5%**（当前 10 pass / 22；CI baseline **0.45**，见 [`TrackARuntime/README.md`](../../TrackARuntime/README.md)）
- **Issue 3 建议新增**（Learner L3，**计划 S23**）：

```json
{"id": "S23", "task": "answer from retrieved chunk only", "expect": "fail", "failure_code": "RETRIEVAL_OK_GEN_FAIL"}
```

> **注意**：**S21** 已绑定 Case 11 的 `STALE_INDEX`（freshness），与 #9415 的 generation 失败不同。

> **导师提示（Issue 2 Day2 填空）**
>
> 1. 填 **EVAL_JUDGE_FAIL** 行：#929 的三类根因 + fix（model_name、max_tokens、schema enforce）。
> 2. 说明 **gate_pass 与 judge 可靠性**：judge 崩了应 fail closed（block merge），不能 skip。
>
> **导师提示（Issue 3 Day2 填空）**
>
> 1. 填 **RETRIEVAL_OK_GEN_FAIL** 行：检测信号 = retrieval hit + generation faithfulness assert。
> 2. 与 S11 `RETRIEVAL_MISS` 对比——**一个检索层错，一个生成层错**。

## 解法设计（总表）

| 机制 | Issue 1 (#2643) | Issue 2 (#929) | Issue 3 (#9415) |
|---|---|---|---|
| 检测层 | trace loop | eval judge JSON | retrieval vs gen 拆分 |
| taxonomy | LOOP_DETECTED | EVAL_JUDGE_FAIL | RETRIEVAL_OK_GEN_FAIL |
| 门禁 | loop scenario fail | judge fail → gate 不可信 | 拆分 metric 才可信 |
| Runtime | runner stub | structured output | scenarios.json |

## evaluation-report 契约确认

| 字段 | 含义 | Issue 1 示例 |
|---|---|---|
| `success_rate` | 通过率 | 0.6 |
| `gate_pass` | ≥ baseline | true |
| `failure_distribution` | Top 失败码 | OVER_EDIT: 1, ... |
| `p95_latency_ms` | 性能基线 | 对照 Case 7 |
