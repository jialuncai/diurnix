from __future__ import annotations

from datetime import UTC, datetime

from diurnix.tasks_app import Clarification, capture_task, clarify_task

NOW = datetime(2026, 10, 30, 9, tzinfo=UTC)


def test_task_clarification_recognizes_nonactionable_buckets() -> None:
    assert (
        clarify_task(capture_task("参考资料\N{FULLWIDTH COLON}日程说明", NOW))
        is Clarification.REFERENCE
    )
    assert clarify_task(capture_task("也许将来学习新工具", NOW)) is Clarification.SOMEDAY
    assert clarify_task(capture_task("垃圾 无需处理", NOW)) is Clarification.DELETE


def test_task_clarification_defaults_specific_work_to_actionable() -> None:
    assert clarify_task(capture_task("完成实验记录", NOW)) is Clarification.ACTIONABLE


def test_delete_cue_precedes_reference_and_someday() -> None:
    task = capture_task("垃圾参考资料\N{FULLWIDTH COMMA}也许将来再看", NOW)
    assert clarify_task(task) is Clarification.DELETE


def test_reference_cue_precedes_someday() -> None:
    task = capture_task("参考资料 someday", NOW)
    assert clarify_task(task) is Clarification.REFERENCE


def test_clarification_schema_is_complete() -> None:
    assert tuple(item.value for item in Clarification) == (
        "actionable",
        "reference",
        "someday",
        "delete",
    )
