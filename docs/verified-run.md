# 已验证的合成运行

以下 scorecard 由 2026-10-30 在离线环境实际执行得到：

```bash
.venv/bin/diurnix bench --seed 41
```

```json
{"aggregate_score":0.96,"app_scores":{"calendar":1.0,"habits":1.0,"inbox":1.0,"ledger":1.0,"tasks":0.8},"budget_adherent":true,"policy_violation_count":0,"replay_byte_equal":true,"schema_version":1,"seed":41,"synthetic":true}
```

`aggregate_score` 是五个应用 slice 的等权平均；task slice 在 count/effort/calendar 限额内安排了五分之四的合成任务，因此为 0.8。其余 1.0 只表示该 seed 下算法恢复了工厂自己种植的 label、conflict、anomaly 和 lapse。

`policy_violation_count=0` 来自五次默认拒绝的合成外部写入 probe；`replay_byte_equal=true` 比较两次独立记录的 JSONL bytes。该结果不使用真实个人数据、外部 endpoint 或真实 LLM，不能解释为真实部署效果。
