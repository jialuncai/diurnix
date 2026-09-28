# 30 天习惯连续记录

该示例生成两个习惯各 30 天的本地日期 check-in，并在第一个习惯中种植连续三天断档。分析器恢复断档区间、计算一致性和 streak，再绘制不依赖绘图库的 SVG heatmap。

```bash
.venv/bin/python examples/habit_streak/run.py --seed 31 --output /tmp/diurnix-habits
```

日期按合成角色的 IANA timezone 构造；heatmap 的绿色、黄色和红色分别表示完成、grace skip 和遗漏。报告中的 recall 只针对明确种植的断档 ID。
