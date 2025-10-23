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
