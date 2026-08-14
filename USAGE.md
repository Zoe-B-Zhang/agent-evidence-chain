# Track A 使用指引

> 面向第一次进入本仓库的学习者：先知道**读什么、跑什么、证明什么**。  
> **学习主轴**在 `track-a-notes/`。可选 **mock 自检模拟**（非主轴、非生产运行时）的目录与命令见 [`STRUCTURE.md`](STRUCTURE.md) · 本节 [§2](#2-可选自检模拟)。  
> 仓库组成见 [`STRUCTURE.md`](STRUCTURE.md)。尚未实现的能力见 [`track-a-notes/case-library/BACKLOG.md`](track-a-notes/case-library/BACKLOG.md)。

---

## 1. 我是谁？该走哪条路？

### 1.0 三种编号：M 模块 · K 点 · P 扩展包

本仓库用三套编号，**层级不同，不要混读**：

| 符号 | 是什么 | 去哪读 | 什么时候看 |
|---|---|---|---|
| **M1–M5** | **模块** — 五条工程生命线（控制面 / 工具 / 配置 / 质量 / 运维） | [`00-knowledge-system`](track-a-notes/curriculum/00-knowledge-system.md) · [`01-course`](track-a-notes/curriculum/01-course.md) 第 N 课 · [`module-0N/`](track-a-notes/module-01/) | **主线学习**：按周推进、模块 Exit |
| **Mx-Kyy** | **K 点** — 模块内可考核的知识工程点（核心 26 个 + 生产扩展 K） | [`module-XX/knowledge.md`](track-a-notes/module-01/knowledge.md) · [`KNOWLEDGE-MAP` §5–§7](track-a-notes/KNOWLEDGE-MAP.md) | **懂机理、做 rubric、Case 啃不动时回退** |
| **P1–P6** | **扩展包** — 求职生产追问主题（**不新增 M6**），定义在 [`02-production-extension-packs`](track-a-notes/curriculum/02-production-extension-packs.md) **§2** | 同上文件 **§3–§8**（每节对应一个 Px） | **核心 M1–M5 Exit 之后**；读 Case 10–18 前先选 Px |

**关系一句话**：**P 挂回 M，K 落在 M 里**——每个 Px 声明主归属模块（如 P1→M3），并引入 **生产扩展 K**（如 M3-K07）；**不替代**核心 26 K 的 Exit 门槛。完整对照见 [`KNOWLEDGE-MAP` §2.5](track-a-notes/KNOWLEDGE-MAP.md)。

**我该看哪个？**

| 你的状态 | 先看 | 再看 | 不要 |
|---|---|---|---|
| 在学第 N 周（主线） | **M{N}** + `01-course` 第 N 课 + **核心 K** | Case **01–08**、OSS 三联 | 不必先读 P1–P6 |
| 核心 Exit 已过（求职） | [`02-production-extension-packs`](track-a-notes/curriculum/02-production-extension-packs.md) **§2 选 P1–P6** | Case **10–18** + 扩展 K（§7.1） | 不要把 P 当成第六门主课 |
| 打开某个 Case | 元数据 **关联模块** → **补强 K 点** → **目标扩展包 Px** | [`§1.1`](#11-case-啃不动先回-curriculum-对标-k-点) 回退顺序 | 不要跳过 K 点直接背故事 |
| 面试前速查 | [`KNOWLEDGE-MAP` §2.5](track-a-notes/KNOWLEDGE-MAP.md) | §5–§7 K 点表 · §11 Case 反查 | — |

所有角色共用**同一条学习栈**——差别只在阶段、Case 范围和证明侧重：

```text
curriculum/00（Why · 模块定位）
  → curriculum/01 第 N 课 + module-XX/knowledge（K 点机理）
  → module-XX/issues（真实 PR 分析）+ case-library（Case / OSS / SOP）
  → rubric / portfolio（Exit 自评 · 面试叙事）
  → （可选）自检模拟 + 物证指读（见 [`STRUCTURE.md`](STRUCTURE.md)）
```

| 你是谁 | 阶段 | Case 范围 | curriculum 入口 | 证明目标 |
|---|---|---|---|---|
| **Track A 主线学习者**（M1–M5 Exit） | 在学第 N 周 | **01–08** + OSS 三联 | [`00-knowledge-system`](track-a-notes/curriculum/00-knowledge-system.md) → [`01-course`](track-a-notes/curriculum/01-course.md) **第 N 课** → [`module-0N/GUIDE`](track-a-notes/module-01/GUIDE.md) | 主轴材料 + rubric；可选 Anchor 物证 |
| **核心 Exit 后求职增强** | 已过关 M1–M5 | **10–18** | [`02-production-extension-packs`](track-a-notes/curriculum/02-production-extension-packs.md) **§2 选 P1–P6** → 回挂 `module-XX/knowledge` | Case + SOP（Anchor 模拟 **计划中**） |
| **面试口述准备** | 任意 | 挑 3–5 个精讲 | [`KNOWLEDGE-MAP`](track-a-notes/KNOWLEDGE-MAP.md) 速查 K 点 ↔ Case | [`demo-script`](portfolio/demo-script.md) 计时口述 |
| **贡献 / 改进** | — | 见 BACKLOG | [`BACKLOG.md`](track-a-notes/case-library/BACKLOG.md) 认领项 | PR / 文档 / Runtime 模拟 |

**统一约定**：

- **curriculum + module-XX** 负责「懂机理、对标 K 点、读真实 PR」；**Case Library** 负责「用事故校准直觉」；**自检模拟**仅为可选自测（不替代主轴 Exit；目录见 [`STRUCTURE.md`](STRUCTURE.md)）。
- K 点主轴覆盖与可选自检对照见根目录 [`README.md` · 主轴 K 点](README.md#主轴-k-点)（表中只写命令，不写目录名）。
- [`METHODOLOGY.md`](track-a-notes/case-library/METHODOLOGY.md) 是 **Case 啃不动时的校准法**（三日挑战 + 系统等价物），不是第一入口——先回 curriculum 补 K 点，再用三日法做实作校准。
- Case **10–18** 是生产扩展 Case，**不计入** M5 深读四 Case；求职增强请读 [`02-production-extension-packs.md`](track-a-notes/curriculum/02-production-extension-packs.md) 中的 **P1–P6**（§2 总览选包 → §3–§8 分节机理 → 回挂 M/K）。

### 1.1 Case 啃不动？先回 curriculum 对标 K 点

Case 不是孤立故事。每个 Case 文件头部的元数据表是**回 curriculum 的索引**：

| 元数据字段 | 去哪补机理 |
|---|---|
| **关联模块**（如 M3、M4） | [`01-course`](track-a-notes/curriculum/01-course.md) **第 N 课**（N=模块号）+ [`module-0N/knowledge.md`](track-a-notes/module-03/knowledge.md) |
| **补强 K 点**（Case 01–18） | [`KNOWLEDGE-MAP`](track-a-notes/KNOWLEDGE-MAP.md) §11 或搜 K 点 ID → 同上 `knowledge.md` 详卡 |
| **目标扩展包**（P1–P6） | [`02-production-extension-packs`](track-a-notes/curriculum/02-production-extension-packs.md) **§2 定位 Px · §3–§8 读机理**（见 [`KNOWLEDGE-MAP` §2.5](track-a-notes/KNOWLEDGE-MAP.md)） |
| **主类 / 次类**（KNW、CTL…） | [`case-library/README`](track-a-notes/case-library/README.md) **分类体系** → 该类「技术点 / 切入方式」 |

**推荐回退顺序**（由快到深）：

```text
1. Case 元数据 → 记下「关联模块」和「补强 K 点」
2. KNOWLEDGE-MAP 搜 K 点 / Case 编号 → 一句话考核句
3. module-XX/knowledge.md 读该 K 的 What / Why / How / Prove
4. curriculum/01 第 N 课 → 模块级机理与过关动作
5. （仅 10–18）curriculum/02 对应 Px → 生产纵深与面试模板
6. 仍抽象 → METHODOLOGY 三日校准 + 对应 OSS Issue + module-XX/issues.md 实作任务
```

**示例**（Case 11 看不懂「stale index」）：

| 步 | 动作 |
|---|---|
| 1 | Case 11 元数据：`关联模块 M4` · `补强 K 点 M4-K06` · `目标扩展包 P2` |
| 2 | [`KNOWLEDGE-MAP`](track-a-notes/KNOWLEDGE-MAP.md) → M4-K06 RAG Eval |
| 3 | [`module-04/knowledge.md`](track-a-notes/module-04/knowledge.md) → K06 详卡 |
| 4 | [`01-course`](track-a-notes/curriculum/01-course.md) 第 4 课 §4.2–4.3（检索 vs 生成拆分） |
| 5 | [`02`](track-a-notes/curriculum/02-production-extension-packs.md) §4 P2（freshness / citation） |
| 6 | 跑 `python cli.py eval --baseline auto` → 看 `STALE_INDEX`（S21） |

主线 Case **01–09** 元数据表均有 **补强 K 点**；也可在 [`KNOWLEDGE-MAP` §11](track-a-notes/KNOWLEDGE-MAP.md) 按 Case 编号反查，或在 [`01-course`](track-a-notes/curriculum/01-course.md) 各章 **§X.0.1** 找课内推荐 Case。

---

## 2. 可选自检模拟

> 本节是**可选自检模拟**的快速命令链（子项目目录见 [`STRUCTURE.md`](../STRUCTURE.md)）。学习主轴请先读 §1；K 点定义在 `track-a-notes/module-XX/`。

在仓库根目录：

```powershell
cd TrackARuntime
pip install -r requirements.txt
python scripts/self_check.py

# M1+M2：控制面 + trace
python cli.py run --task "fix failing test" --llm mock

# M3：灰度回滚
python cli.py harness --prompt v2 --gray-percent 10

# M4：质量门禁（22 场景，见下节数字真源）
python cli.py eval --baseline auto
```

打开证据：

| 模块 | 路径 |
|---|---|
| M1+M2 | `m1_m2/evidence/<run_id>/state.json`、`trace.json`、`metrics-*.json` |
| M3 | `m3/evidence/harness-report.json` |
| M4 | `m4/evidence/evaluation-report.json`、`.md` |

跑完 `run` 后不知道「然后呢」→ 见 **[§2.1 证据文件怎么用](#21-证据文件怎么用m1m2-示例)**（含 `3514fa2f` 指读 checklist 与 M1 命令链）。

**CI 与本地演示的区别**：

| 用途 | baseline | 说明 |
|---|---|---|
| 本地学习 / 校准 | `--baseline auto` | 用历史上次 `success_rate` 校准（夹在 0.4–0.9） |
| **CI 门禁** | `--baseline 0.45` | 见 [`.github/workflows/ci.yml`](.github/workflows/ci.yml) |
| 固定对照实验 | `--baseline 0.45` | 与 CI 一致，便于复现 gate |

完整 Eval 数字真源见 [`STRUCTURE.md`](../STRUCTURE.md) 所链自检子项目 README 的 M4 小节。

### 2.1 证据文件怎么用（M1+M2 示例）

CLI 打印 `state` / `trace` / `metrics` 路径后，**不要停在「文件生成了」**——这三份是 **自检物证**，用来练习指读：Agent 这一轮为何继续、为何停（**是否解读正确由你在主轴材料中自评**，Anchor 不阅卷）。

**三个文件各回答什么**（与 [`01-course` §0.3](track-a-notes/curriculum/01-course.md) 一致）：

| 文件 | 角色 | 优先看谁 | 典型问题 |
|---|---|---|---|
| `state.json` | **叙事** — round / phase / history | 顶层 `success`、`round`、`history[]` | 第几轮 replan？最后一行 `phase` 是什么？为何 DONE？ |
| `trace.json` | **物证** — 每步 tool 调用 | 每条 `tool`、`input`、`output`、`error_class` | 这一轮 **实际** 调了什么？测试失败/通过对应哪条 event？ |
| `metrics-<run_id>.json` | **估算 stub** — token / cost / route | `tokens`、`cost_usd`、`route_decisions` | 本轮大概花了多少 token？走了哪条 model route？（教学记账，非真实账单） |

**推荐阅读顺序**：`state.json`（先懂故事）→ `trace.json`（核对事实）→ `metrics-*.json`（成本/路由口述）。

#### 指读示例：`run 3514fa2f`（`fix failing test`）

假设你刚跑完：

```powershell
python cli.py run --task "fix failing test" --llm mock
# Run 3514fa2f: success=True
```

按下面 checklist 打开 `TrackARuntime/m1_m2/evidence/3514fa2f/`：

| 步 | 打开 | 看什么 | 本 run 要点 |
|---|---|---|---|
| 1 | `state.json` | `success`、`round`、`plan` / `observation` | `round: 2`、`success: true` — 第二轮才成功 |
| 2 | `state.json` → `history` | round1 `observe` → `replan` → round2 `done` | round1：`pytest: 1 failed [retryable]` → 触发 replan；round2：`pytest: 1 passed` → `phase: done` |
| 3 | `trace.json` | 逐步 `tool` 与 `output` | event1 `docker_exec`（盲 patch）→ event2 `run_tests` fail → event3 新 plan 的 `docker_exec` → event4 `run_tests` pass |
| 4 | `metrics-3514fa2f.json` | `tokens`、`cost_usd`、`route_decisions` | 2 次 plan 调用；`route_tier: simple`（M3 路由 stub 的旁路证据） |

**自测（M1 L2，能口述即过关）**：

1. 用 **一句话** 讲清 plan→act→observe→replan 在本 run 里如何发生。
2. 指出 **observe 是 branch 信号**：`[retryable]` 导致 replan，而不是直接 DONE。
3. 说明 `state.json` 与 `trace.json` 的分工：**故事 vs 物证**（见 [`module-01/knowledge` M1-K02](track-a-notes/module-01/knowledge.md)）。
4. （可选）对照 **真 replan** 证据 run `5fb33372` 与 **fatal** run `7c3a04c8` — 见 [`module-01/issues.md`](track-a-notes/module-01/issues.md) I01–I02。

**然后呢？M1 最小命令链**（仍在 `TrackARuntime/`）：

```powershell
# ① 已成功 replan（你刚完成的）
python cli.py run --task "fix failing test" --llm mock

# ② fatal 必须 interrupt，不能当普通 observation 继续
python cli.py run --task "container death" --simulate-container-death 1
# → 对照 7c3a04c8：CLI exit 2；state 无后续 replan

# ③ 可选：checkpoint / resume（M1-I05）
python cli.py run --task "ckpt" --llm mock --checkpoint-dir m1_m2/evidence/checkpoints
# 中断后：--resume-from m1_m2/evidence/checkpoints/<file>.json（须再传 --llm mock）

# ④ 进入 M2：工具边界
python cli.py demo-allowlist --tool rm_rf
python cli.py demo-no-output-hang --idle-timeout 1

# ⑤ 全模块冒烟 + M4 门禁
python cli.py harness --prompt v2 --gray-percent 10
python cli.py eval --baseline auto
```

学完 M1 后填 [`module-01/rubric.md`](track-a-notes/module-01/rubric.md)，面试练 [`interview/DRILLS.md`](track-a-notes/interview/DRILLS.md) 第 1–2 题（指读 `state` / `trace`）。

**其他模块证据**（跑完对应命令后用同样方式「先叙事 / 再事实」）：

| 模块 | 命令 | 打开什么 | 读什么 |
|---|---|---|---|
| M3 | `harness` | `m3/evidence/harness-report.json` | 护栏是否 pass、是否触发 rollback |
| M3 L3 | `harness --watch` | `m3/evidence/rollout-state.json` | 跨 tick 灰度 / 锁定状态 |
| M4 | `eval` | `m4/evidence/evaluation-report.md` | 22 场景通过率、`category_split`、taxonomy 建议 |
| M2 demo | `demo-no-output-hang` | `m1_m2/evidence/m2-8448-demo/` | hang / timeout 的 trace 物证 |

证据 ↔ K 点 ↔ Case 反查见 [`KNOWLEDGE-MAP` §8–§9](track-a-notes/KNOWLEDGE-MAP.md)。

---

## 3. 扩展 Case 10–18 怎么用（先 Px 后 Case）

扩展 Case **不是**学习起点。推荐顺序与 §1 学习栈一致：

```text
curriculum/02 §2 选 Px（扩展包总览）
  → 同节 §3–§8 读机理 + 面试模板
  → module-XX/knowledge 补强 K 点
  → Case 文件（现象校准）
  → SOP + 可选自检物证
```

每个扩展 Case 的证据链：

```text
Px 扩展包（Why / How）
  → Case 元数据「补强 K 点」→ module-XX/knowledge
  → Case 正文（现象 / 根因 / Prove 附表）
  → SOP（值班演习）
  → 自检模拟（能跑则跑，不能跑则设计题；见 STRUCTURE.md）
```

### 推荐阅读顺序（Wave）

| Wave | Px | Case | 先读 curriculum | 最小 Runtime 证据 |
|---|---|---|---|---|
| 1 | P1, P2, P3, P5 | 10, 11, 12, 15 | [`02`](track-a-notes/curriculum/02-production-extension-packs.md) §3–§6 | Case 10：`metrics` + harness；11/15：`eval` S21/S22 |
| 2 | P4, P6 | 13, 14, 16 | 同上 §7–§8 | Case 13：`--checkpoint-dir`；16：`trace`/`metrics` 对照 |
| 3 | P3, P6 | 17, 18 | 同上 §6、§8 | Case 12/18：`demo-allowlist`、`--require-hitl` |

### 与 `scenarios.json` 的绑定（已实现）

| Scenario ID | failure_code | 关联 Case | 验证命令 |
|---|---|---|---|
| **S21** | `STALE_INDEX` | [Case 11](track-a-notes/case-library/cases/case-11-rag-stale-index-hallucination.md) | `python cli.py eval --baseline auto` → 看 `STALE_INDEX` |
| **S22** | `JUDGE_BIAS` | [Case 15](track-a-notes/case-library/cases/case-15-judge-bias-false-regression.md) | 同上 → 看 `JUDGE_BIAS` |

> **注意**：`S21` 表示 **stale index**（Case 11），**不是** oss-9415 的 `RETRIEVAL_OK_GEN_FAIL`。后者计划为 **S23**（尚未实现），见 [`BACKLOG.md`](track-a-notes/case-library/BACKLOG.md)。

### 单个 Case 的学习步骤

1. 读 [`02`](track-a-notes/curriculum/02-production-extension-packs.md) 对应 **Px** 节（扩展包机理）。
2. 读 Case 元数据 **补强 K 点** → [`module-XX/knowledge.md`](track-a-notes/module-03/knowledge.md) 详卡。
3. 读 `track-a-notes/case-library/cases/case-XX-*.md` 的 **场景、根因、Prove 附表**。
4. 读对应 [`sops/sop-case-XX-*.md`](track-a-notes/case-library/sops/)。
5. 跑 **Runtime / Evidence 映射** 中的命令（若有）。
6. 填 Case 末尾 **学习记录**；面试按 **60s / 2min / 5min 口述路径** 练一遍。

---

## 4. 与 OSS / 模块的交叉引用

| 类型 | 入口 |
|---|---|
| OSS 真实事故 | [`case-library/oss-incidents/`](track-a-notes/case-library/oss-incidents/) |
| M1–M5 模块练习 | [`track-a-notes/module-0X/`](track-a-notes/module-01/) |
| 生产扩展 K 点 | [`02-production-extension-packs.md`](track-a-notes/curriculum/02-production-extension-packs.md) |
| K 点速查 | [`KNOWLEDGE-MAP.md`](track-a-notes/KNOWLEDGE-MAP.md) |
| 作品集叙事 | [`portfolio/`](portfolio/)（M6 模板与示例；成稿在 `personal/`） |

---

## 5. 面试 5 分钟 Demo（含 P1 扩展）

见 [`portfolio/demo-script.md`](portfolio/demo-script.md)：

1. `run` → trace + metrics  
2. `harness` → 灰度回滚  
3. `eval` → 22 场景 + taxonomy  
4. **P1 扩展 60s**：口述 Case 10/11/12/15，指向已有 evidence（不必新命令）

---

## 6. 文档索引

| 文件 | 用途 |
|---|---|
| [`README.md`](README.md) | 项目目的（稳定层，少改） |
| **本文件 `USAGE.md`** | 学习路径、命令链、Case 用法 |
| [`STRUCTURE.md`](STRUCTURE.md) | 仓库组成与双层材料 |
| [`case-library/README.md`](track-a-notes/case-library/README.md) | Case 分类 + 索引表 |
| [`case-library/BACKLOG.md`](track-a-notes/case-library/BACKLOG.md) | 尚未完成工作与改进清单 |
| [`case-library/METHODOLOGY.md`](track-a-notes/case-library/METHODOLOGY.md) | 三日校准法 |
| [`portfolio/README.md`](portfolio/README.md) | M6：`templates/` · `examples/` · `personal/`（gitignore） |
| [`AGENTS.md`](AGENTS.md) | AI 编程助手工程约定 |

---

## 变更记录

| 日期 | 变更 |
|---|---|
| 2026-08-09 | 初版（原 `track-a-notes/case-library/USAGE.md`） |
| 2026-08-09 | 迁至仓库根目录；标题改为「Track A 使用指引」 |
| 2026-08-10 | 新增 §1.0 M/K/P 三种编号；P1–P6 明确指向 `02-production-extension-packs`；链至 `KNOWLEDGE-MAP` §2.5 |
| 2026-08-10 | `track-a-notes/portfolio/` 合并入根 `portfolio/` |
| 2026-08-10 | 明确学习主轴为 `track-a-notes/`；§2 标为可选 Anchor 自检 |
