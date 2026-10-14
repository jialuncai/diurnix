## 变更

说明被修改的 runtime mechanism 或 daily application behavior，以及 public schema/API 是否变化。

## 验证

- [ ] `make build`
- [ ] `make test-all`
- [ ] `make format-check`
- [ ] `make lint`
- [ ] `make typecheck`
- [ ] 新行为有成功与拒绝/边界测试；序列化变化有 roundtrip 和 golden test

## 可复现性与边界

- [ ] 所有随机输入都有 seed，时间值包含 timezone
- [ ] 文档中的数字来自实际执行的 synthetic scenario，并标注 planted ground truth
- [ ] 未加入真实个人数据、凭据、网络端点、预训练权重或必须下载的数据集
- [ ] side effect 仍经过 policy、approval、budget 与 idempotency 边界
