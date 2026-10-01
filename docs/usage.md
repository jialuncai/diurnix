# 使用指南

所有命令默认离线执行。`--start` 必须是包含 UTC offset 的 ISO datetime；固定 seed 与 start 可复现同一批合成数据。

## CLI

```bash
# 数据与路由
.venv/bin/diurnix simulate --seed 12 --start 2026-10-26T09:00:00+08:00
.venv/bin/diurnix route --text "账单好像重复扣款了"

# 四个应用
.venv/bin/diurnix triage --seed 12
.venv/bin/diurnix schedule --seed 12
.venv/bin/diurnix budget --seed 12
.venv/bin/diurnix habits --seed 12

# 计划、执行和报告
.venv/bin/diurnix plan --seed 12 --max-tasks 3 --max-effort 90
.venv/bin/diurnix act --value "loopback only"
.venv/bin/diurnix bench --seed 12
.venv/bin/diurnix digest --seed 12 --format markdown
.venv/bin/diurnix demo --seed 12
```

`act` 使用内存 loopback tool，展示 policy-gated receipt，不代表外部写入。`bench` 的分数来自 planted labels；`demo` 会输出实际计算的应用分数、policy violation 数和 replay byte equality。

Session 文件可用 `replay --path FILE` 校验，或用 `diff --left A --right B` 比较；有差异时 `diff` 返回 exit code 1，输入或 schema 错误返回 2。

## Python

```python
from datetime import datetime
from zoneinfo import ZoneInfo

from diurnix import BenchConfig, generate_bundle
from diurnix.bench import run_bench, scorecard_to_dict

start = datetime(2026, 10, 26, 9, tzinfo=ZoneInfo("Asia/Shanghai"))
bundle = generate_bundle(12, start)
scorecard = run_bench(BenchConfig(12, start))

print(bundle.event_count)
print(scorecard_to_dict(scorecard))
```

应用级可执行脚本见 [`../examples/README.md`](../examples/README.md)。生产集成应显式提供 tool implementation、policy rules、时钟和存储位置，不应把 synthetic factory 当作真实数据 connector。
