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


def test_rate_limit_releases_capacity_at_exact_window_boundary() -> None:
    tracker = RateLimitTracker(1, timedelta(minutes=1))
    tracker.record("mail", NOW)
    assert not tracker.allows("mail", NOW + timedelta(seconds=59, microseconds=999999))
    assert tracker.allows("mail", NOW + timedelta(minutes=1))
    tracker.record("mail", NOW + timedelta(minutes=1))


def test_rate_limit_rejects_naive_and_backward_record_times() -> None:
    tracker = RateLimitTracker(2, timedelta(minutes=1))
    with pytest.raises(ValidationError, match="timezone-aware"):
        tracker.record("mail", datetime(2026, 10, 30, 8))
    tracker.record("mail", NOW)
    with pytest.raises(ValidationError, match="backward"):
        tracker.record("mail", NOW - timedelta(microseconds=1))
