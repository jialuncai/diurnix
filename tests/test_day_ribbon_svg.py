from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.reports import day_ribbon_svg


def test_day_ribbon_sorts_days_and_scales_counts() -> None:
    svg = day_ribbon_svg({"2026-01-02": 2, "2026-01-01": 1})
    assert svg.index("2026-01-01") < svg.index("2026-01-02")
    assert 'opacity="0.575"' in svg and 'opacity="1.0"' in svg


def test_day_ribbon_validates_counts_and_width() -> None:
    with pytest.raises(ValidationError, match="invalid"):
        day_ribbon_svg({"2026-01-01": -1})
    with pytest.raises(ValidationError, match="invalid"):
        day_ribbon_svg({}, cell_width=4)
