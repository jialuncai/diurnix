# 合成角色的一天

该示例把同一份种植真值的合成数据依次用于收件箱分类、日历冲突提案和限额内的每日任务计划。最后一个日历写入请求交给离线 scripted approver；该 approver 明确选择暂缓，因此请求进入一级升级状态，不会执行外部写入。

```bash
.venv/bin/python examples/persona_day/run.py --seed 17 --output /tmp/diurnix-persona-day
```

输出目录包含收件箱与日历 Markdown、版本化任务计划 JSON 和汇总 JSON。`inbox_accuracy` 仅针对工厂种植标签，不能解释为真实邮件数据上的准确率。
