"""Deterministic sliding-window policy rate accounting."""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta

from diurnix.errors import ValidationError


class RateLimitTracker:
    """Count accepted action timestamps in per-key sliding windows."""

    def __init__(self, limit: int, window: timedelta) -> None:
        if limit < 1 or window <= timedelta(0):
            raise ValidationError("rate limit and window must be positive")
        self.limit = limit
        self.window = window
        self._history: dict[str, deque[datetime]] = defaultdict(deque)

    def allows(self, key: str, now: datetime) -> bool:
        """Return whether another action fits without recording it."""
        history = self._prune(key, now)
        return len(history) < self.limit

    def record(self, key: str, now: datetime) -> None:
        """Record an allowed action and reject overflow or backwards time."""
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValidationError("rate limit time must be timezone-aware")
        history = self._prune(key, now)
        if history and now < history[-1]:
            raise ValidationError("rate limit time cannot move backward")
        if len(history) >= self.limit:
            raise ValidationError("rate limit exceeded")
        history.append(now)

    def _prune(self, key: str, now: datetime) -> deque[datetime]:
        history = self._history[key]
        cutoff = now - self.window
        while history and history[0] <= cutoff:
            history.popleft()
        return history
