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


def test_torch_training_reduces_real_cross_entropy_loss() -> None:
    items = (
        ("mail 邮件 回复", Intent.INBOX),
        ("calendar 日程 会议", Intent.CALENDAR),
        ("task 任务 计划", Intent.TASKS),
        ("budget 账单 消费", Intent.LEDGER),
        ("habit 习惯 打卡", Intent.HABITS),
    )
    _, losses = train_synthetic_router(items, seed=17, epochs=40)
    assert len(losses) == 40
    assert losses[-1] < losses[0]
