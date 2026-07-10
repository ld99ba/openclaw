from __future__ import annotations

from pathlib import Path

from tools.triage_v1_1_untracked_review_queue import build_review_queue, review_bucket


def test_review_bucket_maps_untracked_surfaces() -> None:
    assert review_bucket("openclaw/__init__.py") == "source_surface_candidate"
    assert review_bucket("policies/policy.json") == "source_surface_candidate"
    assert review_bucket("reports/final/current_state.json") == "baseline_evidence_preserve"
    assert review_bucket("reports/hermes-run.json") == "historical_runtime_evidence"
    assert review_bucket("reports/.hermes-current-owner-token") == "local_control_state"
    assert review_bucket("memory/session.json") == "local_knowledge_or_memory_state"
    assert review_bucket("external/package/file.txt") == "external_research_or_dependency_surface"
    assert review_bucket("quant_screenshot_1.png") == "media_or_binary_artifact"
    assert review_bucket("120B") == "root_misc_review"


def test_review_queue_is_read_only_and_approval_gated(tmp_path: Path) -> None:
    result = build_review_queue(
        paths=[
            "openclaw/__init__.py",
            "reports/final/current_state.json",
            "reports/hermes-run.json",
            "memory/session.json",
            "quant_screenshot_1.png",
            "reports/v1_1/phase_07/untracked_review_queue_result.json",
            "120B",
        ],
        output_dir=tmp_path,
    )

    assert result["ok"] is True
    assert result["untracked_count"] == 7
    assert result["review_queue_count"] == 6
    assert result["v1_1_release_candidate_excluded_count"] == 1
    assert result["manual_review_required"] is True
    assert result["explicit_approval_required_before_stage"] is True
    assert result["destructive_action_taken"] is False
    assert result["files_moved_or_deleted"] is False
    assert result["git_stage_executed"] is False
    assert result["source_candidate_count"] == 1
    assert result["bucket_counts"]["source_surface_candidate"] == 1
    assert result["bucket_counts"]["baseline_evidence_preserve"] == 1
    assert result["bucket_counts"]["historical_runtime_evidence"] == 1
    assert result["bucket_counts"]["local_knowledge_or_memory_state"] == 1
    assert result["bucket_counts"]["media_or_binary_artifact"] == 1
    assert result["bucket_counts"]["root_misc_review"] == 1
    assert (tmp_path / "untracked_review_queue_result.json").exists()
    assert (tmp_path / "untracked_review_queue_report.md").exists()
