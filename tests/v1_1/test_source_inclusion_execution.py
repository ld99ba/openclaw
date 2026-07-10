from __future__ import annotations

from pathlib import Path

from tools.verify_v1_1_source_inclusion_execution import (
    build_source_inclusion_execution_record,
)


def approval_gate() -> dict:
    return {
        "approval_phrase": "批准纳入 Phase 09/10 的 10 个 openclaw 源码候选",
        "next_stage_pathspec": [
            "openclaw/__init__.py",
            "openclaw/policies/policy.json",
        ],
        "recommended_exclusions": ["policies/repair_policy.yaml"],
        "blocking_issue_count": 0,
        "warning_count": 1,
    }


def test_source_inclusion_execution_requires_exact_approval_phrase(tmp_path: Path) -> None:
    result = build_source_inclusion_execution_record(
        approval_phrase="批准",
        approval_gate_result=approval_gate(),
        output_dir=tmp_path,
    )

    assert result["ok"] is False
    assert result["approval_phrase_matched"] is False
    assert result["approval_granted"] is False
    assert result["approved_pathspec"] == []


def test_source_inclusion_execution_records_approved_pathspec(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "openclaw" / "policies").mkdir(parents=True)
    (tmp_path / "openclaw" / "__init__.py").write_text('"""OpenClaw."""\n', encoding="utf-8")
    (tmp_path / "openclaw" / "policies" / "policy.json").write_text("{}", encoding="utf-8")

    result = build_source_inclusion_execution_record(
        approval_phrase="批准纳入 Phase 09/10 的 10 个 openclaw 源码候选",
        approval_gate_result=approval_gate(),
        output_dir=tmp_path / "reports",
    )

    assert result["ok"] is True
    assert result["approval_phrase_matched"] is True
    assert result["approval_granted"] is True
    assert result["approved_pathspec_count"] == 2
    assert result["excluded_pathspec"] == ["policies/repair_policy.yaml"]
    assert result["missing_approved_paths"] == []
    assert result["forbidden_root_policy_paths"] == []
    assert result["git_stage_executed_by_tool"] is False
    assert result["git_commit_executed_by_tool"] is False
    assert result["destructive_action_taken"] is False
    assert result["files_moved_or_deleted"] is False
    assert (tmp_path / "reports" / "source_inclusion_execution_result.json").exists()
    assert (tmp_path / "reports" / "source_inclusion_execution_report.md").exists()
