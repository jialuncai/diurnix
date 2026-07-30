from __future__ import annotations

import subprocess
import sys

import diurnix
from diurnix.cli import build_parser, main


def test_public_version_is_semantic() -> None:
    major, minor, patch = diurnix.__version__.split(".")
    assert all(part.isdigit() for part in (major, minor, patch))


def test_root_parser_identifies_program() -> None:
    assert build_parser().prog == "diurnix"
    assert main([]) == 0


def test_module_imports_in_fresh_interpreter() -> None:
    completed = subprocess.run(
        [sys.executable, "-c", "import diurnix; print(diurnix.__version__)"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout.strip() == diurnix.__version__


def test_foundation_public_api_is_explicit_and_importable() -> None:
    expected = {
        "ApprovalQueue",
        "AnomalyFinding",
        "ApprovalStatus",
        "ArtifactEnvelope",
        "Budget",
        "BudgetEnvelope",
        "CalendarEntry",
        "CategoryResult",
        "DailyTaskPlan",
        "DecisionLog",
        "DiurnixError",
        "HabitCheckIn",
        "HabitLoop",
        "InboxMessage",
        "ExecutionReceipt",
        "ExecutionStatus",
        "Executor",
        "InputRef",
        "Intent",
        "IntervalRelation",
        "IntegrityError",
        "LoopPhase",
        "LoopState",
        "LoopTrace",
        "MemoryNote",
        "MemoryScope",
        "MemoryStore",
        "PendingApproval",
        "Plan",
        "PlanStep",
        "PersonalEvent",
        "Persona",
        "PolicyAction",
        "PolicyDecision",
        "PolicyEffect",
        "PolicyEngine",
        "PolicyRule",
        "PrivacyTier",
        "NumpyRouter",
        "RescheduleProposal",
        "RetryConfig",
        "RouteResult",
        "RoutineSchedule",
        "SeededRandom",
        "SessionEntry",
        "SessionFileRecorder",
        "SessionRecorder",
        "SessionReplayer",
        "SideEffect",
        "SyntheticBundle",
        "StreakSummary",
        "SyntheticClock",
        "TaskItem",
        "TaskStatus",
        "TimerFire",
        "TriageResult",
        "ToolCall",
        "ToolRegistry",
        "ToolResult",
        "ToolSpec",
        "TraceEntry",
        "Transaction",
        "Usage",
        "UserUtterance",
        "ValidationError",
        "ValueType",
        "__version__",
        "generate_bundle",
    }
    assert set(diurnix.__all__) == expected
    for name in expected:
        assert getattr(diurnix, name) is not None
