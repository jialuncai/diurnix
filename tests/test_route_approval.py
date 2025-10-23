from __future__ import annotations

from diurnix.router import NumpyRouter, route_requires_approval


def test_ambiguous_route_requires_approval() -> None:
    assert route_requires_approval(NumpyRouter().route("hello"))
    assert not route_requires_approval(NumpyRouter().route("budget budget 账单"))
