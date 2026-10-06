# 合成数据与测量方法

Synthetic factory 是离线验证的共同数据源。Persona 只包含虚构姓名、IANA timezone、工作时段、`example.test` 联系人、合成商户和习惯目标。seed 经过命名 fork 分配给各域，新增一个域不会改变其他域的随机序列。

## 种植真值

- **Inbox**：action-required、FYI、newsletter、spam、phishing 文本含可审计 tell；accuracy 与 per-label slice 从 `planted_label` 计算。
- **Calendar**：固定重叠和 travel buffer 不足；precision/recall 比较冲突 entry ID。
- **Ledger**：duplicate、outlier、subscription creep、miscategorized 使用 `planted_anomaly`；报告 precision、recall 与类别计数。
- **Habits**：每个目标 30 个本地日 check-in，并种植连续 lapse ID；报告 streak、consistency 与 lapse recovery。
- **Tasks**：从 action-required 邮件构造任务，按 deadline、importance、effort 排序，在工作时段、日历和 effort/count budget 内排期。

## Scorecard

Bench 运行上述五个 app slice，aggregate 是 app score 的等权平均。它另外执行五次默认拒绝的外部写入 probe，要求 implementation call 与 policy violation 均为零；同一 section 记录两次，要求 JSONL bytes 相同；任务 effort 必须不超过配置预算。

这些数字只回答“实现是否恢复了自己种植的模式、是否遵守运行时约束”。它们不是公开语料 benchmark，不测量真实 LLM、真实用户体验或真实金融风险。报告自动生成相同局限说明，示例不会把 synthetic score 与真实效果类比。

可选 NumPy/Torch classifier 使用相同合成 feature/label。训练测试固定 seed 并检查真实 loss decrease；它只证明优化循环在小数据上工作，不提供预训练权重或通用模型结论。
