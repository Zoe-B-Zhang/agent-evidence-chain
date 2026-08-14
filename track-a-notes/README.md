# 轨道 A 学习笔记索引

**入口**：[`curriculum/00-knowledge-system.md`](curriculum/00-knowledge-system.md) · 使用指引：[`USAGE.md`](../USAGE.md)

## 目录结构

```text
track-a-notes/
├── curriculum/          # 课程体系（先 00 再 01；求职增强读 02）
│   ├── 00-knowledge-system.md   # Greenhand 第一站：世界观 + 26 K 矩阵
│   ├── 01-course.md               # 主读教案：机理 + 过关动作
│   ├── 02-production-extension-packs.md # 求职增强：P1–P6 生产扩展包
│   └── study-notes/     # → 已迁移，见根目录 study-notes/
├── study-notes/         # 补充概念（Saga、五步 SOP 等）
├── tutor/               # 导师规范：K 点 Level + Issue 选材
├── interview/           # 面试实战：60s / debug / 5min design
├── case-library/        # Case 01–18 + OSS + SOP（已对齐 _TEMPLATE.md；可选 Runtime 未实现）
├── module-01 … 05/      # 逐模块 GUIDE · knowledge · issues · day1–3 · exit
├── KNOWLEDGE-MAP.md     # 纯索引速查
├── MASTERY-RUBRIC.md    # 0–3 分评分
```

## 学习路径（按顺序）

| 顺序 | 文档 | 用途 |
|---|---|---|
| 0 | [`curriculum/00-knowledge-system.md`](curriculum/00-knowledge-system.md) | **世界观**：五条生命线 + 覆盖度 + 26 K 矩阵 |
| 1 | [`curriculum/01-course.md`](curriculum/01-course.md) | **教案**：逐课机理、过关动作 |
| 2 | [`curriculum/02-production-extension-packs.md`](curriculum/02-production-extension-packs.md) | **求职增强**：LLM Gateway、RAG、安全、Runtime Scale、Eval 可信度、Observability |
| 3 | [`KNOWLEDGE-MAP.md`](KNOWLEDGE-MAP.md) | **速查**：考核句、术语、命令 |
| 4 | [`tutor/README.md`](tutor/README.md) | **导师规范**：L1/L2/L3 + Issue 选材 |
| 5 | [`MASTERY-RUBRIC.md`](MASTERY-RUBRIC.md) | **评分**：0–3 分 |
| 6 | [`interview/DRILLS.md`](interview/DRILLS.md) | **面试 drill** |
| — | [`case-library/README.md`](case-library/README.md) | Case + OSS + SOP；[`USAGE.md`](../USAGE.md) · [`BACKLOG`](case-library/BACKLOG.md) |
| — | [`../portfolio/README.md`](../portfolio/README.md) | **M6** 作品集：case study · demo · 简历 |

**学习闭环**：`curriculum/00` → `curriculum/01` 对应章 → `module-XX/knowledge.md` → Issue Day1–3 → **改 TrackARuntime** → rubric → interview drill → exit。核心 Exit 后读 `curriculum/02`，把生产级岗位追问补到作品集叙事。

**Cursor 预览**：跨文件 `#锚点` 不可靠；从 GUIDE 直链同目录 `knowledge.md` / `issues.md` / `rubric.md`。

## 模块 GUIDE

| 模块 | GUIDE | 三件套 | TrackARuntime |
|---|---|---|---|
| M1 | [GUIDE](module-01/GUIDE.md) | [K](module-01/knowledge.md) · [I](module-01/issues.md) · [R](module-01/rubric.md) | `cli.py run` |
| M2 | [GUIDE](module-02/GUIDE.md) | [K](module-02/knowledge.md) · [I](module-02/issues.md) · [R](module-02/rubric.md) | trace |
| M3 | [GUIDE](module-03/GUIDE.md) | [K](module-03/knowledge.md) · [I](module-03/issues.md) · [R](module-03/rubric.md) | `cli.py harness` |
| M4 | [GUIDE](module-04/GUIDE.md) | [K](module-04/knowledge.md) · [I](module-04/issues.md) · [R](module-04/rubric.md) | `cli.py eval` |
| M5 | [GUIDE](module-05/GUIDE.md) | [K](module-05/knowledge.md) · [I](module-05/issues.md) | mapping |
| M6 | [`portfolio/README.md`](../portfolio/README.md) | [MASTERY-RUBRIC](MASTERY-RUBRIC.md) M6 行 | demo |

## 进度追踪

| 模块 | Rubric | Day1 | Day2 | Day3 | Exit | Runtime |
|---|---|---|---|---|---|---|
| M1 | [rubric](module-01/rubric.md) | [day1](module-01/module-01-day1.md) | [day2](module-01/module-01-day2.md) | [day3](module-01/module-01-day3.md) | [exit](module-01/module-01-exit.md) | `cli.py run` |
| M2 | [rubric](module-02/rubric.md) | [day1](module-02/module-02-day1.md) | [day2](module-02/module-02-day2.md) | [day3](module-02/module-02-day3.md) | [exit](module-02/module-02-exit.md) | trace |
| M3 | [rubric](module-03/rubric.md) | [day1](module-03/module-03-day1.md) | [day2](module-03/module-03-day2.md) | [day3](module-03/module-03-day3.md) | [exit](module-03/module-03-exit.md) | `cli.py harness` |
| M4 | [rubric](module-04/rubric.md) | [day1](module-04/module-04-day1.md) | [day2](module-04/module-04-day2.md) | [day3](module-04/module-04-day3.md) | [exit](module-04/module-04-exit.md) | `cli.py eval` |
| M5 | — | [day1](module-05/module-05-day1.md) | [day2](module-05/module-05-day2.md) | [day3](module-05/module-05-day3.md) | [exit](module-05/module-05-exit.md) | mapping |
| M6 | [MASTERY](MASTERY-RUBRIC.md) | — | — | — | [`portfolio/`](../portfolio/) | demo |

## 总复盘

[`RETROSPECTIVE.md`](RETROSPECTIVE.md)
