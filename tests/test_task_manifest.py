from __future__ import annotations

from datetime import date

from diurnix.integrity import content_checksum
from diurnix.tasks_app import DailyTaskPlan, daily_plan_to_dict, task_planning_manifest


def test_task_manifest_hashes_executed_plan_and_review() -> None:
    plan = DailyTaskPlan(date(2026, 10, 30), (), (), 0)
    review = {"completion_rate": 0.0, "synthetic": True}
    manifest = task_planning_manifest(plan, review, 4)
    assert manifest["synthetic"] is True and manifest["scheduled_count"] == 0
    assert manifest["plan_checksum"] == content_checksum(daily_plan_to_dict(plan))
    assert manifest["review_checksum"] == content_checksum(review)
