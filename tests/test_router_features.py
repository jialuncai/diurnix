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


def test_recurrence_score_is_bounded_and_multilingual() -> None:
    from diurnix.router import recurrence_score

    assert recurrence_score("每天 routine weekly") == 1.0
    assert recurrence_score("one time") == 0.0


def test_priority_score_caps_weighted_cues() -> None:
    from diurnix.router import priority_score

    assert priority_score("urgent today!") == 1.0
    assert priority_score("今天处理") == 0.5
    assert priority_score("later") == 0.0
