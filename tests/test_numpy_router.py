from __future__ import annotations

import pytest

from diurnix.router import Intent, NumpyRouter


def test_numpy_router_routes_strong_synthetic_cues() -> None:
    router = NumpyRouter()
    assert router.route("查看账单 budget").intent is Intent.LEDGER
    assert router.route("habit 每天打卡").intent is Intent.HABITS


def test_numpy_router_marks_empty_text_ambiguous() -> None:
    assert NumpyRouter().route("").ambiguous is True


def test_numpy_router_validates_ambiguity_band() -> None:
    with pytest.raises(ValueError, match="negative"):
        NumpyRouter(-0.1)


def test_route_probabilities_sum_to_one_after_quantization() -> None:
    from diurnix.router import route_probabilities

    probabilities = route_probabilities(NumpyRouter().route("budget 账单"))
    assert round(sum(probabilities.values()), 6) == 1.0
    assert max(probabilities, key=probabilities.get) is Intent.LEDGER  # type: ignore[arg-type]
