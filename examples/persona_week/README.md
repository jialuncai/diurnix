# 合成角色完整一周

该示例用一个 seed 生成收件箱、日历、账本与习惯流，运行全部四个应用和任务计划评测，并把实际计算结果合成为 Markdown、self-contained HTML、scorecard 与工厂 manifest。

```bash
.venv/bin/python examples/persona_week/run.py --seed 41 --output /tmp/diurnix-week
```

scorecard 检查任务预算、拒绝动作的 policy violation 计数和双次记录的 byte equality。所有应用得分都相对种植真值计算；报告的局限章节明确说明本次运行没有真实 LLM、外部服务或真实个人数据。
