from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.randomness import SeededRandom


def test_seeded_draws_have_stable_golden_sequence() -> None:
    random = SeededRandom(42)
    assert [random.integer(0, 100) for _ in range(6)] == [8, 77, 65, 43, 43, 85]


def test_shuffle_is_reproducible_and_does_not_mutate_input() -> None:
    values = ["mail", "calendar", "ledger", "habit"]
    first = SeededRandom(7).shuffled(values)
    second = SeededRandom(7).shuffled(values)
    assert first == second == ("mail", "ledger", "calendar", "habit")
    assert values == ["mail", "calendar", "ledger", "habit"]


def test_random_range_choice_and_seed_have_strict_bounds() -> None:
    with pytest.raises(ValidationError, match="unsigned"):
        SeededRandom(-1)
    random = SeededRandom(1)
    with pytest.raises(ValidationError, match="nonempty"):
        random.integer(2, 2)
    with pytest.raises(ValidationError, match="at least one"):
        random.choice([])
