from __future__ import annotations

from diurnix.cli import main


def test_cli_digest_emits_markdown_by_default(capsys) -> None:
    assert main(["digest", "--seed", "8"]) == 0
    output = capsys.readouterr().out
    assert output.startswith("# diurnix 合成运行报告")
    assert "policy_violations: 0" in output


def test_cli_digest_emits_self_contained_html(capsys) -> None:
    assert main(["digest", "--seed", "8", "--format", "html"]) == 0
    output = capsys.readouterr().out
    assert output.startswith("<!doctype html>") and output.endswith("</html>")
    assert "<style>" in output
