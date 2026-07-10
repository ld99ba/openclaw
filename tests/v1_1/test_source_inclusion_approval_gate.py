from __future__ import annotations

from pathlib import Path

from tools.verify_v1_1_source_inclusion_approval_gate import (
    build_source_inclusion_approval_gate,
)


def test_source_inclusion_approval_gate_preserves_approval_boundary(tmp_path: Path) -> None:
    result = build_source_inclusion_approval_gate(
        decision_result={
            "next_stage_pathspec": [
                "openclaw/__init__.py",
                "openclaw/policies/policy.json",
            ],
            "deferred_pathspec": ["policies/repair_policy.yaml"],
        },
        preflight_result={
            "blocking_issue_count": 0,
            "warning_count": 1,
            "preflight": [
                {"path": "openclaw/__init__.py", "warnings": []},
                {"path": "openclaw/policies/policy.json", "warnings": ["owner_review"]},
            ],
        },
        output_dir=tmp_path,
    )

    assert result["ok"] is True
    assert result["approval_granted"] is False
    assert result["approval_required"] is True
    assert result["next_stage_pathspec_count"] == 2
    assert result["deferred_pathspec_count"] == 1
    assert result["warning_paths"] == ["openclaw/policies/policy.json"]
    assert result["git_stage_executed"] is False
    assert result["git_commit_executed"] is False
    assert result["destructive_action_taken"] is False
    assert result["files_moved_or_deleted"] is False
    assert (tmp_path / "source_inclusion_approval_gate_result.json").exists()
    assert (tmp_path / "source_inclusion_approval_gate_report.md").exists()


def test_source_inclusion_approval_gate_fails_when_preflight_has_blockers(tmp_path: Path) -> None:
    result = build_source_inclusion_approval_gate(
        decision_result={
            "next_stage_pathspec": ["openclaw/__init__.py"],
            "deferred_pathspec": [],
        },
        preflight_result={
            "blocking_issue_count": 1,
            "warning_count": 0,
            "preflight": [{"path": "openclaw/__init__.py", "warnings": []}],
        },
        output_dir=tmp_path,
    )

    assert result["ok"] is False
    assert result["approval_granted"] is False
    assert result["approval_required"] is True
