# 离线示例

所有示例都接受 seed 和输出目录，只使用 synthetic factory，并由测试套件实际执行。

- [合成角色的一天](persona_day/README.md)：triage → calendar proposal → task plan → approval escalation
- [合成账本异常周](ledger_anomaly/README.md)：异常检测 → 月报 → SVG
- [30 天习惯连续记录](habit_streak/README.md)：planted lapse → heatmap → consistency report
- [合成角色完整一周](persona_week/README.md)：四应用 → bench → HTML report bundle

一次验证全部示例及其精确产物集合：

```bash
make examples-check
```

最小安装检查仍可运行 `.venv/bin/python examples/quickstart.py`。
