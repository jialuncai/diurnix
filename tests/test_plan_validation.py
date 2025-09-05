from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.plan_validation import validate_references
from diurnix.plans import InputRef, Plan, PlanStep, ValueType


def test_reference_validator_accepts_declared_source_output() -> None:
    source = PlanStep("source", "clock.now", {}, {}, {"time": ValueType.STRING})
    target = PlanStep(
        "target",
        "echo",
        {},
        {"text": InputRef("source", "time", ValueType.STRING)},
        {"out": ValueType.STRING},
    )
    assert validate_references(Plan("plan", (source, target))) is None


def test_reference_validator_reports_dangling_step_and_output() -> None:
    target = PlanStep(
        "target", "echo", {}, {"x": InputRef("missing", "out")}, {"out": ValueType.ANY}
    )
    with pytest.raises(ValidationError, match="dangling"):
        validate_references(Plan("plan", (target,)))
