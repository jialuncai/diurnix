from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.executor import RetryConfig


def test_retry_config_includes_valid_bounds() -> None:
    assert RetryConfig().max_attempts == 1
    assert RetryConfig(max_attempts=10, base_delay_seconds=1, jitter_seconds=0.5).max_attempts == 10


def test_retry_config_rejects_attempt_and_delay_bounds() -> None:
    for attempts in (0, 11):
        with pytest.raises(ValidationError, match="one to ten"):
            RetryConfig(max_attempts=attempts)
    with pytest.raises(ValidationError, match="cannot be negative"):
        RetryConfig(base_delay_seconds=-1)
