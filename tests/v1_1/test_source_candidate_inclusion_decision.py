from __future__ import annotations

from pathlib import Path

from tools.plan_v1_1_source_candidate_inclusion import (
    build_source_candidate_inclusion_decision,
    decision_for_candidate,
)


def candidate(path: str, kind: str, duplicate_hash_match: bool | None = None) -> dict:
    return {
        "path": path,
        "kind": kind,
        "duplicate_hash_match": duplicate_hash_match,
    }


def test_root_policy_shadow_duplicate_is_deferred() -> None:
    decision = decision_for_candidate(
        candidate("policies/repair_policy.yaml", "root_policy_shadow", True)
    )

    assert decision["decision"] == "defer_root_policy_shadow_duplicate"
    assert decision["include_in_next_stage_pathspec"] is False
    assert decision["requires_adr_before_inclusion"] is True
    assert decision["requires_explicit_approval_before_stage"] is True


def test_package_marker_is_next_stage_candidate_with_approval() -> None:
    decision = decision_for_candidate(candidate("openclaw/__init__.py", "package_marker"))

    assert decision["decision"] == "include_package_marker_after_approval"
    assert decision["include_in_next_stage_pathspec"] is True
    assert decision["requires_explicit_approval_before_stage"] is True


def test_build_inclusion_decision_writes_read_only_packet(tmp_path: Path) -> None:
    assessment = {
        "assessments": [
            candidate("openclaw/__init__.py", "package_marker"),
            candidate("openclaw/hermes_adapter/__main__.py", "package_entrypoint"),
            candidate("openclaw/policies/policy.json", "package_policy_config"),
            candidate("openclaw/governance/project_spec.json", "runtime_json_config"),
            candidate("policies/repair_policy.yaml", "root_policy_shadow", True),
        ],
    }

    result = build_source_candidate_inclusion_decision(
        assessment_result=assessment,
        output_dir=tmp_path,
    )

    assert result["ok"] is True
    assert result["source_candidate_count"] == 5
    assert result["next_stage_pathspec_count"] == 4
    assert result["deferred_pathspec_count"] == 1
    assert result["next_stage_pathspec"] == [
        "openclaw/__init__.py",
        "openclaw/hermes_adapter/__main__.py",
        "openclaw/policies/policy.json",
        "openclaw/governance/project_spec.json",
    ]
    assert result["deferred_pathspec"] == ["policies/repair_policy.yaml"]
    assert result["explicit_approval_required_before_stage"] is True
    assert result["git_stage_executed"] is False
    assert result["destructive_action_taken"] is False
    assert result["files_moved_or_deleted"] is False
    assert (tmp_path / "source_candidate_inclusion_decision_result.json").exists()
    assert (tmp_path / "source_candidate_inclusion_decision_report.md").exists()
