from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from diurnix.errors import ValidationError
from diurnix.memory import (
    MemoryScope,
    PrivacyTier,
    RetentionPolicy,
    make_memory_note,
    retention_score,
)


def _note(scope: MemoryScope, created_at: datetime):
    return make_memory_note("n", scope, PrivacyTier.PUBLIC, "value", (), created_at)


def test_retention_score_hits_planted_linear_thresholds() -> None:
    created = datetime(2026, 1, 1, tzinfo=UTC)
    policy = RetentionPolicy(working_days=2)
    assert retention_score(_note(MemoryScope.WORKING, created), created, policy) == 1.0
    assert (
        retention_score(_note(MemoryScope.WORKING, created), created + timedelta(days=1), policy)
        == 0.5
    )
    assert (
        retention_score(_note(MemoryScope.WORKING, created), created + timedelta(days=3), policy)
        == 0.0
    )


def test_retention_score_rejects_naive_now() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        retention_score(
            _note(MemoryScope.WORKING, datetime.now(UTC)),
            datetime.now(),
            RetentionPolicy(),
        )
