from __future__ import annotations

import pytest

from diurnix.budgets import Budget, Usage
from diurnix.errors import ValidationError


def test_usage_addition_quantizes_float_dimensions() -> None:
    combined = Usage(1, 0.1, 0.2) + Usage(2, 0.2, 0.1)
    assert combined == Usage(3, 0.3, 0.3)


def test_budget_limits_are_inclusive_in_all_dimensions() -> None:
    budget = Budget(3, 1.5, 2.5)
    assert budget.allows(Usage(3, 1.5, 2.5))
    assert not budget.allows(Usage(4, 1.5, 2.5))
    assert not budget.allows(Usage(3, 1.500001, 2.5))
    assert not budget.allows(Usage(3, 1.5, 2.500001))


def test_budget_require_reports_all_exceeded_dimensions() -> None:
    with pytest.raises(ValidationError, match="steps, wall_seconds, money") as captured:
        Budget(1, 1, 1).require(Usage(2, 2, 2))
    assert captured.value.context == {"path": "$.usage"}


def test_remaining_budget_and_reservation_are_dual_operations() -> None:
    from diurnix.budgets import remaining, reserve

    budget = Budget(10, 5.0, 20.0)
    used = Usage(3, 1.25, 4.5)
    capacity = remaining(budget, used)
    assert capacity == Usage(7, 3.75, 15.5)
    assert reserve(budget, used, capacity) == Usage(10, 5.0, 20.0)


def test_reservation_failure_leaves_original_usage_unchanged() -> None:
    from diurnix.budgets import reserve

    used = Usage(1, 1, 1)
    with pytest.raises(ValidationError, match="budget exceeded"):
        reserve(Budget(1, 1, 1), used, Usage(1, 0, 0))
    assert used == Usage(1, 1, 1)
