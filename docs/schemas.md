# Schema 与可复现性

diurnix 的可持久化对象使用整数 `schema_version`。当前 event envelope、plan、tool registry、policy set、approval queue、memory、session entry、应用 manifest 和 scorecard 均从 version 1 开始。Decoder 拒绝未知字段，避免拼写错误被静默忽略。

## Canonical JSON

- UTF-8，无 ASCII 强制转义；
- object key 按字典序排列，使用紧凑分隔符；
- 不接受 NaN 与 Infinity；
- datetime 写入含 offset 的 ISO 8601 文本；
- tuple 在 JSON 中成为 array，读取时恢复为不可变 tuple；
- checksum 为 canonical payload bytes 的 SHA-256。

Content checksum 不包含它自身。Codec 不对 float 做 rounding；分数、统计量和费用在产生它们的算法中量化，因此 encode/decode 保持双向值相等。

## JSONL 与 session

每行是完整 envelope，以单个 LF 结束。Session entry 记录前序 checksum，形成有序链；插入、删除、换序或 payload 修改都会在 replay 前失败。相同 seed、输入、配置和 runtime version 生成相同 bytes。

Checkpoint 保存已提交 idempotency key、预算 usage、loop phase 和 recorder offset。恢复过程先验证 checksum 与 schema，再继续未完成步骤；已提交 side effect 不会重复调用。

## 变更规则

新增可选语义也需要新的 schema version 或显式 migration，不能仅让 decoder 接受额外字段。Golden tests 固定 public exports、small seeded fixtures、plan/registry/policy/session JSON 和报告 manifest；有意变更时应同时更新 migration、golden 和 changelog。
