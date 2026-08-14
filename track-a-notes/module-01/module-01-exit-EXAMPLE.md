# M1 Exit — 示例（TrackARuntime 跑通后参考）

> 本文件为**参考范例**；你的自证请写在 `module-01-exit.md`。

## 原理口述稿

Agent 是有状态任务机：parse → plan → act → observe →（失败则）replan。等价于工作流引擎加 Saga 补偿——不能在一次工具失败后直接给用户最终答案，而要把 observation 写回状态机。Case 3 说明：未 observe 检索质量就塞满 context，等价于未建索引的全表扫描。

## 自己的例子

- **载体**：TrackARuntime
- **证据**：`TrackARuntime/m1_m2/evidence/<run_id>/state.json` — round 1 observe 测试失败，round 2 replan 后 success=true
- **命令**：`python cli.py run --task "fix failing test"`

## Bad Case 口述（Case 3）

现象：300 页 PDF 遗漏中间关键页。根因：全量 context + attention 中间弱化。工程等价：无索引全表扫描。监控：输入 token 分布、分层命中率。回滚：恢复摘要优先路由。与 M1 关联：observe 阶段应检测「检索不充分」并 replan 到摘要树策略，而非继续生成。

## Exit Criteria

- [x] 3 分钟白板讲清 Agent loop
- [x] 能演示 replan trace
- [x] Case 3 口述完整
- [x] Day1–3 笔记已完成（用户执行时勾选）
