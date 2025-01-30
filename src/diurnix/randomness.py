"""Seeded random primitives with stable, explicit result types."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

import numpy as np

from diurnix.errors import ValidationError
from diurnix.integrity import content_checksum

T = TypeVar("T")


class SeededRandom:
    """Small deterministic wrapper around NumPy's PCG64 generator."""

    def __init__(self, seed: int) -> None:
        if not 0 <= seed < 2**64:
            raise ValidationError("seed must be an unsigned 64-bit integer", path="$.seed")
        self.seed = seed
        self._generator = np.random.Generator(np.random.PCG64(seed))

    def integer(self, low: int, high: int) -> int:
        """Draw from the half-open integer interval ``[low, high)``."""
        if high <= low:
            raise ValidationError("integer range must be nonempty")
        return int(self._generator.integers(low, high))

    def choice(self, values: Sequence[T]) -> T:
        """Choose one value without coercing the result through an array."""
        if not values:
            raise ValidationError("choice requires at least one value")
        return values[self.integer(0, len(values))]

    def shuffled(self, values: Sequence[T]) -> tuple[T, ...]:
        """Return a deterministic shuffled copy."""
        indices = self._generator.permutation(len(values))
        return tuple(values[int(index)] for index in indices)

    def fork(self, namespace: str) -> SeededRandom:
        """Derive a namespace-specific generator independent of draw history."""
        digest = content_checksum({"seed": self.seed, "namespace": namespace})
        child_seed = int(digest.removeprefix("sha256:")[:16], 16)
        return SeededRandom(child_seed)


def random_streams(seed: int, namespaces: Sequence[str]) -> dict[str, SeededRandom]:
    """Create unique named child streams and reject duplicate namespaces."""
    if len(set(namespaces)) != len(namespaces):
        raise ValidationError("random stream namespaces must be unique")
    root = SeededRandom(seed)
    return {namespace: root.fork(namespace) for namespace in namespaces}
