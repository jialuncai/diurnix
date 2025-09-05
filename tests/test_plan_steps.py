from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.plans import PlanStep, ValueType


def step(**changes: object) -> PlanStep:
    values = {
        "step_id": "read_mail",
        "tool": "mail.list",
        "arguments": {},
        "inputs": {},
        "outputs": {"messages": ValueType.ARRAY},
    }
    values.update(changes)
    return PlanStep(**values)  # type: ignore[arg-type]


def test_plan_step_keeps_contract_and_annotations() -> None:
    item = step(preconditions=("online",), effects=("mail_loaded",), money_budget=1.5)
    assert item.effects == ("mail_loaded",) and item.money_budget == 1.5


def test_plan_step_requires_output_and_nonnegative_budget() -> None:
    with pytest.raises(ValidationError, match="requires outputs"):
        step(outputs={})
    with pytest.raises(ValidationError, match="cannot be negative"):
        step(money_budget=-0.01)
