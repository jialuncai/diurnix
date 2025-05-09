from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from diurnix.factory import SyntheticBundle
from diurnix.persona_factory import create_persona


def test_empty_synthetic_bundle_counts_domains() -> None:
    bundle = SyntheticBundle(1, create_persona(1), (), (), (), (), {})
    assert bundle.event_count == 0
    with pytest.raises(FrozenInstanceError):
        bundle.seed = 2  # type: ignore[misc]
