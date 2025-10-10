from __future__ import annotations

from diurnix.loop import LoopPhase, LoopState
from diurnix.loop_runtime import apply_receipt_stop


def test_terminal_receipts_stop_with_precise_reason() -> None:
    for status, reason in (
        ("denied", "policy denied"),
        ("pending", "approval pending"),
        ("failed", "tool failed"),
    ):
        stopped = apply_receipt_stop(LoopState(), status)
        assert stopped.phase is LoopPhase.STOPPED and stopped.stop_reason == reason


def test_success_receipt_keeps_loop_running() -> None:
    assert apply_receipt_stop(LoopState(), "succeeded").phase is LoopPhase.PERCEIVE
