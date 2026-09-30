# 架构

diurnix 把日常应用视为确定性运行时之上的纯算法消费者。输入首先成为 versioned personal event；计划器只选择 registry 中声明过 schema、capability 和 side-effect class 的工具。Executor 在每次调用前查询 policy engine，`deny` 永不进入实现，`ask` 进入有过期时间的 approval queue，`allow` 才能得到 receipt。

```text
synthetic events → intent router → plan DAG → policy decision
                                             ├─ deny → audit receipt
                                             ├─ ask  → approval queue
                                             └─ allow → executor → observation
                                                          ↓
         report ← four life applications ← session log ← agent loop
```

## 层次

1. **数据基础**：aware datetime、事件 dataclass、canonical JSON、checksum、strict JSONL 与 schema migration。
2. **运行时核心**：tool registry、policy precedence、redaction、approval、idempotent executor、plan DAG、预算化 agent loop。
3. **状态层**：checksummed session、byte-identical replay、checkpoint，以及 working / session / persistent memory 与 privacy tier。
4. **应用层**：inbox/calendar triage、GTD-style task planning、household ledger analysis、habit/routine tracking。
5. **观察层**：bench scorecard、Markdown/HTML digest 和无绘图库 SVG。

## 决定性边界

所有随机入口都接受显式 seed，并用命名 fork 隔离子流。时间由 aware datetime 或 `SyntheticClock` 提供；排序键包含稳定 ID；浮点统计在产生处量化。Codec 不修改数据，只拒绝非有限值、未知字段、checksum 不一致和 unsupported schema version。

Side effect 使用 two-phase prepare/commit 与 idempotency key。中断后的 checkpoint 恢复已完成 key，避免重复执行。拒绝动作、超预算动作和高于 reader privacy tier 的 memory note 都在边界处被阻断，并在测试中覆盖随机序列不变量。

## 依赖方向

`events`、`codec` 和 `integrity` 不依赖应用；runtime 模块不导入 CLI；四个应用只依赖公开数据结构与小型基础函数。可选 Torch 模块延迟导入，因此不安装 `torch` 时基础包、CLI 和默认测试仍可运行。
