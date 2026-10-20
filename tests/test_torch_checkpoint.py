from __future__ import annotations

import pytest

pytest.importorskip("torch")
pytestmark = pytest.mark.model
torch_router_module = pytest.importorskip("diurnix.torch_router")
TorchRouter = torch_router_module.TorchRouter
export_router_weights = torch_router_module.export_router_weights
restore_router_weights = torch_router_module.restore_router_weights


def test_torch_router_weights_roundtrip_predictions() -> None:
    router = TorchRouter(seed=23)
    restored = restore_router_weights(export_router_weights(router))
    assert restored.route("budget 账单") == router.route("budget 账单")


def test_torch_router_checkpoint_rejects_wrong_shape() -> None:
    value = export_router_weights(TorchRouter())
    value["weight"] = [[1.0]]
    with pytest.raises(ValueError, match="shape"):
        restore_router_weights(value)


def test_torch_router_checkpoint_rejects_coerced_ambiguity_band() -> None:
    with pytest.raises(ValueError, match="numeric"):
        restore_router_weights(
            {
                "schema_version": 1,
                "synthetic_only": True,
                "ambiguity_band": "0.1",
                "weight": [],
                "bias": [],
            }
        )
