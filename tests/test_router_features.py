from __future__ import annotations

from diurnix.router import tokenize


def test_tokenizer_normalizes_latin_and_splits_han() -> None:
    assert tokenize("Plan 明天 TASK-42") == ("plan", "明", "天", "task", "42")


def test_tokenizer_ignores_punctuation_and_empty_text() -> None:
    assert tokenize("...\N{FULLWIDTH COMMA}\N{FULLWIDTH EXCLAMATION MARK}") == ()


def test_keyword_counts_keep_all_intent_classes() -> None:
    from diurnix.router import Intent, keyword_counts

    counts = keyword_counts("回复邮件并查看 budget")
    assert list(counts) == list(Intent) and counts[Intent.INBOX] == 2 and counts[Intent.LEDGER] == 1
