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


def test_fork_depends_on_namespace_not_parent_draw_history() -> None:
    root = SeededRandom(91)
    early = root.fork("inbox").integer(0, 1_000_000)
    for _ in range(20):
        root.integer(0, 10)
    late = root.fork("inbox").integer(0, 1_000_000)
    other = root.fork("ledger").integer(0, 1_000_000)
    assert early == late
    assert other != early


def test_named_random_streams_are_order_independent() -> None:
    from diurnix.randomness import random_streams

    left = random_streams(3, ["mail", "habit"])
    right = random_streams(3, ["habit", "mail"])
    assert left["mail"].integer(0, 1000) == right["mail"].integer(0, 1000)
    assert left["habit"].integer(0, 1000) == right["habit"].integer(0, 1000)


def test_named_random_streams_reject_duplicates() -> None:
    from diurnix.randomness import random_streams

    with pytest.raises(ValidationError, match="unique"):
        random_streams(3, ["mail", "mail"])


def test_singleton_choice_never_consumes_out_of_bounds_index() -> None:
    random = SeededRandom(2**64 - 1)
    assert [random.choice(("only",)) for _ in range(10)] == ["only"] * 10


def test_integer_draws_respect_negative_half_open_interval() -> None:
    random = SeededRandom(123)
    draws = [random.integer(-3, 2) for _ in range(100)]
    assert min(draws) == -3
    assert max(draws) == 1
    assert 2 not in draws


def test_seed_upper_bound_is_exclusive() -> None:
    SeededRandom(2**64 - 1)
    with pytest.raises(ValidationError, match="unsigned"):
        SeededRandom(2**64)
