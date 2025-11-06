from __future__ import annotations

import pytest

pytest.importorskip("torch")
pytestmark = [pytest.mark.model, pytest.mark.slow]
router_module = pytest.importorskip("diurnix.router")
torch_router_module = pytest.importorskip("diurnix.torch_router")
Intent = router_module.Intent
train_synthetic_router = torch_router_module.train_synthetic_router


def test_torch_training_validates_input_boundaries() -> None:
    with pytest.raises(ValueError, match="empty"):
        train_synthetic_router(())
    with pytest.raises(ValueError, match="positive"):
        train_synthetic_router((("mail", Intent.INBOX),), epochs=0)
