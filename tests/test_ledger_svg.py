from __future__ import annotations

import pytest

from diurnix.errors import ValidationError
from diurnix.ledger_app import ledger_svg


def test_ledger_svg_is_deterministic_and_self_contained() -> None:
    summary = {"category_spending": {"transport": 20.0, "groceries": 40.0}}
    first = ledger_svg(summary)
    assert first == ledger_svg(summary)
    assert first.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    assert "groceries" in first and "transport" in first and first.endswith("</svg>")


def test_ledger_svg_validates_dimensions() -> None:
    with pytest.raises(ValidationError, match="small"):
        ledger_svg({"category_spending": {}}, width=100)


def test_ledger_svg_escapes_category_labels() -> None:
    svg = ledger_svg({"category_spending": {"<script>alert(1)</script>": 1.0}})
    assert "<script>" not in svg
    assert "&lt;script&gt;" in svg


def test_empty_ledger_svg_remains_valid() -> None:
    svg = ledger_svg({"category_spending": {}})
    assert 'height="40"' in svg and svg.endswith("</svg>")
