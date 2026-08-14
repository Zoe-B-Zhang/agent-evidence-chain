# Personal — 个人成稿（不提交公开仓）

本目录用于存放 **第一人称求职材料**（STAR case study、LinkedIn 段落、你的简历 bullet、postmortem 等）。

## 用法

1. 从 [`../templates/`](../templates/) 复制对应 `*.template.md` 到本目录。
2. 去掉文件名中的 `.template`（例如 `case-study-01.template.md` → `case-study-01.md`）。
3. 填入个人叙事与本地重跑 CLI 后的数字。
4. 参考 [`../examples/`](../examples/) 的写法；**勿直接提交 examples 当简历**。

## 建议文件清单（M6 Exit）

| 文件 | 来源模板 |
|---|---|
| `case-study-01.md` | [`templates/case-study-01.template.md`](../templates/case-study-01.template.md) |
| `case-study-02.md` | [`templates/case-study-02.template.md`](../templates/case-study-02.template.md) |
| `case-study-03.md` | [`templates/case-study-03.template.md`](../templates/case-study-03.template.md) |
| `postmortem-01.md` | [`templates/postmortem.template.md`](../templates/postmortem.template.md) |
| `linkedin-project-paragraph.md` | [`templates/linkedin-project-paragraph.template.md`](../templates/linkedin-project-paragraph.template.md) |
| `resume-snippet.md` | [`templates/resume-snippet.template.md`](../templates/resume-snippet.template.md) |

## Git

根目录 `.gitignore` 忽略 `portfolio/personal/*`，**仅本 README 可跟踪**。你的成稿只留在本地或私有 fork。
