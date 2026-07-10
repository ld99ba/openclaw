from __future__ import annotations

from pathlib import Path

from tools.assess_v1_1_source_candidates import (
    assess_candidate,
    build_source_candidate_assessment,
    candidate_kind,
    discover_source_candidates,
)


def test_candidate_kind_identifies_source_surfaces() -> None:
    assert candidate_kind("openclaw/__init__.py") == "package_marker"
    assert candidate_kind("openclaw/hermes_adapter/__main__.py") == "package_entrypoint"
    assert candidate_kind("policies/repair_policy.yaml") == "root_policy_shadow"
    assert candidate_kind("openclaw/policies/policy.json") == "package_policy_config"
    assert candidate_kind("openclaw/governance/project_spec.json") == "runtime_json_config"


def test_discover_source_candidates_excludes_v1_1_release_candidates() -> None:
    candidates = discover_source_candidates(
        [
            "openclaw/__init__.py",
            "policies/repair_policy.yaml",
            "reports/v1_1/phase_08/source_candidate_assessment_result.json",
            "docs/plans/2026-07-09-ogk-final-v1-1-phase-08-implementation-plan.md",
        ]
    )

    assert candidates == ["openclaw/__init__.py", "policies/repair_policy.yaml"]


def test_assess_candidate_detects_duplicate_policy_shadow(tmp_path: Path) -> None:
    (tmp_path / "policies").mkdir()
    (tmp_path / "openclaw" / "policies").mkdir(parents=True)
    (tmp_path / "policies" / "repair_policy.yaml").write_text("policy: repair\n", encoding="utf-8")
    (tmp_path / "openclaw" / "policies" / "repair_policy.yaml").write_text(
        "policy: repair\n",
        encoding="utf-8",
    )

    result = assess_candidate("policies/repair_policy.yaml", root=tmp_path)

    assert result["kind"] == "root_policy_shadow"
    assert result["duplicate_of"] == "openclaw/policies/repair_policy.yaml"
    assert result["duplicate_hash_match"] is True
    assert result["explicit_approval_required_before_stage"] is True
    assert result["auto_stage_recommended"] is False


def test_build_source_candidate_assessment_is_read_only(tmp_path: Path) -> None:
    result = build_source_candidate_assessment(
        paths=[
            "openclaw/__init__.py",
            "openclaw/hermes_adapter/__main__.py",
            "policies/repair_policy.yaml",
        ],
        output_dir=tmp_path,
    )

    assert result["ok"] is True
    assert result["source_candidate_count"] == 3
    assert result["manual_review_required"] is True
    assert result["explicit_approval_required_before_stage"] is True
    assert result["git_stage_executed"] is False
    assert result["destructive_action_taken"] is False
    assert result["files_moved_or_deleted"] is False
    assert (tmp_path / "source_candidate_assessment_result.json").exists()
    assert (tmp_path / "source_candidate_assessment_report.md").exists()
