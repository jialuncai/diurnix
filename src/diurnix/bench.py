"""End-to-end synthetic persona benchmark harness."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from diurnix.errors import ValidationError
from diurnix.factory import SyntheticBundle, generate_bundle


@dataclass(frozen=True, slots=True)
class BenchConfig:
    seed: int
    start: datetime
    max_task_minutes: int = 120
    max_task_count: int = 4

    def __post_init__(self) -> None:
        if self.seed < 0:
            raise ValidationError("bench seed cannot be negative")
        if self.start.tzinfo is None or self.start.utcoffset() is None:
            raise ValidationError("bench start must be timezone-aware")
        if self.max_task_minutes < 0 or self.max_task_count < 0:
            raise ValidationError("bench task budgets cannot be negative")


def create_bench_bundle(config: BenchConfig) -> SyntheticBundle:
    return generate_bundle(config.seed, config.start)
