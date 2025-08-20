from __future__ import annotations

from diurnix.executor import Executor, executor_recovery_manifest
from diurnix.integrity import content_checksum
from diurnix.policy import PolicyEffect, PolicyEngine
from diurnix.registry import ToolRegistry


def test_empty_executor_recovery_manifest_is_self_verifying() -> None:
    executor = Executor(ToolRegistry(), PolicyEngine((), default_effect=PolicyEffect.DENY))
    manifest = executor_recovery_manifest(executor)
    assert manifest["kind"] == "executor.checkpoint"
    assert manifest["checksum"] == content_checksum(manifest["checkpoint"])
    assert manifest["checkpoint"] == {"schema_version": 1, "idempotency": []}
