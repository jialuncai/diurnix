from __future__ import annotations

from datetime import UTC, datetime

import pytest

from diurnix.errors import ValidationError
from diurnix.events import EventKind, UserUtterance

NOW = datetime(2026, 10, 30, 8, tzinfo=UTC)


def test_user_utterance_keeps_literal_multilingual_text() -> None:
    event = UserUtterance("utterance_1", NOW, "明天提醒我买牛奶", "zh-CN")
    assert event.kind is EventKind.USER_UTTERANCE
    assert event.text == "明天提醒我买牛奶"
    assert event.locale == "zh-CN"


def test_user_utterance_rejects_blank_text() -> None:
    with pytest.raises(ValidationError, match="text"):
        UserUtterance("utterance_1", NOW, "\n \t")


def test_user_utterance_requires_language_region_locale() -> None:
    for locale in ("zh", "zh_CN", "z-CN", "zh-CHN"):
        with pytest.raises(ValidationError, match="language-region"):
            UserUtterance("utterance_1", NOW, "hello", locale)
