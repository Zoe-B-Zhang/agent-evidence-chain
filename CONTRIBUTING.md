# 贡献指南

感谢关注 **AI Assistant 开发求职**（GitHub 仓库名：`agent-evidence-chain`）。本仓库是**教学 / 能力验证型**项目，不是生产 Agent 服务。

## 开始前

1. 阅读 [`README.md`](README.md) 与 [`USAGE.md`](USAGE.md)：**学习主轴**在 `track-a-notes/`；可选自检模拟的目录与边界见 [`STRUCTURE.md`](STRUCTURE.md)。
2. 若需改自检模拟代码或跑通 CLI，进入 `STRUCTURE.md` 所述自检子项目目录后：

```powershell
pip install -r requirements.txt
python scripts/self_check.py
python -m unittest discover tests
```

3. 改进待办见 [`track-a-notes/case-library/BACKLOG.md`](track-a-notes/case-library/BACKLOG.md)。

## 证据文件（evidence）策略

自检模拟生成的 `m*/evidence/` 下 JSON/MD **由 CLI 自动生成**，规则如下：

| 规则 | 说明 |
|---|---|
| **勿手改** | 证据用于复盘与 CI 对照；手动编辑会破坏可复现性 |
| **仓库内保留示例** | 当前提交的 evidence 是**教学指读样本**（如 `metrics-426ee936.json`、最新 `evaluation-report.*`） |
| **本地运行会更新** | 每次 `run` / `harness` / `eval` 可能改写或新增文件；提交 PR 前请只 stage 与本次改动相关的 evidence，或还原无关 diff |
| **CI 会重跑** | GitHub Actions 在干净环境执行 unittest、harness、eval；不依赖你本地的 run_id |

若新增 CLI 子命令或改变 evidence schema，请同步更新 `STRUCTURE.md` 所指向的自检文档、`USAGE.md` 与相关测试。

## 贡献类型

| 类型 | 落点 | 注意 |
|---|---|---|
| 自检模拟行为 / bugfix | 见 [`STRUCTURE.md`](STRUCTURE.md) 自检子项目 | 保持离线、无网络、最小依赖（仅 PyYAML） |
| 新 Case / SOP | `track-a-notes/case-library/` | 对齐 `cases/_TEMPLATE.md` |
| **OSS 校准来源**（Issue / PR 链接） | 见 [`HOW-TO-ADD-OSS-CALIBRATION.md`](track-a-notes/case-library/HOW-TO-ADD-OSS-CALIBRATION.md) | 先写 `oss-incidents/`，再反链 Case / `issues.md` |
| K 点 / 课程 | `track-a-notes/module-XX/`、`curriculum/` | 同步 `KNOWLEDGE-MAP.md` |
| 规划中的 demo CLI | 见 BACKLOG | **不要**在文档中写成已存在命令 |

## 文档与 Case 约定

- 模块 docstring 与文档使用中文；代码标识符使用英文。
- Case 内写「SOP 摘要」，正式 SOP 放在 `track-a-notes/case-library/sops/`。
- 生产扩展 K 点回填时同步：`knowledge.md`、`issues.md`、`KNOWLEDGE-MAP.md`、相关 Case 链接。
- **增补真实 OSS Issue/PR 链接**：遵循 [`track-a-notes/case-library/HOW-TO-ADD-OSS-CALIBRATION.md`](track-a-notes/case-library/HOW-TO-ADD-OSS-CALIBRATION.md)（含 Case 10–18 认领表）。
- **根目录入口文档**（`README.md`、`USAGE.md`、`CONTRIBUTING.md`）勿将自检子项目目录与仓库名、展示名并列；目录真源见 [`STRUCTURE.md`](STRUCTURE.md)。

## Pull Request 检查清单

- [ ] `python -m unittest discover tests` 通过（在自检子项目目录下，见 `STRUCTURE.md`）
- [ ] 若改 harness/eval 路径，`python cli.py eval --baseline 0.45` 通过
- [ ] 未提交 `temp/`、`.env`、无关 evidence 噪音
- [ ] 文档中的 CLI 命令与自检子项目 `cli.py` 一致
- [ ] 未引入 openai/pytest 等新依赖（除非议题明确要求）

## 许可

贡献即表示同意以 [MIT License](LICENSE) 授权你的改动。
