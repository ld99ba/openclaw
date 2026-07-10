from __future__ import annotations

from pathlib import Path

from openclaw.intelligence.memory_lifecycle import MemoryLifecycle
from openclaw.intelligence.skill_lifecycle import SkillLifecycle
from tools.verify_memory_skill_lifecycle import (
    MEMORY_REQUIRED_FIELDS,
    SKILL_REQUIRED_FIELDS,
    validate_lifecycle,
    verify_memory_skill_lifecycle,
)


def test_memory_lifecycle_accepts_complete_record() -> None:
    lifecycle = MemoryLifecycle()
    result = validate_lifecycle({
        "source": "reports/final/current_state.json",
        "purpose": "resume context",
        "expiry": "2026-12-31",
        "audit": "reports/v1_1/phase_02/memory_audit.md",
    }, lifecycle.rules, MEMORY_REQUIRED_FIELDS)

    assert result["ok"] is True
    assert result["missing"] == []


def test_memory_lifecycle_reports_missing_governance_fields() -> None:
    lifecycle = MemoryLifecycle()
    result = validate_lifecycle({"source": "scratch"}, lifecycle.rules, MEMORY_REQUIRED_FIELDS)

    assert result["ok"] is False
    assert result["missing"] == ["purpose", "expiry", "audit"]


def test_skill_lifecycle_accepts_complete_record() -> None:
    lifecycle = SkillLifecycle()
    result = validate_lifecycle({
        "tests": ["tests/v1_1/test_memory_skill_lifecycle.py"],
        "promotion_gate": "pytest-pass",
        "rollback": "disable-skill-and-restore-previous-rules",
        "workshop": "manual-review-required-before-release",
    }, lifecycle.rules, SKILL_REQUIRED_FIELDS)

    assert result["ok"] is True
    assert result["missing"] == []


def test_skill_lifecycle_reports_missing_release_fields() -> None:
    lifecycle = SkillLifecycle()
    result = validate_lifecycle({"tests": []}, lifecycle.rules, SKILL_REQUIRED_FIELDS)

    assert result["ok"] is False
    assert result["missing"] == ["tests", "promotion_gate", "rollback", "workshop"]


def test_memory_skill_lifecycle_verifier_writes_reports(tmp_path: Path) -> None:
    result = verify_memory_skill_lifecycle(output_dir=tmp_path)

    assert result["ok"] is True
    assert (tmp_path / "memory_skill_lifecycle_result.json").exists()
    assert (tmp_path / "memory_skill_lifecycle_report.md").exists()
