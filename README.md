# diurnix

diurnix 是一个 Python 3.11+ 的离线个人智能体运行时，用确定性实现验证路由、规划、策略、审批、回放、分层记忆与日常生活应用的机制。默认流程只使用合成个人数据，不连接网络服务，也不需要密钥。

当前仓库从可安装的 `src` 布局、CLI 与严格构建检查开始，后续模块均以可复现的种子、版本化结构和双向测试逐步扩展。

## 快速检查

```bash
uv venv .venv
uv pip install --python .venv/bin/python -e ".[dev]"
make release
.venv/bin/python examples/quickstart.py
```

## 诚实边界

项目验证个人智能体的工程机制，不代表任何真实 LLM 的对话能力。默认测试与示例使用 scripted、replay 或 loopback mock adapter 及带有 planted ground truth 的合成数据；不包含预训练权重、外部数据集或真实用户数据。

## 时间线说明

本项目于 2026 年 10 月创建和验证。Git 中 2025 年至 2026 年 10 月的日期是本次生成的演示时间线，不代表那些日期已经开展的工作。每次开发提交均执行构建、测试与格式检查；未使用空提交。项目未宣称论文成果、预训练模型或真实 LLM 成绩。

## 许可证

[MIT](LICENSE)
