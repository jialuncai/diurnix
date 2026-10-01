# Python API

`diurnix` package root 暴露稳定的类型入口；模块级函数提供 codec、factory、应用分析与报告操作。类型均使用 dataclass、enum 和明确的 tuple/mapping 边界。

## 事件与数据

- `PersonalEvent` 及 `InboxMessage`、`CalendarEntry`、`Transaction`、`HabitCheckIn`、`TimerFire`、`UserUtterance`
- `SyntheticClock`、`SeededRandom`、`Persona`、`SyntheticBundle`
- `generate_bundle(seed, start)`：产生四域数据与 planted ground truth
- `ArtifactEnvelope`：schema version、kind、payload checksum 封装

## 运行时

- `ToolSpec`、`ToolRegistry`、`ToolCall`、`ToolResult`
- `PolicyRule`、`PolicyEngine`、`PolicyDecision`、`DecisionLog`
- `Executor`、`RetryConfig`、`ExecutionReceipt`
- `Plan`、`PlanStep`、`InputRef`、`ValueType`
- `Budget`、`Usage`、`LoopState`、`LoopTrace`
- `ApprovalQueue`、`PendingApproval`、`ApprovalStatus`

Executor 的实现返回值先转换为 `ToolResult` 再写入 receipt；side-effecting call 应提供 idempotency key。Policy 默认 effect 必须由调用者明确选择，规则冲突按 specificity、priority 与 deny-safe tie break 解析。

## Session 与 memory

- `SessionRecorder` / `SessionFileRecorder` 追加 checksummed JSONL；`SessionReplayer` 验证链并重建相同 bytes。
- `MemoryStore` 管理 `WORKING`、`SESSION`、`PERSISTENT` scope；`PrivacyTier` 限定 reader 可见性。

## 路由、应用与报告

- `NumpyRouter` 返回 `RouteResult`；ambiguous band 可触发审批路径。
- `TriageResult`、`RescheduleProposal`、`DailyTaskPlan`、`BudgetEnvelope`、`AnomalyFinding`、`StreakSummary` 描述四个应用的输出。
- `BenchConfig` / `BenchScorecard` 运行合成端到端检查。
- `RunMetadata` / `ReportBundle` 生成 Markdown、self-contained HTML 与 SVG checksum manifest。

序列化函数采用 `*_to_dict` / `*_from_dict` 成对命名，decoder 严格检查字段集合和 schema version。兼容性与校验规则见 [`schemas.md`](schemas.md)。
