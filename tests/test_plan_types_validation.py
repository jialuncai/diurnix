from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.plan_validation import validate_types
from diurnix.plans import InputRef, Plan, PlanStep, ValueType


def test_type_validator_accepts_exact_and_any_ports() -> None:
    source = PlanStep("source", "echo", {}, {}, {"out": ValueType.STRING})
    exact = PlanStep(
        "exact",
        "echo",
        {},
        {"x": InputRef("source", "out", ValueType.STRING)},
        {"out": ValueType.ANY},
    )
    assert validate_types(Plan("plan", (source, exact))) is None


def test_type_validator_reports_precise_mismatch() -> None:
    source = PlanStep("source", "echo", {}, {}, {"out": ValueType.NUMBER})
    target = PlanStep(
        "target",
        "echo",
        {},
        {"x": InputRef("source", "out", ValueType.STRING)},
        {"out": ValueType.ANY},
    )
    with pytest.raises(ValidationError, match="expected string, got number"):
        validate_types(Plan("plan", (source, target)))
