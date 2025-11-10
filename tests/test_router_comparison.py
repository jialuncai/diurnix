from __future__ import annotations

import pytest

pytest.importorskip("torch")
pytestmark = pytest.mark.model
router_module = pytest.importorskip("diurnix.router")
torch_router_module = pytest.importorskip("diurnix.torch_router")
Intent = router_module.Intent
TorchRouter = torch_router_module.TorchRouter
compare_with_numpy = torch_router_module.compare_with_numpy


def test_router_comparison_labels_synthetic_measurements() -> None:
    report = compare_with_numpy(TorchRouter(seed=3), (("budget 账单", Intent.LEDGER),))
    assert report["synthetic"] is True
    assert report["sample_count"] == 1
    assert 0.0 <= report["numpy_accuracy"] <= 1.0
    assert 0.0 <= report["torch_accuracy"] <= 1.0
