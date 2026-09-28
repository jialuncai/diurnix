# 合成账本异常周

该示例读取工厂生成的一个月合成流水，运行重复近似匹配、分类内 z-score、订阅涨价和错分类检测，再输出月报与自包含 SVG。指标由检测结果和 `planted_anomaly` 标签直接计算。

```bash
.venv/bin/python examples/ledger_anomaly/run.py --seed 23 --output /tmp/diurnix-ledger
```

`manifest.json` 记录 precision、recall、各类计数和产物 checksum。数值只描述确定性合成样本；示例没有连接银行、支付服务或外部数据集。
