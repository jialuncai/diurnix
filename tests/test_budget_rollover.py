from __future__ import annotations

from diurnix.ledger_app import BudgetEnvelope, rollover_envelope


def test_unused_budget_rolls_into_next_month() -> None:
    closed = BudgetEnvelope("groceries", 500, spent=425)
    opened = rollover_envelope(closed, 500)
    assert opened.rollover == 75 and opened.available == 575 and opened.spent == 0


def test_overspend_can_carry_as_negative_rollover() -> None:
    closed = BudgetEnvelope("groceries", 500, spent=550)
    assert rollover_envelope(closed, 500).rollover == -50
    assert rollover_envelope(closed, 500, carry_overspend=False).rollover == 0
