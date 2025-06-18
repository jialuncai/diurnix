from __future__ import annotations

from datetime import UTC, datetime, timedelta

from diurnix.rate_limit import RateLimitTracker, rate_limit_decision


def test_rate_limit_decision_reports_allow_and_deny_reasons() -> None:
    now = datetime(2026, 10, 30, 8, tzinfo=UTC)
    tracker = RateLimitTracker(1, timedelta(minutes=1))
    assert rate_limit_decision(tracker, "mail.send", now) == (True, "rate capacity available")
    tracker.record("mail.send", now)
    assert rate_limit_decision(tracker, "mail.send", now) == (
        False,
        "rate limit exceeded for mail.send",
    )
