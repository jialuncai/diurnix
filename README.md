# diurnix

diurnix 是一个 Python 3.11+ 的离线个人智能体运行时与日常应用工作台。它用可复现代码验证事件路由、计划 DAG、工具策略、审批、预算、回放和分层记忆等工程机制，并把这些机制用于收件箱与日历、任务、家庭账本、习惯四类应用。

NumPy 是唯一必需的运行时依赖。默认命令不访问网络，不读取真实个人数据，也不需要密钥；可选 `torch` extra 只用于 CPU 上的小型合成训练演示。

## 能做什么

- 生成带 planted ground truth 的合成角色、邮件、日历、流水与习惯记录；
- 以 schema-versioned JSON/JSONL 保存事件、计划、决策、receipt、session 与报告 manifest；
- 在工具执行前应用 allow / deny / ask 策略，并记录不可变审计结果；
- 执行 perceive → plan → act → observe 循环，限制步数、时间和合成金额预算；
- 检测日历区间冲突、账本异常和习惯断档，生成确定性 Markdown、HTML 与 SVG；
- 对同 seed、配置和输入产生 byte-identical session 与报告。

## 安装与检查

```bash
uv venv .venv
uv pip install --python .venv/bin/python -e ".[dev]"
make build
make test
make format-check
```

可选 CPU Torch 演示使用 PyTorch 官方 CPU wheel index：

```bash
uv pip install --python .venv/bin/python -e ".[dev,torch]" \
  --extra-index-url https://download.pytorch.org/whl/cpu \
  --index-strategy unsafe-best-match
make test-all
```

## 快速使用

```bash
.venv/bin/diurnix simulate --seed 7
.venv/bin/diurnix route --text "请在周五前确认日程"
.venv/bin/diurnix demo --seed 7
.venv/bin/diurnix digest --seed 7 --format html > /tmp/diurnix-report.html
```

四个完整离线示例位于 [`examples/`](examples/README.md)。命令与 Python API 说明见 [`docs/usage.md`](docs/usage.md) 和 [`docs/api.md`](docs/api.md)，设计边界见 [`docs/architecture.md`](docs/architecture.md)。

## 诚实边界

项目验证个人智能体的 mechanics，而不是任何真实 LLM 的对话能力。默认测试与示例使用 scripted、replay 或 loopback adapter 及带种植真值的合成数据；所有 accuracy、precision、recall、预算遵守率和 byte equality 都由实际合成运行计算。项目不包含预训练权重、外部数据集、真实用户数据或真实服务端点。

## 时间线说明

本项目于 2026 年 10 月创建和验证。Git 中 2025 年至 2026 年 10 月的日期是本次生成的演示时间线，不代表那些日期已经开展的工作。每次开发提交均执行构建、测试与格式检查；未使用空提交。项目未宣称论文成果、预训练模型或真实 LLM 成绩。

## 开发与许可

完整检查运行 `make release`。贡献约定见 [`CONTRIBUTING.md`](CONTRIBUTING.md)，安全问题处理方式见 [`SECURITY.md`](SECURITY.md)。项目采用 [MIT License](LICENSE)。
