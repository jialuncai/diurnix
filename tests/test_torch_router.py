from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")
pytestmark = pytest.mark.model

router_module = pytest.importorskip("diurnix.router")
torch_router_module = pytest.importorskip("diurnix.torch_router")
Intent = router_module.Intent
TorchRouter = torch_router_module.TorchRouter


def test_torch_router_returns_complete_scores() -> None:
    result = TorchRouter(seed=4).route("budget 账单")
    assert set(result.scores) == set(Intent)
    assert result.intent in Intent


def test_torch_router_validates_ambiguity_band() -> None:
    with pytest.raises(ValueError, match="negative"):
        TorchRouter(ambiguity_band=-0.1)
