# 安全策略

## 支持范围

最新 patch release 接收安全修复。diurnix 默认只处理合成数据并离线运行，但 library 可被集成到具有真实 side effect 的系统，因此 policy bypass、PII redaction 泄漏、privacy tier 越权、checksum/replay 绕过和 idempotency 失效都属于安全问题。

## 报告问题

请使用仓库的私密 security advisory 报告未公开漏洞，不要在公开 issue 中附上真实个人数据、凭据或可直接利用的细节。报告应包含受影响版本、最小复现、预期 policy boundary 和实际结果。维护者确认后会通过 patch release 修复并在 advisory 中说明影响。

## 运行责任

内置工具与示例是 deterministic in-process implementation，不连接邮箱、日历、银行或付费服务。真实 connector 必须由集成方提供最小权限、明确 allowlist、审批人、timeout、rate limit 和可恢复存储；不能把 synthetic benchmark 分数当作部署安全证明。
