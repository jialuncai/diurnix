from __future__ import annotations

from diurnix.tasks_app import weekly_review_digest


def test_weekly_review_digest_renders_measured_fields() -> None:
    digest = weekly_review_digest(
        {
            "task_count": 2,
            "completed_count": 1,
            "actionable_count": 1,
            "completion_rate": 0.5,
            "slipped_task_ids": ["late"],
        }
    )
    assert digest.startswith("# 每周任务回顾\n")
    assert "完成率: 50.00%" in digest and "- late" in digest


def test_weekly_review_digest_handles_no_slippage() -> None:
    digest = weekly_review_digest(
        {
            "task_count": 0,
            "completed_count": 0,
            "actionable_count": 0,
            "completion_rate": 0.0,
            "slipped_task_ids": [],
        }
    )
    assert "## 延误任务\n- 无" in digest
