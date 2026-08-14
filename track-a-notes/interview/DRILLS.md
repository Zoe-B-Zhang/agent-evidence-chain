# Interview Drills — 面试表达训练

> 每个模块 Exit 前完成对应 drill，记录用时与卡壳点。  
> 证据工程见 [`TrackARuntime/`](../../TrackARuntime/)。

---

## Drill 类型

| 类型 | 时长 | 何时做 |
|---|---|---|
| **D1 — 60s explain** | 60s | 每模块读完 K 点后 |
| **D2 — Debug story** | 3min | 完成 Issue Day3 后 |
| **D3 — Mini system design** | 5min | M4 后 + M6 前 |

---

## M1 Drills

### D1-60s：Agent loop 是什么？

**计时**：____ 秒  
**提纲**（不要背稿，按点说）：
1. 状态机：parse→plan→act→observe→replan
2. 系统等价：工作流 + Saga 补偿
3. 自己例子：`TrackARuntime/m1_m2/evidence/.../state.json` round1 fail → round2 pass

**卡壳点**：

### D2-Debug：#803 silent loop

**STAR**：
- S：container_timeout 后容器已死
- T：agent 仍发命令直到 cost limit
- A：FatalAgentError + save trajectory（对照 PR #807）
- R：runtime `--simulate-container-death` 演示

**计时**：____ 分钟

---

## M2 Drills

### D1-60s：Tool + Trace

- Tool = RPC + allowlist + timeout tier
- TraceEvent 字段各一句
- 指 `m1_m2/evidence/.../trace.json` 一条 event

### D2-Debug：Cline #7355

- 根因：30s SLA 与 build 时长错位
- 修复：分 tier timeout（PR #9159）
- runtime：`_timeouts` 差异

---

## M3 Drills

### D1-60s：Harness 与 Agent 边界

- Harness = 版本 + 灰度 + 护栏 + 回滚
- Case 2：不是删 Prompt，是补交付层
- 演示：`harness --prompt v2 --gray-percent 10`

---

## M4 Drills

### D1-60s：Eval 为何不是「感觉不错」

- 20 固定场景 + taxonomy + gate
- 报数字：成功 X/20，Top3 失败类型

---

## D3 — 5min System Design（M4 后）

**题目**：设计一个最小 Agent Runtime（白板）。

**必须画出的四块**：
1. Loop engine（plan/act/observe/replan）
2. Tool executor（allowlist, timeout）
3. Trace collector
4. Harness + Eval gate

**必须口述的边界**：
- recoverable vs fatal 错误
- 回滚触发条件

**计时**：____ 分钟  
**自评**：/5

---

## M6 — 完整 Demo 脚本（5min）

见 [`../../portfolio/demo-script.md`](../../portfolio/demo-script.md)，改为 **TrackARuntime 路径**：

```powershell
cd TrackARuntime
python cli.py run --task "fix failing test"
python cli.py run --simulate-container-death 1
python cli.py harness --prompt v2 --gray-percent 10
python cli.py eval
```

**演练日期**：____ **总用时**：____ **PASS**：是 / 否

---

## 模拟面试问题库（随机抽 2 题练）

1. 你做到什么程度？L1/L2/L3 + rubric 分数
2. observe 和 log 区别？举 runtime 例子
3. 为什么 #803 比 crash 更贵？
4. Harness 和 RAG 是什么关系？
5. eval 指标和 business 指标如何分开？
6. 讲一个你故意注入失败并回滚的案例

**记录**：

| 日期 | 问题 | 用时 | 自评/5 |
|---|---|---|---|
| | | | |
