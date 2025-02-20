from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from diurnix.errors import ValidationError
from diurnix.events import EventKind, TimerFire

DUE = datetime(2026, 10, 30, 8, tzinfo=UTC)


def test_timer_fire_reports_exact_and_late_delivery() -> None:
    exact = TimerFire("timer_1", DUE, "wake", DUE)
    late = TimerFire("timer_2", DUE + timedelta(seconds=1.25), "wake", DUE)
    assert exact.kind is EventKind.TIMER_FIRE
    assert exact.lateness_seconds == 0.0
    assert late.lateness_seconds == 1.25


def test_timer_fire_rejects_early_delivery() -> None:
    with pytest.raises(ValidationError, match="before"):
        TimerFire("timer_1", DUE - timedelta(microseconds=1), "wake", DUE)


def test_timer_fire_requires_named_aware_schedule() -> None:
    with pytest.raises(ValidationError, match="timer name"):
        TimerFire("timer_1", DUE, " ", DUE)
    with pytest.raises(ValidationError, match="scheduled time"):
        TimerFire("timer_1", DUE, "wake", datetime(2026, 10, 30, 8))


def test_timer_lateness_uses_absolute_time_across_offsets() -> None:
    from datetime import timezone

    plus_eight = timezone(timedelta(hours=8))
    scheduled = datetime(2026, 10, 30, 16, tzinfo=plus_eight)
    fired = datetime(2026, 10, 30, 8, 0, 2, tzinfo=UTC)
    assert TimerFire("timer_1", fired, "wake", scheduled).lateness_seconds == 2.0


def test_timer_lateness_is_quantized_to_microseconds() -> None:
    fired = DUE + timedelta(microseconds=123456)
    assert TimerFire("timer_1", fired, "wake", DUE).lateness_seconds == 0.123456
