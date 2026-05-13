from __future__ import annotations

from diurnix.ledger_app import BudgetEnvelope


def test_budget_adherence_uses_actual_available_balances() -> None:
    envelopes = (
        BudgetEnvelope("groceries", 500, 450),
        BudgetEnvelope("transport", 100, 120),
        BudgetEnvelope("subscriptions", 80, 80),
    )
    adherent = sum(envelope.available >= 0 for envelope in envelopes)
    assert round(adherent / len(envelopes), 6) == 0.666667


def test_rollover_is_included_in_adherence_boundary() -> None:
    assert BudgetEnvelope("food", 100, spent=110, rollover=10).available == 0
