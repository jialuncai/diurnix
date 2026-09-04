from __future__ import annotations

import json

from diurnix.cli import main


def test_cli_route_emits_canonical_result(capsys) -> None:
    assert main(["route", "--text", "查看 budget 账单"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["intent"] == "ledger"
    assert payload["ambiguous"] is False
    assert round(sum(payload["probabilities"].values()), 6) == 1.0


def test_cli_route_marks_uncued_text_ambiguous(capsys) -> None:
    assert main(["route", "--text", "hello"]) == 0
    assert json.loads(capsys.readouterr().out)["ambiguous"] is True


def test_cli_route_requires_text(capsys) -> None:
    import pytest

    with pytest.raises(SystemExit) as caught:
        main(["route"])
    assert caught.value.code == 2
    assert "--text" in capsys.readouterr().err


def test_cli_route_rejects_negative_ambiguity_band() -> None:
    import pytest

    with pytest.raises(ValueError, match="negative"):
        main(["route", "--text", "hello", "--ambiguity-band", "-1"])
