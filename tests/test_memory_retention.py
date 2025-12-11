from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.memory import MemoryScope, RetentionPolicy


def test_retention_policy_maps_each_scope() -> None:
    policy = RetentionPolicy(working_days=1, session_days=8, persistent_days=90)
    assert tuple(policy.days_for(scope) for scope in MemoryScope) == (1, 8, 90)


def test_retention_policy_validates_windows_and_threshold() -> None:
    with pytest.raises(ValidationError, match="positive"):
        RetentionPolicy(working_days=0)
    with pytest.raises(ValidationError, match="between"):
        RetentionPolicy(minimum_score=1.1)
