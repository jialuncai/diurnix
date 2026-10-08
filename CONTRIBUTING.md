# 贡献指南

diurnix 接受聚焦于离线运行时、合成数据和四个内置应用的可复现改进。请先说明行为变化及其 honesty boundary，再提交小而完整的变更。

## 本地环境

```bash
uv venv .venv
uv pip install --python .venv/bin/python -e ".[dev]"
make format
make release
```

涉及可选模型时安装 `.[dev,torch]` 的 CPU wheel，并运行 `make test-all`。不要加入网络密钥、真实个人数据、预训练权重或必须下载的外部数据集。

## 代码与测试

- 支持 Python 3.11+，保持 dataclass 与完整 type hints；
- 新的可持久化 artifact 必须包含 schema version、strict decoder、roundtrip 与 golden test；
- 新的随机路径接受 seed，新的时间路径使用 aware datetime；
- 工具 side effect 必须经过 policy、approval 和 idempotency 边界；
- 测试覆盖成功/拒绝、encode/decode 和边界值，slow/model test 使用对应 marker；
- 合成测量必须标注 planted ground truth，不能表述为真实模型或真实数据效果。

提交前运行 `make build test-all format-check lint typecheck`。变更 public API、schema 或用户可见行为时同步更新文档与 `CHANGELOG.md`。
