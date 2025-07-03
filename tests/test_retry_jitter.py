from __future__ import annotations

from diurnix.executor import RetryConfig, retry_delays


def test_retry_delays_are_seeded_bounded_and_do_not_sleep() -> None:
    config = RetryConfig(max_attempts=4, base_delay_seconds=1.0, jitter_seconds=0.5)
    first = retry_delays(config, 42)
    assert first == retry_delays(config, 42)
    assert len(first) == 3
    for index, delay in enumerate(first, start=1):
        assert index <= delay <= index + 0.5


def test_single_attempt_has_no_retry_delays() -> None:
    assert retry_delays(RetryConfig(max_attempts=1), 1) == ()
