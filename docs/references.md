# 设计参考

diurnix 使用下列资料中的机制概念，但 schema、实现和测试均为本项目设计。引用不表示复现论文结果。

- Yao 等人的 [ReAct](https://arxiv.org/abs/2210.03629) 描述 reasoning 与 action 交错的框架；diurnix 只实现显式 perceive → plan → act → observe 状态机，不生成或评价语言推理轨迹。
- Schick 等人的 [Toolformer](https://arxiv.org/abs/2302.04761) 讨论模型何时及如何调用 API；diurnix 借用 tool-use 问题定义，重点实现 registry schema、policy gate、receipt 和 loopback adapter，不训练 Toolformer。
- Packer 等人的 [MemGPT](https://arxiv.org/abs/2310.08560) 使用 memory tiering 思路；diurnix 的 working/session/persistent scope 是确定性存储与 retention 机制，不包含其模型或实验。
- Allen 的 [Maintaining Knowledge about Temporal Intervals](https://cse.unl.edu/~choueiry/Documents/Allen-CACM1983.pdf) 给出 13 种基本 interval relation；日历应用实现这些 relation 的分类与冲突子集。
- David Allen 的 [Getting Things Done 方法概览](https://gettingthingsdone.com/what-is-gtd/) 提供 capture / clarify / organize 工作流术语；任务应用将其实现为小型离线状态转换。
- NumPy 的 [`numpy.std` 文档](https://numpy.org/doc/stable/reference/generated/numpy.std.html) 对标准差参数与浮点行为作出说明；账本在分类内计算 population z-score，并在生产点量化。
- PyTorch 的 [Reproducibility notes](https://docs.pytorch.org/docs/stable/notes/randomness.html) 说明跨平台完全可复现的限制；可选训练演示固定 seed、只用 CPU，并仅断言同环境的确定性与 loss decrease。

Household anomaly detector 的 EWMA、z-score 与 edit distance 是透明的基础算法组合。它没有学习真实交易分布，也不输出金融建议。
