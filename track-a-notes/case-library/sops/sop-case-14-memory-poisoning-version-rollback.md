# SOP Case 14：Memory poisoning 与版本回滚

> 案例叙事：[case-14](../cases/case-14-memory-poisoning-version-rollback.md)  
> **定位**：生产扩展 Case（求职增强）；主练 P4 Memory Policy + M4 Security Eval。

## 现象

- Agent 在多个无关任务里复用错误偏好或错误规则。
- 追溯发现污染来自单次用户输入、恶意文档或错误 summary。
- 删除当前会话无效，因为错误已经写入长期 memory。

## 根因

1. **CTX**：长期 memory 被当成普通 context，没有写入策略和作用域。
2. **SEC**：untrusted input 能影响持久状态，缺少 provenance、approval、TTL。
3. **M4**：eval 没有覆盖 memory poisoning 和 rollback 场景。

## 系统等价物

等价于把一次请求中的未验证输入写入全局配置，之后所有请求都受污染配置影响。

## 故障响应 SOP

| 阶段 | 时间 | 动作 |
|---|---|---|
| 观察 | 5 min | 查询近期 memory write：source task、scope、author、created_at、version、usage count |
| 隔离 | 10 min | 禁用受污染 memory scope；切 session-only mode；暂停自动 memory write |
| 定位 | 30 min | 判断是 write policy 缺失、scope 过宽、approval 缺失、summary 污染，还是来源不可信 |
| 修复验证 | 1 h | rollback / delete / quarantine 对应 memory version；重放受影响任务 |
| 复盘 | 全天 | 新增 memory poisoning eval、write approval、provenance audit 和 TTL 策略 |

## 监控

| 层 | 指标 |
|---|---|
| Memory | `memory_write_count`、`high_impact_memory_write`、`memory_rollback_count` |
| Security | untrusted source → memory write 触发率 |
| Runtime | memory hit rate、scope mismatch count |
| Eval | memory poisoning scenario pass rate |

## 回滚预案

1. Quarantine 污染 memory 及同 source 批次写入。
2. 回滚到污染前版本或禁用该 scope。
3. 重放受影响任务，确认不再引用污染 memory。
4. 恢复 memory write 前先加 policy 与 approval。

## 我的项目映射

（填写：memory taxonomy、write policy table、provenance 字段、rollback 记录）
