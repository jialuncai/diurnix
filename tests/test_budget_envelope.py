from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.ledger_app import BudgetEnvelope


def test_budget_envelope_combines_allocation_and_rollover() -> None:
    envelope = BudgetEnvelope("groceries", 500, spent=120.25, rollover=25.5)
    assert envelope.available == 405.25


def test_budget_envelope_validates_values() -> None:
    with pytest.raises(ValidationError, match="blank"):
        BudgetEnvelope("", 1)
    with pytest.raises(ValidationError, match="negative"):
        BudgetEnvelope("food", -1)
    with pytest.raises(ValidationError, match="finite"):
        BudgetEnvelope("food", float("nan"))
