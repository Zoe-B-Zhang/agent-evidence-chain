# 仓库组成

> 本文描述**目录与材料分层**，也是 **自检子项目目录名** 的唯一入口说明处。  
> **学习主轴**：[`track-a-notes/`](track-a-notes/) · **怎么用**：[`USAGE.md`](USAGE.md) · **项目目的**：[`README.md`](README.md)

## English overview

This repo is an **agent engineering evidence-chain template**, not a notes dump or a shippable product.

| Layer | Path | Role |
|---|---|---|
| **Spine (notes)** | [`track-a-notes/`](track-a-notes/) | Curriculum, K-points, real PR/OSS analysis, Cases 01–18, SOPs — primary learning material (Chinese) |
| **Mock self-check** | [`TrackARuntime/`](TrackARuntime/) | Offline teaching simulation; CLI writes evidence under `m*/evidence/` — **not** the learning spine |
| **Portfolio** | [`portfolio/`](portfolio/) | M6 interview templates & neutral examples; your drafts in `portfolio/personal/` (gitignored) |

**Naming**: display name *AI Assistant 开发求职* · GitHub repo `agent-evidence-chain` · mock code tree `TrackARuntime/` — see table below.  
**Honest scope**: M1–M4 mock commands exist; P1–P6 extension demos are mostly **planned** ([BACKLOG.md](track-a-notes/case-library/BACKLOG.md)).

---

## 命名约定（避免混读）

| 名称 | 含义 | 去哪看 |
|---|---|---|
| **AI Assistant 开发求职** | 项目**展示名** / 学习体系全名 | [`README.md`](README.md) |
| **`agent-evidence-chain`** | **GitHub 仓库名**（clone URL 用） | [`README.md`](README.md) 副标题 |
| **自检子项目目录** | 对照主轴的 **mock CLI 自测**代码树；**非主轴、非生产运行时** | 下文「TrackARuntime」专节 |

> 根目录其他文档（`USAGE.md`、`CONTRIBUTING.md` 等）**不**把上述三者并列成「三个并列品牌」；需要进代码树时回到本文件。

---

## 材料分层

| 层 | 路径 | 用途 |
|---|---|---|
| **主轴（Notes）** | [`track-a-notes/`](track-a-notes/) | **学习主线**：curriculum、M1–M5、`module-01`…`05`、真实 PR/OSS 分析、Case 库、K 点、SOP、rubric |
| **自检子项目（Anchor）** | [`TrackARuntime/`](TrackARuntime/) | 对主轴知识点的**教学模拟**（mock CLI + 物证），供学习者自测；**不是**学习主轴 |
| **作品集** | [`portfolio/`](portfolio/) | M6 模板与示例；个人成稿在 `portfolio/personal/`（gitignore） |

K 点主轴覆盖与 Anchor 模拟对照见根目录 [`README.md` · 主轴 K 点](README.md#主轴-k-点)。

---

## 目录树

```text
.
├── README.md                 # 项目目的 + 主轴 K 点表
├── LICENSE                   # MIT
├── CONTRIBUTING.md           # 贡献与 evidence 策略
├── USAGE.md                  # 学习指引（主轴路径）
├── STRUCTURE.md              # 本文件
├── AGENTS.md
├── portfolio/                # M6 模板 + 示例；personal/ 本地成稿（gitignore）
├── TrackARuntime/            # Anchor 自检子项目（M1–M4 模拟代码与 evidence）
│   ├── cli.py
│   ├── m1_m2/  m3/  m4/
│   └── tests/
├── track-a-notes/            # ★ 学习主轴
│   ├── curriculum/           # 00 世界观 → 01 教案 → 02 生产扩展
│   ├── case-library/         # Case + OSS 真实 PR 事故 + SOP
│   ├── module-01 … 05/       # 逐模块：knowledge / issues（PR 分析）/ GUIDE
│   ├── KNOWLEDGE-MAP.md
│   ├── MASTERY-RUBRIC.md
│   ├── study-notes/          # 补充概念（Saga、SOP 等）
│   └── tutor/  interview/
└── _archive/                 # 归档计划（已纳入仓库）
```

`temp/` 为本地 handoff / 会话草稿，**不纳入公开仓库**（见根目录 `.gitignore`）。

```text
（本地 only，不提交）
temp/                         # handoff、会话草稿；含已归档的 RESIDENCY-v2-OVERVIEW.md
```

---

## track-a-notes（主轴）要点

| 路径 | 内容 |
|---|---|
| [`curriculum/00-knowledge-system.md`](track-a-notes/curriculum/00-knowledge-system.md) | 五条生命线 + K 矩阵 |
| [`curriculum/01-course.md`](track-a-notes/curriculum/01-course.md) | 主线教案 M1–M5 |
| [`curriculum/02-production-extension-packs.md`](track-a-notes/curriculum/02-production-extension-packs.md) | 求职增强 P1–P6 |
| [`case-library/`](track-a-notes/case-library/) | Case 01–18、**OSS 真实 PR 事故**、SOP |
| [`module-0X/`](track-a-notes/module-01/) | **来自实际 PR 的分析与学习**（knowledge / issues / day 笔记 / rubric） |

---

## TrackARuntime（自检子项目）要点

| 目录 | 对应主轴模块 | CLI 示例 |
|---|---|---|
| `m1_m2/` | M1 控制面 + M2 工具边界 | `run`, `demo-allowlist`, `demo-no-output-hang` |
| `m3/` | M3 配置交付 | `harness` |
| `m4/` | M4 质量门禁 | `eval` |

证据写入各 `m*/evidence/`（CLI 生成，勿手改）。仓库内保留的 evidence 为**教学指读样本**；本地重跑会更新文件，提交前见 [`CONTRIBUTING.md` · evidence 策略](CONTRIBUTING.md#证据文件evidence策略)。详情 [`TrackARuntime/README.md`](TrackARuntime/README.md) · 设计边界 [`DESIGN.md`](TrackARuntime/DESIGN.md)。

---

## CI 与容器

| 阶段 | 入口 |
|---|---|
| 本地自检 | `TrackARuntime/scripts/self_check.py` → `cli.py` |
| CI | [`.github/workflows/ci.yml`](.github/workflows/ci.yml)（验 Anchor 代码回归，非学习者阅卷） |
| 容器 | [`TrackARuntime/Dockerfile`](TrackARuntime/Dockerfile) |

---

## 变更记录

| 日期 | 变更 |
|---|---|
| 2026-08-09 | 从根 `README.md` 拆出；双层材料与目录树独立维护 |
| 2026-08-10 | `track-a-notes/portfolio/` 合并入根 `portfolio/` |
| 2026-08-10 | 明确主轴为 `track-a-notes/`；`TrackARuntime/` 为自检子项目 |
| 2026-08-14 | GitHub 仓库名定为 `agent-evidence-chain`（原规划名 `track-a-runtime` 未发布） |
| 2026-08-12 | 开源上架准备：MIT、`CONTRIBUTING.md`、`.gitignore` 排除 `temp/` |
