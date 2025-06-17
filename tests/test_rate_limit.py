from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from diurnix.errors import ValidationError
from diurnix.rate_limit import RateLimitTracker

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def test_rate_limit_allows_then_rejects_at_capacity() -> None:
    tracker = RateLimitTracker(2, timedelta(minutes=1))
    assert tracker.allows("mail", NOW)
    tracker.record("mail", NOW)
    tracker.record("mail", NOW + timedelta(seconds=1))
    assert not tracker.allows("mail", NOW + timedelta(seconds=2))
    with pytest.raises(ValidationError, match="exceeded"):
        tracker.record("mail", NOW + timedelta(seconds=2))


def test_rate_limit_keys_are_independent() -> None:
    tracker = RateLimitTracker(1, timedelta(minutes=1))
    tracker.record("mail", NOW)
    assert not tracker.allows("mail", NOW)
    assert tracker.allows("calendar", NOW)


def test_rate_limit_validates_configuration() -> None:
    for limit, window in ((0, timedelta(seconds=1)), (1, timedelta(0))):
        with pytest.raises(ValidationError, match="positive"):
            RateLimitTracker(limit, window)
