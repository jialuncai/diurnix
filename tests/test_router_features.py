from __future__ import annotations

from diurnix.router import tokenize


def test_tokenizer_normalizes_latin_and_splits_han() -> None:
    assert tokenize("Plan 明天 TASK-42") == ("plan", "明", "天", "task", "42")


def test_tokenizer_ignores_punctuation_and_empty_text() -> None:
    assert tokenize("...\N{FULLWIDTH COMMA}\N{FULLWIDTH EXCLAMATION MARK}") == ()
